# ADR-001: Kickbox ⇄ Camelot Integration Boundaries

- Status: **Proposed** (awaiting maintainer approval)
- Date: 2026-08-07
- Author: Merlin (systems architect pass)
- Related: [`../architecture/current-state.md`](../architecture/current-state.md),
  [`../architecture/bootstrap-plan.md`](../architecture/bootstrap-plan.md)

## Context

Camelot-Ecosystem is the sovereign governance platform; Kickbox-audio is the
Anya Lyte voice/avatar PWA (separate repo, protected `main`, not writable from
this workstream). The two already share gateway lineage — Camelot's
`apps/bifrost` is a fork of Kickbox's — but neither implements policy
decisions, capability leases, or a governed audit trail. Ad-hoc merging would
duplicate the bifrost fork problem and put UX code inside the trust boundary.

## Decision

Integrate by **contract, not by merge**. A new, self-contained vertical slice
lives in Camelot-Ecosystem under `integration/`; Kickbox-audio adopts the
shared contract package later, additively, in its own repo.

### Ownership boundaries (normative)

| Owner | Owns | Explicitly may NOT |
|---|---|---|
| **Camelot** (Go gateway + platform) | Identity, policy decisions, capability leases, skill registry, tool execution, audit, node authorization | Render UX; capture audio |
| **Kickbox** (PWA) | Microphone capture, VAD, barge-in UX, transcript display, text/TTS playback, avatar state rendering | Call any tool or node-agent directly — all traffic goes through the gateway |
| **Hermes** (adapter) | Capture/transcribe/speak; propose transcript→intent mappings | Call privileged tools; touch the tool broker, leases, or audit |
| **Rust node-agent** | Local compute job validation, batching, health, CPU fallback, optional Vulkan | Accept jobs without a valid gateway-signed lease |

### Rules

1. Every effectful action requires an **approved, short-lived lease**
   (TTL ≈ 30 s, single-use, revocable). Reads at tier 1 need no lease.
2. `change_request.create` (and any tier-3 skill) additionally requires an
   explicit human confirmation before its lease activates.
3. Raw audio is **ephemeral by default**. Persisted: transcript (tier 1 only),
   SHA-256 hashes, policy decisions, redacted audit events. Tier ≥ 2 audit
   records never contain raw transcripts.
4. Barge-in cancels response streaming and revokes unused leases; both actions
   are audited.
5. Vulkan is optional (`--features vulkan`) and must never prevent node-agent
   startup; CPU is the guaranteed backend.
6. Deterministic fixtures and mocks throughout — the demo requires no API keys.
7. Contract evolution is additive-only within a major version.

### Placement

- Contracts: `integration/contracts` (`@camelot/contracts`) — Camelot hosts
  the schema because the governance vocabulary is platform-owned; the package
  is dependency-free ESM so the Kickbox PWA can consume it unchanged.
  Kickbox's future thin wrapper (`@kickbox/camelot-client`) lives in Kickbox's
  `packages/` — out of scope here.
- Gateway: `integration/gateway`, a **new** stdlib-only Go module.
  `control_plane/go_router` (rune routing) and both bifrost gateways remain
  untouched; retiring or bridging them is a separate future ADR.
- Node-agent: `integration/node-agent`, a new Cargo workspace member.
- Console: `integration/kickbox`, a static text-first PWA standing in for the
  Kickbox surface until the real PWA adopts the contracts.

## Consequences

**Positive.** Existing Kickbox and Camelot functionality is preserved
verbatim; the trust boundary is enforced in one place (gateway) and testable;
the slice is offline-deterministic; CI is unaffected (no workflow path filter
matches `integration/**`); the contract package gives the two repos a stable
seam that survives independent release cadences.

**Negative / accepted costs.** A third gateway-shaped service exists until a
consolidation ADR lands; the static console duplicates a small amount of UI
that the real Kickbox PWA already has (accepted: it is a reference client for
the contract, not a product surface); minimal RFC 6455 WebSocket code is
maintained in-repo to keep the gateway dependency-free.

## Amendment 2026-08-07 — native runtime correction (νKG)

Accepted after the slice went live:

1. **Native processes only.** The supported deployment is bare processes with
   PID/log files in `integration/.run/`, health-gated startup, and the
   `scripts/{build,dev-up,dev-down,status,logs,smoke,benchmark}.sh` lifecycle. Docker
   and Kubernetes are unsupported; the compose artifacts are archived under
   `integration/archive/docker/`. Optional supervision (systemd user unit,
   tmux, Termux) wraps the scripts; Tailscale only if a remote mesh is wanted.
2. **Durable redacted audit.** The gateway persists the hash-chained audit
   into a local SQLite file (`GATEWAY_DB`, default
   `.run/camelot-voice.db`) via the pure-Go `modernc.org/sqlite` driver —
   the gateway's single external dependency (no CGO, no remote DB). A
   tampered store is refused at startup. Rule 3's persistence set is
   unchanged: hashes, decisions, redacted events — never raw transcripts
   (tier ≥ 2) or raw audio. Leases remain memory-only by design.
3. **Resource envelope.** 8 GB RAM target; no automatic local-model boot.

## Amendment 2026-08-08 — private mesh boundary (Phase 4A)

1. **Reachability is not authorization.** Tailscale (or any transport) may
   make a node reachable. It confers no trust and no permission. The gateway
   assigns a trust band (`pending → limited → trusted`, with `degraded` on
   stale health and terminal `revoked`) and mints every authorization.
2. **Every remote job needs a bound lease.** Node-job leases are node-scoped,
   tenant-scoped, capability-scoped, ~30 s, single-use, and HMAC-signed over
   `leaseId|capability|expiresAt|nodeId|tenantId`. The Rust agent
   independently re-validates all of it and enforces single use locally.
3. **No node self-declares locality or trust.** The operator names the local
   node (`CAMELOT_LOCAL_NODE_ID`); it is auto-trusted only when also reachable
   over loopback. Identity is pinned by an enrolment-secret fingerprint.
4. **Camelot never operates the network.** No login, no `tailscale up`, no ACL
   or route changes, no exit nodes, no public ingress. The only permitted
   external command is `tailscale status --json`, for observation.
5. **Local-first routing.** The mesh is used only when explicitly requested.
   Naming a node is a requirement, not a hint. Read-only remote failures fall
   back locally; effectful jobs are never retried and never re-run elsewhere.
6. **No addresses or key material in the UI or audit.** Both see a truncated
   address hash and nothing more.

**Rejected alternatives.**
- *Merge Kickbox into Camelot* — destroys independent deploy/release, violates
  "do not merge blindly", and would drag Next.js/Vercel/Sentry into the
  governance plane.
- *Extend `apps/bifrost` in place* — mixes the new lease/policy authority into
  a fork that must track upstream Kickbox; blast radius onto working code.
- *Extend `control_plane/go_router`* — different concern (rune routing), and
  its CLI contract is frozen by existing consumers.
