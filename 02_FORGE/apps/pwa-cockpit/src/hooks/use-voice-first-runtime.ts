"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  VoiceFirstRuntime,
  type VoiceFrame,
  type VoiceRuntimeMetrics,
  type VoiceRuntimeState,
} from "@camelot/voice-first-runtime";
import type { CockpitStatus } from "@/lib/cockpit-types";

const INITIAL_METRICS: VoiceRuntimeMetrics = {
  state: "idle",
  transport: null,
  frames: 0,
  droppedSamples: 0,
  utterances: 0,
  lastRms: 0,
};

async function sendFrame(frame: VoiceFrame, discontinuity: boolean): Promise<void> {
  const body = frame.samples.slice().buffer as ArrayBuffer;
  const response = await fetch("/api/voice/frames", {
    method: "POST",
    headers: {
      "content-type": "application/octet-stream",
      "x-voice-session": frame.sessionId,
      "x-voice-sequence": String(frame.sequence),
      "x-voice-sample-rate": String(frame.sampleRate),
      "x-voice-discontinuity": discontinuity ? "1" : "0",
    },
    body,
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`Voice ingress returned ${response.status}.`);
}

export function useVoiceFirstRuntime(status: CockpitStatus | null) {
  const runtimeRef = useRef<VoiceFirstRuntime | null>(null);
  const sendingRef = useRef(false);
  const pendingDiscontinuityRef = useRef(false);
  const [metrics, setMetrics] = useState<VoiceRuntimeMetrics>(INITIAL_METRICS);
  const [state, setState] = useState<VoiceRuntimeState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState(false);

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
      holderId: "live-interphase-vfc",
      reason: "local VFC capture",
      resourceGate: () => {
        const used = status?.telemetry.memoryUsedGb;
        const total = status?.telemetry.memoryTotalGb;
        const freeMb = used !== null && used !== undefined && total !== null && total !== undefined
          ? (total - used) * 1024
          : null;
        if ((used ?? 0) > 7.2) return { ok: false, reason: "Host memory exceeds the 7.2 GB voice gate." };
        if (freeMb !== null && freeMb < 800) return { ok: false, reason: "Voice capture requires at least 800 MB free RAM." };
        return { ok: true };
      },
      onState: (next, detail) => {
        setState(next);
        if (detail) setError(detail);
      },
      onMetrics: setMetrics,
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
            setError(reason instanceof Error ? reason.message : "Voice ingress failed.");
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
      setError(reason instanceof Error ? reason.message : "Voice capture could not start.");
    }
  }, [status]);

  const interrupt = useCallback(() => runtimeRef.current?.interrupt(), []);

  useEffect(() => () => {
    void stop();
  }, [stop]);

  return { state, metrics, error, active, start, stop, interrupt };
}
