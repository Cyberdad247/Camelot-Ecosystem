import { describe, expect, it } from 'vitest';
import { CANONICAL_CAMELOT_TOPOLOGY, parseTopology } from './openrig_topology';

describe('OpenRig Topology Parser', () => {
  it('should validate canonical Camelot multi-agent topology', () => {
    const result = parseTopology(CANONICAL_CAMELOT_TOPOLOGY);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('should flag memory ceiling breaches (>4096 MB)', () => {
    const bloatedTopology = {
      ...CANONICAL_CAMELOT_TOPOLOGY,
      agents: [
        {
          name: 'Merlin_Ω',
          role: 'Lead',
          knight_binding: 'MERLIN_Ω',
          model: 'gemini',
          capabilities: [],
          max_ram_mb: 3000,
        },
        {
          name: 'Sir_Boris',
          role: 'Architect',
          knight_binding: 'SIR_BORIS',
          model: 'claude',
          capabilities: [],
          max_ram_mb: 2000,
        },
      ],
    };

    const result = parseTopology(bloatedTopology);
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('breaches Camelot 4 GB Node Ceiling');
  });
});
