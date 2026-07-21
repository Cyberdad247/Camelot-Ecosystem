# PLAN: Northstar Phase 2
## Bifrost Roaming, Dynamic Swarm Routing, & Delta-Sync Payload Compression

**Target:** Expand the Camelot-OS voice companion into a truly omnipresent, cellular-resilient assistant that dynamically coordinates multiple Knights mid-conversation and traverses Tailscale boundaries securely.

---

## 🗺️ Execution Milestones

### 📍 Milestone 1: Bifrost Public Gateway & mTLS Roaming
Upgrade the Bifrost bridge to support cellular mobile devices that drop Tailscale connection.
* **Target File:** [control_plane/bifrost.py](file:///C:/Users/vizio/CAMELOT_OS/control_plane/bifrost.py)
* **Tasks:**
  1. Add optional client certificate validation (mTLS) to the FastAPI server.
  2. Implement an OIDC / OAuth authentication header check path as an alternative to tailscale whois mapping.
  3. Update subnet checking logic: if incoming connection has a valid client certificate or token, bypass the strict local loopback/tailnet IP check.

### 📍 Milestone 2: Dynamic Knight Swapping & Intent Switchboard
Enable real-time context and agent swapping during active full-duplex conversations.
* **Target Files:** 
  - [02_FORGE/KINETIC_ARMORY/omnivoice-router/omnivoice-router.ts](file:///C:/Users/vizio/CAMELOT_OS/02_FORGE/KINETIC_ARMORY/omnivoice-router/omnivoice-router.ts)
  - [01_KERNEL/senses/audio/audio_session.py](file:///C:/Users/vizio/CAMELOT_OS/01_KERNEL/senses/audio/audio_session.py)
* **Tasks:**
  1. Update WebSocket message protocol in the omnivoice-router to accept a `knight_id` hint.
  2. Implement intent parsing during speech analysis in the audio session: if a user addresses a specific Knight (e.g. *"Sentinel, check the port"*), parse the keyword and update the active completion target Knight.
  3. Hot-swap the voice configuration (pitch, gender, speed) in the Kokoro synthesis stream on the fly.

### 📍 Milestone 3: Delta-Sync Payload Compression
Implement bandwidth-efficient state diffs over the cellular WebSocket connections.
* **Target Files:**
  - [02_FORGE/KINETIC_ARMORY/edge-router/edge-router.ts](file:///C:/Users/vizio/CAMELOT_OS/02_FORGE/KINETIC_ARMORY/edge-router/edge-router.ts)
  - [control_plane/worker.py](file:///C:/Users/vizio/CAMELOT_OS/control_plane/worker.py)
* **Tasks:**
  1. Design a state-differential JSON serialization schema (`TOON_v2_diff`) that only transmits changed fields.
  2. Integrate gzip / deflate compression on the WebSocket frame payloads to minimize network footprint.

### 📍 Milestone 4: Verification & Integration Testing
* **Target Script:** [scripts/start_northstar.py](file:///C:/Users/vizio/CAMELOT_OS/scripts/start_northstar.py)
* **Tasks:**
  1. Write E2E mock tests simulating roaming clients connecting via public gateways.
  2. Test active voice turn sequences where the Knight role swaps mid-dialogue.
  3. Validate compression ratio and payload sizes.

---

## 🏁 Completion & Success Criteria
1. **Network Resilience:** Zero connection drops when switching from Tailscale to public cellular roaming gateways.
2. **Context Latency:** Active speaker/Knight swap latency must complete under 100ms.
3. **Bandwidth Optimization:** Payload serialization footprint reduced by >= 60% using delta compression.
