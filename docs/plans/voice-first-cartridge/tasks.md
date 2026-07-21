# Voice-First Cartridge Tasks

## Phase 0 - Pre-flight

- [x] Verify `docs/protocols/pre-flight.md` exists and remains canonical.
- [ ] Require at least 800 MB free RAM and no more than 7.2 GB committed use.
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

- [ ] Test lease contention, overflow, discontinuity, VAD, and teardown.
- [ ] Test API authentication, origin, payload size, content type, and host policy.
- [ ] Test OmniVoice binary frame validation and bounded peer state.
- [ ] Run PWA architecture tests, strict TypeScript, production build, and browser checks.
- [ ] Run OmniVoice TypeScript checks and focused Camelot voice tests.
- [ ] Crystallize only after every source hash and verification result matches.
