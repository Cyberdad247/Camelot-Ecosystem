// SPDX-License-Identifier: MIT
// Sovereign Round Table Knights Tab — v10001.00-CYBERTRONIA

'use client';

import React, { useState } from 'react';
import { useBifrost } from '../../context/BifrostContext';
import { SOVEREIGN_PERSONAS, VoicePersona } from '../../lib/voiceInferenceLayer';
import { KnightCharacterSheetModal } from '../knights/KnightCharacterSheetModal';

export function KnightsTab() {
  const { sendVoiceCommand, connected } = useBifrost();
  const [selectedKnight, setSelectedKnight] = useState<VoicePersona | null>(null);
  const [filter, setFilter] = useState<'ALL' | 'ALPHA_OMEGA' | 'ACTIVE_LEASE' | 'HANDSHAKE_REQ'>('ALL');

  const filteredKnights = SOVEREIGN_PERSONAS.filter(k => {
    if (filter === 'ALPHA_OMEGA') {
      return k.rpgCodex.level >= 10 || k.reyaFabricConnection.autonomyTier === 'HITL_GUIDED_ALPHA_OMEGA' || k.reyaFabricConnection.autonomyTier === 'SOVEREIGN_ROOT';
    }
    if (filter === 'ACTIVE_LEASE') {
      return k.reyaFabricConnection.leaseActive;
    }
    if (filter === 'HANDSHAKE_REQ') {
      return k.reyaFabricConnection.handshakeStatus === 'HANDSHAKE_REQUIRED';
    }
    return true;
  });

  const activeLeases = SOVEREIGN_PERSONAS.filter(k => k.reyaFabricConnection.leaseActive).length;
  const alphaOmegas = SOVEREIGN_PERSONAS.filter(k => k.rpgCodex.level >= 10).length;

  const statusColors = {
    SOVEREIGN_ROOT: 'bg-amber-500/20 text-amber-300 border-amber-500/50',
    HITL_GUIDED_ALPHA_OMEGA: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
    APPROVED_LEASE: 'bg-sky-500/20 text-sky-300 border-sky-500/50',
    HANDSHAKE_REQUIRED: 'bg-rose-500/20 text-rose-400 border-rose-500/50'
  };

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Banner ─────────────────────────────────── */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between border border-gold/30 bg-smoke-900/80 px-6 py-4 backdrop-blur-md gap-4 shadow-gold">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-gold-royal uppercase tracking-[0.2em]">
              SOVEREIGN ROUND TABLE KNIGHT MATRIX
            </span>
            <span className="px-1.5 py-0.5 text-[9px] border border-emerald-500/40 bg-emerald-950/40 text-emerald-400">
              OMEGA_PANTHEON_SYNCED
            </span>
          </div>
          <h2 className="text-xl font-display text-white tracking-minted mt-0.5">
            Round Table Pantheon ({SOVEREIGN_PERSONAS.length} Sovereign Knights)
          </h2>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="px-3 py-1.5 border border-gold/30 bg-black/40 text-gold-light">
            Alpha Omega (Lv ≥ 10): <span className="font-bold text-white">{alphaOmegas}</span>
          </div>
          <div className="px-3 py-1.5 border border-emerald-500/40 bg-black/40 text-emerald-300">
            REYA Leases Active: <span className="font-bold text-white">{activeLeases}/{SOVEREIGN_PERSONAS.length}</span>
          </div>
        </div>
      </div>

      {/* ── Filter Navigation ─────────────────────────────────── */}
      <div className="flex border-b border-gold/20 gap-2 text-xs">
        {[
          { id: 'ALL', label: `All Knights (${SOVEREIGN_PERSONAS.length})` },
          { id: 'ALPHA_OMEGA', label: `Alpha Omega Tiers (${alphaOmegas})` },
          { id: 'ACTIVE_LEASE', label: `Active REYA Leases (${activeLeases})` },
          { id: 'HANDSHAKE_REQ', label: `Handshake Required (${SOVEREIGN_PERSONAS.length - activeLeases})` }
        ].map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setFilter(tab.id as any)}
            className={`px-3 py-2 font-bold uppercase transition-all border-b-2 -mb-px ${
              filter === tab.id
                ? 'border-gold text-gold-royal bg-gold/10'
                : 'border-transparent text-white/50 hover:text-white/80'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Knight Cards Grid ─────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredKnights.map((k) => {
          const hStatus = k.reyaFabricConnection.handshakeStatus;
          const statusBadge = statusColors[hStatus];

          return (
            <div
              key={k.id}
              className="flex flex-col border border-gold/20 bg-smoke-800/80 p-5 backdrop-blur-sm transition-all hover:border-gold hover:shadow-gold cursor-pointer rounded-sm"
              onClick={() => setSelectedKnight(k)}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="text-2xl p-1.5 bg-black/50 border border-gold/30 rounded">
                    {k.avatar}
                  </span>
                  <div>
                    <p className="font-display text-lg text-gold-royal tracking-minted">{k.name}</p>
                    <p className="text-[10px] text-white/40 uppercase tracking-wider">
                      {k.layer} · {k.role.split(' ')[0]}
                    </p>
                  </div>
                </div>
                <span className={`text-[8px] px-1.5 py-0.5 rounded border uppercase font-bold ${statusBadge}`}>
                  {hStatus.replace(/_/g, ' ')}
                </span>
              </div>

              {/* RPG Codex Level Progress */}
              <div className="mt-3.5 p-2 bg-black/40 border border-slate-900 rounded space-y-1">
                <div className="flex justify-between text-[10px]">
                  <span className="text-[#D4AF37] font-bold">LVL {k.rpgCodex.level} {k.rpgCodex.title}</span>
                  <span className="text-slate-400">{k.rpgCodex.xp} XP</span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-violet-500 to-[#D4AF37] h-full rounded-full"
                    style={{ width: `${Math.min(100, Math.max(10, (k.rpgCodex.xp / (k.rpgCodex.xp + k.rpgCodex.xpToNext)) * 100))}%` }}
                  />
                </div>
              </div>

              {/* Voice Cloning & Weights */}
              <div className="mt-3 text-[10px] space-y-1 text-slate-300">
                <div className="flex justify-between text-slate-400 text-[9px]">
                  <span>SYNTHESIS MODEL:</span>
                  <span className="text-sky-300 font-bold">{k.voiceCloning.modelId}</span>
                </div>
                <div className="truncate text-[9px] text-slate-500 font-mono">
                  {k.voiceCloning.weightsPath}
                </div>
              </div>

              {/* 5-Pillar Dialect Metrics */}
              <div className="mt-2.5 pt-2 border-t border-white/5 grid grid-cols-3 gap-1 text-[9px] text-slate-400 text-center">
                <div className="bg-slate-950/60 p-1 border border-slate-900 rounded">
                  <div className="text-[8px] text-slate-500">PITCH F0</div>
                  <div className="text-slate-200 font-bold">{k.fivePillars.pillar1_pitchContour.basePitchHz}Hz</div>
                </div>
                <div className="bg-slate-950/60 p-1 border border-slate-900 rounded">
                  <div className="text-[8px] text-slate-500">CADENCE</div>
                  <div className="text-slate-200 font-bold">{k.fivePillars.pillar2_intonationAndCadence.speechCadenceWpm}WPM</div>
                </div>
                <div className="bg-slate-950/60 p-1 border border-slate-900 rounded">
                  <div className="text-[8px] text-slate-500">SILENCE</div>
                  <div className="text-slate-200 font-bold">{k.fivePillars.pillar5_adaptiveTurnTakingAndVisemes.adaptiveSilenceThresholdMs}ms</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-4 pt-2 border-t border-white/10 flex items-center justify-between gap-2">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedKnight(k);
                  }}
                  className="flex-1 border border-gold/40 px-2 py-1 text-[10px] text-gold-light uppercase tracking-wider hover:bg-gold/15 transition-colors"
                >
                  Character Sheet
                </button>
                <button
                  type="button"
                  disabled={!connected}
                  onClick={(e) => {
                    e.stopPropagation();
                    sendVoiceCommand(`channel ${k.id}`);
                  }}
                  className="border border-violet/50 px-2.5 py-1 text-[10px] text-violet-300 uppercase tracking-wider hover:bg-violet/15 disabled:opacity-30 transition-colors"
                >
                  Channel
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Full Character Sheet Modal */}
      {selectedKnight && (
        <KnightCharacterSheetModal
          persona={selectedKnight}
          isOpen={true}
          onClose={() => setSelectedKnight(null)}
        />
      )}
    </div>
  );
}
