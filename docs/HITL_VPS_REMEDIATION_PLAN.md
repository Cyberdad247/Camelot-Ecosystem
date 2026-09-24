# HITL Remediation Plan — VPS Hub KVM563 Service Gaps

**Status:** DRAFT — requires operator (HITL) approval for every deployment step.
**Source of findings:** on-box read-only investigation, 2026-09-23 (SSH BatchMode
diagnostics: `systemctl`, `ss -tlnp`, `docker ps`, `journalctl`).
**Scope:** KVM563 (162.35.107.134, tailscale0 100.110.180.18), node `vps_hub_kvm563`,
assigned knight HERMES_PRIME, co-governor SIR_HEIMDALL.

**Hard rules honored:** no service is started/stopped/installed by an agent without
explicit HITL confirmation; `SERVICE_PORT_MAP` was truthed to observed reality so the
tissue record never asserts state that cannot be verified (per commit `4d5bfebd`).

---

## Findings (evidence-backed)

| # | Finding | Evidence |
|---|---------|----------|
| F1 | `multivoice_router` (:7680), `honcho_self_hosted` (:8000), `webhook_receiver` (:9000) have **never been deployed** on KVM563 | No systemd unit files, no listeners (`ss -tlnp`), no containers (`docker ps -a` shows only `hermes`) |
| F2 | `vps_mobile_mesh_bridge` (:8095) binds the **Tailscale IP only**; loopback probing false-reports STOPPED | `camelot-vps-mesh.service` active; `ss`: `100.110.180.18:8095` LISTEN (python3 pid 1140397); `/dev/tcp/100.110.180.18/8095` OPEN |
| F3 | `:80` is served by **nginx**, not Caddy | `ss -tlnp`: nginx pids on `0.0.0.0:80`; no caddy unit on the box |
| F4 | GitHub webhook delivery is broken at two layers (receiver absent per F1; Caddyfile routes unmapped per F3) | `infra/caddy/Caddyfile` routes `/webhook/* → 127.0.0.1:9000`, `/worldtree/* → /var/www/worldtree`; only nginx exists |
| F5 | `camelot-selfcheck.service` FAILED (exit 7): audit references `user postgres` that does not exist | `journalctl -u camelot-selfcheck`: `root: unknown user postgres` ; `hub self-check FAILED` |
| F6 | Postgres absent (related to F5) — Honcho's typical DB dependency was never provisioned | Same journal evidence |

Already verified healthy (no action): `camelot-bifrost.service` (:3001, health 200),
`camelot-edge-bus.service`, `camelot-vps-mesh.service` (:8095 via TS IP),
nginx :80 serving WorldTree (HTTP 200), SSH :22.

---

## Remediation steps (each requires explicit operator y/N)

### R1 — Truth the probe surface (DONE, code-only, already shipped)
- `SERVICE_PORT_MAP` reduced to `{nginx_worldtree_gateway:80, bifrost_gateway:3001, vps_mobile_mesh_bridge:8095}` (key renamed from `caddy_worldtree_gateway` — nginx serves :80, R3 truthing).
- Tailscale-bound ports (`TS_IP_BOUND_PORTS = {8095}`) now probed at the tailscale0 address.
- Regression pins added in `tests/control_plane/test_worldtree_vps_cloudbrain_sync.py`.

### R2 — Decide the fate of the three absent services (DECISION, HITL)
Options per service:
- **multivoice_router (:7680)**: runs on the Windows host node, not the hub. Recommend:
  remove from hub expectations permanently; document hub↔host split. If hub presence is
  actually wanted, produce a unit file + deployment runbook first.
- **honcho_self_hosted (:8000)**: requires Postgres (F6). Recommend: deploy only if the
  hub is meant to serve self-hosted memory APIs; otherwise drop. Deployment needs:
  postgres install + user provisioning, honcho unit, secrets via `camelot keys set`
  (never plaintext).
- **webhook_receiver (:9000)**: required for GitHub-driven deploy flow (F4). Recommend:
  deploy (it gates the assimilation pipeline). Needs unit + secret token
  (`CLIPROXY`-style header) + ingress fix (R3).

**Operator choices needed:** deploy vs. drop, per service. Current map assumes DROP.

### R3 — Restore webhook ingress (requires R2 = deploy receiver)
**DECISION RECORDED 2026-09-23: nginx parity chosen.** Repo-side artifacts shipped:
`infra/nginx/webhook.conf` (route snippet + install runbook) and a selfcheck parity
check asserting the route is active in `nginx -T` once the snippet is installed.
The Caddyfile remains repo-canonical reference but is dormant for the hub.
On-box steps (scp snippet, include, reload, receiver unit) still require the
separate explicit approval below. Original options for the record:
1. **Caddy route** (repo-canonical): install caddy on KVM563, deploy `infra/caddy/Caddyfile`,
   disable nginx (or move :80 ownership). Risk: brief :80 downtime; nginx config drift.
2. **nginx parity**: replicate `/webhook/* → 127.0.0.1:9000` and `/worldtree/*` routes in
   the existing nginx server block. Risk: dual source of truth vs. repo Caddyfile —
   requires an audit note + parity check in `camelot-selfcheck`.

**Operator choice needed:** Caddy (canonical) vs. nginx (less disruption).

### R4 — Fix `camelot-selfcheck` postgres audit (small, still HITL)
**DECISION RECORDED 2026-09-23: conditional audit chosen, shipped in
`scripts/vps_hub_bootstrap.sh`.** Datastore checks (postgresql active, camelot_vmax,
qdrant world_tree) now WARN when the backing binary/unit is absent (expected state
after R2) and FAIL only when present-but-broken. Also fixed the true exit-7 root
cause: the hermes-prime engine check probed `127.0.0.1:8095` while the mesh binds
the tailscale0 address only, and the unguarded `$(curl | python3)` assignment
aborted the whole audit under `set -euo pipefail` with curl's exit code 7 before
any FAIL could be recorded. Options for the record:
- Provision `postgres` user/system user if the audit legitimately requires its existence
  (ties into R2 honcho decision), **or**
- Patch the selfcheck audit to treat postgres as conditional (skip with WARN, not FAIL)
  when honcho/postgres are not part of the hub's expected state.

**Operator choice needed:** provision vs. conditional-audit.

### R5 — Post-change verification gate
After any approved step: rerun
`python -m control_plane.runners.worldtree_vps_cloudbrain_sync` and require
- `worldtree_http_status == 200`, `bifrost_health_status == 200`,
- no `PROBE_FAILED` entries, drift reflecting only intentional state,
- `tests/control_plane/test_camelot_vps_hub_deployment.py` green.

---

## Evidence class
All findings above are `confirmed` (on-box commands, timestamps in journal excerpts).
Nothing in this plan has been executed on the VPS; the only writes so far are the
repo-side probe fix, map truthing, tests, and this document.
