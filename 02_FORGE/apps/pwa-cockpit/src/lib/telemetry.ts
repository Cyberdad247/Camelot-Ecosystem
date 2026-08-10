// Telemetry — Camelot PWA Cockpit
// Lightweight observability hook for production monitoring. Edge-runtime
// compatible (no Node primitives, no shell access). Tracks cartridge
// loads, voice pipeline events, and V2 verify results.
//
// In dev: logs to console with a structured prefix.
// In prod: batches events and POSTs to NEXT_PUBLIC_TELEMETRY_URL.
//
// Phase 8 hardening:
//   - Batches events (flush at FLUSH_THRESHOLD) instead of one fetch
//     per event. A ReAct loop with many steps previously fired N HTTP
//     requests; now it fires ceil(N / FLUSH_THRESHOLD).
//   - BUFFER_LIMIT bumped to 500 (was 100) so a slow endpoint does not
//     drop events as aggressively before backpressure kicks in.
//   - isFlushing mutex prevents two concurrent flushes (a fetch in
//     flight will pick up events added during the fetch on completion).
//   - flushSync() exported for tests and graceful shutdown paths
//     (the edge runtime freezes background tasks, so this is best-effort).
//   - On fetch failure, events are re-prepended to the buffer
//     (oldest-first) up to BUFFER_LIMIT. Beyond the cap, oldest events
//     are dropped — never block the user-facing flow on a failed
//     telemetry send.

type TelemetryEvent = {
  ts: number;
  name: string;
  category: "cartridge" | "voice" | "v2" | "system";
  level: "info" | "warn" | "error";
  payload?: Record<string, unknown>;
};

const BUFFER_LIMIT = 500;
const FLUSH_THRESHOLD = 20;
const buffer: TelemetryEvent[] = [];
let endpoint: string | null = null;
let initialized = false;
let isFlushing = false;

function init(): void {
  if (initialized) return;
  initialized = true;
  if (typeof process !== "undefined" && process.env?.NEXT_PUBLIC_TELEMETRY_URL) {
    endpoint = process.env.NEXT_PUBLIC_TELEMETRY_URL;
  } else if (
    typeof window !== "undefined" &&
    (window as { NEXT_PUBLIC_TELEMETRY_URL?: string }).NEXT_PUBLIC_TELEMETRY_URL
  ) {
    endpoint = (window as { NEXT_PUBLIC_TELEMETRY_URL?: string }).NEXT_PUBLIC_TELEMETRY_URL ?? null;
  }
}

// Schedule a flush if we have a configured endpoint and enough events.
// Single-flight via the isFlushing mutex; user-facing flow is never
// awaited (fire-and-forget).
function scheduleFlush(): void {
  if (isFlushing) return;
  if (buffer.length < FLUSH_THRESHOLD) return;
  if (!endpoint) return;
  isFlushing = true;
  void doFlush();
}

async function doFlush(): Promise<void> {
  if (buffer.length === 0 || !endpoint) {
    isFlushing = false;
    return;
  }
  // Drain a snapshot of the current buffer atomically. Events added
  // during the fetch stay in the buffer for the next flush; this
  // avoids losing events that arrived mid-send.
  const batch = buffer.splice(0, buffer.length);
  try {
    await fetch(endpoint, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ events: batch }),
      keepalive: true,
    });
  } catch {
    // Backpressure: re-prepend the batch to the buffer (oldest first).
    // If the buffer would exceed BUFFER_LIMIT, drop the oldest events
    // to make room — never block the user-facing flow on telemetry.
    const room = BUFFER_LIMIT - buffer.length;
    if (room >= batch.length) {
      buffer.unshift(...batch);
    } else if (room > 0) {
      const kept = batch.slice(batch.length - room);
      buffer.unshift(...kept);
    }
    // else: room === 0, drop the entire batch (buffer already full)
  } finally {
    isFlushing = false;
  }
  // If events were added during the fetch, schedule another flush.
  if (buffer.length >= FLUSH_THRESHOLD) {
    scheduleFlush();
  }
}

export function track(
  name: string,
  category: TelemetryEvent["category"],
  level: TelemetryEvent["level"] = "info",
  payload?: Record<string, unknown>,
): void {
  init();
  const event: TelemetryEvent = {
    ts: Date.now(),
    name,
    category,
    level,
    payload,
  };
  buffer.push(event);
  if (buffer.length > BUFFER_LIMIT) buffer.shift();

  if (endpoint) {
    scheduleFlush();
  } else if (typeof console !== "undefined") {
    const tag = `[telemetry:${category}]`;
    if (level === "error") console.error(tag, name, payload);
    else if (level === "warn") console.warn(tag, name, payload);
    else console.info(tag, name, payload);
  }
}

// Drain the buffer synchronously (async but awaiting). Used by tests
// to assert batched payloads and by graceful shutdown paths. In edge
// runtime, this is best-effort because the runtime freezes background
// tasks; the function is still safe to call.
export async function flushSync(): Promise<void> {
  if (!endpoint) return;
  if (buffer.length === 0) return;
  // If a flush is in flight, wait for it; if not, start one.
  if (isFlushing) {
    // Spin until the in-flight flush completes. Bounded by an
    // internal safety net so we never deadlock in tests.
    const start = Date.now();
    while (isFlushing && Date.now() - start < 5000) {
      await new Promise((r) => setTimeout(r, 1));
    }
    // If more events accumulated during the wait, flush them.
    if (buffer.length > 0 && !isFlushing) {
      isFlushing = true;
      try {
        await doFlush();
      } finally {
        isFlushing = false;
      }
    }
  } else {
    isFlushing = true;
    try {
      await doFlush();
    } finally {
      isFlushing = false;
    }
  }
}

// Convenience helpers for the most common event types.
export const telemetry = {
  cartridgeLoaded: (cartridgeId: string, source: "v1" | "v2") =>
    track("cartridge_loaded", "cartridge", "info", { cartridgeId, source }),
  voiceState: (state: string) =>
    track("voice_state", "voice", "info", { state }),
  v2Verify: (ok: boolean, stage: string, reason?: string) =>
    track("v2_verify", "v2", ok ? "info" : "warn", { ok, stage, reason }),
  error: (name: string, err: unknown) =>
    track(name, "system", "error", {
      message: err instanceof Error ? err.message : String(err),
    }),
};

// Read-only view for the health endpoint and debug overlays.
export function getRecentEvents(limit = 20): readonly TelemetryEvent[] {
  return buffer.slice(-limit);
}

// Test-only: clear the buffer, endpoint cache, and init flag so
// each test starts with a known state. The buffer is a module-level
// singleton; without this, tests can leak events into each other.
// Exported as `__resetTelemetryForTesting` to make the test-only
// intent explicit and discourage production use.
//
// Contract: call this AFTER any pending flushSync() in a previous
// test has resolved, so an in-flight doFlush() from that test
// doesn't observe a half-reset state. The post-flush check in
// doFlush() inspects buffer.length after the fetch settles; if
// reset happened first, the buffer will be empty and no new
// scheduleFlush will be triggered, so this is currently safe — but
// the contract is documented for future maintainers.
export function __resetTelemetryForTesting(): void {
  buffer.length = 0;
  endpoint = null;
  initialized = false;
  isFlushing = false;
}
