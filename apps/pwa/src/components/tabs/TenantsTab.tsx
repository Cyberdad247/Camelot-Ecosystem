// SPDX-License-Identifier: MIT
// Tenants Tab & Tenant Selection Screen — v10001.00-CYBERTRONIA

'use client';

import React, { useState } from 'react';
import { MultivoiceRouterCockpit } from '../MultivoiceRouterCockpit';

export interface TenantCartridge {
  id: string;
  code: string;
  name: string;
  tagline: string;
  risk: 'R0' | 'R1' | 'R2' | 'R3' | 'R4' | 'R5';
  status: 'ACTIVE' | 'UNLOCKED' | 'SEALED';
  category: string;
  description: string;
  units: number;
  monthlyRevenue: number;
  capabilities: string[];
}

export const SOVEREIGN_TENANTS: TenantCartridge[] = [
  {
    id: 'ecosystem-pwa',
    code: 'PWA SHELL',
    name: 'PWA Ecosystem // S26 Edge',
    tagline: 'S26 Edge Mobile Shell, Vault & Guild',
    risk: 'R0',
    status: 'ACTIVE',
    category: 'Ecosystem Shell',
    description: 'Mobile-first Windows-like dashboard, Cartridge Vault hotswap, Marketplace, Guild contracts, and OCEAN customizer.',
    units: 1,
    monthlyRevenue: 0,
    capabilities: ['s26_edge_shell', 'hotswap_vault', 'marketplace', 'guild_board']
  },
  {
    id: 'excalibur-ecc',
    code: 'CARTRIDGE 00',
    name: 'Excalibur Command Center',
    tagline: 'Arch-Sovereign Digital Throne & Node Telemetry',
    risk: 'R5',
    status: 'ACTIVE',
    category: 'Sovereign Core',
    description: 'Converged Node Inventory, 2D Holographic Globe, Alfred Audio Engine, and King Arthur Arch-Sovereign Directives.',
    units: 3,
    monthlyRevenue: 45000,
    capabilities: ['arch_sovereign_gate', 'scrcpy_relay', 'knox_enclave', 'sovereign_dag']
  },
  {
    id: 'kba-executive',
    code: 'CARTRIDGE 01',
    name: 'KBA Executive Holdings',
    tagline: 'Sovereign Governance & Multi-Unit Holdings',
    risk: 'R4',
    status: 'ACTIVE',
    category: 'Governance & Real Estate',
    description: 'Executive Strategy, S-Corp Operating Directives, Cuyahoga County jurisdiction compliance, and GraphRAG knowledge base.',
    units: 8,
    monthlyRevenue: 18200,
    capabilities: ['graphrag_mempalace', 'z3_prover', 'governance_ledger', 'tenant_contracts']
  },
  {
    id: 'digital-factory',
    code: 'CARTRIDGE 02',
    name: 'Digital Factory',
    tagline: 'Invisioned Marketing & Head Artworks',
    risk: 'R3',
    status: 'ACTIVE',
    category: 'Commercial Engines',
    description: 'The Midas Loop inbound lead engine, Firecrawl data pipelines, and Head Artworks physical artisan e-commerce matrix.',
    units: 4,
    monthlyRevenue: 27500,
    capabilities: ['midas_loop', 'firecrawl_scraper', 'artisan_listings', 's_corp_operations']
  },
  {
    id: '1vizion-rcrds',
    code: 'CARTRIDGE 03',
    name: '1VIZION RCRDS',
    tagline: 'Audio Physics & Distribution Matrix',
    risk: 'R3',
    status: 'ACTIVE',
    category: 'Audio & Media Distribution',
    description: 'Automated UPC/ISRC binding, 3000x3000px artwork verification, Records Unchained 71228 sealing, and AI audio synthesis.',
    units: 12,
    monthlyRevenue: 34000,
    capabilities: ['isrc_upc_binding', 'artwork_verification_3000px', 'dsp_audio_physics']
  }
];

export function TenantsTab() {
  const [selectedTenant, setSelectedTenant] = useState<TenantCartridge | null>(null);

  // If a tenant has been selected, transition full-stack into the Multivoice Router Cockpit
  if (selectedTenant) {
    return (
      <MultivoiceRouterCockpit
        activeTenantId={selectedTenant.id}
        activeTenantName={selectedTenant.name}
        onSwitchTenant={() => setSelectedTenant(null)}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Header & Selection Instruction ──────────────────────── */}
      <div className="border border-gold/20 bg-smoke-800/80 p-6 backdrop-blur-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <span className="text-[10px] uppercase tracking-[0.2em] text-white/40 font-mono">
              TENANT SELECTION GATEWAY // APEX MULTI-TENANT ISOLATION
            </span>
            <h2 className="text-2xl font-display text-white tracking-minted mt-1">
              Select Enterprise Tenant Cartridge
            </h2>
            <p className="text-xs text-white/50 mt-1 font-mono">
              Choose a tenant realm to engage zero-trust credentials, mount VFS coordinates, and launch the Multivoice Router.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 text-[10px] font-mono border border-gold/40 bg-gold/10 text-gold-royal">
              5 REALMS ONLINE
            </span>
            <span className="px-2.5 py-1 text-[10px] font-mono border border-emerald-500/40 bg-emerald-950/40 text-emerald-400">
              ZERO-TRUST VAD
            </span>
          </div>
        </div>
      </div>

      {/* ── Tenant Cards Grid ───────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {SOVEREIGN_TENANTS.map(tenant => (
          <div
            key={tenant.id}
            className="border border-gold/20 bg-smoke-800/80 p-6 backdrop-blur-sm flex flex-col justify-between transition-all hover:border-gold/60 hover:shadow-gold group"
          >
            <div>
              <div className="flex items-center justify-between text-[10px] font-mono text-white/40 mb-2">
                <span className="text-gold-light font-bold">{tenant.code}</span>
                <span className="px-1.5 py-0.5 border border-white/10 bg-black/40 text-gold-royal">
                  [{tenant.risk}] {tenant.status}
                </span>
              </div>

              <h3 className="text-lg font-display text-white group-hover:text-gold-light transition-colors">
                {tenant.name}
              </h3>
              <p className="text-xs font-mono text-gold-light/70 mt-0.5">{tenant.tagline}</p>
              <p className="text-xs text-white/50 mt-3 line-clamp-3 leading-relaxed">
                {tenant.description}
              </p>

              <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-xs font-mono">
                <span className="text-white/40">Units / Nodes: {tenant.units}</span>
                <span className="text-gold-royal font-bold">
                  {tenant.monthlyRevenue > 0 ? `$${tenant.monthlyRevenue.toLocaleString()}/mo` : 'Core Shell'}
                </span>
              </div>

              <div className="mt-3 flex flex-wrap gap-1">
                {tenant.capabilities.map(cap => (
                  <span
                    key={cap}
                    className="text-[9px] font-mono px-1.5 py-0.5 border border-white/5 bg-obsidian text-white/40"
                  >
                    {cap}
                  </span>
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={() => setSelectedTenant(tenant)}
              className="mt-6 w-full py-2.5 px-4 border border-gold/40 bg-smoke-900 text-gold-light text-xs font-mono uppercase tracking-wider hover:bg-gold hover:text-black font-bold transition-all shadow-sm flex items-center justify-center gap-2"
            >
              <span>Ingress Tenant Cockpit</span>
              <span>➔</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
