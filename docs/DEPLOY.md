# CAMELOT-OS Deploy Reality (decision record, 2026-09-17)

Three deploy stories exist in-tree and contradict each other. This file declares
which is canonical per target so agents stop guessing.

| Target | Canonical path | Evidence |
|---|---|---|
| Windows dev host | Native processes: `make dev-up` / `make status` / `make smoke` (Bifrost :3001, PWA :3000) | `Makefile:3,13-16` ("Native local processes only — no Docker") |
| Linux VPS hub (KVM563) | systemd units in `infra/systemd/` (`camelot-bifrost.service` → `node apps/bifrost/dist/server.js`); bootstrap via `scripts/vps_hub_bootstrap.sh` | `infra/systemd/camelot-bifrost.service:43-55` |
| Secrets on any host | `SecretManager` (`~/.camelot/secrets.enc`, env override wins) + edge VPS bus canonical values; never commit values | `control_plane/infra/secret_manager.py` |
| State backup | `scripts/backup_runtime_state.ps1` daily (RPO < 1d, RTO < 1h); SHA256 manifest; off-host copy over Tailscale only | `docs/guides/PRODUCTION_READINESS_GUIDE.md:321-327` |

Legacy / non-canonical:

- `docker-compose.yml` = photo-viewer + redis/minio/prometheus stack, NOT the CAMELOT stack. Do not extend it for Bifrost/PWA.
- `Dockerfile` ships wasmtime + edge WASM only. Full-stack image is a tracked follow-up (needs SBOM + cosign — see `supply-chain` CI job).
- `deploy/`, `ansible/`, `terraform/`, `ops/`, `05_INFRASTRUCTURE/` overlap. New deploy work goes here (this file) or `scripts/` — not a sixth directory.
- systemd units carry `User=root` and `/opt/camelot-ecosystem` paths (`camelot-bifrost.service:45-47`, flagged KNOWN GAP in-file). Harden before prod.
