// src/lib/observability/trace.ts
//
// Phase 7: W3C Trace Context (https://www.w3.org/TR/trace-context/).
// Edge-runtime safe — uses crypto.getRandomValues (Web Crypto) and
// atob/btoa. No Node primitives.
//
// Header format: traceparent: 00-{traceId-32hex}-{spanId-16hex}-{flags-2hex}
//   - version: 2 hex chars (we accept only "00" per spec; future versions
//     are parsed leniently by the spec but we reject for safety)
//   - traceId: 32 hex chars, all-zero is invalid
//   - spanId: 16 hex chars, all-zero is invalid
//   - flags: 2 hex chars (typically "01" = sampled)
//
// Usage: the route handler extracts or generates a TraceContext, threads
// it through AgentOrchestrator.dispatch (which attaches traceId/spanId
// to each AgentStep), and emits a child traceparent on the response so
// the caller can chain.

export type TraceContext = {
  traceId: string;
  spanId: string;
  flags: string;
  /** Full traceparent header value, e.g. "00-abc...-def...-01". */
  traceparent: string;
};

const TRACEPARENT_REGEX = /^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$/;
const VERSION_00 = "00";
const SAMPLED_FLAGS = "01";
const ALL_ZERO_TRACE = "0".repeat(32);
const ALL_ZERO_SPAN = "0".repeat(16);

// Generate a lowercase hex string of the given byte length.
// 16 bytes -> 32 hex chars (traceId); 8 bytes -> 16 hex chars (spanId).
function generateHex(byteLength: number): string {
  const bytes = new Uint8Array(byteLength);
  // crypto.getRandomValues is available in both edge and Node runtimes.
  globalThis.crypto.getRandomValues(bytes);
  let hex = "";
  for (let i = 0; i < bytes.length; i++) {
    hex += bytes[i]!.toString(16).padStart(2, "0");
  }
  return hex;
}

export function generateTraceId(): string {
  return generateHex(16);
}

export function generateSpanId(): string {
  return generateHex(8);
}

export function generateTraceContext(): TraceContext {
  const traceId = generateTraceId();
  const spanId = generateSpanId();
  return {
    traceId,
    spanId,
    flags: SAMPLED_FLAGS,
    traceparent: `${VERSION_00}-${traceId}-${spanId}-${SAMPLED_FLAGS}`,
  };
}

// Parse a W3C traceparent header. Returns null for malformed input.
// Per spec, all-zero traceId/spanId are invalid.
export function parseTraceparent(
  header: string | null | undefined,
): TraceContext | null {
  if (!header) return null;
  const trimmed = header.trim();
  const match = TRACEPARENT_REGEX.exec(trimmed);
  if (!match) return null;
  const [, version, traceId, spanId, flags] = match;
  if (version !== VERSION_00) return null;
  if (traceId === ALL_ZERO_TRACE) return null;
  if (spanId === ALL_ZERO_SPAN) return null;
  return {
    traceId: traceId!,
    spanId: spanId!,
    flags: flags!,
    traceparent: `${version}-${traceId}-${spanId}-${flags}`,
  };
}

// Extract the incoming traceparent, or generate a new one if absent
// or malformed. The route handler should always use this so the
// response can always carry a valid traceparent.
export function extractOrGenerateTrace(
  header: string | null | undefined,
): TraceContext {
  return parseTraceparent(header) ?? generateTraceContext();
}

// Build a child traceparent for the response. Keeps the same traceId
// (so the response links to the request) but mints a new spanId
// (so the response is its own span within the trace).
export function childTraceparent(parent: TraceContext): string {
  const spanId = generateSpanId();
  return `${VERSION_00}-${parent.traceId}-${spanId}-${parent.flags}`;
}

// Test-only: a no-op reserved for future state if we add caching.
export function __resetTraceForTesting(): void {
  // No state to reset; functions are pure (or use crypto.getRandomValues
  // which is non-deterministic by design).
}
