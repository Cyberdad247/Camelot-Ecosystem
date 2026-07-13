// src/lib/agents/orchestrator.ts
//
// Phase 3 Agent orchestrator — ReAct loop with budget enforcement.
// Phase 4 followups: split `no_action` into `no_action` + `depth_mismatch`
// so the orchestrator can surface malformed LLM output (unclosed braces)
// as a hard failure rather than silently treating it as a final answer.
// Also bounds `current` prompt growth: after DIGEST_THRESHOLD observations,
// older ones are folded into a single digest line so long-running agents
// don't hit token limits.
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

// Uniform discriminated union — every parse result carries a `kind`
// discriminator so the orchestrator can switch on it exhaustively.
// The four cases:
//   - "no_action"      — no `Action: tool(` header (final answer)
//   - "ok"             — header matched and JSON body parsed
//   - "json_error"     — header matched but JSON body failed to parse
//   - "depth_mismatch" — header matched but braces didn't balance
//                        (malformed LLM output; cap snippet to keep
//                        parseError bounded)
export type ParseResult =
  | { kind: "no_action" }
  | { kind: "ok"; name: string; args: Record<string, unknown> }
  | { kind: "json_error"; error: string }
  | { kind: "depth_mismatch"; snippet: string };

// Thrown by withTimeout when a promise doesn't resolve within the
// allotted window. The orchestrator catches this and converts it to
// a proper AgentResult with ok: false so the route handler doesn't
// 500 on a hung LLM or tool.
export class TimeoutError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TimeoutError";
  }
}

const SNIPPET_MAX = 256;

export function parseAction(thought: string): ParseResult {
  const headerMatch = thought.match(/Action:\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(/);
  if (!headerMatch) return { kind: "no_action" };
  const name = headerMatch[1]!;
  const startIdx = (headerMatch.index ?? 0) + headerMatch[0].length;
  let depth = 1; // we're inside the opening `(`
  let inString = false;
  let escape = false;
  let i = startIdx;
  while (i < thought.length) {
    const c = thought[i];
    if (escape) {
      escape = false;
      i += 1;
      continue;
    }
    if (inString) {
      if (c === "\\") {
        escape = true;
      } else if (c === '"') {
        inString = false;
      }
      i += 1;
      continue;
    }
    if (c === '"') {
      inString = true;
      i += 1;
      continue;
    }
    if (c === "(" || c === "{") {
      depth += 1;
      i += 1;
      continue;
    }
    if (c === ")" || c === "}") {
      depth -= 1;
      if (depth === 0) break;
      i += 1;
      continue;
    }
    i += 1;
  }
  if (depth !== 0) {
    // Header matched but we ran out of input before the call closed.
    // Return the unfinished tail (capped) so operators can see what
    // the LLM produced without unbounded memory growth.
    const tail = thought.slice(startIdx);
    return {
      kind: "depth_mismatch",
      snippet: tail.length > SNIPPET_MAX ? tail.slice(0, SNIPPET_MAX) : tail,
    };
  }
  const jsonStr = thought.slice(startIdx, i);
  try {
    const args = JSON.parse(jsonStr) as Record<string, unknown>;
    return { kind: "ok", name, args };
  } catch (e) {
    return {
      kind: "json_error",
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

// Races a promise against a timer. If the timer wins, throws a
// TimeoutError. The underlying promise is NOT cancelled (JS has no
// general-purpose cancellation), but its result is discarded. The
// timer is always cleared in the finally block to prevent leaks.
async function withTimeout<T>(
  p: Promise<T>,
  ms: number,
  label: string,
): Promise<T> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<never>((_, reject) => {
    timer = setTimeout(
      () => reject(new TimeoutError(`timeout after ${ms}ms: ${label}`)),
      ms,
    );
  });
  try {
    return await Promise.race([p, timeout]);
  } finally {
    if (timer !== undefined) clearTimeout(timer);
  }
}

// After more than DIGEST_THRESHOLD observations, the prompt is rebuilt
// from the original input + a digest line + the latest observation only.
// Older observations are summarized away to keep `current` bounded as
// the agent's action count grows.
const DIGEST_THRESHOLD = 2;

function buildCurrent(input: string, observations: readonly string[]): string {
  if (observations.length <= DIGEST_THRESHOLD) {
    return observations.reduce(
      (acc, obs) => `${acc}\nObservation: ${obs}`,
      input,
    );
  }
  const digestCount = observations.length - 1;
  const latest = observations[observations.length - 1] ?? "";
  return `${input}\n[digest: ${digestCount} earlier observations summarized]\nObservation: ${latest}`;
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
    const observations: string[] = [];
    let current = input;

    for (let i = 0; i < maxSteps; i += 1) {
      if (Date.now() - startTime >= maxMs) {
        return {
          ok: false,
          output: "",
          steps,
          reason: "budget exceeded: maxMs",
        };
      }
      // Floor at 1ms (not 100ms) so a small `maxMs` is respected.
      // A 100ms floor would let a single call exceed the total budget
      // when `maxMs < 100`.
      const remainingMs = Math.max(1, maxMs - (Date.now() - startTime));
      let thought: string;
      try {
        thought = await withTimeout(
          this.llm.generateThinking(
            `[${agent.name} GOAL: ${agent.goal}] Input: ${current}\n` +
              `Available tools: ${Object.keys(agent.tools).join(", ")}`,
          ),
          remainingMs,
          "llm.generateThinking",
        );
      } catch (e) {
        // LLM call failed (timeout or other error). Hard-fail so the
        // caller gets a proper AgentResult with ok: false instead of
        // a rejected promise that would 500 the route handler.
        const reason = e instanceof TimeoutError
          ? `budget exceeded: timeout in llm.generateThinking after ${remainingMs}ms`
          : `llm error: ${e instanceof Error ? e.message : String(e)}`;
        return { ok: false, output: "", steps, reason };
      }
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
      if (parsed.kind === "depth_mismatch") {
        // Header matched but the call never closed (unbalanced braces).
        // Same hard-failure shape as json_error, but the parseError
        // carries the truncated unfinished tail for debugging.
        steps.push({
          step: i + 1,
          thought,
          action: null,
          observation: null,
          parseError: `depth_mismatch: ${parsed.snippet}`,
        });
        return {
          ok: false,
          output: thought,
          steps,
          reason: "action parse error: depth_mismatch",
        };
      }
      // parsed.kind === "ok" — use parsed.name/parsed.args directly to
      // avoid rebuilding the { name, args } object on every iteration.
      const tool: Tool | undefined = agent.tools[parsed.name];
      let observation: string;
      if (!tool) {
        observation = `error: tool '${parsed.name}' not found`;
      } else {
        const toolRemainingMs = Math.max(1, maxMs - (Date.now() - startTime));
        try {
          observation = await withTimeout(
            tool.execute(parsed.args),
            toolRemainingMs,
            `tool.${parsed.name}`,
          );
        } catch (e) {
          observation = `error: ${e instanceof TimeoutError
            ? `timeout after ${toolRemainingMs}ms`
            : e instanceof Error ? e.message : String(e)}`;
        }
      }
      steps.push({
        step: i + 1,
        thought,
        action: { name: parsed.name, args: parsed.args },
        observation,
      });
      observations.push(observation);
      current = buildCurrent(input, observations);
    }
    return { ok: false, output: "", steps, reason: "budget exceeded: maxSteps" };
  }
}
