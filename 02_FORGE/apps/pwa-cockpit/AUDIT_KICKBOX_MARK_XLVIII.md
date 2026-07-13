# PWA Cockpit Cross-Architecture Audit

Validated against current source on 2026-07-12.

## Sources

- Camelot PWA Cockpit: `CAMELOT_OS/02_FORGE/apps/pwa-cockpit`
- Kickbox-audio local checkout: `C:/Users/vizio/Kickbox-audio` at `67848a4bd80ab60f3e0c3e8d31c3b95d9b846511` on `feat/knight-console`
- Kickbox-audio upstream: `https://github.com/Cyberdad247/Kickbox-audio`
- FatihMakes-Mark-XLVIII audit clone: `d178f6b9ee43e4e3d7edcc78b7df3e10f372fec2`
- Mark XLVIII upstream: `https://github.com/Cyberdad247/FatihMakes-Mark-XLVIII`

The Kickbox checkout contains unrelated local modifications and was treated as read-only. Mark XLVIII has no visible license file in the audited fork, so no source code was copied. Only general interaction and resilience patterns were independently implemented.

## Executive Verdict

The Cockpit is stronger than either source as a sovereign mobile control plane: it has passkeys, signed sessions, one-time approval grants, durable receipts, strict API cache exclusion, cartridge isolation, and a verified private HTTPS route. Kickbox remains stronger in its layered voice fallback architecture and explicit Bifrost dispatch model. Mark XLVIII remains stronger in real-time interrupt handling, transient-session reset, local screen/camera context, reconnect behavior, and proactive assistant behaviors.

This pass closes the highest-value browser-safe gaps without importing vendor-bound Gemini sessions, unrestricted desktop actions, committed private keys, or unlicensed code.

## Integration Matrix

| Capability | Kickbox-audio | Mark XLVIII | Cockpit decision |
| --- | --- | --- | --- |
| Responsive avatar runtime | Device class, save-data, reduced-motion, CPU heuristics | Desktop HUD modes | Adopted as `interphase-runtime.ts` and applied to Anya |
| Voice interruption | Browser speech cancellation and isolated hook state | 50 ms audio slices and explicit queue drain | Adopted at browser boundary through immediate speech cancellation and Live Interphase interrupt |
| Voice fallback | Web Speech, local ASR worker, VAD fallback, local TTS worker | Gemini Live PCM stream | Partial: Web Speech plus text and local browser TTS remain; local ASR worker is still missing |
| Bridge failure visibility | Explicit Bifrost disconnect state and governed plan cards | Reconnect status in UI | Adopted: transport state, retry count, and next retry are visible |
| Reconnect strategy | Fixed retry in current checkout | 3s, 6s, 12s, 60s backoff | Adopted for Cockpit SSE transport |
| Session isolation | Hook-local awaiting gates | Vision/interrupt flags reset on reconnect | Adopted through explicit transient-state reset |
| Visual context | Avatar/video continuity | Screen and camera capture with cooldown | Adopted as operator-mediated local screen capture with 4-second echo guard |
| Visual data custody | Mixed PWA/runtime paths | Sent to Gemini Live | Strengthened: preview is volatile and never uploaded automatically |
| Human approval | Bifrost plan cards and named publish approval | Broad direct tool dispatch | Cockpit Iron Gate retained; Mark direct actions rejected |
| Authentication | App-specific deployment auth | Password/dashboard certificate | Cockpit passkeys and signed sessions retained |
| Provider race | Not central | First valid search result wins | Deferred until two sovereign providers exist |
| Proactive check-ins | Briefing surfaces | Silence-triggered Gemini decision | Rejected by default; requires explicit opt-in, local policy, and quiet hours |

## Changes Implemented

1. Added the trusted `Live Interphase` cartridge to the explicit dynamic catalog.
2. Added real browser capability telemetry for voice input, voice output, local screen capture, network state, and SSE transport.
3. Added operator-mediated local screen capture. Tracks stop immediately after one frame; no fetch, persistent storage, command dispatch, or automatic upload exists in the cartridge.
4. Added a four-second visual capture cooldown and busy guard to prevent duplicate/echo capture loops.
5. Added explicit `Interrupt output` and `Reset transient state` controls.
6. Replaced opaque EventSource reconnection with visible 3s, 6s, 12s, then 60s capped backoff.
7. Added Kickbox-derived runtime profiling for mobile/tablet/desktop, save-data, reduced-motion, CPU, and dense mobile displays.
8. Expanded mobile navigation from four to five stable cartridge tracks.
9. Fixed a first-use cooldown defect found by browser verification: a capture attempted during the first four seconds after page load was incorrectly treated as a duplicate because the initial timestamp was zero.

## Security Rejections

- Do not import Mark XLVIII's `config/certs/jarvis.key` or self-signed certificate model.
- Do not store Gemini or other provider keys in client-visible JSON.
- Do not expose unrestricted file, process, power, keyboard, mouse, browser, or messaging actions through a PWA route.
- Do not automatically upload screen context or retain screenshots in IndexedDB, localStorage, the service-worker cache, or Camelot runtime state.
- Do not bypass Iron Gate for voice-originated commands.
- Do not copy Mark XLVIII implementation code without a confirmed compatible license.

## Remaining Gaps

### P0 before enabling broad live actions

- Add per-capability scopes to passkey sessions so screen context, voice, approvals, and future desktop tools can be independently authorized.
- Bind any future visual-analysis handoff to an explicit approval receipt and content hash.
- Keep `CAMELOT_COCKPIT_EXEC_ENABLED=false` until every newly exposed action has an exact allowlist and negative tests.

### P1 product completeness

- Add a local ASR worker or native local speech bridge. Browser SpeechRecognition may use a vendor service and is not a guaranteed offline path.
- Add VAD and measured time-to-first-audio telemetry rather than capability-only labels.
- Add a local audio relay contract for ESP32-S3/phone PCM with arbitration so only one microphone is active.
- Add opt-in proactive briefings with quiet hours, local-only policy evaluation, and a visible disable control.
- Add a provider-race abstraction only when two approved local or zero-cost research providers are available.

### P2 cartridge scale

- Current cartridges are trusted lazy-loaded modules compiled into one Next.js deployment. They have capability manifests and error boundaries, but they are not independently deployed micro-frontends.
- True independent deployment requires signed cartridge bundles, versioned host contracts, CSP-integrity enforcement, compatibility negotiation, and rollback evidence. Remote arbitrary code loading should remain prohibited.

## Verification Contract

Release requires:

- architecture tests proving API/cache/security boundaries;
- strict TypeScript and production build;
- authenticated desktop and mobile browser checks;
- local capture denial/success/track-stop tests;
- SSE rollover/backoff verification;
- offline cartridge prewarming;
- Bio-Kinetic release receipt;
- no secret values or captured images in generated artifacts.

Current evidence satisfies this contract: 16 architecture tests, strict TypeScript, production build, desktop/mobile browser checks, capture denial, synthetic capture success with confirmed track stop, zero-storage verification, offline fifth-cartridge mount, and a fresh Bio-Kinetic Formica receipt all pass.
