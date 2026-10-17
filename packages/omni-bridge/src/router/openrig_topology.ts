export interface AgentTopologyNode {
  name: string;
  role: string;
  knight_binding: string;
  model: string;
  capabilities: string[];
  max_ram_mb: number;
}

export interface AgentTopology {
  team_name: string;
  lead_agent: string;
  agents: AgentTopologyNode[];
  delegation_rules: {
    from: string;
    to: string;
    trigger_task: string;
  }[];
}

export const CANONICAL_CAMELOT_TOPOLOGY: AgentTopology = {
  team_name: 'Camelot-Omni-Lattice',
  lead_agent: 'Merlin_Ω',
  agents: [
    {
      name: 'Merlin_Ω',
      role: 'Lead Architect & Cognitive Planner',
      knight_binding: 'MERLIN_Ω',
      model: 'gemini-3-pro',
      capabilities: ['planning', 'dag_synthesis', 'task_decomposition'],
      max_ram_mb: 1024,
    },
    {
      name: 'Sir_Boris',
      role: 'AST Code Architect & UX Conductor',
      knight_binding: 'SIR_BORIS',
      model: 'claude-3-7-sonnet',
      capabilities: ['ast_patching', 'refactoring', 'ui_ux'],
      max_ram_mb: 1024,
    },
    {
      name: 'Sir_Forge',
      role: 'Kinetic Implementation Specialist',
      knight_binding: 'SIR_FORGE',
      model: 'gemini-3.8-flash',
      capabilities: ['file_edits', 'builds', 'test_runs'],
      max_ram_mb: 512,
    },
    {
      name: 'Sir_Sentinel',
      role: 'Security, AgentArmor & Governance Guard',
      knight_binding: 'SIR_SENTINEL',
      model: 'gemini-3.8-flash',
      capabilities: ['waf_check', 'secret_audit', 'hitl_gate'],
      max_ram_mb: 256,
    },
  ],
  delegation_rules: [
    { from: 'Merlin_Ω', to: 'Sir_Boris', trigger_task: 'code_refactor' },
    { from: 'Sir_Boris', to: 'Sir_Forge', trigger_task: 'apply_patch' },
    { from: 'Sir_Forge', to: 'Sir_Sentinel', trigger_task: 'verify_build' },
  ],
};

export function parseTopology(topology: AgentTopology): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  if (!topology.team_name) errors.push('Missing team_name');
  if (!topology.lead_agent) errors.push('Missing lead_agent');

  const names = new Set(topology.agents.map((a) => a.name));
  if (!names.has(topology.lead_agent)) {
    errors.push(`Lead agent [${topology.lead_agent}] is not declared in agents roster`);
  }

  // RAM Governance Check: Total team allocation on local node must not exceed 4096 MB
  const totalAllocatedRam = topology.agents.reduce((acc, a) => acc + (a.max_ram_mb || 512), 0);
  if (totalAllocatedRam > 4096) {
    errors.push(
      `Total team RAM allocation (${totalAllocatedRam} MB) breaches Camelot 4 GB Node Ceiling`,
    );
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
