// src/app/api/agent/run/route.ts
//
// Phase 4 /api/agent/run — edge-runtime POST handler for the Agent
// abstraction. Validates the Bearer token with the shared gate
// (so this handler stays in lockstep with the middleware regex),
// resolves the named agent by id, then dispatches through the
// AgentOrchestrator and returns the AgentResult.
//
// Edge-safe: no Node primitives, no React imports. The StubIntelligenceAdapter
// below MUST be replaced with a real LLM adapter before production; it
// currently returns a deterministic "no Action" final answer so the
// HTTP round-trip can be exercised end-to-end without an upstream call.

import { NextResponse } from "next/server";
import { isValidBearerToken } from "@/lib/security/gate";
import {
  AgentOrchestrator,
  getAgentById,
} from "@/lib/agents";
import { createLLMAdapter } from "@/lib/agents/llm-adapter";
import type { AgentResult } from "@/lib/agents/types";

export const runtime = "edge";
export const dynamic = "force-dynamic";

// The LLM adapter is env-configurable. Set LLM_PROVIDER=gemini|openai|anthropic
// in the deploy env to use a real model; the default ("stub") returns a
// deterministic final answer so the round-trip is exercisable without an
// upstream call. See src/lib/agents/llm-adapter.ts.

interface RunBody {
  agentId?: unknown;
  input?: unknown;
  budget?: { maxSteps?: unknown; maxMs?: unknown };
}

export async function POST(req: Request): Promise<NextResponse<AgentResult>> {
  // 1. Bearer validation via shared gate (matches middleware regex).
  const authHeader = req.headers.get("Authorization") ?? "";
  if (!isValidBearerToken(authHeader)) {
    return NextResponse.json<AgentResult>(
      { ok: false, output: "", steps: [], reason: "unauthorized" },
      { status: 401 },
    );
  }

  // 2. Body parsing.
  let body: RunBody;
  try {
    body = (await req.json()) as RunBody;
  } catch {
    return NextResponse.json<AgentResult>(
      { ok: false, output: "", steps: [], reason: "invalid json body" },
      { status: 400 },
    );
  }

  const { agentId, input } = body;
  if (typeof agentId !== "string" || typeof input !== "string") {
    return NextResponse.json<AgentResult>(
      {
        ok: false,
        output: "",
        steps: [],
        reason: "agentId and input must be strings",
      },
      { status: 400 },
    );
  }

  // 3. Optional budget overrides. Validate before dispatch so a
  // degenerate budget (0 or negative) is rejected at the edge
  // rather than silently returning "budget exceeded" with no work
  // done.
  const budget = body.budget ?? {};
  const rawMaxSteps = budget.maxSteps;
  const rawMaxMs = budget.maxMs;
  if (
    rawMaxSteps !== undefined &&
    (typeof rawMaxSteps !== "number" ||
      !Number.isInteger(rawMaxSteps) ||
      rawMaxSteps < 1)
  ) {
    return NextResponse.json<AgentResult>(
      {
        ok: false,
        output: "",
        steps: [],
        reason: "budget.maxSteps must be a positive integer",
      },
      { status: 400 },
    );
  }
  if (
    rawMaxMs !== undefined &&
    (typeof rawMaxMs !== "number" ||
      !Number.isInteger(rawMaxMs) ||
      rawMaxMs < 1)
  ) {
    return NextResponse.json<AgentResult>(
      {
        ok: false,
        output: "",
        steps: [],
        reason: "budget.maxMs must be a positive integer",
      },
      { status: 400 },
    );
  }
  const maxSteps = rawMaxSteps as number | undefined;
  const maxMs = rawMaxMs as number | undefined;

  // 4. Agent lookup (case-insensitive via the barrel helper).
  const agent = getAgentById(agentId);
  if (!agent) {
    return NextResponse.json<AgentResult>(
      { ok: false, output: "", steps: [], reason: "agent not found" },
      { status: 404 },
    );
  }

  // 5. Dispatch.
  const orchestrator = new AgentOrchestrator(createLLMAdapter());
  const result = await orchestrator.dispatch(agent, input, maxSteps, maxMs);

  // 6. Response: always the AgentResult body, status reflects ok.
  return NextResponse.json<AgentResult>(result, {
    status: result.ok ? 200 : 500,
  });
}
