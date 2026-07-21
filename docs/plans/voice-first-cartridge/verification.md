# Voice-First Cartridge Verification

## Resource Gate

- Start fails closed below 800 MB free RAM.
- Start fails closed when committed use exceeds 7.2 GB.
- No verification command launches a model or native build while the gate is red.

## Capture Contract

- Frames are ordered 16 kHz mono Int16 payloads of at most 3,200 bytes.
- SharedArrayBuffer and MessagePort transports produce equivalent frame metadata.
- Ring overflow increments the dropped counter and marks the next frame discontinuous.
- Two consumers cannot hold the microphone simultaneously.
- Permission denial and unsupported AudioWorklet produce a visible unavailable state.
- Stop and interrupt release every track, node, port, timer, buffer, and AudioContext.

## Network and Security

- `/api/voice/frames` requires an authenticated operator session.
- Cross-site requests and non-octet-stream payloads are rejected.
- Payloads over the frame limit are rejected before forwarding.
- OmniVoice forwarding accepts only loopback HTTP endpoints.
- OmniVoice `/ingest_pcm` accepts only loopback callers and valid Int16 frames.
- No raw PCM, transcript secret, token, or screenshot enters offline storage or Cloud Brain.
- Voice-derived commands continue through the existing Iron Gate approval route.

## Commands

```powershell
cd C:\Users\vizio\CAMELOT_OS
.\.venv\Scripts\python.exe scripts\verify_vfc_preflight.py

cd 02_FORGE\apps\pwa-cockpit
npm test
npm run typecheck
npm run build

cd ..\..\KINETIC_ARMORY\omnivoice-router
npx tsc --noEmit
```

The build and native checks run only after the resource gate reports `GO`.
