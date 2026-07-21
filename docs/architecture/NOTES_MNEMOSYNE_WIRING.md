---
context: "CAMELOT-OS Lady Mnemosyne memory stack — Appwrite + Bifrost Bridge + NotebookLM MCP wire-up"
schema: "camelot.mnemosyne-wiring/v1"
status: "§7 RESOLVED 2026-07-14 — Q1/Q2/Q3 decided; PR #2 unblocked"
author: "freebuff (parent agent); maps to SIR_BORIS executive architect + MERLIN_OMEGA mapping role + SIR_HEIMDALL perimeter"
recon_date: "2026-07-14"
recon_files: 11
follows_from: "CAMELOT_OS/docs/architecture/UNIVERSAL_MCP_SYSTEM.md, CAMELOT_OS/docs/protocols/pre-flight.md v1.0.1"
supersedes: null
---

# 🪢 NOTES_MNEMOSYNE_WIRING — Appwrite + Bifrost + NotebookLM MCP for Lady Mnemosyne

> **Direct from operator (2026-07-14, ask_user clarification)**:
> "We are wiring up Appwrite as the self-hosted backend engine for Lady Mnemosyne's memory,
> wrapping the whole thing in Sir Heimdall's Bifrost Bridge (zero-trust network), and
> connecting the NotebookLM MCP directly into the Bifrost Bridge." → implementation intent.
>
> Per the §3 Assimilation Directive, MERLIN_OMEGA draws the map, SIR_BORIS builds it,
> SIR_HEIMDALL guards the perimeter. This document is the durable record of the
> architecture + PR sequence.

## 0. Preamble — Where This Lives

CAMELOT-OS already has substantial memory infrastructure:
- `control_plane/bifrost_gateway.py:62` exports HMAC-SHA256 signing (the canonical envelope scheme)
- `control_plane/bifrost_sandbox_adapter.py` exposes `get_bridge().handle_signed(raw_body, sig)`
- `control_plane/mnemosyne_chimera.py` — Lady Mnemosyne orchestration (NB synthesis, phial assignment)
- `control_plane/notebooklm_graphify_bridge.py` — NotebookLM-state → Graphify corpus bridge
- `control_plane/cloudbrain_sync.py` — CloudBrain ↔ Appwrite ↔ Modal sync (with local queue fallback)
- `03_VAULT/training/configs/integration_brain.py` — Dual-tier router (NotebookLM ST + Modal/Appwrite LT)
- `03_VAULT/training/configs/knights/mnemo.py` — Tier resolution (ST/LT/both)
- `CAMELOT_OS/01_KERNEL/titan/memory/appwrite_sync.py` — Push MemoryNode to Appwrite (orphaned in phase-verify-wt; promoted here)
- `control_plane/soul_oversight.py:177-209` — Iron Gate v2 `pre_execute()` (AUTO/PROMPT/HUMAN_GATE tier dispatch)
- `control_plane/heimdall_bifrost_governance.py` — "Check bridge intents against zero-trust and HITL policy"

**What's missing** (the gap set this PR sequence closes):
1. Appwrite self-host stack — no `CAMELOT_OS/docker-compose.appwrite.yml` (only ad-hoc references in `phase-verify-wt/02_FORGE/PORTAL_CORE/Modal/`)
2. `appwrite` Python dep is un-pinned (TITAN_AUDIT_OPEN_SRE_2026-07-06.md:41 MEDIUM)
3. `APPWRITE_ENDPOINT`/`APPWRITE_PROJECT`/`APPWRITE_API_KEY` env vars — no `.env.appwrite.example` template
4. End-to-end live Bifrost→Appwrite test path (HMAC parity test exists, but no Appwrite destination)
5. **No** official NotebookLM MCP server exists (Google has not published a public API); only path is Playwright-scraped export + custom MCP tool caching to local Vector DB.
6. Lower-environment validation of `_APP_REALTIME_HOST` mismatch (causes VPN/NAT handshake failures per researcher-docs guidance)
7. `heimdall_bifrost_governance.py` — currently scans mesh manifest, but does not gate Bifrost→Appwrite egress traffic explicitly

## 1. Architecture — Zero-Trust Egress Path

```
                    ┌─────────────────┐
                    │  Runic Router   │
                    │  (control_plane)│
                    └────────┬────────┘
                             │ tier dispatch (soul_oversight: AUTO|PROMPT|HUMAN_GATE)
                             ▼
                    ┌─────────────────┐
                    │ Bifrost Bridge  │  ← HMAC-signed envelope
                    │  (gateway.py:62)│  ← x-webhook-signature pattern
                    └────────┬────────┘
                             │ signed RPC envelope (POST /bifrost/dispatch)
                             ▼
                    ┌─────────────────┐
                    │ Bifrost Sandbox │  ← cartridge.bifrost_bridge
                    │ (cartridge pkg) │  ← ToolRegistry + RBAC + TrustManager
                    └────────┬────────┘
                             │ typed tool_id dispatch
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       Appwrite LT    NotebookLM MCP    Local Vector DB cache
       (self-host)    (Playwright scrape)
```

**Bifrost as the single ingress for both Appwrite and NotebookLM MCP**: every outbound call from a knight goes through `bifrost_sandbox_adapter.handle_signed(raw_body, sig)`. Signature scheme is HMAC-SHA256 over the raw body, shared `WEBHOOK_SECRET` env var, `hmac.compare_digest` constant-time. This is the unified envelope — Appwrite and NotebookLM MCP EGRESS go through the same gate.

**Iron Gate v2 calibration** (added to `soul_oversight.pre_execute`):
- `bifrost→appwrite write` → HUMAN_GATE (data mutation, external backend)
- `bifrost→appwrite read` → AUTO (read-only, idempotent)
- `notebooklm_mcp.export` → PROMPT (data ingestion, default confirm + timeout)
- `notebooklm_mcp.delete` → HUMAN_GATE (destructive)
- `appwrite_bootstrap.sh` → HUMAN_GATE (infra lifecycle)
- `heimbaseless init` (armed Bifrost→Appwrite first-launch envelope) → HUMAN_GATE per operator session

## 2. PR Sequence — 4 PRs (HIGH-IMPACT ROLL)

| PR | Title | Files (Δ lines) | Risk class | Reversible |
|---|---|---|---|---|
| **PR #1** | Appwrite self-host infra + dep pin | ~340 lines (5 files) | LOW (infra-only, no code surface change) | `rm -rf .appwrite_runtime/` |
| **PR #2** | Python SDK pin + typed client wrapper | ~280 lines (3 files) | MEDIUM (new dep version in compiled graph) | `git revert SHA` |
| **PR #3** | Bifrost→Appwrite envelope glue | ~220 lines (2 files) | HIGH (cross-tier HITL) | `git revert SHA` |
| **PR #4** | NotebookLM MCP stub + verification | ~240 lines (3 files) | HIGH (Playwright fragility, no official API) | `git revert SHA` |

**Estimated total**: ~1,080 lines of Python + ~280 lines of YAML/sh across all four PRs. Each PR ≤400-line diff target for review-ability.

## 3. PR #1 — Appwrite Self-Host Infra (THIS TURN)

**Goal**: stand up a self-hostable Appwrite 2.0 instance reachable from the Bifrost Bridge, with reproducible env contract per SEPTEM B4. NO `control_plane/*.py` modification.

**Files**:

### 3.1 `CAMELOT_OS/docker-compose.appwrite.yml`
- 5 services: `appwrite` (main), `mariadb` (10.x), `redis` (7-alpine), `minio` (storage), `traefik` (TLS termination).
- All on internal `appwrite_net` bridge network; only `traefik` exposes 80/443 to host.
- Named volumes for `appwrite-data`, `mariadb-data`, `redis-data`, `minio-data` (persist across reboots).
- Healthchecks per service via `test: ["CMD", "..."]`.
- Image pin: `appwrite/appwrite:1.6.5` (LTS as of 2026-07; 2.0 migration is a follow-on PR).
- Env vars templated from `CAMELOT_OS/.env.appwrite` (with `.env.appwrite.example` template).

### 3.2 `CAMELOT_OS/.env.appwrite.example`
Templated env contract:
- `_APP_ENV=production`
- `_APP_OPENSSL_KEY_DIFFICULTY=8`
- `_APP_REALTIME_HOST=appwrite.local` (FQDN to avoid VPN/NAT handshake failure)
- `APPWRITE_DB_HOST=mariadb`
- `APPWRITE_DB_PORT=3306`
- `APPWRITE_DB_USER=appwrite`
- `APPWRITE_DB_PASS=changeme-at-bootstrap`
- `APPWRITE_DB_ROOT_PASS=changeme-at-bootstrap` (auto-rotate via bootstrap script)
- `APPWRITE_REDIS_HOST=redis`
- `APPWRITE_REDIS_PORT=6379`
- `APPWRITE_STORAGE_DEVICE=MinIO`
- `APPWRITE_STORAGE_MINIO_ENDPOINT=minio`
- `APPWRITE_STORAGE_MINIO_ACCESS_KEY=changeme`
- `APPWRITE_STORAGE_MINIO_SECRET=changeme`
- `APPWRITE_DOMAIN=appwrite.local`
- `APPWRITE_ENDPOINT_PUBLIC=https://appwrite.local/v1`
- `APPWRITE_PROJECT=sovereign_db`
- `APPWRITE_API_KEY=<issued-by-bootstrap-script>`

### 3.3 `CAMELOT_OS/bin/appwrite_bootstrap.sh`
Bash bootstrap:
- (1) `cp .env.appwrite.example .env.appwrite` if missing
- (2) `openssl rand -hex 32` for APPWRITE_DB_PASS / APPWRITE_STORAGE_MINIO_SECRET if not present
- (3) `docker compose -f docker-compose.appwrite.yml pull` (downloading images)
- (4) `docker compose -f docker-compose.appwrite.yml up -d` (starting)
- (5) Health-check loop: poll `https://appwrite.local/v1/health` until 200 (max 120s)
- (6) Issue API key via `docker exec appwritecli api-key create` (after server up); write to `.env.appwrite`
- (7) Print `Appwrite LIVE at https://appwrite.local — APPWRITE_API_KEY in .env.appwrite`
- (8) Optional: register a MemStorage collection `memory_spine` with attributes `agent_id`, `content_hash`, `content`, `confidence`, `created_at`, `last_accessed`.

### 3.4 `CAMELOT_OS/docs/architecture/Appwrite_SelfHost_2026-07-14.md`
Deployment contract per SEPTEM B4:
- Required env vars table (matches `.env.appwrite.example`)
- Required port surface (80/443 host, 3306/6379/9000 internal)
- Required disk / RAM budget (per Appwrite 1.6 minimums: 2GB RAM + 1GB swap + 10GB disk)
- Backup strategy (named volumes + weekly `docker exec mariadb mysqldump`)
- Rollback strategy (`docker compose down -v` for full reset)
- 7-section template matching the Tier-N doc convention.

### 3.5 `CAMELOT_OS/pyproject.toml`
Single line change:
- OLD: `"appwrite",`
- NEW: `"appwrite>=2.0.0,<3.0.0",`

This pins the SDK to the 2.x line (matches 1.6.x server-side per dependency compat). Closes the TITAN_AUDIT_OPEN_SRE MEDIUM risk (line 41).

### 3.6 Verification (PR #1 acceptance)
- `docker compose -f CAMELOT_OS/docker-compose.appwrite.yml config` parses (no YAML errors)
- `bin/appwrite_bootstrap.sh --dry-run` checks env + required port availability (no docker daemon invocation)
- `python -c "import importlib.util; spec = importlib.util.spec_from_file_location('appwrite_sdk_check', None); print('OK')"` confirms sample import path
- `ruff check --select F401 --statistics CAMELOT_OS/pyproject.toml` (advisory only — pyproject.toml is TOML not Python)
- `git grep -n "appwrite>=2.0.0,<3.0.0" CAMELOT_OS/pyproject.toml` resolves to the new line

## 4. PR #2-#4 (queued for subsequent turns)

### 4.1 PR #2 — Python SDK pin + typed client wrapper
**Files**:
- `CAMELOT_OS/control_plane/appwrite_client.py` — typed `AppwriteClient` wrapper around `appwrite==2.x.Services.Databases` with retry + env-toggle + Z3 gate hand-off.
- `CAMELOT_OS/tests/control_plane/test_appwrite_client.py` — golden-path test + retry semantics + Authorization header.

### 4.2 PR #3 — Bifrost→Appwrite envelope glue
**Files**:
- `CAMELOT_OS/control_plane/bifrost_appwrite_dispatch.py` — thin module: `dispatch_to_appwrite(intent: str, payload: dict, signature: str)`. Wires into `bifrost_sandbox_adapter` so the existing bifurcation ingress picks up Appwrite destinations.
- `CAMELOT_OS/tests/control_plane/test_bifrost_appwrite_dispatch.py` — HMAC parity + signed-RPC smoke test.

### 4.3 PR #4 — NotebookLM MCP stub + verification
**Files**:
- `CAMELOT_OS/bin/notebooklm_mcp_server.py` — `FastMCP("notebooklm-bifrost-bridge")` exposing `export_notebook(url)` via Playwright; results cached to `03_VAULT/runtime_state/notebooklm_cache/`.
- `CAMELOT_OS/tests/control_plane/test_notebooklm_mcp.py` — mock-Playwright test with golden-path notebook fixture.
- `CAMELOT_OS/docs/architecture/NotebookLM_MCP_Bridge_2026-07-14.md` — operator-facing doc explaining the Playwright-fragility caveat + manual export alternative.

## 5. Risks (ranked HIGH→LOW)

| Rank | Risk | Mitigation |
|---|---|---|
| HIGH | `appwrite` dep version un-pinned (already in TITAN_AUDIT) | PR #1 §3.5 closes |
| HIGH | NotebookLM has NO public API/MCP — only Playwright-scraped path | PR #4 documents fragility + manual fallback |
| MEDIUM | `_APP_REALTIME_HOST` env mismatch causes VPN/NAT handshake failure | PR #1 §3.2 sets `appwrite.local` FQDN consistently |
| MEDIUM | Bifrost→Appwrite policy collision w/ existing `Anyagate_triage` entropy | PR #3 introduces co-located `triage.hitl_tier` review |
| LOW | Tailscale not installed on every operator's LAN | Optional follow-on PR for tailscale ACL wiring |
| LOW | Docker Compose v2 syntax vs v1 (legacy ops hosts) | PR #1 uses Compose v2 (modern); legacy v1 fallback documented |

## 6. Decision Matrix

| Decision | Pick | Rationale |
|---|---|---|
| Tailscale vs WireGuard vs Headscale for zero-trust mesh | **Tailscale** | Already baked into the heap (`kba_drone_bundle/`, `mesh/node_c/k8s/empire-drone-sidecar.example.yaml`); MagiC Wormhole + KBA drone verify the pattern |
| Appwrite deployment: docker-compose vs Helm vs one-binary | **docker-compose** | Cheapest host footprint (1 laptop vs k8s); matches existing `kinetic_edge/saltare/docker/` precedent |
| NotebookLM MCP: official vs custom FastMCP | **Custom FastMCP** | No official exists |
| Bifrost envelope extension: revise `bifrost_sandbox_adapter.py` vs new module | **New module** (`bifrost_appwrite_dispatch.py`) | Lower blast radius; existing adapter stays focused on Cartridge |
| How to ensure `CAMELOT_OS` doesn't accidentally regress on the appwrite pin | **CI lint** in PR #2 — `ruff check --select F401` augmented to also notice unpinned deps via `pip-audit` |

## 7. Resolved Decisions (2026-07-14 — operator resolved)

The three open questions from the prior draft are **RESOLVED**. The defaults were retained after grounding against existing code surface — no new code change required before PR #2.

### 7.1 Q1 — Pin version: **LOOSE** SemVer `appwrite>=2.0.0,<3.0.0`
- **Evidence anchored at**: `pyproject.toml:46`
- **Rationale**: Appwrite 1.6.x server + 2.x client SDK are in active maintenance (~monthly patch releases for the SDK; Appwrite 1.6.x branch is in active patch cadence through 2026 per Appwrite project roadmap — verify https://appwrite.io/roadmap at PR #2 kickoff). Loose bounds let security patches auto-tide; switching to exact (`==X.Y.Z`) blocks them and adds no reproducibility benefit (we gate egress via Bifrost HMAC + soul_oversight pre_execute HUMAN_GATE — any breaking change surfaces in PR #3's deploy).
- **Re-resolution trigger**: bump to exact pin in PR #N+1 once prod is stable and SDK churn-rate is known.

### 7.2 Q2 — Co-location: **SAME-HOST** via `docker-compose.appwrite.yml`
- **Evidence anchored at**: `docker-compose.appwrite.yml` + `bin/appwrite_bootstrap.sh`
- **Rationale**: 
  - PR #1 already GREEN — `bin/appwrite_bootstrap.sh` is idempotent; compose stack is reproducible.
  - "[[no-docker-microcubic-vm]]" heap law + "no-micro-VM" pattern prefer single-host compose.
  - Data persists across reboots via 4 named volumes (`camelot_appwrite_mariadb_data`, `camelot_appwrite_redis_data`, `camelot_appwrite_minio_data`, `camelot_appwrite_traefik_acme`).
- **Re-resolution trigger**: Tailscale-node co-location is **OPTIONAL** follow-on PR #5+ (post-self-host-stable). Triggers: laptop reboots > 3x/week, or operator wants remote-host zero-trust isolation.

### 7.3 Q3 — Heimdall responsibility split: **CARVE INTO** `heimdall_bifrost_governance.py` (option b)
- **Evidence anchored at**: `CAMELOT_OS/control_plane/heimdall_bifrost_governance.py:51`
- **Rationale**:
  - The `heimdall.rune_law` nano-knight (line 51) is **explicitly scoped** as *"Check bridge intents against zero-trust and HITL policy"* — the canonical fit for an Appwrite egress policy.
  - `heimdall_knight.py` (pydantic_ai Agent with `bifrost_lock`/`scan_vectors`/`guard_bridge`/`threat_pipe_hermes` tools) is the LLM-based mesh agent — wrong place for deterministic egress policy.
  - Creating a third module `heimdall_appwrite_guard.py` would split Bifrost policy across 3 files (SRP violation — the policy is one concern).
- **Concrete edit scope (PR #3)**: add a 6th nano-knight `heimdall.appwrite_egress` to the `HEIMDALL_NANO_KNIGHTS` tuple. Mission = *"Gate Bifrost→Appwrite egress against zero-trust policy; rotate `APPWRITE_API_KEY` per `appwrite_bootstrap.sh --rotate`."* Channel = `bifrost.policy.appwrite`. Tier = `S2` (matches sibling `rune_law`).

### 7.4 Forward-pointer — these resolutions unblock PR #2 immediately

None of the three resolutions require new code before PR #2 lands. PR #2 (typed `appwrite_client.py` wrapper, AUTO HITL tier) starts under the existing pin + same-host compose + governance carve-into plan. **PR #2 unblocked means §7-resolved; PR #2 STARTS only after PR #1 docker stack is verified-live per §8.**

## 8. Verification Discipline

- PR #1 → PR #2 → PR #3 → PR #4 must land sequentially; PR #2 will not start until PR #1's docker stack is verified live.
- Each PR ships with its own VLAD Cap verification (`bin/vlad <PR-prefix>.cap`) + a 60-minute smoke test.
- The §3 Assimilation Directive status row will be updated per PR landing (forward-pointer format).
- All four PRs run through `soul_oversight.pre_execute` (HUMAN_GATE tier per Iron Gate v2). The operator approves each lane via `CAMELOT_DASHBOARD_OPERATOR_TOKEN`.

## 9. References

- TITAN_AUDIT_OPEN_SRE_2026-07-06.md:41 — `appwrite` un-pinned MEDIUM risk
- TITAN_AUDIT_OPEN_SRE_2026-07-06.md:104 — uv-managed Python with mostly advisory pins
- docs/SEPTEM_REGNA/L7_ETHEREAL/tasks.md:36 — Track B B4 (Remote deployment contract) — PR #1 closes this
- docs/protocols/pre-flight.md v1.0.1 — §1.1 MCP table (where Appwrite-notebooklm would slot as a new MCP server)
- control_plane/heimdall_bifrost_governance.py:51 — "Check bridge intents against zero-trust and HITL policy"
- control_plane/soul_oversight.py:177-209 — Iron Gate v2 `pre_execute`
- kba_drone_bundle/control_plane/heimdall_watch.py — tailnet enforcement pattern (PR #4 optional integration)

---

*End of NOTES_MNEMOSYNE_WIRING blueprint. PR #1 (infra-only) lands in this turn;
PRs #2-#4 are queued. Operator confirmation requested on §7's three open questions
before any PR moves to merge.*
