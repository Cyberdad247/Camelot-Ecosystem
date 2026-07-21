import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function source(path) {
  return readFile(new URL(`../${path}`, import.meta.url), "utf8");
}

test("manifest exposes an installable standalone shell", async () => {
  const manifest = JSON.parse(await source("public/manifest.json"));
  assert.equal(manifest.start_url, "/");
  assert.equal(manifest.display, "standalone");
  assert.ok(manifest.icons.some((icon) => icon.sizes === "192x192" && icon.type === "image/png"));
  assert.ok(manifest.icons.some((icon) => icon.sizes === "512x512" && icon.type === "image/png"));
  assert.ok(manifest.shortcuts.some((shortcut) => shortcut.url.includes("cartridge=factory")));
});

test("service worker excludes every privileged API route", async () => {
  const worker = await source("public/sw.js");
  assert.match(worker, /url\.pathname\.startsWith\("\/api\/"\)/);
  assert.match(worker, /request\.method !== "GET"/);
  assert.match(worker, /offline\.html/);
  assert.match(worker, /anya-cockpit-[a-f0-9]{12}/);
  assert.match(worker, /CACHE_RESOURCES_COMPLETE/);
});

test("service worker cache identity is derived during every production build", async () => {
  const generator = await source("scripts/generate-service-worker.mjs");
  const packageJson = JSON.parse(await source("package.json"));
  assert.match(generator, /createHash\("sha256"\)/);
  assert.match(generator, /filesUnder\(sourceRoot\)/);
  assert.match(packageJson.scripts.prebuild, /service-worker/);
});

test("cartridges mount from an explicit trusted dynamic catalog", async () => {
  const registry = await source("src/cartridges/registry.tsx");
  for (const cartridge of ["command", "factory", "forge-law", "intelligence", "interphase", "device-hall", "mesh"]) {
    assert.match(registry, new RegExp(`${cartridge.includes("-") ? `"${cartridge}"` : cartridge}: dynamic`));
  }
  assert.doesNotMatch(registry, /https?:\/\//);
  assert.match(registry, /class CartridgeBoundary/);
  assert.match(registry, /Promise\.allSettled/);
  assert.match(registry, /preloadTrustedCartridges/);
});

test("Anya motion and local perception remain lazy, bounded, and disposable", async () => {
  const presence = await source("src/components/anya-presence.tsx");
  const stage = await source("src/components/anya-vrm-stage.tsx");
  const hook = await source("src/hooks/use-anya-perception.ts");
  const worker = await source("src/workers/anya-perception.worker.ts");
  const nextConfig = await source("next.config.ts");

  assert.match(presence, /dynamic\(\(\) => import\("@\/components\/anya-vrm-stage"\)/);
  assert.match(presence, /NEXT_PUBLIC_ANYA_VRM_URL/);
  assert.match(stage, /VRMLoaderPlugin/);
  assert.match(stage, /VRMUtils\.deepDispose/);
  assert.match(stage, /1000 \/ 30/);
  assert.match(hook, /new Worker\(new URL/);
  assert.match(hook, /getUserMedia/);
  assert.match(hook, /frameRate: \{ ideal: 12, max: 15 \}/);
  assert.match(hook, /stream\?\.getTracks\(\)\.forEach\(\(track\) => track\.stop\(\)\)/);
  assert.match(worker, /frame\.close\(\)/);
  assert.doesNotMatch(worker, /fetch\(|localStorage|indexedDB/);
  assert.match(nextConfig, /camera=\(self\)/);
  assert.match(nextConfig, /microphone=\(self\)/);
});

test("Device Hall uses signed allowlisted bridges and Iron Gate delivery", async () => {
  const control = await source("src/lib/device-control.ts");
  const contract = await source("src/lib/device-contract.ts");
  const devices = await source("src/app/api/devices/route.ts");
  const actions = await source("src/app/api/devices/[id]/actions/route.ts");
  const approval = await source("src/app/api/approvals/[id]/route.ts");
  const desktop = await source("native/desktop-bridge/src-tauri/src/lib.rs");
  const mobile = await source("native/mobile-bridge/src/main.ts");

  assert.match(contract, /desktop\.notification/);
  assert.match(contract, /mobile\.haptic/);
  assert.match(control, /asymmetricKeyType !== "ed25519"/);
  assert.match(control, /seenNonces\.has/);
  assert.match(control, /Math\.abs\(now - Number\(timestamp\)\) > 60_000/);
  assert.match(control, /verify\(null/);
  assert.match(devices, /isAuthorized/);
  assert.match(devices, /isCrossSiteRequest/);
  assert.match(actions, /createApproval\(`\/\/DEVICE/);
  assert.match(approval, /resolveDeviceAction/);
  assert.match(desktop, /KEYRING_SERVICE/);
  assert.match(desktop, /Capability is not implemented by the desktop allowlist/);
  assert.match(mobile, /generateKey\(\{ name: "Ed25519" \}, false/);
  assert.match(mobile, /Intent target is outside the mobile allowlist/);
  for (const unsafe of [control, desktop, mobile]) assert.doesNotMatch(unsafe, /child_process|cmd\.exe|powershell|Command::new|std::process/i);
});

test("Forge Queue renders immutable evidence and digest-bound execution requests", async () => {
  const registry = await source("src/cartridges/registry.tsx");
  const component = await source("src/cartridges/forge-law/forge-law-cartridge.tsx");
  const contract = await source("src/lib/forge-law.ts");
  const collection = await source("src/app/api/forge/route.ts");
  const detail = await source("src/app/api/forge/[id]/route.ts");
  const approval = await source("src/app/api/approvals/[id]/route.ts");

  assert.match(registry, /import\("\.\/forge-law\/forge-law-cartridge"\)/);
  assert.match(component, /\/\/CRYSTALLIZE blueprints\/v10000\.1/);
  assert.match(component, /`\/\/EXECUTE_PROMPT \$\{selected\.id\}`/);
  assert.match(component, /selected\.operations\.map/);
  assert.match(contract, /forgeApprovalBinding/);
  assert.match(contract, /runtime_state.*forge_law/s);
  assert.match(collection, /isAuthorized/);
  assert.match(detail, /isAuthorized/);
  assert.match(approval, /forgeApprovalBinding\(approval\.command\)/);
  assert.doesNotMatch(collection, /POST|PUT|PATCH|DELETE/);
});

test("mutating runes remain behind the approval boundary", async () => {
  const route = await source("src/app/api/commands/route.ts");
  assert.match(route, /readOnlyRunes = new Set\(\["\/\/STATUS"\]\)/);
  assert.match(route, /isRunic && !readOnlyRunes\.has/);
  assert.match(route, /isCrossSiteRequest/);
  assert.match(route, /isAuthorized/);
  assert.doesNotMatch(route, /child_process/);
  assert.doesNotMatch(route, /\bexec\s*\(/);
  assert.doesNotMatch(route, /directive === "\/\/LAUNCH_CELL"/);
  assert.doesNotMatch(route, /executeRunic/);
  assert.match(route, /no harness task was queued/);
});

test("remote access uses a strict HttpOnly operator session", async () => {
  const session = await source("src/app/api/session/route.ts");
  const auth = await source("src/lib/cockpit-auth.ts");
  assert.match(session, /httpOnly: true/);
  assert.match(session, /sameSite: "strict"/);
  assert.match(auth, /CAMELOT_COCKPIT_TOKEN/);
  assert.match(auth, /timingSafeEqual/);
  assert.match(auth, /createHmac\("sha256", token\)/);
  assert.match(auth, /randomBytes\(18\)/);
  assert.match(auth, /expiresAt <= nowSeconds/);
  assert.match(session, /OPERATOR_SESSION_TTL_SECONDS/);
  assert.match(auth, /current\.count >= 5/);
  assert.match(auth, /process\.env\.NODE_ENV !== "production"/);
  assert.doesNotMatch(auth, /x-forwarded-host/);
  assert.match(auth, /x-forwarded-proto/);
  assert.match(session, /secure: isSecureRequest\(request\)/);
});

test("passkeys are local, user-verified, replay-resistant, and token recovery remains explicit", async () => {
  const shell = await source("src/components/cockpit-shell.tsx");
  const challenges = await source("src/lib/passkey-challenges.ts");
  const store = await source("src/lib/passkey-store.ts");
  const registerOptions = await source("src/app/api/passkeys/register/options/route.ts");
  const registerVerify = await source("src/app/api/passkeys/register/verify/route.ts");
  const authVerify = await source("src/app/api/passkeys/authenticate/verify/route.ts");

  assert.match(shell, /startAuthentication/);
  assert.match(shell, /startRegistration/);
  assert.match(shell, /Continue with passkey/);
  assert.match(shell, /<details className="recovery-access"/);
  assert.match(registerOptions, /isAuthorized\(request\)/);
  assert.match(registerOptions, /userVerification: "required"/);
  assert.match(registerVerify, /consumePasskeyChallenge/);
  assert.match(registerVerify, /requireUserVerification: true/);
  assert.match(authVerify, /newCounter/);
  assert.match(authVerify, /OPERATOR_SESSION_TTL_SECONDS/);
  assert.match(challenges, /challenges\.delete\(transactionId\)/);
  assert.match(challenges, /PASSKEY_CHALLENGE_TTL_SECONDS = 5 \* 60/);
  assert.match(store, /pwa_cockpit_passkeys\.json/);
  assert.match(store, /fsyncSync/);
  assert.match(store, /BACKUP_PATH/);
  assert.doesNotMatch(store, /privateKey/i);
});

test("live runic execution is explicit and shell-free", async () => {
  const adapter = await source("src/lib/runic-adapter.ts");
  const grant = await source("src/lib/approval-grant.ts");
  const approval = await source("src/app/api/approvals/[id]/route.ts");
  assert.match(adapter, /CAMELOT_COCKPIT_EXEC_ENABLED/);
  assert.match(adapter, /CAMELOT_COCKPIT_ALLOWED_RUNES/);
  assert.match(adapter, /allowedRunes\(\)\.has\(directive\)/);
  assert.match(adapter, /result\.status !== "ROUTED"/);
  assert.match(adapter, /result\.queued !== true/);
  assert.match(adapter, /execFileAsync\(CAMELOT_BINARY/);
  assert.match(adapter, /CAMELOT_COCKPIT_APPROVAL_GRANT/);
  assert.match(adapter, /CAMELOT_COCKPIT_REQUIRE_APPROVAL_GRANT/);
  assert.doesNotMatch(adapter, /shell:\s*true/);
  assert.match(grant, /commandDigest/);
  assert.match(grant, /createHmac\("sha256", key\)/);
  assert.match(grant, /GRANT_TTL_SECONDS = 90/);
  assert.match(approval, /issueApprovalGrant\(approval\.id, approval\.command, binding\)/);
  assert.match(grant, /GRANT_CONTEXT_V2/);
  assert.match(grant, /cartridgeDigest/);
  assert.match(approval, /execution_blocked/);
  assert.match(approval, /createReceipt\(approval\.command, "executed"\)/);
});

test("Anya video presence has a local visual fallback", async () => {
  const presence = await source("src/components/anya-presence.tsx");
  const styles = await source("src/app/globals.css");
  assert.match(presence, /NEXT_PUBLIC_ANYA_AVATAR_VIDEO_URL/);
  assert.match(presence, /avatarVideoUrl && !runtimeGuard/);
  assert.match(presence, /src="\/anya-fullbody\.png"/);
  assert.match(presence, /onError=\{\(\) => setVideoReady\(false\)\}/);
  assert.match(presence, /avatar-local-motion/);
  assert.match(presence, /avatar-state-ring/);
  assert.match(styles, /@keyframes avatar-presence/);
  assert.match(styles, /\.voice-speaking \.avatar-local-motion/);
  assert.match(styles, /\.anya-low-power \.avatar-local-motion/);
});

test("Anya is a movable cross-cartridge companion with bounded hardware capabilities", async () => {
  const presence = await source("src/components/anya-presence.tsx");
  const capabilities = await source("src/lib/device-capabilities.ts");
  const shell = await source("src/components/cockpit-shell.tsx");
  const styles = await source("src/app/globals.css");

  assert.match(shell, /<AnyaPresence[\s\S]+<CartridgeMount/);
  assert.match(presence, /onPointerDown=\{startDrag\}/);
  assert.match(presence, /setPointerCapture/);
  assert.match(presence, /Math\.min\(window\.innerWidth - width - 8/);
  assert.match(presence, /setPosition\(null\)/);
  assert.match(presence, /requestScreenWakeLock/);
  assert.match(presence, /pulseDevice/);
  assert.match(capabilities, /boundary: "native-gated"/);
  assert.match(capabilities, /available: false/);
  assert.doesNotMatch(capabilities, /child_process|powershell|cmd\.exe|exec\(/i);
  assert.match(styles, /\.anya-presence \{[\s\S]+position: fixed/);
  assert.match(styles, /\.anya-collapsed/);
});

test("Anya speech is user-gated, terse, deterministic, and supports barge-in", async () => {
  const voice = await source("src/lib/anya-voice.ts");
  const shell = await source("src/components/cockpit-shell.tsx");
  const presence = await source("src/components/anya-presence.tsx");
  assert.match(voice, /NEXT_PUBLIC_ANYA_VOICE_NAME/);
  assert.match(voice, /selectAnyaVoice/);
  assert.match(voice, /receiptPattern/);
  assert.match(voice, /synth\.cancel\(\)/);
  assert.match(shell, /if \(!voiceReplies\) return/);
  assert.match(shell, /function bargeIn\(\)/);
  assert.match(presence, /onBargeIn\(\)/);
  // Phase 5: the className hook `voice-${voiceState}` emits the
  // .voice-speaking CSS rule for the speaking state, and the
  // .voice-transcribing / .voice-interrupted rules for the new states.
  assert.match(presence, /voice-\$\{voiceState\}/);
  // Phase 5: 7-state machine + centralized label helper.
  assert.match(presence, /voiceStateToLabel/);
  assert.match(presence, /import \{ type VoiceState, voiceStateToLabel \}/);
});

test("Live Interphase adopts resilient local-first patterns without importing unsafe desktop control", async () => {
  const cartridge = await source("src/cartridges/interphase/interphase-cartridge.tsx");
  const runtime = await source("src/lib/interphase-runtime.ts");
  const shell = await source("src/components/cockpit-shell.tsx");
  const manifests = await source("src/cartridges/manifests.ts");

  assert.match(manifests, /id: "interphase"/);
  assert.match(manifests, /vision\.capture-local/);
  assert.match(cartridge, /getDisplayMedia/);
  assert.match(cartridge, /stream\?\.getTracks\(\)\.forEach\(\(track\) => track\.stop\(\)\)/);
  assert.match(cartridge, /toDataURL\("image\/webp", 0\.74\)/);
  assert.match(cartridge, /onInterrupt\(\)/);
  assert.match(cartridge, /lastCaptureAt\.current > 0 && now - lastCaptureAt\.current < 4_000/);
  assert.match(cartridge, /hostConstrained/);
  assert.match(cartridge, /host-memory/);
  assert.doesNotMatch(cartridge, /fetch\(|localStorage|indexedDB/);
  assert.match(runtime, /prefersReducedMotion/);
  assert.match(runtime, /saveData/);
  assert.match(runtime, /hardwareConcurrency/);
  assert.match(shell, /retrySchedule = \[3_000, 6_000, 12_000, 60_000\]/);
  assert.match(shell, /state: "reconnecting"/);
});

test("Phase 5 voice pipeline is governed by MicArbiter, TTS router, and the 7-state machine", async () => {
  const voice = await source("src/lib/anya-voice.ts");
  const mic = await source("src/lib/mic-arbiter.ts");
  const tts = await source("src/lib/tts-router.ts");
  const presence = await source("src/components/anya-presence.tsx");
  const shell = await source("src/components/cockpit-shell.tsx");

  // Voice state schema: the 7-state machine is exported from anya-voice.
  for (const state of ["idle", "listening", "transcribing", "thinking", "speaking", "interrupted", "unavailable"]) {
    assert.match(voice, new RegExp(`"${state}"`));
  }
  assert.match(voice, /export type VoiceState/);
  assert.match(voice, /export function voiceStateToLabel/);

  // MicArbiter exports the cross-cartridge arbitration API.
  assert.match(mic, /export function requestMic/);
  assert.match(mic, /export function releaseMic/);
  assert.match(mic, /export function currentHolder/);
  assert.match(mic, /export function onMicChange/);
  assert.match(mic, /export function clearMicArbiter/);
  assert.match(mic, /MicGrant/);
  // No native bridges in Phase 5.
  assert.doesNotMatch(mic, /child_process|powershell|cmd\.exe|exec\(/i);

  // TTS router exports the priority chain + trusted-host check.
  assert.match(tts, /export async function synthesizeSpeech/);
  assert.match(tts, /export function isTrustedTtsHost/);
  assert.match(tts, /export function currentTtsProvider/);
  assert.match(tts, /NEXT_PUBLIC_MULTIVOICE_URL/);
  assert.match(tts, /NEXT_PUBLIC_TTS_VENDOR_FALLBACK/);
  // Visible fallback labeling is the security property.
  assert.match(tts, /"multivoice" \| "vendor-cloud" \| "browser-synth"/);
  assert.match(tts, /vendor cloud/);
  assert.match(tts, /fallback: multivoice unreachable/);
  // Trusted-host regex mirrors Kickbox-audio/mcp-query exactly.
  assert.match(tts, /100\\.\(6\[4-9\]/);
  assert.match(tts, /\\.ts\\.net/);
  // No native whisper bridges in Phase 5.
  assert.doesNotMatch(tts, /whisper\.cpp|whisper_cpp|whisperCpp/);

  // Anya presence uses the new state machine and routes mic access through
  // the arbiter. releaseMic fires in onend AND onerror so the holder slot
  // does not leak when STT terminates unexpectedly.
  assert.match(presence, /import \{ type VoiceState, voiceStateToLabel \} from "@\/lib\/anya-voice"/);
  assert.match(presence, /import \{ requestMic, releaseMic, onMicChange \} from "@\/lib\/mic-arbiter"/);
  assert.match(presence, /requestMic\(ANYA_MIC_HOLDER/);
  assert.match(presence, /releaseMic\(ANYA_MIC_HOLDER\)/);
  assert.match(presence, /setVoiceState\("transcribing"\)/);
  assert.match(presence, /setVoiceState\("interrupted"\)|interrupted/);
  // The CSS class hook still emits .voice-speaking for the speaking state.
  assert.match(presence, /voice-\$\{voiceState\}/);

  // Cockpit shell routes speak() through tts-router and surfaces the
  // provider label in the Anya channel UI.
  assert.match(shell, /import \{ synthesizeSpeech, currentTtsProvider/);
  assert.match(shell, /await synthesizeSpeech\(/);
  assert.match(shell, /setTtsLabel\(result\.label\)/);
  assert.match(shell, /provider: result\.provider/);
  assert.match(shell, /tts-provider/);
  // Barge-in closes the multivoice AudioContext so audio does not leak past
  // the operator's interrupt.
  assert.match(shell, /function bargeIn\(\)/);
  assert.match(shell, /ttsAudioCtx|ttsAudioSource/);
  assert.match(shell, /source\.stop\(\)/);
});

test("Voice-first cartridge uses bounded PCM frames and a loopback-only OmniVoice bridge", async () => {
  const hook = await source("src/hooks/use-voice-first-runtime.ts");
  const route = await source("src/app/api/voice/frames/route.ts");
  const cartridge = await source("src/cartridges/interphase/interphase-cartridge.tsx");
  const config = await source("next.config.ts");
  const runtime = await source("../../packages/voice-first-runtime/src/voice-first-runtime.ts");
  const ring = await source("../../packages/voice-first-runtime/src/shared-pcm-ring.ts");
  const worklet = await source("public/voice-capture.worklet.js");
  const omniVoice = await source("../../KINETIC_ARMORY/omnivoice-router/omnivoice-router.ts");
  const worker = await source("../../../control_plane/worker.py");

  assert.match(hook, /new VoiceFirstRuntime/);
  assert.match(hook, /memory exceeds the 7\.2 GB voice gate/);
  assert.match(hook, /at least 800 MB free RAM/);
  assert.match(hook, /pendingDiscontinuityRef/);
  assert.match(route, /MAX_FRAME_BYTES = 3_200/);
  assert.match(route, /operatorCapabilities\(request\)\.includes\("voice\.use"\)/);
  assert.match(route, /127\.0\.0\.1/);
  assert.match(route, /AbortSignal\.timeout\(750\)/);
  assert.match(route, /isCrossSiteRequest/);
  assert.match(runtime, /AudioWorkletNode/);
  assert.match(runtime, /shared-ring/);
  assert.match(runtime, /message-port/);
  assert.match(runtime, /maxUtteranceMs \?\? 30_000/);
  assert.match(ring, /SharedArrayBuffer/);
  assert.match(worklet, /camelot-voice-capture/);
  assert.match(omniVoice, /req\.url === "\/ingest_pcm"/);
  assert.match(omniVoice, /isLoopback\(remoteAddr\)/);
  assert.match(omniVoice, /MAX_HTTP_SESSIONS = 16/);
  assert.match(omniVoice, /server\.listen\(PORT, "127\.0\.0\.1"/);
  assert.match(omniVoice, /AUDIO_RETENTION_MS = 5 \* 60_000/);
  assert.match(omniVoice, /purgeExpiredAudio\(audioDir, now\)/);
  assert.match(worker, /audio_path\.relative_to\(audio_root\)/);
  assert.match(worker, /audio_path\.unlink\(missing_ok=True\)/);
  assert.match(config, /Cross-Origin-Embedder-Policy/);
  assert.match(config, /require-corp/);
  assert.match(cartridge, /useVoiceFirstRuntime\(status\)/);
  assert.match(cartridge, /Start capture/);
  assert.match(cartridge, /voice\.interrupt\(\)/);
  for (const file of [hook, route, runtime, ring]) {
    assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
  }
});

test("Anya recommends an explainable qualified council and keeps convening governed", async () => {
  const recommendations = await source("src/lib/knight-recommendations.ts");
  const intelligence = await source("src/cartridges/intelligence/intelligence-cartridge.tsx");

  for (const knight of ["lady-mnemosyne", "sir-link", "sir-helio", "sir-debug", "sir-sentinel", "sir-alex", "sir-forge", "sir-codex", "sir-boris"]) {
    assert.match(recommendations, new RegExp(`id: "${knight}"`));
  }
  assert.match(recommendations, /memory >= 85/);
  assert.match(recommendations, /status\.capabilities\.cloudbrain !== "live"/);
  assert.match(recommendations, /status\.stale/);
  assert.match(recommendations, /sort\(\(left, right\) => right\.score - left\.score/);
  assert.match(recommendations, /\.slice\(0, 5\)/);
  assert.match(recommendations, /return `\/\/PLAN Anya council/);
  assert.match(recommendations, /\.slice\(0, 1200\)/);
  assert.match(intelligence, /Recommended council/);
  assert.match(intelligence, /knight\.reason/);
  assert.match(intelligence, /knight\.recommendation/);
  assert.match(intelligence, /onCommand\(councilPlan\(recommendations\)\)/);
});

test("cartridge mounting never hides operational content", async () => {
  const styles = await source("src/app/globals.css");
  assert.doesNotMatch(styles, /@keyframes mount \{ from \{ opacity:/);
  assert.match(styles, /\.command-composer \{ order: 5; \}/);
  assert.match(styles, /position: static;/);
});

test("durable control-plane evidence has backup and corruption recovery", async () => {
  const controlPlane = await source("src/lib/control-plane.ts");
  assert.match(controlPlane, /randomUUID/);
  assert.match(controlPlane, /BACKUP_PATH/);
  assert.match(controlPlane, /\.corrupt-/);
  assert.match(controlPlane, /fsyncSync/);
  assert.match(controlPlane, /BACKUP_PATH, STORE_PATH/);
  assert.match(controlPlane, /copyFileSync\([^\n]+STORE_PATH, BACKUP_PATH\)/);
});

test("SSE rollover reconnects without leaking its interval", async () => {
  const stream = await source("src/app/api/stream/route.ts");
  const shell = await source("src/components/cockpit-shell.tsx");
  assert.match(stream, /retry: 3000/);
  assert.match(stream, /closeTimer = setTimeout\(close, 55000\)/);
  assert.match(stream, /if \(interval\) clearInterval\(interval\)/);
  assert.match(shell, /reconnectTimer = window\.setTimeout\(connect, delay\)/);
  assert.match(shell, /stream\?\.close\(\)/);
});

test("offline storage excludes commands, events, and approvals", async () => {
  const offline = await source("src/lib/offline-store.ts");
  const shell = await source("src/components/cockpit-shell.tsx");
  assert.doesNotMatch(offline, /CockpitEvent|Approval\[\]/);
  assert.match(offline, /lastCommand: \{\}/);
  assert.match(shell, /Commands, events, and approvals are never retained offline/);
  assert.match(shell, /setApprovals\(\[\]\)/);
});

test("PWA prewarming waits for every trusted cartridge cache acknowledgement", async () => {
  const runtime = await source("src/components/pwa-runtime.tsx");
  assert.match(runtime, /preloadTrustedCartridges/);
  assert.match(runtime, /new MessageChannel\(\)/);
  assert.match(runtime, /CACHE_RESOURCES_COMPLETE/);
  assert.match(runtime, /dataset\.pwaPrewarmed = "true"/);
});

test("V2 cartridge platform preserves the V1 trusted loader and stays browser-only", async () => {
  const platform = await source("src/lib/v2/cartridge-platform.ts");
  const zip = await source("src/lib/v2/cartridge-zip.ts");
  const registry = await source("src/cartridges/registry.tsx");
  const manifests = await source("src/cartridges/manifests.ts");

  // V2 namespace is reachable.
  assert.match(platform, /export async function hydrateV2Cartridge/);
  assert.match(platform, /export async function verifyV2Archive/);
  assert.match(platform, /export const V1_LEGACY_SHA256 = "v1-legacy-import"/);
  assert.match(zip, /export function readZip/);
  assert.match(zip, /export async function sha256Hex/);

  // V2 bridges to V1 via manifestFor, never mutates the V1 trusted loader.
  assert.match(platform, /import \{ manifestFor \} from "@\/cartridges\/registry"/);
  assert.match(platform, /manifestFor\(manifest\.cartridge_id/);
  assert.doesNotMatch(platform, /trustedLoaders\[/);
  assert.doesNotMatch(platform, /trustedCatalog\[/);

  // V1 trusted loader is unchanged: same 7 cartridges, same CartridgeBoundary,
  // same preloadTrustedCartridges, no URL imports.
  for (const cartridge of ["command", "factory", "forge-law", "intelligence", "interphase", "device-hall", "mesh"]) {
    assert.match(registry, new RegExp(`${cartridge.includes("-") ? `"${cartridge}"` : cartridge}: dynamic`));
  }
  assert.match(registry, /class CartridgeBoundary/);
  assert.match(registry, /preloadTrustedCartridges/);
  assert.doesNotMatch(registry, /https?:\/\//);

  // V1 manifests still declare all 7 cartridges.
  for (const cartridge of ["command", "factory", "forge-law", "intelligence", "interphase", "device-hall", "mesh"]) {
    assert.match(manifests, new RegExp(`id: "${cartridge}"`));
  }

  // V2 is browser-only: no shell exec, no Node fs, no process.cwd.
  for (const file of [platform, zip]) {
    assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
    assert.doesNotMatch(file, /fs\.readFileSync|fs\.writeFileSync/);
    assert.doesNotMatch(file, /require\(|process\.cwd/);
  }

  // V2 never imports remote URLs (no fetch(http), no dynamic URL import).
  for (const file of [platform, zip]) {
    assert.doesNotMatch(file, /import\(["']https?:/);
    assert.doesNotMatch(file, /fetch\(["']https?:/);
  }

  // V1 bridge constant matches the Python V1_LEGACY_SHA256 magic.
  assert.match(platform, /V1_LEGACY_SHA256 = "v1-legacy-import"/);
});
