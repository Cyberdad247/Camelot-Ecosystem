package main

import (
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"sync"
	"time"
)

// Capability leases: short-lived, single-use, revocable authorizations for
// effectful actions. Only the gateway issues them (ADR-001 rule 1).

const leaseTTL = 30 * time.Second

var (
	ErrLeaseNotFound  = errors.New("lease not found")
	ErrLeaseNotActive = errors.New("lease is not approved")
	ErrLeaseExpired   = errors.New("lease expired")
	ErrLeaseConsumed  = errors.New("lease already consumed (single-use)")
	ErrLeaseCapMatch  = errors.New("lease capability does not match requested action")
	ErrLeaseBadToken  = errors.New("lease token signature invalid")
)

type LeaseStore struct {
	mu     sync.Mutex
	leases map[string]*CapabilityLease
	seq    int
	// signingKey signs lease tokens (HMAC-SHA256). Random per process for the
	// demo; the node-agent receives it out of band via env in compose.
	signingKey []byte
	now        func() time.Time
}

func NewLeaseStore(now func() time.Time) *LeaseStore {
	key := make([]byte, 32)
	if _, err := rand.Read(key); err != nil {
		panic(err)
	}
	return &LeaseStore{
		leases:     map[string]*CapabilityLease{},
		signingKey: key,
		now:        now,
	}
}

// sign binds a lease to its id, capability, expiry, and — for node jobs —
// the exact node and tenant it was issued for. Binding node/tenant into the
// signature is what makes a lease for node A unusable at node B, and a
// tenant-A lease unusable by tenant B, even if the token leaks (Phase 4A).
// Skill leases carry empty node/tenant, so the message shape is uniform.
func (s *LeaseStore) sign(leaseID, capability, expiresAt, nodeID, tenantID string) string {
	mac := hmac.New(sha256.New, s.signingKey)
	fmt.Fprintf(mac, "%s|%s|%s|%s|%s", leaseID, capability, expiresAt, nodeID, tenantID)
	return hex.EncodeToString(mac.Sum(nil))
}

// SigningKeyHex exposes the lease signing key so the operator can hand it to
// a node agent out of band (CAMELOT_NODE_LEASE_KEY). Never audited, never
// logged, never returned over the wire by any handler.
func (s *LeaseStore) SigningKeyHex() string {
	return hex.EncodeToString(s.signingKey)
}

// SetSigningKey pins the key to a operator-provided value so an already
// running node agent and the gateway share it across gateway restarts.
func (s *LeaseStore) SetSigningKey(key []byte) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.signingKey = key
}

// Issue creates a lease. Tier-2 skills get status "approved" immediately
// (policy auto-grants drafts); tier-3 leases start "pending" and carry no
// token until a human confirms.
func (s *LeaseStore) Issue(sessionID, turnID, capability string, approved bool) CapabilityLease {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.seq++
	now := s.now()
	lease := &CapabilityLease{
		LeaseID:    fmt.Sprintf("lease-%04d", s.seq),
		SessionID:  sessionID,
		TurnID:     turnID,
		Capability: capability,
		Status:     "pending",
		IssuedAt:   now.UTC().Format(time.RFC3339),
		ExpiresAt:  now.Add(leaseTTL).UTC().Format(time.RFC3339),
		SingleUse:  true,
	}
	if approved {
		lease.Status = "approved"
		lease.Token = s.sign(lease.LeaseID, lease.Capability, lease.ExpiresAt, "", "")
	}
	s.leases[lease.LeaseID] = lease
	return *lease
}

// IssueNodeLease mints an approved, single-use, 30s lease bound to one node,
// one tenant, and one capability. Only the gateway can mint these; the node
// agent independently verifies every field before doing any work.
func (s *LeaseStore) IssueNodeLease(sessionID, turnID, capability, nodeID, tenantID string) CapabilityLease {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.seq++
	now := s.now()
	lease := &CapabilityLease{
		LeaseID:    fmt.Sprintf("nlease-%04d", s.seq),
		SessionID:  sessionID,
		TurnID:     turnID,
		Capability: capability,
		NodeID:     nodeID,
		TenantID:   tenantID,
		Status:     "approved",
		IssuedAt:   now.UTC().Format(time.RFC3339),
		ExpiresAt:  now.Add(leaseTTL).UTC().Format(time.RFC3339),
		SingleUse:  true,
	}
	lease.Token = s.sign(lease.LeaseID, lease.Capability, lease.ExpiresAt, nodeID, tenantID)
	s.leases[lease.LeaseID] = lease
	return *lease
}

func (s *LeaseStore) Get(leaseID string) (CapabilityLease, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	l, ok := s.leases[leaseID]
	if !ok {
		return CapabilityLease{}, false
	}
	s.expireLocked(l)
	return *l, true
}

// Approve activates a pending lease (human confirmation path).
func (s *LeaseStore) Approve(leaseID string) (CapabilityLease, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	l, ok := s.leases[leaseID]
	if !ok {
		return CapabilityLease{}, ErrLeaseNotFound
	}
	s.expireLocked(l)
	switch l.Status {
	case "pending":
		l.Status = "approved"
		l.Token = s.sign(l.LeaseID, l.Capability, l.ExpiresAt, l.NodeID, l.TenantID)
		return *l, nil
	case "expired":
		return *l, ErrLeaseExpired
	default:
		return *l, fmt.Errorf("cannot approve lease in status %q", l.Status)
	}
}

// Revoke kills a lease that has not been consumed. Used by barge-in and by
// confirmation denial. Returns false if the lease was already terminal.
func (s *LeaseStore) Revoke(leaseID string) (CapabilityLease, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	l, ok := s.leases[leaseID]
	if !ok {
		return CapabilityLease{}, false
	}
	if l.Status == "pending" || l.Status == "approved" {
		l.Status = "revoked"
		l.Token = ""
		return *l, true
	}
	return *l, false
}

// RevokeUnusedForTurn revokes every pending/approved lease attached to a turn.
func (s *LeaseStore) RevokeUnusedForTurn(turnID string) []string {
	s.mu.Lock()
	defer s.mu.Unlock()
	var revoked []string
	for _, l := range s.leases {
		if l.TurnID == turnID && (l.Status == "pending" || l.Status == "approved") {
			l.Status = "revoked"
			l.Token = ""
			revoked = append(revoked, l.LeaseID)
		}
	}
	return revoked
}

// Consume validates and burns an approved lease for the given capability.
// This is the single choke point the tool broker relies on.
func (s *LeaseStore) Consume(leaseID, capability, token string) (CapabilityLease, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	l, ok := s.leases[leaseID]
	if !ok {
		return CapabilityLease{}, ErrLeaseNotFound
	}
	s.expireLocked(l)
	switch l.Status {
	case "consumed":
		return *l, ErrLeaseConsumed
	case "expired":
		return *l, ErrLeaseExpired
	case "approved":
		// fall through to validation
	default:
		return *l, ErrLeaseNotActive
	}
	if l.Capability != capability {
		return *l, ErrLeaseCapMatch
	}
	expected := s.sign(l.LeaseID, l.Capability, l.ExpiresAt, l.NodeID, l.TenantID)
	if !hmac.Equal([]byte(expected), []byte(token)) {
		return *l, ErrLeaseBadToken
	}
	l.Status = "consumed"
	l.Token = ""
	return *l, nil
}

func (s *LeaseStore) expireLocked(l *CapabilityLease) {
	if l.Status != "pending" && l.Status != "approved" {
		return
	}
	exp, err := time.Parse(time.RFC3339, l.ExpiresAt)
	if err == nil && s.now().After(exp) {
		l.Status = "expired"
		l.Token = ""
	}
}
