// SPDX-License-Identifier: MIT
// Sovereign Command Dashboard // Invisioned Command Nexus
// Authored under D.A.X. v10000.56 & Scabbard Cartridge Protocol
// Chromatic Palette: Obsidian (#050508, #0B0B0E), Slate (#121217, #2A2A35), Luxora Gold (#D4AF37), Cyan (#00E5FF)
// Zero-latency reactive agent telemetry

'use client';

import React, { useState, useEffect } from 'react';

export interface SwarmNode {
  id: string;
  role: string;
  status: 'ACTIVE' | 'IDLE' | 'ANALYZING';
  latency: number;
}

export function SovereignCommandDashboard() {
  const [nodes, setNodes] = useState<SwarmNode[]>([
    { id: 'NODE_1_SCOUT', role: 'Competitor Discovery', status: 'ACTIVE', latency: 14 },
    { id: 'NODE_3_SEO', role: 'Organic Forensic', status: 'ANALYZING', latency: 22 },
    { id: 'NODE_5_GROWTH', role: 'B2B Campaign ROI', status: 'IDLE', latency: 8 },
    { id: 'NODE_7_SYNTHESIS', role: 'Autonomous Copy Synthesis', status: 'ACTIVE', latency: 19 },
  ]);

  const [pipelineValue, setPipelineValue] = useState<number>(142500);

  // Simulate incoming agentic telemetry
  useEffect(() => {
    const timer = setInterval(() => {
      setNodes((prev) =>
        prev.map((node) => ({
          ...node,
          latency: Math.max(
            4,
            node.latency + (Math.random() > 0.5 ? 1 : -1) * Math.floor(Math.random() * 3)
          ),
          status:
            Math.random() > 0.85
              ? 'ACTIVE'
              : Math.random() > 0.5
              ? 'ANALYZING'
              : node.status,
        }))
      );
      setPipelineValue((prev) => prev + Math.floor(Math.random() * 500));
    }, 2500);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full bg-[#050508] p-4 md:p-8 font-sans text-slate-200 border-2 border-gold/40 shadow-[6px_6px_0px_0px_#D4AF37]">
      {/* Top Telemetry Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-6 mb-8 gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase">
            Invisioned <span className="text-[#D4AF37]">Command Nexus</span>
          </h1>
          <span className="text-xs font-mono text-[#00E5FF] tracking-widest uppercase flex items-center gap-2 mt-1">
            {/* Network Icon SVG */}
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="16" y="16" width="6" height="6" rx="1" />
              <rect x="2" y="16" width="6" height="6" rx="1" />
              <rect x="9" y="2" width="6" height="6" rx="1" />
              <path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3" />
              <path d="M12 12V8" />
            </svg>
            Agentic Swarm Topology: Online
          </span>
        </div>

        <div className="flex items-center gap-6 font-mono text-xs">
          <div className="flex flex-col text-right">
            <span className="text-slate-500">EDGE_NODE</span>
            <span className="text-white">CLEVELAND_US_EAST</span>
          </div>
          <div className="h-8 w-px bg-[#2A2A35]" />
          <div className="flex flex-col text-right">
            <span className="text-slate-500">SYSTEM_MEMORY</span>
            <span className="text-emerald-400">4.9GB / 8.0GB (Sovereign Hub)</span>
          </div>
        </div>
      </header>

      {/* Bento Grid Architecture */}
      <main className="grid grid-cols-1 md:grid-cols-12 gap-6 auto-rows-[minmax(180px,auto)]">
        {/* Pipeline Value Widget (Spans 4 cols) */}
        <div className="md:col-span-4 bg-[#121217] border border-[#2A2A35] rounded-2xl p-6 flex flex-col justify-between shadow-[0_10px_30px_rgba(0,0,0,0.5)] transition-all duration-300 hover:border-gold/50 hover:shadow-[0_10px_30px_rgba(212,175,55,0.15)]">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Active Pipeline (B2B)</span>
            {/* TrendingUp Icon SVG */}
            <svg className="w-4 h-4 text-[#D4AF37]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
              <polyline points="17 6 23 6 23 12" />
            </svg>
          </div>
          <div>
            <span className="text-4xl font-black text-white tracking-tighter">
              ${pipelineValue.toLocaleString()}
            </span>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-[10px] font-mono bg-[#D4AF37]/10 text-[#D4AF37] px-2 py-1 rounded border border-[#D4AF37]/30">
                +12% vs LAST_MONTH
              </span>
              <span className="text-[10px] font-mono text-emerald-400">P2P Mesh Verified</span>
            </div>
          </div>
        </div>

        {/* Swarm Roster (Spans 8 cols) */}
        <div className="md:col-span-8 bg-[#121217] border border-[#2A2A35] rounded-2xl p-6 flex flex-col shadow-[0_10px_30px_rgba(0,0,0,0.5)] transition-all duration-300 hover:border-gold/50 hover:shadow-[0_10px_30px_rgba(212,175,55,0.15)]">
          <div className="flex justify-between items-center text-slate-400 mb-4 border-b border-[#2A2A35] pb-2">
            <span className="text-xs font-mono uppercase flex items-center gap-2">
              {/* Users Icon SVG */}
              <svg className="w-4 h-4 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              Omni-Agency Nodes
            </span>
            <span className="text-xs font-mono text-[#D4AF37]">D.A.X. ROUTING</span>
          </div>

          <div className="flex flex-col gap-3">
            {nodes.map((node) => (
              <div
                key={node.id}
                className="flex items-center justify-between bg-[#0B0B0E] p-3 rounded-lg border border-white/5 hover:border-gold/30 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-2.5 h-2.5 rounded-full ${
                      node.status === 'ACTIVE'
                        ? 'bg-emerald-400 animate-pulse'
                        : node.status === 'ANALYZING'
                        ? 'bg-[#D4AF37] animate-pulse'
                        : 'bg-slate-600'
                    }`}
                  />
                  <div>
                    <span className="text-sm font-bold text-white block">{node.role}</span>
                    <span className="text-[10px] font-mono text-slate-500 uppercase">{node.id}</span>
                  </div>
                </div>

                <div className="flex items-center gap-4 font-mono text-xs">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      node.status === 'ACTIVE'
                        ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10'
                        : node.status === 'ANALYZING'
                        ? 'border-[#D4AF37]/40 text-[#D4AF37] bg-[#D4AF37]/10'
                        : 'border-slate-700 text-slate-400 bg-slate-800'
                    }`}
                  >
                    {node.status}
                  </span>
                  <span className="text-slate-400 w-16 text-right">
                    {node.latency}ms <span className="text-slate-600">RTT</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Security & Shield Widget (Spans 6 cols) */}
        <div className="md:col-span-6 bg-[#121217] border border-[#2A2A35] rounded-2xl p-6 flex flex-col justify-between">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase">Perimeter Verification</span>
            {/* ShieldCheck Icon SVG */}
            <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
              <path d="m9 12 2 2 4-4" />
            </svg>
          </div>
          <div className="mt-4">
            <div className="text-lg font-bold text-white uppercase tracking-wide">
              Zero-Trust APEE v7.0
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Kyber-768 mTLS tunnel active on Tailscale dark mesh. Zero unverified AST code injection.
            </p>
            <div className="mt-3 flex items-center gap-2">
              <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded">
                SIR_SENTINEL: ARMED
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-violet-500/10 text-violet-300 border border-violet-500/30 rounded">
                Z3 THEOREM: PASS
              </span>
            </div>
          </div>
        </div>

        {/* Telemetry & Database Hub Widget (Spans 6 cols) */}
        <div className="md:col-span-6 bg-[#121217] border border-[#2A2A35] rounded-2xl p-6 flex flex-col justify-between">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase">WorldTree Memory Mesh</span>
            {/* Database Icon SVG */}
            <svg className="w-4 h-4 text-[#00E5FF]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <ellipse cx="12" cy="5" rx="9" ry="3" />
              <path d="M3 5V19A9 3 0 0 0 21 19V5" />
              <path d="M3 12A9 3 0 0 0 21 12" />
            </svg>
          </div>
          <div className="mt-4">
            <div className="text-lg font-bold text-white uppercase tracking-wide">
              SQLite-Vec + CloudBrain KNN
            </div>
            <p className="text-xs text-slate-400 mt-1">
              O(1) episodic retrieval enabled. Sub-50ms latency across 275+ federated notebooks.
            </p>
            <div className="mt-3 flex items-center gap-2">
              <span className="text-[10px] font-mono px-2 py-0.5 bg-[#00E5FF]/10 text-[#00E5FF] border border-[#00E5FF]/30 rounded">
                LADY_MNEMOSYNE: LIVING
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-gold/10 text-gold-royal border border-gold/30 rounded">
                VKG CRYSTALS: SYNCED
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default SovereignCommandDashboard;
