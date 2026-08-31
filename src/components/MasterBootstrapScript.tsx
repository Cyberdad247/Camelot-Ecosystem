import React, { useState } from 'react';
import { 
  Terminal, 
  Copy, 
  Check, 
  Code2, 
  Download, 
  Play, 
  Layers, 
  CheckCircle2, 
  Flame,
  FileCode,
  Minus,
  Plus,
  Crown,
  Key,
  Binary,
  Code
} from 'lucide-react';
import { RAW_BOOTSTRAP_PROMPT, BOOTSTRAP_PHASES } from '../data/bootstrapData';
import confetti from 'canvas-confetti';

interface MasterBootstrapScriptProps {
  scriptText?: string;
  onCopy?: () => void;
  copied?: boolean;
  onRunPhaseInTerminal?: (phaseIndex: number) => void;
}

export const MasterBootstrapScript: React.FC<MasterBootstrapScriptProps> = ({
  scriptText = RAW_BOOTSTRAP_PROMPT,
  onCopy,
  copied = false,
  onRunPhaseInTerminal
}) => {
  const [copiedAll, setCopiedAll] = useState(false);
  const [copiedPhaseIndex, setCopiedPhaseIndex] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'raw' | 'phases'>('raw');

  // Minimization states
  const [minimizedScript, setMinimizedScript] = useState(false);

  // Hidden Aspect: Binary Hex Injector & Kernel Assembly Disassembler
  const [showHexInjector, setShowHexInjector] = useState(false);
  const [injectedOpcode, setInjectedOpcode] = useState('0x48 0x89 0xE5 0x48 0x83 0xEC 0x20 0xE8 0x00 0x00');
  const [asmOutput, setAsmOutput] = useState('mov rbp, rsp\nsub rsp, 32\ncall camelot_vfs_mempalace_init\nret');

  const handleCopyAll = () => {
    if (onCopy) {
      onCopy();
    } else {
      navigator.clipboard.writeText(scriptText);
      setCopiedAll(true);
      setTimeout(() => setCopiedAll(false), 2000);
    }
  };

  const handleCopyPhase = (index: number, script: string) => {
    navigator.clipboard.writeText(script);
    setCopiedPhaseIndex(index);
    setTimeout(() => setCopiedPhaseIndex(null), 2000);
  };

  const toggleHexInjector = () => {
    setShowHexInjector(!showHexInjector);
    if (!showHexInjector) {
      confetti({ particleCount: 25, spread: 60, origin: { y: 0.6 } });
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-2 sm:p-4 space-y-4 font-mono">
      
      {/* Top Banner */}
      <div className="bg-[#0e131f] border border-amber-950/80 rounded-xl p-4 sm:p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono tracking-[0.2em] text-amber-500 uppercase">
                Direct Root Automation // 162.35.107.134
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight font-heraldic">
              MASTER BAREMETAL HUB BOOTSTRAP SCRIPT
            </h2>
            <p className="text-xs text-slate-400 font-terminal mt-1">
              Complete single-pass bootstrap prompt for initialization of native processes, systemd units, storage nodes, and Arthur R5/R6 zero-trust verification.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* HIDDEN ASPECT: Binary Hex Injector */}
            <button
              onClick={toggleHexInjector}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs font-bold transition-all ${
                showHexInjector
                  ? 'bg-amber-950 border-amber-400 text-amber-200 shadow-[0_0_15px_rgba(245,158,11,0.5)] animate-pulse'
                  : 'bg-slate-900 border-amber-900/60 text-amber-400/80 hover:text-amber-300'
              }`}
            >
              <Binary className="w-3.5 h-3.5 text-amber-400" />
              <span>{showHexInjector ? 'HEX INJECTOR: OPEN' : '[CLASSIFIED: KERNEL ASM & HEX INJECTOR]'}</span>
            </button>

            <button
              id="copy-full-bootstrap-btn"
              onClick={handleCopyAll}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition-all shadow-[0_0_15px_rgba(245,158,11,0.35)] active:scale-95"
            >
              {copied || copiedAll ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-black" />
                  <span>Copied Script!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-black" />
                  <span>Copy Master Script</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* HIDDEN ASPECT DRAWER: KERNEL ASM & BINARY HEX INJECTOR */}
      {showHexInjector && (
        <div className="bg-amber-950/20 border-2 border-amber-500/60 rounded-xl p-4 shadow-2xl space-y-3 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-amber-500/40 pb-2">
            <div className="flex items-center gap-2">
              <Key className="w-5 h-5 text-amber-400 animate-pulse" />
              <div>
                <h3 className="text-sm font-bold text-amber-200 tracking-wider">
                  CLASSIFIED BAREMETAL ASSEMBLY DISASSEMBLER & RAW HEX INJECTOR
                </h3>
                <span className="text-[10px] text-amber-300/80">
                  x86_64 DIRECT INSTRUCTION BYPASS & SYS_ENTER ARBITRATOR
                </span>
              </div>
            </div>
            <button
              onClick={() => setShowHexInjector(false)}
              className="text-xs text-amber-300 hover:text-white underline"
            >
              Close Disassembler
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-black/80 border border-amber-500/40 rounded-lg space-y-2">
              <span className="text-amber-300 font-bold flex items-center gap-1.5">
                <Binary className="w-4 h-4 text-cyan-400" />
                RAW OPCODE INJECTION BUFFER
              </span>
              <input
                type="text"
                value={injectedOpcode}
                onChange={(e) => setInjectedOpcode(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs text-cyan-300 font-mono"
              />
              <button
                onClick={() => {
                  setAsmOutput('mov rax, 0x3b\nsyscall ; Execve Arthur R6 binary\njmp 0x7FFF8A49B000');
                  confetti({ particleCount: 20, spread: 50, origin: { y: 0.7 } });
                }}
                className="w-full py-1.5 rounded bg-amber-950 border border-amber-500 text-amber-200 text-xs font-bold hover:bg-amber-900"
              >
                Disassemble Opcodes to Assembly
              </button>
            </div>

            <div className="p-3 bg-black/80 border border-amber-500/40 rounded-lg space-y-1.5">
              <span className="text-amber-300 font-bold flex items-center gap-1.5">
                <Code className="w-4 h-4 text-emerald-400" />
                DEOBFUSCATED KERNEL ASSEMBLY
              </span>
              <pre className="p-2 rounded bg-slate-950 border border-slate-800 text-[11px] font-mono text-emerald-300 h-24 overflow-y-auto">
                {asmOutput}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Script Navigation and Minimization Header */}
      <div className="bg-[#0a1020] border border-cyan-950/80 p-3 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('raw')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
              activeTab === 'raw'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
                : 'bg-slate-900 text-slate-400 border border-slate-800'
            }`}
          >
            Raw Prompt View
          </button>
          <button
            onClick={() => setActiveTab('phases')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
              activeTab === 'phases'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
                : 'bg-slate-900 text-slate-400 border border-slate-800'
            }`}
          >
            Structured Phases ({BOOTSTRAP_PHASES.length})
          </button>
        </div>

        <button
          onClick={() => setMinimizedScript(!minimizedScript)}
          className="p-1 rounded bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300"
          title={minimizedScript ? "Expand Script View" : "Minimize Script View"}
        >
          {minimizedScript ? <Plus className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
        </button>
      </div>

      {/* Main Script Box */}
      {!minimizedScript ? (
        activeTab === 'raw' ? (
          <div className="bg-[#05080e] border border-amber-950/80 rounded-xl p-4 shadow-2xl relative">
            <div className="absolute top-4 right-4 flex items-center gap-2">
              <button
                onClick={handleCopyAll}
                className="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs"
              >
                {copied || copiedAll ? 'Copied' : 'Copy'}
              </button>
            </div>
            <pre className="text-xs font-mono text-cyan-300 leading-relaxed overflow-x-auto whitespace-pre-wrap max-h-[600px] overflow-y-auto custom-scrollbar p-2">
              {scriptText}
            </pre>
          </div>
        ) : (
          <div className="space-y-3">
            {BOOTSTRAP_PHASES.map((phase, idx) => (
              <div key={phase.id} className="bg-[#0e131f] border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-300 text-xs">{phase.title}</span>
                  <button
                    onClick={() => handleCopyPhase(idx, phase.subtitle)}
                    className="text-[10px] px-2 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-300"
                  >
                    {copiedPhaseIndex === idx ? 'Copied' : 'Copy Phase'}
                  </button>
                </div>
                <p className="text-xs text-slate-400">{phase.subtitle}</p>
              </div>
            ))}
          </div>
        )
      ) : (
        <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl text-xs text-slate-400 flex justify-between items-center">
          <span>Master Bootstrap Script Minimized</span>
          <button
            onClick={() => setMinimizedScript(false)}
            className="px-3 py-1 rounded bg-cyan-950 border border-cyan-500 text-cyan-300 text-xs"
          >
            Expand Script
          </button>
        </div>
      )}

    </div>
  );
};
