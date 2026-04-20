# Controlling the Media Server via Bridge
## Camelot Apex OS v300.4 — Sir Sonus / Lukas Edge / TitanLink

---

## Architecture Overview

The Camelot media stack is a multi-layer bridge chain. User intent flows
through Anya's compiler, routes to the correct knight, and executes
through the bridge layer to reach the actual media hardware.

```
USER DIRECTIVE
     |
     v
ANYA (APEE v6.5 Compiler) ── Intent: CREATIVE / domain: MEDIA
     |
     v
MERLIN (Router) ── Knight: Sir Sonus (L7) or Sir Boris (//vocal)
     |
     v
BRIDGE LAYER (this document)
     |
     +── VoxService (Kokoro TTS) ──── GPU/CPU synthesis
     +── Piper TTS (HuggingFace) ──── ONNX local synthesis
     +── SonusCompiler ──────────── Audio prompt compilation
     +── TitanLink Server ────────── WebSocket → mobile/remote
     +── RustDesk Bridge ─────────── Input injection + screen capture
     +── Anya IPC Bridge (Rust) ──── Named Pipes → kernel
     +── OmniRoute Gateway ───────── Port 20128 → LiveKit WebRTC
     +── Docker: sir_sonus ────────── Container on :5050
```

---

## 1. Voice Synthesis (TTS)

### 1a. Piper TTS (Zero-Cost Local — Recommended)

Piper uses HuggingFace ONNX models. Sub-200ms latency, 8GB RAM safe.

**Module:** `01_KERNEL/agora/swarms/piper_tts.py`

```python
from agora.swarms.piper_tts import synthesize, synthesize_stream, create_podcast

# Single utterance → WAV file
samples, sample_rate = synthesize(
    text="Welcome to Camelot, Sovereign.",
    voice_preset="tasha",          # see VOICE_PRESETS below
    output_path="output/greeting.wav",
)

# Real-time streaming (for live playback)
for audio_bytes, sr in synthesize_stream("Hello darlin'.", voice_preset="tasha"):
    # feed to audio device or WebSocket
    audio_output.write(audio_bytes)

# Multi-speaker podcast generation
script = [
    {"speaker": 1, "text": "Welcome to the round table."},
    {"speaker": 2, "text": "The threat assessment is complete."},
]
create_podcast(
    script,
    output_path="output/podcast.wav",
    voice_map={1: "tasha", 2: "merlin"},
)
```

**Voice Presets:**

| Preset | Model | Character |
|--------|-------|-----------|
| `tasha` | en_GB-jenny_dioco-medium | British female, warm |
| `tasha_british` | en_GB-cori-medium | British female, formal |
| `tasha_scottish` | en_GB-alba-medium | Scottish female |
| `merlin` | en_US-ryan-medium | American male, authoritative |
| `narrator` | en_US-lessac-medium | American male, broadcast |
| `narrator_hq` | en_US-lessac-high | Same, high quality |
| `host_1` | en_US-lessac-medium | Podcast host 1 |
| `host_2` | en_US-joe-medium | Podcast host 2 |

**Model auto-download:** First use of any voice triggers download from
`rhasspy/piper-voices` on HuggingFace. Models stored in:
`~/CAMELOT_OS/docs/EXTERNAL/piper/models/<voice_name>/`

**Manual setup:**
```bash
python -m forge.scripts.setup_piper --voice en_GB-jenny_dioco-medium
```

### 1b. VoxService / Kokoro TTS (GPU-Accelerated)

Higher fidelity, requires Kokoro model weights + CUDA.

**Module:** `01_KERNEL/senses/audio/vox_service.py`

```python
from senses.audio.vox_service import vox_service

# Singleton — auto-detects CUDA vs CPU
result = vox_service.synthesize(
    text="The kingdom stands ready.",
    persona_name="merlin",
    voice_state=voice_state_object,  # .style, .speed, .texture
)
# Returns metadata dict: mode (ORGANIC/SIMULATED), persona, timestamps
```

**Requirements:**
- `kokoro-v0_19.pth` at `workspace/Active_Projects/Kokoro_TTS/`
- Voice tensors (`af_bella.pt`, `am_michael.pt`, `af_sarah.pt`) in `voices/`
- `espeak-ng` installed for phoneme generation
- PyTorch with CUDA (falls back to CPU)

### 1c. Sir Sonus Audio Compiler (Songwriting / Suno / Udio)

Compiles text into executable audio voltage prompts with phonetic hacking.

**Module:** `01_KERNEL/senses/audio/sonus/compiler.py`

```python
from senses.audio.sonus.compiler import SonusCompiler, VocalState

compiler = SonusCompiler()

# Apply phonetic hacking (controls pronunciation)
hacked = compiler.apply_phonetic_hacking("Fire and power forever")
# → "fy-ah and pow-wah fo-reh-vah"

# Get state driver tags for Suno/Udio
tag = compiler.state_drivers[VocalState.BELTING]
# → "[Chorus: Power Belting, High Notes, Anthem]"
```

---

## 2. Bridge Transport Layer

### 2a. TitanLink Server (WebSocket → Mobile / Remote)

WebSocket bridge for real-time event broadcasting and Iron Gate challenges.

**Module:** `01_KERNEL/senses/connectivity/titanlink_server.py`

```python
from senses.connectivity.titanlink_server import TitanLinkServer

server = TitanLinkServer()

# Send Iron Gate biometric challenge to mobile app
challenge = server.send_challenge(action_type="deploy_to_production")
# Returns: {kind, id, action, severity, timestamp}

# Broadcast event to all connected clients
# If event has 'vocal_cue', Sir Sonus queues speech automatically
server.broadcast_event({
    "type": "audit_complete",
    "severity": "HIGH",
    "vocal_cue": "Sovereign, the audit has completed with five critical findings.",
})
```

**Event → Voice Bridge:** Any event payload containing a `vocal_cue` key
auto-triggers Sir Sonus to synthesize and queue the speech. This is how
the system "speaks" audit results, deployment confirmations, and alerts.

### 2b. Anya IPC Bridge (Rust Named Pipes → Kernel)

Low-level Rust bridge for high-performance IPC between RustDesk and the
Camelot kernel. Communicates via Windows Named Pipes.

**Module:** `01_KERNEL/senses/connectivity/anya_ipc_bridge.rs`

**Pipe name:** `\\.\pipe\anya_rustdesk_bridge`

**Message format (JSON over pipe):**
```json
{
  "ver": "1.0",
  "id": "uuid-v4",
  "method": "session_created",
  "params": {
    "peer_id": "123-456-789",
    "access_method": "password"
  }
}
```

**Supported methods (inbound to kernel):**

| Method | Params | Description |
|--------|--------|-------------|
| `session_created` | `{peer_id, access_method}` | New RustDesk session connected |
| `inject_keypress` | `{keys: "string"}` | Inject keyboard input into remote session |
| `terminate_session` | `{}` | Emergency kill of all sessions |

**Sending from kernel → bridge:**
```rust
bridge.send_to_kernel("session_created", serde_json::json!({
    "peer_id": "123-456-789",
    "access_method": "password"
}));
```

### 2c. RustDesk Bridge (Telepresence Input Injection)

Python bridge for remote desktop control — translates Anya's compiled
intent into mouse/keyboard actions on the remote machine.

**Module:** `01_KERNEL/senses/connectivity/rustdesk_bridge.py`

```python
from senses.connectivity.rustdesk_bridge import RustDeskBridge

bridge = RustDeskBridge(host="localhost", port=21115)

# Click at coordinates
bridge.execute_command({"action": "click", "x": 500, "y": 300})

# Type text
bridge.execute_command({"action": "type", "text": "camelot exec 'audit security'"})

# Send hotkey combo
bridge.execute_command({"action": "hotkey", "keys": "ctrl+shift+t"})

# Capture screen frame for AI vision analysis
frame_b64 = bridge.capture_frame()
# Returns base64-encoded image for Sir Visage or vision LLM
```

**Actions:**

| Action | Params | Description |
|--------|--------|-------------|
| `click` | `{x, y}` | Mouse click at pixel coordinates |
| `type` | `{text}` | Type text string |
| `hotkey` | `{keys}` | Send key combination |
| `capture_frame` | — | Screenshot for AI vision |

### 2d. Aether Engine (Saltare MCP Gateway)

Semantic router that maps natural language queries to MCP tools.

**Module:** `01_KERNEL/senses/connectivity/aether.py`

```python
from senses.connectivity.aether import AetherEngine

aether = AetherEngine(
    config_path="01_KERNEL/config/saltare.toml",
    registry_path="01_KERNEL/config/mcp_registry.json",
)

# Route a query to the best MCP tool
result = aether.route_query("send a message on WhatsApp")
# → {target_type: "gateway", id: "gateway::clawdbot", confidence: 0.95}

result = aether.route_query("create a workflow in Notion")
# → {target_type: "gateway", id: "gateway::claraverse", confidence: 0.90}
```

---

## 3. Docker Services (Container Media Stack)

Defined in `docker-compose.yml` at project root.

```bash
# Start the full media stack
docker compose up -d

# Start only voice services
docker compose up -d sonus memory
```

| Service | Container | Port | Function |
|---------|-----------|------|----------|
| `merlin` | merlin_brain | 18000 | L3 Neural reasoning |
| `rotel` | rotel_telemetry | 4317 | OpenTelemetry collector |
| `cribo` | cribo_bundler | — | Code bundler |
| `sonus` | sir_sonus | 5050 | Voice synthesis server |
| `memory` | camelot_memory | 6333 | Qdrant vector store |

**Network:** All services on `camelot_net` internal Docker network.

**Note:** Saltare runs natively as `cli-proxy-api.exe` on `:8080`, not
in a container. Config: `~/CLIProxyAPI/config.yaml`.

---

## 4. OmniRoute Gateway (LiveKit WebRTC)

Real-time audio streaming over WebRTC via LiveKit.

**Config:** `03_VAULT/training/configs/config/omniroute.json`
**Port:** 20128

The OmniRoute gateway bridges the voice pipeline to LiveKit for
real-time browser/mobile audio streaming:

```
Piper/Kokoro TTS → OmniRoute (:20128) → LiveKit WebRTC → Browser/Mobile
```

This is activated by the `//vocal` runic command, which triggers the
3-phase Voice OS bootstrap:

1. **Oracle Phase:** AST-Aware Plan Mode, install dependencies, bridge OmniRoute
2. **Veritas Phase:** 13-Agent Critique, extract persona souls, assign voice IDs
3. **Lazarus Phase:** E2E self-healing, Saltare gateway, mock voice test

---

## 5. CLI Commands

### Via Camelot CLI
```bash
# Trigger the full voice pipeline bootstrap
camelot exec "//vocal"

# Synthesize speech directly
camelot exec "speak 'Welcome to Camelot' as tasha"

# Generate a podcast
camelot exec "create podcast from script.json"

# Audit the voice pipeline
camelot exec "audit voice"
```

### Via Python Direct
```python
# Quick synthesis test
python -m agora.swarms.piper_tts
# → Outputs test_piper.wav to docs/ARTIFACTS/
```

---

## 6. End-to-End Flow Examples

### Example A: Voice Alert on Audit Finding

```
1. User: camelot exec "audit security"
2. Anya compiles → AUDIT intent → Sir Sentinel executes
3. Sentinel finds CRITICAL secrets → HITL LOCK
4. Sentinel result passed to TitanLink:
     server.broadcast_event({
         "type": "audit_alert",
         "severity": "CRITICAL",
         "vocal_cue": "Sovereign, 5 critical secrets detected. Iron Gate engaged."
     })
5. TitanLink detects vocal_cue → queues Sir Sonus
6. Piper TTS synthesizes with "tasha" voice
7. Audio streams via OmniRoute → LiveKit → mobile app
```

### Example B: Remote Desktop Automation via Bridge

```
1. User: camelot exec "open terminal on fothers-camelot and run status check"
2. Anya compiles → AUDIT/CREATE intent
3. Merlin routes to Sir Boris (orchestration)
4. Boris dispatches via RustDesk Bridge:
     bridge = RustDeskBridge(host="100.121.48.50", port=21115)
     bridge.execute_command({"action": "hotkey", "keys": "ctrl+alt+t"})
     bridge.execute_command({"action": "type", "text": "tailscale status\n"})
5. Boris captures frame for verification:
     frame = bridge.capture_frame()
     # → Sent to vision LLM for validation
6. Results logged to PROVENANCE_LEDGER.md
```

### Example C: Multi-Node Media Broadcast

```
1. TitanLink broadcasts to all Tailscale nodes:
     - cybertronia (100.118.224.52) — primary
     - fothers-camelot (100.121.48.50) — secondary
2. Each node receives event via WebSocket
3. If vocal_cue present → local Piper TTS synthesizes
4. Synchronized audio output across the mesh
```

---

## 7. Security Constraints

| Rule | Enforcement |
|------|-------------|
| Named Pipe ACL | Bind to authenticated Tailscale session only |
| RustDesk relay | Binds to 100.x.x.x, not 0.0.0.0 |
| Input injection | Zenith Scanner validates all typed commands |
| Voice model paths | Hardcoded to CAMELOT_OS — no user-supplied URLs |
| HITL on remote exec | Iron Gate approval required for remote commands |
| Latency ceiling | Sub-second mandatory (Titanium Law VIII) |
| RAM ceiling | 8GB total — VoxService singleton prevents double allocation |
| Container isolation | Docker services on internal camelot_net only |

---

## 8. Troubleshooting

| Problem | Fix |
|---------|-----|
| Piper voice not found | `python -m forge.scripts.setup_piper --voice <name>` |
| VoxService falls back to SIMULATED | Install espeak-ng + place kokoro model |
| TitanLink not connecting | Check Tailscale status, verify WS port open |
| RustDesk bridge timeout | Verify relay on Tailscale IP, check port 21115 |
| Named Pipe connection refused | Run anya_ipc_bridge as admin, check pipe name |
| Docker sonus not starting | `docker compose logs sonus` — check port 5050 |
| OmniRoute WebRTC no audio | Verify LiveKit token, check port 20128 |
| Audio crackling/latency | Switch from Kokoro (GPU) to Piper (CPU ONNX) |

---

## File Reference

| Component | Path | Language |
|-----------|------|----------|
| Piper TTS | `01_KERNEL/agora/swarms/piper_tts.py` | Python |
| VoxService | `01_KERNEL/senses/audio/vox_service.py` | Python |
| Sonus Compiler | `01_KERNEL/senses/audio/sonus/compiler.py` | Python |
| TitanLink Server | `01_KERNEL/senses/connectivity/titanlink_server.py` | Python |
| Anya IPC Bridge | `01_KERNEL/senses/connectivity/anya_ipc_bridge.rs` | Rust |
| RustDesk Bridge | `01_KERNEL/senses/connectivity/rustdesk_bridge.py` | Python |
| Aether Engine | `01_KERNEL/senses/connectivity/aether.py` | Python |
| Morgana Bridge | `01_KERNEL/senses/morgana_bridge/` | Rust |
| Voice-Media Cartridge | `03_VAULT/training/configs/cartridges/voice-media.yaml` | YAML |
| OmniRoute Config | `03_VAULT/training/configs/config/omniroute.json` | JSON |
| Docker Compose | `docker-compose.yml` | YAML |
| CLIProxyAPI | `~/CLIProxyAPI/cli-proxy-api.exe` | Go (binary) |
