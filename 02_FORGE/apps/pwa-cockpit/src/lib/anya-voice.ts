"use client";

const receiptPattern = /\b(?:rcpt|appr)-[a-f0-9-]+\b/gi;
const preferredVoiceName = process.env.NEXT_PUBLIC_ANYA_VOICE_NAME?.trim().toLowerCase() ?? "";

// Phase 5: extended voice event schema. The seven states model the full
// Anya voice lifecycle: idle (not capturing), listening (STT capturing
// operator speech), transcribing (audio captured, STT still finalizing),
// thinking (LLM compiling intent), speaking (TTS playing back), interrupted
// (barge-in cut the playback briefly), unavailable (API gated or denied).
// Replaces the prior 5-state machine that conflated idle with ready.
export type VoiceState =
  | "idle"
  | "listening"
  | "transcribing"
  | "thinking"
  | "speaking"
  | "interrupted"
  | "unavailable";

// Centralized label so the presence pill, the TTS router, and the MicArbiter
// (cross-cartridge notifications) all surface the same human-readable state.
// The shape mirrors the prior ternary chain in anya-presence.tsx so the
// existing aria-live region keeps the same copy.
export function voiceStateToLabel(state: VoiceState, runtimeGuard: boolean = false, mode: string = "live"): string {
  if (state === "speaking") return "Speaking";
  if (state === "interrupted") return "Interrupted";
  if (state === "thinking") return "Compiling intent";
  if (state === "transcribing") return "Transcribing";
  if (state === "listening") return "Listening";
  if (state === "unavailable") return "Voice input unavailable";
  if (runtimeGuard) return "Resource guard active";
  if (mode === "offline") return "Edge memory active";
  return "Ready at the edge";
}

export type AnyaSpeechCallbacks = {
  onStart?: () => void;
  onEnd?: () => void;
  onError?: () => void;
};

export function spokenSummary(message: string) {
  const normalized = message.replace(receiptPattern, "").replace(/\s+/g, " ").trim();
  const lower = normalized.toLowerCase();
  if (lower.includes("iron gate approval queued") || lower.includes("approval required")) return "Iron Gate approval required.";
  if (lower.includes("rune allowlist blocked") || lower.includes("allowlist blocked execution")) return "Command approved, but execution policy blocked it.";
  if (lower.includes("rejected and recorded")) return "Command rejected and recorded.";
  if (lower.startsWith("//status refreshed")) return "Status refreshed from local runtime evidence.";
  if (lower.includes("execution failed")) return "Execution failed. Review the event trace.";
  const sentence = normalized.split(/(?<=[.!?])\s/)[0] ?? normalized;
  return sentence.length <= 180 ? sentence : `${sentence.slice(0, 177).trimEnd()}...`;
}

function voiceScore(voice: SpeechSynthesisVoice) {
  const name = voice.name.toLowerCase();
  let score = 0;
  if (preferredVoiceName && name === preferredVoiceName) score += 100;
  if (/^en[-_]us$/i.test(voice.lang)) score += 30;
  else if (/^en/i.test(voice.lang)) score += 15;
  if (/aria|ava|jenny|samantha|sonia|zira|female|natural|neural/i.test(name)) score += 12;
  if (voice.localService) score += 4;
  if (voice.default) score += 2;
  return score;
}

export function selectAnyaVoice(voices: SpeechSynthesisVoice[]) {
  return [...voices].sort((left, right) => voiceScore(right) - voiceScore(left))[0] ?? null;
}

export function primeAnyaVoices() {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.getVoices();
}

export function cancelAnyaSpeech() {
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}

export function speakAnya(message: string, callbacks: AnyaSpeechCallbacks = {}) {
  if (!("speechSynthesis" in window)) return false;
  const text = spokenSummary(message);
  if (!text) return false;

  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 1.02;
  utterance.pitch = 1;
  utterance.volume = 0.92;
  utterance.voice = selectAnyaVoice(synth.getVoices());
  utterance.onstart = () => callbacks.onStart?.();
  utterance.onend = () => callbacks.onEnd?.();
  utterance.onerror = () => callbacks.onError?.();

  synth.cancel();
  synth.speak(utterance);
  return true;
}
