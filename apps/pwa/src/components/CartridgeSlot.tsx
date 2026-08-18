// SPDX-License-Identifier: MIT

'use client';

import React, { useState } from 'react';

export interface WorkflowPill {
  id: string;
  name: string;
  knight: string;
  cloudbrain_uuid: string;
  status: 'ACTIVE' | 'STANDBY' | 'PAUSED';
  category: 'FINANCE' | 'GOVERNANCE' | 'VOICE' | 'TELEMETRY';
  runtime: 'RUST_WASM' | 'GO_NATIVE' | 'YAML_Z3' | 'WEBRTC_VAD';
  description: string;
}

const DEFAULT_PILLS: WorkflowPill[] = [
  {
    id: 'pill_wasm_ledger',
    name: 'WASM Ledger Engine',
    knight: 'SIR_BORIS / SIR_CRDT_LEDGER',
    cloudbrain_uuid: '8531e6d4-6fc4-428f-a754-b9e9592ac7ff',
    status: 'ACTIVE',
    category: 'FINANCE',
    runtime: 'RUST_WASM',
    description: 'Local WASM CRDT double-entry financial ledger machine',
  },
  {
    id: 'pill_tenant_policy',
    name: 'Tenant 001 Policy Engine',
    knight: 'SIR_SENTINEL',
    cloudbrain_uuid: '07cbb441-f008-424c-820a-85676210be39',
    status: 'ACTIVE',
    category: 'GOVERNANCE',
    runtime: 'YAML_Z3',
    description: 'APEE v7.0 zero-trust multi-tenant isolation validator',
  },
  {
    id: 'pill_eagle_draft',
    name: 'EAGLE Speculative Draft',
    knight: 'LADY_APIS',
    cloudbrain_uuid: '378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f',
    status: 'ACTIVE',
    category: 'TELEMETRY',
    runtime: 'RUST_WASM',
    description: 'Needle-26M speculative token drafting engine',
  },
  {
    id: 'pill_bio_swarm',
    name: 'Bio-Kinetic Cellular Matrix',
    knight: 'LADY_APIS / SIR_BIO_SWARM',
    cloudbrain_uuid: '93b21c40-10ff-4e89-a212-08f37b1297e1',
    status: 'ACTIVE',
    category: 'GOVERNANCE',
    runtime: 'GO_NATIVE',
    description: 'Diode biological isolation & swarm graph router',
  },
  {
    id: 'pill_bifrost_mesh',
    name: 'Bifrost Polyglot Mesh',
    knight: 'SIR_FORGE / SIR_BIFROST',
    cloudbrain_uuid: 'cbbb0c32-3919-4b77-9158-1d9f9ebf359f',
    status: 'ACTIVE',
    category: 'TELEMETRY',
    runtime: 'GO_NATIVE',
    description: 'mTLS WebSocket & gRPC polyglot transport courier',
  },
  {
    id: 'pill_lakesha_voice',
    name: 'LaKesha Voice Hypervisor',
    knight: 'SIR_HELIO / LAKISHA_HYPERVISOR',
    cloudbrain_uuid: '8531e6d4-6fc4-428f-a754-b9e9592ac7ff',
    status: 'ACTIVE',
    category: 'VOICE',
    runtime: 'WEBRTC_VAD',
    description: 'Sub-500ms Web Audio VAD voice OS hypervisor',
  },
  {
    id: 'pill_memory_worldtree',
    name: 'Memory Palace WorldTree',
    knight: 'LADY_MNEMOSYNE',
    cloudbrain_uuid: 'a0a4bfb9-e847-4c38-be39-7aee398f0795',
    status: 'ACTIVE',
    category: 'GOVERNANCE',
    runtime: 'RUST_WASM',
    description: 'WorldTree Sovereign memory anchor & state graph',
  },
  {
    id: 'pill_airgap_sentry',
    name: 'Air-Gapped Zero-Trust Sentry',
    knight: 'SIR_GHOST',
    cloudbrain_uuid: '422a184b-93e7-4dfd-8a12-75d2268b6c60',
    status: 'ACTIVE',
    category: 'GOVERNANCE',
    runtime: 'YAML_Z3',
    description: 'Air-gapped secret scanner & credential sanitizer',
  },
];

export function CartridgeSlot() {
  const [pills] = useState<WorkflowPill[]>(DEFAULT_PILLS);
  const [selectedPillId, setSelectedPillId] = useState<string>('pill_wasm_ledger');

  const selectedPill = pills.find((p) => p.id === selectedPillId) || pills[0];

  return (
    <div className="border-2 border-[#D4AF37]/40 bg-[#0B0B0E] p-6 shadow-[6px_6px_0px_0px_#D4AF37] space-y-6 font-mono mb-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#D4AF37]/30 pb-4 gap-3">
        <div>
          <div className="text-[10px] text-[#9D4EDD] font-bold tracking-widest uppercase">
            SCABBARD PROTOCOL // SOVEREIGN EXECUTIVE INTELLIGENCE PILLS
          </div>
          <h2 className="text-xl font-black text-slate-100 uppercase mt-1">
            Sovereign Executive Intelligence Pills
          </h2>
        </div>
        <div className="px-3 py-1 bg-slate-900 border border-[#D4AF37] text-[#D4AF37] text-xs font-bold uppercase">
          SLOT 01: LOADED ({pills.filter((p) => p.status === 'ACTIVE').length}/{pills.length}{' '}
          ACTIVE)
        </div>
      </div>

      {/* Pill Selector Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {pills.map((pill) => {
          const isSelected = pill.id === selectedPillId;
          return (
            <div
              key={pill.id}
              onClick={() => setSelectedPillId(pill.id)}
              className={`p-4 border-2 cursor-pointer transition-all hover:scale-[1.02] ${
                isSelected
                  ? 'border-[#D4AF37] bg-[#D4AF37]/10 shadow-[4px_4px_0px_0px_#D4AF37]'
                  : 'border-slate-800 bg-slate-950 hover:border-slate-700'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  {pill.category}
                </span>
                <span className="text-[9px] px-1.5 py-0.5 font-bold border border-emerald-500/40 text-emerald-400 bg-emerald-500/10">
                  {pill.status}
                </span>
              </div>
              <div className="text-sm font-black text-slate-100 truncate">{pill.name}</div>
              <div className="text-[11px] text-[#D4AF37] font-bold mt-1 truncate">
                KNIGHT: {pill.knight}
              </div>
              <div className="text-[9px] text-slate-500 mt-2 font-mono truncate">
                UUID: {pill.cloudbrain_uuid}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Pill Telemetry Box */}
      <div className="p-4 border border-slate-800 bg-slate-950 space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400">ACTIVE CARTRIDGE TELEMETRY:</span>
          <span className="text-[#9D4EDD] font-bold">RUNTIME: {selectedPill.runtime}</span>
        </div>
        <div className="text-sm font-bold text-slate-100">
          {selectedPill.name} &mdash;{' '}
          <span className="text-slate-400 text-xs font-normal">{selectedPill.description}</span>
        </div>
      </div>
    </div>
  );
}
