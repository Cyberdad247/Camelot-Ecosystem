package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"strings"
	"testing"
)

// T6: audit redaction + hash chain.

func TestAuditChainVerifies(t *testing.T) {
	log := NewAuditLog(fixedNow)
	for i := 0; i < 5; i++ {
		log.Append(auditEntry{
			SessionID:       "sess",
			TurnID:          "turn-0001",
			Kind:            "turn.received",
			Transcript:      "create a change request to scale the api tier",
			RedactedSummary: "tier-3 blocked pending confirmation",
		})
	}
	if broken := log.VerifyChain(); broken != -1 {
		t.Fatalf("chain broken at %d", broken)
	}
	first, _ := log.Get("audit-0001")
	if first.PrevHash != "genesis" {
		t.Fatalf("first prevHash %q", first.PrevHash)
	}
	second, _ := log.Get("audit-0002")
	if second.PrevHash != first.Hash {
		t.Fatal("chain not linked")
	}
}

func TestAuditStoresHashNotTranscript(t *testing.T) {
	log := NewAuditLog(fixedNow)
	secret := "create a change request to move funds to the offshore cluster"
	event := log.Append(auditEntry{
		SessionID:       "sess",
		TurnID:          "turn-0001",
		Kind:            "lease.issued",
		Transcript:      secret,
		RedactedSummary: "tier-3 change_request.create blocked pending confirmation (lease lease-0001)",
	})

	sum := sha256.Sum256([]byte(secret))
	if event.TranscriptSHA256 != hex.EncodeToString(sum[:]) {
		t.Fatal("transcript hash mismatch")
	}

	// The raw transcript must appear nowhere in the serialized audit record.
	payload, err := json.Marshal(event)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(payload), "offshore") {
		t.Fatalf("raw transcript leaked into audit record: %s", payload)
	}
}

func TestTier3AuditOverHTTPNeverLeaksTranscript(t *testing.T) {
	_, ts := newTestServer(t)
	transcript := "create a change request to rotate the production signing keys"
	_, turnRes := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-0020", transcript))

	res, err := httpGet(ts.URL + "/v1/audit/" + turnRes.AuditID)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(res, "rotate the production signing keys") {
		t.Fatalf("tier-3 audit leaked transcript: %s", res)
	}
	if !strings.Contains(res, "transcriptSha256") {
		t.Fatalf("tier-3 audit missing transcript hash: %s", res)
	}
}

func TestAuditNotFound(t *testing.T) {
	_, ts := newTestServer(t)
	res, err := httpGetStatus(ts.URL + "/v1/audit/audit-9999")
	if err != nil {
		t.Fatal(err)
	}
	if res != 404 {
		t.Fatalf("want 404, got %d", res)
	}
}
