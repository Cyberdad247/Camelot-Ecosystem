package main

import (
	"path/filepath"
	"strings"
	"testing"
)

// Audit persistence: the redacted hash chain survives a restart and new
// events continue it; raw transcripts stay out of the file.

func TestAuditChainSurvivesRestart(t *testing.T) {
	dbPath := filepath.Join(t.TempDir(), "audit.db")

	first, err := openAuditStore(dbPath, fixedNow)
	if err != nil {
		t.Fatal(err)
	}
	secret := "create a change request to rotate the offshore signing keys"
	for i := 0; i < 3; i++ {
		first.Append(auditEntry{
			SessionID:       "sess",
			TurnID:          "turn-0001",
			Kind:            "lease.issued",
			Transcript:      secret,
			RedactedSummary: "tier-3 blocked pending confirmation",
		})
	}
	lastHash := first.events[len(first.events)-1].Hash
	if err := first.Close(); err != nil {
		t.Fatal(err)
	}

	second, err := openAuditStore(dbPath, fixedNow)
	if err != nil {
		t.Fatalf("reopen: %v", err)
	}
	defer second.Close()

	if second.Len() != 3 {
		t.Fatalf("reloaded %d events, want 3", second.Len())
	}
	if broken := second.VerifyChain(); broken != -1 {
		t.Fatalf("reloaded chain broken at %d", broken)
	}

	// New events continue the persisted chain, ids do not collide.
	event := second.Append(auditEntry{
		SessionID:       "sess",
		Kind:            "turn.cancelled",
		RedactedSummary: "barge-in after restart",
	})
	if event.PrevHash != lastHash {
		t.Fatalf("new event does not chain onto persisted tail")
	}
	if event.AuditID != "audit-0004" {
		t.Fatalf("audit id sequence broken: %s", event.AuditID)
	}
	if broken := second.VerifyChain(); broken != -1 {
		t.Fatalf("extended chain broken at %d", broken)
	}

	// The raw transcript must not exist anywhere in the reloaded records.
	for _, e := range second.events {
		if strings.Contains(e.RedactedSummary, "offshore") || strings.Contains(e.TranscriptSHA256, "offshore") {
			t.Fatal("raw transcript leaked into persisted audit")
		}
	}
}

func TestTamperedStoreIsRefused(t *testing.T) {
	dbPath := filepath.Join(t.TempDir(), "audit.db")
	log, err := openAuditStore(dbPath, fixedNow)
	if err != nil {
		t.Fatal(err)
	}
	log.Append(auditEntry{SessionID: "sess", Kind: "turn.received", RedactedSummary: "a"})
	log.Append(auditEntry{SessionID: "sess", Kind: "turn.received", RedactedSummary: "b"})

	// Tamper with a persisted summary directly.
	if _, err := log.db.Exec(`UPDATE audit_events SET redacted_summary = 'forged' WHERE audit_id = 'audit-0001'`); err != nil {
		t.Fatal(err)
	}
	log.Close()

	if _, err := openAuditStore(dbPath, fixedNow); err == nil {
		t.Fatal("tampered audit store was accepted")
	}
}
