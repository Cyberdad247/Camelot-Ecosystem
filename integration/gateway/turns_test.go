package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func newTestServer(t *testing.T) (*Server, *httptest.Server) {
	t.Helper()
	server := NewServer(time.Millisecond, time.Now)
	ts := httptest.NewServer(server.Handler())
	t.Cleanup(ts.Close)
	return server, ts
}

func postJSON[T any](t *testing.T, url string, body any) (int, T) {
	t.Helper()
	payload, err := json.Marshal(body)
	if err != nil {
		t.Fatal(err)
	}
	res, err := http.Post(url, "application/json", bytes.NewReader(payload))
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	var out T
	if err := json.NewDecoder(res.Body).Decode(&out); err != nil {
		t.Fatalf("decode: %v", err)
	}
	return res.StatusCode, out
}

func turnBody(turnID, transcript string) VoiceTurn {
	return VoiceTurn{
		SessionID:   "sess-anya-demo-001",
		TurnID:      turnID,
		Modality:    "text",
		Transcript:  transcript,
		StartedAtMs: 1754000000000,
	}
}

func TestHealthz(t *testing.T) {
	_, ts := newTestServer(t)
	res, err := http.Get(ts.URL + "/healthz")
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		t.Fatalf("healthz status %d", res.StatusCode)
	}
}

func TestTier1ReadAllowsWithoutLease(t *testing.T) {
	_, ts := newTestServer(t)
	status, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-0001", "read staging status"))
	if status != http.StatusOK {
		t.Fatalf("status %d", status)
	}
	if res.Decision.Effect != "allow" || res.Decision.Tier != 1 {
		t.Fatalf("decision %+v", res.Decision)
	}
	if res.Lease != nil {
		t.Fatalf("tier-1 read must not carry a lease, got %+v", res.Lease)
	}
	if res.Artifact == nil || res.Artifact.Kind != "staging_status" {
		t.Fatalf("artifact %+v", res.Artifact)
	}
}

// T2: tier-2 draft creation works.
func TestTier2DraftCreation(t *testing.T) {
	server, ts := newTestServer(t)
	status, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-0002", "prepare a deployment review for the voice slice"))
	if status != http.StatusOK {
		t.Fatalf("status %d", status)
	}
	if res.Decision.Effect != "allow" || res.Decision.Tier != 2 {
		t.Fatalf("decision %+v", res.Decision)
	}
	if res.Artifact == nil || res.Artifact.Kind != "deployment_review_draft" {
		t.Fatalf("want draft artifact, got %+v", res.Artifact)
	}
	if res.Lease == nil {
		t.Fatal("tier-2 turn should report its lease")
	}
	if res.Lease.Status != "consumed" {
		t.Fatalf("tier-2 lease should be consumed after execution, got %q", res.Lease.Status)
	}
	if res.Lease.Token != "" {
		t.Fatal("consumed lease must not leak its token")
	}
	stored, ok := server.leases.Get(res.Lease.LeaseID)
	if !ok || stored.Status != "consumed" {
		t.Fatalf("stored lease %+v", stored)
	}
}

// T3: change_request.create requires confirmation.
func TestChangeRequestRequiresConfirmation(t *testing.T) {
	server, ts := newTestServer(t)

	status, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-0003", "create a change request to scale the api tier"))
	if status != http.StatusOK {
		t.Fatalf("status %d", status)
	}
	if res.Decision.Effect != "requires_confirmation" || res.UIState != "blocked" {
		t.Fatalf("tier-3 must block: %+v", res.Decision)
	}
	if res.Artifact != nil {
		t.Fatal("nothing may execute before confirmation")
	}
	if res.Lease == nil || res.Lease.Status != "pending" {
		t.Fatalf("want pending lease, got %+v", res.Lease)
	}
	if res.Lease.Token != "" {
		t.Fatal("pending lease must not carry a token")
	}

	// Approve -> lease activates, skill executes, lease consumed.
	status, confirmation := postJSON[ConfirmationResponse](t, ts.URL+"/v1/confirmations", ConfirmationRequest{
		SessionID: "sess-anya-demo-001",
		LeaseID:   res.Lease.LeaseID,
		Approve:   true,
	})
	if status != http.StatusOK {
		t.Fatalf("confirmation status %d", status)
	}
	if confirmation.Artifact == nil || confirmation.Artifact.Kind != "change_request" {
		t.Fatalf("want change_request artifact, got %+v", confirmation.Artifact)
	}
	if confirmation.Lease.Status != "consumed" {
		t.Fatalf("lease after approval: %q", confirmation.Lease.Status)
	}

	// The audit trail contains the confirmation.
	if server.audit.VerifyChain() != -1 {
		t.Fatal("audit chain broken")
	}
}

func TestConfirmationDenyRevokesLease(t *testing.T) {
	_, ts := newTestServer(t)
	_, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-0004", "create a change request to scale the api tier"))
	if res.Lease == nil {
		t.Fatal("expected pending lease")
	}

	status, confirmation := postJSON[ConfirmationResponse](t, ts.URL+"/v1/confirmations", ConfirmationRequest{
		SessionID: "sess-anya-demo-001",
		LeaseID:   res.Lease.LeaseID,
		Approve:   false,
	})
	if status != http.StatusOK {
		t.Fatalf("deny status %d", status)
	}
	if confirmation.Lease.Status != "revoked" {
		t.Fatalf("denied lease status %q", confirmation.Lease.Status)
	}
	if confirmation.Artifact != nil {
		t.Fatal("denied confirmation must not execute anything")
	}

	// A denied (revoked) lease cannot be approved afterwards.
	status, _ = postJSON[map[string]any](t, ts.URL+"/v1/confirmations", ConfirmationRequest{
		SessionID: "sess-anya-demo-001",
		LeaseID:   res.Lease.LeaseID,
		Approve:   true,
	})
	if status != http.StatusConflict {
		t.Fatalf("approving a revoked lease: want 409, got %d", status)
	}
}

func TestSmallTalkFallsThrough(t *testing.T) {
	_, ts := newTestServer(t)
	status, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-0005", "hello anya"))
	if status != http.StatusOK {
		t.Fatalf("status %d", status)
	}
	if res.Decision.SkillID != "none.smalltalk" || res.Lease != nil || res.Artifact != nil {
		t.Fatalf("small talk must not touch skills/leases: %+v", res)
	}
	if !strings.Contains(res.Reply.Text, "staging") {
		t.Fatalf("small-talk reply should advertise capabilities: %q", res.Reply.Text)
	}
}

func TestTurnValidation(t *testing.T) {
	_, ts := newTestServer(t)
	status, _ := postJSON[map[string]any](t, ts.URL+"/v1/voice/turns", VoiceTurn{SessionID: "s", TurnID: "t", Modality: "hologram", Transcript: "x"})
	if status != http.StatusBadRequest {
		t.Fatalf("bad modality: want 400, got %d", status)
	}
	status, _ = postJSON[map[string]any](t, ts.URL+"/v1/voice/turns", VoiceTurn{SessionID: "s", TurnID: "", Modality: "text", Transcript: "x"})
	if status != http.StatusBadRequest {
		t.Fatalf("missing turnId: want 400, got %d", status)
	}
}
