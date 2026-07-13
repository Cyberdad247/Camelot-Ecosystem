// src/lib/agents/orchestrator.ts
//
// Phase 3 Agent orchestrator — ReAct loop with budget enforcement.
//
// Edge-runtime compatible. Parses LLM output for `Action: toolName({...})`
// directives; re-injects observations into the prompt until the LLM
// produces a final answer (no action) or the budget is exhausted.

import type {
  Agent,
  AgentResult,
  AgentStep,
  IntelligenceAdapter,
  Tool,
} from "./types";

// Match `Action: toolName(` and find the JSON object body by counting
// both `(`/`)` and `{`/`}` together as depth, so the closing `)` of
// the action call returns depth to 0. String literals are skipped
// (with backslash-escape handling) so `}` inside a string value
// doesn't unbalance the count. This handles nested objects correctly;
// a naive non-greedy regex would stop at the first `}` and corrupt
// the JSON.
// Uniform discriminated union — every parse result carries a `kind`
// discriminator so the orchestrator can switch on it exhaustively.
// The three cases:
//   - "no_action"   — no `Action: tool(` header (final answer)
//   - "ok"          — header matched and JSON body parsed
//   - "json_error"  — header matched but JSON body failed to parse
// Keeping this as a single union (not a mix of union + null) makes
// the type easier to extend and forces the orchestrator to handle
// every case explicitly.
type ParseResult =
  | { kind: "no_action" }
  | { kind: "ok"; name: string; args: Record<string, unknown> }
  | { kind: "json_error"; error: string };

function parseAction(thought: string): ParseResult {
  const headerMatch = thought.match(/Action:\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(/);
  if (!headerMatch) return { kind: "no_action" };
  const name = headerMatch[1];
  const startIdx = (headerMatch.index ?? 0) + headerMatch[0].length;
  let depth = 1; // we're inside the opening `(`
  let inString = false;
  let escape = false;
  let i = startIdx;
  while (i < thought.length) {
    const c = thought[i];
    if (escape) { escape = false; i += 1; continue; }
    if (inString) {
      if (c === "\\") { escape = true; }
      else if (c === '"') { inString = false; }
      i += 1;
      continue;
    }
    if (c === '"') { inString = true; i += 1; continue; }
    if (c === "(" || c === "{") { depth += 1; i += 1; continue; }
    if (c === ")" || c === "}") { depth -= 1; if (depth === 0) break; i += 1; continue; }
    i += 1;
  }
  if (depth !== 0) return { kind: "no_action" };
  const jsonStr = thought.slice(startIdx, i);
  try {
    const args = JSON.parse(jsonStr) as Record<string, unknown>;
    return { kind: "ok", name, args };
  } catch (e) {
    return { kind: "json_error", error: e instanceof Error ? e.message : String(e) };
  }
}

export class AgentOrchestrator {
  constructor(private llm: IntelligenceAdapter) {}

  async dispatch(
    agent: Agent,
    input: string,
    maxSteps = 5,
    maxMs = 5000,
  ): Promise<AgentResult> {
    const startTime = Date.now();
    const steps: AgentStep[] = [];
    let current = input;

    for (let i = 0; i < maxSteps; i += 1) {
      if (Date.now() - startTime >= maxMs) {
        return { ok: false, output: "", steps, reason: "budget exceeded: maxMs" };
      }
      const thought = await this.llm.generateThinking(
        `[${agent.name} GOAL: ${agent.goal}] Input: ${current}\n` +
          `Available tools: ${Object.keys(agent.tools).join(", ")}`,
      );
      const parsed = parseAction(thought);
      if (parsed.kind === "no_action") {
        // No `Action: tool(` header → treat as final answer.
        steps.push({ step: i + 1, thought, action: null, observation: null });
        return { ok: true, output: thought, steps };
      }
      if (parsed.kind === "json_error") {
        // Header matched but body didn't parse. This is a hard failure
        // (the LLM tried to act and failed) — the orchestrator returns
        // ok: false with the parse error in the step trace so operators
        // can debug the LLM output. The thought is still returned so
        // the LLM's surrounding text is visible to the operator.
        steps.push({
          step: i + 1,
          thought,
          action: null,
          observation: null,
          parseError: parsed.error,
        });
        return {
          ok: false,
          output: thought,
          steps,
          reason: `action parse error: ${parsed.error}`,
        };
      }
      // parsed.kind === "ok" — use parsed.name/parsed.args directly to
      // avoid rebuilding the { name, args } object on every iteration.
      const tool: Tool | undefined = agent.tools[parsed.name];
      let observation: string;
      if (!tool) {
        observation = `error: tool '${parsed.name}' not found`;
      } else {
        try {
          observation = await tool.execute(parsed.args);
        } catch (e) {
          observation = `error: ${e instanceof Error ? e.message : String(e)}`;
        }
      }
      steps.push({
        step: i + 1,
        thought,
        action: { name: parsed.name, args: parsed.args },
        observation,
      });
      current = `${current}\nObservation: ${observation}`;
    }
    return { ok: false, output: "", steps, reason: "budget exceeded: maxSteps" };
  }
}
