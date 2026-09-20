// SPDX-License-Identifier: MIT
//
// Voice-First Cartridge — React binding for the shared voice runtime.
//
// Re-homed from the purged `02_FORGE/apps/pwa-cockpit`
// `src/hooks/use-voice-first-runtime.ts` (deleted in 944e4532). The cockpit
// version read host memory off a `CockpitStatus` object that does not exist in
// this PWA, so the gate is now an explicit, host-agnostic signal instead of a
// hard dependency on another app's status contract.

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  VoiceFirstRuntime,
  type ResourceGateResult,
  type VoiceFrame,
  type VoiceRuntimeMetrics,
  type VoiceRuntimeState,
} from '@camelot/voice-first-runtime';

/** Host residency ceiling for voice capture, in GB (blueprint resource contract). */
export const VOICE_GATE_MAX_USED_GB = 7.2;
/** Host headroom floor for voice capture, in MB (blueprint resource contract). */
export const VOICE_GATE_MIN_FREE_MB = 800;

export type VoiceResourceSignal =
  | { memoryUsedGb?: number | null; memoryTotalGb?: number | null }
  | null
  | undefined;

const INITIAL_METRICS: VoiceRuntimeMetrics = {
  state: 'idle',
  transport: null,
  frames: 0,
  droppedSamples: 0,
  utterances: 0,
  lastRms: 0,
};

/**
 * Pure resource gate. Fails closed on an exceeded residency ceiling, and on
 * insufficient headroom when both readings are present. Absent telemetry is
 * treated as "no data" and does not block capture — the same posture the
 * cockpit took.
 */
export function voiceResourceGate(signal: VoiceResourceSignal): ResourceGateResult {
  const used = signal?.memoryUsedGb;
  const total = signal?.memoryTotalGb;
  const hasReadings = typeof used === 'number' && typeof total === 'number';
  const freeMb = hasReadings ? (total - used) * 1024 : null;

  if ((used ?? 0) > VOICE_GATE_MAX_USED_GB) {
    return { ok: false, reason: 'Host memory exceeds the 7.2 GB voice gate.' };
  }
  if (freeMb !== null && freeMb < VOICE_GATE_MIN_FREE_MB) {
    return { ok: false, reason: 'Voice capture requires at least 800 MB free RAM.' };
  }
  return { ok: true };
}

async function sendFrame(frame: VoiceFrame, discontinuity: boolean): Promise<void> {
  const body = frame.samples.slice().buffer as ArrayBuffer;
  const response = await fetch('/api/voice/frames', {
    method: 'POST',
    headers: {
      'content-type': 'application/octet-stream',
      'x-voice-session': frame.sessionId,
      'x-voice-sequence': String(frame.sequence),
      'x-voice-sample-rate': String(frame.sampleRate),
      'x-voice-discontinuity': discontinuity ? '1' : '0',
    },
    body,
    cache: 'no-store',
  });
  if (!response.ok) throw new Error(`Voice ingress returned ${response.status}.`);
}

export interface UseVoiceFirstRuntimeOptions {
  /** Host resource signal consulted before capture starts. */
  signal?: VoiceResourceSignal;
  /** Overrides the default `/voice-capture.worklet.js` asset path. */
  workletUrl?: string;
  /** Lease holder label surfaced to contending consumers. */
  holderId?: string;
  /** Optional transcript/utterance sink. */
  onUtterance?: (samples: Int16Array, truncated: boolean) => void;
}

export function useVoiceFirstRuntime(options: UseVoiceFirstRuntimeOptions = {}) {
  const { signal, workletUrl, holderId = 'pwa-voice-first', onUtterance } = options;

  const runtimeRef = useRef<VoiceFirstRuntime | null>(null);
  const sendingRef = useRef(false);
  const pendingDiscontinuityRef = useRef(false);
  const signalRef = useRef<VoiceResourceSignal>(signal);
  const onUtteranceRef = useRef<UseVoiceFirstRuntimeOptions['onUtterance']>(onUtterance);
  const [metrics, setMetrics] = useState<VoiceRuntimeMetrics>(INITIAL_METRICS);
  const [state, setState] = useState<VoiceRuntimeState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState(false);

  // Keep the latest signal/callback reachable from the runtime closure without
  // re-creating it on every render.
  signalRef.current = signal;
  onUtteranceRef.current = onUtterance;

  const stop = useCallback(async () => {
    const runtime = runtimeRef.current;
    runtimeRef.current = null;
    setActive(false);
    if (runtime) await runtime.stop();
    sendingRef.current = false;
    pendingDiscontinuityRef.current = false;
  }, []);

  const start = useCallback(async () => {
    if (runtimeRef.current) return;
    setError(null);
    const runtime = new VoiceFirstRuntime({
      holderId,
      reason: 'local VFC capture',
      workletUrl,
      resourceGate: () => voiceResourceGate(signalRef.current),
      onState: (next, detail) => {
        setState(next);
        if (detail) setError(detail);
      },
      onMetrics: setMetrics,
      onUtterance: (utterance) => onUtteranceRef.current?.(utterance.samples, utterance.truncated),
      onFrame: (frame) => {
        if (sendingRef.current) {
          pendingDiscontinuityRef.current = true;
          return;
        }
        sendingRef.current = true;
        const discontinuity = frame.discontinuity || pendingDiscontinuityRef.current;
        pendingDiscontinuityRef.current = false;
        void sendFrame(frame, discontinuity)
          .catch((reason: unknown) => {
            pendingDiscontinuityRef.current = true;
            setError(reason instanceof Error ? reason.message : 'Voice ingress failed.');
          })
          .finally(() => {
            sendingRef.current = false;
          });
      },
    });
    runtimeRef.current = runtime;
    setActive(true);
    try {
      await runtime.start();
    } catch (reason) {
      runtimeRef.current = null;
      setActive(false);
      setError(reason instanceof Error ? reason.message : 'Voice capture could not start.');
    }
  }, [holderId, workletUrl]);

  const interrupt = useCallback(() => runtimeRef.current?.interrupt(), []);

  useEffect(
    () => () => {
      void stop();
    },
    [stop]
  );

  return { state, metrics, error, active, start, stop, interrupt };
}
