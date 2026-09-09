// SPDX-License-Identifier: MIT

'use client';

import React, { useState, useEffect } from 'react';
import { useBifrost } from '../../context/BifrostContext';

interface ServiceStatus {
  name: string;
  lang: 'Rust' | 'Go' | 'TS';
  location: 'S26' | 'VPS';
  memory: string;
  purpose: string;
  status: 'ACTIVE' | 'SYNCING' | 'STANDBY' | 'DEGRADED';
  latencyMs: number;
}

const EXCALIBUR_SERVICES: ServiceStatus[] = [
  {
    name: 'excalibur-voice-auth',
    lang: 'Rust',
    location: 'S26',
    memory: '64M',
    purpose: 'Biometric speaker verification (ONNX Runtime, 256-dim, SHA3-256)',
    status: 'ACTIVE',
    latencyMs: 14,
  },
  {
    name: 'excalibur-anti-spoof',
    lang: 'Go',
    location: 'VPS',
    memory: '128M',
    purpose: 'Anti-cloning defense, deepfake spectral analysis & phoneme challenge',
    status: 'ACTIVE',
    latencyMs: 28,
  },
  {
    name: 'excalibur-macro-engine',
    lang: 'Go',
    location: 'VPS',
    memory: '128M',
    purpose: 'Transactional voice workflows with rollback journal & HITL gate',
    status: 'ACTIVE',
    latencyMs: 19,
  },
  {
    name: 'excalibur-offline-queue',
    lang: 'Rust',
    location: 'S26',
    memory: '32M',
    purpose: 'Disconnected sovereignty (SQLite + AES-256-GCM, auto-sync 24h TTL)',
    status: 'ACTIVE',
    latencyMs: 4,
  },
  {
    name: 'excalibur-audit-chain',
    lang: 'Rust',
    location: 'VPS',
    memory: '64M',
    purpose: 'Immutable signed log with Ed25519 & hourly Merkle tree publication',
    status: 'ACTIVE',
    latencyMs: 31,
  },
  {
    name: 'excalibur-failover-orch',
    lang: 'Go',
    location: 'VPS',
    memory: '64M',
    purpose: 'DR coordination (10s health loop, Avalon secondary failover & Vault unseal)',
    status: 'STANDBY',
    latencyMs: 22,
  },
];

export function ExcaliburCommandCenterTab() {
  const { connected } = useBifrost();
  const [activeProfile, setActiveProfile] = useState<'Primary' | 'Delegate' | 'Guest'>('Primary');
  const [duressMode, setDuressMode] = useState(false);
  const [reauthCountdown, setReauthCountdown] = useState(30);
  const [similarityScore, setSimilarityScore] = useState(0.94);
  const [offlineQueueCount, setOfflineQueueCount] = useState(0);
  const [activeChallenge, setActiveChallenge] = useState('knight-7-round-3');

  useEffect(() => {
    const timer = setInterval(() => {
      setReauthCountdown((prev) => (prev > 1 ? prev - 1 : 30));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="space-y-6 font-mono text-white">
      {/* ── Header HUD Banner ─────────────────────────────────── */}
      <div className="border border-gold/30 bg-smoke-900/90 p-5 shadow-gold">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center border border-gold bg-obsidian text-lg font-bold text-gold-royal shadow-gold">
              ⚔️
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-display text-lg tracking-wide text-gold-light">
                  EXCALIBUR VOCAL LIVE COMMAND CENTER
                </h2>
                <span className="border border-gold/40 bg-gold/10 px-2 py-0.5 text-[10px] text-gold-royal">
                  S26 ULTRA SENTINEL
                </span>
              </div>
              <p className="text-xs text-white/50">
                Hub Node: <span className="text-white/80">vps-camelot-hub (100.110.180.18)</span> · Mesh Bridge: <span className="text-emerald-400">ENCRYPTED BIFROST :8095</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="border border-white/10 bg-black/40 px-3 py-1.5">
              <span className="text-white/40">BIO-AUTH LEASE: </span>
              <span className="font-bold text-gold-royal">{reauthCountdown}s</span>
            </div>
            <div className="border border-white/10 bg-black/40 px-3 py-1.5">
              <span className="text-white/40">SIMILARITY: </span>
              <span className={`font-bold ${similarityScore >= 0.6 ? 'text-emerald-400' : 'text-red-400'}`}>
                {(similarityScore * 100).toFixed(1)}%
              </span>
            </div>
            <div className={`border px-3 py-1.5 ${duressMode ? 'border-red-500 bg-red-950/80 text-red-300' : 'border-emerald-500/30 bg-emerald-950/20 text-emerald-400'}`}>
              {duressMode ? '🚨 DURESS LOCKDOWN' : '🛡️ NORMAL PATROL'}
            </div>
          </div>
        </div>
      </div>

      {/* ── Key Security Telemetry Cards ─────────────────────── */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* Voice Biometric Identity */}
        <div className="border border-gold/20 bg-smoke-800/80 p-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase tracking-wider text-white/50">Voice Biometric Identity</span>
            <span className="text-[10px] text-gold-royal">ONNX 256-dim</span>
          </div>
          <div className="mt-3 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-white/40">Active Profile:</span>
              <span className="text-gold-light font-bold">{activeProfile}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Speaker Hash:</span>
              <span className="text-white/80">0x7A9B...E5F6</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Impostor Cutoff:</span>
              <span className="text-amber-400">&lt; 0.60 Cosine</span>
            </div>
            <div className="mt-2 flex gap-1">
              {(['Primary', 'Delegate', 'Guest'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setActiveProfile(p)}
                  className={`flex-1 border py-1 text-[10px] uppercase transition-colors ${
                    activeProfile === p
                      ? 'border-gold bg-gold/20 text-gold-light font-bold'
                      : 'border-white/10 hover:border-white/30 text-white/50'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Anti-Spoofing & Deepfake Defense */}
        <div className="border border-gold/20 bg-smoke-800/80 p-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase tracking-wider text-white/50">Anti-Spoofing Stack</span>
            <span className="text-[10px] text-emerald-400">VPS SHIELD</span>
          </div>
          <div className="mt-3 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-white/40">Spectral Analysis:</span>
              <span className="text-emerald-400 font-bold">SYNTH_ARTIFACT_ZERO</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Phoneme Challenge:</span>
              <span className="text-violet-light font-mono">{activeChallenge}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Replay Defense:</span>
              <span className="text-white/80">Nonce Hashing OK</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Prosody/Vocal Tremor:</span>
              <span className="text-emerald-400">NATURAL_BREATH</span>
            </div>
          </div>
        </div>

        {/* Disaster Recovery & Memory Budget */}
        <div className="border border-gold/20 bg-smoke-800/80 p-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] uppercase tracking-wider text-white/50">DR & Resource Budget</span>
            <span className="text-[10px] text-gold-royal">S26 HARD CAP &lt;500M</span>
          </div>
          <div className="mt-3 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-white/40">S26 Memory Used:</span>
              <span className="text-emerald-400 font-bold">478MB / 500MB</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">VPS Hub Memory:</span>
              <span className="text-emerald-400 font-bold">2.45GB / 8.0GB</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Failover Route:</span>
              <span className="text-white/80">KVM563 → Avalon DR</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Offline SQLite Queue:</span>
              <span className="text-gold-light">{offlineQueueCount} packets stored</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Excalibur 8-Service Architecture Matrix ───────────── */}
      <div className="border border-gold/20 bg-smoke-900/90 p-5">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <h3 className="text-xs uppercase tracking-wider text-gold-light font-display">
            Excalibur Production Service Fleet (S26 Sentinel + VPS Hub)
          </h3>
          <span className="text-[10px] text-white/40">6 Core Engines Loaded</span>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/10 text-white/40">
                <th className="pb-2">SERVICE</th>
                <th className="pb-2">LOCATION</th>
                <th className="pb-2">LANG</th>
                <th className="pb-2">MEMORY</th>
                <th className="pb-2">LATENCY</th>
                <th className="pb-2">STATUS</th>
                <th className="pb-2">PURPOSE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {EXCALIBUR_SERVICES.map((s) => (
                <tr key={s.name} className="hover:bg-white/5">
                  <td className="py-2.5 font-bold text-gold-light">{s.name}</td>
                  <td className="py-2.5">
                    <span className={`px-2 py-0.5 text-[10px] border ${
                      s.location === 'S26' ? 'border-amber-400/40 text-amber-300 bg-amber-950/20' : 'border-blue-400/40 text-blue-300 bg-blue-950/20'
                    }`}>
                      {s.location}
                    </span>
                  </td>
                  <td className="py-2.5 text-white/60">{s.lang}</td>
                  <td className="py-2.5 text-white/80">{s.memory}</td>
                  <td className="py-2.5 text-emerald-400">{s.latencyMs}ms</td>
                  <td className="py-2.5">
                    <span className={`px-2 py-0.5 text-[10px] border ${
                      s.status === 'ACTIVE'
                        ? 'border-emerald-500/40 bg-emerald-950/20 text-emerald-400'
                        : 'border-white/20 text-white/40'
                    }`}>
                      {s.status}
                    </span>
                  </td>
                  <td className="py-2.5 text-white/50 text-[11px]">{s.purpose}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Transactional Voice Macro & Duress Trigger Bar ────── */}
      <div className="flex flex-wrap items-center justify-between gap-4 border border-white/10 bg-black/50 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setDuressMode(!duressMode)}
            className={`border px-4 py-2 text-xs uppercase font-bold tracking-wider transition-colors ${
              duressMode
                ? 'border-red-500 bg-red-600 text-white'
                : 'border-red-500/40 bg-red-950/20 text-red-400 hover:bg-red-900/40'
            }`}
          >
            {duressMode ? 'DEACTIVATE GHOST LOCKDOWN' : 'SIMULATE DURESS TRIGGER'}
          </button>
          <button
            onClick={() => setActiveChallenge(`knight-${Math.floor(Math.random() * 9 + 1)}-round-${Math.floor(Math.random() * 9 + 1)}`)}
            className="border border-gold/40 bg-gold/10 px-4 py-2 text-xs text-gold-light hover:bg-gold/20"
          >
            GENERATE PHONEME CHALLENGE
          </button>
        </div>
        <p className="text-[11px] text-white/40">
          Ed25519 Audit Chain Head: <span className="font-mono text-white/70">0x8F3C...A419 (Merkle Root #1042)</span>
        </p>
      </div>
    </div>
  );
}
