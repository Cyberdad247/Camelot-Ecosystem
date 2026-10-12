// SPDX-License-Identifier: MIT
// MagSafe Ambient Voice Recorder & Kinetic Action Item Dispatcher Card
// v10001.00-CYBERTRONIA

'use client';

import React, { useState } from 'react';

export interface ActionItemUI {
  id: string;
  title: string;
  description: string;
  targetKnight: string;
  actionType: 'RUN_COMMAND' | 'CUA_CLICK' | 'CUA_TYPE' | 'VERIFY_TESTS' | 'MEMCASTLE_STORE';
  requiresCua: boolean;
  targetCoordinates: [number, number] | null;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  dispatched: boolean;
  handshakeRequired: boolean;
}

export function MagsafeRecorderCard() {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [selectedKnight, setSelectedKnight] = useState<string>('SIR_HELIOS');
  const [autoDispatch, setAutoDispatch] = useState<boolean>(true);
  const [activeSession, setActiveSession] = useState<{
    id: string;
    duration: string;
    summary: string;
    keyIdeas: string[];
    turnId: string;
    xpAwarded: number;
    items: ActionItemUI[];
  }>({
    id: 'magsafe_ambient_active',
    duration: '14.8s',
    summary: 'SecondBrain synthesized 2 core concepts and extracted 3 actionable kinetic tasks.',
    keyIdeas: [
      'Ambient audio captured via MagSafe edge hardware.',
      'Transcripts synchronized to living memory behind impenetrable glass wall.'
    ],
    turnId: 'turn_1789962243059_51',
    xpAwarded: 60,
    items: [
      {
        id: 'act_01',
        title: 'Task 1: Run unit tests on magsafe bridge',
        description: 'Run pytest tests/test_magsafe_voice_dispatcher.py to verify stability.',
        targetKnight: 'SIR_HELIOS',
        actionType: 'VERIFY_TESTS',
        requiresCua: false,
        targetCoordinates: null,
        priority: 'MEDIUM',
        dispatched: true,
        handshakeRequired: false,
      },
      {
        id: 'act_02',
        title: 'Task 2: Click coordinate (500, 320)',
        description: 'Click coordinate (500, 320) to awaken the Cockpit HUD.',
        targetKnight: 'SIR_CODEX',
        actionType: 'CUA_CLICK',
        requiresCua: true,
        targetCoordinates: [500, 320],
        priority: 'HIGH',
        dispatched: false,
        handshakeRequired: true,
      },
      {
        id: 'act_03',
        title: 'Task 3: Memorize ambient session',
        description: 'Store SecondBrain executive summary into MemCastle KNN partition.',
        targetKnight: 'LADY_MNEMOSYNE',
        actionType: 'MEMCASTLE_STORE',
        requiresCua: false,
        targetCoordinates: null,
        priority: 'LOW',
        dispatched: true,
        handshakeRequired: false,
      }
    ]
  });

  const handleSimulateRecord = () => {
    setIsRecording(true);
    setTimeout(() => {
      setIsRecording(false);
      setActiveSession(prev => ({
        ...prev,
        id: `magsafe_${Date.now()}`,
        duration: '18.4s',
        turnId: `turn_${Date.now()}_51`,
        xpAwarded: 60,
      }));
    }, 1800);
  };

  const handleApproveHandshake = (itemId: string) => {
    setActiveSession(prev => ({
      ...prev,
      items: prev.items.map(it => it.id === itemId ? { ...it, dispatched: true, handshakeRequired: false } : it)
    }));
  };

  return (
    <div className="border border-[#D4AF37]/30 bg-[#0B0B0E]/95 p-5 backdrop-blur-md space-y-5 font-mono shadow-[0_0_20px_rgba(212,175,55,0.08)]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-[#D4AF37]/20 pb-3 gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">🧲</span>
          <div>
            <h3 className="text-sm font-black text-slate-100 uppercase tracking-wider flex items-center gap-2">
              <span>MAGSAFE AMBIENT AUDIO SENTINEL</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                EDGE HARDWARE ARMED
              </span>
            </h3>
            <div className="text-[10px] text-slate-400">
              cgroups v2 scarcity &lt;350MB RSS • Glass Observatory WORM tap active
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right text-[11px]">
            <div className="text-slate-400">OBSERVATORY PROGRESS</div>
            <div className="text-[#D4AF37] font-bold">+{activeSession.xpAwarded} XP (Turn {activeSession.turnId.slice(-6)})</div>
          </div>
          <button
            type="button"
            onClick={handleSimulateRecord}
            className={`px-3 py-1.5 border text-xs font-bold uppercase transition-all flex items-center gap-1.5 ${
              isRecording
                ? 'bg-rose-600/30 border-rose-500 text-rose-300 animate-pulse'
                : 'bg-[#D4AF37]/20 border-[#D4AF37] text-[#D4AF37] hover:bg-[#D4AF37] hover:text-black'
            }`}
          >
            <span>{isRecording ? '🔴 INGESTING...' : '🎙️ SIMULATE INGEST'}</span>
          </button>
        </div>
      </div>

      {/* Hardware Telemetry Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="p-2.5 bg-slate-950/80 border border-slate-800 rounded-sm">
          <div className="text-[10px] text-slate-500 uppercase">Hardware Snap</div>
          <div className="text-emerald-400 font-bold">MAGSAFE ATTACHED (98%)</div>
        </div>
        <div className="p-2.5 bg-slate-950/80 border border-slate-800 rounded-sm">
          <div className="text-[10px] text-slate-500 uppercase">Memory Footprint</div>
          <div className="text-[#D4AF37] font-bold">34.2 MB / 350.0 MB</div>
        </div>
        <div className="p-2.5 bg-slate-950/80 border border-slate-800 rounded-sm">
          <div className="text-[10px] text-slate-500 uppercase">Glass Wall Status</div>
          <div className="text-cyan-400 font-bold">PROJECT SPECULUM (WORM)</div>
        </div>
        <div className="p-2.5 bg-slate-950/80 border border-slate-800 rounded-sm">
          <div className="text-[10px] text-slate-500 uppercase">Attributed Knight</div>
          <div className="text-white font-bold">{selectedKnight}</div>
        </div>
      </div>

      {/* SecondBrain Executive Summary */}
      <div className="p-3.5 bg-black/50 border border-[#D4AF37]/20 rounded-sm space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-[#D4AF37] font-bold uppercase flex items-center gap-1.5">
            <span>🧠</span>
            <span>SecondBrain Executive Summary</span>
          </span>
          <span className="text-slate-400 text-[10px]">Session: {activeSession.id} ({activeSession.duration})</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">{activeSession.summary}</p>
        <div className="flex flex-wrap gap-2 pt-1">
          {activeSession.keyIdeas.map((idea, idx) => (
            <span
              key={idx}
              className="text-[10px] px-2 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300"
            >
              💡 {idea}
            </span>
          ))}
        </div>
      </div>

      {/* Extracted Kinetic Action Items & REYA Gate */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-white font-bold uppercase flex items-center gap-1.5">
            <span>⚡</span>
            <span>Extracted Kinetic Action Items ({activeSession.items.length})</span>
          </span>
          <label className="flex items-center gap-1.5 text-[11px] text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoDispatch}
              onChange={e => setAutoDispatch(e.target.checked)}
              className="accent-[#D4AF37]"
            />
            <span>Auto-Dispatch through REYA Fabric</span>
          </label>
        </div>

        <div className="space-y-2">
          {activeSession.items.map(item => (
            <div
              key={item.id}
              className="p-3 bg-slate-950/90 border border-slate-800 hover:border-[#D4AF37]/40 transition-colors rounded-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${
                    item.actionType === 'CUA_CLICK' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' :
                    item.actionType === 'VERIFY_TESTS' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' :
                    'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  }`}>
                    {item.actionType}
                  </span>
                  <span className="font-bold text-white">{item.title}</span>
                  {item.targetCoordinates && (
                    <span className="text-[10px] text-slate-400 font-mono">
                      [{item.targetCoordinates[0]}, {item.targetCoordinates[1]}]
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-slate-400">{item.description}</div>
                <div className="text-[10px] text-slate-500">
                  Target Knight: <span className="text-slate-300 font-bold">{item.targetKnight}</span>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center">
                {item.dispatched ? (
                  <span className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-[10px] font-bold">
                    ✓ DISPATCHED VIA REYA
                  </span>
                ) : item.handshakeRequired ? (
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 text-[10px] font-bold animate-pulse">
                      HANDSHAKE REQUIRED
                    </span>
                    <button
                      type="button"
                      onClick={() => handleApproveHandshake(item.id)}
                      className="px-2.5 py-1 bg-[#D4AF37]/20 border border-[#D4AF37] text-[#D4AF37] hover:bg-[#D4AF37] hover:text-black text-[10px] font-bold uppercase transition-colors"
                    >
                      Approve Handshake
                    </button>
                  </div>
                ) : (
                  <span className="px-2 py-1 rounded bg-slate-800 text-slate-400 text-[10px]">
                    PENDING DISPATCH
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
