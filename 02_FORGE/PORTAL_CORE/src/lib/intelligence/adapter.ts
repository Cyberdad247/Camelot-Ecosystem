// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
// THE INTERFACE (Our Law)
// We only code against this. We never import 'openai' in our UI components.
export interface IntelligenceAgent {
  generateThinking(prompt: string): Promise<string>;
  streamCode(prompt: string): AsyncGenerator<string>;
}

// ADAPTER 1: The Proprietary Route (Fast, Expensive)
// Placeholder for OpenAI SDK - explicitly avoiding direct import to demonstrate pattern
// In a real scenario, this would import OpenAI from 'openai';
export class OpenAISovereign implements IntelligenceAgent {
  private apiKey: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_OPENAI_KEY || '';
  }

  async generateThinking(prompt: string) {
    if (!this.apiKey) return 'Error: No OpenAI Key provided.';

    // Simulation of OpenAI Call
    /*
        const res = await this.client.chat.completions.create({
          model: "gpt-4o",
          messages: [{ role: "user", content: prompt }]
        });
        return res.choices[0].message.content || "";
        */
    return `[OPENAI_MOCK] Thinking about: ${prompt}`;
  }

  async *streamCode(prompt: string) {
    yield '// OpenAI Stream Started...';
    yield `// Processing: ${prompt}`;
    yield '// Done.';
  }
}

// ADAPTER 2: The Sovereign Route (Free, Local, Private)
// We switch to this if OpenAI goes down or changes pricing.
export class OllamaSovereign implements IntelligenceAgent {
  private endpoint = 'http://localhost:11434/api/generate';

  async generateThinking(prompt: string) {
    try {
      const res = await fetch(this.endpoint, {
        method: 'POST',
        body: JSON.stringify({ model: 'llama3', prompt, stream: false }),
      });
      const json = await res.json();
      return json.response;
    } catch (e) {
      return 'Error: Local Ollama unreachable.';
    }
  }

  async *streamCode(prompt: string) {
    // Basic simulation of streaming for adapter compliance
    const response = await this.generateThinking(prompt);
    yield response;
  }
}

// THE FACTORY
export const getAgent = (): IntelligenceAgent => {
  // Config-driven switch. NO CODE CHANGE REQUIRED to switch providers.
  return import.meta.env.VITE_USE_LOCAL_AI === 'true'
    ? new OllamaSovereign()
    : new OpenAISovereign();
};
