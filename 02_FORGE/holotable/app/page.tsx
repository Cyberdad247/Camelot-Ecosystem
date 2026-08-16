'use client';

import React, { useState } from 'react';
import TheRoster from '@/components/TheRoster';
import TheLedger from '@/components/TheLedger';
import OracleCanvas from '@/components/OracleCanvas';
import DevHub from '@/components/DevHub';
import GenesisDesigner from '@/components/GenesisDesigner';
import { LayoutGrid, Binary, GitBranch, Cpu, Sparkles } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'oracle' | 'genesis'>('oracle');

  return (
    <main className="min-h-screen p-6 flex flex-col gap-6 bg-[#0a0a0a]">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-[#1a1a1a] pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wider flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-[#7D52FF]" />
            ⚔️ CAMELOT_OS <span className="text-[#7D52FF]">HOLOTABLE</span>
          </h1>
          <p className="text-xs text-zinc-500 font-mono mt-1">SYSTEM_STATUS :: RADIANT</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('oracle')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 border ${activeTab === 'oracle' ? 'bg-[#7D52FF]/10 text-[#7D52FF] border-[#7D52FF]' : 'bg-[#1a1a1a] text-zinc-400 border-zinc-800'}`}
            title="Switch to Oracle Simulation"
            aria-label="Simulation Mode"
          >
            <GitBranch size={14} /> ORACLE_SIM
          </button>
          <button
            onClick={() => setActiveTab('genesis')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 border ${activeTab === 'genesis' ? 'bg-[#FF0055]/10 text-[#FF0055] border-[#FF0055]' : 'bg-[#1a1a1a] text-zinc-400 border-zinc-800'}`}
            title="Switch to Genesis Designer"
            aria-label="Designer Mode"
          >
            <Cpu size={14} /> GENESIS_FORGE
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">
        {/* Left: The Roster & DevHub */}
        <div className="col-span-3 flex flex-col gap-6 h-full overflow-hidden">
          <TheRoster />
          <div className="flex-1 overflow-hidden min-h-0">
            <DevHub />
          </div>
        </div>

        {/* Center: Main Workspace */}
        <div className="col-span-6 flex flex-col gap-4 h-full overflow-hidden">
          {activeTab === 'oracle' ? (
            <div className="flex-1 h-full min-h-0">
              <OracleCanvas />
            </div>
          ) : (
            <div className="flex-1 h-full min-h-0">
              <GenesisDesigner />
            </div>
          )}
        </div>

        {/* Right: The Ledger */}
        <div className="col-span-3 h-full overflow-hidden">
          <TheLedger />
        </div>
      </div>
    </main>
  );
}
