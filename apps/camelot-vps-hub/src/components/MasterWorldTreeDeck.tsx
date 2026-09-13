import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  Volume2, 
  VolumeX, 
  Compass, 
  Maximize2, 
  Minimize2,
  Activity, 
  ShieldCheck, 
  Layers, 
  Terminal, 
  RefreshCw, 
  Zap, 
  Sliders, 
  Eye, 
  EyeOff,
  Radio, 
  Play, 
  RotateCw,
  Cpu,
  Database,
  Network,
  Minus,
  Plus,
  Lock,
  Unlock,
  Key,
  Flame,
  Binary,
  Anchor,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Brain,
  Github,
  ExternalLink
} from 'lucide-react';
import { ThreeWorldTreeScene } from './ThreeWorldTreeScene';
import { audioEngine } from '../utils/audioEngine';
import { MemcastleModal } from './MemcastleModal';
import { TwinBrainsModal } from './TwinBrainsModal';
import { VikingRefractionsModal } from './VikingRefractionsModal';
import confetti from 'canvas-confetti';

interface MasterWorldTreeDeckProps {
  onOpenTerminalModal?: () => void;
}

export const MasterWorldTreeDeck: React.FC<MasterWorldTreeDeckProps> = () => {
  // Sound & Visual Options
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [parallaxEnabled, setParallaxEnabled] = useState(true);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [energyPulseTrigger, setEnergyPulseTrigger] = useState(0);

  // Active Modals
  const [activeModal, setActiveModal] = useState<'memcastle' | 'twin_brains' | 'viking' | 'ouroboros' | 'graphify' | 'eigen_solver' | null>(null);

  // 3D Parallax Mouse tilt state
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  // Telemetry Interactive State
  const [ramUsedGB, setRamUsedGB] = useState(6.24);
  const [isStressTesting, setIsStressTesting] = useState(false);

  // Minimization State for Individual HUD Panels
  const [minimizedPanels, setMinimizedPanels] = useState<Record<string, boolean>>({
    telemetry: false,
    process: false,
    ouroboros: false,
    logs: false,
    graphify: false,
    vfs: false,
    slabs: false,
    commands: false
  });

  // Master HUD Visibility Mode (Full, Cinema, or Minimized All)
  const [cinemaMode, setCinemaMode] = useState(false);

  // Hidden Aspects & Classified Overlays
  const [showHiddenCipher, setShowHiddenCipher] = useState(false);
  const [stealthDrakkarMode, setStealthDrakkarMode] = useState(false);
  const [secretFrequency, setSecretFrequency] = useState(432); // 432Hz -> 528Hz Solfeggio / Root Frequency
  const [classifiedAccessGranted, setClassifiedAccessGranted] = useState(false);

  // Ouroboros Ternary Matrix State (5 rows x 9 cols)
  const [ternaryMatrix, setTernaryMatrix] = useState<number[][]>([
    [-1,  1,  1,  1, -1,  0,  1,  1,  1],
    [-1,  0,  0, -1,  1,  0,  0,  1,  1],
    [-3,  0, -1,  1,  0, -1,  0,  0,  1],
    [-1,  1, -2,  0,  0,  0, -1,  0,  0],
    [-1,  1,  1,  0,  0,  0,  1,  1, -3]
  ]);

  // Graphify Depth Layer
  const [depthLayer, setDepthLayer] = useState(5);

  // VFS Stream Progress Channels
  const [streams, setStreams] = useState([
    { id: 'char', name: 'CHARACTER STATES', progress: 88, speed: '1.2 GB/s' },
    { id: 'prompt', name: 'PROMPT SCAFFOLDING', progress: 95, speed: '840 MB/s' },
    { id: 'dag', name: 'AGENT DAG EXECUTION', progress: 76, speed: '2.1 GB/s' },
    { id: 'hydration', name: 'CONTEXT HYDRATION', progress: 92, speed: '1.8 GB/s' },
    { id: 'sandbox', name: 'SANDBOX BOUNDARY', progress: 100, speed: 'VERIFIED' }
  ]);

  // IPC Memory Slab 32 Bins
  const [slabs, setSlabs] = useState<boolean[]>(
    Array.from({ length: 32 }, (_, i) => i < 24)
  );

  // Process Matrix
  const [processes, setProcesses] = useState([
    { name: 'vkg_world_tree', pid: 31415, cpu: '12.5%', ram: '1.21 GB', status: 'RUNNING' },
    { name: 'ouroboros_ssm', pid: 27182, cpu: '8.2%', ram: '512 MB', status: 'RUNNING' },
    { name: 'open_notebook', pid: 16180, cpu: '7.1%', ram: '1.08 GB', status: 'RUNNING' },
    { name: 'notebooklm_py', pid: 14142, cpu: '6.5%', ram: '896 MB', status: 'RUNNING' },
    { name: 'graphify_engine', pid: 12231, cpu: '5.4%', ram: '732 MB', status: 'RUNNING' },
    { name: 'vfs_refractions', pid: 10001, cpu: '3.2%', ram: '420 MB', status: 'RUNNING' },
    { name: 'mem_palace', pid: 8888, cpu: '2.1%', ram: '256 MB', status: 'RUNNING' }
  ]);

  // Terminal Log Lines
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    '[12:00:01] WORLD_TREE_BOOTSTRAP... OK',
    '[12:00:01] MEMCASTLE_LINK (/vfs/mempalace/*)... OK (0.18ms)',
    '[12:00:01] OUROBOROS_SSM (1.58-bit ternary W_ij)... OK',
    '[12:00:02] TWIN_BRAINS_SYNC (Open-Notebook <-> NotebookLM)... OK',
    '[12:00:02] VFS_REFRACTIONS (/vfs/refractions/*)... OK (DMA 12μs)',
    '[12:00:02] GRAPHIFY_ENGINE (3D Spatial Network L1-L7)... OK',
    '[12:00:03] SYSTEM ONLINE // AXIS MUNDI CONVERGED'
  ]);
  const [cmdInput, setCmdInput] = useState('');

  // Oscilloscope Canvas for Utilization Over Time
  const waveCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // Sound Engine Sync
  useEffect(() => {
    audioEngine.setEnabled(soundEnabled);
  }, [soundEnabled]);

  // Continuous Waveform Animation in Telemetry Panel
  useEffect(() => {
    const canvas = waveCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let offset = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      offset += 0.04;

      ctx.beginPath();
      ctx.strokeStyle = showHiddenCipher ? '#f59e0b' : '#34d399';
      ctx.lineWidth = 1.6;
      ctx.shadowBlur = 6;
      ctx.shadowColor = showHiddenCipher ? '#d97706' : '#10b981';

      const w = canvas.width;
      const h = canvas.height;

      for (let x = 0; x < w; x++) {
        const y = h * 0.5 + Math.sin(x * 0.08 + offset) * 12 + Math.sin(x * 0.2 - offset * 1.5) * 5;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [showHiddenCipher]);

  // Parallax tracking
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!parallaxEnabled) return;
    const { clientX, clientY, currentTarget } = e;
    const rect = currentTarget.getBoundingClientRect();
    const xRatio = (clientX - rect.left) / rect.width - 0.5;
    const yRatio = (clientY - rect.top) / rect.height - 0.5;
    setTilt({ x: xRatio * 6, y: -yRatio * 6 });
  };

  // Toggle Matrix Cell
  const handleCellClick = (r: number, c: number) => {
    audioEngine.playHoverBeep();
    setTernaryMatrix((prev) => {
      const next = prev.map((row) => [...row]);
      const val = next[r][c];
      next[r][c] = val === 1 ? -1 : val === -1 ? 0 : 1;
      return next;
    });
  };

  // Ouroboros State Pulse Trigger
  const handleOuroborosTrigger = () => {
    audioEngine.playStatePulse();
    setEnergyPulseTrigger((prev) => prev + 1);
    setTerminalLogs((prev) => [
      ...prev.slice(-12),
      `[${new Date().toLocaleTimeString()}] OUROBOROS_SSM_CYCLE: 1.58-bit state transition converged (0.04ms)`
    ]);
  };

  // Toggle Individual Panel Minimization
  const togglePanel = (panelId: string) => {
    audioEngine.playClick();
    setMinimizedPanels((prev) => {
      const nextState = !prev[panelId];
      const panelName = panelId.toUpperCase();
      setTerminalLogs((p) => [
        ...p.slice(-12),
        `[${new Date().toLocaleTimeString()}] HUD_PANEL [${panelName}]: ${nextState ? 'MINIMIZED' : 'RESTORED'}`
      ]);
      return {
        ...prev,
        [panelId]: nextState
      };
    });
  };

  // Master Minimize All / Restore All
  const handleToggleAllPanels = () => {
    audioEngine.playClick();
    const allMin = Object.values(minimizedPanels).every(Boolean);
    const newState = !allMin;
    setMinimizedPanels({
      telemetry: newState,
      process: newState,
      ouroboros: newState,
      logs: newState,
      graphify: newState,
      vfs: newState,
      slabs: newState,
      commands: newState
    });
    setTerminalLogs((prev) => [
      ...prev.slice(-12),
      `[${new Date().toLocaleTimeString()}] HUD_MASTER: ${newState ? 'ALL 8 PANELS MINIMIZED TO DOCK' : 'ALL 8 PANELS RESTORED TO VIEWPORT'}`
    ]);
  };

  // Keyboard shortcut listener (H for HUD toggle, C for Cinema toggle)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing inside input
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) return;
      if (e.key === 'h' || e.key === 'H') {
        handleToggleAllPanels();
      } else if (e.key === 'c' || e.key === 'C') {
        audioEngine.playClick();
        setCinemaMode((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [minimizedPanels]);

  // Execute Command Action
  const executeCommand = (cmd: string) => {
    audioEngine.playCommandExecute();
    const time = new Date().toLocaleTimeString();
    
    if (cmd.includes('INIT_WORLD_TREE')) {
      setEnergyPulseTrigger((p) => p + 1);
      confetti({ particleCount: 40, spread: 60, origin: { y: 0.5 } });
      setTerminalLogs((p) => [...p.slice(-12), `[${time}] > INIT_WORLD_TREE: Axis Mundi calibrated. All 28 VFS nodes verified.`]);
    } else if (cmd.includes('SYNC_ALL_ENGINES')) {
      audioEngine.playBrainSync();
      setEnergyPulseTrigger((p) => p + 1);
      setTerminalLogs((p) => [...p.slice(-12), `[${time}] > SYNC_ALL_ENGINES: Open-Notebook <-> NotebookLM synchronized (0.12ms).`]);
    } else if (cmd.includes('FLUSH_CONTEXT')) {
      setTerminalLogs((p) => [...p.slice(-12), `[${time}] > FLUSH_CONTEXT: Memory palaces pruned. 412 MB reclaimed.`]);
      setRamUsedGB(5.82);
    } else if (cmd.includes('OPTIMIZE_MEMORY')) {
      setIsStressTesting(true);
      setTimeout(() => {
        setIsStressTesting(false);
        setRamUsedGB(5.12);
        setTerminalLogs((p) => [...p.slice(-12), `[${time}] > OPTIMIZE_MEMORY: Z3 invariant solver compacted cgroup memory.`]);
      }, 1000);
    } else if (cmd.includes('RUN_DIAGNOSTICS')) {
      setTerminalLogs((p) => [...p.slice(-12), `[${time}] > RUN_DIAGNOSTICS: All systems nominal. 100% Invariant SAT satisfied.`]);
    } else if (cmd.includes('SECRET_CIPHER') || cmd.includes('CLASSIFIED')) {
      setShowHiddenCipher(true);
      setClassifiedAccessGranted(true);
      setTerminalLogs((p) => [...p.slice(-12), `[${time}] > [CLASSIFIED CIPHER]: Quantum Singularity Matrix & Root Invariants unlocked.`]);
    } else {
      setTerminalLogs((p) => [...p.slice(-12), `[${time}] > ${cmd}: Command dispatched successfully.`]);
    }
  };

  // Custom Console Input Handler
  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cmdInput.trim()) return;
    executeCommand(cmdInput.toUpperCase());
    setCmdInput('');
  };

  // Toggle Slabs
  const handleToggleSlab = (index: number) => {
    audioEngine.playHoverBeep();
    setSlabs((prev) => {
      const next = [...prev];
      next[index] = !next[index];
      return next;
    });
  };

  const countMinimized = Object.values(minimizedPanels).filter(Boolean).length;

  return (
    <div 
      className="relative w-full min-h-screen bg-[#030712] text-slate-100 overflow-x-hidden select-none font-mono"
      onMouseMove={handleMouseMove}
    >
      {/* Top Floating Control Bar */}
      <div className="relative z-40 bg-slate-950/90 border-b border-cyan-950 px-4 py-2 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-bold text-cyan-300 tracking-wider">CAMELOT-OS // 3D WORLD TREE HUD</span>
          </div>
          <span className="text-slate-500">|</span>
          <span className="text-amber-300/90 text-[11px]">2D BACKGROUND UI + 3D ANIMATION ENGINE</span>
          {countMinimized > 0 && (
            <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold">
              {countMinimized} PANELS MINIMIZED
            </span>
          )}
        </div>

        {/* Action Toggles */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Master Minimize / Restore All HUD Panels */}
          <button
            id="btn-minimize-all-hud"
            onClick={handleToggleAllPanels}
            className={`px-3 py-1 rounded border text-[11px] font-bold flex items-center gap-1.5 transition-all active:scale-95 ${
              countMinimized === 8
                ? 'bg-amber-950/80 border-amber-400 text-amber-200 shadow-[0_0_12px_rgba(245,158,11,0.4)] animate-pulse'
                : countMinimized > 0
                ? 'bg-slate-900 border-cyan-400 text-cyan-200'
                : 'bg-slate-900 border-cyan-500/40 hover:border-cyan-400 text-cyan-300 hover:bg-slate-800'
            }`}
            title={countMinimized === 8 ? "Restore all HUD panels (Hotkeys: H)" : "Minimize all HUD panels (Hotkeys: H)"}
          >
            {countMinimized === 8 ? <Maximize2 className="w-3.5 h-3.5 text-amber-400" /> : <Minimize2 className="w-3.5 h-3.5 text-cyan-400" />}
            <span>{countMinimized === 8 ? 'RESTORE ALL HUD' : 'MINIMIZE ALL HUD'}</span>
            <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/50 text-slate-400 border border-slate-700">
              {countMinimized}/8
            </span>
          </button>

          {/* Open-Notebook Studio Launcher */}
          <button
            onClick={() => {
              audioEngine.playBrainSync();
              setActiveModal('twin_brains');
            }}
            className="px-2.5 py-1 rounded bg-purple-950/80 hover:bg-purple-900 border border-purple-500/50 text-purple-200 text-[10px] font-bold flex items-center gap-1.5 transition-all shadow-[0_0_12px_rgba(192,132,252,0.3)]"
            title="Launch Open-Notebook & Twin Quantum Brains Studio"
          >
            <Brain className="w-3.5 h-3.5 text-purple-300" />
            <span>OPEN-NOTEBOOK</span>
          </button>

          {/* GitHub Repo Direct Link */}
          <a
            href="https://github.com/lfnovo/open-notebook.git"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-purple-900/60 text-purple-300 text-[10px] transition-all"
            title="Open-Notebook GitHub Repository (lfnovo/open-notebook)"
          >
            <Github className="w-3 h-3 text-purple-400" />
            <span>lfnovo/open-notebook</span>
            <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
          </a>

          {/* Cinema / Clean Mode Toggle */}
          <button
            onClick={() => {
              audioEngine.playClick();
              setCinemaMode(!cinemaMode);
            }}
            className={`px-2.5 py-1 rounded border text-[10px] flex items-center gap-1.5 transition-all ${
              cinemaMode 
                ? 'bg-purple-950 border-purple-400 text-purple-200 shadow-[0_0_12px_rgba(168,85,247,0.4)]' 
                : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
            title="Toggle Clean Cinema View (Hide all overlays for pure 3D art inspection)"
          >
            {cinemaMode ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            <span>{cinemaMode ? 'CINEMA ACTIVE' : 'CINEMA VIEW'}</span>
          </button>

          {/* HIDDEN ASPECT 1: Quantum Holographic Cipher & Singularity Protocol */}
          <button
            onClick={() => {
              audioEngine.playStatePulse();
              setShowHiddenCipher(!showHiddenCipher);
              if (!showHiddenCipher) {
                confetti({ particleCount: 30, spread: 70, origin: { y: 0.6 } });
              }
            }}
            className={`px-2.5 py-1 rounded border text-[10px] flex items-center gap-1.5 transition-all ${
              showHiddenCipher 
                ? 'bg-amber-950 border-amber-400 text-amber-200 shadow-[0_0_15px_rgba(245,158,11,0.5)] animate-pulse' 
                : 'bg-slate-900 border-amber-900/60 text-amber-400/80 hover:text-amber-300'
            }`}
            title="Classified: Reveal Quantum Holographic Cipher & Root Singularity Matrix"
          >
            <Key className="w-3.5 h-3.5 text-amber-400" />
            <span>{showHiddenCipher ? 'CIPHER: DECRYPTED' : '[CLASSIFIED CIPHER]'}</span>
          </button>

          {/* HIDDEN ASPECT 2: Stealth Drakkar Cloaking Mode */}
          <button
            onClick={() => {
              audioEngine.playClick();
              setStealthDrakkarMode(!stealthDrakkarMode);
            }}
            className={`px-2.5 py-1 rounded border text-[10px] flex items-center gap-1.5 transition-all ${
              stealthDrakkarMode 
                ? 'bg-emerald-950 border-emerald-400 text-emerald-200 shadow-[0_0_12px_rgba(16,185,129,0.4)]' 
                : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-emerald-300'
            }`}
            title="Classified: Activate Sovereign Viking Drakkar Stealth Cloaking"
          >
            <Anchor className="w-3.5 h-3.5" />
            <span>STEALTH DRAKKAR: {stealthDrakkarMode ? 'CLOAKED' : 'STANDARD'}</span>
          </button>

          {/* Sound Toggle */}
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`px-2.5 py-1 rounded border text-[10px] flex items-center gap-1.5 transition-all ${
              soundEnabled 
                ? 'bg-cyan-950/80 border-cyan-500 text-cyan-300' 
                : 'bg-slate-900 border-slate-700 text-slate-500'
            }`}
            title="Toggle Web Audio Synthesizer"
          >
            {soundEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
            <span>AUDIO FX: {soundEnabled ? 'ON' : 'OFF'}</span>
          </button>

          {/* 3D Parallax Tilt Toggle */}
          <button
            onClick={() => setParallaxEnabled(!parallaxEnabled)}
            className={`px-2.5 py-1 rounded border text-[10px] flex items-center gap-1.5 transition-all ${
              parallaxEnabled 
                ? 'bg-amber-950/80 border-amber-500 text-amber-300' 
                : 'bg-slate-900 border-slate-700 text-slate-500'
            }`}
            title="Toggle 3D Cursor Parallax"
          >
            <Compass className="w-3.5 h-3.5" />
            <span>3D DEPTH: {parallaxEnabled ? 'ACTIVE' : 'LOCKED'}</span>
          </button>

          {/* Trigger State Pulse */}
          <button
            onClick={handleOuroborosTrigger}
            className="px-2.5 py-1 rounded bg-emerald-950/80 border border-emerald-500/60 hover:border-emerald-400 text-emerald-300 hover:text-emerald-200 text-[10px] flex items-center gap-1.5 active:scale-95 transition-all"
            title="Fire 3D State Pulse through Yggdrasil"
          >
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            <span>PULSE SSM</span>
          </button>
        </div>
      </div>

      {/* Main 3D Canvas / 2D UI Container */}
      <div 
        className="relative w-full max-w-[1720px] mx-auto p-2 md:p-4 transition-transform duration-300 ease-out"
        style={{
          perspective: '1200px',
          transform: parallaxEnabled ? `rotateX(${tilt.y}deg) rotateY(${tilt.x}deg)` : 'none'
        }}
      >
        {/* ================= BACKGROUND 2D UI IMAGE LAYER ================= */}
        <div className="relative w-full aspect-[16/9] min-h-[760px] rounded-2xl overflow-hidden border border-cyan-900/50 shadow-[0_0_50px_rgba(34,211,238,0.15)] bg-slate-950">
          
          {/* 1. Master Reference Concept Artwork as Background */}
          <img 
            src="https://i.postimg.cc/Lssx07X3/1787629062694-01a036fd-ed60-74c1-b1c7-5e5177f9ba69.png"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).src = '/1787629062694-01a036fd-ed60-74c1-b1c7-5e5177f9ba69.png';
            }}
            alt="Camelot-OS Sovereign World Tree Control Center"
            referrerPolicy="no-referrer"
            onLoad={() => setImageLoaded(true)}
            className={`absolute inset-0 w-full h-full object-cover object-center pointer-events-none z-0 transition-all duration-700 ${
              stealthDrakkarMode ? 'brightness-75 contrast-125 hue-rotate-15' : 'brightness-95 contrast-105'
            }`}
          />

          {/* Fallback & Enhanced Ambient Backdrop Glows */}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-slate-950/40 pointer-events-none z-10" />

          {/* 2. THREE.JS 3D WEBGL ANIMATION SCENE OVERLAY */}
          <ThreeWorldTreeScene 
            energyPulseTrigger={energyPulseTrigger}
            depthLayer={depthLayer}
            onHotspotClick={(zone) => {
              if (zone === 'memcastle') setActiveModal('memcastle');
              if (zone === 'brains') setActiveModal('twin_brains');
              if (zone === 'viking') setActiveModal('viking');
            }}
          />

          {/* ================= HIDDEN ASPECT: QUANTUM SINGULARITY & RUNIC CIPHER OVERLAY ================= */}
          {showHiddenCipher && (
            <div className="absolute inset-0 z-25 pointer-events-auto bg-amber-950/20 backdrop-blur-[2px] border-4 border-amber-500/40 animate-fadeIn flex flex-col justify-between p-6">
              <div className="flex items-center justify-between bg-black/80 border border-amber-500/60 rounded-xl px-4 py-2 text-amber-300">
                <div className="flex items-center gap-2">
                  <Flame className="w-5 h-5 text-amber-400 animate-pulse" />
                  <span className="font-bold text-sm tracking-widest uppercase">
                    YGGDRASIL QUANTUM ROOT SINGULARITY // ZERO-POINT ENERGY MATRIX
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span>ROOT FREQUENCY: <strong className="text-white">{secretFrequency} Hz</strong></span>
                  <span>CORE TEMP: <strong className="text-cyan-300">0.042 K</strong></span>
                  <span>Z3 INVARIANTS: <strong className="text-emerald-400">100% FORMAL SAT</strong></span>
                  <button
                    onClick={() => setSecretFrequency(prev => prev === 432 ? 528 : prev === 528 ? 963 : 432)}
                    className="px-2 py-0.5 rounded bg-amber-900/60 border border-amber-400 text-[10px] text-amber-200 hover:bg-amber-800"
                  >
                    CYCLE SOLFEGGIO
                  </button>
                </div>
              </div>

              {/* Runic Math Overlay Matrix */}
              <div className="grid grid-cols-3 gap-6 my-auto">
                <div className="p-4 rounded-xl bg-black/75 border border-amber-500/40 text-xs space-y-2 text-amber-200">
                  <div className="font-bold text-amber-400 border-b border-amber-500/30 pb-1">AXIS MUNDI ENTANGLEMENT</div>
                  <p className="text-[11px] font-mono text-slate-300">
                    |Ψ⟩ = 1/√2 (|00⟩ + |11⟩) ⊗ |VFS_DMA⟩
                  </p>
                  <p className="text-[10px] text-slate-400">
                    Zero-copy quantum memory bridge linking /vfs/mempalace with Open-Notebook cognitive buffers.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-black/75 border border-cyan-500/40 text-xs space-y-2 text-cyan-200">
                  <div className="font-bold text-cyan-400 border-b border-cyan-500/30 pb-1">OUROBOROS TERNARY EIGENSPACE</div>
                  <p className="text-[11px] font-mono text-slate-300">
                    det(W_ij - λI) = 0, with W_ij ∈ &#123;-1, 0, 1&#125;
                  </p>
                  <p className="text-[10px] text-slate-400">
                    Recurrent state compression achieves 1.58-bit lossless state storage across all 8GB partitions.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-black/75 border border-emerald-500/40 text-xs space-y-2 text-emerald-200">
                  <div className="font-bold text-emerald-400 border-b border-emerald-500/30 pb-1">ARTHUR R5/R6 CRYPTOGRAPHIC PROOF</div>
                  <p className="text-[11px] font-mono text-slate-300">
                    SHA256(Block#850 ⊕ WAL2_Seal) = 0x8f74...e3902
                  </p>
                  <p className="text-[10px] text-slate-400">
                    Sovereign constitutional invariants validated by Z3 SMT solver.
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] text-amber-400/80 bg-black/80 px-4 py-1.5 rounded-lg border border-amber-500/30">
                <span>[CLASSIFIED_OVERRIDE_ENABLED]: All sub-quantum memory barriers verified.</span>
                <button
                  onClick={() => setShowHiddenCipher(false)}
                  className="text-white hover:text-amber-300 underline text-xs"
                >
                  Close Cipher Overlay
                </button>
              </div>
            </div>
          )}

          {/* ================= 3. INTERACTIVE HOTSPOTS & HUD PANELS ================= */}
          {!cinemaMode && (
            <>
              {/* --- TOP LEFT: HEADER & STATUS --- */}
              <div className="absolute top-4 left-4 z-30 flex items-center gap-3">
                <div className="bg-slate-950/85 backdrop-blur-md border border-cyan-900/80 px-3.5 py-2 rounded-xl shadow-lg flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-cyan-950/80 border border-cyan-400 flex items-center justify-center text-cyan-300">
                    <ShieldCheck className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h1 className="text-sm font-bold text-amber-200 tracking-wider">
                      Camelot-OS World Tree
                    </h1>
                    <span className="text-[10px] text-cyan-400 block tracking-wider">
                      THE SOVEREIGN CONTEXT ENGINE
                    </span>
                  </div>
                </div>

                <div className="bg-slate-950/85 backdrop-blur-md border border-emerald-900/80 px-3 py-1.5 rounded-xl shadow-lg flex items-center gap-2 text-[11px]">
                  <span className="text-slate-400">SYSTEM STATUS:</span>
                  <span className="text-emerald-400 font-bold tracking-wider">NOMINAL</span>
                </div>
              </div>

              {/* --- UPPER LEFT: SYSTEM TELEMETRY (8GB RAM // REAL-TIME) --- */}
              <div className={`absolute top-20 left-4 z-30 w-72 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.telemetry 
                  ? 'border-cyan-900/40 bg-slate-950/60 p-2' 
                  : 'border-cyan-900/80 hover:border-cyan-400/80'
              }`}>
                <div className="flex items-center justify-between border-b border-cyan-950/90 pb-1.5 mb-2">
                  <div className="flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">SYSTEM TELEMETRY</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-400">{minimizedPanels.telemetry ? `${ramUsedGB.toFixed(1)}GB` : '8GB RAM'}</span>
                    <button
                      onClick={() => togglePanel('telemetry')}
                      className="p-1 rounded bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.telemetry ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.telemetry ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.telemetry && (
                  <div className="grid grid-cols-2 gap-2 items-center">
                    {/* Donut Gauge */}
                    <div className="flex flex-col items-center">
                      <div className="relative w-16 h-16 flex items-center justify-center">
                        <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                          <circle cx="18" cy="18" r="14" fill="none" stroke="#1e293b" strokeWidth="3" />
                          <circle
                            cx="18" cy="18" r="14"
                            fill="none"
                            stroke="#f59e0b"
                            strokeWidth="3.2"
                            strokeDasharray="88"
                            strokeDashoffset={88 - (88 * (ramUsedGB / 8))}
                            strokeLinecap="round"
                            className="transition-all duration-500"
                          />
                        </svg>
                        <div className="absolute flex flex-col items-center justify-center">
                          <span className="text-xs font-bold text-amber-300">{Math.round((ramUsedGB / 8) * 100)}%</span>
                        </div>
                      </div>
                      <span className="text-[9px] text-slate-300 mt-1 font-bold">{ramUsedGB.toFixed(2)} GB USED</span>
                      <span className="text-[8px] text-slate-500">8.00 GB TOTAL</span>
                    </div>

                    {/* Live Oscilloscope Wave */}
                    <div className="flex flex-col justify-between h-full">
                      <div className="flex items-center justify-between text-[9px] text-slate-400">
                        <span>UTILIZATION</span>
                        <span className="text-emerald-400">60s</span>
                      </div>
                      <div className="h-12 w-full bg-slate-900/80 rounded border border-emerald-900/50 overflow-hidden relative">
                        <canvas ref={waveCanvasRef} width={120} height={48} className="w-full h-full" />
                      </div>
                      <button
                        onClick={() => executeCommand('OPTIMIZE_MEMORY')}
                        className="mt-1 px-2 py-0.5 rounded bg-amber-950/60 border border-amber-500/40 hover:border-amber-400 text-amber-300 text-[9px] text-center w-full active:scale-95 transition-all"
                      >
                        {isStressTesting ? 'RECLAIMING...' : 'GC TRIM RAM'}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* --- MIDDLE LEFT: PROCESS MATRIX --- */}
              <div className={`absolute ${minimizedPanels.telemetry ? 'top-32' : 'top-64'} left-4 z-30 w-72 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.process 
                  ? 'border-cyan-900/40 bg-slate-950/60 p-2' 
                  : 'border-cyan-900/80 hover:border-cyan-400/80'
              }`}>
                <div className="flex items-center justify-between border-b border-cyan-950/90 pb-1 mb-2">
                  <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">PROCESS MATRIX</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-emerald-400">7 ACTIVE</span>
                    <button
                      onClick={() => togglePanel('process')}
                      className="p-1 rounded bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.process ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.process ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.process && (
                  <div className="space-y-1 text-[9px]">
                    <div className="grid grid-cols-4 text-slate-500 border-b border-slate-800/80 pb-0.5 font-bold">
                      <span>PROCESS</span>
                      <span className="text-right">PID</span>
                      <span className="text-right">CPU%</span>
                      <span className="text-right">RAM</span>
                    </div>
                    {processes.map((proc) => (
                      <div 
                        key={proc.name}
                        onClick={() => {
                          audioEngine.playHoverBeep();
                          setTerminalLogs((p) => [...p.slice(-12), `[${new Date().toLocaleTimeString()}] INSPECT_PID: ${proc.name} (${proc.pid}) -> CPU: ${proc.cpu}, RAM: ${proc.ram}`]);
                        }}
                        className="grid grid-cols-4 text-slate-300 hover:text-cyan-200 hover:bg-cyan-950/40 px-1 py-0.5 rounded cursor-pointer transition-colors"
                      >
                        <span className="truncate text-cyan-400">{proc.name}</span>
                        <span className="text-right text-slate-400">{proc.pid}</span>
                        <span className="text-right text-amber-400">{proc.cpu}</span>
                        <span className="text-right text-emerald-400">{proc.ram}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* --- LOWER LEFT: OUROBOROS SSM STATE TRANSITIONS --- */}
              <div className={`absolute ${
                minimizedPanels.telemetry && minimizedPanels.process 
                  ? 'top-44' 
                  : minimizedPanels.process 
                  ? 'top-56' 
                  : 'top-[425px]'
              } left-4 z-30 w-72 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.ouroboros 
                  ? 'border-amber-900/40 bg-slate-950/60 p-2' 
                  : 'border-amber-900/80 hover:border-amber-400/80'
              }`}>
                <div className="flex items-center justify-between border-b border-amber-950/90 pb-1 mb-2">
                  <span className="text-xs font-bold text-amber-300 uppercase tracking-wider">OUROBOROS SSM</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-slate-400">1.58-BIT TERNARY</span>
                    <button
                      onClick={() => togglePanel('ouroboros')}
                      className="p-1 rounded bg-slate-900 hover:bg-amber-950 text-slate-400 hover:text-amber-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.ouroboros ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.ouroboros ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.ouroboros && (
                  <>
                    <div className="flex items-center gap-3">
                      {/* Clickable Ternary Matrix */}
                      <div className="grid grid-cols-9 gap-1 bg-slate-900/90 p-1.5 rounded border border-amber-950/80">
                        {ternaryMatrix.map((row, r) =>
                          row.map((val, c) => (
                            <button
                              key={`${r}-${c}`}
                              onClick={() => handleCellClick(r, c)}
                              className={`w-3.5 h-3.5 text-[9px] font-bold rounded flex items-center justify-center transition-all ${
                                val === 1 
                                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/50' 
                                  : val === -1 
                                  ? 'bg-rose-950 text-rose-300 border border-rose-500/50' 
                                  : 'bg-slate-800 text-slate-400 border border-slate-700'
                              }`}
                            >
                              {val}
                            </button>
                          ))
                        )}
                      </div>

                      {/* Golden Ouroboros Emblem with State Trigger */}
                      <div 
                        onClick={handleOuroborosTrigger}
                        className="flex flex-col items-center justify-center cursor-pointer group"
                        title="Click to cycle Ouroboros SSM state loop"
                      >
                        <div className="w-12 h-12 rounded-full border border-amber-400/60 p-1 flex items-center justify-center bg-amber-950/40 group-hover:scale-110 group-hover:border-amber-300 transition-all">
                          <RotateCw className="w-6 h-6 text-amber-300 group-hover:rotate-180 transition-transform duration-700" />
                        </div>
                        <span className="text-[8px] text-amber-300/80 mt-1">CYCLE</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[9px] text-slate-400 mt-2 border-t border-slate-800/80 pt-1">
                      <span>STATE CYCLE: <strong className="text-amber-300">1.58 BITS</strong></span>
                      <span>RECURRENCE: <strong className="text-emerald-400">STABLE</strong></span>
                    </div>
                  </>
                )}
              </div>

              {/* --- BOTTOM LEFT: SYSTEM LOG PANEL --- */}
              <div className={`absolute bottom-4 left-4 z-30 w-80 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.logs 
                  ? 'border-cyan-900/40 bg-slate-950/60 p-2' 
                  : 'border-cyan-900/80'
              }`}>
                <div className="flex items-center justify-between border-b border-cyan-950/90 pb-1 mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">SYSTEM LOG</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {!minimizedPanels.logs && (
                      <button
                        onClick={() => setTerminalLogs([])}
                        className="text-[9px] text-slate-500 hover:text-slate-300"
                      >
                        CLEAR
                      </button>
                    )}
                    <button
                      onClick={() => togglePanel('logs')}
                      className="p-1 rounded bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.logs ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.logs ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.logs && (
                  <>
                    <div className="h-20 overflow-y-auto space-y-0.5 text-[9px] font-mono text-slate-300 custom-scrollbar pr-1">
                      {terminalLogs.map((log, i) => (
                        <div key={i} className="leading-tight">
                          <span className="text-cyan-400">{log.slice(0, 10)}</span>
                          <span className={log.includes('OK') ? 'text-emerald-300' : 'text-amber-300'}>
                            {log.slice(10)}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Custom Input */}
                    <form onSubmit={handleInputSubmit} className="mt-1.5 flex items-center gap-1 border-t border-slate-800/80 pt-1">
                      <span className="text-cyan-400 text-[10px]">&gt;</span>
                      <input
                        type="text"
                        value={cmdInput}
                        onChange={(e) => setCmdInput(e.target.value)}
                        placeholder="Enter command (e.g. SYNC, SECRET_CIPHER)..."
                        className="w-full bg-transparent text-[9px] text-slate-200 focus:outline-none placeholder:text-slate-600"
                      />
                    </form>
                  </>
                )}
              </div>

              {/* --- CENTER INTERACTIVE HOTSPOTS --- */}
              
              {/* APEX: REDIS MEMCASTLE HOTSPOT */}
              <div
                onClick={() => {
                  audioEngine.playClick();
                  setActiveModal('memcastle');
                }}
                className="absolute top-[4%] left-[42%] w-[16%] h-[16%] z-30 cursor-pointer rounded-2xl group hover:border border-cyan-400/50 flex flex-col items-center justify-center transition-all"
                title="Inspect Redis Memcastle (/vfs/mempalace/*)"
              >
                <div className="bg-slate-950/80 border border-cyan-400/80 px-2.5 py-1 rounded-lg text-[9px] text-cyan-200 shadow-[0_0_20px_rgba(34,211,238,0.5)] group-hover:scale-105 transition-all">
                  <span className="font-bold">REDIS MEMCASTLE</span>
                  <span className="block text-[8px] text-amber-300">/vfs/mempalace/*</span>
                </div>
              </div>

              {/* LEFT BRAIN: OPEN-NOTEBOOK (DEEP REASONING ENGINE) HOTSPOT */}
              <div
                onClick={() => {
                  audioEngine.playBrainSync();
                  setActiveModal('twin_brains');
                }}
                className="absolute top-[38%] left-[22%] w-[15%] h-[20%] z-30 cursor-pointer rounded-2xl group hover:border border-purple-400/50 flex flex-col items-center justify-center transition-all"
                title="Inspect Open-Notebook (https://github.com/lfnovo/open-notebook.git)"
              >
                <div className="bg-slate-950/90 border border-purple-400/80 px-2.5 py-1 rounded-lg text-[9px] text-purple-200 shadow-[0_0_20px_rgba(192,132,252,0.5)] group-hover:scale-105 transition-all text-center">
                  <span className="font-bold block">OPEN-NOTEBOOK</span>
                  <span className="text-[8px] text-purple-300 block">lfnovo/open-notebook</span>
                  <span className="text-[7px] px-1 rounded bg-purple-950 text-cyan-300 border border-purple-800">PORT 8502</span>
                </div>
              </div>

              {/* RIGHT BRAIN: NOTEBOOKLM (LOGICAL SYNCHRONIZER) HOTSPOT */}
              <div
                onClick={() => {
                  audioEngine.playBrainSync();
                  setActiveModal('twin_brains');
                }}
                className="absolute top-[38%] right-[22%] w-[15%] h-[20%] z-30 cursor-pointer rounded-2xl group hover:border border-sky-400/50 flex flex-col items-center justify-center transition-all"
                title="Inspect NotebookLM (Logical Synchronizer)"
              >
                <div className="bg-slate-950/85 border border-sky-400/80 px-2.5 py-1 rounded-lg text-[9px] text-sky-200 shadow-[0_0_20px_rgba(56,189,248,0.5)] group-hover:scale-105 transition-all text-center">
                  <span className="font-bold block">NOTEBOOKLM</span>
                  <span className="text-[8px] text-sky-300">LOGICAL SYNCHRONIZER</span>
                </div>
              </div>

              {/* CENTER TRUNK: OUROBOROS STATE LOOP HOTSPOT */}
              <div
                onClick={handleOuroborosTrigger}
                className="absolute top-[48%] left-[44%] w-[12%] h-[18%] z-30 cursor-pointer rounded-xl group hover:border border-amber-400/50 flex flex-col items-center justify-center transition-all"
                title="Click to trigger Ouroboros O(1) State Loop"
              >
                <div className="bg-slate-950/85 border border-amber-400/80 px-2.5 py-1 rounded-lg text-[9px] text-amber-200 shadow-[0_0_20px_rgba(251,191,36,0.5)] group-hover:scale-105 transition-all text-center">
                  <span className="font-bold block text-amber-300">O(1) STATE LOOP</span>
                  <span className="text-[8px] text-slate-300">OUROBOROS SSM</span>
                </div>
              </div>

              {/* BASE: EMERALD DATA RIVERS & VIKING DRAKKAR HOTSPOT */}
              <div
                onClick={() => {
                  audioEngine.playClick();
                  setActiveModal('viking');
                }}
                className="absolute bottom-[8%] left-[35%] w-[30%] h-[16%] z-30 cursor-pointer rounded-2xl group hover:border border-emerald-400/50 flex flex-col items-center justify-center transition-all"
                title="Inspect Open Viking Protocol & Emerald Rivers"
              >
                <div className="bg-slate-950/85 border border-emerald-400/80 px-3 py-1 rounded-lg text-[9px] text-emerald-200 shadow-[0_0_20px_rgba(52,211,153,0.5)] group-hover:scale-105 transition-all text-center">
                  <span className="font-bold block text-emerald-300">EMERALD DATA RIVERS</span>
                  <span className="text-[8px] text-cyan-300">VIKING DRAKKAR // DMA BUFFERS</span>
                </div>
              </div>

              {/* --- TOP RIGHT: GRAPHIFY 3D->2D DEPTH SPATIAL NETWORK --- */}
              <div className={`absolute top-4 right-4 z-30 w-76 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.graphify 
                  ? 'border-cyan-900/40 bg-slate-950/60 p-2' 
                  : 'border-cyan-900/80 hover:border-cyan-400/80'
              }`}>
                <div className="flex items-center justify-between border-b border-cyan-950/90 pb-1 mb-1.5">
                  <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">GRAPHIFY NETWORK</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-slate-400">L{depthLayer}</span>
                    <button
                      onClick={() => togglePanel('graphify')}
                      className="p-1 rounded bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.graphify ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.graphify ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.graphify && (
                  <>
                    {/* Depth Slider */}
                    <div className="space-y-1 my-1.5">
                      <div className="flex items-center justify-between text-[9px] text-slate-400">
                        <span>DEPTH LAYER</span>
                        <span className="text-amber-300 font-bold">L{depthLayer} (1.0 to 7.0)</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="7"
                        step="1"
                        value={depthLayer}
                        onChange={(e) => {
                          audioEngine.playHoverBeep();
                          setDepthLayer(parseInt(e.target.value));
                        }}
                        className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                      />
                    </div>

                    {/* Topology Metrics */}
                    <div className="grid grid-cols-4 gap-1 text-[9px] text-center border-t border-slate-800/80 pt-1.5">
                      <div className="bg-slate-900/80 p-1 rounded border border-slate-800">
                        <span className="text-slate-500 block text-[8px]">TOTAL NODES</span>
                        <span className="text-cyan-300 font-bold">10,428</span>
                      </div>
                      <div className="bg-slate-900/80 p-1 rounded border border-slate-800">
                        <span className="text-slate-500 block text-[8px]">ACTIVE PATHS</span>
                        <span className="text-emerald-300 font-bold">1,284</span>
                      </div>
                      <div className="bg-slate-900/80 p-1 rounded border border-slate-800">
                        <span className="text-slate-500 block text-[8px]">AVG DEGREE</span>
                        <span className="text-amber-300 font-bold">2.91</span>
                      </div>
                      <div className="bg-slate-900/80 p-1 rounded border border-slate-800">
                        <span className="text-slate-500 block text-[8px]">CLUSTER COEFF</span>
                        <span className="text-purple-300 font-bold">0.73</span>
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* --- MIDDLE RIGHT: VFS REFRACTIONS // OPEN VIKING PROTOCOL --- */}
              <div className={`absolute ${minimizedPanels.graphify ? 'top-16' : 'top-48'} right-4 z-30 w-76 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.vfs 
                  ? 'border-cyan-900/40 bg-slate-950/60 p-2' 
                  : 'border-cyan-900/80 hover:border-cyan-400/80'
              }`}>
                <div className="flex items-center justify-between border-b border-cyan-950/90 pb-1 mb-2">
                  <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">VFS REFRACTIONS</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-amber-300">OPEN VIKING</span>
                    <button
                      onClick={() => togglePanel('vfs')}
                      className="p-1 rounded bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.vfs ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.vfs ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.vfs && (
                  <div className="space-y-1.5">
                    {streams.map((stream) => (
                      <div key={stream.id} className="text-[9px]">
                        <div className="flex items-center justify-between text-slate-300 mb-0.5">
                          <span className="truncate">{stream.name}</span>
                          <span className="text-cyan-400 font-bold">{stream.speed}</span>
                        </div>
                        <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden flex items-center">
                          <div 
                            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full transition-all duration-500"
                            style={{ width: `${stream.progress}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* --- LOWER RIGHT: IPC & MEMORY SLAB SYNC --- */}
              <div className={`absolute ${
                minimizedPanels.graphify && minimizedPanels.vfs 
                  ? 'top-28' 
                  : minimizedPanels.vfs 
                  ? 'top-40' 
                  : 'top-[400px]'
              } right-4 z-30 w-76 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.slabs 
                  ? 'border-cyan-900/40 bg-slate-950/60 p-2' 
                  : 'border-cyan-900/80 hover:border-cyan-400/80'
              }`}>
                <div className="flex items-center justify-between border-b border-cyan-950/90 pb-1 mb-2">
                  <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">IPC & MEMORY SLABS</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-emerald-400 font-bold">OPTIMAL</span>
                    <button
                      onClick={() => togglePanel('slabs')}
                      className="p-1 rounded bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.slabs ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.slabs ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.slabs && (
                  <>
                    <div className="grid grid-cols-2 gap-2 text-[9px] mb-2">
                      <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                        <span className="text-slate-500 block text-[8px]">SUB-MS LATENCY</span>
                        <span className="text-emerald-300 font-bold text-xs">0.23 ms</span>
                      </div>
                      <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                        <span className="text-slate-500 block text-[8px]">THROUGHPUT</span>
                        <span className="text-amber-300 font-bold text-xs">2.4 GB/s</span>
                      </div>
                    </div>

                    {/* 32 Slab Bins Grid */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-[8px] text-slate-400">
                        <span>MEMORY SLAB BINS (32 BINS)</span>
                        <span className="text-cyan-400">100% SYNC</span>
                      </div>
                      <div className="grid grid-cols-16 gap-0.5 p-1 bg-slate-900/90 rounded border border-slate-800">
                        {slabs.map((active, i) => (
                          <button
                            key={i}
                            onClick={() => handleToggleSlab(i)}
                            className={`h-2 rounded-[1px] transition-colors ${
                              active ? 'bg-amber-400 shadow-[0_0_4px_rgba(251,191,36,0.6)]' : 'bg-slate-800 hover:bg-slate-700'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* --- BOTTOM RIGHT: SYSTEM COMMANDS --- */}
              <div className={`absolute bottom-4 right-4 z-30 w-76 bg-slate-950/90 backdrop-blur-md border rounded-xl p-3 shadow-2xl transition-all duration-300 ${
                minimizedPanels.commands 
                  ? 'border-cyan-900/40 bg-slate-950/60 p-2' 
                  : 'border-cyan-900/80'
              }`}>
                <div className="flex items-center justify-between border-b border-cyan-950/90 pb-1 mb-2">
                  <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">SYSTEM COMMANDS</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-slate-500">ROOT</span>
                    <button
                      onClick={() => togglePanel('commands')}
                      className="p-1 rounded bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-slate-800 transition-colors"
                      title={minimizedPanels.commands ? "Expand panel" : "Minimize panel"}
                    >
                      {minimizedPanels.commands ? <Plus className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {!minimizedPanels.commands && (
                  <div className="space-y-1 text-[9px]">
                    {[
                      { cmd: 'INIT_WORLD_TREE', label: '> INIT_WORLD_TREE', color: 'text-amber-300 hover:bg-amber-950/50' },
                      { cmd: 'SYNC_ALL_ENGINES', label: '> SYNC_ALL_ENGINES', color: 'text-cyan-300 hover:bg-cyan-950/50' },
                      { cmd: 'FLUSH_CONTEXT', label: '> FLUSH_CONTEXT', color: 'text-rose-300 hover:bg-rose-950/50' },
                      { cmd: 'OPTIMIZE_MEMORY', label: '> OPTIMIZE_MEMORY', color: 'text-emerald-300 hover:bg-emerald-950/50' },
                      { cmd: 'RUN_DIAGNOSTICS', label: '> RUN_DIAGNOSTICS', color: 'text-purple-300 hover:bg-purple-950/50' },
                      { cmd: 'SECRET_CIPHER', label: '> [CLASSIFIED_CIPHER]', color: 'text-amber-400 font-bold hover:bg-amber-950/80' }
                    ].map((item) => (
                      <button
                        key={item.cmd}
                        onClick={() => executeCommand(item.cmd)}
                        className={`w-full text-left px-2 py-1 rounded transition-all font-mono active:scale-95 ${item.color}`}
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

          {/* --- BOTTOM CENTER: VKG_HUD TITLE BANNER & MINIMIZED DOCK --- */}
          {!cinemaMode && countMinimized > 0 && (
            <div className="absolute bottom-16 left-1/2 -translate-x-1/2 z-35 flex items-center gap-1.5 p-1.5 rounded-2xl bg-slate-950/95 backdrop-blur-xl border border-cyan-500/50 shadow-[0_0_30px_rgba(0,0,0,0.85),0_0_15px_rgba(34,211,238,0.3)] animate-fadeIn max-w-[95%] overflow-x-auto custom-scrollbar">
              <div className="flex items-center gap-1 px-2 text-[10px] text-cyan-300 font-bold tracking-wider whitespace-nowrap">
                <Minimize2 className="w-3.5 h-3.5 text-amber-400" />
                <span>HUD DOCK ({countMinimized}/8):</span>
              </div>
              
              {minimizedPanels.telemetry && (
                <button
                  onClick={() => togglePanel('telemetry')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-cyan-950 border border-cyan-800/80 hover:border-cyan-400 text-cyan-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore System Telemetry"
                >
                  <Activity className="w-3 h-3 text-cyan-400" />
                  <span>Telemetry ({ramUsedGB.toFixed(1)}GB)</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              {minimizedPanels.process && (
                <button
                  onClick={() => togglePanel('process')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-cyan-950 border border-cyan-800/80 hover:border-cyan-400 text-cyan-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore Process Matrix"
                >
                  <Cpu className="w-3 h-3 text-emerald-400" />
                  <span>Processes (7)</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              {minimizedPanels.ouroboros && (
                <button
                  onClick={() => togglePanel('ouroboros')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-amber-950 border border-amber-800/80 hover:border-amber-400 text-amber-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore Ouroboros SSM"
                >
                  <RotateCw className="w-3 h-3 text-amber-400" />
                  <span>Ouroboros (1.58b)</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              {minimizedPanels.logs && (
                <button
                  onClick={() => togglePanel('logs')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-cyan-950 border border-cyan-800/80 hover:border-cyan-400 text-cyan-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore System Log"
                >
                  <Terminal className="w-3 h-3 text-cyan-400" />
                  <span>Logs</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              {minimizedPanels.graphify && (
                <button
                  onClick={() => togglePanel('graphify')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-cyan-950 border border-cyan-800/80 hover:border-cyan-400 text-cyan-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore Graphify Network"
                >
                  <Radio className="w-3 h-3 text-purple-400" />
                  <span>Graphify (L{depthLayer})</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              {minimizedPanels.vfs && (
                <button
                  onClick={() => togglePanel('vfs')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-cyan-950 border border-cyan-800/80 hover:border-cyan-400 text-cyan-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore VFS Streams"
                >
                  <Layers className="w-3 h-3 text-amber-400" />
                  <span>VFS Streams</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              {minimizedPanels.slabs && (
                <button
                  onClick={() => togglePanel('slabs')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-cyan-950 border border-cyan-800/80 hover:border-cyan-400 text-cyan-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore IPC & Memory Slabs"
                >
                  <Database className="w-3 h-3 text-emerald-400" />
                  <span>Memory Slabs</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              {minimizedPanels.commands && (
                <button
                  onClick={() => togglePanel('commands')}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-900 hover:bg-cyan-950 border border-cyan-800/80 hover:border-cyan-400 text-cyan-300 text-[10px] whitespace-nowrap transition-all active:scale-95"
                  title="Restore System Commands"
                >
                  <Play className="w-3 h-3 text-rose-400" />
                  <span>Commands</span>
                  <Plus className="w-2.5 h-2.5 text-slate-400" />
                </button>
              )}

              <div className="h-4 w-px bg-slate-800 mx-1" />

              <button
                onClick={handleToggleAllPanels}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-gradient-to-r from-cyan-900 to-emerald-900 hover:from-cyan-800 hover:to-emerald-800 border border-cyan-400 text-cyan-100 text-[10px] font-bold whitespace-nowrap shadow-[0_0_10px_rgba(34,211,238,0.3)] transition-all active:scale-95"
                title="Restore all HUD panels to viewport"
              >
                <Maximize2 className="w-3.5 h-3.5 text-amber-300" />
                <span>RESTORE ALL HUD</span>
              </button>
            </div>
          )}

          {/* --- BOTTOM CENTER: VKG_HUD TITLE BANNER --- */}
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-30 text-center pointer-events-none">
            <div className="bg-slate-950/90 backdrop-blur-md border border-cyan-900/60 px-5 py-1 rounded-xl shadow-lg">
              <span className="text-[10px] text-cyan-400 font-bold tracking-widest block">vKG_HUD</span>
              <h2 className="text-xs font-bold text-amber-200 tracking-wider">
                THE SOVEREIGN WORLD TREE CONTROL CENTER
              </h2>
              <p className="text-[8px] text-slate-400 tracking-widest">
                WHERE MYTHIC ARCHITECTURE MEETS ENGINEERED INTELLIGENCE
              </p>
            </div>
          </div>

        </div>
      </div>

      {/* Modals for Deep Inspection */}
      {activeModal === 'memcastle' && (
        <MemcastleModal isOpen={true} onClose={() => setActiveModal(null)} />
      )}
      {activeModal === 'twin_brains' && (
        <TwinBrainsModal isOpen={true} onClose={() => setActiveModal(null)} />
      )}
      {activeModal === 'viking' && (
        <VikingRefractionsModal isOpen={true} onClose={() => setActiveModal(null)} />
      )}
    </div>
  );
};

