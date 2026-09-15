// SPDX-License-Identifier: MIT
//
// Voice-First Cartridge — Live Interphase mount point.
//
// Re-homed from the purged `02_FORGE/apps/pwa-cockpit`
// `src/cartridges/interphase/interphase-cartridge.tsx` (deleted in 944e4532).
// The cockpit version also carried a screen-capture ("vision") surface bound to
// a `lib/interphase-runtime` module that does not exist in this PWA; that is
// deliberately NOT reproduced here rather than stubbed, so this cartridge has
// exactly one responsibility: arbitrated, bounded microphone capture.

'use client';

import React from 'react';
import { useVoiceFirstRuntime } from '@/hooks/useVoiceFirstRuntime';

export interface InterphaseCartridgeProps {
  /** Host memory signal; drives the runtime resource gate. */
  memoryUsedGb?: number | null;
  memoryTotalGb?: number | null;
}

function stateTone(state: string): string {
  if (state === 'unavailable' || state === 'interrupted') return 'text-rose-400 border-rose-500/40';
  if (state === 'listening' || state === 'detecting') return 'text-emerald-400 border-emerald-500/40';
  return 'text-slate-400 border-slate-700';
}

export function InterphaseCartridge({
  memoryUsedGb = null,
  memoryTotalGb = null,
}: InterphaseCartridgeProps) {
  const runtime = useVoiceFirstRuntime({
    signal: { memoryUsedGb, memoryTotalGb },
    holderId: 'live-interphase-vfc',
  });

  return (
    <div className="border-2 border-[#D4AF37]/40 bg-[#0B0B0E] p-6 shadow-[6px_6px_0px_0px_#D4AF37] space-y-5 font-mono mb-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#D4AF37]/30 pb-4 gap-3">
        <div>
          <div className="text-[10px] text-[#9D4EDD] font-bold tracking-widest uppercase">
            Voice-First Cartridge // Live Interphase
          </div>
          <h2 className="text-xl font-black text-slate-100 uppercase mt-1">Microphone Interphase</h2>
        </div>
        <div
          className={`px-3 py-1 bg-slate-900 border text-xs font-bold uppercase ${stateTone(runtime.state)}`}
        >
          State: {runtime.state}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void runtime.start()}
          disabled={runtime.active}
          className="px-4 py-2 border-2 border-[#D4AF37] text-[#D4AF37] text-xs font-black uppercase tracking-widest disabled:opacity-40 hover:bg-[#D4AF37]/10"
        >
          Start capture
        </button>
        <button
          type="button"
          onClick={() => void runtime.stop()}
          disabled={!runtime.active}
          className="px-4 py-2 border-2 border-slate-700 text-slate-300 text-xs font-black uppercase tracking-widest disabled:opacity-40 hover:bg-slate-800"
        >
          Stop capture
        </button>
        <button
          type="button"
          onClick={runtime.interrupt}
          disabled={!runtime.active}
          className="px-4 py-2 border-2 border-slate-700 text-slate-300 text-xs font-black uppercase tracking-widest disabled:opacity-40 hover:bg-slate-800"
        >
          Barge-in
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Transport', value: runtime.metrics.transport ?? '—' },
          { label: 'Frames', value: String(runtime.metrics.frames) },
          { label: 'Dropped', value: String(runtime.metrics.droppedSamples) },
          { label: 'Utterances', value: String(runtime.metrics.utterances) },
        ].map((cell) => (
          <div key={cell.label} className="p-3 border border-slate-800 bg-slate-950">
            <div className="text-[9px] text-slate-500 uppercase tracking-widest">{cell.label}</div>
            <div className="text-sm font-black text-slate-100 mt-1 truncate">{cell.value}</div>
          </div>
        ))}
      </div>

      {runtime.error ? (
        <div className="p-3 border border-rose-500/40 bg-rose-500/10 text-rose-300 text-xs font-bold">
          {runtime.error}
        </div>
      ) : null}

      <div className="text-[10px] text-slate-500 uppercase tracking-widest">
        One microphone owner per document. PCM is transient and never persisted.
      </div>
    </div>
  );
}

export default InterphaseCartridge;
