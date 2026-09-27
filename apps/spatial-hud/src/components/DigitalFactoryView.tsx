import React, { useState } from 'react';
import { ThemeMode } from '../types';
import { 
  Factory, 
  Cpu, 
  Layers, 
  Workflow, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  Play, 
  RefreshCw, 
  Download, 
  Copy, 
  Check, 
  Code, 
  ShieldCheck, 
  Boxes, 
  Flame 
} from 'lucide-react';
import { multiVoiceRouter } from '../services/multiVoiceRouter';
import { motion } from 'motion/react';

interface DigitalFactoryViewProps {
  theme?: ThemeMode;
  onKineticTrigger?: (cmd: string) => void;
}

interface BlastStage {
  id: string;
  name: string;
  code: string;
  leadKnight: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'VALIDATED';
  description: string;
  deliverable: string;
}

const INITIAL_BLAST_STAGES: BlastStage[] = [
  {
    id: 'blueprint',
    name: '1. BLUEPRINT',
    code: 'SPEC_DAG_V3',
    leadKnight: 'MERLIN_Ω',
    status: 'COMPLETED',
    description: 'System-2 architectural decomposition, AST parsing, and user requirements spec.',
    deliverable: 'spec.camelot.json (DAG Spec Contract)'
  },
  {
    id: 'link',
    name: '2. LINK',
    code: 'VFS_GRAPH_SYNC',
    leadKnight: 'LADY_MNEMOSYNE',
    status: 'COMPLETED',
    description: 'Resolves package dependencies, mounts VFS crystals, and binds 24D Leech Lattice vectors.',
    deliverable: 'lattice.bindings.toml'
  },
  {
    id: 'architect',
    name: '3. ARCHITECT',
    code: 'AST_SYNTHESIS',
    leadKnight: 'SIR_HYDRON',
    status: 'COMPLETED',
    description: 'Compiles declarative A2UI schema, scaffold React 19 / Vite components, and sets up state.',
    deliverable: 'ComponentMatrix.tsx & StateRouter.ts'
  },
  {
    id: 'stylize',
    name: '4. STYLIZE',
    code: 'THREEUI_DTCG',
    leadKnight: 'SIR_VISAGE & SIR_STITCH',
    status: 'COMPLETED',
    description: 'Applies Neo-Spatial Cyberpunk tokens, WebGPU shaders, and Framer Motion spring physics.',
    deliverable: 'threeui.theme.json & styles.css'
  },
  {
    id: 'trigger',
    name: '5. TRIGGER',
    code: 'CONSTITUTIONAL_GATE',
    leadKnight: 'SIR_GIDEON & SIR_BORIS',
    status: 'COMPLETED',
    description: 'Gideon L7 safety audit, Boris chaos stress testing, and edge node deployment dispatch.',
    deliverable: 'GoldenReceipt.L7.sig (Verified Hash)'
  }
];

export const DigitalFactoryView: React.FC<DigitalFactoryViewProps> = ({
  theme = 'dark',
  onKineticTrigger
}) => {
  const isDark = theme === 'dark';

  const [stages, setStages] = useState<BlastStage[]>(INITIAL_BLAST_STAGES);
  const [selectedArtifactType, setSelectedArtifactType] = useState<'A2UI_CARTRIDGE' | 'THREEUI_WIDGET' | 'VOICE_AGENT' | 'SMART_CONTRACT'>('THREEUI_WIDGET');
  const [artifactName, setArtifactName] = useState('SpatialQuantumDial');
  const [isCompiling, setIsCompiling] = useState(false);
  const [copied, setCopied] = useState(false);
  const [factoryLogs, setFactoryLogs] = useState<string[]>([
    '[02:45:10] FACTORY_CORE: Sovereign Digital Factory initialized on 8GB Edge Node.',
    '[02:45:12] BLAST_PIPELINE: Loaded 5-stage sovereign manufacturing chain.',
    '[02:45:15] AGENT_SWARM: 5 Lead Knights assigned to factory workstations.'
  ]);

  // Generated Artifact Code Template
  const generatedCode = `// ============================================================================
// SOVEREIGN DIGITAL FACTORY ARTIFACT: ${artifactName}
// GENERATED VIA BLAST PIPELINE (CYBERTRONIA EDGE NODE)
// TYPE: ${selectedArtifactType}
// LEAD ARCHITECT: MERLIN_Ω & SIR_HYDRON
// ============================================================================

import React from 'react';
import * as THREE from 'three';
import { multiVoiceRouter } from './services/multiVoiceRouter';

export interface ${artifactName}Props {
  theme?: 'dark' | 'light';
  frequency?: number;
  onTrigger?: (data: any) => void;
}

export const ${artifactName}: React.FC<${artifactName}Props> = ({
  theme = 'dark',
  frequency = 440,
  onTrigger
}) => {
  const isDark = theme === 'dark';

  const handleActivate = () => {
    multiVoiceRouter.playCyberSfx('lock');
    if (onTrigger) {
      onTrigger({ status: 'ACTIVE', timestamp: Date.now(), node: 'CLEVELAND_EDGE' });
    }
  };

  return (
    <div className="p-4 border border-cyan-500/30 bg-black/80 backdrop-blur-md text-white font-mono">
      <div className="flex justify-between items-center mb-2 border-b border-cyan-500/20 pb-1">
        <span className="text-xs font-bold text-cyan-400">${artifactName.toUpperCase()}</span>
        <span className="text-[10px] text-amber-400 font-bold">TYPE: ${selectedArtifactType}</span>
      </div>
      <p className="text-xs text-neutral-300 mb-3">
        Declarative ThreeUI spatial element with live Web Audio telemetry bindings.
      </p>
      <button
        onClick={handleActivate}
        className="px-3 py-1.5 bg-cyan-500 text-black font-bold text-xs hover:bg-cyan-400 transition-all"
      >
        //activate:${artifactName.toLowerCase()}
      </button>
    </div>
  );
};`;

  const handleRunPipeline = () => {
    setIsCompiling(true);
    multiVoiceRouter.playCyberSfx('boot');
    multiVoiceRouter.speakAsKnight('hydron', `Initializing BLAST Digital Factory run for ${artifactName}. All 5 production stages armed.`);

    setFactoryLogs(prev => [
      `[${new Date().toLocaleTimeString()}] COMPILER: Starting BLAST pipeline build for ${artifactName}...`,
      ...prev
    ]);

    // Simulate progressive assembly
    setTimeout(() => {
      multiVoiceRouter.playCyberSfx('beam');
      setFactoryLogs(prev => [
        `[${new Date().toLocaleTimeString()}] ARCHITECT: Generated AST for ${selectedArtifactType}.`,
        ...prev
      ]);
    }, 800);

    setTimeout(() => {
      multiVoiceRouter.playCyberSfx('lock');
      setIsCompiling(false);
      setFactoryLogs(prev => [
        `[${new Date().toLocaleTimeString()}] TRIGGER: Gideon L7 Constitutional check PASSED. Golden Receipt signed.`,
        ...prev
      ]);
    }, 1800);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`w-full flex flex-col gap-6 p-4 lg:p-6 backdrop-blur-md border ${
      isDark 
        ? 'bg-[#080511]/90 border-cyan-500/30 text-white shadow-2xl' 
        : 'bg-white/95 border-cyan-600/30 text-slate-900 shadow-xl'
    }`}>
      
      {/* FACTORY HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b pb-4 border-cyan-500/20">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-amber-500 to-rose-600 text-black font-bold shadow-lg shadow-amber-500/20">
            <Factory className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-black tracking-widest uppercase font-mono">
                SOVEREIGN DIGITAL FACTORY & BLAST ENGINE
              </h2>
              <span className={`text-[10px] px-2 py-0.5 font-mono font-bold border ${
                isDark ? 'bg-amber-950/80 border-amber-500 text-amber-300' : 'bg-amber-100 border-amber-400 text-amber-800'
              }`}>
                BLAST_V4_CORE
              </span>
            </div>
            <p className="text-xs opacity-75 font-mono mt-0.5">
              Automated Multi-Agent Software Assembly Line // Edge Node Cleveland
            </p>
          </div>
        </div>

        {/* Factory Quick Stats */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className={`px-2.5 py-1 border flex items-center gap-1.5 ${
            isDark ? 'bg-[#0E091D] border-cyan-500/30 text-cyan-400' : 'bg-cyan-50 border-cyan-300 text-cyan-800'
          }`}>
            <Cpu className="w-3.5 h-3.5" />
            <span>YIELD: 99.98%</span>
          </div>

          <button
            onClick={handleRunPipeline}
            disabled={isCompiling}
            className="px-4 py-1.5 bg-gradient-to-r from-amber-500 to-rose-500 hover:from-amber-400 hover:to-rose-400 text-black font-bold font-mono text-xs border border-amber-300 transition-all flex items-center gap-1.5 active:scale-95 disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-black" />
            <span>{isCompiling ? 'MANUFACTURING...' : 'RUN BLAST PIPELINE'}</span>
          </button>
        </div>
      </div>

      {/* 5-STAGE BLAST CONVEYOR BELT */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs font-mono text-cyan-400 font-bold">
          <span>BLAST PIPELINE CONVEYOR (BLUEPRINT → LINK → ARCHITECT → STYLIZE → TRIGGER)</span>
          <span className="text-[11px] opacity-75">5 Active Autonomous Stages</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {stages.map((stage, idx) => (
            <div
              key={stage.id}
              className={`p-3 border flex flex-col justify-between relative overflow-hidden transition-all ${
                isDark 
                  ? 'bg-[#050507] border-cyan-500/30 shadow-md' 
                  : 'bg-slate-50 border-slate-300 shadow-sm'
              }`}
            >
              {/* Stage Number Marker */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-black font-mono text-amber-400">
                  {stage.name}
                </span>
                <span className="text-[9px] px-1.5 py-0.2 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-mono font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-2.5 h-2.5" />
                  VALID
                </span>
              </div>

              <div className="text-[10px] font-mono text-cyan-400 font-bold mb-1">
                LEAD: {stage.leadKnight}
              </div>

              <p className="text-[10px] opacity-75 font-mono leading-tight mb-2">
                {stage.description}
              </p>

              <div className={`p-1.5 border text-[9px] font-mono ${
                isDark ? 'bg-[#0E091D] border-purple-500/30 text-purple-200' : 'bg-white border-purple-200 text-purple-900'
              }`}>
                OUTPUT: {stage.deliverable}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ARTIFACT COMPILER & VAULT */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Manufacturing Config (Cols 1-4) */}
        <div className={`lg:col-span-4 border p-4 flex flex-col justify-between ${
          isDark ? 'bg-[#050507] border-cyan-500/20' : 'bg-slate-50 border-slate-300'
        }`}>
          <div>
            <h3 className="text-xs font-bold font-mono text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Boxes className="w-4 h-4" />
              Artifact Blueprint Configuration
            </h3>

            {/* Target Artifact Selector */}
            <div className="space-y-2 mb-4">
              <label className="text-[11px] font-mono opacity-80 block">TARGET ARTIFACT TYPE</label>
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                {[
                  { id: 'THREEUI_WIDGET', label: 'ThreeUI 3D Widget' },
                  { id: 'A2UI_CARTRIDGE', label: 'A2UI Cartridge' },
                  { id: 'VOICE_AGENT', label: 'Knight Voice Agent' },
                  { id: 'SMART_CONTRACT', label: 'L7 Smart Contract' }
                ].map(type => (
                  <button
                    key={type.id}
                    onClick={() => setSelectedArtifactType(type.id as any)}
                    className={`p-2 border text-left font-bold transition-all ${
                      selectedArtifactType === type.id
                        ? isDark ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300' : 'bg-cyan-100 border-cyan-500 text-cyan-900'
                        : isDark ? 'bg-white/5 border-white/10 text-neutral-400' : 'bg-white border-slate-200 text-slate-700'
                    }`}
                  >
                    {type.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Artifact Name Input */}
            <div className="space-y-1 mb-4">
              <label className="text-[11px] font-mono opacity-80 block">ARTIFACT IDENTIFIER</label>
              <input
                type="text"
                value={artifactName}
                onChange={(e) => setArtifactName(e.target.value)}
                className={`w-full p-2 text-xs font-mono border focus:outline-none ${
                  isDark 
                    ? 'bg-[#0E091D] border-cyan-500/40 text-white focus:border-cyan-400' 
                    : 'bg-white border-slate-300 text-slate-900 focus:border-cyan-600'
                }`}
              />
            </div>

            {/* Scarcity Guard Notice */}
            <div className={`p-2.5 border text-[10px] font-mono flex items-center gap-2 ${
              isDark ? 'bg-amber-950/30 border-amber-500/40 text-amber-300' : 'bg-amber-50 border-amber-300 text-amber-900'
            }`}>
              <ShieldCheck className="w-4 h-4 shrink-0 text-amber-400" />
              <span>8GB Scarcity Guard Active: AST cache clamped to &lt;250MB.</span>
            </div>
          </div>

          <button
            onClick={handleRunPipeline}
            disabled={isCompiling}
            className="mt-4 w-full py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-bold font-mono text-xs border border-cyan-300 transition-all flex items-center justify-center gap-2 active:scale-95"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isCompiling ? 'animate-spin' : ''}`} />
            <span>SYNTHESIZE ARTIFACT</span>
          </button>
        </div>

        {/* Right: Code Inspector & Output Vault (Cols 5-12) */}
        <div className={`lg:col-span-8 border p-4 flex flex-col justify-between ${
          isDark ? 'bg-[#050507] border-purple-500/20' : 'bg-slate-50 border-slate-300'
        }`}>
          <div>
            <div className="flex items-center justify-between border-b pb-2 mb-3 border-cyan-500/20">
              <div className="flex items-center gap-2">
                <Code className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-bold font-mono uppercase text-purple-400">
                  OUTPUT ARTIFACT CODE // {artifactName}.tsx
                </span>
              </div>

              <button
                onClick={handleCopy}
                className={`px-2.5 py-1 border text-[10px] font-mono flex items-center gap-1.5 transition-all ${
                  copied 
                    ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300' 
                    : isDark ? 'bg-[#150E24] border-purple-500/40 text-purple-200 hover:bg-purple-950' : 'bg-white border-purple-300 text-purple-900'
                }`}
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'COPIED TO CLIPBOARD' : 'COPY CODE'}</span>
              </button>
            </div>

            {/* Code Display Area */}
            <div className={`p-3 border font-mono text-[11px] leading-relaxed max-h-[260px] overflow-y-auto ${
              isDark ? 'bg-[#0A0710] border-cyan-500/20 text-cyan-200' : 'bg-slate-900 border-slate-800 text-cyan-300'
            }`}>
              <pre>{generatedCode}</pre>
            </div>
          </div>

          {/* Real-time Factory Assembly Logs */}
          <div className="mt-3 pt-2 border-t border-cyan-500/20">
            <div className="text-[10px] font-mono opacity-60 mb-1">FACTORY TELEMETRY LOGS</div>
            <div className="space-y-1 max-h-20 overflow-y-auto text-[10px] font-mono opacity-85">
              {factoryLogs.map((log, i) => (
                <div key={i} className="leading-tight text-neutral-400">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
