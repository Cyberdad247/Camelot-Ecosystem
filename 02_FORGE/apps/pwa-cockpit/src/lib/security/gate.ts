// src/lib/security/gate.ts
//
// Phase 3 shared edge-safe auth + path validation. Eliminates the
// duplication between middleware.ts (fast pre-filter) and the
// RoutingAgent (agentic decisions). Both must use the same regex so
// a future tweak in one place doesn't silently diverge from the other.
//
// Edge-runtime compatible: no Node primitives, no React imports.

export function isValidBearerToken(header: string): boolean {
  return /^Bearer ([A-Za-z0-9_-]{32,})$/.test(header);
}

export function isValidCartridgeId(id: string): boolean {
  return /^[a-z0-9_-]{1,64}$/i.test(id);
}
