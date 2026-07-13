"use client";

import { useEffect, useRef, useState } from "react";
import { Camera, CircleStop, Eye, Mic, MonitorUp, RefreshCcw, RotateCcw, Volume2 } from "lucide-react";
import { browserInterphaseRuntime, type InterphaseRuntimeProfile } from "@/lib/interphase-runtime";
import type { CartridgeProps } from "../types";

type VisionState = "idle" | "selecting" | "capturing" | "ready" | "blocked" | "unavailable";

function capabilityLabel(enabled: boolean) {
  return enabled ? "READY" : "UNAVAILABLE";
}

export default function InterphaseCartridge({ onInterrupt, transport, status }: CartridgeProps) {
  const [runtime, setRuntime] = useState<InterphaseRuntimeProfile | null>(null);
  const [online, setOnline] = useState(true);
  const [visionState, setVisionState] = useState<VisionState>("idle");
  const [preview, setPreview] = useState<string | null>(null);
  const [capturedAt, setCapturedAt] = useState<string | null>(null);
  const visionBusy = useRef(false);
  const lastCaptureAt = useRef(0);

  useEffect(() => {
    const refresh = () => {
      setRuntime(browserInterphaseRuntime());
      setOnline(navigator.onLine);
    };
    refresh();
    window.addEventListener("resize", refresh);
    window.addEventListener("online", refresh);
    window.addEventListener("offline", refresh);
    return () => {
      window.removeEventListener("resize", refresh);
      window.removeEventListener("online", refresh);
      window.removeEventListener("offline", refresh);
    };
  }, []);

  async function captureLocalContext() {
    const now = performance.now();
    if (visionBusy.current || (lastCaptureAt.current > 0 && now - lastCaptureAt.current < 4_000)) {
      setVisionState("blocked");
      return;
    }
    if (!navigator.mediaDevices?.getDisplayMedia) {
      setVisionState("unavailable");
      return;
    }

    visionBusy.current = true;
    lastCaptureAt.current = now;
    setVisionState("selecting");
    let stream: MediaStream | null = null;
    try {
      stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
      setVisionState("capturing");
      const video = document.createElement("video");
      video.srcObject = stream;
      video.muted = true;
      await video.play();
      const scale = Math.min(1, 960 / Math.max(1, video.videoWidth));
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
      canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
      canvas.getContext("2d")?.drawImage(video, 0, 0, canvas.width, canvas.height);
      setPreview(canvas.toDataURL("image/webp", 0.74));
      setCapturedAt(new Date().toISOString());
      setVisionState("ready");
    } catch (error) {
      setVisionState(error instanceof DOMException && error.name === "NotAllowedError" ? "blocked" : "unavailable");
    } finally {
      stream?.getTracks().forEach((track) => track.stop());
      visionBusy.current = false;
    }
  }

  function resetSession() {
    onInterrupt();
    setPreview(null);
    setCapturedAt(null);
    setVisionState("idle");
    visionBusy.current = false;
    lastCaptureAt.current = 0;
  }

  const recognition = typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);
  const speech = typeof window !== "undefined" && "speechSynthesis" in window;
  const vision = typeof window !== "undefined" && !!navigator.mediaDevices?.getDisplayMedia;
  const retryLabel = transport.nextRetryMs ? `${Math.round(transport.nextRetryMs / 1000)}s` : "--";
  const hostConstrained = (status?.telemetry.memoryPercent ?? 0) >= 85;
  const effectiveMotion = hostConstrained ? "poster-only" : runtime?.motionMode ?? "profiling";
  const runtimeReasons = [
    ...(hostConstrained ? ["host-memory"] : []),
    ...(runtime?.reasons ?? []),
  ];

  return (
    <div className="cartridge-view interphase-cartridge" data-cartridge="interphase">
      <section className="metric-strip interphase-metrics" aria-label="Live interphase capabilities">
        <div><Mic aria-hidden="true" /><span>Voice input</span><strong>{capabilityLabel(recognition)}</strong></div>
        <div><Volume2 aria-hidden="true" /><span>Voice output</span><strong>{capabilityLabel(speech)}</strong></div>
        <div><Eye aria-hidden="true" /><span>Local vision</span><strong>{capabilityLabel(vision)}</strong></div>
        <div><RefreshCcw aria-hidden="true" /><span>Transport</span><strong>{transport.state.toUpperCase()}</strong></div>
      </section>

      <div className="interphase-grid">
        <section className="surface live-session-surface" aria-labelledby="live-session-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Session isolation</p><h2 id="live-session-title">Anya live loop</h2></div>
            <span className={`phase-badge ${transport.state === "live" ? "phase-live" : "phase-warn"}`}>[{transport.state.toUpperCase()}]</span>
          </div>
          <div className="session-lanes">
            <div><span>DEVICE</span><strong>{runtime?.deviceClass ?? "detecting"}</strong><small>{effectiveMotion}</small></div>
            <div><span>NETWORK</span><strong>{online ? "online" : "offline"}</strong><small>browser edge</small></div>
            <div><span>RETRY</span><strong>{transport.attempt}</strong><small>next {retryLabel}</small></div>
          </div>
          <div className="interphase-actions">
            <button type="button" onClick={onInterrupt}><CircleStop aria-hidden="true" /> Interrupt output</button>
            <button type="button" onClick={resetSession}><RotateCcw aria-hidden="true" /> Reset transient state</button>
          </div>
          <p className="runtime-reasons">Runtime guard: {runtimeReasons.length ? runtimeReasons.join(" / ") : "full local capability"}</p>
        </section>

        <section className="surface vision-surface" aria-labelledby="vision-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Operator-mediated context</p><h2 id="vision-title">Local visual context</h2></div>
            <Camera aria-hidden="true" />
          </div>
          <div className="vision-preview">
            {preview ? <img src={preview} alt="Locally captured screen context" /> : <MonitorUp aria-hidden="true" />}
          </div>
          <div className="vision-footer">
            <div><strong>{visionState.replace("_", " ")}</strong><small>{capturedAt ? new Date(capturedAt).toLocaleTimeString() : "No context retained"}</small></div>
            <button type="button" onClick={() => void captureLocalContext()} disabled={visionState === "selecting" || visionState === "capturing"}>
              <Camera aria-hidden="true" /> Capture locally
            </button>
          </div>
          <p className="vision-privacy">Preview remains in volatile browser memory and is never uploaded automatically.</p>
        </section>
      </div>
    </div>
  );
}
