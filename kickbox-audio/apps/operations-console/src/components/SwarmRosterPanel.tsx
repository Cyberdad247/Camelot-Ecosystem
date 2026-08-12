'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

export interface SwarmAgentMember {
  id: string;
  name: string;
  role: string;
  domain: string;
  status: 'ACTIVE' | 'BUSY' | 'IDLE';
  task: string;
}

const SWARM_ROSTER_AGENTS: SwarmAgentMember[] = [
  { id: 'agent_malik', name: 'Malik', role: 'Chief of Staff', domain: 'Executive', status: 'ACTIVE', task: 'Compiling the daily Sovereign briefing' },
  { id: 'agent_jalen', name: 'Jalen', role: 'Calendar', domain: 'Executive', status: 'IDLE', task: '3 events scheduled today' },
  { id: 'agent_aaliyah', name: 'Aaliyah', role: 'Email', domain: 'Comms', status: 'BUSY', task: 'Triaging 14 inbound threads' },
  { id: 'agent_marcus', name: 'Marcus', role: 'Property', domain: 'Property', status: 'ACTIVE', task: 'Sandusky portfolio review' },
  { id: 'agent_tyrell', name: 'Tyrell', role: 'Maintenance', domain: 'Property', status: 'BUSY', task: '2 work orders dispatched' },
  { id: 'agent_nia', name: 'Nia', role: 'Rent', domain: 'Finance', status: 'ACTIVE', task: 'Rent roll reconciled · 96% collected' },
  { id: 'agent_isaiah', name: 'Isaiah', role: 'Streaming', domain: 'Streaming', status: 'ACTIVE', task: 'Edge nodes nominal · 2.1k live' },
  { id: 'agent_chloe', name: 'Chloe', role: 'Billing', domain: 'Finance', status: 'IDLE', task: 'Next invoice run in 4 days' },
];

export function SwarmRosterPanel() {
  const [agents, setAgents] = useState<SwarmAgentMember[]>(SWARM_ROSTER_AGENTS);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('agent_malik');

  const activeCount = agents.filter((a) => a.status === 'ACTIVE' || a.status === 'BUSY').length;
  const selectedAgent = agents.find((a) => a.id === selectedAgentId) || agents[0];

  const statusBadges = {
    ACTIVE: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
    BUSY: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
    IDLE: 'bg-slate-800 text-slate-400 border-slate-700',
  };

  return (
    <div className="border-2 border-[#D4AF37]/40 bg-[#0B0B0E] p-6 shadow-[6px_6px_0px_0px_#9D4EDD] space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#D4AF37]/30 pb-4 gap-3">
        <div>
          <div className="text-[10px] text-[#9D4EDD] font-bold tracking-widest uppercase">
            SWARM ROSTER // OPERATIONAL AGENT MATRIX
          </div>
          <h2 className="text-xl font-black text-slate-100 uppercase mt-1">
            Active Swarm Roster
          </h2>
        </div>
        <div className="px-3 py-1 bg-slate-900 border border-[#D4AF37] text-[#D4AF37] text-xs font-bold uppercase flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>ROSTER STATUS: {activeCount}/{agents.length} ENGAGED</span>
        </div>
      </div>

      {/* Grid of 8 Swarm Agents */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((agent) => {
          const isSelected = agent.id === selectedAgentId;
          return (
            <motion.div
              key={agent.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedAgentId(agent.id)}
              className={`p-4 border-2 cursor-pointer transition-all ${
                isSelected
                  ? 'border-[#9D4EDD] bg-[#9D4EDD]/10 shadow-[4px_4px_0px_0px_#9D4EDD]'
                  : 'border-slate-800 bg-slate-950 hover:border-[#D4AF37]/60'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-[10px] font-extrabold text-[#D4AF37] uppercase">
                  {agent.name}
                </span>
                <span className={`text-[9px] px-1.5 py-0.5 font-bold border ${statusBadges[agent.status]}`}>
                  {agent.status}
                </span>
              </div>
              <div className="text-xs text-slate-300 font-bold truncate">
                {agent.role} · <span className="text-slate-400 text-[10px]">{agent.domain}</span>
              </div>
              <div className="text-[10px] text-slate-400 mt-2 line-clamp-2 italic">
                "{agent.task}"
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Selected Agent Console Details */}
      <div className="p-4 border border-slate-800 bg-slate-950 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="text-[10px] text-slate-500 uppercase">SELECTED AGENT CONSOLE:</div>
          <div className="text-sm font-bold text-[#D4AF37] mt-0.5">
            {selectedAgent.name} <span className="text-slate-400 text-xs">({selectedAgent.role} · {selectedAgent.domain})</span>
          </div>
          <div className="text-xs text-slate-300 mt-1">
            Current Task: <span className="text-emerald-400 font-bold">{selectedAgent.task}</span>
          </div>
        </div>

        <button
          onClick={() => {
            alert(`Opening Sovereign Console for ${selectedAgent.name} (${selectedAgent.role})...`);
          }}
          className="px-5 py-2.5 bg-[#9D4EDD] text-slate-950 font-black text-xs uppercase tracking-wider hover:bg-purple-400 transition-all shadow-[3px_3px_0px_0px_#D4AF37] active:translate-x-0.5 active:translate-y-0.5 cursor-pointer"
        >
          OPEN CONSOLE ({selectedAgent.name.toUpperCase()})
        </button>
      </div>
    </div>
  );
}
