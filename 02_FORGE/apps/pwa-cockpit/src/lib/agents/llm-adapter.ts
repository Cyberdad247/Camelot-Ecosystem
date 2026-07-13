// src/lib/agents/llm-adapter.ts
//
// Phase 5: env-configurable LLM adapter factory. Reads `LLM_PROVIDER`
// from the environment and returns the appropriate IntelligenceAdapter
// implementation. Defaults to "stub" for safe local development.
//
// Edge-runtime safe: SDKs are lazy-imported inside `generateThinking`
// via `await import(...)`. In Next.js edge runtime, dynamic imports
// create separate chunks, so the main handler bundle is smaller when
// `LLM_PROVIDER=stub`, but the SDKs are still bundled (in lazy chunks)
// for the other providers — they ship, just on-demand. All three
// providers (Gemini, OpenAI, Anthropic) use `fetch` under the hood
// and work on the edge runtime.
//
// API keys are read at call time (not at import time) so tests can
// mutate `process.env` freely. Note: in Next.js edge runtime, `process.env`
// values are statically replaced at build time, so the provider is
// effectively fixed at deploy time (swap via rebuild, not at runtime).
// The factory still works in edge — it just dispatches based on the
// build-time env value. Each provider validates its key before
// constructing the SDK client and throws a clear "missing <KEY>" error
// if absent.

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

export function createLLMAdapter(): IntelligenceAdapter {
  const provider = (process.env.LLM_PROVIDER ?? "stub") as LLMProvider;
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
