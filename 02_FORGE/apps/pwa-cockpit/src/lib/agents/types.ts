// src/lib/agents/types.ts
//
// Phase 3 Agent abstraction — types module.
//
// Edge-runtime compatible: no Node primitives, no React imports. The Agent
// shape mirrors the standard ReAct loop (observe → think → act) but stays
// thin enough to run on Vercel Edge / Cloudflare Workers without a heavy
// SDK. Concrete LLM integration is delegated to the IntelligenceAdapter
// (see PORTAL_CORE/src/lib/intelligence/adapter.ts for the OpenAI/Ollama
// implementations); the orchestrator just calls `generateThinking` and
// parses the response for an `Action: toolName({...})` directive.

// ── Budget enforcement ────────────────────────────────────────────────────
export interface AgentBudget {
  maxSteps: number;
  maxMs: number;
  startTime: number;
}

// ── Tool surface ──────────────────────────────────────────────────────────
export interface Tool {
  name: string;
  description: string;
  execute: (args: Record<string, unknown>) => Promise<string>;
}

// ── LLM adapter (edge-safe interface; concrete impls live elsewhere) ──────
export interface IntelligenceAdapter {
  generateThinking: (prompt: string) => Promise<string>;
}

// ── Agent ─────────────────────────────────────────────────────────────────
export interface Agent {
  name: string;
  goal: string;
  tools: Record<string, Tool>;
}

// ── Per-step trace (for observability + tests) ────────────────────────────
export interface AgentStep {
  step: number;
  thought: string;
  action: { name: string; args: Record<string, unknown> } | null;
  observation: string | null;
  // Set when the LLM emitted a syntactically-valid `Action: tool(...)`
  // header but the JSON body failed to parse. Surfaces the parse error
  // to operators instead of silently treating it as a final answer.
  parseError?: string;
}

// ── Run result ────────────────────────────────────────────────────────────
export interface AgentResult {
  ok: boolean;
  output: string;
  steps: readonly AgentStep[];
  reason?: string;
}
