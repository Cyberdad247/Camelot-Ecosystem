// Telemetry — Camelot PWA Cockpit
// Lightweight observability hook for production monitoring. Edge-runtime
// compatible (no Node primitives, no shell access). Tracks cartridge
// loads, voice pipeline events, and V2 verify results.
//
// In dev: logs to console with a structured prefix.
// In prod: sends to NEXT_PUBLIC_TELEMETRY_URL if configured; otherwise
// stays in-memory and exposes via the health endpoint.
//
// This is intentionally opt-in and cheap. The PWA must work without
// telemetry (degraded mode); a failed telemetry send never blocks the
// user-facing flow.

type TelemetryEvent = {
  ts: number;
  name: string;
  category: "cartridge" | "voice" | "v2" | "system";
  level: "info" | "warn" | "error";
  payload?: Record<string, unknown>;
};

const BUFFER_LIMIT = 100;
const buffer: TelemetryEvent[] = [];
let endpoint: string | null = null;
let initialized = false;

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

  // Dev: structured console log. Prod: fire-and-forget POST.
  if (endpoint) {
    try {
      fetch(endpoint, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(event),
        keepalive: true,
      }).catch(() => {
        // Swallow telemetry failures silently. The user-facing flow
        // must not be affected by a failed telemetry send.
      });
    } catch {
      // ignore
    }
  } else if (typeof console !== "undefined") {
    const tag = `[telemetry:${category}]`;
    if (level === "error") console.error(tag, name, payload);
    else if (level === "warn") console.warn(tag, name, payload);
    else console.info(tag, name, payload);
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
