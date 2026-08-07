package main

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"fmt"
	"sync"
	"time"
)

// Hash-chained, redacted audit log (pattern borrowed from Kickbox's
// ledgerValidator). Persistence rules (ADR-001 rule 3):
//   - transcripts are stored as SHA-256 hashes for tier >= 2 skills;
//   - tier-1/read interactions may include the transcript in the summary;
//   - raw audio never reaches this layer at all.

type AuditLog struct {
	mu     sync.Mutex
	events []AuditEvent
	byID   map[string]int
	seq    int
	now    func() time.Time
	// db, when non-nil, mirrors the chain into a local SQLite file
	// (store.go). nil = in-memory only (tests, ephemeral runs).
	db *sql.DB
}

func NewAuditLog(now func() time.Time) *AuditLog {
	return &AuditLog{byID: map[string]int{}, now: now}
}

type auditEntry struct {
	SessionID string
	TurnID    string
	Kind      string
	// Transcript is hashed on append; the raw text is never stored here.
	// Tier-1 summaries may quote it via RedactedSummary at the caller's
	// discretion; tier >= 2 callers must not.
	Transcript      string
	RedactedSummary string
	Decision        *PolicyDecision
	LeaseID         string
}

func (a *AuditLog) Append(e auditEntry) AuditEvent {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.seq++

	prevHash := "genesis"
	if len(a.events) > 0 {
		prevHash = a.events[len(a.events)-1].Hash
	}

	event := AuditEvent{
		AuditID:         fmt.Sprintf("audit-%04d", a.seq),
		SessionID:       e.SessionID,
		TurnID:          e.TurnID,
		Kind:            e.Kind,
		At:              a.now().UTC().Format(time.RFC3339),
		RedactedSummary: e.RedactedSummary,
		Decision:        e.Decision,
		LeaseID:         e.LeaseID,
		PrevHash:        prevHash,
	}
	if e.Transcript != "" {
		sum := sha256.Sum256([]byte(e.Transcript))
		event.TranscriptSHA256 = hex.EncodeToString(sum[:])
	}

	body := fmt.Sprintf("%s|%s|%s|%s|%s|%s|%s|%s",
		event.AuditID, event.SessionID, event.TurnID, event.Kind,
		event.At, event.TranscriptSHA256, event.RedactedSummary, event.LeaseID)
	sum := sha256.Sum256([]byte(prevHash + body))
	event.Hash = hex.EncodeToString(sum[:])

	a.events = append(a.events, event)
	a.byID[event.AuditID] = len(a.events) - 1
	a.persist(event)
	return event
}

func (a *AuditLog) Get(auditID string) (AuditEvent, bool) {
	a.mu.Lock()
	defer a.mu.Unlock()
	i, ok := a.byID[auditID]
	if !ok {
		return AuditEvent{}, false
	}
	return a.events[i], true
}

// VerifyChain recomputes every hash; returns the first broken index or -1.
func (a *AuditLog) VerifyChain() int {
	a.mu.Lock()
	defer a.mu.Unlock()
	prevHash := "genesis"
	for i, event := range a.events {
		if event.PrevHash != prevHash {
			return i
		}
		body := fmt.Sprintf("%s|%s|%s|%s|%s|%s|%s|%s",
			event.AuditID, event.SessionID, event.TurnID, event.Kind,
			event.At, event.TranscriptSHA256, event.RedactedSummary, event.LeaseID)
		sum := sha256.Sum256([]byte(prevHash + body))
		if hex.EncodeToString(sum[:]) != event.Hash {
			return i
		}
		prevHash = event.Hash
	}
	return -1
}

func (a *AuditLog) Len() int {
	a.mu.Lock()
	defer a.mu.Unlock()
	return len(a.events)
}
