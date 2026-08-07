package main

import (
	"testing"
	"time"
)

// T4: barge-in cancels response streaming and revokes the unused lease.

func TestBargeInCancelsStreaming(t *testing.T) {
	// Slow chunks so the stream is alive when the barge-in lands.
	server := NewServer(50*time.Millisecond, time.Now)
	sessionID := "sess-anya-demo-001"

	events, unsubscribe := server.sessions.Subscribe(sessionID)
	defer unsubscribe()

	server.sessions.StreamReply(sessionID, "turn-0010", "one two three four five six seven eight nine ten")

	// Wait for at least one chunk to prove streaming started.
	var sawChunk bool
	deadline := time.After(2 * time.Second)
	for !sawChunk {
		select {
		case e := <-events:
			if e.Type == "reply.chunk" && e.TurnID == "turn-0010" {
				sawChunk = true
			}
		case <-deadline:
			t.Fatal("no reply.chunk arrived")
		}
	}

	if ok := server.sessions.CancelTurn("turn-0010"); !ok {
		t.Fatal("expected an active stream to cancel")
	}

	// Drain until turn.cancelled; reply.done must never appear.
	deadline = time.After(2 * time.Second)
	for {
		select {
		case e := <-events:
			if e.Type == "reply.done" && e.TurnID == "turn-0010" {
				t.Fatal("stream completed despite barge-in")
			}
			if e.Type == "turn.cancelled" && e.TurnID == "turn-0010" {
				return // success
			}
		case <-deadline:
			t.Fatal("turn.cancelled never arrived")
		}
	}
}

func TestBargeInRevokesUnusedLease(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	sessionID := "sess-anya-demo-001"

	// Tier-3 turn issues a pending (unused) lease.
	pending := server.leases.Issue(sessionID, "turn-0011", "skill:change_request.create", false)
	// An approved-but-unconsumed lease on the same turn must die too.
	approved := server.leases.Issue(sessionID, "turn-0011", "skill:deployment.review.prepare", true)
	// A consumed lease on another turn must survive.
	other := server.leases.Issue(sessionID, "turn-0009", "skill:deployment.review.prepare", true)
	if _, err := server.leases.Consume(other.LeaseID, other.Capability, other.Token); err != nil {
		t.Fatal(err)
	}

	revoked := server.leases.RevokeUnusedForTurn("turn-0011")
	if len(revoked) != 2 {
		t.Fatalf("want 2 revoked leases, got %v", revoked)
	}
	for _, id := range []string{pending.LeaseID, approved.LeaseID} {
		lease, _ := server.leases.Get(id)
		if lease.Status != "revoked" {
			t.Fatalf("lease %s status %q, want revoked", id, lease.Status)
		}
		if lease.Token != "" {
			t.Fatalf("revoked lease %s still carries a token", id)
		}
	}
	surviving, _ := server.leases.Get(other.LeaseID)
	if surviving.Status != "consumed" {
		t.Fatalf("unrelated lease disturbed: %q", surviving.Status)
	}

	// A revoked lease can never execute.
	broker := NewToolBroker(server.leases)
	restored := pending
	restored.Token = "does-not-matter"
	if _, _, err := broker.Execute("change_request.create", "turn-0011", &restored); err == nil {
		t.Fatal("revoked lease executed")
	}
}

// End-to-end over HTTP: a blocked tier-3 turn followed by barge-in reports
// the revoked lease in the response body.
func TestBargeInEndpointRevokesPendingLease(t *testing.T) {
	_, ts := newTestServer(t)

	_, turnRes := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-0012", "create a change request to scale the api tier"))
	if turnRes.Lease == nil || turnRes.Lease.Status != "pending" {
		t.Fatalf("setup: want pending lease, got %+v", turnRes.Lease)
	}

	status, bargeRes := postJSON[BargeInResponse](t, ts.URL+"/v1/voice/barge-in", VoiceBargeIn{
		SessionID: "sess-anya-demo-001",
		TurnID:    "turn-0012",
		AtMs:      1754000099000,
		Reason:    "mock",
	})
	if status != 200 {
		t.Fatalf("barge-in status %d", status)
	}
	if bargeRes.CancelledTurnID != "turn-0012" {
		t.Fatalf("cancelled turn %q", bargeRes.CancelledTurnID)
	}
	if len(bargeRes.RevokedLeaseIDs) != 1 || bargeRes.RevokedLeaseIDs[0] != turnRes.Lease.LeaseID {
		t.Fatalf("revoked leases %v, want [%s]", bargeRes.RevokedLeaseIDs, turnRes.Lease.LeaseID)
	}

	// The dead lease cannot be approved afterwards.
	status, _ = postJSON[map[string]any](t, ts.URL+"/v1/confirmations", ConfirmationRequest{
		SessionID: "sess-anya-demo-001",
		LeaseID:   turnRes.Lease.LeaseID,
		Approve:   true,
	})
	if status != 409 {
		t.Fatalf("approving a barge-in-revoked lease: want 409, got %d", status)
	}
}
