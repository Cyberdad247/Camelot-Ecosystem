// src/router/policy.ts

export interface RoutingContext {
  contextSize: number;
  taskType: string;
  // BitRouter & Cost parameters
  virtualKey?: string;
  spendCap?: number;
  currentSpend?: number;
  loopCount?: number;
  maxLoops?: number;
  // agency-agents & Persona
  persona?: string;
  // Custom providers / model overrides (simonw/llm)
  providerOverride?: string;
  // Lane / Intent text for OmniRoute lane-signal policies
  intentText?: string;
}

export interface RoutingDecision {
  route: string; // Core resolved target (e.g. "OmniRoute/gemini")
  engine: string; // Model engine family (e.g. "gemini", "anthropic", "openai", "council")
  costAllowed: boolean; // Cost check result
  rejectionReason?: string; // Reason for route rejection (e.g. loop guard or spend cap exceeded)
  mcpGateway?: {
    allowedTools: string[];
    policy: 'strict' | 'relaxed';
  };
  councilPipeline?: {
    // karpathy/llm-council deliberation flow
    councillors: string[];
    chairman: string;
    critiqueRequired: boolean;
  };
  systemPrompt?: string; // agency-agents persona injection
}

// Predefined agent personas (assimilated from agency-agents & Camelot Knights)
export const PERSONA_PROMPTS: Record<string, string> = {
  architect:
    'You are SIR_BORIS, the system architect. Design for scalability, DRY principles, and loose coupling.',
  planner:
    'You are SIR_ALEX, the campaign planner. Establish clear execution tasks and dependencies.',
  critic:
    'You are SIR_SENTINEL, the security critic. Scan for vulnerabilities, data leaks, and invalid inputs.',
  coder: 'You are SIR_FORGE, the execution coder. Write high-performance, strictly typed code.',
};

export function determineRoute(ctx: RoutingContext): string {
  // 1. Provider / Model overrides (simonw/llm)
  if (ctx.providerOverride) {
    return `OmniRoute/custom/${ctx.providerOverride}`;
  }

  // 2. Select optimal framework lane based on intent keywords (Item 1a & 1b)
  if (ctx.intentText) {
    const needle = ctx.intentText.toLowerCase();

    // Item 1a: Route low-latency, rapid boilerplate scaffolding through OmniRoute (:20128) directly to SIR_CODEX
    const scaffoldKeywords = [
      'scaffold',
      'boilerplate',
      'prototype',
      'rapid',
      'velocity',
      'codex',
      'fast_gen',
      'iteration',
    ];
    if (scaffoldKeywords.some((kw) => needle.includes(kw))) {
      return 'OmniRoute/omni_route_codex';
    }

    // Item 1b: Route massive reasoning/deep-context tasks through CLIProxyAPI (:8080) for heavy Cloud Brain computing
    const reasoningKeywords = [
      'deep-context',
      'reasoning',
      'cloud_brain',
      'merlin',
      '1m-context',
      'context_window',
    ];
    if (reasoningKeywords.some((kw) => needle.includes(kw))) {
      return 'OmniRoute/cliproxy_heavy_reasoning';
    }
  }

  // 3. Default routing policy heuristic
  if (ctx.contextSize > 100000) return 'OmniRoute/gemini';
  if (ctx.taskType === 'kinetic_code_generation') return 'OmniRoute/anthropic';
  if (ctx.taskType === 'stealth_web_foraging') return 'OmniRoute/proxy/stream';
  return 'OmniRoute/openai'; // Cost-optimized default
}

export function resolveRoute(ctx: RoutingContext): RoutingDecision {
  // 1. BitRouter Virtual Key Check
  if (ctx.virtualKey && !ctx.virtualKey.startsWith('brvk_')) {
    return {
      route: 'OmniRoute/rejected',
      engine: 'rejected',
      costAllowed: false,
      rejectionReason: "Invalid virtual key format. Keys must be prefixed with 'brvk_'.",
    };
  }

  // 2. BitRouter Cost Guardrail
  if (
    ctx.spendCap !== undefined &&
    ctx.currentSpend !== undefined &&
    ctx.currentSpend >= ctx.spendCap
  ) {
    return {
      route: 'OmniRoute/rejected',
      engine: 'rejected',
      costAllowed: false,
      rejectionReason:
        'Spend cap exceeded. Current spend: ' + ctx.currentSpend + ', Cap: ' + ctx.spendCap,
    };
  }

  // 3. BitRouter Loop Guard
  if (ctx.maxLoops !== undefined && ctx.loopCount !== undefined && ctx.loopCount >= ctx.maxLoops) {
    return {
      route: 'OmniRoute/rejected',
      engine: 'rejected',
      costAllowed: false,
      rejectionReason:
        'Loop guard triggered: runaway loop detected at ' + ctx.loopCount + ' iterations.',
    };
  }

  // 4. karpathy/llm-council Deliberative Consensus Routing
  if (ctx.taskType === 'deliberative_consensus' || ctx.taskType === 'llm_council') {
    const councillors = ['OmniRoute/openai', 'OmniRoute/anthropic'];
    const chairman = ctx.contextSize > 100000 ? 'OmniRoute/gemini' : 'OmniRoute/anthropic';
    return {
      route: 'OmniRoute/council',
      engine: 'council',
      costAllowed: true,
      councilPipeline: {
        councillors,
        chairman,
        critiqueRequired: true,
      },
    };
  }

  // 5. agency-agents Persona Injection
  let systemPrompt: string | undefined;
  if (ctx.persona && PERSONA_PROMPTS[ctx.persona]) {
    systemPrompt = PERSONA_PROMPTS[ctx.persona];
  }

  // 6. Standard Route Resolution
  const resolvedRoute = determineRoute(ctx);
  let engine = 'openai';
  if (resolvedRoute.includes('gemini')) engine = 'gemini';
  else if (resolvedRoute.includes('anthropic')) engine = 'anthropic';
  else if (resolvedRoute.includes('cliproxy')) engine = 'cliproxy';
  else if (resolvedRoute.includes('proxy')) engine = 'proxy';
  else if (resolvedRoute.includes('codex')) engine = 'codex';

  return {
    route: resolvedRoute,
    engine,
    costAllowed: true,
    systemPrompt,
  };
}
