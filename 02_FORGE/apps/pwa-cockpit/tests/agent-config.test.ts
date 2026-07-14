// tests/agent-config.test.ts
//
// Phase 9: env-mocked tests for the GET / OPTIONS handlers in
// src/app/api/agent/config/route.ts. The endpoint reads process.env
// at call time, so we mutate env in a t.before/t.after pair so other
// tests aren't polluted.
//
// 19 subtests across 5 buckets: stub / per-provider coverage (gemini,
// openai, anthropic, agents_a1) / LLM_PROVIDER dispatch edge cases /
// CORS + response headers / contract invariants.
//
// Runs under `npx tsx --test tests/agent-config.test.ts` (matches
// the convention used by llm-adapter.test.ts and the rest of the
// tests/ folder).

import assert from "node:assert/strict";
import test from "node:test";
import { GET, OPTIONS } from "../src/app/api/agent/config/route";

/**
 * All env vars the route reads. Snapshotted before the suite starts
 * and restored after any test in the suite so we don't pollute
 * sibling suites (e.g. llm-adapter.test.ts).
 */
const ENV_KEYS = [
  "LLM_PROVIDER",
  "GEMINI_API_KEY",
  "GEMINI_MODEL",
  "OPENAI_API_KEY",
  "OPENAI_MODEL",
  "ANTHROPIC_API_KEY",
  "ANTHROPIC_MODEL",
  "AGENTS_A1_BASE_URL",
  "AGENTS_A1_API_KEY",
  "AGENTS_A1_MODEL",
] as const;

test("GET /api/agent/config", async (t) => {
  // Snapshot the ambient env once before any subtest runs.
  const originalEnv: Record<string, string | undefined> = {};
  for (const k of ENV_KEYS) originalEnv[k] = process.env[k];

  t.after(() => {
    for (const k of ENV_KEYS) {
      if (originalEnv[k] === undefined) delete process.env[k];
      else process.env[k] = originalEnv[k];
    }
  });

  /**
   * Clear every relevant env var so each subtest starts from a known
   * baseline. The next line under `t.test` sets only what that subtest
   * needs.
   */
  const resetEnv = () => {
    for (const k of ENV_KEYS) delete process.env[k];
  };

  // ---------- stub ----------
  await t.test("LLM_PROVIDER=stub → deterministic defaults (no env keys)", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "stub";
    const res = GET();
    assert.equal(res.status, 200);
    assert.deepEqual(await res.json(), {
      active_provider: "stub",
      provider_label: "Stub (deterministic local fallback)",
      model: "stub-deterministic",
      config: { stub_active: true },
      read_only: true,
    });
  });

  // ---------- gemini ----------
  await t.test("LLM_PROVIDER=gemini (no key, no model) → default model, key_set=false", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "gemini";
    const res = GET();
    assert.equal(res.status, 200);
    assert.deepEqual(await res.json(), {
      active_provider: "gemini",
      provider_label: "Google Gemini",
      model: "gemini-2.0-flash",
      config: { gemini_key_set: false },
      read_only: true,
    });
  });

  await t.test("LLM_PROVIDER=gemini + GEMINI_API_KEY + GEMINI_MODEL → model override + key_set=true", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "gemini";
    process.env.GEMINI_API_KEY = "sk-test";
    process.env.GEMINI_MODEL = "gemini-1.5-pro";
    const res = GET();
    assert.deepEqual(await res.json(), {
      active_provider: "gemini",
      provider_label: "Google Gemini",
      model: "gemini-1.5-pro",
      config: { gemini_key_set: true },
      read_only: true,
    });
  });

  // ---------- openai ----------
  await t.test("LLM_PROVIDER=openai (no key) → default model, key_set=false", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "openai";
    const res = GET();
    assert.deepEqual(await res.json(), {
      active_provider: "openai",
      provider_label: "OpenAI",
      model: "gpt-4o-mini",
      config: { openai_key_set: false },
      read_only: true,
    });
  });

  await t.test("LLM_PROVIDER=openai + OPENAI_API_KEY + OPENAI_MODEL → both honored", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "openai";
    process.env.OPENAI_API_KEY = "sk-test";
    process.env.OPENAI_MODEL = "gpt-4o";
    const res = GET();
    assert.deepEqual(await res.json(), {
      active_provider: "openai",
      provider_label: "OpenAI",
      model: "gpt-4o",
      config: { openai_key_set: true },
      read_only: true,
    });
  });

  await t.test("OPENAI_API_KEY=\"\" (empty string, not unset) → key_set=false (Boolean(\"\") === false)", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "openai";
    process.env.OPENAI_API_KEY = ""; // explicitly empty, DISTINCT from delete
    const res = GET();
    const json = await res.json();
    assert.equal(json.active_provider, "openai");
    assert.equal(json.config.openai_key_set, false);
  });

  // ---------- anthropic ----------
  await t.test("LLM_PROVIDER=anthropic (no key) → default model, key_set=false", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "anthropic";
    const res = GET();
    assert.deepEqual(await res.json(), {
      active_provider: "anthropic",
      provider_label: "Anthropic Claude",
      model: "claude-3-5-haiku-latest",
      config: { anthropic_key_set: false },
      read_only: true,
    });
  });

  await t.test("LLM_PROVIDER=anthropic + ANTHROPIC_API_KEY + ANTHROPIC_MODEL → both honored", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "anthropic";
    process.env.ANTHROPIC_API_KEY = "sk-ant-test";
    process.env.ANTHROPIC_MODEL = "claude-3-5-sonnet-latest";
    const res = GET();
    assert.deepEqual(await res.json(), {
      active_provider: "anthropic",
      provider_label: "Anthropic Claude",
      model: "claude-3-5-sonnet-latest",
      config: { anthropic_key_set: true },
      read_only: true,
    });
  });

  // ---------- agents_a1 ----------
  await t.test("LLM_PROVIDER=agents_a1 (no env vars) → both flags false, default model", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "agents_a1";
    const res = GET();
    assert.deepEqual(await res.json(), {
      active_provider: "agents_a1",
      provider_label: "Agents-A1 (35B MoE, OpenAI-compat local)",
      model: "InternScience/Agents-A1",
      config: { agents_a1_base_url_set: false, agents_a1_key_set: false },
      read_only: true,
    });
  });

  await t.test("LLM_PROVIDER=agents_a1 + AGENTS_A1_BASE_URL + AGENTS_A1_API_KEY → both flags true", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "agents_a1";
    process.env.AGENTS_A1_BASE_URL = "http://127.0.0.1:8000/v1";
    process.env.AGENTS_A1_API_KEY = "local-vllm-key";
    const res = GET();
    const json = await res.json();
    assert.equal(json.active_provider, "agents_a1");
    assert.deepEqual(json.config, {
      agents_a1_base_url_set: true,
      agents_a1_key_set: true,
    });
  });

  await t.test("LLM_PROVIDER=agents_a1 + only AGENTS_A1_BASE_URL → base_url_set=true, key_set=false (local vLLM is auth-less)", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "agents_a1";
    process.env.AGENTS_A1_BASE_URL = "http://127.0.0.1:8000/v1";
    const res = GET();
    const json = await res.json();
    assert.deepEqual(json.config, {
      agents_a1_base_url_set: true,
      agents_a1_key_set: false,
    });
  });

  await t.test("LLM_PROVIDER=agents_a1 + AGENTS_A1_MODEL → model override honored", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "agents_a1";
    process.env.AGENTS_A1_BASE_URL = "http://127.0.0.1:8000/v1";
    process.env.AGENTS_A1_MODEL = "InternScience/Agents-A1-Q4";
    const res = GET();
    const json = await res.json();
    assert.equal(json.model, "InternScience/Agents-A1-Q4");
    assert.equal(json.read_only, true);
  });

  // ---------- edge cases on the dispatcher ----------
  await t.test("LLM_PROVIDER unset → falls through to stub (safe default)", async () => {
    resetEnv();
    delete process.env.LLM_PROVIDER;
    const res = GET();
    const json = await res.json();
    assert.equal(json.active_provider, "stub");
    assert.equal(json.model, "stub-deterministic");
  });

  await t.test("LLM_PROVIDER=garbage → falls through to stub (unknown values are not silently accepted)", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "not-a-real-provider";
    const res = GET();
    const json = await res.json();
    assert.equal(json.active_provider, "stub");
  });

  await t.test("LLM_PROVIDER=GEMINI (uppercase) → route lowercases first → accepted as gemini", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "GEMINI";
    const res = GET();
    const json = await res.json();
    // Pin the contract: provider ids are CASE-INSENSITIVE. The route
    // does `(process.env.LLM_PROVIDER ?? \"stub\").toLowerCase()` BEFORE
    // the membership check, so any case of a known id is accepted and
    // the response normalizes to lowercase.
    assert.equal(json.active_provider, "gemini");
    assert.equal(json.provider_label, "Google Gemini");
  });

  // ---------- CORS / response headers ----------
  await t.test("GET response includes CORS headers and no Pragma (HTTP/1.0 legacy)", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "stub";
    const res = GET();
    assert.equal(
      res.headers.get("Access-Control-Allow-Origin"),
      "*",
      "Access-Control-Allow-Origin must be '*'"
    );
    assert.equal(
      res.headers.get("Cache-Control"),
      "no-store, no-cache, must-revalidate, proxy-revalidate",
      "no-store cache directive must be set so Vercel Edge cannot shoulder"
    );
    assert.equal(
      res.headers.get("Pragma"),
      null,
      "legacy HTTP/1.0 Pragma header should not be present"
    );
  });

  await t.test("OPTIONS preflight returns 204 with CORS + method headers", async () => {
    const res = await OPTIONS();
    assert.equal(res.status, 204);
    assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
    assert.equal(res.headers.get("Access-Control-Allow-Methods"), "GET, OPTIONS");
    assert.equal(res.headers.get("Access-Control-Allow-Headers"), "Content-Type");
  });

  // ---------- contract invariants ----------
  await t.test("read_only is always true (contract: endpoint never accepts writes)", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "agents_a1";
    const res = GET();
    const json = await res.json();
    assert.equal(json.read_only, true);
  });

  await t.test("config never includes API key VALUES (only *_set booleans)", async () => {
    resetEnv();
    process.env.LLM_PROVIDER = "openai";
    process.env.OPENAI_API_KEY = "sk-must-not-leak-1234";
    const res = GET();
    const json = (await res.json()) as Record<string, unknown>;
    const configBlob = JSON.stringify(json);
    assert.ok(
      !configBlob.includes("sk-must-not-leak-1234"),
      "API key value must NEVER appear in the response"
    );
    assert.equal(
      (json.config as Record<string, boolean>).openai_key_set,
      true
    );
  });
});
