# CAMELOT-OS ENTIRE MAP

Last reviewed: 2026-05-23
Root: `C:\Users\vizio\CAMELOT_OS`
Status: live architecture map for the current checkout
Mirror: `docs/SEPTEM_REGNA/L7_ETHEREAL/entiremap.md`

## Scope

This file is the maintained architecture map for the live repository state.
It is not a historical narrative and it does not assume missing paths are still
canonical.

## Canonical inputs

The current map is derived from these live surfaces:

- [bin/awaken.py](C:/Users/vizio/CAMELOT_OS/bin/awaken.py:1)
- [control_plane/boot_sequence.py](C:/Users/vizio/CAMELOT_OS/control_plane/boot_sequence.py:845)
- [control_plane/runic_router.py](C:/Users/vizio/CAMELOT_OS/control_plane/runic_router.py:1)
- [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:1)
- [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:16)
- [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)
- [docs/architecture/SOURCE_OF_TRUTH_MAP.md](C:/Users/vizio/CAMELOT_OS/docs/architecture/SOURCE_OF_TRUTH_MAP.md:1)

## Live identity

- NotebookLM notebook ID: `8c656cfa-a189-409e-a72d-07692a47f17e`
- NotebookLM notebook title in bridge code: `Camelot-OS v.999.3`
- NotebookLM URL in operator config:
  `https://notebooklm.google.com/notebook/8c656cfa-a189-409e-a72d-07692a47f17e`

## Topology

| Surface | Live path | Role | Status |
|---|---|---|---|
| Boot entry | `bin/awaken.py` | operator bootstrap command | present |
| Boot contract | `control_plane/boot_sequence.py` | required and optional startup phases | present |
| Runic router | `control_plane/runic_router.py` | `//...` and `Omega_...` dispatch | present |
| Cloud services | `control_plane/cloud_services.py` | typed cloud, research, NotebookLM routing | present |
| NotebookLM bridge | `03_VAULT/training/configs/notebooklm_bridge.py` | Cloud Brain health, sync, synthesis | present |
| Operator config | `.camelot-config.yaml` | active notebook URL and bridge URLs | present |
| Dashboard A | `02_FORGE/PORTAL_CORE/Anya_Dashboard` | main portal dashboard surface | present |
| Dashboard B | `02_FORGE/apps/omni-eye-dashboard` | secondary dashboard surface | present |
| Morgana bridge | `01_KERNEL/senses/morgana_bridge` | bifrost bridge service source | present |
| Kinetic edge tree | `kinetic_edge` | kinetic binaries and related assets | present |
| Verification matrix | `verification.md` | manual verification contract | present |
| Verification ledger | `03_VAULT/Missions/verification_ledger.jsonl` | proof of verification runs | present |
| Ledger sync status | `logs/defense_grid/ledger_sync_status.json` | machine-readable sync state | present |

## Boot architecture

The current boot contract is defined by `run_boot(...)` in
[control_plane/boot_sequence.py](C:/Users/vizio/CAMELOT_OS/control_plane/boot_sequence.py:845).

### Required phases

- `CLIProxyAPI   :8080`
- `Defense Grid`
- `Kinetic Edge  :3001`
- `Morgana Bridge :8001`

### Optional phases currently wired in the boot sequence

- `Cloud Brain  Auth`
- `Vizion Telemetry`
- `Sovereign Harness`

## Command architecture

### Operator entrypoints

- `awaken` -> [bin/awaken.py](C:/Users/vizio/CAMELOT_OS/bin/awaken.py:1)
- `camelot` surfaces under `bin/` and `control_plane/`
- `ks` / knight session -> [bin/knight_session.py](C:/Users/vizio/CAMELOT_OS/bin/knight_session.py:1)

### Runic routing

Live rune routing is defined in
[control_plane/runic_router.py](C:/Users/vizio/CAMELOT_OS/control_plane/runic_router.py:1).
The current router includes the runic command table and Omega rune table used
by this checkout.

## Cloud Brain architecture

The live Cloud Brain path is split across:

- NotebookLM short-term surface:
  [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:16)
- operator configuration:
  [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)
- typed router and local/remote fallback behavior:
  [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:1)

Important current rule:

- `CAMELOT_CLOUDBRAIN_URL` is not the notebook identity source for the live
  NotebookLM surface. The bridge constants and the operator notebook URL are
  the canonical identity anchors.

## Dashboard architecture

The current repo does not use `02_FORGE/web/` as the live dashboard root.
Use these live surfaces instead:

- `02_FORGE/PORTAL_CORE/Anya_Dashboard`
- `02_FORGE/apps/omni-eye-dashboard`

## Kinetic and bridge architecture

The repo contains a `kinetic_edge` tree, but not the old
`kinetic_edge/mcp_server/` path referenced by older docs. The current live repo
also contains:

- `bin/camelot-mcp-edge.exe`
- `01_KERNEL/senses/morgana_bridge`

Docs should reference those existing surfaces instead of the removed nested
`mcp_server` path.

## Known stale anchors removed from the canonical map

Do not use these as current source-of-truth anchors for this checkout:

- root `OS_MANIFEST.md`
- root `VERSION`
- root `config.json`
- repo-root `cloud_orchestrator/`
- `kinetic_edge/mcp_server/`
- `02_FORGE/web/`

## Maintenance rule

1. Check live code and config first
2. Verify the referenced paths exist
3. Update root `entiremap.md` first
4. Keep the L7 mirror content-aligned with this file
