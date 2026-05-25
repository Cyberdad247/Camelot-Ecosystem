# Camelot-OS Source Of Truth Map

Last reviewed: 2026-05-21
Repo root: `C:\Users\vizio\CAMELOT_OS`

## Purpose

This document defines which files are authoritative for the current Camelot-OS
runtime. It also records which older docs are mirrors, historical snapshots, or
broken references.

## Executive Summary

The repository currently contains multiple architecture eras in parallel.
Several older docs still reference files that do not exist in this checkout.
Do not treat those references as canonical.

Current engineering truth should come from executable runtime surfaces first,
then from the config files they load, then from verification artifacts.

## Current Canonical Order

When files disagree, use this precedence:

1. Executable runtime code under `control_plane/` and `bin/`
2. Runtime bridge and operator config loaded by that code
3. Verification artifacts that prove the runtime behavior
4. Maintained architecture docs aligned to the live repo
5. Historical mirrors, notebook pulls, and archived architecture narratives

## Tier 1: Executable Runtime Sources

### 1. Boot contract

File: [control_plane/boot_sequence.py](C:/Users/vizio/CAMELOT_OS/control_plane/boot_sequence.py:845)

Why it is canonical:

- Defines the current boot phases through `run_boot(...)`
- Confirms the required surfaces the system expects to start
- Includes the current optional runtime surfaces such as `Cloud Brain  Auth`,
  `Vizion Telemetry`, and `Sovereign Harness`

Current live phase anchors include:

- `CLIProxyAPI   :8080`
- `Defense Grid`
- `Kinetic Edge  :3001`
- `Morgana Bridge :8001`
- `Cloud Brain  Auth`
- `Vizion Telemetry`
- `Sovereign Harness`

### 2. User boot entrypoint

File: [bin/awaken.py](C:/Users/vizio/CAMELOT_OS/bin/awaken.py:1)

Why it is canonical:

- It is the direct operator-facing bootstrap command
- It wraps `control_plane.boot_sequence`
- It defines the current `awaken` behavior and user-visible boot framing

### 3. Runic command surface

File: [control_plane/runic_router.py](C:/Users/vizio/CAMELOT_OS/control_plane/runic_router.py:1)

Why it is canonical:

- It defines the live rune routing tables
- It is the source of truth for current `//...` and `Omega_...` dispatch names
- It reflects the actual command vocabulary supported by this repo

### 4. Cloud and NotebookLM routing

File: [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:1)

Why it is canonical:

- It defines the typed cloud service router used by the current control plane
- It documents the current split between local and remote cloud surfaces
- It contains the deprecation note for `CAMELOT_CLOUDBRAIN_URL` as a notebook
  identity source

Operational note:

- This file imports long-term cloudbrain logic through
  `agora.cloud_orchestrator_shim`, not through a repo-root `cloud_orchestrator/`
  directory. Any doc that still claims `cloud_orchestrator/` is the active local
  canonical path is stale for this checkout.

### 5. NotebookLM bridge identity

File: [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:16)

Why it is canonical:

- Defines `CANONICAL_NOTEBOOK_ID`
- Defines `CANONICAL_NOTEBOOK_TITLE`
- Is imported by the live cloud services surface
- Is used for health, sync, synthesis, research, and snapshot generation

Current values in code:

- Notebook ID: `8c656cfa-a189-409e-a72d-07692a47f17e`
- Notebook title: `Camelot-OS v.999.3`

### 6. Operator config

File: [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)

Why it is canonical:

- Stores the active `living_notebook_url`
- Stores the current Excalibur bridge URLs
- Provides operator defaults used by the current CLI stack

Current configured notebook URL:

- `https://notebooklm.google.com/notebook/8c656cfa-a189-409e-a72d-07692a47f17e`

## Tier 2: Verification And Corroboration

### 7. Verification matrix

File: [verification.md](C:/Users/vizio/CAMELOT_OS/verification.md:1)

Why it matters:

- Captures the repeatable verification contract for the current repo
- Serves as the human-readable evidence checklist

### 8. Verification ledger

File: [03_VAULT/Missions/verification_ledger.jsonl](C:/Users/vizio/CAMELOT_OS/03_VAULT/Missions/verification_ledger.jsonl:1)

Why it matters:

- Records real verification runs
- Corroborates whether a claimed sync or validation step actually occurred

### 9. Ledger sync status

File: [logs/defense_grid/ledger_sync_status.json](C:/Users/vizio/CAMELOT_OS/logs/defense_grid/ledger_sync_status.json:1)

Why it matters:

- Provides the current machine-readable ledger sync surface used by the repo
- Is a stronger sync signal than narrative references inside old docs

## Tier 3: Maintained Architecture Docs

### 10. Canonical live map

File: [entiremap.md](C:/Users/vizio/CAMELOT_OS/entiremap.md:1)

Usage rule:

- This is the maintained architecture map for the live repo state
- The L7 mirror may exist for compatibility, but root `entiremap.md` is the
  canonical copy to update first

### 11. L7 compatibility mirror

File: [docs/SEPTEM_REGNA/L7_ETHEREAL/entiremap.md](C:/Users/vizio/CAMELOT_OS/docs/SEPTEM_REGNA/L7_ETHEREAL/entiremap.md:1)

Usage rule:

- Mirror only
- Must stay content-aligned with root `entiremap.md`
- Do not update this first

## Known Broken Or Stale References

The following references appear in older docs but are not valid canonical
anchors for this checkout:

- Root `OS_MANIFEST.md` does not exist
- Root `VERSION` does not exist
- Root `config.json` does not exist
- Repo-root `cloud_orchestrator/` does not exist
- `kinetic_edge/mcp_server/` does not exist under the current `kinetic_edge/`
  tree
- `02_FORGE/web/` does not exist as the active dashboard path

If a doc still uses any of those as current canonical anchors, treat that doc
as historical or stale until corrected.

## Current Live Surface Decisions

### Architecture identity

Use these files together:

- [bin/awaken.py](C:/Users/vizio/CAMELOT_OS/bin/awaken.py:1)
- [control_plane/boot_sequence.py](C:/Users/vizio/CAMELOT_OS/control_plane/boot_sequence.py:845)
- [control_plane/runic_router.py](C:/Users/vizio/CAMELOT_OS/control_plane/runic_router.py:1)
- [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:1)

### NotebookLM identity

Use these files together:

- [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:16)
- [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)

### Current dashboard surfaces

Use these paths:

- `02_FORGE/PORTAL_CORE/Anya_Dashboard`
- `02_FORGE/apps/omni-eye-dashboard`

Do not keep calling `02_FORGE/web/` the current dashboard root.

## Historical And Mirror Docs

These remain useful for context, but not as current truth:

- [docs/architecture/EMPIRE_MAP.md](C:/Users/vizio/CAMELOT_OS/docs/architecture/EMPIRE_MAP.md:1)
- [03_VAULT/training/configs/BOOTSTRAP.md](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/BOOTSTRAP.md:1)
- [docs/SEPTEM_REGNA/L7_ETHEREAL/OS_MANIFEST.md](C:/Users/vizio/CAMELOT_OS/docs/SEPTEM_REGNA/L7_ETHEREAL/OS_MANIFEST.md:1)
- older notebook-derived architecture notes under `docs/` and `03_VAULT/`

## Maintenance Rule

Before changing architecture docs:

1. Check the live runtime code and config first
2. Verify referenced paths actually exist in this checkout
3. Update root `entiremap.md` before any mirror copy
4. Treat missing-file references as a doc bug, not as architecture truth
