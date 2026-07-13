import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function source(path) {
  return readFile(new URL(`../${path}`, import.meta.url), "utf8");
}

const VOICE_STATES = [
  "idle",
  "listening",
  "transcribing",
  "thinking",
  "speaking",
  "interrupted",
  "unavailable",
];

test("Anya voice state machine is the full 7-state lifecycle", async () => {
  const file = await source("src/lib/anya-voice.ts");
  assert.match(file, /export type VoiceState\s*=\s*([\s\S]+?);/);
  for (const state of VOICE_STATES) {
    assert.match(file, new RegExp(`"${state}"`), `VoiceState must include "${state}"`);
  }
  // No legacy "ready" alias remains in the union.
  assert.doesNotMatch(file, /"ready"/);
  assert.match(file, /export function voiceStateToLabel/);
});

test("voiceStateToLabel covers every state plus runtime guard + offline mode", async () => {
  const file = await source("src/lib/anya-voice.ts");
  assert.match(file, /if \(state === "speaking"\) return "Speaking"/);
  assert.match(file, /if \(state === "interrupted"\) return "Interrupted"/);
  assert.match(file, /if \(state === "transcribing"\) return "Transcribing"/);
  assert.match(file, /if \(state === "listening"\) return "Listening"/);
  assert.match(file, /if \(state === "unavailable"\) return "Voice input unavailable"/);
  assert.match(file, /if \(state === "thinking"\) return "Compiling intent"/);
  assert.match(file, /if \(runtimeGuard\) return "Resource guard active"/);
  assert.match(file, /if \(mode === "offline"\) return "Edge memory active"/);
  assert.match(file, /return "Ready at the edge"/);
});

test("MicArbiter exposes the cross-cartridge arbitration contract", async () => {
  const file = await source("src/lib/mic-arbiter.ts");
  assert.match(file, /export type MicState/);
  assert.match(file, /export type MicGrant/);
  assert.match(file, /export function requestMic\(holderId: string, reason: string\): MicGrant/);
  assert.match(file, /export function releaseMic\(holderId: string\)/);
  assert.match(file, /export function currentHolder\(\): string \| null/);
  assert.match(file, /export function micState\(\): MicState/);
  assert.match(file, /export function onMicChange/);
  assert.match(file, /export function clearMicArbiter/);
  // Rejects a second concurrent holder.
  assert.match(file, /state\.holderId !== null && state\.holderId !== holderId/);
  assert.match(file, /ok: false, currentHolder: state\.holderId/);
  // Lets the same holder re-acquire.
  assert.match(file, /return \{[\s\S]+ok: true,[\s\S]+revoke/);
  // Notifies subscribers on every transition.
  assert.match(file, /subscribers\.forEach|for \(const callback of subscribers\)/);
  // Phase 5 scope: no shell exec, no PowerShell, no cmd.exe.
  assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
});

test("TTS router prefers Multivoice and visibly labels vendor-cloud fallback", async () => {
  const file = await source("src/lib/tts-router.ts");
  assert.match(file, /export async function synthesizeSpeech/);
  assert.match(file, /export function isTrustedTtsHost/);
  assert.match(file, /export function currentTtsProvider/);
  assert.match(file, /export type TtsProvider/);
  assert.match(file, /export type TtsResult/);
  // Priority chain order: multivoice first, vendor fallback second, browser last.
  assert.match(file, /readMultivoiceUrl/);
  assert.match(file, /readVendorFallbackEnabled/);
  // Trusted-host check mirrors Kickbox-audio/mcp-query/src/query.ts.
  assert.match(file, /TS_CGNAT/);
  assert.match(file, /100\\.\(6\[4-9\]/);
  assert.match(file, /\\.ts\\.net/);
  assert.match(file, /localhost/);
  assert.match(file, /127\.0\.0\.1/);
  // Visible fallback labeling is the security property.
  assert.match(file, /"multivoice" \| "vendor-cloud" \| "browser-synth"/);
  assert.match(file, /TTS: vendor cloud/);
  assert.match(file, /fallback: multivoice unreachable/);
  assert.match(file, /fallback: multivoice not configured/);
  assert.match(file, /fallbackReason/);
  // Phase 5 honesty gate: vendor-cloud only fires when BOTH fallback flag
  // AND vendor URL are configured. Otherwise we fall through to browser-synth
  // with a clear "not wired in Phase 5" note so the operator is never told
  // audio is going to a vendor when the wiring is missing.
  assert.match(file, /NEXT_PUBLIC_TTS_VENDOR_URL/);
  assert.match(file, /vendor-cloud not wired in Phase 5/);
  // Phase 5 scope: no native whisper bridges.
  assert.doesNotMatch(file, /whisper\.cpp|whisper_cpp|whisperCpp|ggml-whisper/);
  assert.doesNotMatch(file, /child_process|powershell|cmd\.exe/);
});

test("Anya presence routes microphone access through the arbiter on every transition", async () => {
  const file = await source("src/components/anya-presence.tsx");
  assert.match(file, /import \{ type VoiceState, voiceStateToLabel \} from "@\/lib\/anya-voice"/);
  assert.match(file, /import \{ requestMic, releaseMic, onMicChange \} from "@\/lib\/mic-arbiter"/);
  assert.match(file, /const ANYA_MIC_HOLDER = "anya-voice"/);
  // Initial state is "idle" (no longer "ready").
  assert.match(file, /useState<VoiceState>\(busy \? "thinking" : "idle"\)/);
  // toggleListening acquires the mic.
  assert.match(file, /const grant = requestMic\(ANYA_MIC_HOLDER, "operator dictation"\)/);
  // Conflict path surfaces "unavailable" instead of dropping silently.
  assert.match(file, /if \(!grant\.ok\)/);
  // Release happens on stop / onend / onerror so the holder slot does not leak.
  assert.match(file, /releaseMic\(ANYA_MIC_HOLDER\)/);
  // The transcribing intermediate state fires on first STT result.
  assert.match(file, /setVoiceState\("transcribing"\)/);
  // CSS class hook still emits .voice-speaking for the speaking state.
  assert.match(file, /voice-\$\{voiceState\}/);
  // The presence pill renders the mic-conflict note.
  assert.match(file, /voice-conflict/);
  // bargeInSignal prop is plumbed so the "interrupted" state is reachable
  // on operator barge-in (350ms flash before returning to "idle").
  assert.match(file, /bargeInSignal: number/);
  assert.match(file, /setVoiceState\("interrupted"\)/);
  assert.match(file, /window\.setTimeout\(\(\) => setVoiceState\("idle"\), 350\)/);
  // No shell exec, no native bridge in Phase 5.
  assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
  assert.doesNotMatch(file, /whisper\.cpp|whisper_cpp/);
});

test("Cockpit shell routes voice through the TTS router and surfaces the provider label", async () => {
  const file = await source("src/components/cockpit-shell.tsx");
  assert.match(file, /import \{ synthesizeSpeech, currentTtsProvider, type TtsProvider \} from "@\/lib\/tts-router"/);
  // ttsLabel initial value is derived from currentTtsProvider() so the
  // heading and the per-message tag never disagree at mount.
  assert.match(file, /useState<string>\(\(\) => \{/);
  assert.match(file, /const provider = currentTtsProvider\(\)/);
  // speak() awaits the router and falls through to browser-synth on failure.
  assert.match(file, /async function speak\(text: string\)/);
  assert.match(file, /await synthesizeSpeech\(/);
  assert.match(file, /setTtsLabel\(result\.label\)/);
  // Multivoice path decodes ArrayBuffer through AudioContext.
  assert.match(file, /result\.provider === "multivoice" && result\.audio/);
  assert.match(file, /ctx\.decodeAudioData\(result\.audio/);
  // Vendor-cloud path is in the prefix ternary; the prefix is composed
  // separately from the spoken text so the same pattern serves the
  // fallbackReason + vendor-cloud + decode-failure branches.
  assert.match(file, /result\.provider === "vendor-cloud"/);
  assert.match(file, /\$\{result\.label\}\. /);
  assert.match(file, /\$\{prefix\}\$\{result\.spokenText\}/);
  // Audio decode failure and AudioContext-unavailable both fall through
  // to fallbackToBrowserSynth with an explicit labeled prefix.
  assert.match(file, /multivoice audio decode failed/);
  assert.match(file, /AudioContext unavailable/);
  // fallbackToBrowserSynth takes a single arg now (the unused _reason
  // parameter was removed in this pass).
  assert.match(file, /function fallbackToBrowserSynth\(text: string\)/);
  // Barge-in closes the multivoice AudioContext AND increments the
  // bargeInSignal so the presence component flashes "interrupted".
  assert.match(file, /function bargeIn\(\)/);
  assert.match(file, /setBargeInSignal\(\(current\) => current \+ 1\)/);
  assert.match(file, /ttsAudioCtx|ttsAudioSource/);
  assert.match(file, /source\.stop\(\)/);
  // The Anya message is tagged (not the operator's) by scanning backward
  // for the newest Anya entry whose text matches the synthesized response.
  assert.match(file, /next\[i\]\.role === "anya" && next\[i\]\.text === text/);
  // The Anya channel heading surfaces the current provider label.
  assert.match(file, /tts-provider/);
  assert.match(file, /data-provider=\{ttsProvider\}/);
  // Per-message provider tag annotates the most recent Anya message.
  assert.match(file, /message\.providerLabel/);
  // voiceReplies gate is preserved.
  assert.match(file, /if \(!voiceReplies\) return/);
  // No native bridge in Phase 5.
  assert.doesNotMatch(file, /whisper\.cpp|whisper_cpp|child_process|powershell/);
});

test("voice contract is the source of truth for the presence pill labels", async () => {
  // The centralized label helper is imported by Anya presence; the cockpit
  // shell relies on the TTS router for the TTS-side label. Both must be the
  // single source of truth — no second string table elsewhere.
  const presence = await source("src/components/anya-presence.tsx");
  const voice = await source("src/lib/anya-voice.ts");
  const shell = await source("src/components/cockpit-shell.tsx");
  assert.match(presence, /voiceStateToLabel\(voiceState, runtimeGuard, mode\)/);
  // The presence ternary chain is gone; the helper does the work.
  assert.doesNotMatch(presence, /voiceState === "speaking"\s*\?\s*"Speaking"/);
  // The TTS router exports the label for the shell.
  assert.match(voice, /export function voiceStateToLabel/);
  assert.match(shell, /currentTtsProvider\(\)/);
});
