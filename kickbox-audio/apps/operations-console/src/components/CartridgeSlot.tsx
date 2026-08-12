'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

export interface SaaSWorkflowPill {
  id: string;
  name: string;
  category: 'FINANCE' | 'GOVERNANCE' | 'TELEMETRY' | 'VOICE';
  status: 'ACTIVE' | 'HOT_SWAPPABLE' | 'STANDBY';
  runtime: 'RUST_WASM' | 'GO_NATIVE' | 'YAML_Z3' | 'WEBRTC_VAD';
  version: string;
}

const DEFAULT_PILLS: SaaSWorkflowPill[] = [
  {
    id: 'pill_crdt_ledger',
    name: 'WASM Ledger Engine',
    category: 'FINANCE',
    status: 'ACTIVE',
    runtime: 'RUST_WASM',
    version: 'v1.0.0-EXCALIBUR',
  },
  {
    id: 'pill_hitl_policy',
    name: 'Tenant 001 Policy Engine',
    category: 'GOVERNANCE',
    status: 'ACTIVE',
    runtime: 'YAML_Z3',
    version: 'v1.0.0-EXCALIBUR',
  },
  {
    id: 'pill_eagle_audit',
    name: 'EAGLE Speculative Draft',
    category: 'TELEMETRY',
    status: 'ACTIVE',
    runtime: 'RUST_WASM',
    version: 'v999.3-EAGLE',
  },
  {
    id: 'pill_bio_swarm',
    name: 'Bio-Kinetic Cellular Matrix',
    category: 'GOVERNANCE',
    status: 'ACTIVE',
    runtime: 'GO_NATIVE',
    version: 'v1000-EXCALIBUR-A',
  },
  {
    id: 'pill_bifrost_mesh',
    name: 'Bifrost Polyglot Mesh',
    category: 'TELEMETRY',
    status: 'ACTIVE',
    runtime: 'GO_NATIVE',
    version: 'v2.1.0-BAREMETAL',
  },
  {
    id: 'pill_vocal_hypervisor',
    name: 'LaKesha Voice Hypervisor',
    category: 'VOICE',
    status: 'HOT_SWAPPABLE',
    runtime: 'WEBRTC_VAD',
    version: 'v1.2.0-PCM',
  },
];

export function CartridgeSlot() {
  const [pills, setPills] = useState<SaaSWorkflowPill[]>(DEFAULT_PILLS);
  const [selectedPillId, setSelectedPillId] = useState<string>('pill_crdt_ledger');

  const toggleStatus = (id: string) => {
    setPills((prev) =>
      prev.map((pill) => {
        if (pill.id === id) {
          const nextStatus =
            pill.status === 'ACTIVE'
              ? 'HOT_SWAPPABLE'
              : pill.status === 'HOT_SWAPPABLE'
              ? 'STANDBY'
              : 'ACTIVE';
          return { ...pill, status: nextStatus };
        }
        return pill;
      })
    );
  };

  const selectedPill = pills.find((p) => p.id === selectedPillId) || pills[0];

  return (
    <div className="border-2 border-[#D4AF37]/40 bg-[#0B0B0E] p-6 shadow-[6px_6px_0px_0px_#D4AF37] space-y-6 font-mono">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#D4AF37]/30 pb-4 gap-3">
        <div>
          <div className="text-[10px] text-[#9D4EDD] font-bold tracking-widest uppercase">
            SCABBARD PROTOCOL // SAAS CARTRIDGE SLOT
          </div>
          <h2 className="text-xl font-black text-slate-100 uppercase mt-1">
            Hot-Swappable Workflow Pills
          </h2>
        </div>
        <div className="px-3 py-1 bg-slate-900 border border-[#D4AF37] text-[#D4AF37] text-xs font-bold uppercase">
          SLOT 01: LOADED ({pills.filter((p) => p.status === 'ACTIVE').length}/{pills.length} ACTIVE)
        </div>
      </div>

      {/* Pill Selector Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {pills.map((pill) => {
          const isSelected = pill.id === selectedPillId;
          const isActive = pill.status === 'ACTIVE';

          return (
            <motion.div
              key={pill.id}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setSelectedPillId(pill.id)}
              className={`p-4 border-2 cursor-pointer transition-all ${
                isSelected
                  ? 'border-[#9D4EDD] bg-[#9D4EDD]/10 shadow-[4px_4px_0px_0px_#9D4EDD]'
                  : 'border-slate-800 bg-slate-950 hover:border-[#D4AF37]/60'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">
                  {pill.category}
                </span>
                <span
                  className={`text-[9px] px-1.5 py-0.5 font-bold uppercase ${
                    isActive
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  }`}
                >
                  {pill.status}
                </span>
              </div>
              <h3 className="text-sm font-extrabold text-slate-100 truncate">{pill.name}</h3>
              <div className="text-[10px] text-slate-500 mt-1 font-mono">{pill.runtime}</div>
            </motion.div>
          );
        })}
      </div>

      {/* Selected Pill Inspector Panel */}
      <div className="p-4 border border-slate-800 bg-slate-950 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="text-[10px] text-slate-500 uppercase">ACTIVE CARTRIDGE DETAILS:</div>
          <div className="text-sm font-bold text-[#D4AF37] mt-0.5">
            {selectedPill.name} <span className="text-slate-400 text-xs">({selectedPill.version})</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Execution Mode: <span className="text-emerald-400 font-bold">{selectedPill.runtime}</span> | Target Edge: 100.71.218.75
          </div>
        </div>

        <button
          onClick={() => toggleStatus(selectedPill.id)}
          className="px-5 py-2.5 bg-[#D4AF37] text-slate-950 font-black text-xs uppercase tracking-wider hover:bg-[#FFF8D6] transition-all shadow-[3px_3px_0px_0px_#9D4EDD] active:translate-x-0.5 active:translate-y-0.5"
        >
          SWAP STATE ({selectedPill.status})
        </button>
      </div>

    </div>
  );
}
