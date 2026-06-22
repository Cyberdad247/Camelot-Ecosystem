# TODO: Northstar Phase 1 Work Breakdown

Decomposed from `PLAN.md` into actionable tasks.

- [x] **Milestone 1: WebSocket Edge Routing Upgrade** `[backend] [parallel]`
  - [x] Setup WebSocket server instance in `edge-router.ts` on port `3001`
  - [x] Define client registration handler to track `PhoneClaw` and `Superpowers Chrome` sessions
  - [x] Implement standard ping/pong heartbeats to purge stale node connections
  - [x] Modify `dispatchToEdge` to check active WebSocket pools and send frames over WS instead of HTTP fetch
  - [x] Build fallback router to execute standard HTTP POST requests if no WebSocket connection is active
- [x] **Milestone 2: Token-to-Audio Chunked TTS Refactor** `[backend] [parallel]`
  - [x] Refactor Kokoro synthesis functions in `kitten_service.py` to yield audio chunks (generators)
  - [x] Setup streaming endpoint on port `8300` to stream audio buffers incrementally
  - [x] Implement message priority queues so new voice inputs purge existing audio tracks instantly
- [x] **Milestone 3: WebRTC Full-Duplex Signaling** `[backend]`
  - [x] Setup signaling endpoints in `omnivoice-router.ts` on port `3002` to exchange SDP Offers/Answers and ICE candidates
  - [x] Configure client `RTCPeerConnection` listeners for incoming microphone track streams
  - [x] Route synthesized TTS chunks to the outgoing WebRTC track
- [x] **Milestone 4: Voice Activity Detection (VAD) & Interruption Handling** `[backend]`
  - [x] Implement RMS amplitude voice trigger (e.g. threshold > 0.01) over 200ms incoming PCM audio track
  - [x] Setup interruption event dispatcher:
    - [x] Flush current outgoing audio streams in `kitten_service.py`
    - [x] Cancel current LLM completion run on the control plane
    - [x] Send socket clear-signal to clients to immediately halt local audio playback
- [x] **Milestone 5: Verification & End-to-End Testing** `[test]`
  - [x] Create system test suite in `scripts/start_northstar.py` to launch full pipeline
  - [x] Verify WebSocket connection handshake completing under 200ms
  - [x] Verify VAD interruption halts playback under 150ms
