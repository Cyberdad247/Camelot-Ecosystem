package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	_ "modernc.org/sqlite" // pure-Go driver: no CGO, native builds stay trivial
)

// SQLite-backed audit persistence (νKG native-runtime correction). Only the
// redacted, hash-chained audit records are durable: transcript hashes, policy
// decisions, lease references. Raw transcripts and raw audio are never
// written (ADR-001 rule 3). Leases stay in-memory by design — they are 30s
// single-use grants and must die with the process.

const auditSchema = `
CREATE TABLE IF NOT EXISTS audit_events (
    seq               INTEGER PRIMARY KEY,
    audit_id          TEXT NOT NULL UNIQUE,
    session_id        TEXT NOT NULL,
    turn_id           TEXT,
    kind              TEXT NOT NULL,
    at                TEXT NOT NULL,
    transcript_sha256 TEXT,
    redacted_summary  TEXT NOT NULL,
    decision_json     TEXT,
    lease_id          TEXT,
    prev_hash         TEXT NOT NULL,
    hash              TEXT NOT NULL
);`

// openAuditStore opens (or creates) the local SQLite file and loads the
// existing chain so new events continue it seamlessly across restarts.
func openAuditStore(path string, now func() time.Time) (*AuditLog, error) {
	db, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, fmt.Errorf("open audit store: %w", err)
	}
	if _, err := db.Exec(auditSchema); err != nil {
		db.Close()
		return nil, fmt.Errorf("init audit schema: %w", err)
	}

	log := NewAuditLog(now)
	log.db = db

	rows, err := db.Query(`SELECT seq, audit_id, session_id, turn_id, kind, at,
        transcript_sha256, redacted_summary, decision_json, lease_id, prev_hash, hash
        FROM audit_events ORDER BY seq`)
	if err != nil {
		db.Close()
		return nil, fmt.Errorf("load audit chain: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var (
			seq          int
			event        AuditEvent
			turnID       sql.NullString
			transcript   sql.NullString
			decisionJSON sql.NullString
			leaseID      sql.NullString
		)
		if err := rows.Scan(&seq, &event.AuditID, &event.SessionID, &turnID, &event.Kind,
			&event.At, &transcript, &event.RedactedSummary, &decisionJSON, &leaseID,
			&event.PrevHash, &event.Hash); err != nil {
			db.Close()
			return nil, fmt.Errorf("scan audit row: %w", err)
		}
		event.TurnID = turnID.String
		event.TranscriptSHA256 = transcript.String
		event.LeaseID = leaseID.String
		if decisionJSON.Valid && decisionJSON.String != "" {
			var decision PolicyDecision
			if err := json.Unmarshal([]byte(decisionJSON.String), &decision); err == nil {
				event.Decision = &decision
			}
		}
		log.events = append(log.events, event)
		log.byID[event.AuditID] = len(log.events) - 1
		if seq > log.seq {
			log.seq = seq
		}
	}
	if err := rows.Err(); err != nil {
		db.Close()
		return nil, err
	}
	if broken := log.VerifyChain(); broken != -1 {
		db.Close()
		return nil, fmt.Errorf("audit store %s: hash chain broken at index %d (tampering?)", path, broken)
	}
	return log, nil
}

// persist writes one appended event. Called under the AuditLog mutex.
func (a *AuditLog) persist(event AuditEvent) {
	if a.db == nil {
		return
	}
	var decisionJSON string
	if event.Decision != nil {
		if b, err := json.Marshal(event.Decision); err == nil {
			decisionJSON = string(b)
		}
	}
	if _, err := a.db.Exec(`INSERT INTO audit_events
        (audit_id, session_id, turn_id, kind, at, transcript_sha256,
         redacted_summary, decision_json, lease_id, prev_hash, hash)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)`,
		event.AuditID, event.SessionID, event.TurnID, event.Kind, event.At,
		event.TranscriptSHA256, event.RedactedSummary, decisionJSON, event.LeaseID,
		event.PrevHash, event.Hash); err != nil {
		// The in-memory chain remains authoritative for this process; a write
		// failure must not take the voice path down, but it must be loud.
		fmt.Printf("audit persist failed for %s: %v\n", event.AuditID, err)
	}
}

func (a *AuditLog) Close() error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.db == nil {
		return nil
	}
	err := a.db.Close()
	a.db = nil
	return err
}
