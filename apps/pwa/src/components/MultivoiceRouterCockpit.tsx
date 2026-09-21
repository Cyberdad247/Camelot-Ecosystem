// SPDX-License-Identifier: MIT
// Multivoice Router Full-Stack Cockpit — v10001.00-CYBERTRONIA

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  SOVEREIGN_PERSONAS, 
  VoicePersona, 
  INFERENCE_BACKENDS, 
  InferenceBackend, 
  MESH_NODES 
} from '../lib/voiceInferenceLayer';
import { useBifrost } from '../context/BifrostContext';
import { FivePillarDialectVisualizer } from './voice/FivePillarDialectVisualizer';
import { KnightCharacterSheetModal } from './knights/KnightCharacterSheetModal';

interface Props {
  activeTenantId: string;
  activeTenantName: string;
  onSwitchTenant: () => void;
}

export function MultivoiceRouterCockpit({
  activeTenantId,
  activeTenantName,
  onSwitchTenant
}: Props) {
  // Default to SIR_HELIO per user directive
  const [selectedPersona, setSelectedPersona] = useState<VoicePersona>(SOVEREIGN_PERSONAS[0]);
  const [activeBackend, setActiveBackend] = useState<InferenceBackend>('LOCAL_OLLAMA');
  const [isMicActive, setIsMicActive] = useState<boolean>(false);
  const [isAiSpeaking, setIsAiSpeaking] = useState<boolean>(false);
  const [audioLatencyMs, setAudioLatencyMs] = useState<number>(18);
  const [waveformBars, setWaveformBars] = useState<number[]>([15, 30, 60, 45, 80, 50, 95, 40, 70, 25, 45, 20]);
  const [inputPrompt, setInputPrompt] = useState<string>('');
  const [activeCockpitTab, setActiveCockpitTab] = useState<'CONSOLE' | 'FIVE_PILLARS' | 'CLONING_SPEC'>('CONSOLE');
  const [isCharacterSheetOpen, setIsCharacterSheetOpen] = useState<boolean>(false);
  const [transcripts, setTranscripts] = useState<Array<{ sender: string; text: string; time: string }>>([
    {
      sender: 'SIR_HELIO',
      text: `Sovereign Voice OS online for tenant [${activeTenantName}]. Duplex Gemini Live audio channel armed. Ready for kinetic execution.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }
  ]);

  const { connected } = useBifrost();
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Animate audio waveform when mic is listening or AI is speaking
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isMicActive || isAiSpeaking) {
      interval = setInterval(() => {
        setWaveformBars(Array.from({ length: 16 }, () => Math.floor(Math.random() * 85 + 15)));
        setAudioLatencyMs(Math.floor(Math.random() * 8 + 14));
      }, 100);
    } else {
      setWaveformBars([10, 15, 12, 18, 14, 16, 12, 20, 15, 14, 18, 12, 10, 15, 12, 14]);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isMicActive, isAiSpeaking]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcripts]);

  const toggleMic = () => {
    if (!isMicActive) {
      setIsMicActive(true);
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setTranscripts(prev => [...prev, {
        sender: 'OPERATOR',
        text: 'Acoustic VAD active · Listening...',
        time: timeStr
      }]);

      // Simulate duplex response from the selected persona
      setTimeout(() => {
        setIsMicActive(false);
        setIsAiSpeaking(true);
        const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setTranscripts(prev => [...prev, {
          sender: selectedPersona.name,
          text: `[${selectedPersona.title}]: Intention compiled under tenant ${activeTenantName}. Telemetry dispatched via ${INFERENCE_BACKENDS[activeBackend].name}. Dialect 5-pillar prosody locked at ${selectedPersona.fivePillars.pillar1_pitchContour.basePitchHz}Hz F0.`,
          time: replyTime
        }]);
        setTimeout(() => {
          setIsAiSpeaking(false);
        }, 2600);
      }, 3000);
    } else {
      setIsMicActive(false);
      setIsAiSpeaking(false);
    }
  };

  const handleSendText = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim()) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const userText = inputPrompt.trim();
    setInputPrompt('');

    setTranscripts(prev => [...prev, { sender: 'OPERATOR', text: userText, time: timeStr }]);

    setIsAiSpeaking(true);
    setTimeout(() => {
      setIsAiSpeaking(false);
      const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setTranscripts(prev => [...prev, {
        sender: selectedPersona.name,
        text: `Synthesized response from ${selectedPersona.name} [VFS: ${selectedPersona.vfsPath}]. Task verified under ${INFERENCE_BACKENDS[activeBackend].name}. Model: ${selectedPersona.voiceCloning.modelId}. Weights: ${selectedPersona.voiceCloning.weightsPath}.`,
        time: replyTime
      }]);
    }, 1200);
  };

  const handleGrantLease = (knightId: string) => {
    setTranscripts(prev => [...prev, {
      sender: 'SOVEREIGN_OPERATOR',
      text: `Granted 1-Hour REYA Kinetic Fabric Handshake Lease to [${knightId}]. Dual-attribution enabled for ${knightId.toUpperCase()}.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }]);
  };

  const handleRevokeLease = (knightId: string) => {
    setTranscripts(prev => [...prev, {
      sender: 'SOVEREIGN_OPERATOR',
      text: `Revoked REYA Kinetic Fabric Handshake Lease from [${knightId}]. State reverted to HANDSHAKE_REQUIRED.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }]);
  };

  const reyaStatus = selectedPersona.reyaFabricConnection.handshakeStatus;
  const statusBadgeClass = {
    SOVEREIGN_ROOT: 'bg-amber-500/20 text-amber-300 border-amber-500/50',
    HITL_GUIDED_ALPHA_OMEGA: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
    APPROVED_LEASE: 'bg-sky-500/20 text-sky-300 border-sky-500/50',
    HANDSHAKE_REQUIRED: 'bg-rose-500/20 text-rose-400 border-rose-500/50'
  }[reyaStatus];

  return (
    <div className="space-y-6">
      {/* ── Active Tenant Header Banner ─────────────────────────── */}
      <div className="border border-gold/30 bg-smoke-900/90 p-5 backdrop-blur-md flex flex-wrap items-center justify-between gap-4 shadow-gold">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center border border-gold/50 bg-obsidian text-gold-royal font-display text-xl shadow-gold">
            👑
          </span>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase font-mono tracking-widest text-gold-royal">
                ACTIVE TENANT CONTEXT
              </span>
              <span className="px-1.5 py-0.5 text-[9px] font-mono border border-emerald-500/40 bg-emerald-950/40 text-emerald-400">
                ANYA_GATE_SEALED
              </span>
              {/* REYA Handshake Pill */}
              <span className={`px-2 py-0.5 text-[9px] font-mono border rounded ${statusBadgeClass}`}>
                REYA: {reyaStatus.replace(/_/g, ' ')}
              </span>
            </div>
            <h2 className="text-xl font-display text-white tracking-minted">{activeTenantName}</h2>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsCharacterSheetOpen(true)}
            className="px-3.5 py-2 border border-gold bg-gold/20 text-gold-royal text-xs font-mono uppercase tracking-wider hover:bg-gold hover:text-black transition-colors shadow-gold flex items-center gap-1.5"
          >
            <span>📜</span>
            <span>Character Sheet & RPG (Lv. {selectedPersona.rpgCodex.level})</span>
          </button>
          <button
            type="button"
            onClick={onSwitchTenant}
            className="px-3.5 py-2 border border-gold/40 bg-smoke-800 text-gold-light text-xs font-mono uppercase tracking-wider hover:bg-gold/10 hover:border-gold transition-colors"
          >
            Switch Tenant
          </button>
        </div>
      </div>

      {/* ── Cockpit Sub-Navigation Tabs ────────────────────────── */}
      <div className="flex border-b border-gold/30 gap-2 font-mono text-xs">
        <button
          type="button"
          onClick={() => setActiveCockpitTab('CONSOLE')}
          className={`px-4 py-2 font-bold uppercase transition-all border-b-2 -mb-px flex items-center gap-2 ${
            activeCockpitTab === 'CONSOLE'
              ? 'border-gold text-gold-royal bg-gold/10'
              : 'border-transparent text-white/50 hover:text-white/80'
          }`}
        >
          <span>🎙️</span>
          <span>Acoustic Console & Duplex Stream</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveCockpitTab('FIVE_PILLARS')}
          className={`px-4 py-2 font-bold uppercase transition-all border-b-2 -mb-px flex items-center gap-2 ${
            activeCockpitTab === 'FIVE_PILLARS'
              ? 'border-gold text-gold-royal bg-gold/10'
              : 'border-transparent text-white/50 hover:text-white/80'
          }`}
        >
          <span>🧬</span>
          <span>5-Pillar Dialect Emergence HUD</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveCockpitTab('CLONING_SPEC')}
          className={`px-4 py-2 font-bold uppercase transition-all border-b-2 -mb-px flex items-center gap-2 ${
            activeCockpitTab === 'CLONING_SPEC'
              ? 'border-gold text-gold-royal bg-gold/10'
              : 'border-transparent text-white/50 hover:text-white/80'
          }`}
        >
          <span>⚔️</span>
          <span>Voice Cloning & Model Weights</span>
        </button>
      </div>

      {/* ── View 1: Console & Duplex Stream ────────────────────── */}
      {activeCockpitTab === 'CONSOLE' && (
        <div className="border border-gold/20 bg-smoke-800/80 p-6 backdrop-blur-sm space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-[10px] uppercase tracking-[0.2em] text-white/40 font-mono">
                REAL-TIME VOICE & INFERENCE FORGE // LEVEL {selectedPersona.rpgCodex.level} {selectedPersona.rpgCodex.title.toUpperCase()}
              </span>
              <h3 className="text-2xl font-display text-white tracking-minted flex items-center gap-2 mt-1">
                <span>{selectedPersona.name}</span>
                <span className="text-sm font-mono text-gold-light opacity-80">({selectedPersona.title})</span>
              </h3>
            </div>

            <div className="flex items-center gap-3">
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${statusBadgeClass}`}>
                HANDSHAKE: {reyaStatus}
              </span>
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
                <span className="text-xs font-mono text-white/60">
                  {connected ? 'Bifrost Bridge Live' : 'Mesh Standby'} | Glass-to-Ear: {audioLatencyMs}ms
                </span>
              </div>
            </div>
          </div>

          {/* Dynamic Waveform Visualizer */}
          <div className="flex items-end justify-center gap-1.5 h-24 py-2 px-4 bg-obsidian/70 border border-gold/10 rounded-sm">
            {waveformBars.map((height, idx) => (
              <div
                key={idx}
                className={`w-2.5 transition-all duration-100 ${
                  isMicActive
                    ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
                    : isAiSpeaking
                    ? 'bg-gold shadow-[0_0_8px_rgba(212,175,55,0.8)]'
                    : 'bg-white/20'
                }`}
                style={{ height: `${height}%` }}
              />
            ))}
          </div>

          {/* Mic & Inference Controls */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <button
              type="button"
              onClick={toggleMic}
              className={`px-6 py-3 font-mono text-sm uppercase tracking-wider flex items-center gap-2.5 border transition-all ${
                isMicActive
                  ? 'bg-emerald-600 border-emerald-400 text-black font-bold shadow-[0_0_15px_rgba(52,211,153,0.6)] animate-pulse'
                  : isAiSpeaking
                  ? 'bg-gold/30 border-gold text-gold-light font-bold shadow-gold'
                  : 'bg-smoke-900 border-gold/40 text-gold-light hover:bg-gold/20 hover:border-gold'
              }`}
            >
              <span>{isMicActive ? '🎙️ Listening (Active VAD)' : isAiSpeaking ? '🔊 Speaking (Aoede S2S)' : '🎤 Toggle Duplex Voice'}</span>
            </button>

            {/* Inference Backend Selector */}
            <div className="flex items-center gap-2 overflow-x-auto">
              <span className="text-[10px] text-white/40 uppercase font-mono mr-1">Inference:</span>
              {(Object.keys(INFERENCE_BACKENDS) as InferenceBackend[]).map(backendKey => {
                const backend = INFERENCE_BACKENDS[backendKey];
                const isSelected = activeBackend === backendKey;
                return (
                  <button
                    key={backendKey}
                    type="button"
                    onClick={() => setActiveBackend(backendKey)}
                    className={`px-2.5 py-1.5 text-[11px] font-mono whitespace-nowrap border transition-all ${
                      isSelected
                        ? 'bg-gold/20 border-gold text-gold-light font-bold'
                        : 'bg-smoke-900/60 border-white/10 text-white/50 hover:text-white/80'
                    }`}
                  >
                    {backend.name} {backend.airGapped && '🔒'}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ── View 2: 5-Pillar Dialect Emergence HUD ──────────────── */}
      {activeCockpitTab === 'FIVE_PILLARS' && (
        <FivePillarDialectVisualizer
          dialect={selectedPersona.fivePillars}
          knightName={selectedPersona.name}
          isSpeaking={isAiSpeaking}
        />
      )}

      {/* ── View 3: Voice Cloning & Weights Blueprint ─────────── */}
      {activeCockpitTab === 'CLONING_SPEC' && (
        <div className="border border-gold/20 bg-smoke-800/80 p-6 backdrop-blur-sm space-y-4 font-mono">
          <div className="flex justify-between items-center border-b border-gold/20 pb-3">
            <div>
              <div className="text-[10px] text-gold-royal uppercase">Voice Cloning & Weights Configuration</div>
              <h3 className="text-lg font-bold text-white uppercase">{selectedPersona.name} Acoustic Matrix</h3>
            </div>
            <span className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-xs font-bold">
              {(selectedPersona.voiceCloning.cloningSimilarityScore * 100).toFixed(1)}% SIMILARITY CONFIDENCE
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
            <div className="p-3 bg-black/40 border border-white/10 rounded space-y-2">
              <div>
                <span className="text-white/40 text-[10px] uppercase block">Synthesis Engine:</span>
                <span className="text-gold-light font-bold uppercase">{selectedPersona.voiceCloning.engine}</span>
              </div>
              <div>
                <span className="text-white/40 text-[10px] uppercase block">Model Architecture ID:</span>
                <span className="text-sky-300">{selectedPersona.voiceCloning.modelId}</span>
              </div>
              <div>
                <span className="text-white/40 text-[10px] uppercase block">Weights Repository Path:</span>
                <span className="text-[#D4AF37] break-all">{selectedPersona.voiceCloning.weightsPath}</span>
              </div>
            </div>

            <div className="p-3 bg-black/40 border border-white/10 rounded space-y-2">
              <div>
                <span className="text-white/40 text-[10px] uppercase block">Reference Acoustic Sample:</span>
                <span className="text-white/70 break-all">{selectedPersona.voiceCloning.referenceAudioSample}</span>
              </div>
              <div>
                <span className="text-white/40 text-[10px] uppercase block">Speaker Embedding Dimension:</span>
                <span className="text-violet-300 font-bold">{selectedPersona.voiceCloning.speakerEmbeddingDim}-Dimensional Latent Tensor</span>
              </div>
              <div className="grid grid-cols-2 gap-2 pt-1">
                <div>
                  <span className="text-white/40 text-[10px] uppercase block">Pitch Offset:</span>
                  <span className="text-white font-bold">{selectedPersona.voiceCloning.pitchOffsetSemitones} st</span>
                </div>
                <div>
                  <span className="text-white/40 text-[10px] uppercase block">Tempo Velocity:</span>
                  <span className="text-white font-bold">{selectedPersona.voiceCloning.tempoMultiplier}x</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Round Table Persona Selector Matrix ─────────────────── */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <p className="text-[11px] text-white/40 uppercase tracking-[0.16em] font-mono">
            ROUND TABLE SOVEREIGN KNIGHT MATRIX ({SOVEREIGN_PERSONAS.length} KNIGHTS)
          </p>
          <span className="text-[10px] font-mono text-gold-royal">
            CLICK CARD TO CHANNEL PERSONA
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {SOVEREIGN_PERSONAS.map(persona => {
            const isSelected = selectedPersona.id === persona.id;
            const pStatus = persona.reyaFabricConnection.handshakeStatus;
            const pStatusClass = {
              SOVEREIGN_ROOT: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
              HITL_GUIDED_ALPHA_OMEGA: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
              APPROVED_LEASE: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
              HANDSHAKE_REQUIRED: 'bg-rose-500/20 text-rose-400 border-rose-500/40'
            }[pStatus];

            return (
              <div
                key={persona.id}
                onClick={() => setSelectedPersona(persona)}
                className={`p-4 text-left border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-gold bg-smoke-800/90 shadow-gold ring-1 ring-gold/40'
                    : 'border-gold/15 bg-smoke-900/40 hover:border-gold/40 hover:bg-smoke-900/80'
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className="text-2xl">{persona.avatar}</span>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[9px] font-mono px-1.5 py-0.5 border border-white/10 bg-black/40 text-gold-royal">
                      LVL {persona.rpgCodex.level}
                    </span>
                    <span className={`text-[8px] font-mono px-1 py-0.2 rounded border ${pStatusClass}`}>
                      {pStatus.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>
                <h4 className="mt-2 text-base font-display text-white">{persona.name}</h4>
                <p className="text-xs text-gold-light font-mono mt-0.5">{persona.title}</p>
                <p className="text-[10px] text-white/40 mt-1.5 line-clamp-1">{persona.voiceCloning.modelId}</p>
                
                <div className="mt-2 pt-2 border-t border-white/5 flex items-center justify-between text-[9px] font-mono text-white/40">
                  <span>{persona.fivePillars.pillar1_pitchContour.basePitchHz}Hz F0</span>
                  <span>{persona.fivePillars.pillar2_intonationAndCadence.speechCadenceWpm} WPM</span>
                  <span className="text-gold-light">{persona.layer}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Live Transcript & Interaction Stream ────────────────── */}
      <div className="border border-gold/20 bg-smoke-800/80 p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3 font-mono">
          <p className="text-[11px] text-white/40 uppercase tracking-[0.16em]">
            MULTIVOICE STREAM & COMMAND TRANSCRIPT // DUAL ATTRIBUTION ACTIVE
          </p>
          <span className="text-[10px] text-emerald-400">
            PARTITION: {selectedPersona.reyaFabricConnection.dualAttribution.memcastlePartition}
          </span>
        </div>

        {/* Handshake Prompt if Required */}
        {selectedPersona.reyaFabricConnection.handshakeStatus === 'HANDSHAKE_REQUIRED' && (
          <div className="mb-4 p-3 border border-rose-500/40 bg-rose-950/30 rounded flex items-center justify-between font-mono text-xs text-rose-300">
            <div className="flex items-center gap-2">
              <span>⚠️</span>
              <span>
                REYA Kinetic Fabric requires Handshake Clearance for <strong>{selectedPersona.name}</strong>.
              </span>
            </div>
            <button
              onClick={() => handleGrantLease(selectedPersona.id)}
              className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-black font-bold uppercase text-[10px] rounded transition-all"
            >
              Grant 1-Hour Lease
            </button>
          </div>
        )}

        <div className="space-y-3 max-h-64 overflow-y-auto pr-2 mb-4 scrollbar-thin">
          {transcripts.map((t, idx) => (
            <div
              key={idx}
              className={`p-3 border text-xs font-mono ${
                t.sender === 'OPERATOR' || t.sender === 'SOVEREIGN_OPERATOR'
                  ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-300 ml-6'
                  : 'border-gold/20 bg-black/40 text-white/90 mr-6'
              }`}
            >
              <div className="flex items-center justify-between text-[10px] text-white/40 mb-1">
                <span className="font-bold text-gold-royal">{t.sender}</span>
                <span>{t.time}</span>
              </div>
              <p className="whitespace-pre-line leading-relaxed">{t.text}</p>
            </div>
          ))}
          <div ref={chatBottomRef} />
        </div>

        {/* Command Input Form */}
        <form onSubmit={handleSendText} className="flex gap-2">
          <input
            type="text"
            value={inputPrompt}
            onChange={e => setInputPrompt(e.target.value)}
            placeholder={`Instruct ${selectedPersona.name} in tenant ${activeTenantName}...`}
            className="flex-1 bg-obsidian/80 border border-gold/20 px-4 py-2 text-xs font-mono text-white placeholder-white/30 focus:outline-none focus:border-gold"
          />
          <button
            type="submit"
            className="px-5 py-2 border border-gold bg-gold/20 text-gold-royal text-xs font-mono uppercase tracking-wider hover:bg-gold hover:text-black transition-colors"
          >
            Dispatch
          </button>
        </form>
      </div>

      {/* ── Tailscale Mesh Inventory Telemetry ───────────────────── */}
      <div className="border border-gold/15 bg-smoke-900/50 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] uppercase font-mono tracking-widest text-white/40">
            TAILSCALE BIFROST MESH INVENTORY
          </span>
          <span className="text-[10px] font-mono text-emerald-400">
            5/5 NODES ACTIVE
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
          {MESH_NODES.map(node => (
            <div key={node.name} className="p-2 border border-white/5 bg-black/30 text-[10px] font-mono">
              <div className="flex items-center justify-between">
                <span className="text-white/80 font-bold truncate">{node.name}</span>
                <span className="text-emerald-400">{node.pingMs}ms</span>
              </div>
              <p className="text-white/40 truncate text-[9px] mt-0.5">{node.ip}</p>
              <p className="text-gold-light/60 truncate text-[8px] mt-0.5">{node.role}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Full Character Sheet & RPG Modal */}
      <KnightCharacterSheetModal
        persona={selectedPersona}
        isOpen={isCharacterSheetOpen}
        onClose={() => setIsCharacterSheetOpen(false)}
        onGrantHandshake={handleGrantLease}
        onRevokeHandshake={handleRevokeLease}
      />
    </div>
  );
}
