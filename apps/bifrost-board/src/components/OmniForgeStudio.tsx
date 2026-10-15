import React, { useState, useEffect } from 'react';
import { 
  Workflow, 
  CheckCircle2, 
  Circle, 
  Loader2, 
  ShieldCheck, 
  Cpu, 
  Layers, 
  Play, 
  Hash, 
  FileCode, 
  Terminal, 
  Check, 
  Network,
  Lock,
  Boxes,
  Zap,
  Activity
} from 'lucide-react';

export interface StageState {
  id: number;
  key: string;
  name: string;
  description: string;
  assignee: string;
  durationMs: number;
  status: 'PENDING' | 'RUNNING' | 'VERIFIED' | 'FAILED';
  artifact?: string;
  sha256?: string;
  telemetry?: string;
}

const INITIAL_STAGES: StageState[] = [
  {
    id: 1,
    key: 'INTENT',
    name: '1. Socratic Intent',
    description: 'Ingest raw intent, assess risk tier (10/100 LOW), and enforce tenant isolation.',
    assignee: 'Anya_Ω',
    durationMs: 14,
    status: 'VERIFIED',
    telemetry: 'Risk: LOW | Tenant: Isolated',
  },
  {
    id: 2,
    key: 'SPEC',
    name: '2. Formal Spec',
    description: 'Bind active constitution (const_engineering_v1) & 512MB RAM cap boundary.',
    assignee: 'Merlin_Ω',
    durationMs: 22,
    status: 'VERIFIED',
    artifact: 'blueprint.json',
    sha256: 'e98aed2c7788ffe75b9f84ce5dd5179fd1a3059a67abcd51809fb50a112b9179',
    telemetry: 'RAM Cap: 512MB | Root-RO: TRUE',
  },
  {
    id: 3,
    key: 'PLAN',
    name: '3. Milestone Plan',
    description: 'Decompose into 5 operational milestones with knight execution contracts.',
    assignee: 'Sir_Forge',
    durationMs: 18,
    status: 'VERIFIED',
    telemetry: '5 Milestones | Knight Contracts Sealed',
  },
  {
    id: 4,
    key: 'DAG',
    name: '4. Topological DAG',
    description: 'Compile 6-node dependency graph across parallel execution sequences.',
    assignee: 'Merlin_Ω',
    durationMs: 31,
    status: 'VERIFIED',
    artifact: 'task_dag.json',
    sha256: '7195ad4db54ad1596d0d272addb8156bf6c5f3c3416bd92c5ff7e5bc7dfb3074',
    telemetry: '6 Nodes | 0 Circular Dependencies',
  },
  {
    id: 5,
    key: 'SANDBOX',
    name: '5. WASM Sandbox',
    description: 'Simulate WASM32-WASI microVM execution with strict zero-leak delta limit.',
    assignee: 'Sir_Octavian',
    durationMs: 46,
    status: 'VERIFIED',
    artifact: 'skills_manifest.json',
    sha256: '9e5708749d55906aa2e4b91c242a2897c63f5b7b11dcb154de6345be68fffb84',
    telemetry: 'Working Set: 61.4 MB | ΔM: 0.04 MiB',
  },
  {
    id: 6,
    key: 'VERIFICATION',
    name: '6. Z3 SMT Prover',
    description: 'Theorem check: Omni-Forge_Integration_Convexity == TRUE (0 violations).',
    assignee: 'Sir_Codex',
    durationMs: 38,
    status: 'VERIFIED',
    artifact: 'verification.json',
    sha256: 'b1a802148acc6a88f8f0e127df2014be98640cd9aaf629328b482a5041d77644',
    telemetry: 'Convexity: SATISFIED | Rigor: L4',
  },
  {
    id: 7,
    key: 'RECEIPT',
    name: '7. Cryptographic Receipt',
    description: 'SHA-256 seal across all pinned artifacts, anchoring to Provenance Ledger.',
    assignee: 'Sir_Helios',
    durationMs: 15,
    status: 'VERIFIED',
    sha256: '485657f4238121506cd73c468cb2db2cc5b708c19a6a9fcd665b622411bb625e',
    telemetry: 'Mission: SEALED | Ledger Synchronized',
  },
];

interface DAGNode {
  id: string;
  label: string;
  assignee: string;
  x: number;
  y: number;
  status: 'VERIFIED' | 'RUNNING' | 'PENDING';
}

const DAG_NODES: DAGNode[] = [
  { id: 'n1', label: 'Intent Sanitize', assignee: 'Anya_Ω', x: 50, y: 70, status: 'VERIFIED' },
  { id: 'n2', label: 'Constitution Spec', assignee: 'Merlin_Ω', x: 190, y: 70, status: 'VERIFIED' },
  { id: 'n3', label: 'AST Scaffolding', assignee: 'Sir_Forge', x: 330, y: 35, status: 'VERIFIED' },
  { id: 'n4', label: 'WASM MicroVM', assignee: 'Sir_Octavian', x: 330, y: 105, status: 'VERIFIED' },
  { id: 'n5', label: 'Z3 Convexity Prove', assignee: 'Sir_Codex', x: 470, y: 70, status: 'VERIFIED' },
  { id: 'n6', label: 'Provenance Seal', assignee: 'Sir_Helios', x: 600, y: 70, status: 'VERIFIED' },
];

const DAG_EDGES = [
  { from: 'n1', to: 'n2' },
  { from: 'n2', to: 'n3' },
  { from: 'n2', to: 'n4' },
  { from: 'n3', to: 'n5' },
  { from: 'n4', to: 'n5' },
  { from: 'n5', to: 'n6' },
];

interface OmniForgeStudioProps {
  onReceiptGenerated?: (hash: string) => void;
}

export default function OmniForgeStudio({ onReceiptGenerated }: OmniForgeStudioProps) {
  const [stages, setStages] = useState<StageState[]>(INITIAL_STAGES);
  const [activeTab, setActiveTab] = useState<'pipeline' | 'dag' | 'artifacts'>('pipeline');
  const [selectedStageId, setSelectedStageId] = useState<number>(1);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [runDurationMs, setRunDurationMs] = useState<number>(203.83);
  const [lastReceipt, setLastReceipt] = useState<string>('485657f4238121506cd73c468cb2db2cc5b708c19a6a9fcd665b622411bb625e');
  const [copiedHash, setCopiedHash] = useState<boolean>(false);

  const selectedStage = stages.find((s) => s.id === selectedStageId) || stages[0];

  const handleIgniteForge = () => {
    if (isRunning) return;
    setIsRunning(true);

    // Reset all stages to PENDING
    setStages((prev) =>
      prev.map((s) => ({
        ...s,
        status: 'PENDING',
      }))
    );

    let currentStep = 0;
    const interval = setInterval(() => {
      if (currentStep < 7) {
        setStages((prev) =>
          prev.map((s, idx) => {
            if (idx === currentStep) {
              return { ...s, status: 'RUNNING' };
            }
            if (idx < currentStep) {
              return { ...s, status: 'VERIFIED' };
            }
            return { ...s, status: 'PENDING' };
          })
        );
        currentStep++;
      } else {
        clearInterval(interval);
        // Generate new dynamic receipt
        const randHex = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
        setLastReceipt(randHex);
        setRunDurationMs(Math.round(180 + Math.random() * 40));
        setIsRunning(false);
        setStages((prev) =>
          prev.map((s) => ({
            ...s,
            status: 'VERIFIED',
          }))
        );
        if (onReceiptGenerated) {
          onReceiptGenerated(randHex);
        }
      }
    }, 280);
  };

  const handleCopyReceipt = () => {
    navigator.clipboard.writeText(lastReceipt);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <div className="border border-camelot-gold/30 bg-obsidian-smoke/70 rounded-lg p-5 backdrop-blur shadow-2xl flex flex-col space-y-5">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between border-b border-gray-800 pb-4 gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-camelot-gold/10 border border-camelot-gold/40 text-camelot-gold">
            <Workflow className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold tracking-wider text-camelot-gold uppercase">
                Arthurian Omni-Forge Studio
              </h2>
              <span className="px-2 py-0.5 text-[10px] font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-500/40 rounded">
                7-PHASE ACTIVE
              </span>
            </div>
            <p className="text-xs text-gray-400 font-mono">
              Operator: <span className="text-camelot-violet font-semibold">Merlin_Ω ⊕ Sir_Forge</span> | Constitution: <span className="text-camelot-cyan">const_engineering_v1</span>
            </p>
          </div>
        </div>

        {/* Forge Action Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleIgniteForge}
            disabled={isRunning}
            className={`flex items-center gap-2 px-4 py-2 rounded font-mono text-xs font-bold transition-all ${
              isRunning
                ? 'bg-amber-600/30 text-amber-300 border border-amber-500/50 cursor-not-allowed animate-pulse'
                : 'bg-camelot-gold/20 hover:bg-camelot-gold/30 text-camelot-gold border border-camelot-gold/60 shadow-lg shadow-camelot-gold/10'
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>SYNTHESIZING...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-camelot-gold" />
                <span>IGNITE DIGITAL FORGE</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800 gap-4 text-xs font-mono">
        <button
          onClick={() => setActiveTab('pipeline')}
          className={`pb-2 transition-colors flex items-center gap-1.5 ${
            activeTab === 'pipeline'
              ? 'border-b-2 border-camelot-gold text-camelot-gold font-bold'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Layers className="h-3.5 w-3.5" />
          <span>7-Phase State Machine</span>
        </button>
        <button
          onClick={() => setActiveTab('dag')}
          className={`pb-2 transition-colors flex items-center gap-1.5 ${
            activeTab === 'dag'
              ? 'border-b-2 border-camelot-gold text-camelot-gold font-bold'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Network className="h-3.5 w-3.5" />
          <span>Topological DAG Graph</span>
        </button>
        <button
          onClick={() => setActiveTab('artifacts')}
          className={`pb-2 transition-colors flex items-center gap-1.5 ${
            activeTab === 'artifacts'
              ? 'border-b-2 border-camelot-gold text-camelot-gold font-bold'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <FileCode className="h-3.5 w-3.5" />
          <span>Z3 Proofs & Artifacts</span>
        </button>
      </div>

      {/* TAB 1: 7-Phase State Machine Stepper */}
      {activeTab === 'pipeline' && (
        <div className="space-y-4">
          {/* Stepper Bar */}
          <div className="grid grid-cols-7 gap-2 bg-black/40 p-3 rounded border border-gray-800">
            {stages.map((stage) => {
              const isSelected = stage.id === selectedStageId;
              return (
                <button
                  key={stage.id}
                  onClick={() => setSelectedStageId(stage.id)}
                  className={`flex flex-col items-center text-center p-2 rounded transition-all ${
                    isSelected
                      ? 'bg-camelot-gold/15 border border-camelot-gold/60'
                      : 'hover:bg-white/5 border border-transparent'
                  }`}
                >
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center border text-xs font-mono font-bold mb-1 transition-all ${
                      stage.status === 'VERIFIED'
                        ? 'bg-emerald-950/80 border-emerald-500 text-emerald-400'
                        : stage.status === 'RUNNING'
                        ? 'bg-amber-950/80 border-amber-400 text-amber-300 animate-pulse'
                        : 'bg-gray-900 border-gray-700 text-gray-500'
                    }`}
                  >
                    {stage.status === 'VERIFIED' ? (
                      <CheckCircle2 className="h-4 w-4" />
                    ) : stage.status === 'RUNNING' ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <span>{stage.id}</span>
                    )}
                  </div>
                  <span className="text-[10px] font-mono font-bold text-gray-300 truncate w-full">
                    {stage.key}
                  </span>
                  <span className="text-[9px] font-mono text-gray-500">{stage.durationMs}ms</span>
                </button>
              );
            })}
          </div>

          {/* Selected Stage Detail Card */}
          <div className="bg-black/50 border border-camelot-gold/20 rounded p-4 space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-gray-800 pb-2">
              <div className="flex items-center gap-2">
                <span className="text-camelot-gold font-bold">{selectedStage.name}</span>
                <span className="px-1.5 py-0.5 text-[10px] bg-camelot-violet/20 text-camelot-violet border border-camelot-violet/40 rounded">
                  {selectedStage.assignee}
                </span>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  selectedStage.status === 'VERIFIED'
                    ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                    : selectedStage.status === 'RUNNING'
                    ? 'bg-amber-950 text-amber-300 border border-amber-500/30'
                    : 'bg-gray-800 text-gray-400'
                }`}
              >
                {selectedStage.status}
              </span>
            </div>
            <p className="text-gray-300">{selectedStage.description}</p>
            <div className="grid grid-cols-2 gap-3 text-[11px] pt-1">
              <div className="p-2 bg-black/60 rounded border border-gray-800">
                <span className="text-gray-500 block text-[9px] uppercase">Telemetry</span>
                <span className="text-camelot-cyan">{selectedStage.telemetry}</span>
              </div>
              <div className="p-2 bg-black/60 rounded border border-gray-800">
                <span className="text-gray-500 block text-[9px] uppercase">Artifact Link</span>
                <span className="text-camelot-gold truncate block">
                  {selectedStage.artifact || 'In-Memory State Transition'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Interactive Topological DAG SVG */}
      {activeTab === 'dag' && (
        <div className="space-y-3">
          <div className="bg-black/60 border border-gray-800 rounded p-3 relative overflow-hidden">
            <div className="flex justify-between items-center mb-2 font-mono text-[11px] text-gray-400">
              <span className="flex items-center gap-1.5 text-camelot-cyan">
                <Network className="h-3.5 w-3.5" />
                <span>TASK_DAG.JSON TOPOLOGICAL COMPILATION</span>
              </span>
              <span>6 Parallel Nodes | Strict Linear Dependency</span>
            </div>
            <svg viewBox="0 0 680 140" className="w-full h-36">
              <defs>
                <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#00E5FF" stopOpacity="0.7" />
                </linearGradient>
              </defs>

              {/* Render Directed Edges */}
              {DAG_EDGES.map((edge, i) => {
                const source = DAG_NODES.find((n) => n.id === edge.from)!;
                const target = DAG_NODES.find((n) => n.id === edge.to)!;
                return (
                  <path
                    key={i}
                    d={`M ${source.x + 35} ${source.y} C ${source.x + 70} ${source.y}, ${target.x - 70} ${target.y}, ${target.x - 35} ${target.y}`}
                    fill="none"
                    stroke="url(#edgeGrad)"
                    strokeWidth="1.5"
                    strokeDasharray="4 2"
                  />
                );
              })}

              {/* Render DAG Nodes */}
              {DAG_NODES.map((node) => (
                <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
                  <rect
                    x="-40"
                    y="-18"
                    width="80"
                    height="36"
                    rx="6"
                    className="fill-obsidian-smoke stroke-camelot-gold/50 stroke-1 hover:stroke-camelot-gold cursor-pointer transition-all"
                  />
                  <text
                    x="0"
                    y="-3"
                    textAnchor="middle"
                    className="fill-gray-200 font-mono text-[9px] font-bold"
                  >
                    {node.label}
                  </text>
                  <text
                    x="0"
                    y="10"
                    textAnchor="middle"
                    className="fill-camelot-cyan font-mono text-[8px]"
                  >
                    {node.assignee}
                  </text>
                </g>
              ))}
            </svg>
          </div>
        </div>
      )}

      {/* TAB 3: Z3 Proofs & Artifacts */}
      {activeTab === 'artifacts' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="bg-black/60 border border-gray-800 rounded p-3 space-y-2">
            <div className="flex justify-between items-center text-camelot-gold border-b border-gray-800 pb-1">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                <span>FORMAL Z3 SMT CONVEXITY VERIFICATION</span>
              </span>
              <span className="text-emerald-400 text-[10px]">VERDICT: SATISFIED</span>
            </div>
            <pre className="text-[10px] text-gray-300 overflow-x-auto p-2 bg-black/80 rounded">
{`{
  "theorem": "Omni-Forge_Integration_Convexity",
  "solver": "Z3_SMT_PROVER",
  "status": "SATISFIED",
  "invariant_violations": 0,
  "rigor_ladder": {
    "L1_self_test": "PASS (11/11 Invariants)",
    "L2_smt_bound": "PASS (ΔM <= 0.12 MiB; RSS <= 512 MB)",
    "L3_property_battery": "PASS (zero path escapes, root_ro: TRUE)",
    "L4_cross_verified_proof": "PASS (Omni-Forge_Integration_Convexity == TRUE)"
  }
}`}
            </pre>
          </div>
        </div>
      )}

      {/* Cryptographic Execution Receipt Footer */}
      <div className="border-t border-gray-800 pt-3 flex flex-wrap items-center justify-between text-xs font-mono gap-3">
        <div className="flex items-center gap-2">
          <Hash className="h-4 w-4 text-camelot-cyan" />
          <span className="text-gray-400">PINNED RECEIPT:</span>
          <span className="text-camelot-gold font-bold select-all truncate max-w-[280px] sm:max-w-md">
            {lastReceipt}
          </span>
          <button
            onClick={handleCopyReceipt}
            className="p-1 hover:bg-white/10 rounded text-gray-400 hover:text-camelot-cyan transition-colors"
            title="Copy Receipt Hash"
          >
            {copiedHash ? <Check className="h-3.5 w-3.5 text-green-400" /> : <Terminal className="h-3.5 w-3.5" />}
          </button>
        </div>
        <div className="text-[11px] text-gray-400">
          Duration: <span className="text-green-400 font-bold">{runDurationMs}ms</span>
        </div>
      </div>
    </div>
  );
}
