# Voice-First Cartridge Architecture

**Version:** v10000.15  
**Authority:** `docs/protocols/pre-flight.md`  
**Primary host:** Windows x64 with portable browser contracts for ARM64 edge clients

## Objective

Add a local-first voice capture substrate to the existing PWA Cockpit without
duplicating OmniVoice, Sir Sonus, Vox, Multivoice, Anya, or Iron Gate. The
runtime captures bounded PCM frames, arbitrates the microphone across Cockpit
surfaces, detects speech locally, and hands frames to the existing OmniVoice
router through an authenticated same-origin adapter.

## Runtime Topology

```text
Anya shell / Live Interphase
  -> exclusive microphone lease
  -> AudioWorklet capture at device sample rate
  -> 16 kHz mono Int16 frames
  -> SharedArrayBuffer ring when cross-origin isolated
     or transferable MessagePort frames otherwise
  -> local energy VAD and bounded utterance state
  -> authenticated /api/voice/frames
  -> loopback-only OmniVoice /ingest_pcm
  -> existing vad_utterance -> Sir Sonus -> governed intent path

Response
  -> Vox / Tiny-TTS / Multivoice
  -> browser speech fallback
  -> operator barge-in clears all active playback
```

## Trust Boundaries

- Raw PCM is transient and must not enter IndexedDB, service-worker caches,
  Cloud Brain, source artifacts, or provenance ledgers.
- The browser calls only the same-origin Cockpit API. The server adapter may
  call only a loopback OmniVoice endpoint.
- Speech-derived mutations are command proposals and retain the existing
  capability, Iron Gate, digest, approval, and replay boundaries.
- The microphone has one owner per browser document. Contending consumers get
  an explicit rejection and current-holder label.
- `PROVENANCE_LEDGER.md` is never edited by VFC code; existing hooks own durable
  provenance.

## Resource Contract

- Start is rejected below 800 MB host headroom or above the 7.2 GB committed
  memory threshold reported by Camelot telemetry.
- Frames are 100 ms maximum, 16 kHz mono Int16, and bounded to 3,200 bytes.
- The ring buffer stores at most two seconds of audio and reports dropped
  samples as a discontinuity.
- Utterance accumulation is capped at 30 seconds and is released on stop,
  interrupt, error, route change, or component unmount.
- AudioWorklet, tracks, nodes, ports, timers, and AudioContext are disposed
  deterministically.

## Platform Truth

SharedArrayBuffer is an optimization requiring COOP and COEP. Browsers without
cross-origin isolation use the MessagePort fallback. Firecracker, KVM, `tmpfs`,
`MADV_DONTNEED`, ternary inference, and quantum transforms are outside this
implementation unless a compatible runtime and verification evidence exist.
