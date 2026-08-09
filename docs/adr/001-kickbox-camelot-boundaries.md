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

## Amendment 2026-08-09 — durable effects and a canonical skill catalog

The slice up to this point governed a pipe with nothing in it: every skill
returned a fixture string, so the lease machinery had never been tested
against a consequence. Two rules follow from giving it one.

1. **The skill catalog is language-neutral and canonical.**
   `integration/contracts/skills.manifest.json` is the single source of truth;
   the Go registry and the TypeScript contract are generated from it and
   committed. Go owns enforcement and TypeScript owns the UI contract, so
   neither may own the product definition. Drift fails `make test` locally —
   not only in CI, which is not a guarantee this repository can currently
   lean on.

2. **A skill's reach is declared, not inferred.** `effect` is one of
   `read_only | local_effect | remote_effect`, and it is independent of tier.
   Tier says who must approve; effect says how far the consequence travels. A
   skill that is `durable` (effect ≠ `read_only`) must also be lease-gated,
   must declare `retry: never`, and must declare
   `idempotency: lease_single_use`. The generator refuses a manifest that
   violates any of these, and the Go and TS suites assert them independently.

3. **The path is never an input, and it is named after the authorization.** A
   durable skill cannot name a location. The broker derives it from the skill
   id and the **lease id** beneath a fixed root under the existing `.run/`
   runtime directory — no second runtime root, so the teardown and ignore
   rules that already exist continue to apply. Size is capped.

   Naming it after the *turn* was wrong: a turn id is client-supplied, so two
   tabs, a page reload, or a hostile caller can reuse one. Combined with a
   write-once rule that meant a reload failed closed until someone wiped the
   runtime directory, and any caller could pre-claim a name to block future
   governed writes. A lease id is minted by the policy kernel, is unique per
   authorized action, and cannot be chosen by the caller. One authorization,
   one artifact.

4. **No action may destroy another's evidence.** Artifacts are write-once:
   the store hard-links into place, which is atomic and refuses to replace.
   With lease-derived names this is unreachable in normal operation — it
   remains because the failure it prevents leaves no trace of having happened.
   A re-submitted turn is a *second* authorization and correctly produces a
   second artifact; what must never occur is the first being overwritten.

5. **A refusal is a record.** A refused or failed execution is a governance
   event with the same evidentiary weight as a success — the same fields
   included, so it carries the transcript hash and can be tied back to what
   was asked — and it revokes the lease it failed under. Previously such a
   path returned `403` and wrote nothing to the audit log, so the log could
   answer "what happened" but not "what was stopped".

7. **Held material cannot outlive its lease.** A tier-3 payload waiting on
   human confirmation is kept in memory keyed by lease id. Approval, denial,
   and barge-in all release it; a lease that merely *expires* releases nothing,
   so the hold is swept against the lease TTL. Retention is bounded by the
   authorization that justified it.

6. **The audit records the effect result, never the material.** For a durable
   skill that means the relative path, byte count, and digest — enough to
   prove what changed, insufficient to reconstruct it. The transcript remains
   hashed for tier ≥ 2.

## Amendment 2026-08-09 (P1) — the governed surface is authenticated

A review of the agency blueprint found that every gateway route was
unauthenticated behind `Access-Control-Allow-Origin: *`, and that
`GATEWAY_ADDR` defaulted to `:8788` — every interface. On a Tailscale-connected
host, `POST /v1/confirmations` — the tier-3 human gate this ADR rests on — was
drivable by anything on the tailnet. The gate was decorative.

1. **Every route but `/healthz` requires a bearer token.** `/healthz` stays open
   because the startup gate polls it before a token could be plumbed, and it
   carries no data. Protecting only the tier-3 endpoint would have been
   incoherent: the approval would be guarded and the tier-2 durable write
   beside it would not.
2. **Absence of configuration is not absence of enforcement.** An unset
   `CAMELOT_API_TOKEN` makes the binary *mint* one, not run open. This is the
   explicit inverse of `control_plane/infra/z3_verify.py`, which returns
   `safe=true` when its solver is missing — a guard that disappears with its
   dependency is not a guard.
3. **The origin allow-list replaces the wildcard.** A preflight from an
   unlisted origin is refused outright rather than left to the browser to
   infer, and `Vary: Origin` is always set so a shared cache cannot serve one
   origin's response to another.
4. **Loopback by default.** Widening the bind is now a deliberate act
   (`GATEWAY_BIND`), required only for genuinely remote mesh nodes, and the
   gateway logs a warning when bound beyond loopback.
5. **The WebSocket accepts `?token=` — on that route only.** Browsers cannot set
   headers on a handshake. Query strings leak into logs and referrers, so the
   exception is scoped rather than general.

**What this does not fix, stated plainly.** The console is served by a static
file server rooted at `integration/`, so the token is readable over HTTP from
the console's own origin. Same-origin policy is what stops a hostile page
reading it; the origin allow-list is what stops one using it. A local process
with filesystem access can read the token — but such a process could always
read it from disk, so authentication was never the control at that boundary.
What the token adds is that reaching the port is no longer sufficient.
