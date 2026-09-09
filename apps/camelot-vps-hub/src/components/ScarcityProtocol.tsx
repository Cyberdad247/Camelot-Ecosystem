import React, { useState } from 'react';
import { 
  Cpu, 
  ShieldAlert, 
  Activity, 
  Layers, 
  Server, 
  Zap, 
  CheckCircle2, 
  AlertTriangle,
  Minus,
  Plus,
  Crown,
  Key,
  Flame,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { CamelotService, SystemVitals } from '../types';
import confetti from 'canvas-confetti';

interface ScarcityProtocolProps {
  vitals: SystemVitals;
  services: CamelotService[];
  onOptimize?: () => void;
}

export const ScarcityProtocol: React.FC<ScarcityProtocolProps> = ({ vitals, services, onOptimize }) => {
  const ramPercent = Math.round((vitals.usedRamMB / vitals.scarcityCapMB) * 100);

  // Minimization states
  const [minimizedBreakdown, setMinimizedBreakdown] = useState(false);
  const [minimizedServices, setMinimizedServices] = useState(false);

  // Hidden Aspect: Kernel Memory Overcommit Bypass & Emergency Swap Vault
  const [showSwapVault, setShowSwapVault] = useState(false);
  const [zramCompressionRatio, setZramCompressionRatio] = useState(3.4);
  const [swappinessValue, setSwappinessValue] = useState(10);
  const [vaultPurged, setVaultPurged] = useState(false);

  const categoryMemory = services.reduce((acc, s) => {
    acc[s.category] = (acc[s.category] || 0) + s.currentRamMB;
    return acc;
  }, {} as Record<string, number>);

  const handlePurge = () => {
    setVaultPurged(true);
    setZramCompressionRatio(3.9);
    onOptimize?.();
    confetti({ particleCount: 30, spread: 60, origin: { y: 0.6 } });
    setTimeout(() => setVaultPurged(false), 3000);
  };

  const toggleSwapVault = () => {
    setShowSwapVault(!showSwapVault);
    if (!showSwapVault) {
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
                Kernel & Memory Subsystem // cgroups v2
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight font-heraldic">
              THE 8GB SCARCITY PROTOCOL & MEMORY LATTICE
            </h2>
            <p className="text-xs text-slate-400 font-terminal mt-1">
              Strict bare-metal memory confinement bounded by Linux cgroups v2 controller. Hard cap enforced at 7.2GB (7,372MB) to prevent kernel OOM stalls.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* HIDDEN ASPECT: Swap Vault */}
            <button
              onClick={toggleSwapVault}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs font-bold transition-all ${
                showSwapVault
                  ? 'bg-amber-950 border-amber-400 text-amber-200 shadow-[0_0_15px_rgba(245,158,11,0.5)] animate-pulse'
                  : 'bg-slate-900 border-amber-900/60 text-amber-400/80 hover:text-amber-300'
              }`}
            >
              <Cpu className="w-3.5 h-3.5 text-amber-400" />
              <span>{showSwapVault ? 'SWAP VAULT: OPEN' : '[CLASSIFIED: ZERO-TRUST SWAP VAULT]'}</span>
            </button>

            {onOptimize && (
              <button
                onClick={onOptimize}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition-all shadow-[0_0_12px_rgba(245,158,11,0.35)]"
              >
                <Zap className="w-3.5 h-3.5 fill-black" />
                <span>Optimize Slab Bins</span>
              </button>
            )}
          </div>
        </div>

        {/* Global Memory Progress Bar */}
        <div className="mt-4 pt-4 border-t border-slate-800 space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">cgroups v2 Hard Cap Utilization:</span>
            <span className="text-cyan-300 font-bold">{vitals.usedRamMB} MB / {vitals.scarcityCapMB} MB ({ramPercent}%)</span>
          </div>
          <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                ramPercent > 85
                  ? 'bg-rose-500'
                  : ramPercent > 70
                  ? 'bg-amber-400'
                  : 'bg-gradient-to-r from-cyan-400 to-emerald-400'
              }`}
              style={{ width: `${ramPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* HIDDEN ASPECT DRAWER: ZERO-TRUST SWAP VAULT */}
      {showSwapVault && (
        <div className="bg-amber-950/20 border-2 border-amber-500/60 rounded-xl p-4 shadow-2xl space-y-3 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-amber-500/40 pb-2">
            <div className="flex items-center gap-2">
              <Key className="w-5 h-5 text-amber-400 animate-pulse" />
              <div>
                <h3 className="text-sm font-bold text-amber-200 tracking-wider">
                  CLASSIFIED KERNEL MEMORY OVERCOMMIT & ZRAM SWAP VAULT
                </h3>
                <span className="text-[10px] text-amber-300/80">
                  REAL-TIME LZ4 COMPRESSION ENGINE & SLUB SLAB BIN FLUSHER
                </span>
              </div>
            </div>
            <button
              onClick={() => setShowSwapVault(false)}
              className="text-xs text-amber-300 hover:text-white underline"
            >
              Close Swap Vault
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-3 bg-black/80 border border-amber-500/40 rounded-lg space-y-2">
              <span className="text-amber-300 font-bold">LZ4 ZRAM RATIO</span>
              <div className="text-2xl font-bold text-emerald-400">{zramCompressionRatio}:1</div>
              <p className="text-[10px] text-slate-400">
                Compresses ephemeral stack frames into RAM blocks before committing to disk.
              </p>
            </div>

            <div className="p-3 bg-black/80 border border-amber-500/40 rounded-lg space-y-2">
              <span className="text-amber-300 font-bold">VM SWAPPINESS</span>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min="0"
                  max="60"
                  value={swappinessValue}
                  onChange={(e) => setSwappinessValue(Number(e.target.value))}
                  className="flex-1 accent-amber-400"
                />
                <span className="text-amber-300 font-bold w-6">{swappinessValue}</span>
              </div>
              <p className="text-[10px] text-slate-400">
                Kernel preference: 10 (Avoid swap aggressively, retain pagecache).
              </p>
            </div>

            <div className="p-3 bg-black/80 border border-amber-500/40 rounded-lg space-y-2">
              <span className="text-amber-300 font-bold">EMERGENCY SLAB PURGE</span>
              <button
                onClick={handlePurge}
                className="w-full py-2 rounded bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs shadow-lg transition-all"
              >
                {vaultPurged ? 'SLABS PURGED (-420MB)' : 'Purge Clean Slabs (sync && drop_caches)'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main 2-Column Memory Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* Left Column: Category Allocation Breakdown (Collapsible) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-[#0e131f] border border-cyan-950/80 rounded-xl p-4 shadow-lg space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span>CATEGORY ALLOCATION LATTICE</span>
              </h3>
              <button
                onClick={() => setMinimizedBreakdown(!minimizedBreakdown)}
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-300"
                title={minimizedBreakdown ? "Expand Breakdown" : "Minimize Breakdown"}
              >
                {minimizedBreakdown ? <Plus className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
              </button>
            </div>

            {!minimizedBreakdown ? (
              <div className="space-y-3">
                {Object.entries(categoryMemory).map(([cat, ram]) => {
                  const percentOfUsed = Math.round((Number(ram) / vitals.usedRamMB) * 100);
                  return (
                    <div key={cat} className="p-2.5 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="font-bold text-slate-300 uppercase">{cat.replace('_', ' ')}</span>
                        <span className="text-cyan-300 font-bold">{ram} MB ({percentOfUsed}%)</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-cyan-400 rounded-full"
                          style={{ width: `${percentOfUsed}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-2 bg-slate-900/60 rounded text-xs text-slate-400 flex justify-between">
                <span>Category Lattice Minimized</span>
                <span className="text-cyan-300 font-bold">{Object.keys(categoryMemory).length} CATEGORIES</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: 28 Unit Breakdown (Collapsible) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-[#0e131f] border border-cyan-950/80 rounded-xl p-4 shadow-lg space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <Server className="w-4 h-4 text-emerald-400" />
                <span>UNIT MEMORY CONFINEMENT ({services.length})</span>
              </h3>
              <button
                onClick={() => setMinimizedServices(!minimizedServices)}
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-300"
                title={minimizedServices ? "Expand Units" : "Minimize Units"}
              >
                {minimizedServices ? <Plus className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
              </button>
            </div>

            {!minimizedServices ? (
              <div className="space-y-2 max-h-[450px] overflow-y-auto custom-scrollbar">
                {services.map((s) => (
                  <div key={s.id} className="p-2 bg-slate-950 rounded border border-slate-800/80 flex items-center justify-between text-xs">
                    <div>
                      <div className="font-bold text-slate-200">{s.name}</div>
                      <div className="text-[10px] text-slate-500 font-mono">{s.unitName}</div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-amber-300 font-bold">{s.currentRamMB} MB</div>
                      <div className="text-[9px] text-slate-500">Cap: {s.allocatedRamMB} MB</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-2 bg-slate-900/60 rounded text-xs text-slate-400 flex justify-between">
                <span>Unit Breakdown Minimized</span>
                <span className="text-emerald-400 font-bold">28 ACTIVE UNITS</span>
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
