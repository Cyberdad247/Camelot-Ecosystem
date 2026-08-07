# Current State — Camelot-Ecosystem × Kickbox-audio

Author: Merlin (systems architect pass)
Date: 2026-08-07
Scope: read-only inspection of `Cyberdad247/Camelot-Ecosystem` (branch
`claude/camelot-kickbox-voice-slice-tdohyi`) and `Cyberdad247/Kickbox-audio`
(`main`, shallow read clone). No code was modified to produce this document.

---

## 1. Camelot-Ecosystem — architecture map

A polyglot sovereign-platform monorepo ("5-layer Omni-Nexus"). The subsystems
relevant to a governed Anya vertical slice:

| Subsystem | Location | Stack / entrypoint | Status |
|---|---|---|---|
| Python control plane | `control_plane/`, `01_KERNEL/` | `control_plane/main.py`; hermes file-bus at `~/.hermes/sessions/*.jsonl` | Working, heavily tested |
| Go rune router | `control_plane/go_router/` | module `camelot/go_router` (go 1.21), `main.go`; routes `/`, `/rune`, `/plan`, `/events` (SSE), `/healthz`; shells to Rust `rtk_cli` | Working — a *different* concern from voice; protected |
| Go multivoice | `04_KINETIC/multivoice/` | module `camelot-os` (go 1.23), `cmd/multivoice` | Provider orchestration; separate concern |
| Rust workspace | root `Cargo.toml` (10 members incl. `04_KINETIC/squires_rs`, `control_plane/rtk`, `kinetic_edge/*`) | toolchain pinned **1.85.0** via `rust-toolchain.toml` (deliberate, documented Truth-Contract pin) | Working |
| Node/TS root | root `package.json` (no `workspaces`; TS ^6, vitest ^4) | `vitest.config.ts` scoped to `tests/router/**` only; `src/router/{policy,schema}.ts` | Working, green tests |
| Bifrost fork | `apps/bifrost/` | Express 4 + `ws` + Prisma; `src/server.ts`; vitest ^2; `src/hermes.ts` publishes to the Python hermes bus | A trimmed fork of Kickbox's bifrost gateway |
| Anya domain types | `02_FORGE/packages/anya-domain/` | zod schemas: Iron Gate challenge/response (nonce + timestamp + 30 s TTL), `VoiceIntent` allow-list, risk levels, UKG graph types | Reusable conceptually |
| Voice-first runtime | `02_FORGE/packages/voice-first-runtime/` | browser mic capture + worklet + RMS VAD; typed `VoiceRuntimeState`, `VoiceFrame`, `VoiceUtterance` | Reusable for the later voice phase |
| Anya apps | `02_FORGE/apps/anya-lyte` (Expo RN), `02_FORGE/apps/pwa-cockpit` (Next 16 cockpit; Iron Gate HITL receipts, allowed-runes policy) | — | Governance precedent; protected |
| CI | `.github/workflows/`: `forge-ci.yml` (paths `02_FORGE/**`), `deploy-vercel.yml`, `build-photo-viewer.yml`, `verify_os.yml` | — | No filter matches a new top-level `integration/` dir |
| Compose | root `docker-compose.yml` | dedicated to the secret-photo-viewer stack (ports 7860, 3000, 9090, 6379, 9000/9001) | Protected — must not be reused |

Key gap: **no existing implementation of capability leases, a voice/turn API,
or a compute node-agent.** Those are genuinely new. (The pwa-cockpit "SSE
lease" is a connection-lifetime bound, not a capability lease.)

## 2. Kickbox-audio — architecture map

Turborepo + npm workspaces, root package `sovereign-system` (workspaces:
`apps/*`, `packages/*`; Node ≥ 20; vitest 2; Biome; Prisma 5).

### Packages and app entrypoints

| Workspace | npm name | Entrypoint | Role |
|---|---|---|---|
| `apps/pwa` | `pwa` | Next.js 14 App Router — `src/app/layout.tsx` / `src/app/page.tsx`; `next dev` | Primary voice/avatar PWA surface (Lakisha HUD, `useVad` RMS VAD, `BifrostContext` WebRTC bridge, Playwright + axe e2e, Sentry/OTel, strict CSP via `vercel.json`) |
| `apps/bifrost` | `bifrost` | `src/server.ts` → `dist/server.js`; listens on `PORT` (default **3001**); HTTP + `ws` WebSocketServer | Gateway: `/health`, `/api/bifrost/issue`, `/api/bifrost/hitl` (HITL), admin cert revoke/reissue, `/webhook/sms`; HMAC envelope (`security.ts`), JWT RBAC (`auth.ts`), lane router with `//REZERO` fallback (`router.ts`), deterministic NLP (`nlp.ts`), in-memory state machine (`state.ts`) |
| `apps/mcp-query` | `mcp-query` | `src/server.ts` → `dist/server.js` | Remote MCP query service |
| `packages/db` | `@sovereign/db` | `src/index.ts`; Prisma schema + `ledgerValidator.ts` (hash-chained ledger) | Persistence + ledger integrity |
| `packages/benchmark` | `@sovereign/benchmark` | `run.ts` (tsx) | Performance harness |
| `core/knights` | (data, not a workspace) | JSON-LD + md knight/persona profiles | Persona definitions |

CI: `ci.yml` (lint + typecheck + test + build), `kba-smoke.yml`, burst-test
workflows, `vault-rotate.yml`. Branch protection on `main`.

### Shared DNA

Camelot's `apps/bifrost` is a fork of Kickbox's `apps/bifrost` (same
`state.ts`/`nlp.ts`/`security.ts` lineage; Camelot's adds `hermes.ts`, Kickbox's
adds RBAC/certs/KBA counters). The repos are already conceptually integrated at
the gateway layer; what is missing is a **contract-first governance boundary**:
policy decisions, capability leases, and audit are implemented nowhere.

## 3. Reusable modules for the slice

| Module | Reuse |
|---|---|
| `voice-first-runtime` types | Align contract `VoiceTurn`/session states with `VoiceRuntimeState`, `VoiceUtterance` so real capture can be wired later without breaking changes |
| `anya-domain/src/ironGate.ts` | Confirmation-gate pattern (nonce, timestamp, 30 s TTL, risk tiers) → informs `CapabilityLease` + confirmation flow |
| Kickbox `apps/bifrost/src/security.ts` | HMAC-SHA256 + freshness-window pattern → lease-token signing gateway ⇄ node-agent |
| Kickbox `router.ts` + `nlp.ts` | Deterministic utterance→command parsing, lane fallback → model for the fixture-driven Hermes adapter |
| Kickbox `packages/db/ledgerValidator.ts` | Hash-chain pattern → audit-event chaining |
| Camelot `control_plane/go_router` | Stdlib-only Go service conventions (mux, `/healthz`, SSE); style reference only, code untouched |
| Camelot `apps/bifrost/src/hermes.ts` | Optional integration point: emit redacted slice events onto the existing hermes file-bus so Python knights can observe |
| `pwa-cockpit` Iron Gate receipts | Governance precedent: approval ≠ execution permission; explicit allow-list wins |

## 4. Constraints and risks discovered

- **Toolchains available**: Go 1.24, Rust 1.85 (matches pin), Node 22, Docker.
- **Dependency skew**: vitest 4 (Camelot root) vs vitest 2 (`apps/bifrost`,
  Kickbox). A new package must be self-contained — do **not** add `workspaces`
  to Camelot's root `package.json`.
- **Shared-file blast radius**: the only shared files a new slice must touch
  are root `Cargo.toml` (one additive member line) and `.gitignore`.
- **Ports free** for the slice: 8080 (console UI), 8788 (gateway), 8789
  (node-agent). Existing claims: 3000/3001/3005/3006/6379/7860/9000/9090.
- **Kickbox-audio is not writable from this workstream.** All integration code
  lands in Camelot-Ecosystem; Kickbox adoption is a documented follow-up in
  that repo.
