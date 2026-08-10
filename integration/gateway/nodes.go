package main

// Phase 4A: private-mesh node registration, trust, health, and capability-
// scoped remote job routing.
//
// THE RULE (ADR-001 amendment): Tailscale makes a node REACHABLE; it does
// not make a node TRUSTED or AUTHORIZED. Reachability is transport. Trust is
// a band this gateway assigns. Authorization is a short-lived, node-scoped,
// tenant-scoped, capability-scoped, single-use lease this gateway mints —
// and that the Rust agent independently re-validates before doing any work.
//
// Nothing here logs into Tailscale, changes ACLs, advertises routes, or
// touches host networking. The gateway only ever speaks HTTP to an address
// a node reported at registration.

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"sort"
	"strings"
	"sync"
	"time"
)

// ── contracts (mirrored in @camelot/contracts node.ts) ──────────────────

// NodeTrustBand is assigned by the gateway, never claimed by the node.
//
//	pending  -> registered, may do nothing at all (default for every new node)
//	limited  -> may serve READ-ONLY capabilities only
//	trusted  -> may serve any capability it registered
//	degraded -> heartbeat went stale; no new jobs until health returns
//	revoked  -> terminal for this registration; re-enrolment required
type NodeTrustBand string

const (
	TrustPending  NodeTrustBand = "pending"
	TrustLimited  NodeTrustBand = "limited"
	TrustTrusted  NodeTrustBand = "trusted"
	TrustDegraded NodeTrustBand = "degraded"
	TrustRevoked  NodeTrustBand = "revoked"
)

type NodeCapability struct {
	Name     string `json:"name"`
	ReadOnly bool   `json:"readOnly"`
}

type NodeIdentity struct {
	NodeID      string `json:"nodeId"`
	TenantID    string `json:"tenantId"`
	DisplayName string `json:"displayName"`
	// KeyFingerprint is a SHA-256 of the node's enrolment secret. The secret
	// itself never leaves the node; the fingerprint pins the identity so a
	// second process cannot re-register the same nodeId with a new key.
	KeyFingerprint string `json:"keyFingerprint"`
}

type NodeRegistration struct {
	Identity     NodeIdentity     `json:"identity"`
	Capabilities []NodeCapability `json:"capabilities"`
	AgentVersion string           `json:"agentVersion"`
	// DispatchURL is where the gateway sends jobs (typically a tailnet
	// address). Stored for dispatch, NEVER audited or exposed to the UI —
	// audit and UI see AddressHash instead.
	DispatchURL string `json:"dispatchUrl"`
}

type NodeHealth struct {
	NodeID string `json:"nodeId"`
	// Status is the node's self-report; the gateway overrides it with
	// "offline" once the heartbeat goes stale.
	Status         string `json:"status"` // healthy|degraded|offline
	Backend        string `json:"backend,omitempty"`
	MeshReachable  bool   `json:"meshReachable"`
	MeshBackend    string `json:"meshBackend,omitempty"` // e.g. "tailscale"|"none"
	ActiveJobs     int    `json:"activeJobs"`
	ReportedAt     string `json:"reportedAt"`
	AgentVersionOK bool   `json:"agentVersionOk,omitempty"`
}

// NodeView is what /v1/nodes returns and the Node Status panel renders.
// It deliberately contains NO dispatch address, key, or secret.
type NodeView struct {
	NodeID       string           `json:"nodeId"`
	TenantID     string           `json:"tenantId"`
	DisplayName  string           `json:"displayName"`
	Trust        NodeTrustBand    `json:"trust"`
	Health       string           `json:"health"` // healthy|degraded|offline
	Local        bool             `json:"local"`
	Capabilities []NodeCapability `json:"capabilities"`
	AgentVersion string           `json:"agentVersion"`
	MeshBackend  string           `json:"meshBackend,omitempty"`
	LastSeen     string           `json:"lastSeen"`
	// AddressHash is a truncated SHA-256 of the dispatch URL: enough to tell
	// two nodes apart in a log, useless for reaching anything.
	AddressHash string `json:"addressHash"`
	Revocation  string `json:"revocationReason,omitempty"`
}

type NodeJobRequest struct {
	JobID      string          `json:"jobId"`
	NodeID     string          `json:"nodeId"`
	TenantID   string          `json:"tenantId"`
	Capability string          `json:"capability"`
	Lease      CapabilityLease `json:"lease"`
	Payload    json.RawMessage `json:"payload"`
}

type NodeJobResult struct {
	JobID   string          `json:"jobId"`
	NodeID  string          `json:"nodeId"`
	OK      bool            `json:"ok"`
	Result  json.RawMessage `json:"result,omitempty"`
	Failure string          `json:"failure,omitempty"`
}

type NodeRouteDecision struct {
	RequestID  string `json:"requestId"`
	Target     string `json:"target"` // local|remote
	NodeID     string `json:"nodeId,omitempty"`
	Capability string `json:"capability"`
	Reason     string `json:"reason"`
	Fallback   bool   `json:"fallback"`
}

type NodeRevocation struct {
	NodeID string `json:"nodeId"`
	Reason string `json:"reason"`
	At     string `json:"at"`
}

// ── registry ────────────────────────────────────────────────────────────

// healthFreshness is how long a heartbeat stays valid. Past it, the node is
// degraded and receives no new jobs until it heartbeats again.
const healthFreshness = 45 * time.Second

type nodeRecord struct {
	Registration NodeRegistration
	Trust        NodeTrustBand
	Health       NodeHealth
	LastSeen     time.Time
	Local        bool
	Revocation   string
}

type NodeRegistry struct {
	mu    sync.Mutex
	nodes map[string]*nodeRecord
	now   func() time.Time
	// localNodeID names the co-located agent this operator starts with
	// dev-up. It is the ONLY node that may be auto-trusted, and only when it
	// also dispatches over loopback. A node cannot claim to be local: the
	// operator declares which id is local (CAMELOT_LOCAL_NODE_ID).
	localNodeID string
	dispatch    *http.Client
}

func NewNodeRegistry(now func() time.Time) *NodeRegistry {
	localID := os.Getenv("CAMELOT_LOCAL_NODE_ID")
	if localID == "" {
		localID = "local-node"
	}
	return &NodeRegistry{
		nodes:       map[string]*nodeRecord{},
		now:         now,
		localNodeID: localID,
		dispatch:    &http.Client{Timeout: 10 * time.Second},
	}
}

// isLocal is true only for the operator-declared local node reachable over
// loopback. Both conditions matter: the id stops a remote node from claiming
// locality, the loopback check stops a stale/hijacked local id from pointing
// the gateway at somebody else's host.
func (r *NodeRegistry) isLocal(reg NodeRegistration) bool {
	return reg.Identity.NodeID == r.localNodeID && isLoopbackURL(reg.DispatchURL)
}

func addressHash(url string) string {
	sum := sha256.Sum256([]byte(url))
	return hex.EncodeToString(sum[:])[:12]
}

var (
	ErrNodeUnknown      = fmt.Errorf("node is not registered")
	ErrNodeIdentityPin  = fmt.Errorf("node key fingerprint does not match the enrolled identity")
	ErrNodeNotEligible  = fmt.Errorf("node trust band does not permit this job")
	ErrNodeUnhealthy    = fmt.Errorf("node health is stale or degraded")
	ErrNodeCapability   = fmt.Errorf("node does not offer this capability")
	ErrNodeTenant       = fmt.Errorf("node belongs to a different tenant")
	ErrNodeReadOnlyOnly = fmt.Errorf("limited-trust nodes may only serve read-only capabilities")
)

// Register enrols or re-enrols a node. New nodes ALWAYS land in "pending":
// registering is not the same as being trusted. A re-registration must
// present the same key fingerprint, otherwise it is refused (identity pin).
func (r *NodeRegistry) Register(reg NodeRegistration) (NodeView, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	if reg.Identity.NodeID == "" || reg.Identity.TenantID == "" || reg.Identity.KeyFingerprint == "" {
		return NodeView{}, fmt.Errorf("nodeId, tenantId and keyFingerprint are required")
	}
	// Locality is decided here, from operator configuration — never from
	// anything the registering node asserts.
	local := r.isLocal(reg)
	now := r.now()
	existing, found := r.nodes[reg.Identity.NodeID]
	if found {
		if existing.Registration.Identity.KeyFingerprint != reg.Identity.KeyFingerprint {
			return NodeView{}, ErrNodeIdentityPin
		}
		if existing.Trust == TrustRevoked {
			return NodeView{}, fmt.Errorf("node is revoked: %s", existing.Revocation)
		}
		existing.Registration = reg
		existing.LastSeen = now
		existing.Health.Status = "healthy"
		existing.Health.ReportedAt = now.UTC().Format(time.RFC3339)
		if existing.Trust == TrustDegraded {
			existing.Trust = TrustLimited // recovered, but re-earn full trust
		}
		return r.viewLocked(existing), nil
	}

	trust := TrustPending
	if local {
		// The co-located agent is started by the same operator, on the same
		// box, by the same scripts — it is trusted by construction. Remote
		// nodes are never auto-trusted.
		trust = TrustTrusted
	}
	record := &nodeRecord{
		Registration: reg,
		Trust:        trust,
		Local:        local,
		LastSeen:     now,
		Health: NodeHealth{
			NodeID:     reg.Identity.NodeID,
			Status:     "healthy",
			ReportedAt: now.UTC().Format(time.RFC3339),
		},
	}
	r.nodes[reg.Identity.NodeID] = record
	return r.viewLocked(record), nil
}

func (r *NodeRegistry) Heartbeat(nodeID, fingerprint string, health NodeHealth) (NodeView, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	record, ok := r.nodes[nodeID]
	if !ok {
		return NodeView{}, ErrNodeUnknown
	}
	if record.Registration.Identity.KeyFingerprint != fingerprint {
		return NodeView{}, ErrNodeIdentityPin
	}
	if record.Trust == TrustRevoked {
		return NodeView{}, fmt.Errorf("node is revoked: %s", record.Revocation)
	}
	now := r.now()
	health.NodeID = nodeID
	health.ReportedAt = now.UTC().Format(time.RFC3339)
	record.Health = health
	record.LastSeen = now
	if record.Trust == TrustDegraded && health.Status == "healthy" {
		record.Trust = TrustLimited // health restored; operator re-promotes
	}
	return r.viewLocked(record), nil
}

// SetTrust is the operator control: pending -> limited -> trusted, or a
// manual demotion. Revocation is terminal and handled by Revoke.
func (r *NodeRegistry) SetTrust(nodeID string, band NodeTrustBand) (NodeView, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	record, ok := r.nodes[nodeID]
	if !ok {
		return NodeView{}, ErrNodeUnknown
	}
	if record.Trust == TrustRevoked {
		return NodeView{}, fmt.Errorf("node is revoked and cannot be re-trusted without re-enrolment")
	}
	switch band {
	case TrustPending, TrustLimited, TrustTrusted:
		record.Trust = band
	default:
		return NodeView{}, fmt.Errorf("trust band %q cannot be set manually", band)
	}
	return r.viewLocked(record), nil
}

func (r *NodeRegistry) Revoke(nodeID, reason string) (NodeRevocation, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	record, ok := r.nodes[nodeID]
	if !ok {
		return NodeRevocation{}, ErrNodeUnknown
	}
	record.Trust = TrustRevoked
	record.Revocation = reason
	return NodeRevocation{NodeID: nodeID, Reason: reason, At: r.now().UTC().Format(time.RFC3339)}, nil
}

func (r *NodeRegistry) List() []NodeView {
	r.mu.Lock()
	defer r.mu.Unlock()
	views := make([]NodeView, 0, len(r.nodes))
	for _, record := range r.nodes {
		views = append(views, r.viewLocked(record))
	}
	sort.Slice(views, func(i, j int) bool {
		if views[i].Local != views[j].Local {
			return views[i].Local // local node first
		}
		return views[i].NodeID < views[j].NodeID
	})
	return views
}

func (r *NodeRegistry) Get(nodeID string) (NodeView, bool) {
	r.mu.Lock()
	defer r.mu.Unlock()
	record, ok := r.nodes[nodeID]
	if !ok {
		return NodeView{}, false
	}
	return r.viewLocked(record), true
}

// viewLocked also applies the health-freshness rule: a node whose heartbeat
// has gone stale is reported (and treated) as degraded/offline, regardless
// of what it last claimed about itself.
func (r *NodeRegistry) viewLocked(record *nodeRecord) NodeView {
	health := record.Health.Status
	trust := record.Trust
	if trust != TrustRevoked && r.now().Sub(record.LastSeen) > healthFreshness {
		health = "offline"
		if trust == TrustTrusted || trust == TrustLimited || trust == TrustPending {
			trust = TrustDegraded
		}
	}
	return NodeView{
		NodeID:       record.Registration.Identity.NodeID,
		TenantID:     record.Registration.Identity.TenantID,
		DisplayName:  record.Registration.Identity.DisplayName,
		Trust:        trust,
		Health:       health,
		Local:        record.Local,
		Capabilities: record.Registration.Capabilities,
		AgentVersion: record.Registration.AgentVersion,
		MeshBackend:  record.Health.MeshBackend,
		LastSeen:     record.LastSeen.UTC().Format(time.RFC3339),
		AddressHash:  addressHash(record.Registration.DispatchURL),
		Revocation:   record.Revocation,
	}
}

// Eligible answers the only question that matters before dispatch: may THIS
// node do THIS capability for THIS tenant, right now? Every rejection is a
// typed error so the audit trail can say exactly why.
func (r *NodeRegistry) Eligible(nodeID, tenantID, capability string) error {
	r.mu.Lock()
	record, ok := r.nodes[nodeID]
	if !ok {
		r.mu.Unlock()
		return ErrNodeUnknown
	}
	view := r.viewLocked(record)
	capabilities := record.Registration.Capabilities
	r.mu.Unlock()

	if view.TenantID != tenantID {
		return ErrNodeTenant
	}
	switch view.Trust {
	case TrustRevoked:
		return fmt.Errorf("%w: node is revoked", ErrNodeNotEligible)
	case TrustPending:
		return fmt.Errorf("%w: node is pending operator approval", ErrNodeNotEligible)
	case TrustDegraded:
		return ErrNodeUnhealthy
	}
	if view.Health != "healthy" {
		return ErrNodeUnhealthy
	}

	var matched *NodeCapability
	for i := range capabilities {
		if capabilities[i].Name == capability {
			matched = &capabilities[i]
			break
		}
	}
	if matched == nil {
		return ErrNodeCapability
	}
	if view.Trust == TrustLimited && !matched.ReadOnly {
		return ErrNodeReadOnlyOnly
	}
	return nil
}

func (r *NodeRegistry) dispatchURL(nodeID string) (string, bool) {
	r.mu.Lock()
	defer r.mu.Unlock()
	record, ok := r.nodes[nodeID]
	if !ok {
		return "", false
	}
	return record.Registration.DispatchURL, true
}

// Dispatch sends a leased job to a node. The caller has already checked
// Eligible() and minted the lease. Remote failure is returned to the caller,
// which falls back locally — an effectful job is NEVER retried.
func (r *NodeRegistry) Dispatch(ctx context.Context, job NodeJobRequest) (NodeJobResult, error) {
	url, ok := r.dispatchURL(job.NodeID)
	if !ok {
		return NodeJobResult{}, ErrNodeUnknown
	}
	body, err := json.Marshal(job)
	if err != nil {
		return NodeJobResult{}, err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, strings.TrimRight(url, "/")+"/v1/node/job", bytes.NewReader(body))
	if err != nil {
		return NodeJobResult{}, err
	}
	req.Header.Set("Content-Type", "application/json")
	res, err := r.dispatch.Do(req)
	if err != nil {
		return NodeJobResult{}, fmt.Errorf("node unreachable: %w", err)
	}
	defer res.Body.Close()
	var result NodeJobResult
	if err := json.NewDecoder(res.Body).Decode(&result); err != nil {
		return NodeJobResult{}, fmt.Errorf("malformed node result: %w", err)
	}
	if res.StatusCode != http.StatusOK || !result.OK {
		if result.Failure == "" {
			result.Failure = fmt.Sprintf("node returned HTTP %d", res.StatusCode)
		}
		return result, fmt.Errorf("node rejected job: %s", result.Failure)
	}
	return result, nil
}
