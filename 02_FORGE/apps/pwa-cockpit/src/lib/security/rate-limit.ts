// src/lib/security/rate-limit.ts
//
// Phase 7: in-memory per-IP rate limiter using a sliding window. Edge-runtime
// safe (no Node primitives — only Map + Date.now + arithmetic). Suitable for
// a single Vercel Edge instance. For multi-instance deployments, swap the
// in-memory `store` Map for Vercel KV or Upstash (the checkRateLimit() shape
// stays the same; only the backing storage changes).
//
// Algorithm: sliding window of request timestamps. On each call, drop
// timestamps older than `windowMs`, then check the count. The oldest
// dropped timestamp determines when the next slot frees up (Retry-After).
//
// Memory: opportunistic eviction when the store exceeds 10k entries
// (drops entries whose newest timestamp is older than the window). This
// keeps the map bounded even under attack from a large number of distinct
// IPs (the attacker's IPs each get one entry).

export type RateLimitOptions = {
  limit?: number;
  windowMs?: number;
};

export type RateLimitResult = {
  ok: boolean;
  /** Seconds until the next request would be allowed (0 when ok). */
  retryAfter: number;
  /** Remaining requests in the current window (0 when rate limited). */
  remaining: number;
  /** Wall-clock ms when the window resets. */
  resetAt: number;
};

const store: Map<string, number[]> = new Map();
const EVICTION_THRESHOLD = 10_000;

export function checkRateLimit(
  ip: string,
  options: RateLimitOptions = {},
): RateLimitResult {
  const limit = options.limit ?? 60;
  const windowMs = options.windowMs ?? 60_000;
  const now = Date.now();
  const cutoff = now - windowMs;

  const existing = store.get(ip) ?? [];
  // Drop expired entries (older than the window).
  const active = existing.filter((t) => t > cutoff);

  if (active.length >= limit) {
    const oldest = active[0]!;
    const retryAfter = Math.max(1, Math.ceil((oldest + windowMs - now) / 1000));
    store.set(ip, active);
    if (store.size > EVICTION_THRESHOLD) evict(cutoff);
    return {
      ok: false,
      retryAfter,
      remaining: 0,
      resetAt: oldest + windowMs,
    };
  }

  active.push(now);
  store.set(ip, active);
  if (store.size > EVICTION_THRESHOLD) evict(cutoff);

  return {
    ok: true,
    retryAfter: 0,
    remaining: limit - active.length,
    resetAt: now + windowMs,
  };
}

function evict(cutoff: number): void {
  for (const [key, timestamps] of store.entries()) {
    if (timestamps.length === 0 || timestamps[timestamps.length - 1]! <= cutoff) {
      store.delete(key);
    }
  }
}

// Extract the client IP from request headers. Vercel/Cloudflare set
// x-forwarded-for (first hop is the original client) and x-real-ip.
// Falls back to "unknown" so the rate limiter still works in tests
// where neither header is set.
export function getClientIp(
  req: { headers: { get(name: string): string | null } },
): string {
  const xff = req.headers.get("x-forwarded-for");
  if (xff) {
    const first = xff.split(",")[0]?.trim();
    if (first) return first;
  }
  const realIp = req.headers.get("x-real-ip");
  if (realIp) return realIp;
  return "unknown";
}

// Test-only: clear the entire store. Used by tests for isolation; not
// for production use (the `__` prefix discourages accidental calls).
export function __resetRateLimitForTesting(): void {
  store.clear();
}
