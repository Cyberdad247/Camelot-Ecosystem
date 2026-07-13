// tests/llm-retry.test.ts
//
// Phase 8: tests for RetryAdapterWrapper and isRetryable() in
// src/lib/agents/llm-adapter.ts. Verifies:
//   - Success on first attempt (no retry)
//   - Retry on 503 until maxAttempts, then re-throw
//   - Recovery after 429 on first attempt
//   - No retry on 4xx other than 429
//   - Retry on TypeError (network error)
//   - withRetry() helper returns a wrapped adapter
//
// Mocks the inner adapter (not the real SDKs) so tests are fast and
// deterministic. Uses a small baseDelayMs so the exponential backoff
// is fast in tests.
//
// Runs under `node --import tsx --test tests/*.test.ts`.

import assert from "node:assert/strict";
import test from "node:test";
import {
  RetryAdapterWrapper,
  isRetryable,
  withRetry,
} from "../src/lib/agents/llm-adapter";
import type { IntelligenceAdapter } from "../src/lib/agents/types";

// A controllable inner adapter. Each call increments `calls` and
// either resolves with a string or throws an error with the given
// status / name. Used to simulate 429, 5xx, 4xx, and network errors.
type Behavior =
  | { kind: "ok"; value: string }
  | { kind: "error"; status?: number; name?: string; message?: string };

function makeAdapter(
  sequence: readonly Behavior[],
): { adapter: IntelligenceAdapter; calls: { count: number } } {
  const calls = { count: 0 };
  const adapter: IntelligenceAdapter = {
    async generateThinking(_prompt: string) {
      const i = calls.count;
      calls.count += 1;
      const b = sequence[Math.min(i, sequence.length - 1)]!;
      if (b.kind === "ok") return b.value;
      const err = new Error(b.message ?? "error") as Error & {
        status?: number;
        name?: string;
      };
      if (typeof b.status === "number") err.status = b.status;
      if (b.name) err.name = b.name;
      throw err;
    },
  };
  return { adapter, calls };
}

test("RetryAdapterWrapper returns immediately on first success", async () => {
  const { adapter, calls } = makeAdapter([{ kind: "ok", value: "hello" }]);
  const wrapped = new RetryAdapterWrapper(adapter, {
    maxAttempts: 3,
    baseDelayMs: 1,
  });
  const result = await wrapped.generateThinking("hi");
  assert.equal(result, "hello");
  assert.equal(calls.count, 1);
});

test("RetryAdapterWrapper retries on 503 up to maxAttempts then re-throws", async () => {
  const { adapter, calls } = makeAdapter([
    { kind: "error", status: 503, message: "down" },
    { kind: "error", status: 503, message: "down" },
    { kind: "error", status: 503, message: "down" },
  ]);
  const wrapped = new RetryAdapterWrapper(adapter, {
    maxAttempts: 3,
    baseDelayMs: 1,
  });
  await assert.rejects(
    () => wrapped.generateThinking("hi"),
    /down/,
  );
  assert.equal(calls.count, 3, "should attempt exactly maxAttempts times");
});

test("RetryAdapterWrapper recovers after a 429 on the first attempt", async () => {
  const { adapter, calls } = makeAdapter([
    { kind: "error", status: 429, message: "rate limited" },
    { kind: "ok", value: "ok" },
    { kind: "ok", value: "ok" },
  ]);
  const wrapped = new RetryAdapterWrapper(adapter, {
    maxAttempts: 3,
    baseDelayMs: 1,
  });
  const result = await wrapped.generateThinking("hi");
  assert.equal(result, "ok");
  assert.equal(calls.count, 2, "should retry once after 429 then succeed");
});

test("RetryAdapterWrapper does NOT retry on 400 (4xx other than 429)", async () => {
  const { adapter, calls } = makeAdapter([
    { kind: "error", status: 400, message: "bad request" },
    { kind: "ok", value: "ok" },
  ]);
  const wrapped = new RetryAdapterWrapper(adapter, {
    maxAttempts: 3,
    baseDelayMs: 1,
  });
  await assert.rejects(
    () => wrapped.generateThinking("hi"),
    /bad request/,
  );
  assert.equal(calls.count, 1, "4xx should not be retried");
});

test("RetryAdapterWrapper retries on TypeError (network error)", async () => {
  const { adapter, calls } = makeAdapter([
    { kind: "error", name: "TypeError", message: "fetch failed" },
    { kind: "ok", value: "ok" },
  ]);
  const wrapped = new RetryAdapterWrapper(adapter, {
    maxAttempts: 3,
    baseDelayMs: 1,
  });
  const result = await wrapped.generateThinking("hi");
  assert.equal(result, "ok");
  assert.equal(calls.count, 2, "TypeError should be retried");
});

test("withRetry() returns a wrapped IntelligenceAdapter", async () => {
  const { adapter } = makeAdapter([{ kind: "ok", value: "wrapped" }]);
  const wrapped = withRetry(adapter, { maxAttempts: 2, baseDelayMs: 1 });
  const result = await wrapped.generateThinking("hi");
  assert.equal(result, "wrapped");
});

test("isRetryable() classifies errors correctly", () => {
  // 429 → retryable
  assert.equal(isRetryable({ status: 429 }), true);
  // 500/502/503/504 → retryable
  assert.equal(isRetryable({ status: 500 }), true);
  assert.equal(isRetryable({ status: 502 }), true);
  assert.equal(isRetryable({ status: 503 }), true);
  assert.equal(isRetryable({ status: 504 }), true);
  // 4xx other than 429 → not retryable
  assert.equal(isRetryable({ status: 400 }), false);
  assert.equal(isRetryable({ status: 401 }), false);
  assert.equal(isRetryable({ status: 404 }), false);
  // Network error names → retryable
  assert.equal(isRetryable({ name: "TypeError" }), true);
  assert.equal(isRetryable({ name: "FetchError" }), true);
  assert.equal(isRetryable({ name: "AbortError" }), true);
  // Plain errors → not retryable
  assert.equal(isRetryable(new Error("nope")), false);
  // Non-objects → not retryable
  assert.equal(isRetryable("string error"), false);
  assert.equal(isRetryable(null), false);
  assert.equal(isRetryable(undefined), false);
});

test("RetryAdapterWrapper uses exponential backoff (1x, 2x)", async () => {
  // This is a behavioral test: the first retry delay should be
  // baseDelayMs * 2^0 = baseDelayMs, the second baseDelayMs * 2^1.
  // With baseDelayMs=50, total backoff time across 2 retries is
  // 50 + 100 = 150ms. Allow generous slack for CI jitter but fail
  // loudly if it exceeds 1500ms (which would mean it's NOT
  // backoff — it would be near-instant).
  const { adapter } = makeAdapter([
    { kind: "error", status: 503, message: "down" },
    { kind: "error", status: 503, message: "down" },
    { kind: "ok", value: "ok" },
  ]);
  const wrapped = new RetryAdapterWrapper(adapter, {
    maxAttempts: 3,
    baseDelayMs: 50,
  });
  const start = Date.now();
  const result = await wrapped.generateThinking("hi");
  const elapsed = Date.now() - start;
  assert.equal(result, "ok");
  assert.ok(
    elapsed >= 100,
    `expected at least 100ms of backoff, got ${elapsed}ms`,
  );
  assert.ok(
    elapsed < 1500,
    `backoff is suspiciously slow: ${elapsed}ms (expected < 1500ms with baseDelayMs=50)`,
  );
});

test("RetryAdapterWrapper with maxAttempts=1 makes no retry", async () => {
  // Regression test for the maxAttempts option: setting it to 1
  // means "try once, give up immediately on error". This locks in
  // the option's contract.
  const { adapter, calls } = makeAdapter([
    { kind: "error", status: 503, message: "down" },
    { kind: "ok", value: "ok" },
  ]);
  const wrapped = new RetryAdapterWrapper(adapter, {
    maxAttempts: 1,
    baseDelayMs: 1,
  });
  await assert.rejects(() => wrapped.generateThinking("hi"), /down/);
  assert.equal(calls.count, 1, "maxAttempts=1 should make exactly one attempt");
});

test("withRetry() returns a different instance from the inner adapter", () => {
  // The wrapper should not be the same object as the inner adapter
  // (otherwise there's no retry happening).
  const { adapter } = makeAdapter([{ kind: "ok", value: "ok" }]);
  const wrapped = withRetry(adapter, { maxAttempts: 2, baseDelayMs: 1 });
  assert.notEqual(wrapped, adapter);
  assert.ok(wrapped !== adapter, "wrapped should be a different object");
});
