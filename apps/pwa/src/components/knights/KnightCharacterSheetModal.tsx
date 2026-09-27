// SPDX-License-Identifier: MIT
// Knight Character Sheet & RPG Progression Modal
// v10001.00-CYBERTRONIA

'use client';

import React, { useState } from 'react';
import { VoicePersona } from '../../lib/voiceInferenceLayer';
import { FivePillarDialectVisualizer } from '../voice/FivePillarDialectVisualizer';

interface Props {
  persona: VoicePersona;
  isOpen: boolean;
  onClose: () => void;
  onGrantHandshake?: (knightId: string) => void;
  onRevokeHandshake?: (knightId: string) => void;
}

export function KnightCharacterSheetModal({
  persona,
  isOpen,
  onClose,
  onGrantHandshake,
  onRevokeHandshake
}: Props) {
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'VOICE_CLONING' | 'FIVE_PILLARS' | 'REYA_FABRIC'>('OVERVIEW');
  const [localLeaseStatus, setLocalLeaseStatus] = useState(persona.reyaFabricConnection.handshakeStatus);

  if (!isOpen) return null;

  const handleGrant = () => {
    setLocalLeaseStatus('APPROVED_LEASE');
    if (onGrantHandshake) onGrantHandshake(persona.id);
  };

  const handleRevoke = () => {
    setLocalLeaseStatus('HANDSHAKE_REQUIRED');
    if (onRevokeHandshake) onRevokeHandshake(persona.id);
  };

  const { rpgCodex, voiceCloning, fivePillars, reyaFabricConnection, oceanVector } = persona;

  const statusColors = {
    SOVEREIGN_ROOT: 'bg-amber-500/20 text-amber-300 border-amber-500/50',
    HITL_GUIDED_ALPHA_OMEGA: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
    APPROVED_LEASE: 'bg-sky-500/20 text-sky-300 border-sky-500/50',
    HANDSHAKE_REQUIRED: 'bg-rose-500/20 text-rose-400 border-rose-500/50'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md font-mono">
      <div className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto border-2 border-[#D4AF37] bg-[#0A0A0E] text-slate-200 p-6 shadow-[0_0_50px_rgba(212,175,55,0.25)] space-y-6 rounded-sm">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-[#D4AF37] text-lg font-bold border border-slate-800 hover:border-[#D4AF37] px-2.5 py-0.5 rounded transition-all"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-[#D4AF37]/30 pb-4 gap-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl p-2 bg-slate-900 border border-[#D4AF37]/50 rounded-sm">
              {persona.avatar}
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black text-slate-100 uppercase tracking-wider">
                  {persona.name}
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/40">
                  {persona.layer}
                </span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${statusColors[localLeaseStatus]}`}>
                  {localLeaseStatus.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{persona.title}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">SPARK ID: {persona.sparkId}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-slate-500 uppercase">OBSERVATORY LEVEL</div>
            <div className="text-2xl font-black text-[#D4AF37]">
              LVL {rpgCodex.level} <span className="text-xs text-slate-400">({rpgCodex.title})</span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800 gap-2 text-xs">
          {[
            { id: 'OVERVIEW', label: '1. Identity & RPG Codex' },
            { id: 'VOICE_CLONING', label: '2. Voice Cloning & Weights' },
            { id: 'FIVE_PILLARS', label: '3. 5-Pillar Dialect Emergence' },
            { id: 'REYA_FABRIC', label: '4. REYA Kinetic Handshake' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-2 font-bold uppercase transition-all border-b-2 -mb-px ${
                activeTab === tab.id
                  ? 'border-[#D4AF37] text-[#D4AF37] bg-[#D4AF37]/10'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab 1: Overview & RPG Codex */}
        {activeTab === 'OVERVIEW' && (
          <div className="space-y-5">
            {/* RPG XP Bar */}
            <div className="p-4 border border-slate-800 bg-slate-950/70 rounded space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#D4AF37] font-bold uppercase">Experience Points Progression</span>
                <span className="text-slate-400">{rpgCodex.xp} XP (Next Level: +{rpgCodex.xpToNext} XP)</span>
              </div>
              <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-violet-600 via-[#D4AF37] to-amber-500 h-full rounded-full"
                  style={{ width: `${Math.min(100, Math.max(15, (rpgCodex.xp / (rpgCodex.xp + rpgCodex.xpToNext)) * 100))}%` }}
                />
              </div>
              <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-400 pt-1">
                <div>Dialogue Turns: <span className="text-slate-200 font-bold">{rpgCodex.turnsTranscribed}</span></div>
                <div>Evaluated Tasks: <span className="text-slate-200 font-bold">{rpgCodex.tasksEvaluated}</span></div>
                <div>Avg Kinetic Score: <span className="text-emerald-400 font-bold">{rpgCodex.averageScore}%</span></div>
              </div>
              {rpgCodex.achievements.length > 0 && (
                <div className="pt-2 border-t border-slate-900 mt-2">
                  <div className="text-[10px] text-slate-500 uppercase">Mastery Achievements:</div>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {rpgCodex.achievements.map((ach, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-[#9D4EDD]/20 text-[#D4AF37] border border-[#9D4EDD]/40">
                        🏆 {ach}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Architectural & Personality Attributes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border border-slate-800 bg-slate-950/70 rounded space-y-2 text-xs">
                <div className="text-[#D4AF37] font-bold uppercase border-b border-slate-800 pb-1">
                  Architectural Coordinates
                </div>
                <div className="space-y-1 text-[11px]">
                  <div><span className="text-slate-500">Summoning Rune:</span> <span className="text-[#D4AF37] font-bold">{persona.summoningRune}</span></div>
                  <div><span className="text-slate-500">CloudBrain UUID:</span> <span className="text-slate-300">{persona.cloudBrainUuid}</span></div>
                  <div><span className="text-slate-500">VFS Coordinate:</span> <span className="text-slate-300">{persona.vfsPath}</span></div>
                  <div><span className="text-slate-500">MemPalace Wing:</span> <span className="text-slate-300">{persona.mempalaceWing}</span></div>
                  <div><span className="text-slate-500">Behavioral Contract:</span> <span className="text-slate-300">{persona.behavioralContract}</span></div>
                </div>
              </div>

              <div className="p-4 border border-slate-800 bg-slate-950/70 rounded space-y-2 text-xs">
                <div className="text-[#D4AF37] font-bold uppercase border-b border-slate-800 pb-1">
                  OCEAN Personality Vector
                </div>
                <div className="space-y-1.5 text-[10px] pt-1">
                  {[
                    { label: 'Openness (O)', val: oceanVector.O },
                    { label: 'Conscientiousness (C)', val: oceanVector.C },
                    { label: 'Extraversion (E)', val: oceanVector.E },
                    { label: 'Agreeableness (A)', val: oceanVector.A },
                    { label: 'Neuroticism (N)', val: oceanVector.N },
                  ].map((trait) => (
                    <div key={trait.label} className="space-y-0.5">
                      <div className="flex justify-between">
                        <span className="text-slate-400">{trait.label}</span>
                        <span className="text-[#D4AF37] font-bold">{(trait.val * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-[#D4AF37] h-full rounded-full" style={{ width: `${trait.val * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* System Prompt Directive */}
            <div className="p-3 border border-slate-800 bg-slate-950/50 rounded text-xs">
              <div className="text-slate-500 text-[10px] uppercase">Active Cognitive Mandate:</div>
              <p className="text-slate-300 mt-1 italic leading-relaxed">"{persona.systemPrompt}"</p>
            </div>
          </div>
        )}

        {/* Tab 2: Voice Cloning & Weights */}
        {activeTab === 'VOICE_CLONING' && (
          <div className="space-y-4 text-xs">
            <div className="p-4 border border-slate-800 bg-slate-950/70 rounded space-y-3">
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <div className="text-[#D4AF37] font-bold uppercase text-sm">
                  Voice Cloning Model & Weights Specification
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-[10px] font-bold">
                  {(voiceCloning.cloningSimilarityScore * 100).toFixed(1)}% SIMILARITY CONFIDENCE
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="space-y-2">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Voice Synthesis Engine:</span>
                    <span className="text-slate-200 font-bold uppercase">{voiceCloning.engine}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Model Architecture ID:</span>
                    <span className="text-sky-300 font-mono">{voiceCloning.modelId}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Model Weights Repository Path:</span>
                    <span className="text-[#D4AF37] font-mono break-all">{voiceCloning.weightsPath}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Reference Acoustic Sample:</span>
                    <span className="text-slate-300 font-mono break-all">{voiceCloning.referenceAudioSample}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Speaker Embedding Dimension:</span>
                    <span className="text-violet-300 font-bold">{voiceCloning.speakerEmbeddingDim}-Dimensional Latent Vector</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 pt-1">
                    <div>
                      <span className="text-slate-500 text-[10px] uppercase block">Pitch Offset:</span>
                      <span className="text-slate-200 font-bold">{voiceCloning.pitchOffsetSemitones > 0 ? `+${voiceCloning.pitchOffsetSemitones}` : voiceCloning.pitchOffsetSemitones} semitones</span>
                    </div>
                    <div>
                      <span className="text-slate-500 text-[10px] uppercase block">Tempo Velocity:</span>
                      <span className="text-slate-200 font-bold">{voiceCloning.tempoMultiplier}x</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-3 border border-slate-800 bg-slate-950/40 rounded text-slate-400 text-[11px]">
              Weights loaded through zero-copy memory mapping (<span className="text-[#D4AF37]">Local\Camelot_Reya_Slab</span>).
              Strictly obeys Rule 7 (0% Python hotpath bloat; C++ / GGML inference).
            </div>
          </div>
        )}

        {/* Tab 3: 5-Pillar Dialect Emergence Visualizer */}
        {activeTab === 'FIVE_PILLARS' && (
          <div>
            <FivePillarDialectVisualizer dialect={fivePillars} knightName={persona.name} isSpeaking={true} />
          </div>
        )}

        {/* Tab 4: REYA Kinetic Handshake */}
        {activeTab === 'REYA_FABRIC' && (
          <div className="space-y-4 text-xs">
            <div className="p-4 border border-slate-800 bg-slate-950/70 rounded space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
                <div>
                  <div className="text-[#D4AF37] font-bold uppercase text-sm">
                    REYA Universal Kinetic Fabric Handshake Gate
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    Governed by <span className="text-slate-200 font-mono">02_FORGE/assimilation/reya/reya_handshake_gate.py</span>
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded text-xs font-bold border ${statusColors[localLeaseStatus]}`}>
                  {localLeaseStatus.replace(/_/g, ' ')}
                </span>
              </div>

              {/* Status explanation */}
              <div className="p-3 bg-black/40 border border-slate-900 rounded space-y-1.5 text-[11px]">
                {localLeaseStatus === 'SOVEREIGN_ROOT' && (
                  <p className="text-amber-300">
                    👑 <strong>SOVEREIGN ROOT AUTHORITY:</strong> Sovereign King Arthur & Operator hold unrestricted kinetic actuation across desktop, mobile, and relays.
                  </p>
                )}
                {localLeaseStatus === 'HITL_GUIDED_ALPHA_OMEGA' && (
                  <p className="text-emerald-400">
                    ⚡ <strong>HITL-GUIDED ALPHA OMEGA AUTONOMY:</strong> Level ≥ 10 or canonical Omega entity status unlocks autonomous kinetic CUA execution within Sentinel capability bounds. Pauses only at Red Zones.
                  </p>
                )}
                {localLeaseStatus === 'APPROVED_LEASE' && (
                  <p className="text-sky-300">
                    🛡️ <strong>APPROVED TIME-BOUND LEASE:</strong> Active handshake lease granted by the sovereign user. Allowed to execute sandboxed kinetic CUA actions under Sentinel monitoring.
                  </p>
                )}
                {localLeaseStatus === 'HANDSHAKE_REQUIRED' && (
                  <p className="text-rose-400">
                    ⚠️ <strong>HANDSHAKE REQUIRED:</strong> Novice/Standard Knight (Level &lt; 10) without an active lease. All kinetic and CUA actuations are blocked until explicit user authorization.
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-2">
                {localLeaseStatus === 'HANDSHAKE_REQUIRED' && (
                  <button
                    onClick={handleGrant}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-black font-bold uppercase text-xs rounded transition-all shadow-[2px_2px_0px_0px_#10B981]"
                  >
                    Grant 1-Hour Handshake Lease
                  </button>
                )}
                {localLeaseStatus === 'APPROVED_LEASE' && (
                  <button
                    onClick={handleRevoke}
                    className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold uppercase text-xs rounded transition-all"
                  >
                    Revoke Active Handshake Lease
                  </button>
                )}
                <span className="text-[10px] text-slate-500">
                  Scarcity ceiling: {reyaFabricConnection.maxEdgeMemoryMb}MB max RSS
                </span>
              </div>

              {/* Dual-Attribution Memory Routing */}
              <div className="p-3 border border-slate-900 bg-slate-950 rounded space-y-1.5 text-[10px]">
                <div className="text-slate-400 uppercase font-bold text-[11px] border-b border-slate-900 pb-1">
                  Dual-Attributed Memory & XP Routing
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-300">
                  <div>MemCastle Partition: <span className="text-[#D4AF37] font-mono">{reyaFabricConnection.dualAttribution.memcastlePartition}</span></div>
                  <div>Graphiti Substrate: <span className="text-sky-400 font-mono">{reyaFabricConnection.dualAttribution.graphitiPartition}</span></div>
                  <div>Observatory XP Recipient: <span className="text-emerald-400 font-mono">{reyaFabricConnection.dualAttribution.observatoryXpRecipient}</span></div>
                  <div>Kinetic Fabric: <span className="text-violet-400 font-mono">{reyaFabricConnection.dualAttribution.kineticFabric}</span></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-1.5 border border-[#D4AF37] text-[#D4AF37] hover:bg-[#D4AF37]/10 font-bold text-xs uppercase tracking-wider transition-all"
          >
            Close Sheet
          </button>
        </div>
      </div>
    </div>
  );
}
