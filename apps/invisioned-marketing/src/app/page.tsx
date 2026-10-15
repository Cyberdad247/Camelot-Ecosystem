'use client';

import React, { useState } from 'react';
import { MidasLeadCapture } from '../components/MidasLeadCapture';
import { SovereignCommandDashboard } from '../components/SovereignCommandDashboard';
import { InteractiveB2BProposal } from '../components/InteractiveB2BProposal';
import { TenantCartridgeManager } from '../components/TenantCartridgeManager';
import { OmniFulfillmentCanvas } from '../components/OmniFulfillmentCanvas';
import { HolographicClientOracle } from '../components/HolographicClientOracle';
import { ClientOraclePortal } from '../components/ClientOraclePortal';

type ModuleTab =
  | 'midas'
  | 'command'
  | 'proposal'
  | 'tenants'
  | 'canvas'
  | 'oracle_avatar'
  | 'oracle_portal';

interface TabConfig {
  id: ModuleTab;
  title: string;
  badge: string;
  knight: string;
}

const TABS: TabConfig[] = [
  { id: 'midas', title: 'Midas Lead Funnel', badge: 'INBOUND', knight: 'SIR_VISAGE' },
  { id: 'command', title: 'Command Nexus', badge: 'SWARM', knight: 'ANYA_Ω' },
  { id: 'proposal', title: 'B2B Proposal', badge: 'CLOSE', knight: 'MERLIN_Ω' },
  { id: 'tenants', title: 'Cartridge Rack', badge: 'SCALING', knight: 'SIR_HYDRON' },
  { id: 'canvas', title: 'Fulfillment DAG', badge: 'FACTORY', knight: 'SIR_STITCH' },
  { id: 'oracle_avatar', title: 'Voice Avatar', badge: 'AUDIO', knight: 'SIR_SONUS' },
  { id: 'oracle_portal', title: 'VIP Client Portal', badge: 'PORTAL', knight: 'LADY_APIS' },
];

export default function InvisionedMarketingHome() {
  const [activeTab, setActiveTab] = useState<ModuleTab>('command');

  return (
    <div className="min-h-screen bg-[#0B0B0E] text-slate-100 flex flex-col font-mono selection:bg-[#D4AF37]/30 selection:text-[#D4AF37]">
      {/* Top Banner & Header */}
      <header className="border-b border-[#D4AF37]/30 bg-[#121217] px-6 py-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 border-2 border-[#D4AF37] flex items-center justify-center font-black text-[#D4AF37] shadow-[2px_2px_0px_#D4AF37] bg-black text-sm">
            IM
          </div>
          <div>
            <div className="text-[10px] text-[#9D4EDD] font-bold tracking-widest uppercase">
              CAMELOT-OS // ENTERPRISE SOVEREIGN DEPLOYMENT
            </div>
            <h1 className="text-lg md:text-xl font-black text-slate-100 uppercase tracking-tight">
              Invisioned Marketing Inc. <span className="text-[#D4AF37]">Digital Factory</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3 self-end md:self-auto">
          <div className="px-3 py-1 bg-black border border-emerald-500/50 text-emerald-400 text-xs font-bold uppercase flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            FACTORY ENGINE ONLINE
          </div>
          <div className="px-3 py-1 bg-[#181820] border border-[#D4AF37]/50 text-[#D4AF37] text-xs font-bold uppercase">
            RAM: &lt;4GB BOUNDED
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-black/80 border-b border-slate-800 px-6 py-2 overflow-x-auto">
        <div className="flex gap-2 min-w-max">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-xs font-bold uppercase transition-all flex items-center gap-2 border ${
                  isActive
                    ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37] shadow-[2px_2px_0px_#D4AF37]'
                    : 'border-slate-800 bg-[#121217] text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <span>{tab.title}</span>
                <span
                  className={`text-[9px] px-1.5 py-0.2 font-mono ${
                    isActive ? 'bg-[#D4AF37] text-black font-black' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {tab.badge}
                </span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Workspace Mount */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
        {activeTab === 'midas' && <MidasLeadCapture />}
        {activeTab === 'command' && <SovereignCommandDashboard />}
        {activeTab === 'proposal' && <InteractiveB2BProposal />}
        {activeTab === 'tenants' && <TenantCartridgeManager />}
        {activeTab === 'canvas' && <OmniFulfillmentCanvas />}
        {activeTab === 'oracle_avatar' && <HolographicClientOracle />}
        {activeTab === 'oracle_portal' && <ClientOraclePortal />}
      </main>

      {/* Footer / Provenance Bar */}
      <footer className="border-t border-slate-900 bg-[#0B0B0E] px-6 py-4 text-center text-xs text-slate-500 font-mono">
        <div>
          Invisioned Marketing Inc. &bull; Sovereign Agentic Monorepo &bull; Crystal ID: <span className="text-[#D4AF37]">VKG_5BB18D058C279F76</span> &bull; Anya Gate Verified
        </div>
      </footer>
    </div>
  );
}
