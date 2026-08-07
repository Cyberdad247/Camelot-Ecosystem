// @camelot/contracts — governance vocabulary for the Camelot x Kickbox slice.
//
// Ownership (ADR-001): Camelot owns PolicyDecision/CapabilityLease/AuditEvent
// semantics; Kickbox owns turn/barge-in UX semantics. Evolution is
// additive-only within a major version: servers reject unknown REQUIRED
// fields, clients ignore unknown fields.
//
// Raw audio never crosses this contract — only transcripts and SHA-256 hashes.

/** How the utterance entered the system. The text-first slice uses "text";
 *  the voice phase populates the same transcript field from capture. */
export type TurnModality = 'text' | 'voice';

/** Skill governance tiers. 1 = read-only, 2 = effectful draft (auto-lease),
 *  3 = effectful + human confirmation required. */
export type SkillTier = 1 | 2 | 3;

/** Avatar/session UI state, aligned with 02_FORGE voice-first-runtime states
 *  so real capture can be wired in later without renaming. */
export type SessionUiState = 'idle' | 'thinking' | 'speaking' | 'blocked';

export type LeaseStatus = 'pending' | 'approved' | 'consumed' | 'revoked' | 'expired';

export type PolicyEffect = 'allow' | 'deny' | 'requires_confirmation';

/** A single user utterance submitted to POST /v1/voice/turns. */
export interface VoiceTurn {
  sessionId: string;
  /** Client-generated, unique per session (e.g. "turn-0001"). */
  turnId: string;
  modality: TurnModality;
  /** The utterance text. For voice turns this is the transcript; the raw
   *  audio stays on the client and is discarded after transcription. */
  transcript: string;
  /** SHA-256 of the source audio, when modality is "voice". Hash only. */
  audioSha256?: string;
  startedAtMs: number;
  endedAtMs?: number;
  locale?: string;
}

/** Interruption of an in-flight turn, submitted to POST /v1/voice/barge-in. */
export interface VoiceBargeIn {
  sessionId: string;
  /** The turn being interrupted. */
  turnId: string;
  atMs: number;
  reason: 'user_speech' | 'user_tap' | 'mock';
}

/** The gateway's policy verdict for one proposed skill invocation. */
export interface PolicyDecision {
  decisionId: string;
  effect: PolicyEffect;
  skillId: string;
  tier: SkillTier;
  /** Human-readable rationale, safe to render in the decision card. */
  reason: string;
  policyVersion: string;
  /** ISO 8601. */
  decidedAt: string;
}

/** Short-lived, single-use authorization for one effectful action.
 *  Issued only by the Camelot gateway; validated by the tool broker and the
 *  Rust node-agent. Nothing executes effectfully without one (ADR-001 rule 1). */
export interface CapabilityLease {
  leaseId: string;
  sessionId: string;
  turnId: string;
  /** Namespaced capability, e.g. "skill:deployment.review.prepare"
   *  or "compute:audio.features". */
  capability: string;
  status: LeaseStatus;
  /** ISO 8601. */
  issuedAt: string;
  /** ISO 8601 — short-lived (~30 s). */
  expiresAt: string;
  singleUse: true;
  /** Opaque gateway-signed token; present only while status is "approved".
   *  The PWA never forwards it anywhere except back to the gateway. */
  token?: string;
}

/** One redacted, hash-chained audit record (GET /v1/audit/:id).
 *  Tier >= 2 records carry transcriptSha256 and never the raw transcript. */
export interface AuditEvent {
  auditId: string;
  sessionId: string;
  turnId?: string;
  /** e.g. "turn.received" | "policy.decision" | "lease.issued"
   *  | "lease.revoked" | "lease.consumed" | "tool.executed"
   *  | "tool.denied" | "turn.cancelled" | "confirmation.recorded" */
  kind: string;
  /** ISO 8601. */
  at: string;
  transcriptSha256?: string;
  redactedSummary: string;
  decision?: PolicyDecision;
  leaseId?: string;
  /** Hash chain: SHA-256 over (prevHash + canonical body). */
  prevHash: string;
  hash: string;
}

/** An artifact produced by an executed skill (e.g. a tier-2 draft). */
export interface SkillArtifact {
  kind: 'staging_status' | 'deployment_review_draft' | 'change_request';
  id: string;
  summary: string;
}

/** Synchronous response to POST /v1/voice/turns. Streaming reply chunks
 *  arrive separately on the session-events WebSocket. */
export interface CamelotTurnResponse {
  sessionId: string;
  turnId: string;
  uiState: SessionUiState;
  decision: PolicyDecision;
  /** Present when a lease was issued for this turn (tier 2 auto-approved,
   *  tier 3 pending until confirmed). */
  lease?: CapabilityLease;
  reply: {
    text: string;
    /** false while chunks are still streaming on the events socket. */
    final: boolean;
  };
  artifact?: SkillArtifact;
  auditId: string;
}

/** Request body for POST /v1/confirmations. */
export interface ConfirmationRequest {
  sessionId: string;
  leaseId: string;
  approve: boolean;
  note?: string;
}

/** Response body for POST /v1/confirmations. */
export interface ConfirmationResponse {
  lease: CapabilityLease;
  /** Populated when approval triggered execution. */
  artifact?: SkillArtifact;
  reply?: { text: string; final: boolean };
  auditId: string;
}

/** Response body for POST /v1/voice/barge-in. */
export interface BargeInResponse {
  cancelledTurnId: string;
  revokedLeaseIds: string[];
  auditId: string;
}

/** Events pushed on GET /v1/sessions/:id/events (WebSocket). */
export type SessionEvent =
  | { type: 'turn.accepted'; turnId: string }
  | { type: 'policy.decision'; turnId: string; decision: PolicyDecision }
  | { type: 'lease.issued'; lease: CapabilityLease }
  | { type: 'lease.revoked'; leaseId: string; reason: string }
  | { type: 'lease.consumed'; leaseId: string }
  | { type: 'reply.chunk'; turnId: string; seq: number; text: string }
  | { type: 'reply.done'; turnId: string }
  | { type: 'turn.cancelled'; turnId: string; reason: string }
  | { type: 'audit.appended'; auditId: string; kind: string }
  | { type: 'model.route'; turnId: string; provider: string; fallback?: boolean; reason?: string };

export interface HealthResponse {
  status: 'ok';
  service: string;
  version: string;
}
