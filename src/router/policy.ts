// src/router/policy.ts
export interface RoutingContext {
    contextSize: number;
    taskType: string;
}

export function determineRoute(ctx: RoutingContext): string {
    if (ctx.contextSize > 100000) return "OmniRoute/gemini";
    if (ctx.taskType === "kinetic_code_generation") return "OmniRoute/anthropic";
    if (ctx.taskType === "stealth_web_foraging") return "OmniRoute/proxy/stream";
    return "OmniRoute/openai"; // Cost-optimized default
}
