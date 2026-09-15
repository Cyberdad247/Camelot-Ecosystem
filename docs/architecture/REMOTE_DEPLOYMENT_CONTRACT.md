# 🏛️ Camelot-OS Remote Deployment Contract Specification

**Schema:** `camelot.deployment-contract/v1`  
**Authority:** SEPTEM_REGNA L7 Ethereal Track B Task **B4**  
**Classification:** Operational Infrastructure Specification  
**Governing Laws:** Anya Law, Rule 7 Hotpath Doctrine, Camelot Privacy Rule  

---

## 1. Overview & Objective

This document formalizes the canonical **Remote Deployment Contract** for **Camelot-OS**. It defines the required and optional environment variables, URI schemes, port surfaces, secret masking rules, and fail-soft fallback semantics across three primary operational subsystems:

1. **Modal Cloudbrain Workload Endpoints**: Serverless cloud infrastructure hosting heavy AI agent workflows (Research Agency, Northstar War Room, Development Blueprint Generator, Precise Mode Browser Swarm, and ElderGod Forge).
2. **Appwrite Memory Spine**: Long-term state and memory retention tier for Lady Mnemosyne and Bifrost Bridge.
3. **Excalibur Mobile & Cloud Telemetry Bridge**: Samsung Galaxy S26 Ultra kinetic command center and remote VPS telemetry link.

---

## 2. Environment Variables Specification

All configuration is managed through `.camelot-config.yaml` or `.env` and hydrated via [`ConfigManager`](file:///C:/Users/vizio/CAMELOT_OS/control_plane/infra/config_manager.py).

### 2.1 Modal Cloudbrain Action Endpoints

| Variable | Target Service | Default / Pattern | Required? | Fallback Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `CAMELOT_RESEARCH_AGENCY_URL` | LADY_APIS Research | `https://<org>--<app>-research-agency.modal.run` | Required if no local Modal | Local `modal` package or in-process stub |
| `CAMELOT_NORTHSTAR_URL` | Northstar War Room | `https://<org>--<app>-northstar-war-room.modal.run` | Required if no local Modal | Local `modal` package or in-process stub |
| `CAMELOT_BLUEPRINT_URL` | Development Blueprint | `https://<org>--<app>-development-blueprint.modal.run` | Required if no local Modal | Local `modal` package or in-process stub |
| `CAMELOT_PRECISE_MODE_URL` | Precise Browser Swarm | `https://<org>--<app>-precise-mode.modal.run` | Required if no local Modal | Local `modal` package or in-process stub |
| `CAMELOT_ELDERGOD_URL` | ElderGod Forge | `https://<org>--<app>-eldergod-forge.modal.run` | Optional (Extended) | Local `modal` package or in-process stub |

### 2.2 Modal Health Endpoints

| Variable | Probe Target | Pattern | Required? | Fallback Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `CAMELOT_RESEARCH_AGENCY_HEALTH_URL` | Research Agency Health | `https://<org>--<app>-research-agency-health-endpoint.modal.run` | Optional | Probes Excalibur health or local state |
| `CAMELOT_NORTHSTAR_HEALTH_URL` | Northstar War Room Health | `https://<org>--<app>-northstar-health-endpoint.modal.run` | Optional | Probes Excalibur health or local state |
| `CAMELOT_BLUEPRINT_HEALTH_URL` | Blueprint Generator Health | `https://<org>--<app>-development-blueprint-health-endpoint.modal.run` | Optional | Probes Excalibur health or local state |
| `CAMELOT_PRECISE_MODE_HEALTH_URL` | Precise Mode Swarm Health | `https://<org>--<app>-precise-mode-health-endpoint.modal.run` | Optional | Probes Excalibur health or local state |
| `CAMELOT_ELDERGOD_HEALTH_URL` | ElderGod Forge Health | `https://<org>--<app>-eldergod-forge-health-endpoint.modal.run` | Optional | Probes Excalibur health or local state |

### 2.3 Appwrite Memory Spine

Per [`Appwrite_SelfHost_2026-07-14.md`](file:///C:/Users/vizio/CAMELOT_OS/docs/architecture/Appwrite_SelfHost_2026-07-14.md):

| Variable | Description | Example / Target | Required? | Fallback Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `APPWRITE_ENDPOINT_PUBLIC` | Public API URL for Appwrite | `https://appwrite.local/v1` | Optional | Local Open-Notebook SQLite / VFS |
| `APPWRITE_PROJECT` | Sovereign Database Project ID | `sovereign_db` | Conditional (req if endpoint set) | N/A |
| `APPWRITE_API_KEY` | Sovereign Secret Access Key | Rotated secret | Conditional (req if endpoint set) | Never serialized to logs/config |

### 2.4 Excalibur & Telemetry Bridge

| Variable | Description | Example / Target | Required? | Fallback Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `CAMELOT_EXCALIBUR_BRIDGE_URL` | VPS / Mobile Telemetry Dispatch | `http://100.118.224.52:8095/dispatch` | Optional | In-process local execution |
| `CAMELOT_EXCALIBUR_HEALTH_URL` | VPS / Mobile Heartbeat Probe | `http://100.118.224.52:8095/health` | Optional | In-process local status |
| `CAMELOT_LIVING_NOTEBOOK_URL` | Canonical Living Notebook Link | `https://notebooklm.google.com/notebook/...` | Optional | Local NotebookLM bridge default |

---

## 3. Privacy & Secrets Governance

In strict accordance with the **Camelot Privacy Rule**:
1. **No Raw Secrets in Configs**: `config.json` and `.camelot-config.yaml` store only boolean presence flags for sensitive keys (`secret`, `token`, `key`, `password`).
2. **Masked Diagnostics**: Programmatic validation and CLI output mask sensitive values (e.g. `<CONFIGURED: 64 chars>`).
3. **Air-Gapped Credentials**: Secrets requiring zero-cloud transit route strictly through `SIR_GHOST`.

---

## 4. Timeout, Retry, and Circuit Breaker Policies (Track B6)

All remote HTTP invocations executed by [`CloudServiceRouter`](file:///C:/Users/vizio/CAMELOT_OS/control_plane/infra/cloud_services.py) follow the typed [`CloudTimeoutPolicy`](file:///C:/Users/vizio/CAMELOT_OS/control_plane/infra/cloud_policy.py):

- **Connect Timeout**: `5.0s` (Fail-fast connection boundary).
- **Health Read Timeout**: `10.0s` (Lightweight heartbeat window).
- **Action Read Timeout**: `60.0s` (Deep reasoning / synthesis window).
- **Retry Mechanism**: Max 2 retries with exponential backoff (`0.5s * 2^attempt`) on transient network drops (`ConnectError`, `ConnectTimeout`, `ReadTimeout`) and HTTP status codes `502`, `503`, and `504`.
- **Circuit Breaker**: Trips to `OPEN` after 3 consecutive failures for a given endpoint, fast-failing subsequent requests for `30.0s` to protect the host from resource exhaustion under hardware scarcity.

---

## 5. Verification Command & Contract Validation

The deployment contract is programmatically verified using:

```bash
# Verify complete deployment contract and health rollup
camelot health

# Emit structured JSON report
camelot health --json

# Inspect cloud endpoint configuration
camelot cloudbrain config show
```

The programmatic validator lives in [`control_plane/infra/deployment_contract.py`](file:///C:/Users/vizio/CAMELOT_OS/control_plane/infra/deployment_contract.py).
