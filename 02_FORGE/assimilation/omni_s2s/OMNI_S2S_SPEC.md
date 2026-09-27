# OMNI SPEECH-TO-SPEECH (S2S) SPECIFICATION
## v10001.00-CYBERTRONIA — SGLang-Omni & Agora RTC Assimilation
@ctx|camelot-os.dev/ukg/v10001/omni_s2s @typ|Sovereign_Assimilation_Spec id|Ω_OMNI_S2S_NEXUS

---

## 1. Executive Summary & Prime Directive

This specification integrates **Mini-SGLang**, **SGLang-Omni**, **AgoraAI_ChatBotApp**, and **AgoraAi** into Camelot-OS's **Multivoice Router** and **Bifrost Bridge** to solve the two remaining hard problems in conversational Speech-to-Speech (S2S):
1. **Multi-Turn Context Latency Degradation (The KV Cache Bloat)**: Solved via SGLang RadixAttention prefix caching for continuous audio tokens.
2. **Mobile & Cellular Edge Packet Stability**: Solved via Agora Software-Defined Real-time Network (SD-RTN) dual-transport bridging.

The goal is to achieve an end-to-end **Time-To-First-Audio (TTFA) of <160ms** regardless of conversation turn depth.

---

## 2. The 4-Repository Assimilation Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │               CLIENT AUDIO INGRESS                      │
                    │   - Agora RTC (SD-RTN Carrier Network)                  │
                    │   - LiveKit (Local LAN / WebRTC)                        │
                    │   - Excalibur S26 Ultra (QtScrcpy / ADB)                │
                    └───────────────────────────┬─────────────────────────────┘
                                                │  Raw PCM16 Audio Stream
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │                 AgoraRTCBridge                          │
                    │   - Jitter Buffering & Packet Loss Concealment (PLC)    │
                    │   - Acoustic Echo Cancellation (AEC)                    │
                    │   - Zero-Copy Pipe to Win32 / POSIX Named Shared Memory │
                    └───────────────────────────┬─────────────────────────────┘
                                                │
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │                 RadixAudioCache                         │
                    │         (mini-sglang & sglang-omni)                     │
                    │   - Radix Tree indexing of multi-turn speech tokens     │
                    │   - O(1) KV cache hit across turns (Turn 5 TTFT < 45ms) │
                    │   - Chunked prefill (100ms chunks) & overlapped decode  │
                    └───────────────────────────┬─────────────────────────────┘
                                                │
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │              OmniS2SEngine Dispatch                     │
                    │   - Humanistic Vocal Prosody Guidance                   │
                    │   - Channeled Knight Selection (Reya / Boris / Codex)   │
                    │   - VibeVoice 0.5B / Kokoro ONNX Streaming Diffusion   │
                    └───────────────────────────┬─────────────────────────────┘
                                                │  Outbound PCM Chunks
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │               CLIENT AUDIO EGRESS                       │
                    │   - First audio packet emitted in < 150ms               │
                    │   - Sub-30ms instant barge-in cancellation              │
                    └─────────────────────────────────────────────────────────┘
```

---

## 3. Key Enhancements

### A. RadixAttention for Audio Latent Tokens
- In conversational S2S, 1 second of user speech corresponds to 25–50 audio tokens. By turn 4, there are 400+ historical audio tokens in context.
- Without prefix caching, recomputing the attention matrix on every turn creates a 300ms–500ms delay.
- The **`RadixAudioCache`** indexes common system prefixes and previous turns in a Radix Tree. When the user speaks turn 5, the prefix matcher finds the shared prefix node in the tree and **reuses the cached Key/Value vectors**, executing prefill only on the newest delta tokens.

### B. Chunked Prefill & Overlapped Decode
- Rather than waiting for the entire 2-second user sentence to finish arriving and encoding:
  1. Incoming audio is chunked into 100ms frames.
  2. Tokens are appended to the active Radix branch.
  3. Generation of response tokens initiates speculatively as soon as the final pause is predicted.

### C. Agora SD-RTN Carrier-Grade Edge Transport
- Adds carrier-grade telecommunications transport to our existing LiveKit WebRTC system:
  - Dynamic route optimization bypassing congested internet peering points.
  - Up to 70% packet loss concealment without audio robotic distortion.
  - Direct integration into our shared memory ring buffers (`/dev/shm` / Win32 named memory).
