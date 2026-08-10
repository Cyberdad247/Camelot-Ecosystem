// src/lib/agents/llm-adapter.ts
//
// Phase 5: env-configurable LLM adapter factory. Reads `LLM_PROVIDER`
// from the environment and returns the appropriate IntelligenceAdapter
// implementation. Defaults to "stub" for safe local development.
//
// Phase 8 hardening:
//   - Stub-in-prod guard: createLLMAdapter() throws a loud, actionable
//     error when NODE_ENV=production AND the provider is stub (or
//     unset, which defaults to stub). Prevents the footgun where a
//     misconfigured Vercel env returns deterministic fake answers to
//     real users. In edge runtime, process.env is statically replaced
//     at build time, so this check fires on first adapter use in prod.
//   - RetryAdapterWrapper + withRetry() exported as separate helpers
//     so callers can compose. The factory still returns the raw
//     adapter (preserving the existing instanceof checks in tests).
//     The route handler in src/app/api/agent/run/route.ts composes
//     `withRetry(createLLMAdapter())`. Retries cover 429/5xx and
//     network errors; 4xx (auth, bad request) is not retried.
//
// Edge-runtime safe: SDKs are lazy-imported inside `generateThinking`
// via `await import(...)`. All three providers (Gemini, OpenAI,
// Anthropic) use `fetch` under the hood and work on the edge runtime.
//
// API keys are read at call time (not at import time) so tests can
// mutate `process.env` freely. Note: in Next.js edge runtime,
// `process.env` values are statically replaced at build time, so the
// provider is effectively fixed at deploy time (swap via rebuild, not
// at runtime).

import type { IntelligenceAdapter } from "./types";

const STUB_FINAL_ANSWER =
  "Final deterministic answer from StubIntelligenceAdapter (replace in prod via LLM_PROVIDER=gemini|openai|anthropic).";

export class StubAdapter implements IntelligenceAdapter {
  async generateThinking(_prompt: string): Promise<string> {
    return STUB_FINAL_ANSWER;
  }
}

export class GeminiAdapter implements IntelligenceAdapter {
  async generateThinking(prompt: string): Promise<string> {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) throw new Error("missing GEMINI_API_KEY");

    // Lazy import keeps the edge bundle small when LLM_PROVIDER=stub.
    const { GoogleGenerativeAI } = await import("@google/generative-ai");
    const genAI = new GoogleGenerativeAI(apiKey);
    const modelName = process.env.GEMINI_MODEL ?? "gemini-2.0-flash";
    const model = genAI.getGenerativeModel({ model: modelName });
    const result = await model.generateContent(prompt);
    return result.response.text();
  }
}

export class OpenAIAdapter implements IntelligenceAdapter {
  async generateThinking(prompt: string): Promise<string> {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error("missing OPENAI_API_KEY");

    const { OpenAI } = await import("openai");
    const openai = new OpenAI({ apiKey, fetch: globalThis.fetch });
    const modelName = process.env.OPENAI_MODEL ?? "gpt-4o-mini";
    const response = await openai.chat.completions.create({
      model: modelName,
      messages: [{ role: "user", content: prompt }],
    });
    return response.choices[0]?.message?.content ?? "";
  }
}

export class AnthropicAdapter implements IntelligenceAdapter {
  async generateThinking(prompt: string): Promise<string> {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error("missing ANTHROPIC_API_KEY");

    const { Anthropic } = await import("@anthropic-ai/sdk");
    const anthropic = new Anthropic({ apiKey, fetch: globalThis.fetch });
    const modelName = process.env.ANTHROPIC_MODEL ?? "claude-3-5-haiku-latest";
    const response = await anthropic.messages.create({
      model: modelName,
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }],
    });
    const block = response.content[0];
    return block && block.type === "text" ? block.text : "";
  }
}

export type LLMProvider = "stub" | "gemini" | "openai" | "anthropic";

// Phase 8: retry/backoff wrapper. Exported as a separate class so
// callers can compose it via withRetry(). The factory does NOT wrap
// the returned adapter — existing tests rely on instanceof checks
// against the concrete adapter classes, and the stub adapter has no
// network I/O so retrying it is meaningless.
export type RetryOptions = {
  maxAttempts?: number;
  baseDelayMs?: number;
};

export class RetryAdapterWrapper implements IntelligenceAdapter {
  private readonly maxAttempts: number;
  private readonly baseDelayMs: number;
  constructor(
    private inner: IntelligenceAdapter,
    options: RetryOptions = {},
  ) {
    this.maxAttempts = options.maxAttempts ?? 3;
    this.baseDelayMs = options.baseDelayMs ?? 500;
  }
  async generateThinking(prompt: string): Promise<string> {
    let lastError: unknown;
    for (let attempt = 0; attempt < this.maxAttempts; attempt++) {
      try {
        return await this.inner.generateThinking(prompt);
      } catch (e) {
        lastError = e;
        if (!isRetryable(e) || attempt === this.maxAttempts - 1) {
          throw e;
        }
        // Exponential backoff: baseDelayMs * 2^attempt (500ms, 1000ms, 2000ms).
        const backoff = this.baseDelayMs * Math.pow(2, attempt);
        await new Promise((r) => setTimeout(r, backoff));
      }
    }
    // Unreachable, but satisfies the type system.
    throw lastError;
  }
}

export function withRetry(
  adapter: IntelligenceAdapter,
  options?: RetryOptions,
): IntelligenceAdapter {
  return new RetryAdapterWrapper(adapter, options);
}

// Determine whether an error warrants a retry. Retry on:
//   - HTTP 429 (rate limit)
//   - HTTP 5xx (server errors)
//   - Network errors (TypeError from fetch, FetchError, AbortError)
// Do NOT retry on 4xx other than 429 (auth, bad request) — those
// represent caller mistakes, not transient failures.
export function isRetryable(e: unknown): boolean {
  if (typeof e !== "object" || e === null) return false;
  const err = e as { status?: number; name?: string };
  if (typeof err.status === "number") {
    if (err.status === 429) return true;
    if (err.status >= 500 && err.status < 600) return true;
    return false;
  }
  const name = err.name ?? "";
  if (name === "TypeError" || name === "FetchError" || name === "AbortError") {
    return true;
  }
  return false;
}

export function createLLMAdapter(): IntelligenceAdapter {
  const provider = (process.env.LLM_PROVIDER ?? "stub") as LLMProvider;

  // Phase 8: stub-in-prod guard. Refuse to silently serve deterministic
  // fake answers in production. In edge runtime, NODE_ENV is statically
  // replaced at build time, so this check fires on first adapter use
  // in prod (Vercel sets NODE_ENV=production on deploy).
  if (process.env.NODE_ENV === "production" && provider === "stub") {
    throw new Error(
      "Refusing to start: LLM_PROVIDER is unset or 'stub' in production. " +
        "Set LLM_PROVIDER=gemini|openai|anthropic and provide the matching API key.",
    );
  }

  switch (provider) {
    case "stub":
      return new StubAdapter();
    case "gemini":
      return new GeminiAdapter();
    case "openai":
      return new OpenAIAdapter();
    case "anthropic":
      return new AnthropicAdapter();
    default:
      throw new Error(`unknown LLM_PROVIDER: ${String(provider)}`);
  }
}
