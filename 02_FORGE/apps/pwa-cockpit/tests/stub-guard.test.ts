// tests/stub-guard.test.ts
//
// Phase 8: tests for the NODE_ENV=production stub guard in
// createLLMAdapter() (src/lib/agents/llm-adapter.ts). The guard
// prevents the footgun where a misconfigured Vercel env silently
// returns deterministic fake answers to real users.
//
// All tests mutate process.env inside a t.after so the suite is
// hermetic and does not affect other tests. NODE_ENV is declared
// `readonly` in @types/node, so we use a setEnv() helper that
// casts the env object to a writable record before assignment.
//
// Runs under `node --import tsx --test tests/*.test.ts`.

import assert from "node:assert/strict";
import test from "node:test";
import {
  AnthropicAdapter,
  GeminiAdapter,
  OpenAIAdapter,
  StubAdapter,
  createLLMAdapter,
} from "../src/lib/agents/llm-adapter";

const ENV_KEYS = [
  "LLM_PROVIDER",
  "NODE_ENV",
  "GEMINI_API_KEY",
  "OPENAI_API_KEY",
  "ANTHROPIC_API_KEY",
] as const;

type EnvKey = (typeof ENV_KEYS)[number];

// NODE_ENV is typed as readonly in @types/node, so a direct
// `process.env.NODE_ENV = "production"` triggers TS2540. The cast
// to Record<string, string | undefined> bypasses the readonly
// qualifier at the call site; the underlying process.env is
// always mutable at runtime.
function setEnv(key: EnvKey, value: string | undefined): void {
  const env = process.env as Record<string, string | undefined>;
  if (value === undefined) {
    delete env[key];
  } else {
    env[key] = value;
  }
}

test("createLLMAdapter refuses stub in production", async (t) => {
  const original: Record<string, string | undefined> = {};
  for (const k of ENV_KEYS) original[k] = process.env[k];

  t.after(() => {
    for (const k of ENV_KEYS) setEnv(k, original[k]);
  });

  await t.test(
    "NODE_ENV=production + LLM_PROVIDER unset → throws with actionable message",
    () => {
      setEnv("NODE_ENV", "production");
      setEnv("LLM_PROVIDER", undefined);
      assert.throws(
        () => createLLMAdapter(),
        /Refusing to start.*stub.*production/i,
      );
    },
  );

  await t.test(
    "NODE_ENV=production + LLM_PROVIDER=stub → throws with actionable message",
    () => {
      setEnv("NODE_ENV", "production");
      setEnv("LLM_PROVIDER", "stub");
      assert.throws(
        () => createLLMAdapter(),
        /Refusing to start.*stub.*production/i,
      );
    },
  );

  await t.test(
    "NODE_ENV=production + LLM_PROVIDER=gemini (no key) → returns GeminiAdapter (guard does not over-block)",
    () => {
      setEnv("NODE_ENV", "production");
      setEnv("LLM_PROVIDER", "gemini");
      setEnv("GEMINI_API_KEY", undefined);
      // The guard doesn't fire (provider is not stub). The factory
      // returns a GeminiAdapter; calling generateThinking throws
      // about the missing key. This confirms the guard does not
      // over-block legitimate providers.
      const adapter = createLLMAdapter();
      assert.ok(adapter instanceof GeminiAdapter);
    },
  );

  await t.test(
    "NODE_ENV=production + LLM_PROVIDER=openai + OPENAI_API_KEY set → returns OpenAIAdapter (no throw)",
    () => {
      setEnv("NODE_ENV", "production");
      setEnv("LLM_PROVIDER", "openai");
      setEnv("OPENAI_API_KEY", "test_key");
      const adapter = createLLMAdapter();
      assert.ok(adapter instanceof OpenAIAdapter);
    },
  );

  await t.test(
    "NODE_ENV=production + LLM_PROVIDER=anthropic + ANTHROPIC_API_KEY set → returns AnthropicAdapter (no throw)",
    () => {
      setEnv("NODE_ENV", "production");
      setEnv("LLM_PROVIDER", "anthropic");
      setEnv("ANTHROPIC_API_KEY", "test_key");
      const adapter = createLLMAdapter();
      assert.ok(adapter instanceof AnthropicAdapter);
    },
  );

  await t.test(
    "NODE_ENV=development + LLM_PROVIDER=stub → returns StubAdapter (guard is dormant in dev)",
    () => {
      setEnv("NODE_ENV", "development");
      setEnv("LLM_PROVIDER", "stub");
      const adapter = createLLMAdapter();
      assert.ok(adapter instanceof StubAdapter);
    },
  );

  await t.test(
    "NODE_ENV unset + LLM_PROVIDER=stub → returns StubAdapter (guard is dormant when NODE_ENV is not 'production')",
    () => {
      setEnv("NODE_ENV", undefined);
      setEnv("LLM_PROVIDER", "stub");
      const adapter = createLLMAdapter();
      assert.ok(adapter instanceof StubAdapter);
    },
  );
});
