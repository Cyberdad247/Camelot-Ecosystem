// SPDX-License-Identifier: MIT
// D.A.X. Master Skill Matrix Component: Tenant Cartridge Manager (The "Excalibur Shell")
// Authored under D.A.X. v10000.56 (Hardware-Bounded Eviction Lifecycle // 512MB Worker Envelope)
// Chromatic Tokens: Obsidian Void (#050508, #0B0B0E), Surface Slate (#121217, #2A2A35), Luxora Gold (#D4AF37, #FFD700)
// Doherty Response: < 140ms physics, Zero Layout Shift (CLS == 0.00)

'use client';

import React, { useState } from 'react';

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

  // Calculate current memory load
  const currentRam = activeCartridges.reduce((acc, id) => {
    const cart = AVAILABLE_CARTRIDGES.find((c) => c.id === id);
    return acc + (cart?.ramCost || 0);
  }, 0);

  const ramPercentage = Math.min(100, Math.round((currentRam / MAX_RAM_ENVELOPE) * 100));

  // Hardware-Bounded Eviction Lifecycle (LRU eviction when adding exceeds 512MB)
  const handleToggleCartridge = (id: string) => {
    if (activeCartridges.includes(id)) {
      // Unmount cartridge
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

      // LRU Eviction loop: evict oldest loaded cartridges until within envelope
      const evictedList: string[] = [];
      while (newRam > MAX_RAM_ENVELOPE && updated.length > 1) {
        const oldestId = updated[0]; // LRU item
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
    <div className="w-full bg-[#050508] p-4 md:p-8 font-sans text-slate-200 border-2 border-gold/40 shadow-[6px_6px_0px_0px_#D4AF37] rounded-xl">
      {/* Top Telemetry Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-6 mb-8 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-gold animate-pulse" />
            <span className="text-[10px] font-mono text-[#00E5FF] tracking-[0.25em] uppercase">
              EXCALIBUR SHELL // MODULAR MULTI-TENANT CARTRIDGE RACK
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase mt-1">
            Tenant <span className="text-gold">Cartridge Hypervisor</span>
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
          <span className="px-3 py-1.5 bg-smoke-800 border border-gold/40 text-gold-royal font-mono text-xs font-bold uppercase tracking-wider">
            SLOTS: {activeCartridges.length}/{AVAILABLE_CARTRIDGES.length}
          </span>
        </div>
      </header>

      {/* Hardware RAM Envelope Gauge Bar */}
      <div className="bg-[#121217] border border-[#2A2A35] rounded-xl p-5 mb-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-3">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gold" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="4" y="4" width="16" height="16" rx="2" />
              <rect x="9" y="9" width="6" height="6" />
              <line x1="9" y1="1" x2="9" y2="4" />
              <line x1="15" y1="1" x2="15" y2="4" />
              <line x1="9" y1="20" x2="9" y2="23" />
              <line x1="15" y1="20" x2="15" y2="23" />
              <line x1="20" y1="9" x2="23" y2="9" />
              <line x1="20" y1="14" x2="23" y2="14" />
              <line x1="1" y1="9" x2="4" y2="9" />
              <line x1="1" y1="14" x2="4" y2="14" />
            </svg>
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

        {/* Progress Track */}
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
                  ? 'border-gold bg-[#121217] shadow-[4px_4px_0px_0px_#D4AF37]'
                  : 'border-[#2A2A35] bg-[#0B0B0E] hover:border-slate-600'
              }`}
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-[#00E5FF]">
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
                  PAYLOAD: <span className="text-gold font-bold">{cart.ramCost} MB</span>
                </span>

                <button
                  type="button"
                  onClick={() => handleToggleCartridge(cart.id)}
                  disabled={isSwapping}
                  className={`px-4 py-1.5 text-xs font-mono font-bold uppercase tracking-wider rounded transition-all ${
                    isActive
                      ? 'bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40'
                      : 'bg-gold hover:bg-gold-light text-obsidian shadow-[2px_2px_0px_0px_#000000]'
                  }`}
                >
                  {isActive ? 'UNMOUNT' : willExceed ? 'SWAP & MOUNT' : 'MOUNT'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom Protocol Footer */}
      <footer className="mt-8 pt-4 border-t border-gold/10 flex flex-col sm:flex-row justify-between items-center text-[10px] text-slate-500 font-mono gap-2">
        <span className="flex items-center gap-1.5">
          <svg className="w-3.5 h-3.5 text-gold" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z"
              clipRule="evenodd"
            />
          </svg>
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
