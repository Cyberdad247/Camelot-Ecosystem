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
      {/* Sidebar — desktop only */}
      {!compact && <Sidebar collapsed={!sidebarOpen} />}

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        {!compact && (
          <header className="flex h-10 shrink-0 items-center gap-2 border-b border-slate-800/50 px-3">
            <button
              onClick={() => setSidebarOpen((s) => !s)}
              className="rounded p-1 text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 transition-colors"
            >
              {sidebarOpen
                ? <PanelLeftClose className="h-4 w-4" />
                : <PanelLeftOpen className="h-4 w-4" />
              }
            </button>
            <span className="text-[10px] font-mono uppercase tracking-widest text-slate-600">
              camelot-os-import-clean
            </span>
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
