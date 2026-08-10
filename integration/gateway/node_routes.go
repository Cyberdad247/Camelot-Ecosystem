package main

// Phase 4A HTTP surface for mesh nodes plus the local-first routing policy.
// Every registration, heartbeat, trust change, route decision, dispatch,
// result, rejection, degradation, and revocation is audited — with hashed
// addresses only, never a host address, key, or secret.

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

const nodeJobTimeout = 15 * time.Second

// NodeJobOutcome is what the routing policy returns to a caller.
type NodeJobOutcome struct {
	Decision NodeRouteDecision `json:"decision"`
	Result   json.RawMessage   `json:"result,omitempty"`
	AuditID  string            `json:"auditId"`
	Failure  string            `json:"failure,omitempty"`
}

type nodeJobAPIRequest struct {
	SessionID  string          `json:"sessionId"`
	TurnID     string          `json:"turnId"`
	TenantID   string          `json:"tenantId"`
	Capability string          `json:"capability"`
	Payload    json.RawMessage `json:"payload"`
	// PreferRemote asks for the mesh explicitly. Absent it, routing is
	// local-first and never reaches for a remote node on its own.
	PreferRemote bool   `json:"preferRemote,omitempty"`
	NodeID       string `json:"nodeId,omitempty"`
	// Effectful jobs are never retried anywhere, and never fall back after a
	// remote attempt (the remote side may have already applied them).
	Effectful bool `json:"effectful,omitempty"`
}

func (s *Server) registerNodeRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /v1/nodes/register", s.handleNodeRegister)
	mux.HandleFunc("POST /v1/nodes/{id}/heartbeat", s.handleNodeHeartbeat)
	mux.HandleFunc("GET /v1/nodes", s.handleNodeList)
	mux.HandleFunc("POST /v1/nodes/{id}/trust", s.handleNodeTrust)
	mux.HandleFunc("POST /v1/nodes/{id}/revoke", s.handleNodeRevoke)
	mux.HandleFunc("POST /v1/nodes/jobs", s.handleNodeJob)
}

func (s *Server) handleNodeRegister(w http.ResponseWriter, r *http.Request) {
	var reg NodeRegistration
	if err := json.NewDecoder(r.Body).Decode(&reg); err != nil {
		httpError(w, http.StatusBadRequest, "invalid NodeRegistration: "+err.Error())
		return
	}
	view, err := s.nodes.Register(reg)
	if err != nil {
		s.auditNode("node.register.rejected", reg.Identity.NodeID,
			fmt.Sprintf("registration refused for %s: %v", safeNodeID(reg.Identity.NodeID), err))
		httpError(w, http.StatusForbidden, err.Error())
		return
	}
	s.auditNode("node.registered", view.NodeID, fmt.Sprintf(
		"node %s (tenant %s, %s) enrolled in band %s with %d capabilities; addr %s",
		view.NodeID, view.TenantID, view.AgentVersion, view.Trust, len(view.Capabilities), view.AddressHash))
	writeJSON(w, http.StatusOK, view)
}

func (s *Server) handleNodeHeartbeat(w http.ResponseWriter, r *http.Request) {
	var payload struct {
		KeyFingerprint string     `json:"keyFingerprint"`
		Health         NodeHealth `json:"health"`
	}
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		httpError(w, http.StatusBadRequest, "invalid heartbeat: "+err.Error())
		return
	}
	nodeID := r.PathValue("id")
	before, _ := s.nodes.Get(nodeID)
	view, err := s.nodes.Heartbeat(nodeID, payload.KeyFingerprint, payload.Health)
	if err != nil {
		httpError(w, http.StatusForbidden, err.Error())
		return
	}
	// Only audit transitions, not every heartbeat — the log stays readable.
	if before.Health != view.Health || before.Trust != view.Trust {
		s.auditNode("node.health", nodeID, fmt.Sprintf(
			"node %s health %s->%s, trust %s->%s (mesh: %s)",
			nodeID, orNone(before.Health), view.Health, orNone(string(before.Trust)), view.Trust, orNone(view.MeshBackend)))
	}
	writeJSON(w, http.StatusOK, view)
}

func (s *Server) handleNodeList(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{"nodes": s.nodes.List()})
}

func (s *Server) handleNodeTrust(w http.ResponseWriter, r *http.Request) {
	var payload struct {
		Band NodeTrustBand `json:"band"`
	}
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		httpError(w, http.StatusBadRequest, "invalid trust request: "+err.Error())
		return
	}
	nodeID := r.PathValue("id")
	before, _ := s.nodes.Get(nodeID)
	view, err := s.nodes.SetTrust(nodeID, payload.Band)
	if err != nil {
		httpError(w, http.StatusConflict, err.Error())
		return
	}
	s.auditNode("node.trust", nodeID, fmt.Sprintf(
		"operator moved node %s from band %s to %s", nodeID, orNone(string(before.Trust)), view.Trust))
	writeJSON(w, http.StatusOK, view)
}

func (s *Server) handleNodeRevoke(w http.ResponseWriter, r *http.Request) {
	var payload struct {
		Reason string `json:"reason"`
	}
	_ = json.NewDecoder(r.Body).Decode(&payload)
	if payload.Reason == "" {
		payload.Reason = "operator revocation"
	}
	nodeID := r.PathValue("id")
	revocation, err := s.nodes.Revoke(nodeID, payload.Reason)
	if err != nil {
		httpError(w, http.StatusNotFound, err.Error())
		return
	}
	s.auditNode("node.revoked", nodeID, fmt.Sprintf("node %s revoked: %s", nodeID, payload.Reason))
	writeJSON(w, http.StatusOK, revocation)
}

func (s *Server) handleNodeJob(w http.ResponseWriter, r *http.Request) {
	var req nodeJobAPIRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		httpError(w, http.StatusBadRequest, "invalid node job request: "+err.Error())
		return
	}
	if req.Capability == "" || req.TenantID == "" {
		httpError(w, http.StatusBadRequest, "tenantId and capability are required")
		return
	}
	outcome := s.RouteNodeJob(r.Context(), req)
	status := http.StatusOK
	if outcome.Failure != "" && outcome.Result == nil {
		status = http.StatusBadGateway
	}
	writeJSON(w, status, outcome)
}

// RouteNodeJob is the routing policy: LOCAL FIRST, always. A remote node is
// considered only when the caller explicitly asks for the mesh (or names a
// node), and only when that node is trusted-or-limited-appropriate, healthy,
// same-tenant, and offers the capability. Remote failure falls back to the
// local node for read-only work; an effectful job never falls back and never
// retries, because the remote side may already have applied it.
func (s *Server) RouteNodeJob(ctx context.Context, req nodeJobAPIRequest) NodeJobOutcome {
	s.nodeSeq.Add(1)
	requestID := fmt.Sprintf("nreq-%04d", s.nodeSeq.Load())

	local, hasLocal := s.localNode()
	wantsRemote := req.PreferRemote || req.NodeID != ""

	if !wantsRemote {
		if !hasLocal {
			return s.nodeFailure(requestID, req, "no local node is registered")
		}
		return s.dispatchTo(ctx, requestID, local.NodeID, req, "local-first routing", false)
	}

	candidate := req.NodeID
	if candidate == "" {
		candidate = s.pickRemote(req.TenantID, req.Capability)
	}
	if candidate == "" {
		// Nothing eligible in the mesh: degrade to local rather than fail.
		if hasLocal {
			decision := "no eligible remote node; degraded to local"
			s.auditNode("node.route.degraded", "", fmt.Sprintf(
				"%s: capability %s had no eligible remote node; served locally", requestID, req.Capability))
			return s.dispatchTo(ctx, requestID, local.NodeID, req, decision, true)
		}
		return s.nodeFailure(requestID, req, "no eligible node for capability "+req.Capability)
	}

	if err := s.nodes.Eligible(candidate, req.TenantID, req.Capability); err != nil {
		s.auditNode("node.route.rejected", candidate, fmt.Sprintf(
			"%s: node %s refused for capability %s: %v", requestID, candidate, req.Capability, err))
		// Naming a node is a REQUIREMENT, not a hint: if that specific node
		// may not serve the job, the job fails. Quietly running it somewhere
		// else would defeat the point of naming it.
		if req.NodeID != "" {
			return s.nodeFailure(requestID, req, err.Error())
		}
		if hasLocal && !req.Effectful {
			return s.dispatchTo(ctx, requestID, local.NodeID, req, "no eligible remote node ("+err.Error()+"); local fallback", true)
		}
		return s.nodeFailure(requestID, req, err.Error())
	}

	outcome := s.dispatchTo(ctx, requestID, candidate, req, "explicit mesh request", false)
	if outcome.Failure == "" {
		return outcome
	}
	// Remote attempt failed AFTER dispatch.
	if req.Effectful {
		// Never retried, never re-run locally: the remote may have applied it.
		s.auditNode("node.route.failed", candidate, fmt.Sprintf(
			"%s: effectful job on %s failed (%s); NOT retried and NOT re-run locally",
			requestID, candidate, outcome.Failure))
		return outcome
	}
	if !hasLocal {
		return outcome
	}
	s.auditNode("node.route.fallback", candidate, fmt.Sprintf(
		"%s: remote %s failed (%s); read-only job re-served locally", requestID, candidate, outcome.Failure))
	return s.dispatchTo(ctx, requestID, local.NodeID, req, "remote failed; local fallback", true)
}

func (s *Server) dispatchTo(ctx context.Context, requestID, nodeID string, req nodeJobAPIRequest, reason string, fallback bool) NodeJobOutcome {
	target := "remote"
	if view, ok := s.nodes.Get(nodeID); ok && view.Local {
		target = "local"
	}
	decision := NodeRouteDecision{
		RequestID:  requestID,
		Target:     target,
		NodeID:     nodeID,
		Capability: req.Capability,
		Reason:     reason,
		Fallback:   fallback,
	}

	if err := s.nodes.Eligible(nodeID, req.TenantID, req.Capability); err != nil {
		event := s.auditNode("node.route.rejected", nodeID, fmt.Sprintf(
			"%s: node %s not eligible for %s: %v", requestID, nodeID, req.Capability, err))
		return NodeJobOutcome{Decision: decision, AuditID: event.AuditID, Failure: err.Error()}
	}

	// One lease, one node, one tenant, one capability, one use, 30 seconds.
	lease := s.leases.IssueNodeLease(req.SessionID, req.TurnID, req.Capability, nodeID, req.TenantID)
	routeEvent := s.auditNode("node.route", nodeID, fmt.Sprintf(
		"%s: %s job %s routed to %s node %s under lease %s (fallback=%t)",
		requestID, req.Capability, orNone(req.TurnID), target, nodeID, lease.LeaseID, fallback))

	jobCtx, cancel := context.WithTimeout(ctx, nodeJobTimeout)
	defer cancel()
	result, err := s.nodes.Dispatch(jobCtx, NodeJobRequest{
		JobID:      requestID,
		NodeID:     nodeID,
		TenantID:   req.TenantID,
		Capability: req.Capability,
		Lease:      lease,
		Payload:    req.Payload,
	})
	if err != nil {
		// The lease dies with the failed attempt — it is never reissued or
		// reused, so a failure can never become a second execution.
		s.leases.Revoke(lease.LeaseID)
		event := s.auditNode("node.job.failed", nodeID, fmt.Sprintf(
			"%s: node %s failed %s under lease %s: %v (lease revoked)",
			requestID, nodeID, req.Capability, lease.LeaseID, err))
		return NodeJobOutcome{Decision: decision, AuditID: event.AuditID, Failure: err.Error()}
	}

	event := s.auditNode("node.job.completed", nodeID, fmt.Sprintf(
		"%s: node %s completed %s under lease %s", requestID, nodeID, req.Capability, lease.LeaseID))
	_ = routeEvent
	return NodeJobOutcome{Decision: decision, Result: result.Result, AuditID: event.AuditID}
}

func (s *Server) nodeFailure(requestID string, req nodeJobAPIRequest, reason string) NodeJobOutcome {
	event := s.auditNode("node.route.failed", "", fmt.Sprintf(
		"%s: no route for capability %s: %s", requestID, req.Capability, reason))
	return NodeJobOutcome{
		Decision: NodeRouteDecision{RequestID: requestID, Target: "none", Capability: req.Capability, Reason: reason},
		AuditID:  event.AuditID,
		Failure:  reason,
	}
}

func (s *Server) localNode() (NodeView, bool) {
	for _, view := range s.nodes.List() {
		if view.Local && view.Health == "healthy" {
			return view, true
		}
	}
	return NodeView{}, false
}

// pickRemote chooses the first trusted, healthy, same-tenant remote node
// offering the capability. Deterministic order (registry List is sorted) —
// no load balancing in Phase 4A, on purpose.
func (s *Server) pickRemote(tenantID, capability string) string {
	for _, view := range s.nodes.List() {
		if view.Local {
			continue
		}
		if s.nodes.Eligible(view.NodeID, tenantID, capability) == nil {
			return view.NodeID
		}
	}
	return ""
}

func (s *Server) auditNode(kind, nodeID, summary string) AuditEvent {
	event := s.audit.Append(auditEntry{
		SessionID:       "mesh",
		Kind:            kind,
		RedactedSummary: summary,
	})
	s.sessions.Publish("mesh", SessionEvent{Type: "audit.appended", AuditID: event.AuditID, Kind: kind})
	return event
}

func isLoopbackURL(url string) bool {
	for _, prefix := range []string{"http://localhost:", "http://127.0.0.1:", "http://[::1]:"} {
		if len(url) >= len(prefix) && url[:len(prefix)] == prefix {
			return true
		}
	}
	return false
}

func safeNodeID(id string) string {
	if id == "" {
		return "<unnamed>"
	}
	return id
}

func orNone(v string) string {
	if v == "" {
		return "none"
	}
	return v
}
