package main

import (
	"errors"
	"testing"
	"time"
)

// T1 (server half): Kickbox cannot invoke an effectful tool without a lease.
// The broker is the only execution path, and it refuses.

func fixedNow() time.Time {
	return time.Date(2026, 8, 7, 12, 0, 0, 0, time.UTC)
}

func TestEffectfulSkillWithoutLeaseIsRejected(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases)

	for _, skillID := range []string{"deployment.review.prepare", "change_request.create"} {
		_, _, err := broker.Execute(skillID, "turn-0001", nil)
		if !errors.Is(err, ErrLeaseRequired) {
			t.Fatalf("%s without lease: want ErrLeaseRequired, got %v", skillID, err)
		}
	}
}

func TestReadOnlySkillNeedsNoLease(t *testing.T) {
	broker := NewToolBroker(NewLeaseStore(fixedNow))
	artifact, reply, err := broker.Execute("ops.staging.read", "turn-0001", nil)
	if err != nil {
		t.Fatalf("tier-1 read failed: %v", err)
	}
	if artifact.Kind != "staging_status" || reply == "" {
		t.Fatalf("unexpected tier-1 result: %+v", artifact)
	}
}

func TestPendingLeaseCannotExecute(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases)
	lease := leases.Issue("sess", "turn-0001", "skill:change_request.create", false)

	_, _, err := broker.Execute("change_request.create", "turn-0001", &lease)
	if err == nil || !errors.Is(err, ErrLeaseNotActive) {
		t.Fatalf("pending lease executed: err=%v", err)
	}
}

func TestForgedTokenIsRejected(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases)
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)
	lease.Token = "forged-token-attempt"

	_, _, err := broker.Execute("deployment.review.prepare", "turn-0001", &lease)
	if !errors.Is(err, ErrLeaseBadToken) {
		t.Fatalf("forged token: want ErrLeaseBadToken, got %v", err)
	}
}

func TestCapabilityMismatchIsRejected(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases)
	// Lease for the draft skill must not authorize the change-request skill.
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)

	_, _, err := broker.Execute("change_request.create", "turn-0001", &lease)
	if !errors.Is(err, ErrLeaseCapMatch) {
		t.Fatalf("capability mismatch: want ErrLeaseCapMatch, got %v", err)
	}
}

func TestLeaseIsSingleUse(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases)
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)

	if _, _, err := broker.Execute("deployment.review.prepare", "turn-0001", &lease); err != nil {
		t.Fatalf("first use failed: %v", err)
	}
	_, _, err := broker.Execute("deployment.review.prepare", "turn-0001", &lease)
	if !errors.Is(err, ErrLeaseConsumed) {
		t.Fatalf("second use: want ErrLeaseConsumed, got %v", err)
	}
}

func TestExpiredLeaseIsRejected(t *testing.T) {
	current := fixedNow()
	leases := NewLeaseStore(func() time.Time { return current })
	broker := NewToolBroker(leases)
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)

	current = current.Add(leaseTTL + time.Second) // outlive the 30s TTL
	_, _, err := broker.Execute("deployment.review.prepare", "turn-0001", &lease)
	if !errors.Is(err, ErrLeaseExpired) {
		t.Fatalf("expired lease: want ErrLeaseExpired, got %v", err)
	}
}

// Fixture parity with @camelot/contracts INTENT_FIXTURES (contracts/src/fixtures.ts).
func TestSkillRegistryMatchesContractFixtures(t *testing.T) {
	expected := []Skill{
		{ID: "ops.staging.read", Tier: 1, Effectful: false, ConfirmationRequired: false, Match: "staging"},
		{ID: "deployment.review.prepare", Tier: 2, Effectful: true, ConfirmationRequired: false, Match: "deployment review"},
		{ID: "change_request.create", Tier: 3, Effectful: true, ConfirmationRequired: true, Match: "change request"},
	}
	if len(skillRegistry) != len(expected) {
		t.Fatalf("registry size %d, want %d", len(skillRegistry), len(expected))
	}
	for i, want := range expected {
		if skillRegistry[i] != want {
			t.Fatalf("registry[%d] = %+v, want %+v", i, skillRegistry[i], want)
		}
	}
}
