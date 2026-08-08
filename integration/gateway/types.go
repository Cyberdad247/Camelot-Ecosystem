package main

// Wire types mirroring @camelot/contracts (integration/contracts/src/types.ts).
// JSON field names must stay byte-identical to the TS package — the contract
// evolves additively only (ADR-001).

type VoiceTurn struct {
	SessionID   string `json:"sessionId"`
	TurnID      string `json:"turnId"`
	Modality    string `json:"modality"` // "text" | "voice"
	Transcript  string `json:"transcript"`
	AudioSHA256 string `json:"audioSha256,omitempty"`
	StartedAtMs int64  `json:"startedAtMs"`
	EndedAtMs   int64  `json:"endedAtMs,omitempty"`
	Locale      string `json:"locale,omitempty"`
}

type VoiceBargeIn struct {
	SessionID string `json:"sessionId"`
	TurnID    string `json:"turnId"`
	AtMs      int64  `json:"atMs"`
	Reason    string `json:"reason"` // "user_speech" | "user_tap" | "mock"
}

type PolicyDecision struct {
	DecisionID    string `json:"decisionId"`
	Effect        string `json:"effect"` // "allow" | "deny" | "requires_confirmation"
	SkillID       string `json:"skillId"`
	Tier          int    `json:"tier"`
	Reason        string `json:"reason"`
	PolicyVersion string `json:"policyVersion"`
	DecidedAt     string `json:"decidedAt"`
}

type CapabilityLease struct {
	LeaseID    string `json:"leaseId"`
	SessionID  string `json:"sessionId"`
	TurnID     string `json:"turnId"`
	Capability string `json:"capability"`
	Status     string `json:"status"` // pending|approved|consumed|revoked|expired
	IssuedAt   string `json:"issuedAt"`
	ExpiresAt  string `json:"expiresAt"`
	SingleUse  bool   `json:"singleUse"`
	Token      string `json:"token,omitempty"`
	// Node-job leases (Phase 4A) additionally bind the exact node and tenant.
	// Empty for ordinary skill leases. Both are covered by the signature.
	NodeID   string `json:"nodeId,omitempty"`
	TenantID string `json:"tenantId,omitempty"`
}

type AuditEvent struct {
	AuditID          string          `json:"auditId"`
	SessionID        string          `json:"sessionId"`
	TurnID           string          `json:"turnId,omitempty"`
	Kind             string          `json:"kind"`
	At               string          `json:"at"`
	TranscriptSHA256 string          `json:"transcriptSha256,omitempty"`
	RedactedSummary  string          `json:"redactedSummary"`
	Decision         *PolicyDecision `json:"decision,omitempty"`
	LeaseID          string          `json:"leaseId,omitempty"`
	PrevHash         string          `json:"prevHash"`
	Hash             string          `json:"hash"`
}

type SkillArtifact struct {
	Kind    string `json:"kind"`
	ID      string `json:"id"`
	Summary string `json:"summary"`
}

type ReplyPayload struct {
	Text  string `json:"text"`
	Final bool   `json:"final"`
}

type CamelotTurnResponse struct {
	SessionID string           `json:"sessionId"`
	TurnID    string           `json:"turnId"`
	UIState   string           `json:"uiState"` // idle|thinking|speaking|blocked
	Decision  PolicyDecision   `json:"decision"`
	Lease     *CapabilityLease `json:"lease,omitempty"`
	Reply     ReplyPayload     `json:"reply"`
	Artifact  *SkillArtifact   `json:"artifact,omitempty"`
	AuditID   string           `json:"auditId"`
}

type ConfirmationRequest struct {
	SessionID string `json:"sessionId"`
	LeaseID   string `json:"leaseId"`
	Approve   bool   `json:"approve"`
	Note      string `json:"note,omitempty"`
}

type ConfirmationResponse struct {
	Lease    CapabilityLease `json:"lease"`
	Artifact *SkillArtifact  `json:"artifact,omitempty"`
	Reply    *ReplyPayload   `json:"reply,omitempty"`
	AuditID  string          `json:"auditId"`
}

type BargeInResponse struct {
	CancelledTurnID string   `json:"cancelledTurnId"`
	RevokedLeaseIDs []string `json:"revokedLeaseIds"`
	AuditID         string   `json:"auditId"`
}

// SessionEvent is the discriminated union pushed over the events WebSocket.
// Only the fields relevant to the given Type are populated.
type SessionEvent struct {
	Type     string           `json:"type"`
	TurnID   string           `json:"turnId,omitempty"`
	Decision *PolicyDecision  `json:"decision,omitempty"`
	Lease    *CapabilityLease `json:"lease,omitempty"`
	LeaseID  string           `json:"leaseId,omitempty"`
	Reason   string           `json:"reason,omitempty"`
	Seq      int              `json:"seq,omitempty"`
	Text     string           `json:"text,omitempty"`
	AuditID  string           `json:"auditId,omitempty"`
	Kind     string           `json:"kind,omitempty"`
	// model.route events (Phase 3)
	Provider string `json:"provider,omitempty"`
	Fallback bool   `json:"fallback,omitempty"`
}

type HealthResponse struct {
	Status  string `json:"status"`
	Service string `json:"service"`
	Version string `json:"version"`
}
