// tests/router/policy.test.ts
import { determineRoute } from '../../src/router/policy';
import { describe, it, expect } from 'vitest';

describe('OmniRoute Policy', () => {
    it('should route high-context tasks to Gemini', () => {
        const target = determineRoute({ contextSize: 150000, taskType: "analysis" });
        expect(target).toBe("OmniRoute/gemini");
    });
    it('should route kinetic code generation to Claude', () => {
        const target = determineRoute({ contextSize: 5000, taskType: "kinetic_code_generation" });
        expect(target).toBe("OmniRoute/anthropic");
    });
    it('should route stealth web foraging to proxy stream', () => {
        const target = determineRoute({ contextSize: 1000, taskType: "stealth_web_foraging" });
        expect(target).toBe("OmniRoute/proxy/stream");
    });
    it('should default to OpenAI for everything else', () => {
        const target = determineRoute({ contextSize: 500, taskType: "summarization" });
        expect(target).toBe("OmniRoute/openai");
    });
});
