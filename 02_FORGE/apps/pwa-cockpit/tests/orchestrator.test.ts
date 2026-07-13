// tests/orchestrator.test.ts
//
// Phase 6: runtime tests for AgentOrchestrator.dispatch timeout
// enforcement. The Phase 3-5 orchestrator only checked `maxMs` BETWEEN
// steps, so a hung LLM or tool could hang the agent forever. This
// file exercises the withTimeout wrapper added in Phase 6 to confirm
// the per-call timeout actually fires.
//
// Runs under `node --import tsx --test tests/*.test.ts`.

import assert from "node:assert/strict";
import test from "node:test";
import {
  AgentOrchestrator,
  TimeoutError,
} from "../src/lib/agents/orchestrator";
import type {
  Agent,
  IntelligenceAdapter,
  Tool,
} from "../src/lib/agents/types";

// A LLM adapter that never resolves. Used to prove the per-call
// timeout fires (the Phase 6 bug fix).
const HANGING_ADAPTER: IntelligenceAdapter = {
  generateThinking: () => new Promise<string>(() => {
    // intentionally empty
  }),
};

// A LLM adapter that returns a final answer immediately.
const FAST_ADAPTER: IntelligenceAdapter = {
  generateThinking: async () => "Final answer.",
};

// A LLM adapter that emits a valid `Action:` call on the first step
// and a final answer on the second step. Used to exercise the tool
// path.
function stepAdapter(thoughts: readonly string[]): IntelligenceAdapter {
  let i = 0;
  return {
    generateThinking: async () => {
      const t = thoughts[Math.min(i, thoughts.length - 1)];
      i += 1;
      return t ?? "";
    },
  };
}

// A tool that hangs forever. Used to prove the per-call tool timeout
// fires and the error is recorded as an observation (so the loop
// can continue to the next step).
const HANGING_TOOL: Tool = {
  name: "hanging",
  description: "A tool that never resolves (for timeout tests).",
  execute: () => new Promise<string>(() => {
    // intentionally empty
  }),
};

const TEST_AGENT: Agent = {
  name: "TestAgent",
  goal: "Test the orchestrator.",
  tools: { hanging: HANGING_TOOL },
};

const NOOP_AGENT: Agent = {
  name: "NoopAgent",
  goal: "Test the orchestrator without tools.",
  tools: {},
};

test("AgentOrchestrator.dispatch enforces maxMs on a hanging LLM (the bug fix)", async () => {
  const orchestrator = new AgentOrchestrator(HANGING_ADAPTER);
  const start = Date.now();
  const result = await orchestrator.dispatch(TEST_AGENT, "test input", 5, 100);
  const elapsed = Date.now() - start;
  assert.equal(result.ok, false);
  assert.match(result.reason ?? "", /timeout/);
  // Should return within ~100ms (the per-call timeout) plus overhead.
  // Allow generous slack for CI jitter, but fail loudly if it hangs.
  assert.ok(
    elapsed < 1000,
    `dispatch took ${elapsed}ms with maxMs=100; expected < 1000ms`,
  );
});

test("AgentOrchestrator.dispatch returns ok on a fast LLM with no Action header", async () => {
  const orchestrator = new AgentOrchestrator(FAST_ADAPTER);
  const result = await orchestrator.dispatch(NOOP_AGENT, "test input", 5, 1000);
  assert.equal(result.ok, true);
  assert.equal(result.output, "Final answer.");
  assert.equal(result.steps.length, 1);
  assert.equal(result.steps[0]?.action, null);
});

test("AgentOrchestrator.dispatch records tool timeout as an observation (budget exhausted after)", async () => {
  // When a tool hangs, `withTimeout` fires after the full remaining
  // budget. The loop then checks the budget, finds it exhausted, and
  // returns `ok: false` with reason "budget exceeded: maxMs". The
  // tool timeout is recorded as the observation for the first step
  // so operators can see what happened.
  //
  // Design note: the tool gets the full remaining budget (not a
  // fraction) so a hung tool can't silently consume the budget
  // step-by-step. After any tool timeout, the loop exits. If we
  // ever need "continue after tool timeout", the design would need
  // to change to per-step budgets (e.g. maxMs / maxSteps).
  const adapter = stepAdapter([
    'Action: hanging({})',
    "Final answer.", // never reached — budget exhausted after step 1
  ]);
  const orchestrator = new AgentOrchestrator(adapter);
  const result = await orchestrator.dispatch(TEST_AGENT, "test input", 5, 80);
  assert.equal(result.ok, false);
  assert.equal(result.reason, "budget exceeded: maxMs");
  assert.equal(result.steps.length, 1);
  const first = result.steps[0];
  assert.ok(first?.action, "first step should have an action");
  assert.match(first?.observation ?? "", /timeout/);
});

test("TimeoutError is exported with the correct name and is an Error subclass", () => {
  const err = new TimeoutError("test");
  assert.equal(err.name, "TimeoutError");
  assert.ok(err instanceof Error);
  assert.equal(err.message, "test");
});

test("AgentOrchestrator.dispatch treats non-timeout LLM errors as hard failures", async () => {
  // The catch block in dispatch handles any thrown Error that isn't
  // a TimeoutError by returning ok: false with reason "llm error: <message>".
  // This covers network errors, 429s, auth failures, etc.
  const errorAdapter: IntelligenceAdapter = {
    generateThinking: async () => {
      throw new Error("network down");
    },
  };
  const orchestrator = new AgentOrchestrator(errorAdapter);
  const result = await orchestrator.dispatch(NOOP_AGENT, "test input", 5, 1000);
  assert.equal(result.ok, false);
  assert.match(result.reason ?? "", /llm error: network down/);
});

test("AgentOrchestrator.dispatch respects small maxMs budgets (no floor overshoot)", async () => {
  // Regression test for the Math.max(100, ...) floor bug: a small
  // maxMs must not be exceeded by the per-call timeout floor.
  const orchestrator = new AgentOrchestrator(HANGING_ADAPTER);
  const start = Date.now();
  const result = await orchestrator.dispatch(NOOP_AGENT, "test input", 5, 20);
  const elapsed = Date.now() - start;
  assert.equal(result.ok, false);
  assert.match(result.reason ?? "", /timeout/);
  // With maxMs=20, the per-call timeout should be ~20ms (not 100ms).
  // Allow generous slack for CI jitter, but fail loudly if it exceeds 500ms.
  assert.ok(
    elapsed < 500,
    `dispatch took ${elapsed}ms with maxMs=20; per-call floor overshoot`,
  );
});
