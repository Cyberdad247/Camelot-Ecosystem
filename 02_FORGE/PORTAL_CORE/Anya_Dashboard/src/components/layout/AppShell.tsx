import MobileNav from '@/components/ui/BottomNav';
import { useDisplayProfile } from '@/hooks/useDisplayProfile';
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { compact } = useDisplayProfile();

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-[#050208] text-slate-100">
      {/* Sidebar — desktop only */}
      {!compact && <Sidebar collapsed={!sidebarOpen} />}

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        {!compact && (
          <header className="flex h-10 shrink-0 items-center gap-2 border-b border-slate-800/50 px-3 bg-[#08080A]">
            <button
              onClick={() => setSidebarOpen((s) => !s)}
              className="rounded p-1 text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 transition-colors"
            >
              {sidebarOpen ? (
                <PanelLeftClose className="h-4 w-4" />
              ) : (
                <PanelLeftOpen className="h-4 w-4" />
              )}
            </button>
            <div className="flex items-center gap-4 text-[10px] font-mono text-slate-500 w-full justify-between select-none">
              <span className="uppercase tracking-widest text-slate-600 font-bold">
                [TELEMETRY_HUD]
              </span>
              <div className="flex items-center gap-3 pr-2">
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">CPU:</span>
                  <span className="text-[#00FFC2] font-bold animate-pulse">100%</span>
                </span>
                <span className="text-slate-800">|</span>
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">RAM:</span>
                  <span className="text-[#00FFC2] font-bold">4.1GB/8.0GB</span>
                </span>
                <span className="text-slate-800">|</span>
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">LATTICE:</span>
                  <span className="text-[#00FFC2] font-bold relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00FFC2] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00FFC2]"></span>
                  </span>
                  <span className="text-[#00FFC2] font-bold uppercase ml-1">ACTIVE</span>
                </span>
                <span className="text-slate-800">|</span>
                <span className="flex items-center gap-1">
                  <span className="text-[#8E95A5]">MTP:</span>
                  <span className="text-[#00FFC2] font-bold uppercase">COHERENT</span>
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
