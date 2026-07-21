---
context: "Appwrite 1.6.5 self-host contract for Lady Mnemosyne's long-term memory backend"
schema: "camelot.appwrite-selfhost-deployment/v1"
version: "v1.0.0"
encoding: "TOON_UKG_v1"
spec_authority: "CAMELOT_OS/docs/architecture/NOTES_MNEMOSYNE_WIRING.md §3 (PR #1)"
follows_from: "CAMELOT_OS/docs/SEPTEM_REGNA/L7_ETHEREAL/tasks.md:36 (Track B B4 'Remote deployment contract')"
---

# 🏰 Appwrite Self-Host Deployment Contract (v1.0.0)

> Per the Absorption Directive's SEPTEM_REGNA Track B **B4** ("document and validate
> required environment variables for Modal, Appwrite, and remote health URLs"), this
> document is the canonical deployment contract for Appwrite 1.6.5 in CAMELOT-OS
> v1000.0.0 — the long-term memory tier for Lady Mnemosyne per integration_brain.py.
>
> Bifrost Bridge egress source-of-truth; spin-up: `bin/appwrite_bootstrap.sh`.

## 0. Preamble — Why v1.0.0

- **Appwrite 1.6.5 LTS** (image: `appwrite/appwrite:1.6.5`) — chosen over 2.x because the
  2.x line is still mid-2026 maturation; pinning to 1.6.x keeps the self-host
  contract minimal and reproducible. A 2.x migration follow-on PR is queued.
- **Python SDK**: pinned `appwrite>=2.0.0,<3.0.0` (in `pyproject.toml`) — this
  matches the SDK's compatibility window which still talks to 1.6.x JSON-RPC.
- **Co-location**: same host as Bifrost Bridge via `camelot_appwrite_net` private bridge
  network. No host-port collision with the existing Camelot-OS port map.

## 1. Required Environment Variables

The full env contract lives in `CAMELOT_OS/.env.appwrite.example`. Required (non-default) keys:

| Group | Variable | Default | Notes |
|---|---|---|---|
| **APPWRITE runtime mode** | `_APP_ENV` | `production` | |
| | `_APP_REALTIME_HOST` | `appwrite.local` | FQDN to dodge VPN/NAT handshake per docs |
| | `APPWRITE_DOMAIN` | `appwrite.local` | Public hostname for Traefik ACME |
| **MariaDB credentials** | `APPWRITE_DB_HOST` | `mariadb` | Appwrite self-host default |
| | `APPWRITE_DB_PORT` | `3306` | |
| | `APPWRITE_DB_PASS` | rotated by bootstrap (`openssl rand -hex 32`) | |
| | `APPWRITE_DB_ROOT_PASS` | rotated by bootstrap | |
| **Redis credentials** | `APPWRITE_REDIS_HOST` | `redis` | |
| | `APPWRITE_REDIS_PORT` | `6379` | |
| **MinIO S3 storage** | `APPWRITE_STORAGE_MINIO_ENDPOINT` | `minio` | Internal only |
| | `APPWRITE_STORAGE_MINIO_ACCESS_KEY` | rotated by bootstrap | |
| | `APPWRITE_STORAGE_MINIO_SECRET` | rotated by bootstrap | |
| **Public endpoint** | `APPWRITE_ENDPOINT_PUBLIC` | `https://appwrite.local/v1` | Bifrost reads this |
| | `APPWRITE_PROJECT` | `sovereign_db` | Project ID printed by bootstrap |
| | `APPWRITE_API_KEY` | `<issued-by-bootstrap-script>` | Bifrost reads this via gateway.py |

## 2. Required Port Surface

| Service | Container port | Host port | Protocol | Note |
|---|---|---|---|---|
| `traefik` (TLS) | 443 | 443 | TCP | ACME cert issuer endpoint |
| `traefik` (PLAINTEXT → redirect) | 80 | 80 | TCP | Redirect → 443 |
| `appwrite` | 80 (internal only) | n/a | TCP | Reached via Traefik |
| `mariadb` | 3306 (internal only) | n/a | TCP | On `appwrite_net` |
| `redis` | 6379 (internal only) | n/a | TCP | On `appwrite_net` |
| `minio` | 9000 (internal only) | n/a | TCP | On `appwrite_net` |
| `minio` console | 9001 (internal only) | n/a | TCP | On `appwrite_net`, optional |

**No host port** under 1024 is opened except 80/443 via Traefik. The Bifrost Bridge
connects over the Docker network — no port collision with the Camelot-OS HUD 5-port
probe (8011 Bifrost, 8077 Heimdall, 8088 Codex, 8090 Colossus, 8079 Anya).

## 3. Required Disk / RAM Budget

Per Appwrite 1.6 minimums (verified by docker-compose `:memory`/`:cpus` reservation):

| Resource | Minimum | Recommended |
|---|---|---|
| RAM (host) | 2 GB | **4 GB** |
| Swap | 1 GB | 4 GB |
| Disk | 10 GB | **50 GB** (MariaDB + MinIO persist) |
| CPU | 2 cores | 4 cores |

The Lady Mnemosyne Memory Spine collection (target: 100k MemoryNodes × ~2 KB) is
projected to consume 200 MB — well within the recommended budget.

## 4. Backup Strategy

```bash
# MariaDB dump (synchronous; safe during low-traffic window)
docker exec camelot-appwrite-mariadb sh -c \
  'mysqldump --all-databases --single-transaction --quick' \
  > /opt/appwrite_runtime/backups/mariadb-$(date +%F).sql

# MinIO bucket mirror
docker exec camelot-appwrite-minio mc mirror /data /backups/$(date +%F)/

# Schedule weekly via cron (add to /etc/crontab):
0 3 * * 0  cd ~vizio/CAMELOT_OS && bin/appwrite_bootstrap.sh --backup
```

## 5. Rollback Strategy

Pure infra — no `.py` files touched. Rollback is a 1-command teardown:

```bash
bin/appwrite_bootstrap.sh --teardown
# Equivalent: docker compose -f docker-compose.appwrite.yml down -v
```

The Bifrost Bridge keeps operating with its current gallop (no Appwrite destination
yet — that lands in PR #3). If the stack is down, Bifrost surfaces the destination
unavailability with `'appwrite_unreachable: ...'` (per cloudbrain_sync.py:209 fall-back
sentence) — graceful degradation.

## 6. Roll-forward Strategy (versions)

- **Appwrite server**: 1.6.5 LTS → 2.x migration queued as follow-on PR. Watch the
  `_APP_REALTIME_HOST` env var during migration (2.x is reportedly stricter on
  FQDN-vs-IP mismatches).
- **Python SDK**: `appwrite>=2.0.0,<3.0.0` — semver-minor compatible; the SDK has not
  pushed a breaking 3.x as of 2026-07-14.
- **MariaDB 10.11 → 11.x**: NOT yet — 1.6 Appwrite image is built against MariaDB 10.x
  client library, and the breaking changes in 11.x need validation.

## 7. Verification Procedure

```bash
# 1. Live health
curl -fsS https://appwrite.local/v1/health | jq .
# Expect: {"status":"pass","version":"1.6.5",...}

# 2. Project exists
APW_ENDPOINT=https://appwrite.local/v1
APW_PROJECT=sovereign_db
APW_API_KEY=$(grep '^APPWRITE_API_KEY=' .env.appwrite | cut -d= -f2-)

# (note: jq selectors below assume appwrite 1.6 REST shape; validate against live)
curl -fsS -H "X-Appwrite-Project: $APW_PROJECT" -H "X-Appwrite-Key: $APW_API_KEY" \
  "$APW_ENDPOINT/databases" | jq .
# Expect: {"total":0, "databases":[]}

# 3. collection ready (after PR #3 wires memory_spine)
curl -fsS -H "X-Appwrite-Project: $APW_PROJECT" -H "X-Appwrite-Key: $APW_API_KEY" \
  "$APW_ENDPOINT/databases/sovereign_db/collections" | jq .
# Expect: {"total":≥1, "collections":[{ "id":"memory_spine", "$id":"memory_spine", ...}]}

# 4. Bifrost Bridge health untouched (Appwrite is downstream of Bifrost,
#    not the other way around). Re-run soul_oversight self-test:
.venv/Scripts/python.exe -m control_plane.soul_oversight --test
# Expect: "ALL PASS - soul_oversight"
```

## 8. Lessons Learned (Carried Forward to PR #2+)

- ALWAYS pin a server LTS + SDK compatible version (1.6.5 + `appwrite>=2.0,<3.0`).
- `_APP_REALTIME_HOST` MUST be a resolvable FQDN (not a bare hostname, not an IP) or
  the WebSocket handshake fails before any data is exchanged.
- Secrets belong in secrets management (Vault / age / sops), NOT in
  `.env.appwrite.example`. PR #1 keeps placeholders; a SECRETS_PR follow-on promotes
  them to a vault-backed store.
- Tailscale ACL for the Appwrite container is a separate concern (PR #3 optional).

## 9. Reversible

```bash
# All artefacts are git-tracked.
git log --oneline -- docker-compose.appwrite.yml .env.appwrite.example \
  bin/appwrite_bootstrap.sh docs/architecture/Appwrite_SelfHost_2026-07-14.md

# Soft roll-back (keeps the directory intact)
git revert -m 1 <PR1-SHA>

# Full teardown (irreversible — wipes data)
bin/appwrite_bootstrap.sh --teardown
# OR:  git reset --hard <SHA_BEFORE_PR1>
```

---

*End of deployment contract. Mirrors the 9-section Tier-N doc template so PR #3+
follow-on slots in clean.*
