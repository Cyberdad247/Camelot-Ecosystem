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
//
// Styling uses the tokens from `tailwind.config.js` (the ACTIVE config —
// `tailwind.config.ts` is shadowed by it) to match `components/tabs/*`.

'use client';

import React from 'react';
import { useVoiceFirstRuntime } from '@/hooks/useVoiceFirstRuntime';

export interface InterphaseCartridgeProps {
  /** Host memory signal; drives the runtime resource gate. */
  memoryUsedGb?: number | null;
  memoryTotalGb?: number | null;
}

function stateTone(state: string): string {
  if (state === 'unavailable' || state === 'interrupted') return 'border-red-400/40 text-red-400';
  if (state === 'listening' || state === 'detecting') return 'border-violet/50 text-violet-light';
  return 'border-white/20 text-white/50';
}

export function InterphaseCartridge({
  memoryUsedGb = null,
  memoryTotalGb = null,
}: InterphaseCartridgeProps) {
  const runtime = useVoiceFirstRuntime({
    signal: { memoryUsedGb, memoryTotalGb },
    holderId: 'live-interphase-vfc',
  });

  const metrics = [
    { label: 'Transport', value: runtime.metrics.transport ?? '—' },
    { label: 'Frames', value: String(runtime.metrics.frames) },
    { label: 'Dropped', value: String(runtime.metrics.droppedSamples) },
    { label: 'Utterances', value: String(runtime.metrics.utterances) },
  ];

  return (
    <div className="space-y-3">
      <p className="px-1 text-[11px] text-white/35 uppercase tracking-[0.2em]">
        Voice-First Cartridge
      </p>

      <div className="border border-gold/20 bg-smoke-800/80 backdrop-blur-sm">
        <div className="flex items-center justify-between border-gold/10 border-b px-5 py-4">
          <div>
            <p className="font-display text-gold-light text-sm tracking-minted">
              Microphone Interphase
            </p>
            <p className="mt-1 text-[11px] text-white/35 uppercase tracking-[0.18em]">
              One owner per document · PCM is transient
            </p>
          </div>
          <span
            className={`border px-3 py-1 text-[11px] uppercase tracking-[0.18em] ${stateTone(runtime.state)}`}
          >
            {runtime.state}
          </span>
        </div>

        <div className="flex flex-wrap gap-3 px-5 py-4">
          <button
            type="button"
            onClick={() => void runtime.start()}
            disabled={runtime.active}
            className="border border-gold/50 bg-obsidian px-5 py-3 text-sm text-gold-light uppercase tracking-widest transition-colors hover:bg-gold/10 disabled:opacity-40"
          >
            Start capture
          </button>
          <button
            type="button"
            onClick={() => void runtime.stop()}
            disabled={!runtime.active}
            className="border border-white/20 px-5 py-3 text-sm text-white/60 uppercase tracking-widest transition-colors hover:bg-white/5 disabled:opacity-40"
          >
            Stop capture
          </button>
          <button
            type="button"
            onClick={runtime.interrupt}
            disabled={!runtime.active}
            className="border border-violet/40 px-5 py-3 text-sm text-violet-light uppercase tracking-widest transition-colors hover:bg-violet/10 disabled:opacity-40"
          >
            Barge-in
          </button>
        </div>

        <div className="grid grid-cols-2 gap-px border-gold/10 border-t bg-gold/10 sm:grid-cols-4">
          {metrics.map((cell) => (
            <div key={cell.label} className="bg-smoke-900/60 px-5 py-4">
              <p className="text-[10px] text-white/30 uppercase tracking-[0.18em]">{cell.label}</p>
              <p className="mt-1 font-display text-gold-royal text-lg tracking-minted">
                {cell.value}
              </p>
            </div>
          ))}
        </div>

        {runtime.error ? (
          <div className="border-red-400/30 border-t px-5 py-3 text-red-400 text-xs">
            {runtime.error}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default InterphaseCartridge;
