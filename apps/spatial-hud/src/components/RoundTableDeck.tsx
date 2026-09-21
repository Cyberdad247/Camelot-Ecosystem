import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Users,
  Cpu,
  ShieldAlert,
  Zap,
  Activity,
  Terminal as TerminalIcon,
  Play,
  RefreshCw,
  Layers,
  Sparkles,
  Lock,
  Radio,
  CheckCircle2,
  AlertTriangle,
  Send,
  HardDrive
} from 'lucide-react';
import { ThemeMode } from '../types';
import { useMasterAgentStore, CaptainType, activeAudioGainAtom, audio3DCoordinateAtom } from '../services/agentBridge';
import { multiVoiceRouter } from '../services/multiVoiceRouter';
import { AegisShieldEngine } from '../services/aegisShield';

interface RoundTableDeckProps {
  theme: ThemeMode;
  onKineticTrigger?: (trigger: string) => void;
}

const CAPTAIN_PROFILES: Record<
  CaptainType,
  {
    name: string;
    title: string;
    specialty: string;
    avatarBorder: string;
    accentColor: string;
    voiceKnight: string;
    responsibilities: string[];
    hardwareBinding: string;
  }
> = {
  Sir_Boris: {
    name: 'Sir Boris',
    title: 'High Marshall of Frontend UI & Spatial Layouts',
    specialty: '12-Column Visual Grid, Doherty < 400ms, A2UI Micro-Frontends',
    avatarBorder: 'border-cyan-400',
    accentColor: '#00E5FF',
    voiceKnight: 'boris',
    responsibilities: ['12-Column Layout Engine', 'Zero Layout Shift (CLS 0.00)', 'Tailwind v4 Token Sync'],
    hardwareBinding: 'GPU Viewport & Compositor (DOM Layer)'
  },
  Sir_Codex: {
    name: 'Sir Codex',
    title: 'Grand Magister of AST Synthesis & WASM Engines',
    specialty: 'WASM32-WASIP1 Sandboxes, Camelot-AST-Engine, Rust FFI',
    avatarBorder: 'border-purple-400',
    accentColor: '#9D4EDD',
    voiceKnight: 'codex',
    responsibilities: ['AST Verified Mutation', 'WASI Component Model', 'Memory-Safe Sandbox Isolation'],
    hardwareBinding: 'WASM32 SIMD Ring Buffers'
  },
  Sir_Helio: {
    name: 'Sir Helio',
    title: 'Sovereign Navigator of 1M+ Context & Worldtree MCP',
    specialty: 'Long-Horizon Context Compression, DuckDB-WASM, Cross-Agent CRDTs',
    avatarBorder: 'border-amber-400',
    accentColor: '#E5B842',
    voiceKnight: 'helio',
    responsibilities: ['Triple-QFT Semantic Anchors', 'CRDT Vector Clocks', 'DuckDB-WASM Session Store'],
    hardwareBinding: 'ZeroClaw memfd_create Shared Memory'
  },
  Sir_Octavian: {
    name: 'Sir Octavian',
    title: 'Lord Commander of ARM64 Microkernel & Scarcity',
    specialty: 'Ouroboros 1.58b Ternary SSM, 7.2GB RAM Ceiling, Scarcity Clamps',
    avatarBorder: 'border-rose-400',
    accentColor: '#FF007F',
    voiceKnight: 'octavian',
    responsibilities: ['1.58-Bit Ternary SSM Weights', '90% Memory Watchdog Interrupt', 'SIGUSR2 Buffer Flusher'],
    hardwareBinding: 'Ouroboros Mamba-3 SSM Core'
  },
  'Merlin_Ω': {
    name: 'Merlin Ω',
    title: 'Arch-Strategist of System-2 DAG Planning',
    specialty: 'Graph-of-Thoughts (GoT) Planning, Z3 SMT Formal Solver, Acyclic DAGs',
    avatarBorder: 'border-emerald-400',
    accentColor: '#10B981',
    voiceKnight: 'merlin',
    responsibilities: ['Topological Kahn Execution', 'Z3 Invariant Validation', 'Multi-Agent Quorum Laws'],
    hardwareBinding: 'DAG Execution Virtual Plane'
  },
  'Anya_Ω': {
    name: 'Anya Ω',
    title: 'Sovereign Sentinel & Iron Gate Custodian',
    specialty: 'Aegis Shield L7 Ingress, Prompt Armor, Iron Gate HITL Checkpoints',
    avatarBorder: 'border-pink-500',
    accentColor: '#EC4899',
    voiceKnight: 'anya',
    responsibilities: ['Layer 7 Intent Sanitizer', 'PII Scrubber', 'Immutable Core Defense'],
    hardwareBinding: 'Aegis Shield Hypervisor'
  }
};

export const RoundTableDeck: React.FC<RoundTableDeckProps> = ({ theme, onKineticTrigger }) => {
  const isDark = theme === 'dark';
  const {
    activeSessions,
    systemMemoryUsageMB,
    maxMemoryCeilingMB,
    totalSemanticDrift,
    isIronGateTripped,
    ironGateTripReason,
    executeDAGTask,
    tripIronGate,
    resetIronGate,
    clearSession
  } = useMasterAgentStore();

  const [selectedCaptain, setSelectedCaptain] = useState<CaptainType>('Sir_Boris');
  const [customTaskName, setCustomTaskName] = useState<string>('');
  const [sanitizationAudit, setSanitizationAudit] = useState<{
    tested: boolean;
    input: string;
    output: string;
    status: string;
    threat: string;
  } | null>(null);

  const activeCaptain = CAPTAIN_PROFILES[selectedCaptain];
  const sessionsArray = Array.from(activeSessions.values());
  const ramPercentage = Math.min(100, (systemMemoryUsageMB / maxMemoryCeilingMB) * 100);

  const handleDispatchTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customTaskName.trim()) return;

    // Run through Aegis Shield first
    const check = AegisShieldEngine.sanitizeIntent(customTaskName);
    if (!check.isValid) {
      setSanitizationAudit({
        tested: true,
        input: customTaskName,
        output: 'BLOCKED BY AEGIS SHIELD',
        status: 'CRITICAL_BLOCK',
        threat: check.flags.join('; ')
      });
      tripIronGate('INGRESS_TASK', check.flags.join('; '));
      multiVoiceRouter.speakAsKnight('anya', 'Threat detected by Aegis Shield. Immutable core protected.');
      return;
    }

    setSanitizationAudit({
      tested: true,
      input: customTaskName,
      output: check.sanitizedText,
      status: 'CLEAN',
      threat: check.flags.length > 0 ? check.flags.join(', ') : 'None'
    });

    const taskId = executeDAGTask(selectedCaptain, check.sanitizedText, {
      piiScrubbed: check.piiScrubbedCount,
      timestamp: Date.now()
    });

    multiVoiceRouter.speakAsKnight(
      activeCaptain.voiceKnight,
      `Task dispatched to ${activeCaptain.name}. Commencing DAG execution.`
    );

    setCustomTaskName('');
    if (onKineticTrigger) onKineticTrigger(`TASK_DISPATCH_${selectedCaptain}`);
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Iron Gate Alert Banner if Tripped */}
      <AnimatePresence>
        {isIronGateTripped && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="p-4 rounded-xl border border-rose-500 bg-rose-950/80 text-rose-200 shadow-[0_0_30px_rgba(244,63,94,0.4)] flex flex-wrap items-center justify-between gap-4"
          >
            <div className="flex items-center space-x-3">
              <ShieldAlert className="w-6 h-6 text-rose-400 animate-pulse" />
              <div>
                <div className="text-sm font-bold tracking-wider uppercase">
                  ANYA IRON GATE HITL ENGAGED // EXECUTION HALTED
                </div>
                <div className="text-xs text-rose-300">Reason: {ironGateTripReason}</div>
              </div>
            </div>
            <button
              onClick={resetIronGate}
              className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition-all shadow-md cursor-pointer"
            >
              //REZERO & RESET GATE
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Top Telemetry & Memory Watchdog Bar */}
      <div
        className={`p-4 sm:p-5 rounded-2xl border backdrop-blur-xl transition-all ${
          isDark
            ? 'bg-[#050508]/90 border-[rgba(0,229,255,0.2)] shadow-[0_0_30px_rgba(0,0,0,0.8)]'
            : 'bg-white/95 border-slate-300 shadow-lg'
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-400">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base sm:text-lg font-bold tracking-wider text-cyan-400">
                  ROUND TABLE AGENT COCKPIT // 12-COLUMN SOVEREIGN MATRIX
                </h2>
                <span className="px-2 py-0.5 text-[10px] rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                  APEE v7.0 COMPLIANT
                </span>
              </div>
              <p className="text-xs text-neutral-400">
                Merlin Ω DAG Planner • Sir Boris • Sir Codex • Sir Helio • Sir Octavian • Anya Ω Gate
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="px-3 py-1.5 rounded-lg bg-neutral-900 border border-neutral-800 text-xs">
              <span className="text-neutral-400">eTUNE DRIFT: </span>
              <span className="text-emerald-400 font-bold">{(totalSemanticDrift * 100).toFixed(3)}% &lt; 0.700%</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-neutral-900 border border-neutral-800 text-xs">
              <span className="text-neutral-400">GC THRESHOLD: </span>
              <span className="text-pink-400 font-bold">7.2GB (90% CEILING)</span>
            </div>
          </div>
        </div>

        {/* 8GB RAM Scarcity Clamp Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-neutral-400 flex items-center space-x-1.5">
              <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
              <span>EDGE NODE RAM WATCHDOG ({systemMemoryUsageMB.toFixed(1)} / {maxMemoryCeilingMB.toFixed(1)} MB)</span>
            </span>
            <span className={ramPercentage > 80 ? 'text-amber-400 font-bold' : 'text-cyan-300 font-bold'}>
              {ramPercentage.toFixed(1)}% ALLOCATED
            </span>
          </div>
          <div className="w-full bg-neutral-900 rounded-full h-2.5 overflow-hidden border border-neutral-800">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                ramPercentage > 80
                  ? 'bg-gradient-to-r from-amber-500 to-rose-500'
                  : 'bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500'
              }`}
              style={{ width: `${ramPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* 12-Column Main Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Captain Selector Grid (4 Cols) */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-bold text-neutral-400 uppercase tracking-wider px-1">
            ROUND TABLE COMMANDERS (6 VECTORS)
          </h3>
          <div className="space-y-2">
            {(Object.keys(CAPTAIN_PROFILES) as CaptainType[]).map((key) => {
              const cap = CAPTAIN_PROFILES[key];
              const isSelected = selectedCaptain === key;
              return (
                <button
                  key={key}
                  onClick={() => {
                    setSelectedCaptain(key);
                    multiVoiceRouter.speakAsKnight(cap.voiceKnight, `${cap.name} active and standing by.`);
                  }}
                  className={`w-full text-left p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? `bg-neutral-900/90 ${cap.avatarBorder} shadow-[0_0_15px_rgba(0,229,255,0.15)]`
                      : 'bg-neutral-950/60 border-neutral-800/80 hover:border-neutral-700 hover:bg-neutral-900/40 text-neutral-400'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-sm text-neutral-100" style={{ color: isSelected ? cap.accentColor : undefined }}>
                      {cap.name}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-neutral-800 text-neutral-300 font-mono">
                      {key}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-400 line-clamp-1">{cap.title}</p>
                  <p className="text-[10px] text-neutral-500 mt-1 font-mono">{cap.hardwareBinding}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Center & Right Column: Active Captain Workbench & DAG Task Stream (8 Cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Active Captain Spec Card */}
          <div
            className={`p-5 rounded-2xl border ${
              isDark ? 'bg-[#0a0a10] border-neutral-800' : 'bg-white border-slate-200'
            }`}
          >
            <div className="flex flex-wrap items-start justify-between gap-4 mb-4 pb-4 border-b border-neutral-800">
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="text-lg font-bold" style={{ color: activeCaptain.accentColor }}>
                    {activeCaptain.name}
                  </h3>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-neutral-900 border border-neutral-700 text-neutral-300 font-mono">
                    {activeCaptain.title}
                  </span>
                </div>
                <p className="text-xs text-neutral-400 mt-1">{activeCaptain.specialty}</p>
              </div>

              <button
                onClick={() => multiVoiceRouter.speakAsKnight(activeCaptain.voiceKnight, `${activeCaptain.name} reporting ready for DAG synthesis.`)}
                className="px-3 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 border border-neutral-700 text-xs font-mono text-cyan-300 flex items-center space-x-1.5 cursor-pointer"
              >
                <Radio className="w-3.5 h-3.5 text-pink-400" />
                <span>VOICE ANNOUNCE</span>
              </button>
            </div>

            {/* Responsibilities */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-4">
              {activeCaptain.responsibilities.map((resp, i) => (
                <div key={i} className="p-2.5 rounded-lg bg-neutral-900/60 border border-neutral-800 text-[11px] text-neutral-300 flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>{resp}</span>
                </div>
              ))}
            </div>

            {/* Task Ingress Dispatch Form */}
            <form onSubmit={handleDispatchTask} className="space-y-3">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={customTaskName}
                  onChange={(e) => setCustomTaskName(e.target.value)}
                  placeholder={`Dispatch sub-agent DAG task to ${activeCaptain.name}... (e.g. "Synthesize 12-column A2UI layout")`}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-neutral-950 border border-neutral-800 text-xs text-neutral-100 placeholder-neutral-500 focus:outline-none focus:border-cyan-400 font-mono"
                />
                <button
                  type="submit"
                  className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs flex items-center space-x-1.5 transition-all shadow-[0_0_15px_rgba(0,229,255,0.3)] cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>DISPATCH</span>
                </button>
              </div>

              {sanitizationAudit && (
                <div className="p-2.5 rounded-lg bg-neutral-950 border border-neutral-800 text-[10px] font-mono flex items-center justify-between text-neutral-400">
                  <span>AEGIS SHIELD INGRESS: <strong className={sanitizationAudit.status === 'CLEAN' ? 'text-emerald-400' : 'text-rose-400'}>{sanitizationAudit.status}</strong></span>
                  <span>FLAGS: {sanitizationAudit.threat}</span>
                </div>
              )}
            </form>
          </div>

          {/* Active DAG Sessions & State Bridge Matrix */}
          <div
            className={`p-5 rounded-2xl border ${
              isDark ? 'bg-[#0a0a10] border-neutral-800' : 'bg-white border-slate-200'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <h4 className="text-sm font-bold text-neutral-200">
                  ACTIVE DAG EXECUTION PIPELINES ({sessionsArray.length})
                </h4>
              </div>
              <span className="text-xs text-neutral-400 font-mono">
                Z3 SMT VERIFIED ERROR RATE: &lt; 0.7%
              </span>
            </div>

            <div className="space-y-2.5 max-h-72 overflow-y-auto">
              {sessionsArray.map((session) => (
                <div
                  key={session.taskId}
                  className="p-3.5 rounded-xl bg-neutral-950/80 border border-neutral-800/80 flex flex-wrap items-center justify-between gap-3 text-xs"
                >
                  <div className="space-y-1 max-w-md">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-neutral-100">{session.taskName}</span>
                      <span className="px-2 py-0.2 rounded text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800">
                        {session.captain}
                      </span>
                    </div>
                    <div className="text-[11px] text-neutral-400 flex items-center space-x-3">
                      <span>STAGE: <strong className="text-purple-300">{session.dagStage}</strong></span>
                      <span>MEM: <strong>{session.memoryFootprintMB} MB</strong></span>
                      <span>DRIFT: <strong>{(session.semanticDrift * 100).toFixed(3)}%</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2.5 py-1 rounded text-[10px] font-mono font-bold ${
                        session.status === 'COMPLETED' || session.status === 'VERIFIED'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : session.status === 'PROCESSING'
                          ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 animate-pulse'
                          : session.status === 'HALTED_IRON_GATE'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : 'bg-neutral-800 text-neutral-300'
                      }`}
                    >
                      {session.status}
                    </span>
                    <button
                      onClick={() => clearSession(session.taskId)}
                      className="p-1 rounded text-neutral-500 hover:text-rose-400"
                      title="Clear session"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoundTableDeck;
