// SPDX-License-Identifier: MIT

// tests/router/policy.test.ts
import { determineRoute, resolveRoute, PERSONA_PROMPTS } from '../../src/router/policy';
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

describe('Assimilated Protocols Policy Routing (resolveRoute)', () => {
    it('should allow valid virtual keys starting with brvk_', () => {
        const target = resolveRoute({ contextSize: 500, taskType: "summarization", virtualKey: "brvk_secret123" });
        expect(target.costAllowed).toBe(true);
        expect(target.route).toBe("OmniRoute/openai");
    });

    it('should reject invalid virtual keys not starting with brvk_', () => {
        const target = resolveRoute({ contextSize: 500, taskType: "summarization", virtualKey: "invalid_key" });
        expect(target.costAllowed).toBe(false);
        expect(target.route).toBe("OmniRoute/rejected");
        expect(target.rejectionReason).toContain("Invalid virtual key format");
    });

    it('should reject when current spend meets or exceeds spend cap', () => {
        const target = resolveRoute({
            contextSize: 500,
            taskType: "summarization",
            spendCap: 10.0,
            currentSpend: 10.5
        });
        expect(target.costAllowed).toBe(false);
        expect(target.route).toBe("OmniRoute/rejected");
        expect(target.rejectionReason).toContain("Spend cap exceeded");
    });

    it('should reject when loop count meets or exceeds max loops', () => {
        const target = resolveRoute({
            contextSize: 500,
            taskType: "summarization",
            loopCount: 5,
            maxLoops: 5
        });
        expect(target.costAllowed).toBe(false);
        expect(target.route).toBe("OmniRoute/rejected");
        expect(target.rejectionReason).toContain("Loop guard triggered");
    });

    it('should route deliberative consensus / llm council tasks to council pipeline', () => {
        const target = resolveRoute({
            contextSize: 500,
            taskType: "deliberative_consensus"
        });
        expect(target.route).toBe("OmniRoute/council");
        expect(target.engine).toBe("council");
        expect(target.councilPipeline).toBeDefined();
        expect(target.councilPipeline?.councillors).toContain("OmniRoute/openai");
        expect(target.councilPipeline?.councillors).toContain("OmniRoute/anthropic");
    });

    it('should inject correct system prompt persona from agency-agents presets', () => {
        const target = resolveRoute({
            contextSize: 500,
            taskType: "summarization",
            persona: "architect"
        });
        expect(target.systemPrompt).toBe(PERSONA_PROMPTS.architect);
    });

    it('should apply provider overrides from simonw/llm client setup', () => {
        const target = resolveRoute({
            contextSize: 500,
            taskType: "summarization",
            providerOverride: "github-copilot/gpt-4o"
        });
        expect(target.route).toBe("OmniRoute/custom/github-copilot/gpt-4o");
    });

    it('should route scaffold keywords to omni_route_codex', () => {
        const target = resolveRoute({
            contextSize: 1000,
            taskType: "scaffolding",
            intentText: "please scaffold a rapid prototype for our new velocity model"
        });
        expect(target.route).toBe("OmniRoute/omni_route_codex");
        expect(target.engine).toBe("codex");
    });

    it('should route reasoning keywords to cliproxy_heavy_reasoning', () => {
        const target = resolveRoute({
            contextSize: 5000,
            taskType: "reasoning_task",
            intentText: "we need deep-context reasoning via the cloud_brain"
        });
        expect(target.route).toBe("OmniRoute/cliproxy_heavy_reasoning");
        expect(target.engine).toBe("cliproxy");
    });
});
