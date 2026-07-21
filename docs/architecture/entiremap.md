# CAMELOT-OS ENTIRE MAP

Last reviewed: 2026-06-29
Root: `C:\Users\vizio\CAMELOT_OS`
Status: live architecture map for the current checkout
Mirror: `docs/SEPTEM_REGNA/L7_ETHEREAL/entiremap.md`

## Scope

This file is the maintained architecture map for the live repository state. It
covers the meaningful source pillars and their real subdirectories. It is not a
file-by-file dump: vendored and generated trees (`.venv`, `node_modules`,
`target`, `dist`, `build`, `*.egg-info`, `__pycache__`, `.ruff_cache`,
`.pytest_cache`, `.worktrees`) are deliberately excluded. Every path listed
below was verified to exist in this checkout on the review date.

## Canonical inputs

The current map is derived from these live surfaces (all verified present):

- [bin/awaken.py](C:/Users/vizio/CAMELOT_OS/bin/awaken.py:1)
- [control_plane/boot_sequence.py](C:/Users/vizio/CAMELOT_OS/control_plane/infra/boot_sequence.py:845)
- [control_plane/runic_router.py](C:/Users/vizio/CAMELOT_OS/control_plane/runes/runic_router.py:1)
- [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/infra/cloud_services.py:1)
- [control_plane/go_router/main.go](C:/Users/vizio/CAMELOT_OS/control_plane/go_router/main.go:1)
- [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:16)
- [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)
- [docs/architecture/SOURCE_OF_TRUTH_MAP.md](C:/Users/vizio/CAMELOT_OS/docs/architecture/SOURCE_OF_TRUTH_MAP.md:1)

## Live identity

- NotebookLM notebook ID: `8c656cfa-a189-409e-a72d-07692a47f17e`
- NotebookLM notebook title in bridge code: `Camelot-OS v.999.3`
- NotebookLM URL in operator config:
  `https://notebooklm.google.com/notebook/8c656cfa-a189-409e-a72d-07692a47f17e`

## Top-level pillar layout

The repository is organized into five numbered pillars plus a control plane and
supporting trees:

| Pillar | Path | Role |
|---|---|---|
| Kernel | `01_KERNEL/` | core runtime, agora agent mesh, EXCALIBUR, forge, senses |
| Forge | `02_FORGE/` | applications, dashboards, cartridges, kinetic tooling |
| Vault | `03_VAULT/` | knowledge, knights, credentials, training, missions, ledgers |
| Kinetic | `04_KINETIC/` | Rust runic router + squires (`cmd/`, `squires_rs/`) |
| Infrastructure | `05_INFRASTRUCTURE/` | gateways, k8s/infra shims, morgana bridge |
| Control plane | `control_plane/` | boot, routers (py/go/rust), cluster, runners |

## Pillar detail

### 01_KERNEL — core runtime and agent mesh

- `agora/` — agent mesh: `agents/`, `knights/`, `squire/`, `Squires/`,
  `swarms/`, `fleet/`, `orchestration/`, `persona/`, `models/`, `prompts/`,
  `pkg/`, `cloud_orchestrator_shim/`
- `core/` — `aegis_shield/`, `mesh/`, `microvm_cages/`
- `EXCALIBUR/` — `BRIDGE/`, `core/`, `proxy/`, `schemas/`, `types/`,
  `kernel_api_bridge/`, `system/`, `shared/`, `config/`
- `forge/` — `assimilation/`, `cmd/`, `deployment/`, `diagnostics/`, `exp/`,
  `internal/`
- `senses/morgana_bridge` — bifrost bridge service source
- `config/`, `config_shim/`, `docs/plans/`

### 02_FORGE — applications and tooling

- `apps/` — `anya-lyte/`, `headartworks/`, `i2l-phygital/`, `lux11/`,
  `omni-eye-dashboard/` (secondary dashboard surface)
- `PORTAL_CORE/Anya_Dashboard` — main portal dashboard surface
- `holotable/` — Next.js surface (`app/`, `components/`, `lib/`, `public/`)
- `cartridge/` — `packages/`, `rustclaw/`
- `kinetic/` — `bin/`, `cribo/`, `hephaestus/`, `nano_knights/`, `pmcp/`,
  `rotel/`, `rustdesk-server/`
- `excalibur-dev/` — `core/`, `crates/`, `orchestrator/`
- `assimilation/voice_assistant_omega/`, `hive_api/`, `hooks/`, `generated/`,
  `dyad-apps/`, `_templates/`

### 03_VAULT — knowledge, knights, credentials

- `Knights/` — role guilds: `Creative/`, `Engineering/`, `Finance/`,
  `Governance/`, `Growth/`, `Kinetic/`, `Memory/`, `Monitoring/`, `Perception/`
- `training/configs/` — includes `notebooklm_bridge.py` (Cloud Brain bridge)
- `credentials/` — `.camelot/`, `.claude/`, `.gemini/`, `.mcp-auth/`,
  `config_mirror/`, `identity_mirror/` (sensitive — keep gitignored)
- `Missions/verification_ledger.jsonl` — proof of verification runs
- `firnflow/l3_cold/`, `GLYPHS/`, `kernels/`, `KINETIC_REFERENCES/`,
  `directives/`, `evidence/`, `CLOUD_SYNC/`, `bifrost_drop/`
- `00_SECURE_ARCHIVE/`, `00_TEMPLATES/`, `99_HISTORY/`, `99_SCRATCHPAD/`

### 04_KINETIC — Rust runic edge

- `cmd/runic_router/` — Rust runic router command
- `squires_rs/src/` — Rust squires implementation

### 05_INFRASTRUCTURE — gateways and shims

- `gateways/`, `infra_shim/caddy/`, `k8s_shim/`, `morgana_bridge/`

### control_plane — orchestration core

- `boot_sequence.py` — boot contract (`run_boot(...)`)
- `runic_router.py` — Python `//...` / `Omega_...` dispatch
- `cloud_services.py` — typed cloud / research / NotebookLM routing
- `go_router/` — Go router. `main.go` is both the one-shot rune CLI
  (`go_router <rune> <task>`) and an SSE daemon (`go_router serve [addr]`,
  default `:8077`) exposing `/healthz`, `/rune`, and `/events`
  (`active_knight` SSE stream for the 3D avatar hub)
- `rtk/src/`, `cluster/`, `runners/go/`, `runners/rust/`

## Supporting trees

- `bin/` — operator entrypoints: `awaken.py`, `knight_session.py`,
  `camelot-mcp-edge.exe`; `bin/redis/`
- `apps/bifrost/` — `src/`, `prisma/`, `public/`, `tests/`
- `kinetic_edge/` — `camelot_edge/src/`, `pqcrypto/src/`, `rotel/src/`,
  `saltare/` (Go service: `cmd/`, `internal/`, `pkg/`, `deployments/`,
  `docker/`, `docs/`, `tests/`), `swarm_spawner/src/`
- `observability/grafana/` — `dashboards/`, `provisioning/`
- `scripts/` — operator scripts incl. `governance/` and `inspect_fs.sh`
  (read-only filesystem audit)
- `docs/` — see Documentation map below
- `squires/`, `conductor/`, `dashboards/`, `terraform/`, `tests/`,
  `verification/`, `data/`, `logs/`

## Documentation map

- `docs/architecture/` — incl. `ARCH/`, `SOURCE_OF_TRUTH_MAP.md`
- `docs/SEPTEM_REGNA/` — layered architecture: `L1_SUBSTRATE/`, `L2_KINETIC/`,
  `L5_AGENTIC/`, `L6_GOVERNANCE/`, `L7_ETHEREAL/` (holds the entiremap mirror)
- `docs/protocols/` — `LAWS/`, `PERSONA/`
- `docs/reference/` — `ARTIFACTS/`, `INTEGRATIONS/`, `LEGAL/`, `MANIFESTS/`,
  `PROMPTS/`, `SPECS/`
- `docs/maestro/` (`plans/`, `state/`), `docs/plans/`, `docs/guides/`,
  `docs/diagrams/`, `docs/reports/`, `docs/catridges/`

## Boot architecture

The current boot contract is defined by `run_boot(...)` in
[control_plane/boot_sequence.py](C:/Users/vizio/CAMELOT_OS/control_plane/infra/boot_sequence.py:845).

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
[control_plane/runic_router.py](C:/Users/vizio/CAMELOT_OS/control_plane/runes/runic_router.py:1)
(Python) with a Rust counterpart under `04_KINETIC/cmd/runic_router/` and a Go
edge at `control_plane/go_router/`. The `//MALICIOUS` SAT-gate returns
`UNSATISFIED` across the CLI and the Go `/rune` endpoint.

## Cloud Brain architecture

The live Cloud Brain path is split across:

- NotebookLM short-term surface:
  [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:16)
- operator configuration:
  [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)
- typed router and local/remote fallback behavior:
  [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/infra/cloud_services.py:1)

Important current rule:

- `CAMELOT_CLOUDBRAIN_URL` is not the notebook identity source for the live
  NotebookLM surface. The bridge constants and the operator notebook URL are
  the canonical identity anchors.

## Dashboard architecture

The current repo does not use `02_FORGE/web/` as the live dashboard root.
Use these live surfaces instead:

- `02_FORGE/PORTAL_CORE/Anya_Dashboard`
- `02_FORGE/apps/omni-eye-dashboard`
- `02_FORGE/holotable` (Next.js)

## Kinetic and bridge architecture

The repo contains a `kinetic_edge` tree, but not the old
`kinetic_edge/mcp_server/` path referenced by older docs. The current live repo
also contains:

- `bin/camelot-mcp-edge.exe`
- `01_KERNEL/senses/morgana_bridge`
- `kinetic_edge/saltare` (Go edge service)

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

## Cleanup status (2026-06-29)

Malformed path-escaping artifacts at the repo root, audited and resolved:

- `CUsersvizioCAMELOT_OSPROVENANCE_LEDGER.md` — REMOVED (untracked 1527-byte
  stray; the canonical ledger is the tracked `PROVENANCE_LEDGER.md`, ~229 KB)
- `UsersvizioCAMELOT_OS.pytest_cache_cx/`, `UsersvizioCAMELOT_OS.pytest_tmp_cx/`
  — REMOVED (standard pytest cache/tmp junk)
- `.runtime_logssaltare.err.log`, `.runtime_logssaltare.out.log` — KEPT for now:
  locked by the live `saltare_gateway` process. Delete after the gateway stops;
  they are intended for `.runtime_logs/`.

## Maintenance rule

1. Check live code and config first
2. Verify the referenced paths exist
3. Update root `entiremap.md` first
4. Keep the L7 mirror content-aligned with this file
