"use client";

import { useEffect, useState } from "react";
import {
  Code,
  Play,
  Settings,
  Activity,
  Search,
  ShieldCheck,
} from "lucide-react";

export default function DevHub() {
  const [stats, setStats] = useState({
    files: 0,
    tests: 0,
    health: "RADIANT",
  });

  return (
    <div className="glass-panel p-6 rounded-2xl h-full flex flex-col bg-gradient-to-br from-slate-900/80 to-purple-900/20">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-mono font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 flex items-center gap-3">
          <Code className="w-6 h-6 text-purple-400" /> SDE HUB
        </h2>
        <div className="flex gap-1">
          <button
            className="p-1 hover:bg-white/5 rounded text-zinc-500"
            title="Check Health"
            aria-label="Check Health"
          >
            <Activity size={12} />
          </button>
          <button
            className="p-1 hover:bg-white/5 rounded text-zinc-500"
            title="Manage Sources"
            aria-label="Manage Sources"
          >
            <Search size={12} />
          </button>
          <button
            className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/40 hover:bg-purple-500/30 transition-colors shadow-[0_0_15px_rgba(168,85,247,0.2)]"
            title="Run Tests"
            aria-label="Run Tests"
          >
            <Play className="w-4 h-4 text-purple-400" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800/50">
          <div
            className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-1"
            title="Source Health Indicator"
          >
            Source Health
          </div>
          <div className="text-xl font-bold text-green-400 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5" /> RADIANT
          </div>
        </div>
        <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800/50">
          <div
            className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-1"
            title="Current Test Coverage"
          >
            Test Coverage
          </div>
          <div className="text-xl font-bold text-purple-400">92.4%</div>
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
        <div className="group p-3 rounded-lg border border-slate-800/50 bg-slate-900/30 hover:border-purple-500/30 transition-all cursor-pointer">
          <div className="flex items-center justify-between">
            <span className="text-sm font-mono text-slate-300">
              Ω_OPEN: Kinetic Refactor
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase font-bold">
              In-Progress
            </span>
          </div>
          <div className="mt-2 text-[10px] text-slate-500 font-mono italic">
            Refactoring Auth layer for JWT symmetry...
          </div>
        </div>
        <div className="group p-3 rounded-lg border border-slate-800/50 bg-slate-900/30 hover:border-purple-500/30 transition-all cursor-pointer">
          <div className="flex items-center justify-between">
            <span className="text-sm font-mono text-slate-300">
              //DEV: Build Deployment
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-500/10 text-slate-400 border border-slate-500/20 uppercase font-bold">
              Standing By
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
