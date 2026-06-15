# Camelot-OS User Tutorial

> Historical tutorial warning:
> This guide contains older workflow and topology material.
> For current architecture truth use `docs/architecture/SOURCE_OF_TRUTH_MAP.md`
> and `entiremap.md` first.

**Version:** v300.5 — Universal Singularity
**Audience:** New operators of the Camelot-OS 3-tier system
**Updated:** 2026-04-13

---

## 1. What Camelot-OS Is

Camelot-OS is a split-brain, 3-tier personal compute stack built around three immutable zones:

```
┌─────────────────────────────────────────────────┐
│  edge   →  Kinetic Rust MCP, port 3001          │  Fast I/O, file ops
├─────────────────────────────────────────────────┤
│  local  →  Excalibur FastAPI, port 8001         │  Reasoning, control plane
├─────────────────────────────────────────────────┤
│  cloud  →  Modal morgana (on-demand)            │  Burst compute, research agency
└─────────────────────────────────────────────────┘
```

Everything runs under 11 **Titanium Laws** — hard constraints like the 8 GB RAM ceiling, Iron-Gate HITL approval for large changes, and the No-Docker rule (native binaries only on this host).

---

## 2. First-Time Setup (one time only)

You should already have these installed; verify in one shot:

```bash
.venv/Scripts/python.exe --version        # 3.13.x
.venv/Scripts/modal.exe --version         # 1.4.x
ls 02_FORGE/kinetic/bin/prometheus/prometheus.exe
ls 02_FORGE/kinetic/bin/grafana/bin/grafana-server.exe
ls bin/camelot-mcp-edge.exe
```

If any are missing:

- **Python venv** — `uv venv .venv && VIRTUAL_ENV=$PWD/.venv uv pip install modal pyyaml circuitbreaker structlog appwrite replicate google-generativeai fastapi uvicorn`
- **Modal auth** — `.venv/Scripts/modal.exe token set --token-id <id> --token-secret <secret>`
- **Edge binary** — use the current repo binary at `bin/camelot-mcp-edge.exe`
  and verify the live path from `entiremap.md`
- **Observability binaries** — see `monitoring/BINARIES_REQUIRED.md`

---

## 3. The Universal Tier Controller

One command to rule the three tiers:

```bash
python tier.py <edge|local|cloud|all> <up|down|status>
```

It reads **`config/tiers.yaml`**, the single source of truth. Edit that YAML and Claude Code, Gemini CLI, and Codex all pick up the change automatically — no per-engine hand-editing.

### 3.1 Common flows

**Daily start (edge + local, cloud stays off):**
```bash
python tier.py edge up
python tier.py local up
python tier.py all status
# → edge UP | local UP | cloud DOWN (on-demand)
```

**Burst into the cloud for a research job:**
```bash
python tier.py cloud up              # modal deploy morgana_core.py
curl https://cyberdad247--morgana-research-agency-prod-health.modal.run
python tier.py cloud down            # modal app stop  (Titanium Law: never leave cloud running idle)
```

**Cold shutdown:**
```bash
python tier.py cloud down
# edge/local: Ctrl+C in their windows, or taskkill /IM camelot-mcp-edge.exe /F && taskkill /IM python.exe /F
```

### 3.2 Editing tier configuration

Change a port, a Modal app name, or a Rust binary path? **Edit `config/tiers.yaml` and nothing else.** All engines read from it.

---

## 4. Health Checks

```bash
# Edge (TCP probe only — no HTTP /health on the Rust MCP binary)
powershell -NoProfile -Command "Test-NetConnection 127.0.0.1 -Port 3001"

# Local
curl http://127.0.0.1:8001/health
# → {"status":"ONLINE","identity":"Merlin_Omega","mode":"SIMULATION"}

# Cloud (only when deployed)
curl https://cyberdad247--morgana-research-agency-prod-health.modal.run
```

---

## 5. Security: MorganaVault + Cost Controller

Two Python modules gate everything:

### 5.1 MorganaVault — encrypted credential store

```python
from security import MorganaVault
v = MorganaVault()
v.set("openai_api_key", "sk-...")
v.get("openai_api_key")
v.list_credentials()
v.rotate_keys(confirm=True)   # backs up current key first, rolls back on failure
v.health()
```

- AES-256-GCM via `cryptography.AESGCM`
- Hardware-bound via Windows `MachineGuid` (PBKDF2-HMAC-SHA256, 480 000 iterations)
- Backups: `03_VAULT/.secure/key_backups/vault_master.key.<ts>.bak`

### 5.2 SmartCostController — spend gate

```python
from security import cost_gate

@cost_gate(estimated_usd=0.12, label="modal.morgana.invoke")
def run_research(prompt): ...
```

- Tiered caps: **$0.50/job · $10/hour · $50/day**
- Rolling-window JSONL ledger: `03_VAULT/.secure/cost_ledger.jsonl` (gitignored)
- Pre-check raises `BudgetExceeded` **before** the API call fires
- Commit on return

---

## 6. Observability (native, no Docker)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File monitoring/start_observability.ps1
```

- Refuses to start if available RAM < **1.5 GB** (Titanium Law VII)
- **Prometheus** → http://127.0.0.1:9090 (scrapes local:8001 and cloud bridge :9091)
- **Grafana** → http://127.0.0.1:3000

Scrape targets live in `monitoring/prometheus.yml`.

---

## 7. Titanium Laws (Never Break These)

1. Never write Python if a Rust/Go binary exists (Kinetic Purity)
2. Log file mods to `PROVENANCE_LEDGER.md` — **three copies must stay in sync**
3. `>10` net lines or `>50 MB` deletion → Iron Gate HITL approval required
4. `>3` reasoning steps → GoT/DoT structured decomposition
5. Check cartridges + context before guessing any API
6. Use `.aiexclude` patterns
7. **8 GB physical RAM ceiling, 7.8 GB usable**
8. Voice latency sub-second mandatory
9. Harmony Gate — conflict detection before assimilation or large refactor
10. BriefingScript — no code-gen on `>5` files without approved plan
11. Docker is outlawed on this host

---

## 8. Where Things Live

| Thing | Path |
|---|---|
| Universal tier config | `config/tiers.yaml` |
| Tier controller | `tier.py` |
| Edge binary | `bin/camelot-mcp-edge.exe` |
| Local entry point | `local_brain/main.py` (loads Excalibur kernel) |
| Cloud app | `02_FORGE/PORTAL_CORE/Modal/morgana/morgana_core.py` |
| Vault | `security/morgana_vault.py` (wraps `03_VAULT/vault_manager.py`) |
| Cost gate | `security/smart_cost_controller.py` |
| Observability launcher | `monitoring/start_observability.ps1` |
| Prometheus config | `monitoring/prometheus.yml` |
| Provenance ledger | `PROVENANCE_LEDGER.md` (+ 4 synced copies) |
| CLAUDE memory | `C:\Users\vizio\CLAUDE.md` |

---

## 9. Troubleshooting

**`modal deploy` dies with `charmap codec can't encode`**
Windows cp1252 can't render Modal's Unicode progress UI. Fix:
```bash
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 .venv/Scripts/modal.exe deploy ...
```

**`Secret not found` on Modal deploy**
The workspace uses `my-sovereign-secrets` (plural). Confirm with:
```bash
COLUMNS=200 .venv/Scripts/modal.exe secret list
```

**Local brain fails with `ModuleNotFoundError: No module named 'connectivity'`**
Excalibur's kernel subpackages must be on `sys.path`. `local_brain/main.py` already loops over the eight kernel dirs; if you moved them, update that loop.

**`No module named 'pip'` in the venv**
This venv was created by `uv`. Use `uv pip install <pkg>` with `VIRTUAL_ENV=$PWD/.venv` set, not `python -m pip`.

**Observability refuses to launch**
You have less than 1.5 GB RAM free. Close Chrome/Code and retry. The gate is intentional.

---

## 10. Cross-Engine Operation

All three AI engines see the same tier config:

| Engine | Shim file |
|---|---|
| Claude Code | `~/.claude/skills/camelot_tiers.md` |
| Gemini CLI | `~/.gemini/extensions/camelot-tiers/GEMINI.md` |
| Codex | `~/.codex/skills/camelot_tiers.md` |

Each shim is a 15-line pointer at `config/tiers.yaml` — zero duplication of ports, paths, or secret names. Edit the YAML once, every engine picks up the change.

---

## 11. Next Steps

- **Android Edge Scout** (Tier 2 mobile) is deferred — tooling install pending.
- **Polygon provenance contract** removed from plan.
- **`.modal.toml`** still holds plaintext tokens — rotate when convenient.

For deeper dives see:
- `docs/reference/COMMANDS.md` (80 runic commands)
- `docs/guides/HIVE_IDE_OMEGA_MANUAL.md`
- `03_VAULT/Knights/README.md` (52-agent roster)
