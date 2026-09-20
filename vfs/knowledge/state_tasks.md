# ⚡ TASKS.md — The Kinetic DAG

## Singularity Lattice Implementation Plan

> Every task is atomized to ≤15 minutes. Dependencies are explicit.
> Check off tasks as completed: `[ ]` → `[x]`

---

## Phase 1: Infrastructure & Foundation

*Estimated: 1.5 hours | Dependencies: None*

- [ ] **T1.1** — Create Supabase project, enable Realtime, note project URL + anon key
- [ ] **T1.2** — Create Supabase tables via migration: `leads` (id, name, email, phone, source, status, emotional_state, transcript, created_at)
  - *Depends on: T1.1*
- [ ] **T1.3** — Create Supabase tables via migration: `sessions` (id, lead_id FK, messages JSONB, persona_state JSONB, started_at, ended_at)
  - *Depends on: T1.1*
- [ ] **T1.4** — Create Supabase tables via migration: `escalations` (id, lead_id FK, session_id FK, type ENUM, transcript TEXT, knight_assignment TEXT, status ENUM [pending/in_progress/resolved], briefing_script JSONB, created_at)
  - *Depends on: T1.1*
- [ ] **T1.5** — Create Supabase tables via migration: `calendar_slots` (id, lead_id FK, datetime TIMESTAMPTZ, duration_min INT, status ENUM [booked/cancelled/completed], gcal_event_id TEXT)
  - *Depends on: T1.1*
- [ ] **T1.6** — Enable Row-Level Security on all tables; write RLS policies (anon can INSERT leads, authenticated can SELECT/UPDATE all)
  - *Depends on: T1.2, T1.3, T1.4, T1.5*
- [ ] **T1.7** — Scaffold Next.js 14 app with App Router (`npx create-next-app@latest --typescript --tailwind --app`)
  - *Depends on: None*
- [ ] **T1.8** — Configure Vercel project, link repo, set environment variables (SUPABASE_URL, SUPABASE_ANON_KEY, MODAL_TOKEN_ID, MODAL_TOKEN_SECRET)
  - *Depends on: T1.7*
- [ ] **T1.9** — Create Modal account, install `modal` CLI, run `modal token set`
  - *Depends on: None*
- [ ] **T1.10** — Initialize Rust project for WASM guardrails (`cargo init --lib guardrails`), add `wasm-pack` and `wasm-bindgen` to Cargo.toml
  - *Depends on: None*

---

## Phase 2: WASM Guardrails (The Bouncer)

*Estimated: 1.5 hours | Dependencies: Phase 1 partial*

- [ ] **T2.1** — Define intent enum in Rust: `Schedule`, `Onboard`, `ServiceInquiry`, `Technical`, `Escalate`, `OutOfScope`, `PromptInjection`
  - *Depends on: T1.10*
- [ ] **T2.2** — Implement regex-based intent classifier in Rust (match technical/architecture/code/debug → Escalate, scheduling keywords → Schedule, etc.)
  - *Depends on: T2.1*
- [ ] **T2.3** — Implement prompt-injection detector in Rust (check for "ignore previous", "system prompt", jailbreak patterns) → returns `PromptInjection` intent
  - *Depends on: T2.1*
- [ ] **T2.4** — Implement `classify(input: &str) -> IntentResult` as the single WASM-exported function returning JSON `{ intent, confidence, flags }`
  - *Depends on: T2.2, T2.3*
- [ ] **T2.5** — Compile to WASM with `wasm-pack build --target web`, verify `.wasm` + `.js` glue output
  - *Depends on: T2.4*
- [ ] **T2.6** — Write 10 unit tests in Rust: 2 scheduling, 2 onboarding, 2 technical (expect Escalate), 2 prompt-injection, 2 out-of-scope
  - *Depends on: T2.4*
- [ ] **T2.7** — Create Next.js utility `lib/guardrails.ts` that loads the WASM module and exposes `classifyIntent(text: string): Promise<IntentResult>`
  - *Depends on: T2.5, T1.7*

---

## Phase 3: Voice Pipeline (The Ear & Voice)

*Estimated: 1.5 hours | Dependencies: T1.9*

- [ ] **T3.1** — Create Modal function `stt_whisper.py`: accepts audio bytes, returns transcript text using `openai/whisper-large-v3`
  - *Depends on: T1.9*
- [ ] **T3.2** — Create Modal function `tts_piper.py`: accepts text string, returns WAV audio bytes using Piper TTS with a warm female voice model
  - *Depends on: T1.9*
- [ ] **T3.3** — Deploy both Modal functions, note endpoint URLs
  - *Depends on: T3.1, T3.2*
- [ ] **T3.4** — Create Next.js API route `app/api/voice/stt/route.ts`: receives audio blob from frontend, forwards to Modal STT, returns transcript
  - *Depends on: T3.3, T1.7*
- [ ] **T3.5** — Create Next.js API route `app/api/voice/tts/route.ts`: receives text, forwards to Modal TTS, streams audio response
  - *Depends on: T3.3, T1.7*
- [ ] **T3.6** — Test round-trip: record 5-second audio → STT → get text → TTS → play audio. Verify <2s total latency.
  - *Depends on: T3.4, T3.5*

---

## Phase 4: PersonaPlex & OmniRoute (The Brain)

*Estimated: 2 hours | Dependencies: Phase 2, Phase 3*

- [ ] **T4.1** — Define PersonaPlex state schema in TypeScript: `{ trust: 0-1, urgency: 0-1, intent_history: string[], sentiment: string, turn_count: number }`
  - *Depends on: T1.7*
- [ ] **T4.2** — Implement PersonaPlex state updater: takes (current_state, new_message, intent) → returns updated state with recalculated trust/urgency scores
  - *Depends on: T4.1*
- [ ] **T4.3** — Define OmniRoute model tier config: `{ tier1: "haiku" (low-stakes), tier2: "sonnet" (standard), tier3: "opus" (high-trust/complex) }` with intent→tier mapping
  - *Depends on: T4.1*
- [ ] **T4.4** — Implement OmniRoute dispatcher: takes (intent, persona_state) → selects model tier, constructs system prompt with Tasha's persona + emotional context, calls LLM
  - *Depends on: T4.2, T4.3*
- [ ] **T4.5** — Define Tasha's system prompt template: matriarchal tone, strict scope (scheduling/onboarding/services only), escalation deflection phrases
  - *Depends on: None*
- [ ] **T4.6** — Implement escalation template handler: when intent=Escalate, OmniRoute returns canned deflection + writes to Supabase `escalations` table
  - *Depends on: T4.4, T1.4*
- [ ] **T4.7** — Implement session logger: after each turn, write message + persona_state to Supabase `sessions` table
  - *Depends on: T4.4, T1.3*
- [ ] **T4.8** — Wire full pipeline: user text → WASM classify → PersonaPlex update → OmniRoute dispatch → response + session log
  - *Depends on: T2.7, T4.4, T4.6, T4.7*

---

## Phase 5: Frontend Chat UI (The Face)

*Estimated: 2 hours | Dependencies: Phase 4*

- [ ] **T5.1** — Create chat page layout `app/page.tsx`: full-screen chat container with Tailwind dark theme, agency branding header
  - *Depends on: T1.7*
- [ ] **T5.2** — Build `ChatBubble` component: renders user/assistant messages with distinct styling, timestamps, typing indicator
  - *Depends on: T5.1*
- [ ] **T5.3** — Build `ChatInput` component: text input + send button + microphone toggle button for voice mode
  - *Depends on: T5.1*
- [ ] **T5.4** — Implement text chat flow: input → POST to `/api/chat` → stream response → render bubbles
  - *Depends on: T5.2, T5.3, T4.8*
- [ ] **T5.5** — Implement voice chat flow: hold-to-record → POST audio to `/api/voice/stt` → pipe transcript to chat pipeline → TTS response → auto-play audio
  - *Depends on: T5.3, T3.4, T3.5, T4.8*
- [ ] **T5.6** — Build `BookingWidget` component: when OmniRoute detects scheduling intent, render inline calendar date picker that writes to `calendar_slots` via Supabase
  - *Depends on: T5.4, T1.5*
- [ ] **T5.7** — Build `LeadCaptureForm` component: name, email, phone — shown at session start or on Tasha's prompt, writes to `leads` table
  - *Depends on: T5.4, T1.2*
- [ ] **T5.8** — Add loading states, error boundaries, and mobile responsiveness to all components
  - *Depends on: T5.4, T5.5, T5.6, T5.7*

---

## Phase 6: The Bridge (Handshake Protocol)

*Estimated: 1 hour | Dependencies: Phase 4 (escalation writes), Phase 7 (local listener)*

- [ ] **T6.1** — Create Supabase Database Function + Trigger: on INSERT to `escalations` where status='pending', fire a `pg_notify` event
  - *Depends on: T1.4*
- [ ] **T6.2** — Create Python listener script `bridge/listener.py`: connects to Supabase Realtime, subscribes to `escalations` table changes where status='pending'
  - *Depends on: T6.1*
- [ ] **T6.3** — Implement Pre-Flight Packet assembler in `bridge/packet.py`: pulls lead info + session transcript + escalation context from Supabase, packages as structured JSON
  - *Depends on: T6.2*
- [ ] **T6.4** — Implement handoff to Lukas: `bridge/dispatch.py` takes assembled packet, writes to local task queue (Redis or filesystem-based queue)
  - *Depends on: T6.3*
- [ ] **T6.5** — Configure Tailscale on local machine, verify Supabase connection works through tunnel with <100ms added latency
  - *Depends on: T6.2*

---

## Phase 7: Kinetic Engine Room (The Knights)

*Estimated: 2.5 hours | Dependencies: Phase 6*

### Lukas Ω (Orchestrator)

- [ ] **T7.1** — Create `knights/lukas.py`: async event loop that monitors local task queue, dispatches tasks to appropriate Knight based on escalation type
  - *Depends on: T6.4*
- [ ] **T7.2** — Define task routing rules: `type=technical → Sir Forge`, `type=security_review → Sir Sentinel`, `type=financial → Sir Valerian`
  - *Depends on: T7.1*
- [ ] **T7.3** — Implement result collector: Lukas gathers Knight outputs, assembles `briefing_script` JSON, writes back to Supabase `escalations` table with status='resolved'
  - *Depends on: T7.1*

### Sir Forge (Code Gen)

- [ ] **T7.4** — Create `knights/forge.py`: accepts project brief JSON, calls Claude Sonnet API with scaffolding system prompt
  - *Depends on: T7.1*
- [ ] **T7.5** — Implement template engine: Forge outputs a Next.js project scaffold (file tree + boilerplate) following Midas Loop UI standards
  - *Depends on: T7.4*
- [ ] **T7.6** — Implement Git integration: Forge creates a new branch, commits scaffolded files, opens draft PR
  - *Depends on: T7.5*

### Sir Sentinel (Security)

- [ ] **T7.7** — Create `knights/sentinel.py`: accepts file paths or PR diff, runs Ruff linter + Bandit security scanner
  - *Depends on: T7.1*
- [ ] **T7.8** — Implement secret scanner: grep for API keys, tokens, passwords in code using regex patterns (AWS, Stripe, OpenAI, etc.)
  - *Depends on: T7.7*
- [ ] **T7.9** — Generate audit report JSON: `{ passed: bool, lint_errors: [], security_findings: [], secrets_found: [] }`
  - *Depends on: T7.8*

### Sir Valerian (Financial)

- [ ] **T7.10** — Create `knights/valerian.py`: accepts client brief + ad spend parameters, runs ROI projection model
  - *Depends on: T7.1*
- [ ] **T7.11** — Implement basic ROI simulator: input (budget, industry, channel) → output (projected leads, CPA, ROAS, break-even month)
  - *Depends on: T7.10*

---

## Phase 8: Iron Gate Dashboard

*Estimated: 1.5 hours | Dependencies: Phase 7*

- [ ] **T8.1** — Create authenticated dashboard route `app/dashboard/page.tsx` with Supabase Auth (email/password for VaShawn only)
  - *Depends on: T1.1, T1.7*
- [ ] **T8.2** — Build `EscalationQueue` component: lists all escalations with status badges (pending/in_progress/resolved), sorted by recency
  - *Depends on: T8.1, T1.4*
- [ ] **T8.3** — Build `BriefingCard` component: for resolved escalations, display client question + Knight's pre-calculated solution + ROI projection side-by-side
  - *Depends on: T8.2*
- [ ] **T8.4** — Build `LeadTable` component: sortable/filterable table of all captured leads with status, source, emotional state snapshot
  - *Depends on: T8.1, T1.2*
- [ ] **T8.5** — Build `SessionReplay` component: click a lead → view full conversation transcript with PersonaPlex state annotations per turn
  - *Depends on: T8.4, T1.3*
- [ ] **T8.6** — Add Supabase Realtime subscription to dashboard: new escalations and lead updates appear live without page refresh
  - *Depends on: T8.2, T8.4*

---

## Phase 9: Deployment & Synchronization

*Estimated: 1 hour | Dependencies: All previous phases*

- [ ] **T9.1** — Create cloud deploy script `deploy.sh`: `vercel deploy --prod` + `modal deploy stt_whisper.py tts_piper.py` in one command
  - *Depends on: T1.8, T3.3*
- [ ] **T9.2** — Create `docker-compose.yml` for local swarm: containers for Lukas, Forge, Sentinel, Valerian, Bridge listener, Redis (task queue)
  - *Depends on: T7.1 through T7.11*
- [ ] **T9.3** — Create local boot script `fleet.sh` (aliased to `//FLEET --activate`): `docker compose up -d` + Tailscale connect + health checks
  - *Depends on: T9.2, T6.5*
- [ ] **T9.4** — Write `.env.example` with all required environment variables documented (Supabase, Modal, Anthropic, Tailscale)
  - *Depends on: None*
- [ ] **T9.5** — End-to-end smoke test: client sends message → Tasha responds → technical question triggers escalation → Knight processes → dashboard shows briefing
  - *Depends on: All tasks*
- [ ] **T9.6** — Write `README.md` with architecture overview, setup instructions, and the two boot commands
  - *Depends on: T9.5*

---

## DAG Summary

```
Phase 1 (Infra) ──┬──→ Phase 2 (WASM) ──────┐
                   ├──→ Phase 3 (Voice) ──────┤
                   │                          ├──→ Phase 4 (Brain) ──→ Phase 5 (UI)
                   └──→ Phase 4.1 (Schemas)───┘                          │
                                                                          ↓
                   Phase 6 (Bridge) ←─────────────────────────────────────┘
                         │
                         ↓
                   Phase 7 (Knights) ──→ Phase 8 (Dashboard) ──→ Phase 9 (Deploy)
```

**Critical Path:** T1.1 → T1.4 → T2.1-T2.7 → T4.4 → T4.8 → T5.4 → T6.1 → T7.1 → T8.1 → T9.5

**Total Estimated Time:** ~13.5 hours of focused coding
