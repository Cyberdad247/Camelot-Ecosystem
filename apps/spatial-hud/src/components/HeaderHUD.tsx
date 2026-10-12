import React from 'react';
import { Shield, HardDrive, Network, Sparkles, RefreshCw, Lock, Flame, Sun, Moon } from 'lucide-react';
import { ActiveTab, ThemeMode } from '../types';
import { NavigationMenu } from './NavigationMenu';

interface HeaderHUDProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  onKineticTrigger: (trigger: string) => void;
  vfsFileCount: number;
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
}

export const HeaderHUD: React.FC<HeaderHUDProps> = ({
  activeTab,
  setActiveTab,
  onKineticTrigger,
  vfsFileCount,
  theme,
  setTheme,
}) => {
  const isDark = theme === 'dark';

  return (
    <header className={`${isDark ? 'bg-neutral-950 border-neutral-800 text-neutral-100' : 'bg-slate-100 border-slate-300 text-slate-900'} border-b select-none transition-colors duration-200`}>
      {/* Top Telemetry Ticker Bar */}
      <div className={`px-6 py-2 ${isDark ? 'bg-neutral-900 border-neutral-800/80' : 'bg-slate-200/90 border-slate-300'} border-b flex flex-wrap items-center justify-between text-xs font-mono tracking-wide gap-3 transition-colors`}>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 text-amber-500 dark:text-amber-400 font-semibold">
            <Flame className="w-3.5 h-3.5 animate-pulse text-amber-500" />
            <span>[CPU: 120% OMNI_EXEC]</span>
          </div>
          <div className="flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400">
            <HardDrive className="w-3.5 h-3.5 text-emerald-500" />
            <span>[RAM: 7.4GB / 8.0GB]</span>
          </div>
          <div className="hidden md:flex items-center space-x-1.5 text-sky-600 dark:text-sky-400">
            <Network className="w-3.5 h-3.5 text-sky-500" />
            <span>[LATTICE: 24D LEECH]</span>
          </div>
          <div className="hidden lg:flex items-center space-x-1.5 text-purple-600 dark:text-purple-400">
            <Lock className="w-3.5 h-3.5 text-purple-500 dark:text-purple-400" />
            <span>[BIFROST: KYBER-768 mTLS]</span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <span className={`${isDark ? 'text-neutral-400' : 'text-slate-600'} hidden sm:inline`}>
            NODE: <span className={`${isDark ? 'text-neutral-200' : 'text-slate-900'} font-medium`}>Cleveland, OH (Vizion)</span>
          </span>
          <span className={`${isDark ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60' : 'bg-emerald-100 text-emerald-800 border-emerald-300'} border px-2 py-0.5 rounded text-[11px] font-semibold tracking-wider uppercase flex items-center gap-1`}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
            APEX_ONLINE
          </span>
        </div>
      </div>

      {/* Main Navigation & System Brand Header */}
      <div className="px-6 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Brand & Mandate */}
        <div className="flex items-center space-x-3.5">
          <div className={`w-10 h-10 rounded-xl ${isDark ? 'bg-neutral-900 border-neutral-700' : 'bg-white border-slate-300 shadow-sm'} border flex items-center justify-center relative group`}>
            <Shield className="w-6 h-6 text-amber-500 dark:text-amber-400 group-hover:scale-110 transition-transform duration-300" />
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-amber-500 ring-2 ring-neutral-950 animate-pulse"></div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className={`text-lg font-bold tracking-tight ${isDark ? 'text-white' : 'text-slate-950'} font-sans uppercase`}>
                CAMELOT-OS <span className={`font-mono text-xs font-normal px-1.5 py-0.5 rounded ${isDark ? 'text-amber-400 bg-amber-950/60 border-amber-800/40' : 'text-amber-700 bg-amber-100 border-amber-300'} border`}>vMAX.54</span>
              </h1>
              <span className={`text-xs ${isDark ? 'text-neutral-500' : 'text-slate-500'} font-mono hidden sm:inline`}>| DGM-H ENGINE</span>
            </div>
            <p className={`text-xs ${isDark ? 'text-neutral-400' : 'text-slate-600'} font-sans italic tracking-wide`}>
              "dreams don't come true visions do" — <span className={`${isDark ? 'text-neutral-300' : 'text-slate-900'} font-medium not-italic`}>Operator: VaShawn O. Head (Vizion)</span>
            </p>
          </div>
        </div>

        {/* Right Section: Kinetic Triggers + Light/Dark Toggle */}
        <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
          {/* Light / Dark Mode Switcher */}
          <button
            onClick={() => setTheme(isDark ? 'light' : 'dark')}
            className={`px-3 py-1.5 ${isDark ? 'bg-neutral-800 hover:bg-neutral-700 text-yellow-300 border-neutral-700 shadow-[0_0_10px_rgba(234,179,8,0.1)]' : 'bg-white hover:bg-slate-200 text-slate-800 border-slate-300 shadow-sm'} border rounded-lg transition-all flex items-center space-x-1.5 active:scale-95`}
            title={`Switch to ${isDark ? 'Light (Solar Matrix)' : 'Dark (Obsidian Void)'} mode`}
          >
            {isDark ? (
              <>
                <Sun className="w-3.5 h-3.5 text-amber-400 animate-spin-slow" />
                <span className="font-semibold text-[11px]">LIGHT</span>
              </>
            ) : (
              <>
                <Moon className="w-3.5 h-3.5 text-purple-600" />
                <span className="font-semibold text-[11px]">DARK</span>
              </>
            )}
          </button>

          <button
            onClick={() => onKineticTrigger('//boot')}
            className="px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-600 dark:text-amber-300 border border-amber-500/30 rounded-lg transition-all flex items-center space-x-1.5 active:scale-95 shadow-sm"
            title="Awaken Camelot-OS Sovereign Kernel"
          >
            <span>⚡</span>
            <span className="font-semibold">//boot</span>
          </button>

          <button
            onClick={() => onKineticTrigger('//nano-swarm expand')}
            className="px-3 py-1.5 bg-sky-500/10 hover:bg-sky-500/20 text-sky-600 dark:text-sky-300 border border-sky-500/30 rounded-lg transition-all flex items-center space-x-1.5 active:scale-95 shadow-sm"
            title="Hydrate full 20-file VFS ecosystem"
          >
            <Sparkles className="w-3.5 h-3.5 text-sky-500 dark:text-sky-400" />
            <span className="font-semibold">//nano-swarm expand</span>
          </button>

          <button
            onClick={() => onKineticTrigger('//sync')}
            className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 rounded-lg transition-all flex items-center space-x-1.5 active:scale-95 shadow-sm"
            title="Bidirectional CRDT sync with Worldtree Cloudbrain"
          >
            <RefreshCw className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span className="font-semibold">//sync</span>
          </button>

          <button
            onClick={() => onKineticTrigger('//shield')}
            className="px-3 py-1.5 bg-purple-500/10 hover:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-500/30 rounded-lg transition-all flex items-center space-x-1.5 active:scale-95 shadow-sm"
            title="Activate Aegis Zero-Trust isolation perimeter"
          >
            <Shield className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
            <span className="font-semibold">//shield</span>
          </button>
        </div>
      </div>

      {/* Unified Tab Navigation Menu */}
      <NavigationMenu
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        theme={theme}
        vfsFileCount={vfsFileCount}
      />
    </header>
  );
};

