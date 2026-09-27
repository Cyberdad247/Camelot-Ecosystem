import { create } from 'zustand';
import { atom } from 'jotai';
import { z } from 'zod';

export const CaptainEnum = z.enum([
  'Sir_Boris',
  'Sir_Codex',
  'Sir_Helio',
  'Sir_Octavian',
  'Merlin_Ω',
  'Anya_Ω'
]);

export type CaptainType = z.infer<typeof CaptainEnum>;

export const AgentExecutionSchema = z.object({
  taskId: z.string(),
  taskName: z.string(),
  captain: CaptainEnum,
  payload: z.record(z.string(), z.unknown()),
  semanticDrift: z.number().min(0).max(1),
  memoryFootprintMB: z.number().max(7372.8), // 90% of 8192 MB (Strict 7.2GB Scarcity Ceiling)
  status: z.enum(['IDLE', 'ROUTING', 'PROCESSING', 'VERIFIED', 'HALTED_IRON_GATE', 'COMPLETED']),
  initiatedAt: z.string(),
  completedAt: z.string().optional(),
  z3ProofVerified: z.boolean().default(true),
  dagStage: z.enum(['Triage', 'Planning', 'Execution', 'ShadowVM', 'IronGateCheckpoint'])
});

export type AgentExecutionState = z.infer<typeof AgentExecutionSchema>;

export interface MasterAgentStore {
  activeSessions: Map<string, AgentExecutionState>;
  systemMemoryUsageMB: number;
  maxMemoryCeilingMB: number;
  totalSemanticDrift: number;
  isIronGateTripped: boolean;
  ironGateTripReason: string | null;
  registerExecution: (task: AgentExecutionState) => void;
  updateTelemetry: (taskId: string, memoryMB: number, drift: number) => void;
  tripIronGate: (taskId: string, reason?: string) => void;
  resetIronGate: () => void;
  clearSession: (taskId: string) => void;
  executeDAGTask: (captain: CaptainType, taskName: string, payload?: Record<string, unknown>) => string;
}

export const useMasterAgentStore = create<MasterAgentStore>((set, get) => ({
  activeSessions: new Map<string, AgentExecutionState>([
    [
      'task-init-01',
      {
        taskId: 'task-init-01',
        taskName: 'Ouroboros 1.58b State Space Model Kernel Init',
        captain: 'Sir_Octavian',
        payload: { kernel: 'mamba-3-ternary', targetMem: '4.2GB', zeroClaw: true },
        semanticDrift: 0.002,
        memoryFootprintMB: 4280.0,
        status: 'VERIFIED',
        initiatedAt: new Date(Date.now() - 60000).toISOString(),
        z3ProofVerified: true,
        dagStage: 'Execution'
      }
    ],
    [
      'task-init-02',
      {
        taskId: 'task-init-02',
        taskName: 'AST Cartridge Parser & WASM32 Bounds Check',
        captain: 'Sir_Codex',
        payload: { parser: 'camelot-ast-engine', sandbox: 'wasm32-wasip1' },
        semanticDrift: 0.001,
        memoryFootprintMB: 184.2,
        status: 'VERIFIED',
        initiatedAt: new Date(Date.now() - 40000).toISOString(),
        z3ProofVerified: true,
        dagStage: 'ShadowVM'
      }
    ],
    [
      'task-init-03',
      {
        taskId: 'task-init-03',
        taskName: '12-Column Spatial Grid & Glassmorphic Viewport',
        captain: 'Sir_Boris',
        payload: { layout: '12-col-grid', dohertyTarget: '18.4ms' },
        semanticDrift: 0.000,
        memoryFootprintMB: 92.5,
        status: 'PROCESSING',
        initiatedAt: new Date(Date.now() - 15000).toISOString(),
        z3ProofVerified: true,
        dagStage: 'Execution'
      }
    ]
  ]),
  systemMemoryUsageMB: 4556.7,
  maxMemoryCeilingMB: 7372.8,
  totalSemanticDrift: 0.0015,
  isIronGateTripped: false,
  ironGateTripReason: null,

  registerExecution: (task) => {
    const validated = AgentExecutionSchema.parse(task);
    set((state) => {
      const next = new Map(state.activeSessions);
      next.set(validated.taskId, validated);
      return { activeSessions: next };
    });
  },

  updateTelemetry: (taskId, memoryMB, drift) => {
    if (memoryMB > 7372.8) {
      console.error(`[CRITICAL_RAM_OVERFLOW]: Memory usage ${memoryMB}MB exceeded 90% threshold (7.2GB)!`);
      get().tripIronGate(taskId, `CRITICAL_RAM_OVERFLOW: ${memoryMB.toFixed(1)}MB > 7372.8MB Ceiling`);
      return;
    }
    if (drift >= 0.007) {
      console.warn(`[DRIFT_VIOLATION]: Semantic drift ${(drift * 100).toFixed(3)}% exceeded 0.7% allowable threshold!`);
      get().tripIronGate(taskId, `DRIFT_CEILING_EXCEEDED: ${(drift * 100).toFixed(3)}% >= 0.700%`);
      return;
    }

    set((state) => {
      const current = state.activeSessions.get(taskId);
      if (!current) return state;
      const updated: AgentExecutionState = {
        ...current,
        memoryFootprintMB: memoryMB,
        semanticDrift: drift
      };
      const next = new Map(state.activeSessions);
      next.set(taskId, updated);

      let totalMem = 0;
      let totalDrift = 0;
      next.forEach((s) => {
        totalMem += s.memoryFootprintMB;
        totalDrift = Math.max(totalDrift, s.semanticDrift);
      });

      return {
        activeSessions: next,
        systemMemoryUsageMB: Math.min(8192, totalMem),
        totalSemanticDrift: totalDrift
      };
    });
  },

  tripIronGate: (taskId, reason) => {
    set((state) => {
      const current = state.activeSessions.get(taskId);
      const next = new Map(state.activeSessions);
      if (current) {
        next.set(taskId, { ...current, status: 'HALTED_IRON_GATE' });
      }
      return {
        activeSessions: next,
        isIronGateTripped: true,
        ironGateTripReason: reason || `Iron Gate tripped by Task ${taskId}`
      };
    });
  },

  resetIronGate: () => {
    set({
      isIronGateTripped: false,
      ironGateTripReason: null
    });
  },

  clearSession: (taskId) => {
    set((state) => {
      const next = new Map(state.activeSessions);
      next.delete(taskId);
      return { activeSessions: next };
    });
  },

  executeDAGTask: (captain, taskName, payload = {}) => {
    const taskId = `task-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`;
    const newTask: AgentExecutionState = {
      taskId,
      taskName,
      captain,
      payload,
      semanticDrift: +(Math.random() * 0.003).toFixed(4),
      memoryFootprintMB: +(50 + Math.random() * 120).toFixed(1),
      status: 'ROUTING',
      initiatedAt: new Date().toISOString(),
      z3ProofVerified: true,
      dagStage: 'Triage'
    };

    get().registerExecution(newTask);

    // Simulate DAG transition
    setTimeout(() => {
      set((state) => {
        const item = state.activeSessions.get(taskId);
        if (!item) return state;
        const next = new Map(state.activeSessions);
        next.set(taskId, { ...item, status: 'PROCESSING', dagStage: 'Planning' });
        return { activeSessions: next };
      });
    }, 400);

    setTimeout(() => {
      set((state) => {
        const item = state.activeSessions.get(taskId);
        if (!item) return state;
        const next = new Map(state.activeSessions);
        next.set(taskId, { ...item, status: 'VERIFIED', dagStage: 'ShadowVM' });
        return { activeSessions: next };
      });
    }, 900);

    setTimeout(() => {
      set((state) => {
        const item = state.activeSessions.get(taskId);
        if (!item) return state;
        const next = new Map(state.activeSessions);
        next.set(taskId, { ...item, status: 'COMPLETED', dagStage: 'IronGateCheckpoint', completedAt: new Date().toISOString() });
        return { activeSessions: next };
      });
    }, 1600);

    return taskId;
  }
}));

// Jotai Atomic States for Micro-UI Nodes
export const activeAudioGainAtom = atom<number>(0.85);
export const audio3DCoordinateAtom = atom<{ x: number; y: number; z: number }>({ x: 2.4, y: 1.8, z: -1.2 });
export const agentTerminalBufferAtom = atom<string[]>([
  '[AEGIS_SHIELD]: Ingress layer 7 active :: Zero-Trust Token Validated',
  '[OUROBOROS_SSM]: Ternary quantized 1.58b engine anchored at 4.2GB RAM',
  '[MERLIN_DAG]: 10-Repository vector unification compiled without conflict'
]);
export const eTuneDriftMetricAtom = atom<number>(0.0015);
export const selectedCaptainAtom = atom<CaptainType>('Sir_Boris');
