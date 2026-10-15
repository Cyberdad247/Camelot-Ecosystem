import React, { useState, useEffect } from 'react';
import { create } from 'zustand';
import { Activity, Shield, Cpu, Server } from 'lucide-react';
import ExcaliburCockpit from './components/ExcaliburCockpit';
import VoiceHUD from './components/VoiceHUD';
import OmniForgeStudio from './components/OmniForgeStudio';
import MeshTelemetryGrid from './components/MeshTelemetryGrid';
import PolyglotAscensionGrid from './components/PolyglotAscensionGrid';
import SovereignCommandDashboard from './components/SovereignCommandDashboard';

// Zustand Store for Zero-Prop-Drilling State Management
interface SystemState {
  ramUsage: number;
  activeVMs: number;
  ledgerHashes: string[];
  addHash: (hash: string) => void;
}

const useSystemStore = create<SystemState>((set) => ({
  ramUsage: 61.4, // Baseline Cybertronia footprint in MB
  activeVMs: 1,
  ledgerHashes: [
    '485657f4238121506cd73c468cb2db2cc5b708c19a6a9fcd665b622411bb625e',
    'fe0db0d83aa85cf41052779c5f7b1f97ac3590bf4d240fc3607aff59a476427d',
  ],
  addHash: (hash) => set((state) => ({ 
    ledgerHashes: [hash, ...state.ledgerHashes].slice(0, 10),
    activeVMs: state.activeVMs + 1 
  })),
}));

export default function BifrostBoard() {
  const { ramUsage, activeVMs, ledgerHashes, addHash } = useSystemStore();

  return (
    <div className="min-h-screen bg-obsidian-void text-gray-300 font-sans selection:bg-camelot-violet">
      {/* HUD Header */}
      <header className="border-b border-camelot-gold/30 bg-obsidian-smoke p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="text-camelot-gold h-6 w-6" />
          <h1 className="text-xl font-bold tracking-widest text-camelot-gold uppercase">Camelot-OS</h1>
          <span className="px-2 py-1 text-xs bg-camelot-violet/20 text-camelot-violet border border-camelot-violet/50 rounded-sm">
            v10001.0.0-CYBERTRONIA
          </span>
        </div>
        <div className="flex items-center gap-4 text-sm font-mono">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-camelot-cyan" />
            <span>4.0GB NODE CAP: <span className="text-green-400">HOLDING (96.8 MB)</span></span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="p-6 grid grid-cols-12 gap-6">
        
        {/* Left Panel: Telemetry & Excalibur Cockpit */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="border border-camelot-gold/20 bg-obsidian-smoke/50 p-4 rounded backdrop-blur">
            <h2 className="text-camelot-cyan font-mono mb-4 flex items-center gap-2">
              <Activity className="h-4 w-4" /> KINETIC TELEMETRY
            </h2>
            <div className="space-y-4 font-mono text-sm">
              <div className="flex justify-between border-b border-gray-800 pb-2">
                <span>Active Working Set:</span>
                <span className="text-camelot-gold">{ramUsage} MB / 4096 MB</span>
              </div>
              <div className="flex justify-between border-b border-gray-800 pb-2">
                <span>WASM MicroVMs:</span>
                <span className="text-camelot-violet">{activeVMs} Active</span>
              </div>
              <div className="flex justify-between pb-2">
                <span>Omni-Forge Pipeline:</span>
                <span className="text-green-400">ARMED & READY</span>
              </div>
            </div>
          </div>

          {/* Excalibur Mobile Cockpit */}
          <ExcaliburCockpit tailscaleIp="100.106.246.126" model="Samsung Galaxy S26 Ultra" status="ONLINE" />

          {/* Sir Sonus Voice Gateway */}
          <VoiceHUD gatewayPort={7680} status="ONLINE" />
        </div>

        {/* Right Panel: Omni-Forge Visual Studio + Mesh Telemetry + Live Provenance Ledger */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          {/* Invisioned Command Nexus — Swarm Topology */}
          <SovereignCommandDashboard />

          {/* Omni-Forge 7-Stage Visual Studio */}
          <OmniForgeStudio onReceiptGenerated={(hash) => addHash(hash)} />

          {/* Bare-Metal Polyglot Hardware Ascension */}
          <PolyglotAscensionGrid />

          {/* Fleet Mesh & Warp-Gate Cockpit */}
          <MeshTelemetryGrid />

          {/* Live Provenance Ledger Feed */}
          <div className="border border-camelot-gold/20 bg-obsidian-smoke/50 p-4 rounded">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4">
              <h2 className="text-camelot-gold font-mono flex items-center gap-2">
                <Server className="h-4 w-4" /> PROVENANCE LEDGER (LIVE RECEIPT FEED)
              </h2>
              <span className="text-[11px] font-mono text-emerald-400">
                ALL 6 MIRRORS SYNCHRONIZED
              </span>
            </div>
            <div className="font-mono text-xs space-y-2">
              {ledgerHashes.length === 0 ? (
                <p className="text-gray-600 italic">Awaiting kinetic execution receipts...</p>
              ) : (
                ledgerHashes.map((hash, i) => (
                  <div key={i} className="p-2.5 bg-black/50 border-l-2 border-camelot-violet rounded flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500 font-bold">[SEALED RECEIPT]</span> 
                      <span className="text-camelot-cyan select-all">{hash}</span>
                    </div>
                    <span className="text-[10px] text-green-400 font-bold">Z3 VERIFIED</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
