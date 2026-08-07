// Model-routing contracts (Phase 3) — mirrors integration/gateway/models.go.
// Boundary: models narrate replies and may PROPOSE a skill plan; proposals
// are validated and audited by the gateway, never executed. Only the policy
// kernel issues leases.

export type ModelFailureCode =
  | 'timeout'
  | 'disabled'
  | 'not_allowed'
  | 'oversized'
  | 'malformed_stream'
  | 'provider_error';

export interface ModelFailure {
  code: ModelFailureCode;
  detail: string;
}

export interface ModelRequest {
  requestId: string;
  sessionId: string;
  turnId: string;
  prompt: string;
  /** Session-local transcript window; memory-only, capped. */
  context?: string[];
  maxChars: number;
}

export interface ModelDelta {
  requestId: string;
  seq: number;
  text: string;
}

export interface ModelResponse {
  requestId: string;
  provider: string;
  text: string;
  finishReason: 'complete' | 'cancelled' | 'fallback' | 'error';
  firstTokenMs: number;
  completionMs: number;
  deltaCount: number;
}

export interface ModelProviderHealth {
  provider: string;
  ok: boolean;
  detail?: string;
}

export interface ModelRouteDecision {
  requestId: string;
  provider: string;
  reason: string;
  fallback: boolean;
  failure?: ModelFailure;
}

/** GET /v1/models/stats */
export interface ModelStats {
  provider: string;
  requests: number;
  fallbacks: number;
  planProposals: number;
  planDenials: number;
  avgFirstTokenMs: number;
  avgCompletionMs: number;
}
