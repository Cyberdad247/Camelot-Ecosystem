# Camelot-OS Source Of Truth Map

Last reviewed: 2026-04-19
Repo root: `C:\Users\vizio\CAMELOT_OS`

## Purpose

This document separates current runtime truth from historical references,
generated artifacts, and stale narrative docs. Use it when determining which
files should drive engineering decisions for Cloud Brain, Living Camelot-OS,
and version identity.

## Executive Summary

Camelot-OS currently contains multiple version eras in parallel:

- `v300.1` historical notebook context
- `v300.4.0` manifest/bootstrap architecture docs
- `v400 / 400.1.0` active NotebookLM bridge and repo version marker

When files disagree, prefer executable runtime code over narrative docs, and
prefer persisted config over older prose.

## Canonical Priority Order

Use this precedence when sources conflict:

1. Executed runtime code in `control_plane/` and `cloud_orchestrator/`
2. Runtime bridge/config files that are imported or read by the CLI
3. Verification ledgers and repeatable tests that prove current behavior
4. Architecture docs that still match the code
5. Historical notebook pulls, training configs, and archived reports

## Tier 1: Canonical Runtime Sources

These files are the strongest sources of truth for the current system.

### 1. NotebookLM Cloud Brain identity

File: [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:14)

Why it is canonical:

- Defines `CANONICAL_NOTEBOOK_ID = "bcaadfdd-1654-487d-9c4c-111f7dea120e"`
- Defines `CANONICAL_NOTEBOOK_TITLE = "Living Camelot-OS v.400"`
- Is loaded dynamically by the active control plane sync path
- Is used for health, sync, synthesis, and research operations

Operational implication:

- This file currently overrides older references to `Living Camelot-OS`
  notebooks from the `v300.x` era.

### 2. Persisted operator config

File: [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)

Why it is canonical:

- Stores the active `cloudbrain_url`
- Points to the same notebook ID as the NotebookLM bridge
- Provides operator defaults used by the current CLI stack

Operational implication:

- If the bridge and config disagree in the future, treat that as a release
  blocker until reconciled.

### 3. Active cloudbrain runtime topology

File: [cloud_orchestrator/long_term_cloudbrain.py](C:/Users/vizio/CAMELOT_OS/cloud_orchestrator/long_term_cloudbrain.py:1)

Why it is canonical:

- Defines the local long-term cloudbrain service surface
- Wires Open Notebook runtime configuration
- Defines Appwrite memory bridge loading
- Is directly used by the current cloud service router

Operational implication:

- This file is the main source of truth for local cloudbrain architecture,
  readiness, and memory topology.

### 4. Active typed cloud routing

File: [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:1)

Why it is canonical:

- Routes `cloudbrain`, `research`, `northstar`, `blueprint`, and
  `precise-mode` requests
- Loads the NotebookLM bridge on demand
- Falls back to local services when remote URLs are absent

Operational implication:

- This is the best source for which service surfaces are actually supported
  by the current CLI.

### 5. Active user-facing command surface

File: [control_plane/camelot_cli.py](C:/Users/vizio/CAMELOT_OS/control_plane/camelot_cli.py:1)

Why it is canonical:

- Defines what the operator can invoke
- Shapes how typed results are rendered
- Represents the currently shipped command surface

Operational implication:

- If a narrative doc claims a command exists, but this CLI does not expose the
  path or typed output expectations, the doc is not authoritative.

## Tier 2: Canonical Corroboration Sources

These files are not the primary runtime source, but they strongly corroborate
the live implementation.

### 6. Current repo version

File: [VERSION](C:/Users/vizio/CAMELOT_OS/VERSION:1)

Current value:

- `400.1.0`

Interpretation:

- The repo has moved beyond the `v300.x` document set.
- Any document still presenting itself as the current system at `v300.x`
  should be treated as historical unless it is explicitly maintained.

### 7. Production verification matrix

File: [verification.md](C:/Users/vizio/CAMELOT_OS/verification.md:1)

Why it matters:

- Defines the current repeatable verification commands
- Explicitly includes `cloudbrain` health and JSON contract checks
- Describes the present production gate, not the original concept

### 8. Verification ledger

File: [03_VAULT/Missions/verification_ledger.jsonl](C:/Users/vizio/CAMELOT_OS/03_VAULT/Missions/verification_ledger.jsonl:1)

Why it matters:

- Records actual command results from the current control plane
- Confirms `cloudbrain status` and related health commands were executed
- Shows real payload shapes and current local fallback behavior

## Tier 3: Useful Architecture Docs

These are high-value documents, but they no longer define the full current
state on their own.

### 9. Current architecture manifest, but on an older version line

File: [OS_MANIFEST.md](C:/Users/vizio/CAMELOT_OS/OS_MANIFEST.md:1)

Strengths:

- Good high-level topology overview
- Accurately describes the split-brain architecture shape
- Correctly identifies `cloud_orchestrator/` as the cloudbrain surface

Weaknesses:

- Still labeled `v300.4.0`
- Does not reflect the active `VERSION` file value `400.1.0`
- Should not be used as the authoritative notebook identity source

Usage rule:

- Use for architecture orientation, not for exact current version or notebook
  identity.

## Tier 4: Historical Sources

These files are valuable for reconstructing prior system states, but not for
current source-of-truth decisions.

### 10. Bootstrap doc for the `v300.4.0` era

File: [03_VAULT/training/configs/BOOTSTRAP.md](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/BOOTSTRAP.md:1)

Historical signals:

- Describes boot phases and older runtime assumptions
- Names canonical notebook `a9cf586e-1971-4959-bb97-cdcd37257ebb`
- Titles that notebook as
  `living Camelot-OS: The v300.4.0 Universal Singularity Recompilation`

Conflict with current truth:

- Conflicts with the active bridge/config notebook ID
- Conflicts with `VERSION = 400.1.0`

Usage rule:

- Treat as a historical architecture record for the `v300.4.0` phase.

### 11. Historical notebook context pull

File: [notebook_context.md](C:/Users/vizio/CAMELOT_OS/notebook_context.md:1)

Historical signals:

- Explicitly dated `2026-03-26`
- References
  `living Camelot-OS: The v300.1 Universal Singularity Recompilation`

Usage rule:

- Treat as an imported historical notebook summary, not a live system spec.

### 12. Historical verification report

File: [docs/reports/verification_report_v300.4.md](C:/Users/vizio/CAMELOT_OS/docs/reports/verification_report_v300.4.md:1)

Historical signals:

- Generated on `2026-04-03`
- Tied to branch `reorg/v300.2-cleanup`
- Captures a point-in-time audit snapshot

Usage rule:

- Useful as evidence of prior readiness work, but not current runtime truth.

## Tier 5: Generated, Derived, Or Mirror Content

Use these only as supporting evidence after checking the tiers above.

- `docs/reports/*`
- `03_VAULT/Missions/*.jsonl`
- `03_VAULT/UKG/*`
- `03_VAULT/training/configs/memory/*`
- shell launchers such as `Camelot-OS.cmd`
- cached client histories under `.claude/` or `.gemini/`

These sources may be informative, but they are either generated, mirrored,
historical, or downstream from canonical runtime code.

## Current Source-Of-Truth Decisions

### Living Camelot-OS notebook identity

Current canonical source:

- [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:14)

Current canonical values:

- Notebook ID: `bcaadfdd-1654-487d-9c4c-111f7dea120e`
- Notebook title: `Living Camelot-OS v.400`

Historical notebook identities still present in docs:

- `v300.4.0`: `a9cf586e-1971-4959-bb97-cdcd37257ebb`
- `v300.1`: title-only reference in `notebook_context.md`

### Cloudbrain architecture

Current canonical sources:

- [cloud_orchestrator/long_term_cloudbrain.py](C:/Users/vizio/CAMELOT_OS/cloud_orchestrator/long_term_cloudbrain.py:1)
- [control_plane/cloud_services.py](C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:1)

Current architectural truth:

- Local cloudbrain uses Open Notebook + Appwrite bridge wiring
- Control plane exposes typed cloud service routes
- NotebookLM bridge is used for health, sync, synthesis, and research

### Product version identity

Current canonical source:

- [VERSION](C:/Users/vizio/CAMELOT_OS/VERSION:1)

Current canonical value:

- `400.1.0`

Conflicting narrative docs:

- [OS_MANIFEST.md](C:/Users/vizio/CAMELOT_OS/OS_MANIFEST.md:1) says `v300.4.0`
- [BOOTSTRAP.md](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/BOOTSTRAP.md:1) says `v300.5`
- [NOTICE.md](C:/Users/vizio/CAMELOT_OS/NOTICE.md:2) says `v300.0.0`

## Drift And Risk Register

### Drift 1: Version identity drift

Symptoms:

- Runtime says `400.1.0`
- Multiple core docs still say `v300.x`

Risk:

- Operators and agents may choose the wrong notebook, wrong boot path, or
  wrong compatibility assumptions.

### Drift 2: Notebook identity drift

Symptoms:

- Runtime bridge/config point to notebook `bcaadfdd...`
- Older bootstrap doc points to notebook `a9cf586e...`

Risk:

- Sync or planning operations may target the wrong notebook if an older doc is
  followed manually.

### Drift 3: Mixed canonical and training content

Symptoms:

- `03_VAULT/training/configs/` contains both live bridge code and historical
  narrative assets

Risk:

- Engineers may assume all files in that directory are equally current.

## Recommended Cleanup Order

1. Update [OS_MANIFEST.md](C:/Users/vizio/CAMELOT_OS/OS_MANIFEST.md:1) to either
   match `400.1.0` or mark itself as a `v300.4.0` historical manifest.
2. Update [03_VAULT/training/configs/BOOTSTRAP.md](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/BOOTSTRAP.md:1)
   to either reference the current notebook ID or add a historical banner.
3. Add explicit `historical snapshot` banners to
   [notebook_context.md](C:/Users/vizio/CAMELOT_OS/notebook_context.md:1) and
   [docs/reports/verification_report_v300.4.md](C:/Users/vizio/CAMELOT_OS/docs/reports/verification_report_v300.4.md:1).
4. Keep notebook identity defined in exactly one code path:
   [03_VAULT/training/configs/notebooklm_bridge.py](C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs/notebooklm_bridge.py:14).
5. Keep operator-facing notebook URL config in exactly one persisted file:
   [.camelot-config.yaml](C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1).

## Short Decision Rule

If the question is:

- "What notebook is current?" use `notebooklm_bridge.py`
- "What URL/profile is the operator using?" use `.camelot-config.yaml`
- "What does the cloudbrain actually do?" use `long_term_cloudbrain.py` and
  `cloud_services.py`
- "What can the operator run?" use `camelot_cli.py`
- "What did the older v300 system say?" use `BOOTSTRAP.md` and
  `notebook_context.md`
