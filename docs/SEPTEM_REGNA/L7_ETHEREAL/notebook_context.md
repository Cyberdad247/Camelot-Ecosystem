# Notebook Context — UKG Pull (2026-03-26)
## Source: "living Camelot-OS: The v300.1 Universal Singularity Recompilation"

### Architecture: Split-Brain AI Agency OS (Invisioned Marketing)

**Cloud/Edge (Tasha):** Client-facing — voice, chat, scheduling, lead capture, emotional routing. Serverless on Modal/Vercel.
**Local/Metal (Knights):** Heavy engineering — code scaffolding, security audits, financial analysis. On-demand via escalation.
**The Bridge:** Supabase-mediated handshake protocol. Zero context loss during escalation.

### Tech Stack
- **Cloud:** Next.js 14, Vercel, Modal (Whisper STT + Piper TTS), Rust→WASM guardrails, OmniRoute/CLIProxyAPI, PersonaPlex, Supabase
- **Local:** Python 3.12 (Lukas Ω), Claude API (Sir Forge), Ruff/Bandit (Sir Sentinel), Docker Compose, Tailscale
- **MCP:** Supabase, Vercel, Google Calendar, Gmail, Notion

### Sovereign Constraints
- Split-Brain Isolation (cloud never runs local, local never exposes public ports)
- Zero local compute for front office
- Tailwind CSS only, strict TypeScript, stable Rust only
- Zero hardcoded secrets, WASM guardrails non-optional
- RLS on all Supabase tables

### Implementation DAG: 9 Phases, ~13.5 hours
- Phase 1: Infrastructure & Foundation (Supabase + Next.js + Modal + Rust init)
- Phase 2: WASM Guardrails (Rust intent classifier + prompt-injection detector)
- Phase 3: Voice Pipeline (Modal STT/TTS + Next.js API routes)
- Phase 4: PersonaPlex & OmniRoute (emotional state + model dispatcher)
- Phase 5: Frontend Chat UI (chat layout, voice, booking, lead capture)
- Phase 6: The Bridge (Supabase Realtime → local listener)
- Phase 7: Kinetic Engine Room (Lukas + Forge + Sentinel + Valerian)
- Phase 8: Iron Gate Dashboard (auth'd UI for escalation queue)
- Phase 9: Deployment & Synchronization (deploy.sh + fleet.sh)

### Critical Path
T1.1 → T1.4 → T2.1-T2.7 → T4.4 → T4.8 → T5.4 → T6.1 → T7.1 → T8.1 → T9.5
