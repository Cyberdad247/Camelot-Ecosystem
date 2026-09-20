// SPDX-License-Identifier: MIT
'use client';

import React, { useState } from 'react';

export interface CartridgeTile {
  id: string;
  name: string;
  category: 'audio' | 'finance' | 'security' | 'marketing' | 'mesh';
  version: string;
  status: 'OFFLINE' | 'RUNNING' | 'APPROVAL_PENDING';
  author: string;
  accent: string;
  icon: string;
}

const INITIAL_CARTRIDGES: CartridgeTile[] = [
  {
    id: 'cart_kba',
    name: 'Kickbox Audio (KBA)',
    category: 'audio',
    version: 'v1.4.2',
    status: 'RUNNING',
    author: 'Cyberdad247',
    accent: '#D4AF37', // Luxora Gold
    icon: '🎙️',
  },
  {
    id: 'cart_finance',
    name: 'Finance Ledger Engine',
    category: 'finance',
    version: 'v2.1.0',
    status: 'RUNNING',
    author: 'Vizion Wealth',
    accent: '#D4AF37',
    icon: '💰',
  },
  {
    id: 'cart_email',
    name: 'Ravenry Mail Cartridge',
    category: 'mesh',
    version: 'v1.0.8',
    status: 'APPROVAL_PENDING',
    author: 'Sir Forge',
    accent: '#6B3FA0', // Royal Purple
    icon: '✉️',
  },
  {
    id: 'cart_sms',
    name: 'Fonoster PBX / SMS Hub',
    category: 'mesh',
    version: 'v0.9.5',
    status: 'OFFLINE',
    author: 'Sir Sonus',
    accent: '#00FF66', // Emerald Green
    icon: '📡',
  },
  {
    id: 'cart_hyperbolic',
    name: 'Hyperbolic Chamber (Eval)',
    category: 'security',
    version: 'v1.0.0',
    status: 'RUNNING',
    author: 'Sir Gideon',
    accent: '#D4AF37',
    icon: '⚡',
  },
  {
    id: 'cart_aeo',
    name: 'Videneptus SkillGraph4',
    category: 'marketing',
    version: 'v1.1.2',
    status: 'RUNNING',
    author: 'Knight Strategos',
    accent: '#6B3FA0',
    icon: '🧠',
  },
];

export function DesktopGrid() {
  const [cartridges, setCartridges] = useState<CartridgeTile[]>(INITIAL_CARTRIDGES);
  const [selectedCartridge, setSelectedCartridge] = useState<CartridgeTile | null>(null);

  const toggleStatus = (id: string) => {
    setCartridges((prev) =>
      prev.map((c) => {
        if (c.id !== id) return c;
        const nextStatus =
          c.status === 'RUNNING'
            ? 'OFFLINE'
            : c.status === 'OFFLINE'
            ? 'RUNNING'
            : 'RUNNING';
        return { ...c, status: nextStatus };
      })
    );
  };

  return (
    <div className="w-full bg-obsidian text-white p-6 font-sans">
      <div className="flex items-center justify-between border-b border-gold/30 pb-4 mb-6">
        <div>
          <h2 className="text-2xl font-display text-gold font-bold tracking-wider flex items-center gap-2">
            <span>♜</span> CAMELOT-OS DESKTOP GRID
          </h2>
          <p className="text-xs text-white/50 uppercase tracking-widest mt-1">
            Windows-Like Native Cartridge Grid · Drag-and-Drop Activation
          </p>
        </div>
        <div className="flex gap-3">
          <span className="px-3 py-1 bg-smoke-800 border border-gold/30 rounded text-xs text-gold">
            ACTIVE: {cartridges.filter((c) => c.status === 'RUNNING').length}
          </span>
          <span className="px-3 py-1 bg-smoke-800 border border-purple-500/30 rounded text-xs text-purple-400">
            PENDING: {cartridges.filter((c) => c.status === 'APPROVAL_PENDING').length}
          </span>
        </div>
      </div>

      {/* 3-Column Native Windows-Like Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cartridges.map((cartridge) => {
          const isRunning = cartridge.status === 'RUNNING';
          const isPending = cartridge.status === 'APPROVAL_PENDING';

          return (
            <div
              key={cartridge.id}
              onClick={() => setSelectedCartridge(cartridge)}
              className={`relative bg-smoke-900/90 border rounded-lg p-5 transition-all cursor-pointer hover:scale-[1.02] shadow-lg ${
                isRunning
                  ? 'border-gold/60 shadow-gold/10'
                  : isPending
                  ? 'border-purple-500/60 shadow-purple-500/10'
                  : 'border-white/10 opacity-70'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-3xl p-2 bg-obsidian border border-white/10 rounded">
                    {cartridge.icon}
                  </span>
                  <div>
                    <h3 className="font-bold text-sm text-gold-light">{cartridge.name}</h3>
                    <p className="text-[11px] text-white/40">{cartridge.author}</p>
                  </div>
                </div>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${
                    isRunning
                      ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40'
                      : isPending
                      ? 'bg-purple-950/80 text-purple-300 border-purple-500/40'
                      : 'bg-smoke-800 text-white/40 border-white/10'
                  }`}
                >
                  {cartridge.status}
                </span>
              </div>

              <div className="mt-4 flex items-center justify-between border-t border-white/5 pt-3">
                <span className="text-xs text-white/40 font-mono">{cartridge.version}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleStatus(cartridge.id);
                  }}
                  className={`px-3 py-1 text-xs font-semibold rounded transition-colors ${
                    isRunning
                      ? 'bg-red-950/80 text-red-300 hover:bg-red-900 border border-red-500/30'
                      : 'bg-gold/20 text-gold hover:bg-gold/30 border border-gold/40'
                  }`}
                >
                  {isRunning ? 'DEACTIVATE' : 'ACTIVATE'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Cartridge Detail Modal */}
      {selectedCartridge && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-smoke-900 border border-gold/40 rounded-lg max-w-md w-full p-6 shadow-2xl">
            <div className="flex justify-between items-center border-b border-gold/20 pb-3">
              <h4 className="text-gold font-bold text-lg flex items-center gap-2">
                <span>{selectedCartridge.icon}</span> {selectedCartridge.name}
              </h4>
              <button
                onClick={() => setSelectedCartridge(null)}
                className="text-white/40 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>
            <div className="py-4 space-y-2 text-sm text-white/70">
              <p><strong>Category:</strong> {selectedCartridge.category.toUpperCase()}</p>
              <p><strong>Version:</strong> {selectedCartridge.version}</p>
              <p><strong>Status:</strong> {selectedCartridge.status}</p>
              <p><strong>Author:</strong> {selectedCartridge.author}</p>
              <p className="text-xs text-white/40 font-mono mt-2">
                WASI 0.2 Sandbox · cgroups v2 Memory Cap 512M · Gideon Verified
              </p>
            </div>
            <div className="pt-3 border-t border-white/10 flex justify-end gap-3">
              <button
                onClick={() => setSelectedCartridge(null)}
                className="px-4 py-2 text-xs bg-smoke-800 text-white/70 rounded hover:bg-smoke-700"
              >
                CLOSE
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
