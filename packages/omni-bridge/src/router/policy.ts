export interface RoutingContext {
  contextSize: number;
  taskType: string;
  containsSecrets?: boolean;
  priority?: 'high' | 'normal' | 'background';
}

export interface KnightResolution {
  knightId: string;
  engineTarget: string;
  reason: string;
}

export function determineRoute(ctx: RoutingContext): string {
  // Privacy & air-gap gate: Sir Ghost
  if (ctx.containsSecrets || ctx.taskType === 'secret_scan' || ctx.taskType === 'privacy_audit') {
    return 'OmniRoute/sir_ghost';
  }

  // Macroscopic context / large document analysis: Gemini 3.8 Flash (Sir Helios / Merlin)
  if (ctx.contextSize > 100000) {
    return 'OmniRoute/gemini';
  }

  // Kinetic code generation & AST refactoring: Claude Code (Sir Boris / Sir Forge)
  if (ctx.taskType === 'kinetic_code_generation' || ctx.taskType === 'ast_patch') {
    return 'OmniRoute/anthropic';
  }

  // Stealth web foraging & swarm research: BASHR (Lady Apis)
  if (ctx.taskType === 'stealth_web_foraging' || ctx.taskType === 'web_scrape') {
    return 'OmniRoute/proxy/stream';
  }

  // Sovereign default: Gemini LATTICE_SIGNAL core (cost-effective high-speed apex)
  return 'OmniRoute/gemini';
}

export function resolveKnightEngine(ctx: RoutingContext): KnightResolution {
  const route = determineRoute(ctx);

  switch (route) {
    case 'OmniRoute/sir_ghost':
      return {
        knightId: 'SIR_GHOST',
        engineTarget: 'ollama/local',
        reason: 'Air-gapped local privacy perimeter',
      };
    case 'OmniRoute/gemini':
      return {
        knightId: 'SIR_HELIOS',
        engineTarget: 'gemini-3.8-flash',
        reason:
          ctx.contextSize > 100000
            ? 'High-context window (>100k tokens)'
            : 'LATTICE_SIGNAL sovereign default',
      };
    case 'OmniRoute/anthropic':
      return {
        knightId: 'SIR_BORIS',
        engineTarget: 'claude-3-7-sonnet',
        reason: 'Kinetic AST code generation specialization',
      };
    case 'OmniRoute/proxy/stream':
      return {
        knightId: 'LADY_APIS',
        engineTarget: 'nullclaw/bashr',
        reason: 'Autonomous stealth web foraging engine',
      };
    default:
      return {
        knightId: 'MERLIN_Ω',
        engineTarget: 'gemini-3-pro',
        reason: 'Deep cognitive DAG synthesis fallback',
      };
  }
}
