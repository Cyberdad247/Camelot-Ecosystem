package main

import (
	"errors"
	"strings"
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
	broker := NewToolBroker(leases, NewEffectStore(t.TempDir()))

	for _, skillID := range []string{"deployment.review.prepare", "change_request.create"} {
		_, _, err := broker.Execute(skillID, "turn-0001", "", nil)
		if !errors.Is(err, ErrLeaseRequired) {
			t.Fatalf("%s without lease: want ErrLeaseRequired, got %v", skillID, err)
		}
	}
}

func TestReadOnlySkillNeedsNoLease(t *testing.T) {
	broker := NewToolBroker(NewLeaseStore(fixedNow), NewEffectStore(t.TempDir()))
	artifact, reply, err := broker.Execute("ops.staging.read", "turn-0001", "", nil)
	if err != nil {
		t.Fatalf("tier-1 read failed: %v", err)
	}
	if artifact.Kind != "staging_status" || reply == "" {
		t.Fatalf("unexpected tier-1 result: %+v", artifact)
	}
}

func TestPendingLeaseCannotExecute(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases, NewEffectStore(t.TempDir()))
	lease := leases.Issue("sess", "turn-0001", "skill:change_request.create", false)

	_, _, err := broker.Execute("change_request.create", "turn-0001", "", &lease)
	if err == nil || !errors.Is(err, ErrLeaseNotActive) {
		t.Fatalf("pending lease executed: err=%v", err)
	}
}

func TestForgedTokenIsRejected(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases, NewEffectStore(t.TempDir()))
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)
	lease.Token = "forged-token-attempt"

	_, _, err := broker.Execute("deployment.review.prepare", "turn-0001", "", &lease)
	if !errors.Is(err, ErrLeaseBadToken) {
		t.Fatalf("forged token: want ErrLeaseBadToken, got %v", err)
	}
}

func TestCapabilityMismatchIsRejected(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases, NewEffectStore(t.TempDir()))
	// Lease for the draft skill must not authorize the change-request skill.
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)

	_, _, err := broker.Execute("change_request.create", "turn-0001", "", &lease)
	if !errors.Is(err, ErrLeaseCapMatch) {
		t.Fatalf("capability mismatch: want ErrLeaseCapMatch, got %v", err)
	}
}

func TestLeaseIsSingleUse(t *testing.T) {
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases, NewEffectStore(t.TempDir()))
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)

	if _, _, err := broker.Execute("deployment.review.prepare", "turn-0001", "", &lease); err != nil {
		t.Fatalf("first use failed: %v", err)
	}
	_, _, err := broker.Execute("deployment.review.prepare", "turn-0001", "", &lease)
	if !errors.Is(err, ErrLeaseConsumed) {
		t.Fatalf("second use: want ErrLeaseConsumed, got %v", err)
	}
}

func TestExpiredLeaseIsRejected(t *testing.T) {
	current := fixedNow()
	leases := NewLeaseStore(func() time.Time { return current })
	broker := NewToolBroker(leases, NewEffectStore(t.TempDir()))
	lease := leases.Issue("sess", "turn-0001", "skill:deployment.review.prepare", true)

	current = current.Add(leaseTTL + time.Second) // outlive the 30s TTL
	_, _, err := broker.Execute("deployment.review.prepare", "turn-0001", "", &lease)
	if !errors.Is(err, ErrLeaseExpired) {
		t.Fatalf("expired lease: want ErrLeaseExpired, got %v", err)
	}
}

// The old hand-maintained parity table is gone: the Go registry and the TS
// catalog are generated from contracts/skills.manifest.json, and
// scripts/check-generated.sh fails the build if either has drifted. What
// remains worth asserting in Go are the invariants the ENFORCER depends on,
// so a manifest change can never quietly weaken policy here.
func TestSkillRegistryInvariants(t *testing.T) {
	if len(skillRegistry) == 0 {
		t.Fatal("skill registry is empty")
	}
	seen := map[string]bool{}
	for _, s := range skillRegistry {
		if seen[s.ID] {
			t.Fatalf("duplicate skill id %q", s.ID)
		}
		seen[s.ID] = true

		if s.Tier < 1 || s.Tier > 3 {
			t.Fatalf("%s: tier %d out of range", s.ID, s.Tier)
		}
		// Tier is what the broker gates on, so it must agree with Effectful.
		if want := s.Tier >= 2; s.Effectful != want {
			t.Fatalf("%s: Effectful=%t but tier=%d", s.ID, s.Effectful, s.Tier)
		}
		if s.Tier == 3 && !s.ConfirmationRequired {
			t.Fatalf("%s: tier 3 without ConfirmationRequired would skip the human gate", s.ID)
		}
		// A durable skill that is not lease-gated could act without approval.
		if s.Durable && !s.Effectful {
			t.Fatalf("%s: durable but not effectful — a real side effect with no lease", s.ID)
		}
		if s.Durable && s.Retry != "never" {
			t.Fatalf("%s: durable with retry=%q would let one approval act twice", s.ID, s.Retry)
		}
		if len(s.Phrases) == 0 {
			t.Fatalf("%s: no intent phrases; unreachable", s.ID)
		}
		for _, p := range s.Phrases {
			if p != strings.ToLower(p) {
				t.Fatalf("%s: phrase %q is not lower-case; matching lower-cases the transcript", s.ID, p)
			}
		}
	}
}

// Every durable skill must have an effect implementation. Without this, a
// manifest entry could declare a real side effect that silently does nothing.
func TestEveryDurableSkillHasAnImplementation(t *testing.T) {
	for _, s := range skillRegistry {
		if !s.Durable {
			continue
		}
		_, _, err := runDurableSkill(s, "turn-impl", "probe content", NewEffectStore(t.TempDir()))
		if err != nil {
			t.Fatalf("%s: durable skill has no working implementation: %v", s.ID, err)
		}
	}
}
