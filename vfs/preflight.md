---
id: preflight
title: Swarm Init Manifest
context: "camelot-os.dev/ukg/v4000/vfs_master_scaffold"
type: Kinetic_Execution_Plane
---
# Swarm Init Manifest & Pre-Flight Folder Architecture
@ctx|camelot-os.dev/ukg/v10001/vfs_preflight id|Ω_VFS_PREFLIGHT_V10001

The key in the ignition. Governed by the **Mastering the AI File and Folder Agent System** (`876f30c4-efce-415d-8098-cad500de159c`).

## 1. Verified Ignition Checks (`vfs/checks/`)
All services and swarms must pass the 8-stage pre-flight catalog before strict-mode graduation:
1. `010_env_dependency_match`: Validates Python 3.13+, Rust 1.96+, Node 20+, and Ollama host availability.
2. `020_foss_validation_constraints`: Enforces SPDX-License-Identifier headers across slice-owned code.
3. `030_northstar_brief_currency`: Verifies currency of `BriefingScript.md` and architectural vision docs.
4. `040_port_readiness_scan`: Probes TCP socket health (:3000 PWA, :3001 Bifrost, :7680 Sonus, :8400 Octavian).
5. `050_provenance_ledger_writable`: Validates read-write integrity of `PROVENANCE_LEDGER.md` across all 4 mirrors.
6. `060_tool_registry_presence`: Asserts presence and integrity of all registered system tools.
7. `070_vfs_scaffold_integrity`: Confirms presence of mandatory VFS files (`preflight.md`, `systeminstructions.md`, `skills.md`, `rosters.md`, `protocols.md`).
8. `080_lattice_yaml_consistency`: Confirms consistency with `docs/architecture/lattice.yaml`.

## 2. Canonical Pre-Flight Folder Scaffolding
- `01_KERNEL/`: Reasoning engines, memory controllers, security kernels (Rust / WASM).
- `02_FORGE/`: Kinetic compilation, fabrication crates, and tooling pipelines.
- `03_VAULT/`: Immutable memory tissues, UKG crystals, training configurations, and encrypted credential storage.
- `04_KINETIC/`: Zero-hotpath native engines, WASM runtimes, and high-frequency edge execution.
- `vfs/`: Position-addressed virtual filesystem, pre-flight catalog probes, and NotebookLM sync tissues.
- `control_plane/`: Cognitive apex, orchestration, runic routers, and preflight ignition gates.
- `apps/`: Next.js 14 PWA shells, Bifrost mTLS bridge, and command cockpits.

## 3. AI File and Folder Agent Directives
- **Zero-Copy Streaming**: Never concatenate entire file trees into monolithic strings in memory; use streaming token-set intersections (`squires/sweep.py`).
- **Air-Gap Separation**: Test fixtures and documentation mock tokens are classified as `mock_secret` (severity `info`), isolating true credentials for `SIR_GHOST`.
- **AST Ceiling**: File size bounded at 2 MB for AST parsing; larger files are indexed by metadata without full text decode.
- **Directory Pruning**: Automatic in-place pruning of `.git`, `node_modules`, `.venv`, `KINETIC_ARMORY`, `99_ARCHIVE`, and generated caches.

