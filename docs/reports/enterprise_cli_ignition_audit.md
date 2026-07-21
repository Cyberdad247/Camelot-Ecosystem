# Camelot Enterprise CLI Ignition Audit

- status: `ENTERPRISE_READY`
- generated_utc: `2026-07-10T06:29:14.127269+00:00`
- repo_root: `C:\Users\vizio\CAMELOT_OS`

## Layer Status

| Layer | Status | Primary Action |
|---|---:|---|
| `chat_interface` | `READY` | `camelot chat` |
| `ui_dashboard` | `READY` | `cd 02_FORGE/PORTAL_CORE/Anya_Dashboard; npm run dev` |
| `bifrost_bridge` | `READY` | `python -m control_plane.bifrost_gateway health` |
| `cloudbrain_mnemosyne` | `READY` | `python -m control_plane.camelot_cli cloudbrain mnemosyne-audit` |
| `local_first_inference` | `READY` | `ollama list` |
| `ledger_provenance` | `READY` | `python -m control_plane.camelot_cli ledger reconcile` |

## Operator Commands

- `camelot ignite`
- `camelot doctor`
- `camelot chat`
- `camelot cockpit refresh --json`
- `python -m control_plane.camelot_cli cloudbrain sync`

## Degraded Layers

- none
