// SPDX-License-Identifier: MIT
// Sovereign Command Dashboard // Invisioned Command Nexus (Bifrost Board Edition)
// Compatible with lucide-react & framer-motion

import React, { useState, useEffect } from 'react';
import { Activity, Network, Zap, ShieldCheck, Database, TrendingUp, Users } from 'lucide-react';

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
    <div className="w-full bg-[#050508] p-4 md:p-8 font-sans text-slate-200 border-2 border-camelot-gold/40 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.8)]">
      {/* Top Telemetry Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-6 mb-8 gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase">
            Invisioned <span className="text-camelot-gold">Command Nexus</span>
          </h1>
          <span className="text-xs font-mono text-camelot-cyan tracking-widest uppercase flex items-center gap-2 mt-1">
            <Network className="w-3.5 h-3.5 text-camelot-cyan" /> Agentic Swarm Topology: Online
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
        <div className="md:col-span-4 bg-[#121217] border border-[#2A2A35] rounded-2xl p-6 flex flex-col justify-between shadow-[0_10px_30px_rgba(0,0,0,0.5)] transition-all duration-300 hover:border-camelot-gold/50 hover:shadow-[0_10px_30px_rgba(212,175,55,0.15)]">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Active Pipeline (B2B)</span>
            <TrendingUp className="w-4 h-4 text-camelot-gold" />
          </div>
          <div>
            <span className="text-4xl font-black text-white tracking-tighter">
              ${pipelineValue.toLocaleString()}
            </span>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-[10px] font-mono bg-camelot-gold/10 text-camelot-gold px-2 py-1 rounded border border-camelot-gold/30">
                +12% vs LAST_MONTH
              </span>
              <span className="text-[10px] font-mono text-emerald-400">P2P Mesh Verified</span>
            </div>
          </div>
        </div>

        {/* Swarm Roster (Spans 8 cols) */}
        <div className="md:col-span-8 bg-[#121217] border border-[#2A2A35] rounded-2xl p-6 flex flex-col shadow-[0_10px_30px_rgba(0,0,0,0.5)] transition-all duration-300 hover:border-camelot-gold/50 hover:shadow-[0_10px_30px_rgba(212,175,55,0.15)]">
          <div className="flex justify-between items-center text-slate-400 mb-4 border-b border-[#2A2A35] pb-2">
            <span className="text-xs font-mono uppercase flex items-center gap-2">
              <Users className="w-4 h-4 text-slate-300" /> Omni-Agency Nodes
            </span>
            <span className="text-xs font-mono text-camelot-gold">D.A.X. ROUTING</span>
          </div>

          <div className="flex flex-col gap-3">
            {nodes.map((node) => (
              <div
                key={node.id}
                className="flex items-center justify-between bg-[#0B0B0E] p-3 rounded-lg border border-white/5 hover:border-camelot-gold/30 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-2.5 h-2.5 rounded-full ${
                      node.status === 'ACTIVE'
                        ? 'bg-emerald-400 animate-pulse'
                        : node.status === 'ANALYZING'
                        ? 'bg-camelot-gold animate-pulse'
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
                        ? 'border-camelot-gold/40 text-camelot-gold bg-camelot-gold/10'
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
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
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
              <span className="text-[10px] font-mono px-2 py-0.5 bg-camelot-violet/10 text-camelot-violet border border-camelot-violet/30 rounded">
                Z3 THEOREM: PASS
              </span>
            </div>
          </div>
        </div>

        {/* Telemetry & Database Hub Widget (Spans 6 cols) */}
        <div className="md:col-span-6 bg-[#121217] border border-[#2A2A35] rounded-2xl p-6 flex flex-col justify-between">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-mono uppercase">WorldTree Memory Mesh</span>
            <Database className="w-4 h-4 text-camelot-cyan" />
          </div>
          <div className="mt-4">
            <div className="text-lg font-bold text-white uppercase tracking-wide">
              SQLite-Vec + CloudBrain KNN
            </div>
            <p className="text-xs text-slate-400 mt-1">
              O(1) episodic retrieval enabled. Sub-50ms latency across 275+ federated notebooks.
            </p>
            <div className="mt-3 flex items-center gap-2">
              <span className="text-[10px] font-mono px-2 py-0.5 bg-camelot-cyan/10 text-camelot-cyan border border-camelot-cyan/30 rounded">
                LADY_MNEMOSYNE: LIVING
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-camelot-gold/10 text-camelot-gold border border-camelot-gold/30 rounded">
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
