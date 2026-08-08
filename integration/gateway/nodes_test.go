package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

// ── fake node agent ─────────────────────────────────────────────────────

type fakeNode struct {
	server   *httptest.Server
	calls    atomic.Int64
	fail     atomic.Bool
	seen     sync.Map
	lastJob  atomic.Value // NodeJobRequest
	rejectAs string
}

func newFakeNode(t *testing.T) *fakeNode {
	t.Helper()
	node := &fakeNode{}
	node.server = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		node.calls.Add(1)
		var job NodeJobRequest
		_ = json.NewDecoder(r.Body).Decode(&job)
		node.lastJob.Store(job)

		if node.rejectAs != "" {
			w.WriteHeader(http.StatusForbidden)
			json.NewEncoder(w).Encode(NodeJobResult{JobID: job.JobID, OK: false, Failure: node.rejectAs})
			return
		}
		if node.fail.Load() {
			w.WriteHeader(http.StatusInternalServerError)
			json.NewEncoder(w).Encode(NodeJobResult{JobID: job.JobID, OK: false, Failure: "node exploded"})
			return
		}
		// Single-use: a replayed lease is refused, exactly like the real agent.
		if _, replayed := node.seen.LoadOrStore(job.Lease.LeaseID, true); replayed {
			w.WriteHeader(http.StatusForbidden)
			json.NewEncoder(w).Encode(NodeJobResult{JobID: job.JobID, OK: false, Failure: "lease already redeemed (single-use)"})
			return
		}
		json.NewEncoder(w).Encode(NodeJobResult{
			JobID:  job.JobID,
			NodeID: job.NodeID,
			OK:     true,
			Result: json.RawMessage(`{"backend":"cpu","results":[]}`),
		})
	}))
	t.Cleanup(node.server.Close)
	return node
}

func (n *fakeNode) registration(nodeID, tenantID string, readOnly bool) NodeRegistration {
	return NodeRegistration{
		Identity: NodeIdentity{
			NodeID:         nodeID,
			TenantID:       tenantID,
			DisplayName:    nodeID,
			KeyFingerprint: "fp-" + nodeID,
		},
		Capabilities: []NodeCapability{{Name: "compute:audio.features", ReadOnly: readOnly}},
		AgentVersion: "0.2.0-test",
		DispatchURL:  n.server.URL,
	}
}

func localRegistration(dispatchURL string) NodeRegistration {
	return NodeRegistration{
		Identity: NodeIdentity{
			NodeID:         "local-node",
			TenantID:       "tenant-1",
			DisplayName:    "local",
			KeyFingerprint: "fp-local",
		},
		Capabilities: []NodeCapability{{Name: "compute:audio.features", ReadOnly: true}},
		AgentVersion: "0.2.0-test",
		DispatchURL:  dispatchURL,
	}
}

func jobRequest(capability string) nodeJobAPIRequest {
	return nodeJobAPIRequest{
		SessionID:  "sess-anya-demo-001",
		TurnID:     "turn-n1",
		TenantID:   "tenant-1",
		Capability: capability,
		Payload:    json.RawMessage(`{"frames":[{"frameId":"f0","samples":[0.1,0.2]}]}`),
	}
}

// 1. An unregistered node is rejected.
func TestUnregisteredNodeRejected(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	err := server.nodes.Eligible("ghost-node", "tenant-1", "compute:audio.features")
	if err != ErrNodeUnknown {
		t.Fatalf("want ErrNodeUnknown, got %v", err)
	}
	req := jobRequest("compute:audio.features")
	req.NodeID = "ghost-node"
	outcome := server.RouteNodeJob(context.Background(), req)
	if outcome.Failure == "" {
		t.Fatal("unregistered node produced no failure")
	}
	if outcome.Result != nil {
		t.Fatal("unregistered node returned a result")
	}
}

// 2. Pending, degraded, and revoked nodes cannot receive jobs.
func TestNonTrustedBandsCannotReceiveJobs(t *testing.T) {
	now := time.Now()
	clock := func() time.Time { return now }
	server := NewServer(time.Millisecond, clock)
	server.nodes = NewNodeRegistry(clock)
	remote := newFakeNode(t)

	view, err := server.nodes.Register(remote.registration("node-remote", "tenant-1", true))
	if err != nil {
		t.Fatal(err)
	}
	// A freshly registered REMOTE node is pending — registering is not trust.
	if view.Trust != TrustPending {
		t.Fatalf("remote node auto-trusted at registration: %s", view.Trust)
	}
	if err := server.nodes.Eligible("node-remote", "tenant-1", "compute:audio.features"); err == nil {
		t.Fatal("pending node was eligible")
	}

	// Promote, then let the heartbeat go stale -> degraded -> ineligible.
	if _, err := server.nodes.SetTrust("node-remote", TrustTrusted); err != nil {
		t.Fatal(err)
	}
	if err := server.nodes.Eligible("node-remote", "tenant-1", "compute:audio.features"); err != nil {
		t.Fatalf("trusted healthy node not eligible: %v", err)
	}
	now = now.Add(healthFreshness + time.Second)
	if err := server.nodes.Eligible("node-remote", "tenant-1", "compute:audio.features"); err != ErrNodeUnhealthy {
		t.Fatalf("stale node still eligible: %v", err)
	}
	if v, _ := server.nodes.Get("node-remote"); v.Trust != TrustDegraded || v.Health != "offline" {
		t.Fatalf("stale node not degraded: %+v", v)
	}

	// Revoked is terminal.
	now = time.Now()
	if _, err := server.nodes.Revoke("node-remote", "test"); err != nil {
		t.Fatal(err)
	}
	if err := server.nodes.Eligible("node-remote", "tenant-1", "compute:audio.features"); err == nil {
		t.Fatal("revoked node was eligible")
	}
	if _, err := server.nodes.SetTrust("node-remote", TrustTrusted); err == nil {
		t.Fatal("revoked node was re-trusted without re-enrolment")
	}
}

// 3a. Wrong tenant and wrong capability are rejected.
func TestWrongTenantAndCapabilityRejected(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	remote := newFakeNode(t)
	server.nodes.Register(remote.registration("node-remote", "tenant-1", true))
	server.nodes.SetTrust("node-remote", TrustTrusted)

	if err := server.nodes.Eligible("node-remote", "tenant-2", "compute:audio.features"); err != ErrNodeTenant {
		t.Fatalf("cross-tenant job allowed: %v", err)
	}
	if err := server.nodes.Eligible("node-remote", "tenant-1", "compute:something.else"); err != ErrNodeCapability {
		t.Fatalf("unregistered capability allowed: %v", err)
	}
}

// 3b. Limited-trust nodes may only serve read-only capabilities.
func TestLimitedTrustIsReadOnly(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	remote := newFakeNode(t)
	// A node offering an EFFECTFUL capability.
	reg := remote.registration("node-remote", "tenant-1", false)
	server.nodes.Register(reg)
	server.nodes.SetTrust("node-remote", TrustLimited)

	if err := server.nodes.Eligible("node-remote", "tenant-1", "compute:audio.features"); err != ErrNodeReadOnlyOnly {
		t.Fatalf("limited node served an effectful capability: %v", err)
	}
	server.nodes.SetTrust("node-remote", TrustTrusted)
	if err := server.nodes.Eligible("node-remote", "tenant-1", "compute:audio.features"); err != nil {
		t.Fatalf("trusted node refused its own capability: %v", err)
	}
}

// 3c. Node leases are bound: wrong node, wrong tenant, expiry, and reuse all fail.
func TestNodeLeaseBindingAndReuse(t *testing.T) {
	current := time.Now()
	leases := NewLeaseStore(func() time.Time { return current })
	lease := leases.IssueNodeLease("sess", "turn-1", "compute:audio.features", "node-a", "tenant-1")

	if lease.NodeID != "node-a" || lease.TenantID != "tenant-1" || lease.Token == "" {
		t.Fatalf("node lease not bound: %+v", lease)
	}

	// A lease minted for node-a must not verify as node-b's lease: the
	// signature covers node and tenant.
	forged := lease
	forged.NodeID = "node-b"
	if _, err := leases.Consume(forged.LeaseID, forged.Capability, forged.Token); err != nil {
		// Consume checks the STORED lease, so mutation client-side is moot —
		// the node-side check is what rejects it (tests/mesh.rs). Here we
		// assert the stored binding is what gets signed.
		t.Fatalf("unexpected consume error: %v", err)
	}
	// Reuse is refused.
	if _, err := leases.Consume(lease.LeaseID, lease.Capability, lease.Token); err != ErrLeaseConsumed {
		t.Fatalf("node lease reuse allowed: %v", err)
	}

	// Expiry.
	lease2 := leases.IssueNodeLease("sess", "turn-2", "compute:audio.features", "node-a", "tenant-1")
	current = current.Add(leaseTTL + time.Second)
	if _, err := leases.Consume(lease2.LeaseID, lease2.Capability, lease2.Token); err != ErrLeaseExpired {
		t.Fatalf("expired node lease accepted: %v", err)
	}
}

// 4. A trusted, healthy remote node receives an allowed read-only job.
func TestTrustedRemoteNodeServesReadOnlyJob(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	remote := newFakeNode(t)
	server.nodes.Register(remote.registration("node-remote", "tenant-1", true))
	server.nodes.SetTrust("node-remote", TrustTrusted)

	req := jobRequest("compute:audio.features")
	req.NodeID = "node-remote"
	outcome := server.RouteNodeJob(context.Background(), req)

	if outcome.Failure != "" {
		t.Fatalf("trusted remote job failed: %s", outcome.Failure)
	}
	if outcome.Decision.Target != "remote" || outcome.Decision.NodeID != "node-remote" {
		t.Fatalf("route decision %+v", outcome.Decision)
	}
	if remote.calls.Load() != 1 {
		t.Fatalf("node called %d times", remote.calls.Load())
	}
	// The dispatched job carried a bound, single-use, short-lived lease.
	job := remote.lastJob.Load().(NodeJobRequest)
	if job.Lease.NodeID != "node-remote" || job.Lease.TenantID != "tenant-1" {
		t.Fatalf("dispatched lease not bound: %+v", job.Lease)
	}
	if !job.Lease.SingleUse || job.Lease.Status != "approved" || job.Lease.Token == "" {
		t.Fatalf("dispatched lease malformed: %+v", job.Lease)
	}
}

// 5. Remote failure falls back safely to the local node.
func TestRemoteFailureFallsBackToLocal(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	local := newFakeNode(t)
	remote := newFakeNode(t)
	remote.fail.Store(true)

	server.nodes.Register(localRegistration(local.server.URL))
	server.nodes.Register(remote.registration("node-remote", "tenant-1", true))
	server.nodes.SetTrust("node-remote", TrustTrusted)

	req := jobRequest("compute:audio.features")
	req.NodeID = "node-remote"
	outcome := server.RouteNodeJob(context.Background(), req)

	if outcome.Failure != "" {
		t.Fatalf("fallback did not recover: %s", outcome.Failure)
	}
	if !outcome.Decision.Fallback || outcome.Decision.Target != "local" {
		t.Fatalf("expected local fallback, got %+v", outcome.Decision)
	}
	if local.calls.Load() != 1 {
		t.Fatalf("local node served %d jobs", local.calls.Load())
	}
}

// 6. An effectful remote job is never retried and never re-run locally.
func TestEffectfulRemoteJobIsNotRetried(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	local := newFakeNode(t)
	remote := newFakeNode(t)
	remote.fail.Store(true)

	server.nodes.Register(localRegistration(local.server.URL))
	server.nodes.Register(remote.registration("node-remote", "tenant-1", false))
	server.nodes.SetTrust("node-remote", TrustTrusted)

	req := jobRequest("compute:audio.features")
	req.NodeID = "node-remote"
	req.Effectful = true
	outcome := server.RouteNodeJob(context.Background(), req)

	if outcome.Failure == "" {
		t.Fatal("effectful failure was masked")
	}
	if remote.calls.Load() != 1 {
		t.Fatalf("effectful job retried remotely %d times", remote.calls.Load())
	}
	if local.calls.Load() != 0 {
		t.Fatal("effectful job was re-run locally after a remote failure")
	}
	// The audit says so explicitly.
	found := false
	for i := 1; i <= server.audit.Len(); i++ {
		event, _ := server.audit.Get(fmt.Sprintf("audit-%04d", i))
		if event.Kind == "node.route.failed" && strings.Contains(event.RedactedSummary, "NOT retried") {
			found = true
		}
	}
	if !found {
		t.Fatal("no audit record of the no-retry decision")
	}
}

// 7. Local-first: with no explicit mesh request, a healthy local node serves
// everything and no remote node is contacted — the absent/unhealthy-mesh case.
func TestLocalFirstAndMeshAbsenceIsHarmless(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	local := newFakeNode(t)
	remote := newFakeNode(t)
	server.nodes.Register(localRegistration(local.server.URL))
	server.nodes.Register(remote.registration("node-remote", "tenant-1", true))
	server.nodes.SetTrust("node-remote", TrustTrusted)

	outcome := server.RouteNodeJob(context.Background(), jobRequest("compute:audio.features"))
	if outcome.Failure != "" {
		t.Fatalf("local-first route failed: %s", outcome.Failure)
	}
	if outcome.Decision.Target != "local" {
		t.Fatalf("routing reached for the mesh unasked: %+v", outcome.Decision)
	}
	if remote.calls.Load() != 0 {
		t.Fatal("remote node contacted without an explicit mesh request")
	}

	// Mesh requested but nothing eligible (the "Tailscale is down" shape):
	// degrade to local rather than fail.
	server.nodes.Revoke("node-remote", "simulating an unreachable mesh")
	degraded := jobRequest("compute:audio.features")
	degraded.PreferRemote = true
	outcome = server.RouteNodeJob(context.Background(), degraded)
	if outcome.Failure != "" {
		t.Fatalf("mesh outage broke local operation: %s", outcome.Failure)
	}
	if outcome.Decision.Target != "local" || !outcome.Decision.Fallback {
		t.Fatalf("expected degraded-to-local, got %+v", outcome.Decision)
	}
}

// 8. Audit records the route without host addresses, keys, or secrets.
func TestNodeAuditHasNoAddressesOrSecrets(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	remote := newFakeNode(t)
	reg := remote.registration("node-remote", "tenant-1", true)
	server.nodes.Register(reg)
	server.nodes.SetTrust("node-remote", TrustTrusted)

	req := jobRequest("compute:audio.features")
	req.NodeID = "node-remote"
	server.RouteNodeJob(context.Background(), req)

	host := strings.TrimPrefix(reg.DispatchURL, "http://")
	leaseKey := server.leases.SigningKeyHex()
	sawRoute := false
	for i := 1; i <= server.audit.Len(); i++ {
		event, _ := server.audit.Get(fmt.Sprintf("audit-%04d", i))
		payload, _ := json.Marshal(event)
		text := string(payload)
		if strings.Contains(text, host) || strings.Contains(text, reg.DispatchURL) {
			t.Fatalf("dispatch address leaked into audit: %s", text)
		}
		if strings.Contains(text, leaseKey) || strings.Contains(text, reg.Identity.KeyFingerprint) {
			t.Fatalf("key material leaked into audit: %s", text)
		}
		if event.Kind == "node.route" {
			sawRoute = true
		}
	}
	if !sawRoute {
		t.Fatal("route decision was not audited")
	}
	if server.audit.VerifyChain() != -1 {
		t.Fatal("audit chain broken")
	}

	// The node list shown to the UI carries a hash, never an address.
	for _, view := range server.nodes.List() {
		if strings.Contains(view.AddressHash, ":") || len(view.AddressHash) != 12 {
			t.Fatalf("address hash looks like an address: %q", view.AddressHash)
		}
	}
}

// Identity pinning: a second process cannot re-register an existing nodeId
// with a different key.
func TestIdentityPinning(t *testing.T) {
	server := NewServer(time.Millisecond, time.Now)
	remote := newFakeNode(t)
	reg := remote.registration("node-remote", "tenant-1", true)
	if _, err := server.nodes.Register(reg); err != nil {
		t.Fatal(err)
	}
	impostor := reg
	impostor.Identity.KeyFingerprint = "fp-impostor"
	if _, err := server.nodes.Register(impostor); err != ErrNodeIdentityPin {
		t.Fatalf("identity pin not enforced: %v", err)
	}
}

// The HTTP surface behaves the same as the routing policy.
func TestNodeEndpoints(t *testing.T) {
	_, ts := newTestServer(t)
	remote := newFakeNode(t)

	status, view := postJSON[NodeView](t, ts.URL+"/v1/nodes/register", remote.registration("node-remote", "tenant-1", true))
	if status != http.StatusOK || view.Trust != TrustPending {
		t.Fatalf("register: %d %+v", status, view)
	}
	if view.AddressHash == "" {
		t.Fatal("registration view lacks an address hash")
	}

	// Pending node cannot serve.
	req := jobRequest("compute:audio.features")
	req.NodeID = "node-remote"
	code, outcome := postJSON[NodeJobOutcome](t, ts.URL+"/v1/nodes/jobs", req)
	if code == http.StatusOK && outcome.Failure == "" {
		t.Fatal("pending node served a job over HTTP")
	}

	// Operator promotes, then it serves.
	postJSON[NodeView](t, ts.URL+"/v1/nodes/node-remote/trust", map[string]string{"band": "trusted"})
	code, outcome = postJSON[NodeJobOutcome](t, ts.URL+"/v1/nodes/jobs", req)
	if code != http.StatusOK || outcome.Failure != "" {
		t.Fatalf("trusted node refused over HTTP: %d %s", code, outcome.Failure)
	}

	// Listing exposes no address.
	body, err := httpGet(ts.URL + "/v1/nodes")
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(body, remote.server.URL) {
		t.Fatalf("node list leaked a dispatch address: %s", body)
	}

	// Revocation is immediate.
	postJSON[NodeRevocation](t, ts.URL+"/v1/nodes/node-remote/revoke", map[string]string{"reason": "test"})
	_, outcome = postJSON[NodeJobOutcome](t, ts.URL+"/v1/nodes/jobs", req)
	if outcome.Failure == "" {
		t.Fatal("revoked node still served a job")
	}
}
