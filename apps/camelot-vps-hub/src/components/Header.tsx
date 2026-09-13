import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Terminal, 
  Cpu, 
  Activity, 
  Copy, 
  Play, 
  Send, 
  CheckCircle2, 
  Server, 
  Layers, 
  Lock, 
  ScrollText,
  FileCode,
  Flame,
  Sparkles,
  TreeDeciduous,
  Radio,
  Minus,
  Plus,
  Crown,
  Eye,
  Key
} from 'lucide-react';
import { SystemVitals } from '../types';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  vitals: SystemVitals;
  onGoLive: () => void;
  onDispatch: () => void;
  onRunMission: () => void;
  copied: boolean;
  onCopyScript: () => void;
  isTabMinimized?: boolean;
  onToggleTabMinimize?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  vitals,
  onGoLive,
  onDispatch,
  onRunMission,
  copied,
  onCopyScript,
  isTabMinimized = false,
  onToggleTabMinimize
}) => {
  const [compactHeader, setCompactHeader] = useState(false);
  const ramPercent = Math.round((vitals.usedRamMB / vitals.scarcityCapMB) * 100);

  const tabs = [
    { id: 'deck', label: '3D World Tree Deck', icon: TreeDeciduous },
    { id: 'bento', label: 'Bento Grid Hub', icon: Layers },
    { id: 'terminal', label: 'Baremetal Terminal', icon: Terminal },
    { id: 'vkg', label: 'VKG-HUD Services', icon: Server },
    { id: 'mission', label: 'Mission Arena', icon: Flame },
    { id: 'laws', label: 'Sovereign Laws & Ledger', icon: Lock },
    { id: 'scarcity', label: '8GB Scarcity Protocol', icon: Cpu },
    { id: 'script', label: 'Master Bootstrap Script', icon: FileCode }
  ];

  return (
    <header className="border-b border-[#D4AF37]/30 bg-[#060a14]/95 backdrop-blur-xl sticky top-0 z-40">
      {/* Top Banner / System Ribbon */}
      {!compactHeader && (
        <div className="px-4 py-1.5 bg-gradient-to-r from-[#1a1405] via-[#0a1224] to-[#170a24] border-b border-[#D4AF37]/20 flex flex-wrap items-center justify-between text-xs gap-3 font-mono">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#D4AF37]/10 border border-[#D4AF37]/40 text-[#D4AF37]">
              <Crown className="w-3.5 h-3.5 text-[#D4AF37]" />
              <span className="font-bold text-[10px] uppercase tracking-wider">ANYA_LAW_SOVEREIGN</span>
            </div>
            <div className="hidden sm:flex items-center gap-2 text-slate-400 text-[11px]">
              <span>OPERATOR: <span className="text-[#F3E5AB] font-semibold">KING ARTHUR (VIZION)</span></span>
              <span className="text-slate-600">|</span>
              <span>HOST: <span className="text-cyan-200 font-semibold">{vitals.targetHost}</span></span>
              <span className="text-slate-600">|</span>
              <span>VPS HUB: <span className="text-emerald-300 font-semibold">KVM563 (HERMES_PRIME)</span></span>
              <span className="text-slate-600">|</span>
              <span className="text-[#D4AF37]">8GB SCARCITY CAP</span>
            </div>
          </div>

          {/* Quick Directives & Actions */}
          <div className="flex items-center gap-2">
            <button
              id="btn-quick-golive"
              onClick={onGoLive}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-gradient-to-r from-[#D4AF37] to-[#F3E5AB] hover:from-[#e5c158] hover:to-[#fff0bd] text-black font-bold text-xs transition-all shadow-[0_0_15px_rgba(212,175,55,0.45)] active:scale-95 cursor-pointer"
              title="Execute //GO_LIVE deployment"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              <span>//GO_LIVE</span>
            </button>

            <button
              id="btn-quick-dispatch"
              onClick={onDispatch}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/40 text-xs transition-all active:scale-95 cursor-pointer"
              title="Dispatch directives to engineering"
            >
              <Send className="w-3.5 h-3.5 text-cyan-400" />
              <span>//DISPATCH</span>
            </button>

            <button
              id="btn-quick-mission"
              onClick={onRunMission}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-purple-950/80 hover:bg-purple-900 text-purple-300 border border-purple-500/40 text-xs transition-all active:scale-95 cursor-pointer"
              title="Dispatch sovereign knight agent mission"
            >
              <Flame className="w-3.5 h-3.5 text-amber-400" />
              <span>//RUN_MISSION</span>
            </button>

            <button
              id="btn-quick-copy"
              onClick={onCopyScript}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs transition-all cursor-pointer"
              title="Copy Raw Master Bootstrap Script"
            >
              {copied ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-300 font-bold">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-slate-400" />
                  <span>Copy Script</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Main Identity & Status Header */}
      <div className="px-4 py-2.5 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        
        {/* Left: Glowing World Tree Logo & Title */}
        <div className="flex items-center gap-3.5">
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-[#1a1405] via-[#0c1e38] to-[#120f26] border-2 border-[#D4AF37]/70 flex items-center justify-center text-[#D4AF37] shadow-[0_0_22px_rgba(212,175,55,0.4)]">
            <TreeDeciduous className="w-5 h-5 text-[#F3E5AB] animate-pulse" />
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[#D4AF37] animate-ping"></div>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-heraldic text-lg sm:text-xl font-bold tracking-wider text-white flex items-center gap-2">
                Camelot-OS <span className="text-[#D4AF37] font-sans font-semibold">World Tree Hub</span>
              </h1>
              <span className="px-2 py-0.5 text-[9px] uppercase font-mono font-bold tracking-wider rounded bg-[#D4AF37]/15 text-[#F3E5AB] border border-[#D4AF37]/40 shadow-[0_0_10px_rgba(212,175,55,0.2)]">
                vMAX OMEGA TITAN
              </span>
            </div>
            <p className="text-[10px] text-[#D4AF37] font-mono tracking-widest font-semibold flex items-center gap-2 uppercase">
              <span>S26 ULTRA COCKPIT // VPS HUB // CYBERTRONIA</span>
              <span className="text-slate-600">•</span>
              <span className="text-slate-400 font-normal">NATIVE BARE-METAL CUBE</span>
            </p>
          </div>
        </div>

        {/* Right: Status & Compact Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Excalibur Mobile Sentinel Pulse Box */}
          <div className="px-3 py-1.5 rounded-xl bg-[#0a1224] border border-cyan-500/50 shadow-[0_0_15px_rgba(34,211,238,0.2)] flex items-center gap-2 font-mono text-xs">
            <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <div>
              <div className="text-[8px] text-cyan-400 font-bold uppercase tracking-widest leading-none">
                EXCALIBUR COCKPIT
              </div>
              <div className="text-[10px] font-bold text-slate-200">
                S26 ULTRA: <span className="text-emerald-400 font-semibold">ONLINE</span>
              </div>
            </div>
          </div>

          {/* Glowing Emerald Box: SYSTEM STATUS: NOMINAL */}
          <div className="px-3 py-1.5 rounded-xl bg-emerald-950/80 border-2 border-emerald-500/60 shadow-[0_0_25px_rgba(16,185,129,0.35)] flex items-center gap-2 font-mono">
            <div className="relative flex items-center justify-center">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span className="absolute w-3.5 h-3.5 rounded-full bg-emerald-400/40 animate-ping"></span>
            </div>
            <div>
              <div className="text-[8px] text-emerald-400 font-bold uppercase tracking-widest leading-none">
                GIDEON GATE CONVERGENCE
              </div>
              <div className="text-[11px] font-bold text-white tracking-wide">
                STATUS: <span className="text-emerald-300">NOMINAL</span>
              </div>
            </div>
          </div>

          {/* Scarcity RAM Pill */}
          <div className="bg-[#050b17] border border-[#D4AF37]/30 rounded-xl px-3 py-1.5 flex items-center gap-2.5 font-mono text-xs">
            <Cpu className="w-4 h-4 text-[#D4AF37]" />
            <div>
              <div className="flex items-center justify-between gap-2 text-[10px]">
                <span className="text-slate-400">8GB RAM</span>
                <span className="font-bold text-[#F3E5AB]">{ramPercent}% ({((vitals.usedRamMB) / 1024).toFixed(1)}G)</span>
              </div>
              <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1">
                <div 
                  className="h-full bg-gradient-to-r from-[#D4AF37] to-cyan-400 rounded-full"
                  style={{ width: `${ramPercent}%` }}
                />
              </div>
            </div>
          </div>

          {/* Toggle Header Ribbons */}
          <button
            onClick={() => setCompactHeader(!compactHeader)}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-[#D4AF37] transition-all text-[11px] cursor-pointer"
            title={compactHeader ? "Expand Header Ribbon" : "Compact Header"}
          >
            {compactHeader ? <Plus className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
          </button>
        </div>

      </div>

      {/* Navigation Tabs */}
      <div className="px-4 flex items-center justify-between overflow-x-auto border-t border-[#D4AF37]/20 bg-[#040812]">
        <div className="flex items-center gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 text-xs font-mono font-medium whitespace-nowrap transition-all border-b-2 cursor-pointer ${
                  isActive
                    ? 'border-[#D4AF37] text-[#F3E5AB] bg-[#D4AF37]/10 shadow-[inset_0_-8px_14px_rgba(212,175,55,0.15)] font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#D4AF37]' : 'text-slate-500'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {onToggleTabMinimize && (
          <button
            onClick={onToggleTabMinimize}
            className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono text-slate-400 hover:text-[#D4AF37] bg-slate-900/70 border border-slate-800 rounded my-1 shrink-0 ml-2 cursor-pointer"
            title="Minimize active view"
          >
            {isTabMinimized ? <Plus className="w-3 h-3 text-[#D4AF37]" /> : <Minus className="w-3 h-3 text-[#D4AF37]" />}
            <span>{isTabMinimized ? 'RESTORE VIEW' : 'MINIMIZE VIEW'}</span>
          </button>
        )}
      </div>
    </header>

  );
};
