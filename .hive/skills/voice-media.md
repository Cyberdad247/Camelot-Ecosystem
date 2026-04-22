# SKILL BIBLE — Voice & Media Pipeline
# Knight: Sir Sonus (Voice) / Sir Visage (Media) | Layer: L7_ETHEREAL | v400.1.0
# LOAD: VOICE_MEDIA — instilled on //vocal, TTS, audio, image, video tasks

## TITANIUM LAW #8 — VOICE LATENCY
Sub-second mandatory. Any path adding >200ms latency is a violation.

## VOICE STACK
| Layer | Tech | Role |
|---|---|---|
| TTS Primary | Piper TTS (HuggingFace ONNX, local) | Zero-cost, zero-latency |
| TTS Secondary | Cartesia | Low-latency cloud fallback |
| TTS Legacy | ElevenLabs | High-cost — use only when explicitly requested |
| Streaming | LiveKit WebRTC | Real-time voice transport |
| Bridge | OmniRoute (port 20128 → LiveKit) | Singleton gateway |
| Singleton | VoxService | Prevents multi-GPU allocation race |

## //vocal RUNE — THREE PHASES
1. **Oracle Phase**: AST-Aware Plan Mode — install notebooklm-mcp-cli, bridge OmniRoute
2. **Veritas Phase**: 13-Agent Critique — extract persona Souls, assign Voice IDs
3. **Lazarus Phase**: E2E Self-Healing — Saltare gateway, mock voice test, latency check

## MEDIA PIPELINE
- **Image**: Flux (primary, local) / Midjourney (cloud, high-cost) — Sir Visage
- **Video**: Singularity Engine via Ω_ACTUATE rune
- **Audio**: Sir Sonus — songwriting, generative audio, audio physics
- **Modal GPU**: T4 inference for heavy generation tasks

## VOICE ID ASSIGNMENT
Each knight persona gets a unique Voice ID from VoxService.
Stored in: `03_VAULT/training/configs/memory/voice_registry.json`

## ANTI-PATTERNS (latency violations = T8 breach)
- Using ElevenLabs when Piper ONNX model is available → cost violation
- Multiple VoxService instances → GPU memory conflict → system crash
- Non-streaming TTS for real-time conversation → latency violation
- Modal GPU spawn for sub-1s tasks → overkill, use local Piper

## TOOLCHAIN
- `@vercel/agent-browser` — E2E browser testing for voice UI
- `Playwright` headless — voice interaction validation
- `NotebookLM MCP` — knowledge retrieval during synthesis
- `Modal GPU T4` — heavy inference (video, large audio generation)
