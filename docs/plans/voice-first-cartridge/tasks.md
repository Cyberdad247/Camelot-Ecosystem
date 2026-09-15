# Voice-First Cartridge Tasks

## Phase 0 - Pre-flight

- [x] Verify `docs/protocols/pre-flight.md` exists and remains canonical.
- [x] Require at least 800 MB free RAM and no more than 7.2 GB committed use.
  - Enforced fail-closed in `scripts/verify_vfc_preflight.py` (`MIN_FREE_MB = 800.0`, `MAX_USED_MB = 7.2 * 1024`).
  - Verified 2026-09-14: `free_mb: 1081.6`, `used_mb: 6814.3` -> `resource_ok: true`.
- [x] Verify the Bio-Swarm, PWA, OmniVoice, and Forge Law source surfaces.

## Phase 1 - Shared Runtime

- [x] Define typed voice frames, states, transport modes, and runtime events.
- [x] Implement exclusive microphone leases with explicit conflict reporting.
- [x] Implement a bounded SharedArrayBuffer PCM ring and discontinuity counter.
- [x] Implement AudioWorklet capture with 16 kHz mono downsampling.
- [x] Implement transferable MessagePort fallback and local energy VAD.
- [x] Dispose media tracks, graph nodes, worklet ports, timers, and contexts.

## Phase 2 - Governed Integration

- [x] Add an authenticated, no-store, same-origin PCM frame API.
- [x] Permit the server adapter to target loopback OmniVoice only.
- [x] Add loopback-only `/ingest_pcm` support to the existing OmniVoice server.
- [x] Mount VFC controls in Live Interphase and share the microphone lease with Anya.
- [x] Preserve existing Multivoice, browser TTS, barge-in, and text fallback behavior.

## Phase 3 - Crucible

**Host re-homed 2026-09-14.** The original host `02_FORGE/apps/pwa-cockpit` was
purged in `944e4532` ("purge redundant PWAs"), which made this entire phase
unrunnable. Phase 1/2 surfaces were re-homed onto `apps/pwa` (the live voice
PWA); `02_FORGE/packages/voice-first-runtime` was already intact and remains the
single source of the runtime and the AudioWorklet asset.

- [x] Test lease contention, overflow, discontinuity, VAD, and teardown.
  - `apps/pwa/src/lib/voice/runtime.test.ts` — 16 tests, all passing.
- [x] Test API authentication, origin, payload size, content type, and host policy.
  - `apps/pwa/src/lib/voice/frames-route.test.ts` — 26 tests, all passing.
- [x] Test OmniVoice binary frame validation and bounded peer state.
  - `apps/pwa/src/lib/voice/omnivoice-ingest.test.ts` — 15 tests against a
    spawned router. The 403 `loopback_only` branch is not asserted: a client on
    this host always presents 127.0.0.1, so it needs a non-loopback bind.
- [x] Run OmniVoice TypeScript checks and focused Camelot voice tests.
  - `npx tsc --noEmit` in `02_FORGE/KINETIC_ARMORY/omnivoice-router` — clean.
  - `npx tsc --noEmit` in `02_FORGE/packages/voice-first-runtime` — clean.
  - `npm test` in `apps/pwa` — 74 tests passing across 8 files.
- [ ] Run PWA architecture tests, strict TypeScript, production build, and browser checks.
  - PWA tests: `npm test` — 74 passing.
  - Strict TypeScript: `npm run typecheck` (`tsc --noEmit`) — clean.
  - Production build: **BLOCKED, and not by VFC.** `next build` compiles
    successfully, passes "Linting and checking validity of types", and generates
    all 10/10 static pages, then fails exporting Next's built-in `_error` pages:
    `/_error: /404` and `/_error: /500` abort with
    `TypeError: Cannot read properties of null (reading 'useContext')`.
    Cause is a pre-existing workspace React split, not this cartridge:
    `apps/camelot-vps-hub` (react ^19.0.1) and `packages/multivoice-router`
    (react ^19.0.0) hoist `node_modules/react@19.2.8` to the workspace root,
    while `apps/pwa` resolves `react@18.3.1` locally. `styled-jsx` exists only at
    the root, so its `react` peer walks up to 19.2.8 against react-dom 18.3.1.
    Verified independent of this work: the build fails identically before and
    after the re-home, and the failing pages contain no VFC code. Fix belongs in
    dependency alignment (pin root React to 18 or bump apps/pwa), not in
    `next.config.js`.
  - Browser checks: not run — no browser harness was exercised in this pass.
- [ ] Crystallize only after every source hash and verification result matches.
  - **Held.** The production-build gate is red for the pre-existing reason above,
    so no Forge Law cartridge is emitted. Crystallizing now would certify a
    verification result that did not pass.
