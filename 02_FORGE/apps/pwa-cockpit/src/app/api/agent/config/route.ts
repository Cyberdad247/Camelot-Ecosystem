// src/app/api/agent/config/route.ts
//
// Phase 9: read-only PWA cockpit config endpoint. The OmniRoute UI
// (Goose desktop app's ProviderGrid, or any external operator console)
// polls this to learn what LLM provider the cockpit is currently
// configured with. Read-only by design: the PWA cockpit runs on
// Vercel Edge where LLM_PROVIDER and the *_API_KEY env vars are
// statically replaced at build time, so runtime config writes are not
// feasible (they would require a Vercel API integration that's out of
// scope for the cockpit). For config changes, operators redeploy with
// new env values — see DEPLOYMENT.md §1.1 pre-deploy checklist.
//
// Edge-runtime safe: only reads process.env and returns a small JSON
// payload. No Node primitives, no React imports. The endpoint runs on
// the Node runtime (not edge) so it can reliably read ALL env vars
// including ones that might not be exposed to the edge bundle.

import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// CORS: this endpoint is intentionally consumable from any origin so that
// any operator console (Goose desktop UI, monitoring dashboards, the CAMELOT
// CLI) can poll it without an explicit pre-allowlist. Read-only by design,
// so the attack surface is a single env-var read.
const CORS_HEADERS: HeadersInit = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  // Do NOT let any intermediate cache shoulder the response across endpoints;
  // the Vercel Edge can otherwise briefly serve a stale provider when the
  // cockpit redeploys mid-session.
  "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
};

export async function OPTIONS(): Promise<NextResponse> {
  return new NextResponse(null, { status: 204, headers: CORS_HEADERS });
}

type ProviderId =
  | "stub"
  | "gemini"
  | "openai"
  | "anthropic"
  | "agents_a1";

// `export` so the symmetric drift test
// (tests/agent-config-drift.test.ts) and the contract-pinning
// `as const satisfies` anchors can `import type { AgentConfig }`
// from this module without tsc TS2459.
export interface AgentConfig {
  /** Active LLM provider id (matches the LLMProvider union in src/lib/agents/llm-adapter.ts). */
  active_provider: ProviderId;
  /** Human-readable provider label for the OmniRoute UI to display. */
  provider_label: string;
  /** Resolved model id (env override OR built-in default). */
  model: string;
  /**
   * Per-provider metadata. Each entry reports ONLY whether the relevant
   * env var is set — never the value (the OmniRoute UI doesn't need the
   * key, just to know whether to display a "configured" badge). The
   * resolved model lives at the top level (`model`), not here, so the
   * shape is uniform across providers.
   */
  config: Record<string, boolean>;
  /** Always true: the endpoint is read-only by design. */
  read_only: true;
}

const LABELS: Record<ProviderId, string> = {
  stub: "Stub (deterministic local fallback)",
  gemini: "Google Gemini",
  openai: "OpenAI",
  anthropic: "Anthropic Claude",
  agents_a1: "Agents-A1 (35B MoE, OpenAI-compat local)",
};

const DEFAULTS: Record<ProviderId, string> = {
  stub: "stub-deterministic",
  gemini: "gemini-2.0-flash",
  openai: "gpt-4o-mini",
  anthropic: "claude-3-5-haiku-latest",
  agents_a1: "InternScience/Agents-A1",
};

function detectProvider(): ProviderId {
  const raw = (process.env.LLM_PROVIDER ?? "stub").toLowerCase();
  if (
    raw === "stub" ||
    raw === "gemini" ||
    raw === "openai" ||
    raw === "anthropic" ||
    raw === "agents_a1"
  ) {
    return raw;
  }
  // Unknown value — report stub so the UI surfaces the misconfig.
  return "stub";
}

function buildConfig(provider: ProviderId): Record<string, boolean> {
  switch (provider) {
    case "stub":
      return { stub_active: true };
    case "gemini":
      return { gemini_key_set: Boolean(process.env.GEMINI_API_KEY) };
    case "openai":
      return { openai_key_set: Boolean(process.env.OPENAI_API_KEY) };
    case "anthropic":
      return { anthropic_key_set: Boolean(process.env.ANTHROPIC_API_KEY) };
    case "agents_a1":
      return {
        agents_a1_base_url_set: Boolean(process.env.AGENTS_A1_BASE_URL),
        agents_a1_key_set: Boolean(process.env.AGENTS_A1_API_KEY),
      };
  }
}

function resolveModel(provider: ProviderId): string {
  switch (provider) {
    case "stub":
      return DEFAULTS.stub;
    case "gemini":
      return process.env.GEMINI_MODEL ?? DEFAULTS.gemini;
    case "openai":
      return process.env.OPENAI_MODEL ?? DEFAULTS.openai;
    case "anthropic":
      return process.env.ANTHROPIC_MODEL ?? DEFAULTS.anthropic;
    case "agents_a1":
      return process.env.AGENTS_A1_MODEL ?? DEFAULTS.agents_a1;
  }
}

export function GET(): NextResponse<AgentConfig> {
  const provider = detectProvider();
  return NextResponse.json<AgentConfig>(
    {
      active_provider: provider,
      provider_label: LABELS[provider],
      model: resolveModel(provider),
      config: buildConfig(provider),
      read_only: true,
    },
    { headers: CORS_HEADERS }
  );
}
