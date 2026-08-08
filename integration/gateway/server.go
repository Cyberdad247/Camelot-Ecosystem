package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync/atomic"
	"time"
)

const (
	serviceName    = "camelot-voice-gateway"
	serviceVersion = "0.1.0"
	policyVersion  = "v1"
)

// Server wires policy, leases, tools, audit, and sessions behind the
// governed HTTP surface. It is the single authority (ADR-001): the PWA and
// Hermes have no other path to effectful execution.
type Server struct {
	leases   *LeaseStore
	broker   *ToolBroker
	audit    *AuditLog
	sessions *SessionHub
	models   *ModelRouter
	nodes    *NodeRegistry
	now      func() time.Time
	decSeq   atomic.Int64
	nodeSeq  atomic.Int64
}

func NewServer(chunkDelay time.Duration, now func() time.Time) *Server {
	leases := NewLeaseStore(now)
	return &Server{
		leases:   leases,
		broker:   NewToolBroker(leases),
		audit:    NewAuditLog(now),
		sessions: NewSessionHub(chunkDelay),
		models:   NewModelRouter(chunkDelay), // deterministic-only default
		nodes:    NewNodeRegistry(now),
		now:      now,
	}
}

// NewPersistentServer is NewServer with the audit chain mirrored into a
// local SQLite file (νKG native runtime: durable redacted audit, no remote DB).
func NewPersistentServer(chunkDelay time.Duration, now func() time.Time, auditDBPath string) (*Server, error) {
	audit, err := openAuditStore(auditDBPath, now)
	if err != nil {
		return nil, err
	}
	leases := NewLeaseStore(now)
	return &Server{
		leases:   leases,
		broker:   NewToolBroker(leases),
		audit:    audit,
		sessions: NewSessionHub(chunkDelay),
		models:   NewModelRouter(chunkDelay),
		nodes:    NewNodeRegistry(now),
		now:      now,
	}, nil
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", s.handleHealth)
	mux.HandleFunc("POST /v1/voice/turns", s.handleTurn)
	mux.HandleFunc("POST /v1/voice/barge-in", s.handleBargeIn)
	mux.HandleFunc("POST /v1/confirmations", s.handleConfirmation)
	mux.HandleFunc("GET /v1/audit/{id}", s.handleAudit)
	mux.HandleFunc("GET /v1/sessions/{id}/events", s.handleSessionEvents)
	mux.HandleFunc("GET /v1/models/stats", s.handleModelStats)
	s.registerNodeRoutes(mux)
	return withCORS(mux)
}

// withCORS allows the Anya Console (a different local origin) to call the
// gateway. Demo-scope: permissive; production hardening is out of scope.
func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "content-type")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func (s *Server) handleHealth(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, HealthResponse{Status: "ok", Service: serviceName, Version: serviceVersion})
}

func (s *Server) nextDecision(effect, skillID string, tier int, reason string) PolicyDecision {
	seq := s.decSeq.Add(1)
	return PolicyDecision{
		DecisionID:    fmt.Sprintf("dec-%04d", seq),
		Effect:        effect,
		SkillID:       skillID,
		Tier:          tier,
		Reason:        reason,
		PolicyVersion: policyVersion,
		DecidedAt:     s.now().UTC().Format(time.RFC3339),
	}
}

func (s *Server) handleTurn(w http.ResponseWriter, r *http.Request) {
	var turn VoiceTurn
	if err := json.NewDecoder(r.Body).Decode(&turn); err != nil {
		httpError(w, http.StatusBadRequest, "invalid VoiceTurn body: "+err.Error())
		return
	}
	if turn.SessionID == "" || turn.TurnID == "" || strings.TrimSpace(turn.Transcript) == "" {
		httpError(w, http.StatusBadRequest, "sessionId, turnId and transcript are required")
		return
	}
	if turn.Modality != "text" && turn.Modality != "voice" {
		httpError(w, http.StatusBadRequest, `modality must be "text" or "voice"`)
		return
	}

	s.sessions.Publish(turn.SessionID, SessionEvent{Type: "turn.accepted", TurnID: turn.TurnID})

	// Hermes proposes; policy disposes.
	proposal := hermesMatchIntent(turn.Transcript)

	if !proposal.Matched {
		decision := s.nextDecision("allow", "none.smalltalk", 1, "no governed skill matched; conversational reply")
		reply := hermesSmallTalkReply()
		auditEvent := s.audit.Append(auditEntry{
			SessionID:       turn.SessionID,
			TurnID:          turn.TurnID,
			Kind:            "turn.received",
			Transcript:      turn.Transcript,
			RedactedSummary: "small talk (no skill matched)",
			Decision:        &decision,
		})
		s.publishDecisionAndAudit(turn.SessionID, turn.TurnID, decision, auditEvent)
		writeJSON(w, http.StatusOK, CamelotTurnResponse{
			SessionID: turn.SessionID,
			TurnID:    turn.TurnID,
			UIState:   "speaking",
			Decision:  decision,
			Reply:     s.narrate(turn.SessionID, turn.TurnID, turn.Transcript, reply),
			AuditID:   auditEvent.AuditID,
		})
		return
	}

	skill, _ := skillByID(proposal.SkillID)
	capability := "skill:" + skill.ID

	switch {
	case !skill.Effectful:
		// Tier 1: read-only, no lease required (ADR-001 rule 1).
		decision := s.nextDecision("allow", skill.ID, skill.Tier, "tier-1 read-only skill; no lease required")
		artifact, reply, err := s.broker.Execute(skill.ID, turn.TurnID, nil)
		if err != nil {
			httpError(w, http.StatusInternalServerError, err.Error())
			return
		}
		auditEvent := s.audit.Append(auditEntry{
			SessionID:       turn.SessionID,
			TurnID:          turn.TurnID,
			Kind:            "tool.executed",
			Transcript:      turn.Transcript,
			RedactedSummary: fmt.Sprintf("tier-1 read %s: %q", skill.ID, turn.Transcript),
			Decision:        &decision,
		})
		s.publishDecisionAndAudit(turn.SessionID, turn.TurnID, decision, auditEvent)
		writeJSON(w, http.StatusOK, CamelotTurnResponse{
			SessionID: turn.SessionID,
			TurnID:    turn.TurnID,
			UIState:   "speaking",
			Decision:  decision,
			Reply:     s.narrate(turn.SessionID, turn.TurnID, turn.Transcript, reply),
			Artifact:  &artifact,
			AuditID:   auditEvent.AuditID,
		})

	case skill.ConfirmationRequired:
		// Tier 3: pending lease, human must confirm before anything executes.
		decision := s.nextDecision("requires_confirmation", skill.ID, skill.Tier, "tier-3 skills require human confirmation")
		lease := s.leases.Issue(turn.SessionID, turn.TurnID, capability, false)
		auditEvent := s.audit.Append(auditEntry{
			SessionID:       turn.SessionID,
			TurnID:          turn.TurnID,
			Kind:            "lease.issued",
			Transcript:      turn.Transcript, // hashed only — tier 3
			RedactedSummary: fmt.Sprintf("tier-3 %s blocked pending confirmation (lease %s)", skill.ID, lease.LeaseID),
			Decision:        &decision,
			LeaseID:         lease.LeaseID,
		})
		s.publishDecisionAndAudit(turn.SessionID, turn.TurnID, decision, auditEvent)
		s.sessions.Publish(turn.SessionID, SessionEvent{Type: "lease.issued", Lease: &lease})
		reply := "This change request needs your explicit approval. Review the decision card and confirm or deny."
		writeJSON(w, http.StatusOK, CamelotTurnResponse{
			SessionID: turn.SessionID,
			TurnID:    turn.TurnID,
			UIState:   "blocked",
			Decision:  decision,
			Lease:     &lease,
			Reply:     ReplyPayload{Text: reply, Final: true},
			AuditID:   auditEvent.AuditID,
		})

	default:
		// Tier 2: effectful draft — policy auto-approves a short-lived lease.
		decision := s.nextDecision("allow", skill.ID, skill.Tier, "tier-2 draft; short-lived lease auto-approved")
		lease := s.leases.Issue(turn.SessionID, turn.TurnID, capability, true)
		s.sessions.Publish(turn.SessionID, SessionEvent{Type: "lease.issued", Lease: &lease})
		artifact, reply, err := s.broker.Execute(skill.ID, turn.TurnID, &lease)
		if err != nil {
			httpError(w, http.StatusForbidden, err.Error())
			return
		}
		consumed, _ := s.leases.Get(lease.LeaseID)
		s.sessions.Publish(turn.SessionID, SessionEvent{Type: "lease.consumed", LeaseID: lease.LeaseID})
		auditEvent := s.audit.Append(auditEntry{
			SessionID:       turn.SessionID,
			TurnID:          turn.TurnID,
			Kind:            "tool.executed",
			Transcript:      turn.Transcript, // hashed only — tier 2
			RedactedSummary: fmt.Sprintf("tier-2 %s executed under lease %s; artifact %s", skill.ID, lease.LeaseID, artifact.ID),
			Decision:        &decision,
			LeaseID:         lease.LeaseID,
		})
		s.publishDecisionAndAudit(turn.SessionID, turn.TurnID, decision, auditEvent)
		writeJSON(w, http.StatusOK, CamelotTurnResponse{
			SessionID: turn.SessionID,
			TurnID:    turn.TurnID,
			UIState:   "speaking",
			Decision:  decision,
			Lease:     &consumed,
			Reply:     s.narrate(turn.SessionID, turn.TurnID, turn.Transcript, reply),
			Artifact:  &artifact,
			AuditID:   auditEvent.AuditID,
		})
	}
}

// narrate routes the reply through the model router (deterministic by
// default) and shapes the sync reply payload: full text when deterministic,
// stream-only when a configured provider narrates. Narration always happens
// AFTER skill execution — a generation failure can never undo or repeat a
// tool action, and the deterministic fixture text is the guaranteed fallback.
func (s *Server) narrate(sessionID, turnID, transcript, deterministicReply string) ReplyPayload {
	s.models.RememberTranscript(sessionID, transcript)
	s.models.Narrate(s.sessions, s.audit, sessionID, turnID, transcript, deterministicReply)
	if s.models.PrimaryIsDeterministic() {
		return ReplyPayload{Text: deterministicReply, Final: false}
	}
	return ReplyPayload{Text: "", Final: false}
}

func (s *Server) handleModelStats(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, s.models.Stats())
}

func (s *Server) handleBargeIn(w http.ResponseWriter, r *http.Request) {
	var event VoiceBargeIn
	if err := json.NewDecoder(r.Body).Decode(&event); err != nil {
		httpError(w, http.StatusBadRequest, "invalid VoiceBargeIn body: "+err.Error())
		return
	}
	if event.SessionID == "" || event.TurnID == "" {
		httpError(w, http.StatusBadRequest, "sessionId and turnId are required")
		return
	}

	cancelled := s.sessions.CancelTurn(event.TurnID)
	if !cancelled {
		// No live stream — still emit the cancellation so the UI settles.
		s.sessions.Publish(event.SessionID, SessionEvent{Type: "turn.cancelled", TurnID: event.TurnID, Reason: "barge-in"})
	}

	revoked := s.leases.RevokeUnusedForTurn(event.TurnID)
	for _, leaseID := range revoked {
		s.sessions.Publish(event.SessionID, SessionEvent{Type: "lease.revoked", LeaseID: leaseID, Reason: "barge-in"})
	}

	auditEvent := s.audit.Append(auditEntry{
		SessionID:       event.SessionID,
		TurnID:          event.TurnID,
		Kind:            "turn.cancelled",
		RedactedSummary: fmt.Sprintf("barge-in (%s): stream cancelled=%t, leases revoked=%d", event.Reason, cancelled, len(revoked)),
	})
	s.sessions.Publish(event.SessionID, SessionEvent{Type: "audit.appended", AuditID: auditEvent.AuditID, Kind: auditEvent.Kind})

	if revoked == nil {
		revoked = []string{}
	}
	writeJSON(w, http.StatusOK, BargeInResponse{
		CancelledTurnID: event.TurnID,
		RevokedLeaseIDs: revoked,
		AuditID:         auditEvent.AuditID,
	})
}

func (s *Server) handleConfirmation(w http.ResponseWriter, r *http.Request) {
	var req ConfirmationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		httpError(w, http.StatusBadRequest, "invalid ConfirmationRequest body: "+err.Error())
		return
	}
	if req.SessionID == "" || req.LeaseID == "" {
		httpError(w, http.StatusBadRequest, "sessionId and leaseId are required")
		return
	}

	if !req.Approve {
		lease, ok := s.leases.Revoke(req.LeaseID)
		if !ok {
			httpError(w, http.StatusConflict, "lease cannot be denied in its current state")
			return
		}
		s.sessions.Publish(req.SessionID, SessionEvent{Type: "lease.revoked", LeaseID: lease.LeaseID, Reason: "denied by user"})
		auditEvent := s.audit.Append(auditEntry{
			SessionID:       req.SessionID,
			TurnID:          lease.TurnID,
			Kind:            "confirmation.recorded",
			RedactedSummary: fmt.Sprintf("confirmation DENIED for lease %s; lease revoked", lease.LeaseID),
			LeaseID:         lease.LeaseID,
		})
		s.sessions.Publish(req.SessionID, SessionEvent{Type: "audit.appended", AuditID: auditEvent.AuditID, Kind: auditEvent.Kind})
		writeJSON(w, http.StatusOK, ConfirmationResponse{Lease: lease, AuditID: auditEvent.AuditID})
		return
	}

	lease, err := s.leases.Approve(req.LeaseID)
	if err != nil {
		httpError(w, http.StatusConflict, err.Error())
		return
	}
	skillID := strings.TrimPrefix(lease.Capability, "skill:")
	artifact, reply, err := s.broker.Execute(skillID, lease.TurnID, &lease)
	if err != nil {
		httpError(w, http.StatusForbidden, err.Error())
		return
	}
	finalLease, _ := s.leases.Get(lease.LeaseID)
	s.sessions.Publish(req.SessionID, SessionEvent{Type: "lease.consumed", LeaseID: lease.LeaseID})
	auditEvent := s.audit.Append(auditEntry{
		SessionID:       req.SessionID,
		TurnID:          lease.TurnID,
		Kind:            "confirmation.recorded",
		RedactedSummary: fmt.Sprintf("confirmation APPROVED for lease %s; %s executed; artifact %s", lease.LeaseID, skillID, artifact.ID),
		LeaseID:         lease.LeaseID,
	})
	s.sessions.Publish(req.SessionID, SessionEvent{Type: "audit.appended", AuditID: auditEvent.AuditID, Kind: auditEvent.Kind})
	confirmedReply := s.narrate(req.SessionID, lease.TurnID, "confirmed: "+skillID, reply)

	writeJSON(w, http.StatusOK, ConfirmationResponse{
		Lease:    finalLease,
		Artifact: &artifact,
		Reply:    &confirmedReply,
		AuditID:  auditEvent.AuditID,
	})
}

func (s *Server) handleAudit(w http.ResponseWriter, r *http.Request) {
	auditID := r.PathValue("id")
	event, ok := s.audit.Get(auditID)
	if !ok {
		httpError(w, http.StatusNotFound, "no audit event "+auditID)
		return
	}
	writeJSON(w, http.StatusOK, event)
}

func (s *Server) handleSessionEvents(w http.ResponseWriter, r *http.Request) {
	sessionID := r.PathValue("id")
	conn, err := wsUpgrade(w, r)
	if err != nil {
		httpError(w, http.StatusBadRequest, err.Error())
		return
	}
	defer conn.Close()

	events, unsubscribe := s.sessions.Subscribe(sessionID)
	defer unsubscribe()

	done := make(chan struct{})
	go func() {
		conn.ReadUntilClose()
		close(done)
	}()

	for {
		select {
		case <-done:
			return
		case event := <-events:
			payload, err := json.Marshal(event)
			if err != nil {
				continue
			}
			if err := conn.WriteText(payload); err != nil {
				return
			}
		}
	}
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(v); err != nil {
		log.Printf("writeJSON: %v", err)
	}
}

func httpError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}

func (s *Server) publishDecisionAndAudit(sessionID, turnID string, decision PolicyDecision, auditEvent AuditEvent) {
	s.sessions.Publish(sessionID, SessionEvent{Type: "policy.decision", TurnID: turnID, Decision: &decision})
	s.sessions.Publish(sessionID, SessionEvent{Type: "audit.appended", AuditID: auditEvent.AuditID, Kind: auditEvent.Kind})
}
