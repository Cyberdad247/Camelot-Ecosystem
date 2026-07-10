import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import Sidebar from './Sidebar';
import MobileNav from '@/components/ui/BottomNav';
import { useDisplayProfile } from '@/hooks/useDisplayProfile';

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { compact } = useDisplayProfile();

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-[#050208] text-slate-100">
      {/* Sidebar â€” desktop only */}
      {!compact && <Sidebar collapsed={!sidebarOpen} />}

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        {!compact && (
          <header className="flex h-10 shrink-0 items-center gap-2 border-b border-slate-800/50 bg-[#08080A] px-3">
            <button
              onClick={() => setSidebarOpen((s) => !s)}
              className="rounded p-1 text-slate-500 transition-colors hover:bg-slate-800/50 hover:text-slate-300"
            >
              {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
            </button>
            <div className="flex w-full items-center justify-between gap-4 font-mono text-[10px] text-slate-500 select-none">
              <div className="flex items-center gap-3">
                <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-1 font-bold uppercase tracking-widest text-cyan-200">
                  [READ_ONLY_TELEMETRY]
                </span>
                <span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-2 py-1 font-bold uppercase tracking-widest text-amber-200">
                  [OPERATOR_SURFACE]
                </span>
              </div>
              <div className="flex items-center gap-3 pr-2">
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">CPU:</span>
                  <span className="animate-pulse font-bold text-[#00FFC2]">100%</span>
                </span>
                <span className="text-slate-800">|</span>
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">RAM:</span>
                  <span className="font-bold text-[#00FFC2]">4.1GB/8.0GB</span>
                </span>
                <span className="text-slate-800">|</span>
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">LATTICE:</span>
                  <span className="relative flex h-2 w-2 text-[#00FFC2] font-bold">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#00FFC2] opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-[#00FFC2]"></span>
                  </span>
                  <span className="ml-1 font-bold uppercase text-[#00FFC2]">ACTIVE</span>
                </span>
                <span className="text-slate-800">|</span>
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">MTP:</span>
                  <span className="font-bold uppercase text-[#00FFC2]">COHERENT</span>
                </span>
              </div>
            </div>
          </header>
        )}

        {/* Page content */}
        <main className="min-h-0 flex-1 overflow-y-auto">
          <Outlet />
        </main>

        {/* Mobile bottom nav */}
        {compact && <MobileNav />}
      </div>
    </div>
  );
}
