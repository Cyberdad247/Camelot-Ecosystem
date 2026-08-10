// tests/telemetry-batching.test.ts
//
// Phase 8: asserts the new batching + backpressure behavior of
// src/lib/telemetry.ts. Mocks globalThis.fetch so we can observe
// how many HTTP requests the module issues per N track() calls and
// what the batched body looks like.
//
// The tests set process.env.NEXT_PUBLIC_TELEMETRY_URL at module load
// time (before the first track()) so init() picks it up. Each test
// calls __resetTelemetryForTesting() to start with a clean buffer
// (the buffer is a module-level singleton, so without reset, events
// from one test leak into the next). They restore the original env
// in t.after.
//
// Runs under `node --import tsx --test tests/*.test.ts`.

import assert from "node:assert/strict";
import test, { after, beforeEach } from "node:test";

// Set the endpoint BEFORE the first track() so init() reads it.
// Must be set at module load, not inside a test, because init() is
// idempotent and caches the endpoint on first call.
const ORIGINAL_URL = process.env.NEXT_PUBLIC_TELEMETRY_URL;
process.env.NEXT_PUBLIC_TELEMETRY_URL = "https://telemetry.test/events";

import {
  __resetTelemetryForTesting,
  flushSync,
  getRecentEvents,
  track,
} from "../src/lib/telemetry";

after(() => {
  if (ORIGINAL_URL === undefined) {
    delete process.env.NEXT_PUBLIC_TELEMETRY_URL;
  } else {
    process.env.NEXT_PUBLIC_TELEMETRY_URL = ORIGINAL_URL;
  }
});

// Reset module-level state before each test so events from the
// previous test don't leak into this one.
beforeEach(() => {
  __resetTelemetryForTesting();
});

// Track all fetch calls for inspection.
type FetchCall = { url: string; body: string };
const originalFetch = globalThis.fetch;
let fetchCalls: FetchCall[] = [];

function mockFetch(): void {
  fetchCalls = [];
  globalThis.fetch = (async (url: string, init?: RequestInit) => {
    fetchCalls.push({ url, body: String(init?.body ?? "") });
    return new Response(null, { status: 200 });
  }) as typeof globalThis.fetch;
}

function restoreFetch(): void {
  globalThis.fetch = originalFetch;
}

test("track() below threshold does not trigger an automatic flush", async () => {
  mockFetch();
  try {
    // 5 events, well below FLUSH_THRESHOLD=20. No flush should be
    // scheduled because track() only schedules a flush when the
    // buffer hits the threshold.
    for (let i = 0; i < 5; i++) {
      track(`below_${i}`, "system");
    }
    // Give the scheduler a brief moment to fire if it was going to.
    await new Promise((r) => setTimeout(r, 50));
    assert.equal(
      fetchCalls.length,
      0,
      "no automatic flush expected when buffer is below threshold",
    );
  } finally {
    restoreFetch();
  }
});

test("track() at threshold calls fetch once with a batched {events: [...]} body", async () => {
  mockFetch();
  try {
    for (let i = 0; i < 20; i++) {
      track(`at_threshold_${i}`, "system");
    }
    // Wait for the scheduled flush to land.
    await flushSync();
    assert.ok(
      fetchCalls.length >= 1,
      `expected at least 1 fetch call, got ${fetchCalls.length}`,
    );
    const body = JSON.parse(fetchCalls[0]!.body);
    assert.ok(Array.isArray(body.events), "body should be {events: [...]}");
    assert.equal(
      body.events.length,
      20,
      "all 20 events should be in the batch (buffer was reset in beforeEach)",
    );
    for (let i = 0; i < 20; i++) {
      assert.equal(body.events[i].name, `at_threshold_${i}`);
    }
  } finally {
    restoreFetch();
  }
});

test("flushSync() drains the buffer even below threshold", async () => {
  mockFetch();
  try {
    track("flush_a", "system");
    track("flush_b", "system");
    // Manually drain via flushSync (does not require threshold).
    await flushSync();
    assert.ok(fetchCalls.length >= 1);
    const body = JSON.parse(fetchCalls[0]!.body);
    assert.equal(body.events.length, 2);
  } finally {
    restoreFetch();
  }
});

test("failed fetch keeps events in the buffer (backpressure)", async () => {
  globalThis.fetch = (async () => {
    throw new Error("network down");
  }) as typeof globalThis.fetch;
  try {
    track("back_a", "system");
    track("back_b", "system");
    await flushSync();
    // The batched flush should have failed and re-prepended the events.
    const events = getRecentEvents(100);
    const names = events.map((e) => e.name);
    assert.ok(
      names.includes("back_a"),
      "back_a should still be in the buffer after failed flush",
    );
    assert.ok(
      names.includes("back_b"),
      "back_b should still be in the buffer after failed flush",
    );
  } finally {
    restoreFetch();
  }
});

test("getRecentEvents returns a stable view independent of flush state", () => {
  track("view_test", "system");
  const events = getRecentEvents(5);
  assert.equal(events.length > 0, true);
  assert.ok(events.some((e) => e.name === "view_test"));
});
