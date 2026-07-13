"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useRef, useState, type CSSProperties, type PointerEvent as ReactPointerEvent } from "react";
import { AudioLines, ChevronDown, ChevronUp, Eye, EyeOff, GripHorizontal, Mic, MicOff, Move, Smartphone, Sparkles, Volume2, VolumeX, Zap } from "lucide-react";
import type { CockpitMode } from "@/lib/cockpit-types";
import { detectDeviceCapabilities, pulseDevice, requestScreenWakeLock, type DeviceCapability, type WakeLockSentinelLike } from "@/lib/device-capabilities";
import { useAnyaPerception } from "@/hooks/use-anya-perception";
import { browserInterphaseRuntime, type InterphaseRuntimeProfile } from "@/lib/interphase-runtime";
import { type VoiceState, voiceStateToLabel } from "@/lib/anya-voice";
import { requestMic, releaseMic, onMicChange } from "@/lib/mic-arbiter";

const AnyaVrmStage = dynamic(() => import("@/components/anya-vrm-stage"), { ssr: false });

const ANYA_MIC_HOLDER = "anya-voice";

type SpeechRecognitionEventLike = Event & {
  results: ArrayLike<{ 0: { transcript: string }; isFinal: boolean }>;
};

type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

export function AnyaPresence({
  mode,
  busy,
  speaking,
  voiceReplies,
  lowPower,
  bargeInSignal,
  onVoiceReplies,
  onBargeIn,
  onTranscript,
}: {
  mode: CockpitMode;
  busy: boolean;
  speaking: boolean;
  voiceReplies: boolean;
  lowPower: boolean;
  bargeInSignal: number;
  onVoiceReplies: (enabled: boolean) => void;
  onBargeIn: () => void;
  onTranscript: (text: string) => void;
}) {
  const avatarVideoUrl = process.env.NEXT_PUBLIC_ANYA_AVATAR_VIDEO_URL;
  const avatarVrmUrl = process.env.NEXT_PUBLIC_ANYA_VRM_URL;
  const presenceRef = useRef<HTMLElement | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const dragRef = useRef<{ pointerId: number; dx: number; dy: number } | null>(null);
  const initialLayoutRef = useRef(false);
  const wakeLockRef = useRef<WakeLockSentinelLike | null>(null);
  const [voiceState, setVoiceState] = useState<VoiceState>(busy ? "thinking" : "idle");
  const [videoReady, setVideoReady] = useState(false);
  const [runtime, setRuntime] = useState<InterphaseRuntimeProfile | null>(null);
  const [expanded, setExpanded] = useState(true);
  const [position, setPosition] = useState<{ x: number; y: number } | null>(null);
  const [capabilities, setCapabilities] = useState<DeviceCapability[]>([]);
  const [wakeLockActive, setWakeLockActive] = useState(false);
  const [perceptionEnabled, setPerceptionEnabled] = useState(false);
  const [vrmReady, setVrmReady] = useState(false);
  const [vrmFailed, setVrmFailed] = useState(false);
  const [micHeldByOther, setMicHeldByOther] = useState<string | null>(null);

  useEffect(() => {
    if (speaking) setVoiceState((current) => (current === "interrupted" ? "interrupted" : "speaking"));
    else if (busy) setVoiceState((current) => (current === "interrupted" ? "interrupted" : "thinking"));
    else if (voiceState === "thinking" || voiceState === "speaking") setVoiceState("idle");
  }, [busy, speaking, voiceState]);

  // bargeInSignal: cockpit-shell increments this every time the operator
  // interrupts the current utterance. We route through the "interrupted"
  // state for 350ms so the avatar state ring visibly shows the cut, then
  // flip to "idle". Natural end of speech (speakAnya onEnd) does NOT
  // increment the signal, so this effect is a no-op for the happy path.
  useEffect(() => {
    if (bargeInSignal === 0) return;
    setVoiceState("interrupted");
    const handle = window.setTimeout(() => setVoiceState("idle"), 350);
    return () => window.clearTimeout(handle);
  }, [bargeInSignal]);

  useEffect(() => {
    const unsubscribe = onMicChange((state) => {
      if (state.holderId && state.holderId !== ANYA_MIC_HOLDER) setMicHeldByOther(state.holderId);
      else setMicHeldByOther(null);
    });
    return unsubscribe;
  }, []);

  useEffect(() => () => {
    recognitionRef.current?.abort();
    releaseMic(ANYA_MIC_HOLDER);
    void wakeLockRef.current?.release();
  }, []);

  useEffect(() => {
    const refresh = () => {
      setRuntime(browserInterphaseRuntime());
      if (!initialLayoutRef.current) {
        setExpanded(window.innerWidth > 920);
        initialLayoutRef.current = true;
      }
    };
    refresh();
    setCapabilities(detectDeviceCapabilities());
    window.addEventListener("resize", refresh);
    return () => window.removeEventListener("resize", refresh);
  }, []);

  function startDrag(event: ReactPointerEvent<HTMLButtonElement>) {
    const bounds = presenceRef.current?.getBoundingClientRect();
    if (!bounds) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    dragRef.current = { pointerId: event.pointerId, dx: event.clientX - bounds.left, dy: event.clientY - bounds.top };
    setPosition({ x: bounds.left, y: bounds.top });
  }

  function drag(event: ReactPointerEvent<HTMLButtonElement>) {
    if (dragRef.current?.pointerId !== event.pointerId || !presenceRef.current) return;
    const width = presenceRef.current.offsetWidth;
    const height = presenceRef.current.offsetHeight;
    const x = Math.max(8, Math.min(window.innerWidth - width - 8, event.clientX - dragRef.current.dx));
    const y = Math.max(64, Math.min(window.innerHeight - height - 8, event.clientY - dragRef.current.dy));
    setPosition({ x, y });
  }

  function stopDrag(event: ReactPointerEvent<HTMLButtonElement>) {
    if (dragRef.current?.pointerId !== event.pointerId) return;
    dragRef.current = null;
    event.currentTarget.releasePointerCapture(event.pointerId);
  }

  async function toggleWakeLock() {
    if (wakeLockRef.current && !wakeLockRef.current.released) {
      await wakeLockRef.current.release();
      wakeLockRef.current = null;
      setWakeLockActive(false);
      return;
    }
    try {
      wakeLockRef.current = await requestScreenWakeLock();
      setWakeLockActive(Boolean(wakeLockRef.current));
    } catch {
      setWakeLockActive(false);
    }
  }

  function toggleListening() {
    if (voiceState === "listening") {
      recognitionRef.current?.stop();
      releaseMic(ANYA_MIC_HOLDER);
      setVoiceState("idle");
      return;
    }

    onBargeIn();

    const grant = requestMic(ANYA_MIC_HOLDER, "operator dictation");
    if (!grant.ok) {
      // Another cartridge already holds the mic. Show "unavailable" with the
      // micHeldByOther surface so the avatar state ring makes the conflict
      // visible instead of silently dropping the request.
      setVoiceState("unavailable");
      return;
    }

    const Recognition = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!Recognition) {
      releaseMic(ANYA_MIC_HOLDER);
      setVoiceState("unavailable");
      return;
    }

    const recognition = new Recognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      const text = Array.from(event.results).map((result) => result[0]?.transcript ?? "").join(" ").trim();
      if (text) {
        setVoiceState("transcribing");
        onTranscript(text);
      }
    };
    recognition.onend = () => {
      releaseMic(ANYA_MIC_HOLDER);
      setVoiceState((current) => (current === "transcribing" ? "idle" : current));
    };
    recognition.onerror = () => {
      releaseMic(ANYA_MIC_HOLDER);
      setVoiceState("unavailable");
    };
    recognitionRef.current = recognition;
    recognition.start();
    setVoiceState("listening");
  }

  const runtimeGuard = lowPower || runtime?.motionMode === "poster-only" || runtime?.reasons.includes("reduced-motion") === true;
  const perception = useAnyaPerception(perceptionEnabled && !runtimeGuard);
  const avatarSignalStyle = {
    "--anya-gaze-x": `${perception.signal.gazeX * 3}px`,
    "--anya-gaze-y": `${perception.signal.gazeY * 2}px`,
  } as CSSProperties;
  const markVrmReady = useCallback(() => setVrmReady(true), []);
  const markVrmFailed = useCallback(() => {
    setVrmReady(false);
    setVrmFailed(true);
  }, []);
  // The className hook `voice-${voiceState}` emits the `.voice-speaking`
  // CSS rule when voiceState === "speaking" (and the parallel
  // .voice-transcribing, .voice-interrupted selectors for the new states).
  // The voiceStateToLabel helper handles the human-readable copy so all
  // seven states are sourced from a single table.
  const label = voiceStateToLabel(voiceState, runtimeGuard, mode);
  const micConflictNote = micHeldByOther
    ? `Mic held by ${micHeldByOther} — Anya voice disabled until released.`
    : null;

  return (
    <section
      ref={presenceRef}
      className={`anya-presence ${expanded ? "anya-expanded" : "anya-collapsed"} voice-${voiceState}${runtimeGuard ? " anya-low-power" : ""}`}
      data-device-class={runtime?.deviceClass ?? "detecting"}
      aria-label="Anya sovereign companion"
      style={position ? { left: position.x, top: position.y, right: "auto", bottom: "auto" } : undefined}
    >
      <div className="anya-dragbar">
        <button type="button" onPointerDown={startDrag} onPointerMove={drag} onPointerUp={stopDrag} onPointerCancel={stopDrag} aria-label="Move Anya" title="Move Anya"><GripHorizontal aria-hidden="true" /></button>
        <span><Sparkles aria-hidden="true" /> Arthurian interphase</span>
        <button type="button" onClick={() => setPosition(null)} aria-label="Dock Anya" title="Dock Anya"><Move aria-hidden="true" /></button>
      </div>

      <div className="anya-avatar-pill">
        <div className="avatar-local-motion" style={avatarSignalStyle}>
          <img className={videoReady || vrmReady ? "avatar-poster avatar-poster-hidden" : "avatar-poster"} src="/anya-fullbody.png" alt="Anya, Camelot's full-body armored digital knight" />
          <span className="avatar-focus" aria-hidden="true" />
          <span className="avatar-speech-field" aria-hidden="true"><i /><i /><i /></span>
        </div>
        {avatarVrmUrl && !runtimeGuard && !vrmFailed ? (
          <AnyaVrmStage modelUrl={avatarVrmUrl} speaking={speaking} signal={perception.signal} reduced={runtime?.motionMode !== "full-motion"} onReady={markVrmReady} onError={markVrmFailed} />
        ) : avatarVideoUrl && !runtimeGuard ? (
          <video
            className={videoReady ? "avatar-video avatar-video-ready" : "avatar-video"}
            src={avatarVideoUrl}
            poster="/anya-fullbody.png"
            muted
            loop
            autoPlay
            playsInline
            onCanPlay={() => setVideoReady(true)}
            onError={() => setVideoReady(false)}
            aria-hidden="true"
          />
        ) : null}
        <div className="avatar-state-ring" aria-hidden="true" />
        <div className="avatar-scan" aria-hidden="true" />
      </div>

      <div className="anya-identity">
        <div className="anya-title-row">
          <strong>Anya</strong>
          <span className={`status-dot status-${mode === "live" ? "online" : mode}`} aria-hidden="true" />
          <small>Omega interphase</small>
        </div>
        <div className="voice-state" role="status" aria-live="polite">
          <AudioLines aria-hidden="true" />
          <span>{label}</span>
          <div className="voice-bars" aria-hidden="true"><i /><i /><i /><i /><i /></div>
          {micConflictNote ? <small className="voice-conflict" role="alert">{micConflictNote}</small> : null}
        </div>
      </div>

      {expanded ? (
        <div className="device-capabilities" aria-label="Available device capabilities">
          {capabilities.map((capability) => (
            <span key={capability.id} className={capability.available ? "available" : "gated"} title={capability.boundary === "native-gated" ? "Requires signed Tauri or Capacitor device bridge" : `${capability.label} browser capability`}>
              {capability.label}
            </span>
          ))}
        </div>
      ) : null}

      <div className="anya-controls">
        <button type="button" className={voiceState === "listening" ? "icon-button active" : "icon-button"} onClick={toggleListening} aria-label={voiceState === "listening" ? "Stop listening" : "Start voice input"} title={voiceState === "listening" ? "Stop listening" : "Voice input"}>
          {voiceState === "listening" ? <MicOff aria-hidden="true" /> : <Mic aria-hidden="true" />}
        </button>
        <button type="button" className={voiceReplies ? "icon-button active" : "icon-button"} onClick={() => onVoiceReplies(!voiceReplies)} aria-label={voiceReplies ? "Disable spoken replies" : "Enable spoken replies"} title="Spoken replies">
          {voiceReplies ? <Volume2 aria-hidden="true" /> : <VolumeX aria-hidden="true" />}
        </button>
        <button type="button" className={perceptionEnabled ? "icon-button active" : "icon-button"} onClick={() => setPerceptionEnabled((current) => !current)} disabled={runtimeGuard || !capabilities.some((capability) => capability.id === "vision" && capability.available)} aria-label={perceptionEnabled ? "Disable local avatar tracking" : "Enable local avatar tracking"} title={`Local perception: ${perception.state}`}>{perceptionEnabled ? <EyeOff aria-hidden="true" /> : <Eye aria-hidden="true" />}</button>
        <button type="button" className="icon-button" onClick={() => pulseDevice()} disabled={!capabilities.some((capability) => capability.id === "haptics" && capability.available)} aria-label="Pulse device" title="Haptic confirmation"><Smartphone aria-hidden="true" /></button>
        <button type="button" className={wakeLockActive ? "icon-button active" : "icon-button"} onClick={() => void toggleWakeLock()} disabled={!capabilities.some((capability) => capability.id === "wake-lock" && capability.available)} aria-label={wakeLockActive ? "Release display wake lock" : "Keep display awake"} title="Display wake lock"><Zap aria-hidden="true" /></button>
        <button type="button" className="icon-button" onClick={() => setExpanded((current) => !current)} aria-label={expanded ? "Collapse Anya" : "Expand Anya"} title={expanded ? "Collapse Anya" : "Expand Anya"}>{expanded ? <ChevronDown aria-hidden="true" /> : <ChevronUp aria-hidden="true" />}</button>
      </div>
    </section>
  );
}
