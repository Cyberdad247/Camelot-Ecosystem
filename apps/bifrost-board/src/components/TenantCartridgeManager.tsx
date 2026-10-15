// SPDX-License-Identifier: MIT
// Tenant Cartridge Manager (Bifrost Board Edition)
// Compatible with lucide-react

import React, { useState } from 'react';
import { Server, Cpu, Database, Plus, X, Lock, CheckCircle2, Zap } from 'lucide-react';

export interface CartridgeDescriptor {
  id: string;
  name: string;
  ramCost: number;
  category: 'Conversion' | 'Sales' | 'Intel' | 'UX' | 'Ops' | 'Visual';
  description: string;
}

export const AVAILABLE_CARTRIDGES: CartridgeDescriptor[] = [
  { id: 'crt_01', name: 'Midas Lead Capture', ramCost: 45, category: 'Conversion', description: 'Zero-latency client intent conversion funnel' },
  { id: 'crt_02', name: 'B2B ROI Calculator', ramCost: 65, category: 'Sales', description: '2.5D spatial client handoff & interactive pricing' },
  { id: 'crt_03', name: 'SEO Forensic Scout', ramCost: 120, category: 'Intel', description: 'Organic entity audit & backlink graph miner' },
  { id: 'crt_04', name: 'Client Portal Comm', ramCost: 85, category: 'UX', description: 'Real-time WebSocket client briefing feed' },
  { id: 'crt_05', name: 'Agentic Ads Swarm', ramCost: 210, category: 'Ops', description: 'Multi-channel B2B campaign ROI optimizer' },
  { id: 'crt_06', name: 'WebGPU Spatial Hub', ramCost: 315, category: 'Visual', description: 'Holographic 3D workspace turntable' },
];

export const MAX_RAM_ENVELOPE = 512; // 512MB Strict Worker / WASM Limit

export function TenantCartridgeManager() {
  const [activeCartridges, setActiveCartridges] = useState<string[]>(['crt_01', 'crt_02']);
  const [evictedNotice, setEvictedNotice] = useState<string | null>(null);
  const [isSwapping, setIsSwapping] = useState<boolean>(false);

  const currentRam = activeCartridges.reduce((acc, id) => {
    const cart = AVAILABLE_CARTRIDGES.find((c) => c.id === id);
    return acc + (cart?.ramCost || 0);
  }, 0);

  const ramPercentage = Math.min(100, Math.round((currentRam / MAX_RAM_ENVELOPE) * 100));

  const handleToggleCartridge = (id: string) => {
    if (activeCartridges.includes(id)) {
      setActiveCartridges((prev) => prev.filter((cId) => cId !== id));
      setEvictedNotice(null);
      return;
    }

    const targetCart = AVAILABLE_CARTRIDGES.find((c) => c.id === id);
    if (!targetCart) return;

    setIsSwapping(true);
    setEvictedNotice(null);

    setTimeout(() => {
      let updated = [...activeCartridges, id];
      let newRam = updated.reduce((acc, cId) => {
        const c = AVAILABLE_CARTRIDGES.find((item) => item.id === cId);
        return acc + (c?.ramCost || 0);
      }, 0);

      const evictedList: string[] = [];
      while (newRam > MAX_RAM_ENVELOPE && updated.length > 1) {
        const oldestId = updated[0];
        const oldestCart = AVAILABLE_CARTRIDGES.find((c) => c.id === oldestId);
        if (oldestCart) {
          evictedList.push(oldestCart.name);
        }
        updated = updated.slice(1);
        newRam = updated.reduce((acc, cId) => {
          const c = AVAILABLE_CARTRIDGES.find((item) => item.id === cId);
          return acc + (c?.ramCost || 0);
        }, 0);
      }

      setActiveCartridges(updated);
      setIsSwapping(false);

      if (evictedList.length > 0) {
        setEvictedNotice(
          `[LRU EVICTION INTERCEPT]: Evicted ${evictedList.join(', ')} to viking:// persistent block storage. Hardware envelope locked under 512MB.`
        );
      }
    }, 180);
  };

  const handleEvictAll = () => {
    setActiveCartridges([]);
    setEvictedNotice('All non-essential cartridges unmounted. Working set reset to baseline.');
  };

  return (
    <div className="w-full bg-[#050508] p-4 md:p-8 font-sans text-slate-200 border-2 border-camelot-gold/40 shadow-[6px_6px_0px_0px_#D4AF37] rounded-xl">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-6 mb-8 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-camelot-gold animate-pulse" />
            <span className="text-[10px] font-mono text-camelot-cyan tracking-[0.25em] uppercase">
              EXCALIBUR SHELL // MODULAR MULTI-TENANT CARTRIDGE RACK
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase mt-1">
            Tenant <span className="text-camelot-gold">Cartridge Hypervisor</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Hardware-Bounded Eviction Lifecycle &bull; 512MB WASM Envelope Protection
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleEvictAll}
            className="px-3 py-1.5 bg-[#0B0B0E] hover:bg-red-500/10 border border-slate-700 hover:border-red-500/50 text-slate-400 hover:text-red-300 font-mono text-xs uppercase tracking-wider transition-all"
          >
            FLUSH WORKER RAM
          </button>
          <span className="px-3 py-1.5 bg-smoke-800 border border-camelot-gold/40 text-camelot-gold font-mono text-xs font-bold uppercase tracking-wider">
            SLOTS: {activeCartridges.length}/{AVAILABLE_CARTRIDGES.length}
          </span>
        </div>
      </header>

      {/* Hardware RAM Envelope Gauge Bar */}
      <div className="bg-[#121217] border border-[#2A2A35] rounded-xl p-5 mb-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-3">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-camelot-gold" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              WASM WORKER RAM ENVELOPE:
            </span>
            <span className="text-xs font-mono text-slate-400">
              {currentRam} MB / {MAX_RAM_ENVELOPE} MB ({ramPercentage}%)
            </span>
          </div>

          <div className="text-[10px] font-mono text-slate-400 flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>HYPERVISOR STATUS: SCARCITY PROTOCOL ARMED</span>
          </div>
        </div>

        <div className="w-full h-3 bg-[#0B0B0E] rounded-full overflow-hidden border border-slate-700">
          <div
            className={`h-full transition-all duration-300 ${
              ramPercentage > 85
                ? 'bg-red-500'
                : ramPercentage > 60
                ? 'bg-amber-400'
                : 'bg-emerald-400'
            }`}
            style={{ width: `${ramPercentage}%` }}
          />
        </div>

        {evictedNotice && (
          <div className="mt-3 p-3 bg-amber-500/10 border border-amber-500/40 text-amber-300 text-xs font-mono rounded">
            {evictedNotice}
          </div>
        )}
      </div>

      {/* Cartridge Inventory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {AVAILABLE_CARTRIDGES.map((cart) => {
          const isActive = activeCartridges.includes(cart.id);
          const willExceed = !isActive && currentRam + cart.ramCost > MAX_RAM_ENVELOPE;

          return (
            <div
              key={cart.id}
              className={`p-5 rounded-xl border-2 transition-all flex flex-col justify-between ${
                isActive
                  ? 'border-camelot-gold bg-[#121217] shadow-[4px_4px_0px_0px_#D4AF37]'
                  : 'border-[#2A2A35] bg-[#0B0B0E] hover:border-slate-600'
              }`}
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-camelot-cyan">
                    {cart.category}
                  </span>
                  <span
                    className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${
                      isActive
                        ? 'border-emerald-500/50 text-emerald-400 bg-emerald-500/10'
                        : 'border-slate-700 text-slate-500 bg-slate-900'
                    }`}
                  >
                    {isActive ? 'MOUNTED' : 'FROZEN'}
                  </span>
                </div>

                <h3 className="text-base font-black text-white uppercase tracking-tight">
                  {cart.name}
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  {cart.description}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-800 flex justify-between items-center">
                <span className="text-xs font-mono text-slate-400">
                  PAYLOAD: <span className="text-camelot-gold font-bold">{cart.ramCost} MB</span>
                </span>

                <button
                  type="button"
                  onClick={() => handleToggleCartridge(cart.id)}
                  disabled={isSwapping}
                  className={`px-4 py-1.5 text-xs font-mono font-bold uppercase tracking-wider rounded transition-all ${
                    isActive
                      ? 'bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40'
                      : 'bg-camelot-gold hover:bg-yellow-400 text-black shadow-[2px_2px_0px_0px_#000000]'
                  }`}
                >
                  {isActive ? 'UNMOUNT' : willExceed ? 'SWAP & MOUNT' : 'MOUNT'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <footer className="mt-8 pt-4 border-t border-camelot-gold/10 flex flex-col sm:flex-row justify-between items-center text-[10px] text-slate-500 font-mono gap-2">
        <span className="flex items-center gap-1.5">
          <Database className="w-3.5 h-3.5 text-camelot-gold" />
          Lady Mnemosyne State Freezer Active &bull; Viking WAL2 Block Storage
        </span>
        <span>
          ENVELOPE GOVERNOR: <span className="text-emerald-400 font-bold">512MB WASM LIMIT (STRICT)</span>
        </span>
      </footer>
    </div>
  );
}

export default TenantCartridgeManager;
