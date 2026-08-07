# Bootstrap Plan — Governed Anya Console Vertical Slice

Author: Merlin (systems architect pass)
Date: 2026-08-07
Prerequisite reading: [`current-state.md`](./current-state.md),
[ADR-001](../adr/001-kickbox-camelot-boundaries.md)

## 0. Prime directives

1. **Preserve existing Kickbox-audio functionality.** Nothing in the Kickbox
   repo is modified in this scope; the adoption path there is additive (a new
   package + a new page, no edits to existing hooks, HUD, or bifrost routes).
2. **Protect working Camelot code.** Only two existing files change across the
   whole plan (root `Cargo.toml`: one member line; `.gitignore`: ignore
   entries). Everything else is new files under `integration/` and `docs/`.
3. **Text-first.** The smallest end-to-end slice takes a *typed* utterance
   through policy → lease → execution → audit → rendered reply. Microphone,
   VAD, and TTS attach later behind the same contract; barge-in is exercised
   with a mock event from day one.
4. **Deterministic fixtures everywhere; no API keys.** Vulkan optional and
   never load-bearing for startup.

## 1. Where the Camelot client package belongs

- **Canonical home (this repo, this scope):** `integration/contracts/` in
  Camelot-Ecosystem, published name `@camelot/contracts`. Camelot owns the
  governance vocabulary (policy, leases, audit), so the contract source of
  truth lives with the platform. The package is ESM, browser-safe, and has
  **zero runtime dependencies** precisely so any client can consume it.
- **Adoption home (Kickbox repo, follow-up scope):** `packages/camelot-client`
  in the Kickbox monorepo — a thin `@kickbox/camelot-client` wrapper that
  re-exports `@camelot/contracts` and adds Kickbox-specific conveniences
  (React hooks around the session client). It slots into the existing
  `workspaces: ["apps/*", "packages/*"]` glob with no config change, and
  `apps/pwa` adds it as a dependency — additive only.

## 2. Smallest path to a text-first Anya vertical slice

```
[Anya Console (static PWA)] --HTTP/WS--> [Go voice gateway] --leased jobs--> [Rust node-agent]
        text input                        policy · leases                     CPU audio features
        transcript pane                   skills · audit                      (Vulkan optional)
        decision card                     Hermes adapter (fixtures)
        approval control
        barge-in (mock)
```

Thin waist: one endpoint family. A *text turn* is a `VoiceTurn` whose
`transcript` is typed rather than transcribed (`modality: "text"`); the voice
phase later populates the same field from capture without any API change.

Minimal E2E (end of Phase 3): type "read staging status" → gateway policy
allows tier-1 read → reply streams over WS → audit drawer shows the redacted
event. Then "prepare deployment review" (tier-2 auto-lease) and "create change
request" (blocked → approval control → executed). Barge-in button cancels the
stream and revokes the unused lease.

## 3. Required services

### Go — `integration/gateway` (new module `camelot/integration/gateway`, stdlib-only)

The **only** authority. Owns identity, policy decisions, capability leases
(TTL ≈ 30 s; `pending → approved → consumed | revoked | expired`), skill
registry, tool broker (refuses any effectful call without an approved lease),
hash-chained redacted audit log, and session event streaming.

| Endpoint | Purpose |
|---|---|
| `POST /v1/voice/turns` | Submit a turn (text-first; `modality` field) |
| `POST /v1/voice/barge-in` | Cancel streaming reply, revoke unused leases |
| `POST /v1/confirmations` | Approve/deny a pending lease |
| `GET  /v1/audit/:id` | Fetch redacted audit record |
| `GET  /healthz` | Liveness |
| `GET  /v1/sessions/:id/events` | WebSocket session events (minimal RFC 6455, server-push) |

Bootstrap skills: `ops.staging.read` (tier 1, read, allow), 
`deployment.review.prepare` (tier 2, effectful draft, auto-lease),
`change_request.create` (tier 3, confirmation required).

The Hermes adapter (`hermes.go`) is a pure transcript→intent proposer driven by
deterministic fixtures. It never touches the tool broker.

### Rust — `integration/node-agent` (new workspace member `camelot-node-agent`)

Local compute plane. `GET /healthz`, `POST /v1/compute` (batched audio-feature
jobs: RMS, zero-crossing rate, peak, frame energies), strict `JobValidator` /
`LeaseValidator` interfaces (expiry, capability match, gateway HMAC), backend
selection `select_backend()`: CPU always available; `--features vulkan`
compiles a probe-based Vulkan backend that degrades to CPU when the loader is
absent. Zero default dependencies beyond serde/serde_json/sha2 (already in the
workspace lockfile); builds on the pinned Rust 1.85.

### Existing services — untouched

`control_plane/go_router`, `apps/bifrost` (both repos), `04_KINETIC/multivoice`,
the Python control plane, and the root photo-viewer compose stack.

## 4. Contract ownership

| Contract | Owner | Consumers |
|---|---|---|
| `PolicyDecision`, `CapabilityLease`, `AuditEvent`, skill/tier registry | **Camelot** (gateway is source of truth; contracts package mirrors it) | Kickbox UI (render-only), node-agent (validate-only) |
| `VoiceTurn`, `VoiceBargeIn`, session/avatar states | **Kickbox** semantics (UX-owned), **Camelot**-hosted schema — field names aligned with `voice-first-runtime` types | Gateway (accepts), Hermes adapter (reads transcript only) |
| `CamelotTurnResponse`, session-event union | Joint; versioned additively | Both |
| Compute job/lease wire format | Camelot | node-agent |

Evolution rule: additive-only within a major version; the gateway rejects
unknown *required* fields; clients ignore unknown fields.

## 5. Test plan

| # | Proof | Layer |
|---|---|---|
| T0 | Protected baseline: root `npx vitest run`, `cargo check --workspace`, `go build ./...` (go_router) green before and after every phase | all |
| T1 | Kickbox cannot invoke an effectful tool without a lease (broker unit test + HTTP-level rejection + contracts client-guard test proving no direct tool surface exists) | Go + TS |
| T2 | Tier-2 draft creation works (`deployment.review.prepare` → draft artifact, lease consumed) | Go |
| T3 | `change_request.create` requires confirmation (blocked until `/v1/confirmations` approve; deny revokes) | Go |
| T4 | Barge-in cancels response streaming and revokes the unused lease (WS stream halts; lease state `revoked`; audited) | Go + TS state test |
| T5 | Node-agent uses CPU when Vulkan is unavailable (default build and `--features vulkan` with no loader both select CPU; startup never blocked) | Rust |
| T6 | Audit redaction: tier ≥ 2 audit records contain transcript SHA-256, never raw transcript; chain hashes verify | Go |
| T7 | Smoke: `scripts/smoke.sh` exercises healthz ×2, all three skills, confirmation, barge-in, audit fetch, one compute job | E2E |

## 6. Implementation phases

| Phase | Deliverable | Acceptance criteria |
|---|---|---|
| **0** | Protected baseline recorded (no new code) | T0 green; pre-existing failures documented, not silently fixed |
| **1** | `@camelot/contracts` package + fixtures + tests | `npm test` green in `integration/`; ESM, zero runtime deps; client-guard test passes (T1 client half) |
| **2** | Go gateway with policy/leases/skills/audit/WS | `go test ./...` green: T1 (server half), T2, T3, T4, T6 |
| **3** | Anya Console UI (static TS PWA) — **smallest text-first E2E complete** | `make demo-dev` serves `http://localhost:8080`; three skill flows + barge-in work in-browser, zero API keys |
| **4** | Rust node-agent scaffold | `cargo test -p camelot-node-agent` green incl. T5; both feature builds compile; workspace check still green |
| **5** | Compose + Make + smoke | `docker compose config` validates; `make demo-dev && make smoke` green (T7) |
| **6** | `docs/integration/camelot-kickbox.md` + Kickbox adoption guide | Every documented command was executed; final smoke output recorded |

One commit per phase; each phase's tests run before the next begins.

Out of scope: production deployment, unrestricted agents, global memory,
custom LLM kernels, edits to protected paths, edits to the Kickbox-audio repo.

## 7. Phase 1 file manifest

New files:

```
integration/package.json
integration/tsconfig.base.json
integration/vitest.config.ts
integration/contracts/package.json
integration/contracts/tsconfig.json
integration/contracts/src/types.ts
integration/contracts/src/client.ts
integration/contracts/src/fixtures.ts
integration/contracts/src/index.ts
integration/contracts/tests/contracts.test.ts
integration/contracts/tests/client-guard.test.ts
integration/contracts/tests/barge-in.test.ts
```

Modified files (additive only):

```
.gitignore        # ignore integration node_modules / dist artifacts
```

No other existing file is touched in Phase 1.
