# Voice Assistant Omega Assimilation Briefing

## Source Genes Assimilated

| Repository | Success Gene | Incorporated Form |
|---|---|---|
| `rcbyron/hey-athena-client` | Simple module/task architecture with phrase matching and priorities | `SkillRegistry`, `Skill`, and priority-sorted async handlers |
| `sksalahuddin2828/AI_Personal_Digital_Assistant` | Rapid single-file assistant command patterns | Built-in demo handlers for reminders, orders, status, and notes |
| `Gladiator07/JARVIS` | Practical desktop automation command catalog | Intent taxonomy for browser, notes, system status, weather, calendar, and email extensions |
| `AndraxDev/speak-gpt` | Mobile-first STT/TTS provider selection and local credential posture | Runtime-selectable STT/TTS providers via env-only settings |
| `leon-ai/leon` | Skills -> Actions -> Tools -> Functions layering; local/remote provider split | Deterministic controlled lane plus model lane and tool lane boundaries |
| `openclaw/openclaw` | Local-first gateway, channel security, pairing/allowlist posture, sandbox defaults | Token-gated WebSocket session, zero-trust request envelope, deny-by-default credentials |
| `claritylab/lucida` | Command center -> typed service graph -> backend service offload | `ServiceGraph`, `ServiceNode`, async fan-out/fan-in execution contract |

## RTK Scythe Decisions

- Keep Leon/OpenClaw modularity.
- Keep Lucida service graph semantics for heavy compute offload.
- Keep SpeakGPT provider switching and user-owned credential posture.
- Drop old blocking `speech_recognition` loops as the primary path.
- Drop desktop-only GUI and Selenium automation from the core.
- Drop cloud credential config files; use environment variables only.
- Drop monolithic command chains; every skill runs as a typed async unit.

## Production Architecture

```text
Audio Client
  -> /v1/audio/ws
  -> WakeGate
  -> STTProvider
  -> IntentRouter
  -> SkillRegistry OR ServiceGraph
  -> TTSProvider
  -> WebSocket response
```

## Runtime Guarantees

- Edge-native: default memory budget is 768 MB, hard ceiling target is 8 GB.
- Async-first: all IO boundaries are `async`.
- Zero-trust credentials: API keys are read from environment and never persisted.
- Quantization-ready: model config includes `ternary_1_58b` hooks for BitNet-style backends.
- Hot-swappable providers: `local`, `openai`, `openrouter`, `llama_cpp`, `lucida_rpc`.
- Sandboxed deploy: Docker Compose plus optional gVisor `runsc` runtime.

## Immediate Demo Script

1. Start stack:
   ```powershell
   cd C:\Users\vizio\CAMELOT_OS\02_FORGE\assimilation\voice_assistant_omega
   docker compose up --build
   ```
2. Health probe:
   ```powershell
   curl http://127.0.0.1:8088/health
   ```
3. Text intent probe:
   ```powershell
   curl -X POST http://127.0.0.1:8088/v1/intent -H "content-type: application/json" -d "{\"text\":\"remind Andre to call me\",\"session_id\":\"demo\"}"
   ```
4. WebSocket audio/control lane:
   ```text
   ws://127.0.0.1:8088/v1/audio/ws?token=change-me
   ```

## Extension Points

- Add wake-word engine in `WakeGate.detect`.
- Add local Vosk/Whisper/Tiny model in `STTProvider.transcribe`.
- Add OpenAI/OpenRouter/llama.cpp model call in `ModelBridge.complete`.
- Add Lucida-style service node in `ServiceGraph.run`.
- Add business skills by registering a `Skill` with patterns and handler.

