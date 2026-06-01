# NORTHSTAR_ARCHITECTURE_BRIEF.md

**Date:** 2026-05-13
**Cartridge Leads:** Lady Apis (Research), Sir Syntax (Engineering), Sir Gareth (Integration)
**Tier:** APEX (Architectural Strategy & Capability Audit)
**Target:** `CAMELOT_OS Empire`

## 📊 EXECUTIVE SUMMARY
The Joint Task Force has completed the APEX-tier audit of the CAMELOT_OS Empire against the North Star Goal: an omnipresent, edge-based "Virtual Mobile Castle" commanded by Anya and the Knight Roster. The current architecture (OmniVox, Edge Router, Bifrost) is structurally sound for discrete, asynchronous operations but critically lacks the persistent, full-duplex streaming capabilities required for a zero-latency, Jarvis-tier voice companion.

---

## 🎙️ TRACK 1: THE ACOUSTIC INTERFACE (Lady Apis)
**Analysis of `omnivoice-router.ts`, `kitten_service.py`, `multivoice-session.ts`**

The current acoustic pipeline is built on a request-response paradigm. `kitten_service.py` is designed to synthesize complete text hashes, and `multivoice-session.ts` pre-orchestrates static turn-taking (e.g., `planCouncilSession`, `planPodcastSession`).

**Path to North Star:**
- **Full-Duplex Streaming:** We must replace discrete TTS generation with chunked, token-by-token audio streaming over WebRTC. 
- **Interruptibility:** Implement a Voice Activity Detection (VAD) layer that can instantly abort the LLM generation and clear the TTS buffer when the user interrupts the agent.
- **Dynamic Spawning:** Move away from statically planned `MultivoiceSession` arrays. Anya needs a routing layer that can dynamically hot-swap Knights into the active audio stream based on semantic intent mid-conversation.

---

## ⚡ TRACK 2: KINETIC ACTUATION & CONTROL (Sir Syntax)
**Analysis of `edge-router.ts` (PhoneClaw, Chrome, Termux, RustDesk)**

The `dispatchToEdge` function relies on HTTP POST requests (`await fetch`) with a 2500ms timeout (implemented in the recent refactor). While resilient for discrete commands, this is incompatible with real-time UI manipulation.

**Path to North Star:**
- **Persistent Bi-Directional Streams:** To achieve zero-latency screen reading and absolute phone control, the Edge Router must be upgraded to support WebSockets or gRPC streams. HTTP polling is too slow and battery-intensive for mobile actuation.
- **Stateful Edge Nodes:** PhoneClaw and Superpowers Chrome need to maintain a persistent connection state to receive rapid-fire DOM/UI coordinate instructions without TLS handshake overhead on every command.

---

## 🛡️ TRACK 3: THE BIFROST COMMAND CENTER (Sir Gareth)
**Analysis of `bifrost.rs`, `integration_brain.py`, Modal Endpoints**

`bifrost.rs` enforces a strict 3-layer security gate, dropping all traffic that does not originate from `127.0.0.0/8` or the Tailnet CGNAT `100.64.0.0/10` with a valid `x-bifrost-token` and trusted `tailscale whois` owner.

**Path to North Star:**
- **Ubiquitous Connectivity:** A mobile companion on cellular networks faces challenges with IP roaming and battery drain from always-on VPNs. If the phone drops off the Tailnet, Bifrost immediately returns a 403 Forbidden. We must either enforce a highly resilient mobile Tailscale integration or establish an mTLS/OIDC authenticated public gateway for roaming edge nodes.
- **Serialization Compression:** Transmitting the massive Modal A100 (`integration_brain.py`) context or Knight Roster state across a 5G connection requires extreme compression. The `TOON_v2` formatting must be extended into a delta-sync protocol over the Bifrost bridge to avoid payload bloat.

---

## 🚫 TOP 5 ENGINEERING BLOCKERS

1. **Synchronous HTTP Edge Routing:** The reliance on stateless HTTP `fetch` in `edge-router.ts` prevents the real-time, low-latency actuation required for continuous phone and browser control.
2. **Discrete Audio Synthesis (No Streaming):** `kitten_service.py` synthesizes full text blocks rather than streaming audio chunks as tokens are generated, preventing sub-100ms conversational latency.
3. **Lack of Interruption Handling (No VAD):** The system cannot handle user interruptions mid-speech. A WebRTC + Voice Activity Detection layer is completely absent.
4. **Tailscale-Exclusive Gate (`bifrost.rs`):** The strict requirement for the `100.64.0.0/10` subnet restricts mobile autonomy if the device drops the VPN connection, limiting true omnipresence.
5. **Static Session Pre-computation:** `multivoice-session.ts` pre-plans agent turns. Anya cannot currently orchestrate Knights dynamically in real-time based on live audio sentiment.

---

## ⚔️ ACTUATION PROTOCOL

To initiate the first phase of this architectural evolution, we must address the most critical infrastructure blockers: Persistent Connectivity and Chunked Audio Streaming.

Execute the following command to deploy the Engineering Cartridge:

```bash
oh-my-product team run --task "NORTHSTAR PHASE 1: 1. Upgrade edge-router.ts to support persistent WebSockets for PhoneClaw/Chrome actuation. 2. Refactor kitten_service.py to stream audio chunks (Token-to-Audio) instead of full-text synthesis. 3. Architect a WebRTC layer for omnivoice-router.ts to support full-duplex communication."
```