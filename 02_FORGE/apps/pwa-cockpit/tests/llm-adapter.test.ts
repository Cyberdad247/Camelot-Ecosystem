// tests/llm-adapter.test.ts
//
// Phase 5: env-mocked tests for createLLMAdapter() in
// src/lib/agents/llm-adapter.ts. The factory reads LLM_PROVIDER at
// call time and dispatches to the right adapter. These tests mutate
// process.env in a t.before/t.after pair so they don't pollute
// other tests.
//
// Runs under `node --import tsx --test tests/*.test.ts`.

import assert from "node:assert/strict";
import test from "node:test";
import {
  AgentsA1Adapter,
  AnthropicAdapter,
  GeminiAdapter,
  OpenAIAdapter,
  StubAdapter,
  createLLMAdapter,
} from "../src/lib/agents/llm-adapter";

const ENV_KEYS = [
  "LLM_PROVIDER",
  "GEMINI_API_KEY",
  "OPENAI_API_KEY",
  "ANTHROPIC_API_KEY",
  "AGENTS_A1_BASE_URL",
  "AGENTS_A1_API_KEY",
  "AGENTS_A1_MODEL",
] as const;

test("createLLMAdapter factory", async (t) => {
  // Snapshot env at the start of the suite and restore after every test.
  const originalEnv: Record<string, string | undefined> = {};
  for (const k of ENV_KEYS) originalEnv[k] = process.env[k];

  t.after(() => {
    for (const k of ENV_KEYS) {
      if (originalEnv[k] === undefined) delete process.env[k];
      else process.env[k] = originalEnv[k];
    }
  });

  await t.test("no env → returns StubAdapter", () => {
    delete process.env.LLM_PROVIDER;
    const adapter = createLLMAdapter();
    assert.ok(adapter instanceof StubAdapter);
  });

  await t.test("LLM_PROVIDER=stub → returns StubAdapter", () => {
    process.env.LLM_PROVIDER = "stub";
    const adapter = createLLMAdapter();
    assert.ok(adapter instanceof StubAdapter);
  });

  await t.test("StubAdapter returns a deterministic final answer", async () => {
    delete process.env.LLM_PROVIDER;
    const adapter = createLLMAdapter();
    const out = await adapter.generateThinking("anything");
    assert.ok(typeof out === "string" && out.length > 0);
    assert.ok(out.includes("StubIntelligenceAdapter"));
  });

  await t.test("LLM_PROVIDER=gemini → returns GeminiAdapter; missing key throws", async () => {
    process.env.LLM_PROVIDER = "gemini";
    delete process.env.GEMINI_API_KEY;
    const adapter = createLLMAdapter();
    assert.ok(adapter instanceof GeminiAdapter);
    await assert.rejects(
      () => adapter.generateThinking("hi"),
      /missing GEMINI_API_KEY/,
    );
  });

  await t.test("LLM_PROVIDER=openai → returns OpenAIAdapter; missing key throws", async () => {
    process.env.LLM_PROVIDER = "openai";
    delete process.env.OPENAI_API_KEY;
    const adapter = createLLMAdapter();
    assert.ok(adapter instanceof OpenAIAdapter);
    await assert.rejects(
      () => adapter.generateThinking("hi"),
      /missing OPENAI_API_KEY/,
    );
  });

  await t.test("LLM_PROVIDER=anthropic → returns AnthropicAdapter; missing key throws", async () => {
    process.env.LLM_PROVIDER = "anthropic";
    delete process.env.ANTHROPIC_API_KEY;
    const adapter = createLLMAdapter();
    assert.ok(adapter instanceof AnthropicAdapter);
    await assert.rejects(
      () => adapter.generateThinking("hi"),
      /missing ANTHROPIC_API_KEY/,
    );
  });

  await t.test("LLM_PROVIDER=invalid → throws on create", () => {
    process.env.LLM_PROVIDER = "invalid";
    assert.throws(() => createLLMAdapter(), /unknown LLM_PROVIDER: invalid/);
  });

  await t.test("LLM_PROVIDER=agents_a1 → returns AgentsA1Adapter; missing BASE_URL throws", async () => {
    process.env.LLM_PROVIDER = "agents_a1";
    delete process.env.AGENTS_A1_BASE_URL;
    const adapter = createLLMAdapter();
    assert.ok(adapter instanceof AgentsA1Adapter);
    await assert.rejects(
      () => adapter.generateThinking("hi"),
      /missing AGENTS_A1_BASE_URL/,
    );
  });

  await t.test("LLM_PROVIDER=agents_a1 with BASE_URL → returns AgentsA1Adapter (no throw on create)", () => {
    process.env.LLM_PROVIDER = "agents_a1";
    process.env.AGENTS_A1_BASE_URL = "http://127.0.0.1:8000/v1";
    const adapter = createLLMAdapter();
    assert.ok(adapter instanceof AgentsA1Adapter);
  });
});
