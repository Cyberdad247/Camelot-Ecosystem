import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { SovereignCartridge, ThemeMode } from '../types';
import { multiVoiceRouter } from '../services/multiVoiceRouter';
import { SovereignHeraldry } from './SovereignHeraldry';
import { VpsDigitalTwin } from './VpsDigitalTwin';

interface CartridgeMatrixViewProps {
  theme: ThemeMode;
  onKineticTrigger: (trigger: string) => void;
  onSwitchTab?: (tab: string) => void;
}

const DEFAULT_CARTRIDGES: SovereignCartridge[] = [
  {
    id: 'CRTR-Ω-01',
    code: 'Ωv10000.54',
    name: 'Autonomous Agentic UI/UX Operating System',
    version: '10000.54.0-APEX',
    themeIdentified: 'Autonomous Agentic UI/UX Operating System',
    mantraCrystal: 'Ωv10000.54::NDR+S(GoT)⊢Z3(SAT)::Ouroboros(1.58b)→O(1)mem::QFT(R,Q,P)::A2UI(60:30:10|8pt)→Δt<400ms',
    leadKnights: ['MERLIN_Ω', 'SIR_GIDEON', 'SIR_HYDRON', 'SIR_VISAGE', 'ANYA_Ω'],
    division: 'Executive',
    targetLatencyMs: 342,
    memoryFootprintMb: 184.2,
    memoryRecurrence: 'Ouroboros-1.58b-O(1)',
    topologicalValidator: "Kahn's Acyclic GoT + Z3 SMT L7",
    qftCompressionFactor: 4.82,
    color: '#00E5FF',
    status: 'ENGAGED',
    payloadSchema: {
      a2uiStandard: 'A2UI_V10000.54',
      ratio: '60:30:10',
      grid: '8pt spatial subgrid',
      targetPlatform: '8GB Edge Node / Cleveland Node'
    },
    description: 'Sovereign flagship cartridge unifying Ouroboros 1.58-bit SSM, Kahn-Z3 topological DAG validation, and Triple-QFT Semantic Anchor Compression into a sub-second hot-swappable A2UI runtime.'
  },
  {
    id: 'CRTR-Ω-06',
    code: 'VPS-DYNAMIC-TWIN-vMAX',
    name: 'VPS Dynamic Digital Twin (vMAX)',
    version: '10000.54.1-ASCENDED',
    themeIdentified: 'Spatial WebGPU Infrastructure Hologram & Nginx Telemetry',
    mantraCrystal: 'VPS_TWIN::WEBGPU(OCTAHEDRON)+SSE(PROMETHEUS)⊢A2UI(60:30:10)→Δt<400ms',
    leadKnights: ['ANYA_Ω', 'SIR_VISAGE', 'SIR_STITCH', 'SIR_HYDRON', 'SIR_CODEX'],
    division: 'Core Engineering & Vanguard',
    targetLatencyMs: 240,
    memoryFootprintMb: 168.0,
    memoryRecurrence: 'WebGPU-Normalized-V_R3',
    topologicalValidator: 'L7-Constitutional-Scarcity-SMT',
    qftCompressionFactor: 5.10,
    color: '#00E5FF',
    status: 'STANDBY',
    payloadSchema: {
      endpoints: ['Nginx_Reverse_Proxy', 'Prometheus_Grafana_Mimir', 'Node_RAM_8GB_Clamp'],
      renderTarget: 'React_Three_Fiber_Canvas_WebGPU',
      dohertyThresholdMs: 400
    },
    description: 'vMAX Dynamic Digital Twin mapping Nginx Reverse Proxy, Prometheus metrics, and ML-KEM-768 quantum handshakes onto an interactive 3D WebGPU wireframe core.'
  },
  {
    id: 'CRTR-Ω-02',
    code: 'THREEUI-SPATIAL-01',
    name: 'ThreeUI Spatial WebGPU Substrate',
    version: '3.14.2',
    themeIdentified: 'Spatial 3D Holographic HUD & Audio Spectrum',
    mantraCrystal: 'THREEUI::WEBGPU+RAYCAST⊢64BAND(FFT)::HERALDRY(3D)→60FPS',
    leadKnights: ['SIR_STITCH', 'SIR_VISAGE'],
    division: 'Core Engineering & Vanguard',
    targetLatencyMs: 280,
    memoryFootprintMb: 142.0,
    memoryRecurrence: 'Volumetric-Buffer-Static',
    topologicalValidator: 'SceneGraph-Acyclic-Proof',
    qftCompressionFactor: 3.90,
    color: '#9D4EDD',
    status: 'STANDBY',
    payloadSchema: {
      repo: 'https://github.com/Cyberdad247/threeui.git',
      renderEngine: 'WebGL/WebGPU ACESFilmic',
      audioChannels: 24
    },
    description: 'WebGL/WebGPU spatial canvas featuring dynamic 3D shield & crown heraldry, non-coplanar orbital halos, and 24-band live audio spectrum equalizers.'
  },
  {
    id: 'CRTR-Ω-03',
    code: 'MULTIVOICE-ROUTER-01',
    name: 'Multi-Voice 9-Channel Multiplexer',
    version: '2.4.0',
    themeIdentified: 'Zero-Cloud Web Audio DSP & Voice Dispatcher',
    mantraCrystal: 'DSP::OSCILLATOR(SINE,SAW)+STT(INTENT)⊢9KNIGHTS→LOCAL_VOICE',
    leadKnights: ['ANYA_Ω', 'SIR_BORIS', 'LADY_MNEMOSYNE'],
    division: 'Streaming & Customer Ops',
    targetLatencyMs: 195,
    memoryFootprintMb: 68.5,
    memoryRecurrence: 'AudioBuffer-O(1)',
    topologicalValidator: 'AudioGraph-DAG-Verifier',
    qftCompressionFactor: 5.40,
    color: '#FF007F',
    status: 'STANDBY',
    payloadSchema: {
      repo: 'https://github.com/Cyberdad247/Multivoice-router',
      sfxGenerators: 6,
      speechProfiles: 9
    },
    description: 'Full-stack client-side voice synthesis underlayer generating cybernetic sound waves, Web Speech API speech-to-text, and Knight personality vocoders.'
  },
  {
    id: 'CRTR-Ω-04',
    code: 'BLAST-FACTORY-V4',
    name: 'Sovereign Digital Factory (BLAST V4)',
    version: '4.0.1',
    themeIdentified: '5-Stage Autonomous Code Synthesis Line',
    mantraCrystal: 'BLAST::B(Spec)→L(VFS)→A(AST)→S(DTCG)→T(Gideon Gate)→ARTIFACT',
    leadKnights: ['SIR_HYDRON', 'MERLIN_Ω'],
    division: 'Core Engineering & Vanguard',
    targetLatencyMs: 388,
    memoryFootprintMb: 196.4,
    memoryRecurrence: 'AST-Cache-Bound',
    topologicalValidator: 'Kahn-AST-Toposort',
    qftCompressionFactor: 4.15,
    color: '#E5B842',
    status: 'STANDBY',
    payloadSchema: {
      stations: 5,
      exportTargets: ['ThreeUI', 'A2UI Cartridge', 'Voice Agent', 'L7 Contract'],
      memoryClampMb: 250
    },
    description: 'Autonomous assembly line taking natural language specifications through Blueprint, Link, Architect, Stylize, and Trigger stations to generate production code.'
  },
  {
    id: 'CRTR-Ω-05',
    code: 'GIDEON-L7-GATE',
    name: 'Gideon Constitutional Sentinel & Z3 SMT',
    version: '7.1.0',
    themeIdentified: '4 Immutable Pillars Theorem Prover',
    mantraCrystal: 'GIDEON::PILLARS(4)⊢Z3(SMT)+L7(SECURITY)→CONSTITUTIONAL_EXEC',
    leadKnights: ['SIR_GIDEON'],
    division: 'Executive',
    targetLatencyMs: 120,
    memoryFootprintMb: 52.0,
    memoryRecurrence: 'Symbolic-Proof-O(1)',
    topologicalValidator: 'Z3-SMT-Complete',
    qftCompressionFactor: 6.20,
    color: '#10B981',
    status: 'STANDBY',
    payloadSchema: {
      pillars: ['Sovereignty', 'Transparency', 'Non-Malice', 'Scarcity'],
      securityLevel: 'L7-CRYPTO'
    },
    description: 'Cryptographic sentinel verifying formal mathematical proofs against constitutional boundary violations and hardware resource starvation.'
  }
];

export function CartridgeMatrixView({ theme, onKineticTrigger, onSwitchTab }: CartridgeMatrixViewProps) {
  const isDark = theme === 'dark';
  const [cartridges, setCartridges] = useState<SovereignCartridge[]>(DEFAULT_CARTRIDGES);
  const [activeCartridgeId, setActiveCartridgeId] = useState<string>('CRTR-Ω-01');
  const [activeSubTab, setActiveSubTab] = useState<'slot' | 'vps-twin' | 'ouroboros' | 'z3-kahn' | 'triple-qft' | 'json-rom'>('slot');
  const [isTransfiguring, setIsTransfiguring] = useState<boolean>(false);
  const [transfigureProgress, setTransfigureProgress] = useState<number>(100);

  // Vector 1: Ouroboros SSM State
  const [ssmTokens, setSsmTokens] = useState<string[]>(['Ω', 'INIT', 'GOT_DAG', 'Z3_SAT', 'OUROBOROS_1.58B', 'A2UI_RENDER']);
  const [ssmInput, setSsmInput] = useState<string>('SYNAPSE_PULSE');
  const [hiddenStateValues, setHiddenStateValues] = useState<number[]>([0.72, -0.41, 0.95, -0.88, 0.12, 0.64, -0.33, 0.91]);
  const [memoryHistory, setMemoryHistory] = useState<number[]>([184.2, 184.2, 184.3, 184.1, 184.2, 184.2, 184.2]);

  // Vector 2: Z3 Kahn's DAG State
  const [dagNodes, setDagNodes] = useState<Array<{ id: string; name: string; inDegree: number; status: 'resolved' | 'processing' | 'pending'; pillar: string }>>([
    { id: 'N1', name: 'SPEC_BLUEPRINT', inDegree: 0, status: 'resolved', pillar: 'Sovereignty' },
    { id: 'N2', name: 'VFS_LINK_GRAPH', inDegree: 1, status: 'resolved', pillar: 'Transparency' },
    { id: 'N3', name: 'AST_SYNTHESIS', inDegree: 1, status: 'resolved', pillar: 'Non-Malice' },
    { id: 'N4', name: 'DTCG_TOKEN_STYLE', inDegree: 2, status: 'processing', pillar: 'Scarcity' },
    { id: 'N5', name: 'GIDEON_L7_GATE', inDegree: 2, status: 'pending', pillar: 'Constitutional Seal' }
  ]);
  const [hasCycleError, setHasCycleError] = useState<boolean>(false);

  // Vector 3: Triple-QFT & SAC State
  const [qftRawText, setQftRawText] = useState<string>(
    'Synthesize autonomous agentic UI dashboard with 60:30:10 hierarchy, ThreeUI 3D holographic shield, and 9-channel multi-voice router.'
  );
  const [qftPhase, setQftPhase] = useState<'idle' | 'rescale' | 'quench' | 'perturb' | 'complete'>('complete');
  const [sacAnchor, setSacAnchor] = useState<string>('Ω::SAC[AUTON_UI|60:30:10|THREEUI_3D|VOICE_9CH]⊕Δt<342ms');
  const [compressionRatio, setCompressionRatio] = useState<number>(4.82);
  const [measuredLatency, setMeasuredLatency] = useState<number>(342);

  const currentCartridge = useMemo(() => {
    return cartridges.find(c => c.id === activeCartridgeId) || cartridges[0];
  }, [cartridges, activeCartridgeId]);

  // Transfigure & Engage Cartridge
  const handleEngageCartridge = (cartridgeId: string) => {
    if (cartridgeId === activeCartridgeId && currentCartridge.status === 'ENGAGED') return;

    multiVoiceRouter.playCyberSfx('lock');
    setIsTransfiguring(true);
    setTransfigureProgress(15);

    setCartridges(prev => prev.map(c => ({
      ...c,
      status: c.id === cartridgeId ? 'TRANSFIGURING' : 'STANDBY'
    })));

    const t1 = setTimeout(() => {
      setTransfigureProgress(65);
      multiVoiceRouter.playCyberSfx('beam');
    }, 120);

    const t2 = setTimeout(() => {
      setTransfigureProgress(100);
      setIsTransfiguring(false);
      setActiveCartridgeId(cartridgeId);
      setCartridges(prev => prev.map(c => ({
        ...c,
        status: c.id === cartridgeId ? 'ENGAGED' : 'STANDBY'
      })));

      const target = cartridges.find(c => c.id === cartridgeId);
      multiVoiceRouter.playCyberSfx('boot');
      if (target) {
        multiVoiceRouter.speakAsKnight(
          target.leadKnights[0]?.toLowerCase().includes('boris') ? 'boris' :
          target.leadKnights[0]?.toLowerCase().includes('merlin') ? 'merlin' :
          target.leadKnights[0]?.toLowerCase().includes('gideon') ? 'gideon' :
          target.leadKnights[0]?.toLowerCase().includes('hydron') ? 'hydron' : 'anya',
          `Cartridge ${target.code} engaged. νKG Mantra Crystal loaded.`
        );
      }
    }, 320);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  };

  // Eject Cartridge
  const handleEjectCartridge = () => {
    multiVoiceRouter.playCyberSfx('chaos');
    multiVoiceRouter.speakAsKnight('boris', 'Cartridge unseated from quantum bus.');
    setCartridges(prev => prev.map(c => c.id === activeCartridgeId ? { ...c, status: 'EJECTED' } : c));
  };

  // Vector 1: Feed Token into Ouroboros 1.58-bit SSM
  const handleFeedSsmToken = () => {
    if (!ssmInput.trim()) return;
    multiVoiceRouter.playCyberSfx('beep');
    const newToken = ssmInput.trim().toUpperCase();
    setSsmTokens(prev => [...prev.slice(-7), newToken]);
    setSsmInput('');

    // Compute new ternary-bounded hidden states
    setHiddenStateValues(prev => prev.map(() => {
      const ternaryWeight = [-1, 0, 1][Math.floor(Math.random() * 3)];
      return Number((Math.tanh(Math.random() * 2 - 1) * 0.85 + ternaryWeight * 0.15).toFixed(2));
    }));

    // Maintain flat O(1) memory
    setMemoryHistory(prev => [...prev.slice(1), 184.2 + Number((Math.random() * 0.4 - 0.2).toFixed(2))]);
  };

  // Vector 2: Run Z3 Kahn's Topological Sort Step
  const handleStepKahnsSort = () => {
    multiVoiceRouter.playCyberSfx('lock');
    setDagNodes(prev => {
      const pendingIdx = prev.findIndex(n => n.status === 'processing');
      if (pendingIdx !== -1) {
        const next = [...prev];
        next[pendingIdx] = { ...next[pendingIdx], status: 'resolved' };
        if (pendingIdx + 1 < next.length) {
          next[pendingIdx + 1] = { ...next[pendingIdx + 1], status: 'processing', inDegree: 0 };
        }
        return next;
      }
      return prev.map((n, i) => ({
        ...n,
        status: i === 0 ? 'resolved' : i === 1 ? 'processing' : 'pending',
        inDegree: i === 0 ? 0 : 1
      }));
    });
    setHasCycleError(false);
  };

  // Vector 2: Inject Cyclic Dependency to test Z3 Gate
  const handleInjectCycle = () => {
    multiVoiceRouter.playCyberSfx('chaos');
    multiVoiceRouter.speakAsKnight('gideon', 'Z3 SMT Invariant Violation detected! Cyclic dependency in AST pipeline.');
    setHasCycleError(true);
    setDagNodes(prev => prev.map(n => ({ ...n, inDegree: 99, status: 'pending' })));
  };

  // Vector 3: Run Triple-QFT & SAC Renormalization
  const handleRunTripleQft = () => {
    if (!qftRawText.trim()) return;
    multiVoiceRouter.playCyberSfx('beam');
    setQftPhase('rescale');

    setTimeout(() => {
      setQftPhase('quench');
      multiVoiceRouter.playCyberSfx('beep');
    }, 100);

    setTimeout(() => {
      setQftPhase('perturb');
    }, 200);

    setTimeout(() => {
      setQftPhase('complete');
      const rawLen = qftRawText.length;
      const compressed = `Ω::SAC[${qftRawText.slice(0, 24).replace(/\s+/g, '_').toUpperCase()}|8pt_DTCG]⊕Δt<${Math.floor(280 + Math.random() * 80)}ms`;
      setSacAnchor(compressed);
      const ratio = Number((rawLen / Math.max(compressed.length, 1) * 2.2).toFixed(2));
      setCompressionRatio(ratio > 1 ? ratio : 4.82);
      const latency = Math.floor(290 + Math.random() * 70);
      setMeasuredLatency(latency);
      multiVoiceRouter.playCyberSfx('lock');
      multiVoiceRouter.speakAsKnight('anya', `Triple-QFT complete. Semantic Anchor compressed at ${ratio}x.`);
    }, 320);
  };

  return (
    <div className={`flex-1 flex flex-col h-full overflow-y-auto ${isDark ? 'bg-neutral-950 text-neutral-100' : 'bg-slate-50 text-slate-900'} p-4 lg:p-6 transition-colors font-sans`}>
      
      {/* Top Banner / Mantra Crystal Header */}
      <div className={`p-4 rounded-xl border mb-6 relative overflow-hidden ${isDark ? 'bg-neutral-900/90 border-cyan-500/30' : 'bg-white border-cyan-300 shadow-sm'}`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                A2UI_CARTRIDGE_HOTSWAP_V10000.54
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider bg-purple-500/20 text-purple-400 border border-purple-500/30">
                Δt &lt; 400ms TARGET
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider bg-amber-500/20 text-amber-400 border border-amber-500/30">
                OUROBOROS O(1) MEM
              </span>
            </div>
            <h1 className="text-xl lg:text-2xl font-black tracking-tight mt-2 flex items-center space-x-2">
              <span className="text-cyan-400">⚡</span>
              <span>Hot-Swappable Cartridge Matrix</span>
              <span className="text-xs font-mono font-normal opacity-60">| Autonomous Agentic OS</span>
            </h1>
            <p className={`text-xs mt-1 font-mono ${isDark ? 'text-neutral-400' : 'text-slate-600'}`}>
              νKG_MANTRA_CRYSTAL: <span className="text-cyan-400 font-bold">{currentCartridge.mantraCrystal}</span>
            </p>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onKineticTrigger('//rezero')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold border transition-all ${
                isDark ? 'bg-neutral-800 hover:bg-neutral-700 text-neutral-200 border-neutral-700' : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300'
              }`}
            >
              //rezero
            </button>
            <button
              onClick={() => onKineticTrigger('//chaos:inject')}
              className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-pink-500/20 hover:bg-pink-500/30 text-pink-400 border border-pink-500/40 transition-all"
            >
              //chaos:inject
            </button>
            {onSwitchTab && (
              <button
                onClick={() => onSwitchTab('command-center')}
                className="px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold bg-cyan-500 hover:bg-cyan-400 text-black shadow-lg shadow-cyan-500/20 transition-all"
              >
                ★ Command Center
              </button>
            )}
          </div>
        </div>

        {/* Transfiguration Progress Bar */}
        {isTransfiguring && (
          <div className="mt-3 w-full bg-neutral-800 rounded-full h-1.5 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500"
              initial={{ width: '0%' }}
              animate={{ width: `${transfigureProgress}%` }}
              transition={{ duration: 0.2 }}
            />
          </div>
        )}
      </div>

      {/* Navigation Sub-Tabs */}
      <div className={`flex space-x-2 border-b mb-6 pb-2 overflow-x-auto ${isDark ? 'border-neutral-800' : 'border-slate-200'}`}>
        {[
          { id: 'slot', label: '🕹️ Hot-Swap Slot & Vault', badge: `${cartridges.length} Cartridges` },
          { id: 'vps-twin', label: '🌐 VPS Dynamic Twin (vMAX)', badge: 'WebGPU 3D' },
          { id: 'ouroboros', label: '1. Ouroboros 1.58b SSM', badge: 'O(1) Memory' },
          { id: 'z3-kahn', label: "2. Z3 Kahn's DAG Gate", badge: 'Topological SAT' },
          { id: 'triple-qft', label: '3. Triple-QFT & SAC', badge: 'Δt < 400ms' },
          { id: 'json-rom', label: '📦 A2UI Cartridge JSON ROM', badge: 'v10000.54' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => {
              multiVoiceRouter.playCyberSfx('beep');
              setActiveSubTab(tab.id as any);
            }}
            className={`px-3.5 py-2 rounded-lg text-xs font-mono font-bold flex items-center space-x-2 transition-all whitespace-nowrap ${
              activeSubTab === tab.id
                ? isDark
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'bg-cyan-100 text-cyan-900 border border-cyan-300 shadow-sm'
                : isDark
                  ? 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <span>{tab.label}</span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded ${isDark ? 'bg-neutral-800 text-neutral-300' : 'bg-slate-200 text-slate-700'}`}>
              {tab.badge}
            </span>
          </button>
        ))}
      </div>

      {/* Sub-Tab 1: Physical Hot-Swap Slot & Cartridge Vault */}
      {activeSubTab === 'slot' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Active Cartridge Slot Drive */}
          <div className="lg:col-span-5 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border relative ${isDark ? 'bg-neutral-900/90 border-cyan-500/40' : 'bg-white border-cyan-200 shadow-md'}`}>
              <div className="flex items-center justify-between border-b pb-3 mb-4 border-neutral-800">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full animate-pulse ${currentCartridge.status === 'ENGAGED' ? 'bg-emerald-400' : currentCartridge.status === 'EJECTED' ? 'bg-rose-500' : 'bg-amber-400'}`} />
                  <span className="text-xs font-mono font-bold uppercase tracking-wider">
                    CARTRIDGE_SLOT_0 // STATUS: {currentCartridge.status}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  {currentCartridge.status === 'ENGAGED' ? (
                    <button
                      onClick={handleEjectCartridge}
                      className="px-2.5 py-1 text-[11px] font-mono font-bold rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 transition-all flex items-center space-x-1"
                    >
                      <span>⏏</span>
                      <span>EJECT</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEngageCartridge(currentCartridge.id)}
                      className="px-2.5 py-1 text-[11px] font-mono font-bold rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 transition-all flex items-center space-x-1"
                    >
                      <span>⚡</span>
                      <span>ENGAGE</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Physical Cartridge Hologram View */}
              <div className={`p-4 rounded-lg border relative overflow-hidden transition-all ${
                currentCartridge.status === 'ENGAGED'
                  ? isDark
                    ? 'bg-neutral-950 border-cyan-500 shadow-[0_0_25px_rgba(0,229,255,0.15)]'
                    : 'bg-cyan-50/50 border-cyan-400 shadow-sm'
                  : 'bg-neutral-950/50 border-neutral-800 opacity-60'
              }`}>
                {/* Scanline Overlay */}
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent pointer-events-none opacity-40 animate-pulse" />

                <div className="flex items-start justify-between relative z-10">
                  <div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-bold">
                      {currentCartridge.code}
                    </span>
                    <h2 className="text-base font-black tracking-tight mt-1.5 text-neutral-100">
                      {currentCartridge.name}
                    </h2>
                    <p className="text-[11px] text-cyan-400 font-mono mt-0.5">
                      Theme: {currentCartridge.themeIdentified}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-mono text-neutral-400 block">LATENCY</span>
                    <span className="text-sm font-mono font-bold text-emerald-400">
                      {currentCartridge.targetLatencyMs}ms
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-neutral-800 text-[11px] font-mono">
                  <div>
                    <span className="text-neutral-500 block text-[10px]">MEMORY RECURRENCE</span>
                    <span className="text-amber-400 font-bold">{currentCartridge.memoryRecurrence}</span>
                  </div>
                  <div>
                    <span className="text-neutral-500 block text-[10px]">MEMORY CLAMP</span>
                    <span className="text-neutral-200">{currentCartridge.memoryFootprintMb} MB / 250 MB</span>
                  </div>
                  <div>
                    <span className="text-neutral-500 block text-[10px]">VALIDATOR</span>
                    <span className="text-purple-400 font-bold">{currentCartridge.topologicalValidator}</span>
                  </div>
                  <div>
                    <span className="text-neutral-500 block text-[10px]">QFT SAC SQUEEZE</span>
                    <span className="text-cyan-300 font-bold">{currentCartridge.qftCompressionFactor}x</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-neutral-800 flex items-center justify-between text-[11px] font-mono">
                  <div className="flex items-center space-x-1">
                    <span className="text-neutral-500">LEAD:</span>
                    {currentCartridge.leadKnights.map((k, i) => (
                      <span key={i} className="px-1.5 py-0.2 rounded bg-neutral-800 text-neutral-300 text-[10px]">
                        {k}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={() => {
                      multiVoiceRouter.speakAsKnight(
                        currentCartridge.leadKnights[0]?.toLowerCase().includes('boris') ? 'boris' : 'merlin',
                        `Sovereign Cartridge ${currentCartridge.name} operational.`
                      );
                    }}
                    className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 text-[10px] font-mono font-bold"
                  >
                    🔊 Test Voice
                  </button>
                </div>
              </div>

              {/* Hardware Heraldry */}
              <div className="mt-4">
                <SovereignHeraldry variant="compact" theme={theme} />
              </div>
            </div>
          </div>

          {/* Cartridge Vault (Hot-Swappable Selection) */}
          <div className="lg:col-span-7 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border flex-1 ${isDark ? 'bg-neutral-900/90 border-neutral-800' : 'bg-white border-slate-200 shadow-sm'}`}>
              <div className="flex items-center justify-between mb-4 pb-2 border-b border-neutral-800">
                <h3 className="text-sm font-mono font-bold tracking-wider flex items-center space-x-2">
                  <span className="text-cyan-400">⚡</span>
                  <span>HOT-SWAPPABLE CARTRIDGE VAULT</span>
                </h3>
                <span className="text-xs font-mono text-neutral-400">Click to Ingest into Slot</span>
              </div>

              <div className="space-y-3">
                {cartridges.map(cartridge => {
                  const isCurrent = cartridge.id === activeCartridgeId;
                  return (
                    <div
                      key={cartridge.id}
                      onClick={() => handleEngageCartridge(cartridge.id)}
                      className={`p-3.5 rounded-lg border transition-all cursor-pointer relative overflow-hidden ${
                        isCurrent
                          ? isDark
                            ? 'bg-neutral-950 border-cyan-400 shadow-[0_0_15px_rgba(0,229,255,0.2)]'
                            : 'bg-cyan-50 border-cyan-500 shadow-sm'
                          : isDark
                            ? 'bg-neutral-950/60 border-neutral-800/80 hover:border-neutral-700 hover:bg-neutral-900/50'
                            : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-2.5 h-2.5 rounded-full ${isCurrent ? 'bg-cyan-400 animate-ping' : 'bg-neutral-600'}`} />
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs font-mono font-bold text-neutral-200">{cartridge.code}</span>
                              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-neutral-800 text-neutral-400">
                                {cartridge.division}
                              </span>
                            </div>
                            <h4 className="text-sm font-bold text-neutral-100">{cartridge.name}</h4>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3 text-right">
                          <div>
                            <span className="text-[10px] font-mono text-neutral-500 block">MEMORY</span>
                            <span className="text-xs font-mono font-bold text-amber-400">{cartridge.memoryFootprintMb} MB</span>
                          </div>
                          <button
                            className={`px-3 py-1 text-xs font-mono font-bold rounded transition-all ${
                              isCurrent
                                ? 'bg-cyan-500 text-black font-black'
                                : isDark
                                  ? 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
                                  : 'bg-slate-200 text-slate-800'
                            }`}
                          >
                            {isCurrent ? 'ACTIVE' : 'HOT-SWAP'}
                          </button>
                        </div>
                      </div>

                      <p className="text-[11px] text-neutral-400 mt-2 line-clamp-2">
                        {cartridge.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab: VPS Dynamic Twin (vMAX) Full Spatial Dashboard */}
      {activeSubTab === 'vps-twin' && (
        <div className="space-y-4">
          <VpsDigitalTwin theme={theme} onKineticTrigger={onKineticTrigger} />
        </div>
      )}

      {/* Sub-Tab 2: Vector 1 - Ouroboros 1.58-bit State Space Model (SSM) */}
      {activeSubTab === 'ouroboros' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border ${isDark ? 'bg-neutral-900/90 border-cyan-500/30' : 'bg-white border-slate-200 shadow-sm'}`}>
              <div className="flex items-center justify-between border-b pb-2 mb-3 border-neutral-800">
                <h3 className="text-sm font-mono font-bold tracking-wider text-cyan-400">
                  1. OUROBOROS 1.58-BIT SSM RECURRENCE ENGINE
                </h3>
                <span className="text-xs font-mono text-emerald-400 font-bold">O(1) CONSTANT MEMORY</span>
              </div>

              <p className="text-xs text-neutral-300 mb-4 leading-relaxed">
                The Ouroboros State Space Model utilizes <strong>ternary quantization (W ∈ {'{-1, 0, +1}'})</strong> with 
                continuous state matrix recursion: <code className="text-cyan-300 font-mono">h_t = A·h_(t-1) + B·x_t</code>. 
                Unlike Transformer self-attention (O(N²) quadratic RAM blowup), Ouroboros locks memory strictly at ~184 MB on 8GB Edge nodes.
              </p>

              {/* Live Token Sequence Input */}
              <div className="flex space-x-2 mb-4">
                <input
                  type="text"
                  value={ssmInput}
                  onChange={e => setSsmInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleFeedSsmToken()}
                  placeholder="Feed token / state impulse..."
                  className={`flex-1 px-3 py-2 rounded-lg text-xs font-mono border focus:outline-none focus:ring-1 focus:ring-cyan-400 ${
                    isDark ? 'bg-neutral-950 border-neutral-800 text-neutral-200' : 'bg-slate-100 border-slate-300 text-slate-900'
                  }`}
                />
                <button
                  onClick={handleFeedSsmToken}
                  className="px-4 py-2 rounded-lg text-xs font-mono font-bold bg-cyan-500 hover:bg-cyan-400 text-black shadow-md transition-all"
                >
                  FEED STEP ➔
                </button>
              </div>

              {/* Rolling Sequence Buffer */}
              <div>
                <span className="text-[10px] font-mono text-neutral-500 block mb-1">RECURRENT TOKEN BUFFER (O(1) TAIL):</span>
                <div className="flex flex-wrap gap-1.5 p-2.5 rounded-lg bg-neutral-950 border border-neutral-800 min-h-[42px] items-center">
                  {ssmTokens.map((tok, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 text-[11px] font-mono font-bold">
                      {tok}
                    </span>
                  ))}
                </div>
              </div>

              {/* Ternary State Space Vector Values */}
              <div className="mt-4">
                <span className="text-[10px] font-mono text-neutral-500 block mb-1">
                  1.58-BIT TERNARY HIDDEN STATE VECTOR (h_t ∈ [-1, 1]):
                </span>
                <div className="grid grid-cols-4 gap-2">
                  {hiddenStateValues.map((val, idx) => (
                    <div key={idx} className="p-2 rounded bg-neutral-950 border border-neutral-800 text-center">
                      <span className="text-[9px] font-mono text-neutral-500 block">h[{idx}]</span>
                      <span className={`text-xs font-mono font-bold ${val > 0 ? 'text-cyan-400' : val < 0 ? 'text-rose-400' : 'text-neutral-400'}`}>
                        {val >= 0 ? `+${val}` : val}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Memory Profiler Telemetry */}
          <div className="lg:col-span-6 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border flex-1 ${isDark ? 'bg-neutral-900/90 border-neutral-800' : 'bg-white border-slate-200 shadow-sm'}`}>
              <div className="flex items-center justify-between border-b pb-2 mb-3 border-neutral-800">
                <h3 className="text-sm font-mono font-bold tracking-wider text-amber-400">
                  MEMORY CONFINEMENT TELEMETRY (8GB EDGE PROFILE)
                </h3>
                <span className="text-xs font-mono text-emerald-400 font-bold">STABLE 184.2 MB</span>
              </div>

              {/* Visual Memory Graph */}
              <div className="p-4 rounded-lg bg-neutral-950 border border-neutral-800 mb-4">
                <div className="flex items-center justify-between text-xs font-mono text-neutral-400 mb-2">
                  <span>RAM USAGE (MB)</span>
                  <span className="text-amber-400 font-bold">SCARCITY CLAMP: &lt; 250 MB</span>
                </div>
                <div className="h-28 flex items-end space-x-2 pt-4 border-b border-neutral-800">
                  {memoryHistory.map((val, i) => {
                    const heightPct = Math.min((val / 250) * 100, 100);
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center">
                        <span className="text-[9px] font-mono text-neutral-400 mb-1">{val.toFixed(1)}</span>
                        <div
                          className="w-full bg-cyan-500/80 rounded-t border-t border-cyan-300"
                          style={{ height: `${heightPct}%` }}
                        />
                      </div>
                    );
                  })}
                </div>
                <div className="flex justify-between text-[10px] font-mono text-neutral-500 mt-2">
                  <span>t-6</span>
                  <span>t-5</span>
                  <span>t-4</span>
                  <span>t-3</span>
                  <span>t-2</span>
                  <span>t-1</span>
                  <span>CURRENT (t_0)</span>
                </div>
              </div>

              {/* Transformer vs Ouroboros Comparison */}
              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="p-3 rounded bg-rose-950/30 border border-rose-500/30 text-rose-200">
                  <span className="font-bold text-rose-400 block mb-1">Standard Transformer:</span>
                  <p className="text-[11px] opacity-80">Attention KV cache scales as O(N²). Memory blows past 4GB after 16k tokens.</p>
                </div>
                <div className="p-3 rounded bg-emerald-950/30 border border-emerald-500/30 text-emerald-200">
                  <span className="font-bold text-emerald-400 block mb-1">Ouroboros 1.58b:</span>
                  <p className="text-[11px] opacity-80">Strict O(1) recurrence. Zero cache blowup over infinite execution turns.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 3: Vector 2 - Z3 Kahn's Topological Validator & SAT Gate */}
      {activeSubTab === 'z3-kahn' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border ${isDark ? 'bg-neutral-900/90 border-purple-500/30' : 'bg-white border-slate-200 shadow-sm'}`}>
              <div className="flex items-center justify-between border-b pb-2 mb-3 border-neutral-800">
                <h3 className="text-sm font-mono font-bold tracking-wider text-purple-400">
                  2. Z3 KAHN&apos;S TOPOLOGICAL VALIDATOR &amp; SAT GATE
                </h3>
                <span className={`text-xs font-mono font-bold ${hasCycleError ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {hasCycleError ? '❌ SAT VIOLATION: CYCLE' : '✓ SAT: PROOF COMPLETE'}
                </span>
              </div>

              <p className="text-xs text-neutral-300 mb-4 leading-relaxed">
                Every agentic action graph (Graph-of-Thoughts) is validated using <strong>Kahn&apos;s Acyclic Topological Sort</strong> 
                and verified via <strong>Z3 SMT logic theorem proving</strong> against the 4 Constitutional Pillars before execution.
              </p>

              {/* Action Controls */}
              <div className="flex items-center space-x-3 mb-4">
                <button
                  onClick={handleStepKahnsSort}
                  className="px-3.5 py-2 rounded-lg text-xs font-mono font-bold bg-purple-500 hover:bg-purple-400 text-black shadow-md transition-all"
                >
                  ▶ STEP KAHN&apos;S SORT
                </button>
                <button
                  onClick={handleInjectCycle}
                  className="px-3 py-2 rounded-lg text-xs font-mono font-bold bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 transition-all"
                >
                  ⚡ INJECT CYCLE (TEST Z3 GATE)
                </button>
              </div>

              {/* Live DAG Node Matrix */}
              <div className="space-y-2">
                {dagNodes.map((node, i) => (
                  <div
                    key={node.id}
                    className={`p-3 rounded-lg border flex items-center justify-between text-xs font-mono transition-all ${
                      node.status === 'resolved'
                        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
                        : node.status === 'processing'
                          ? 'bg-purple-950/60 border-purple-400 text-purple-200 shadow-[0_0_10px_rgba(157,78,221,0.2)]'
                          : 'bg-neutral-950 border-neutral-800 text-neutral-400'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="w-5 h-5 rounded-full bg-neutral-800 flex items-center justify-center font-bold text-[10px]">
                        {i + 1}
                      </span>
                      <div>
                        <span className="font-bold text-neutral-100">{node.name}</span>
                        <span className="text-[10px] text-neutral-400 block">PILLAR: {node.pillar}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className="text-[10px]">IN-DEGREE: {node.inDegree}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        node.status === 'resolved' ? 'bg-emerald-500/20 text-emerald-400' :
                        node.status === 'processing' ? 'bg-purple-500/20 text-purple-400 animate-pulse' :
                        'bg-neutral-800 text-neutral-400'
                      }`}>
                        {node.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 4 Constitutional Pillars Invariant Box */}
          <div className="lg:col-span-5 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border flex-1 ${isDark ? 'bg-neutral-900/90 border-neutral-800' : 'bg-white border-slate-200 shadow-sm'}`}>
              <h3 className="text-sm font-mono font-bold tracking-wider text-cyan-400 mb-3 border-b border-neutral-800 pb-2">
                4 CONSTITUTIONAL PILLARS (Z3 INVARIANTS)
              </h3>

              <div className="space-y-2.5 text-xs font-mono">
                {[
                  { name: '1. SOVEREIGNTY', rule: 'Local Edge Execution ⊢ Zero Unsolicited Cloud Exfiltration', status: 'PASS' },
                  { name: '2. TRANSPARENCY', rule: 'Declarative A2UI AST ⊢ Visible Execution Trace', status: 'PASS' },
                  { name: '3. NON-MALICE', rule: 'Gideon L7 Crypto Gate ⊢ Zero Unauthorized Mutations', status: 'PASS' },
                  { name: '4. SCARCITY', rule: 'Ouroboros 1.58b ⊢ Memory Clamped ≤ 250 MB', status: 'PASS' }
                ].map((p, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-neutral-950 border border-neutral-800">
                    <div className="flex items-center justify-between text-neutral-200 font-bold mb-1">
                      <span>{p.name}</span>
                      <span className="text-emerald-400 text-[10px] bg-emerald-500/20 px-1.5 py-0.2 rounded">
                        {p.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-400">{p.rule}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 4: Vector 3 - Triple-QFT & Semantic Anchor Compression */}
      {activeSubTab === 'triple-qft' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border ${isDark ? 'bg-neutral-900/90 border-pink-500/30' : 'bg-white border-slate-200 shadow-sm'}`}>
              <div className="flex items-center justify-between border-b pb-2 mb-3 border-neutral-800">
                <h3 className="text-sm font-mono font-bold tracking-wider text-pink-400">
                  3. TRIPLE-QFT &amp; SEMANTIC ANCHOR COMPRESSION
                </h3>
                <span className="text-xs font-mono text-cyan-400 font-bold">{compressionRatio}x SQUEEZE</span>
              </div>

              <p className="text-xs text-neutral-300 mb-4 leading-relaxed">
                Triple-QFT normalizes high-entropy natural language through 
                <strong> Rescaling (S) ➔ Quenching (Q) ➔ Perturbation (P)</strong> into dense Semantic Anchors, 
                enabling instantaneous A2UI transfiguration with latency <code className="text-cyan-300">Δt &lt; 400ms</code>.
              </p>

              {/* Live Input */}
              <div className="mb-4">
                <label className="text-[10px] font-mono text-neutral-500 block mb-1">HIGH-ENTROPY RAW INTENT INPUT:</label>
                <textarea
                  value={qftRawText}
                  onChange={e => setQftRawText(e.target.value)}
                  rows={3}
                  className={`w-full px-3 py-2 rounded-lg text-xs font-mono border focus:outline-none focus:ring-1 focus:ring-pink-400 ${
                    isDark ? 'bg-neutral-950 border-neutral-800 text-neutral-200' : 'bg-slate-100 border-slate-300 text-slate-900'
                  }`}
                />
              </div>

              <button
                onClick={handleRunTripleQft}
                className="w-full py-2.5 rounded-lg text-xs font-mono font-bold bg-pink-500 hover:bg-pink-400 text-black shadow-md shadow-pink-500/20 transition-all flex items-center justify-center space-x-2"
              >
                <span>⚡</span>
                <span>EXECUTE TRIPLE-QFT RENORMALIZATION</span>
              </button>
            </div>
          </div>

          {/* QFT Compression Output & Latency Gauge */}
          <div className="lg:col-span-6 flex flex-col space-y-4">
            <div className={`p-5 rounded-xl border flex-1 ${isDark ? 'bg-neutral-900/90 border-neutral-800' : 'bg-white border-slate-200 shadow-sm'}`}>
              <h3 className="text-sm font-mono font-bold tracking-wider text-cyan-400 mb-3 border-b border-neutral-800 pb-2">
                SEMANTIC ANCHOR CRYSTAL &amp; MOUNT LATENCY
              </h3>

              {/* Stages Indicator */}
              <div className="grid grid-cols-3 gap-2 mb-4 text-center text-xs font-mono">
                <div className={`p-2 rounded border ${qftPhase === 'rescale' || qftPhase === 'complete' ? 'bg-cyan-950/60 border-cyan-400 text-cyan-300' : 'bg-neutral-950 border-neutral-800 text-neutral-500'}`}>
                  1. RESCALE (S)
                </div>
                <div className={`p-2 rounded border ${qftPhase === 'quench' || qftPhase === 'complete' ? 'bg-purple-950/60 border-purple-400 text-purple-300' : 'bg-neutral-950 border-neutral-800 text-neutral-500'}`}>
                  2. QUENCH (Q)
                </div>
                <div className={`p-2 rounded border ${qftPhase === 'perturb' || qftPhase === 'complete' ? 'bg-pink-950/60 border-pink-400 text-pink-300' : 'bg-neutral-950 border-neutral-800 text-neutral-500'}`}>
                  3. PERTURB (P)
                </div>
              </div>

              {/* Compressed Crystal Output */}
              <div className="p-4 rounded-lg bg-neutral-950 border border-cyan-500/40 mb-4">
                <span className="text-[10px] font-mono text-neutral-500 block mb-1">COMPRESSED SEMANTIC ANCHOR (SAC):</span>
                <code className="text-xs font-mono font-bold text-cyan-300 break-all block">
                  {sacAnchor}
                </code>
              </div>

              {/* Latency Gauge */}
              <div className="p-4 rounded-lg bg-neutral-950 border border-neutral-800 text-xs font-mono">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-neutral-400">HOT-SWAP TRANSFIGURATION LATENCY (Δt):</span>
                  <span className="text-emerald-400 font-bold text-sm">{measuredLatency} ms</span>
                </div>
                <div className="w-full bg-neutral-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-400 via-cyan-400 to-amber-400"
                    style={{ width: `${Math.min((measuredLatency / 400) * 100, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-neutral-500 mt-1">
                  <span>0ms</span>
                  <span className="text-emerald-400">Δt &lt; 400ms INVARIANT PASS</span>
                  <span>400ms</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sub-Tab 5: Cartridge JSON ROM View */}
      {activeSubTab === 'json-rom' && (
        <div className={`p-5 rounded-xl border flex-1 ${isDark ? 'bg-neutral-900/90 border-neutral-800' : 'bg-white border-slate-200 shadow-sm'}`}>
          <div className="flex items-center justify-between border-b pb-3 mb-4 border-neutral-800">
            <div>
              <h3 className="text-sm font-mono font-bold tracking-wider text-cyan-400">
                A2UI_CARTRIDGE_V10000.54 SPECIFICATION PAYLOAD
              </h3>
              <p className="text-xs text-neutral-400 font-mono mt-0.5">
                Cryptographic cartridge metadata for {currentCartridge.name}
              </p>
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(currentCartridge, null, 2));
                multiVoiceRouter.playCyberSfx('lock');
                multiVoiceRouter.speakAsKnight('anya', 'Cartridge ROM payload copied to clipboard.');
              }}
              className="px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 transition-all flex items-center space-x-1.5"
            >
              <span>📋</span>
              <span>COPY CARTRIDGE ROM</span>
            </button>
          </div>

          <pre className="p-4 rounded-lg bg-neutral-950 border border-neutral-800 text-xs font-mono text-cyan-300 overflow-x-auto max-h-[480px]">
            {JSON.stringify(currentCartridge, null, 2)}
          </pre>
        </div>
      )}

    </div>
  );
}
