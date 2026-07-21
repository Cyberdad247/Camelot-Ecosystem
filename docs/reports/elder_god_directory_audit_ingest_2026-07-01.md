# Elder God Directory Audit Ingest - 2026-07-01

Scope: `C:\Users\vizio\CAMELOT_OS`

Mode: `//INGEST_DIRECTORY` interpreted as a non-mutating directory ingest and Iron Gate briefing. No deletes, moves, merges, ledger edits, or source edits were performed.

## Execution Summary

| Surface | Result | Evidence |
|---|---:|---|
| Camelot skill loaded | PASS | `C:\Users\vizio\.agents\skills\camelot-os\SKILL.md` confirms runic routing, Squire Colony, and HITL constraints. |
| Runic route detection | PASS | `python -m control_plane.runic_router --detect '//SCAN .'` routed to `squire_colony` with task id `rune-ae96fbff`. |
| Python Squire scan | TIMEOUT | `python -m squires.colony scan .` exceeded 120 seconds. |
| Python Squire index | TIMEOUT | `python -m squires.colony index .` exceeded 120 seconds. |
| Rust Squire scan | TIMEOUT | `04_KINETIC\squires_rs\target\release\squires_rs.exe scan .` exceeded 120 seconds. |
| Compressed top-level metrics | PASS | PowerShell file-count/size sweep completed with generated/cache exclusions. |
| Prior semantic index seed | FOUND | `.colony/index.json`, 17.0 MB, reports 19,885 files, 71,099 symbols, and 4,786,847 lines from a previous index run. |
| Latest saved system triage | FOUND | `03_VAULT/runtime_state/system_triage/latest.md` reports GREEN from `2026-06-26T16:22:30.456006+00:00`; this is not treated as current validation. |

## Current Ingest Facts

The current worktree is not clean. `git status --short` returned 134 changed/untracked status rows. `git ls-files -o --exclude-standard` returned 254 untracked files. This must be treated as a live mutation surface, not a stable release baseline.

Tracked files: 3,226.

Top tracked directories:

| Directory | Tracked files |
|---|---:|
| `01_KERNEL` | 833 |
| `03_VAULT` | 771 |
| `02_FORGE` | 660 |
| `docs` | 216 |
| `control_plane` | 174 |
| `kinetic_edge` | 99 |
| `tests` | 54 |
| `scripts` | 54 |
| `bin` | 38 |
| `.camelot` | 32 |

Top untracked directories:

| Directory | Untracked files |
|---|---:|
| `data` | 85 |
| `tests` | 36 |
| `03_VAULT` | 32 |
| `02_FORGE` | 21 |
| `.camelot` | 16 |
| `extensions` | 9 |
| `scripts` | 9 |
| `control_plane` | 8 |
| `01_KERNEL` | 6 |

## Size Hotspots

Compressed top-level scan excluding `.git`, `node_modules`, `target`, `.venv`, `data`, `build`, `dist`, `__pycache__`, `.ruff_cache`, and `.cargo`:

| Directory | Files | Approx MB |
|---|---:|---:|
| `02_FORGE` | 246,911 | 8,675.78 |
| `03_VAULT` | 47,258 | 2,808.10 |
| `kinetic_edge` | 7,704 | 2,484.56 |
| `audit-kickbox-audio` | 146,862 | 1,771.11 |
| `.worktrees` | 24,580 | 791.92 |
| `control_plane` | 1,952 | 642.35 |
| `logs` | 4,436 | 550.66 |
| `apps` | 2,155 | 228.02 |
| `01_KERNEL` | 3,209 | 141.80 |
| `bin` | 69 | 132.93 |
| `04_KINETIC` | 514 | 126.64 |

Primary conclusion: the audit cannot be production-safe if it scans the entire tree as one flat unit. The repo needs tiered scan policy: source first, generated/vendor/archive surfaces second, caches last or excluded.

## Duplicate/Fragmentation Signals

Duplicate basename counts from tracked files:

| Basename | Count | Interpretation |
|---|---:|---|
| `__init__.py` | 67 | Normal Python package spread; not mergeable by name alone. |
| `Cargo.toml` | 27 | Many Rust crates/workspaces; needs workspace ownership map before any merge. |
| `README.md` | 26 | Likely project/module docs; not mergeable by name alone. |
| `package.json` | 22 | Many JS/TS apps/packages; requires package role classification. |
| `.gitignore` | 20 | Potential consolidation candidate only if nested package rules are redundant. |
| `Cargo.lock` | 19 | Strong fragmentation signal; consolidate only after mapping independent Rust apps/crates. |
| `manifest.json` | 19 | Needs schema classification. |
| `package-lock.json` | 11 | Strong Node dependency duplication signal; package-manager policy needed. |
| `sir_codex_directory_purge_report.json` | 10 | Audit artifact duplication signal; candidate for archive consolidation. |
| `sir_codex_scorpion_review.md` | 10 | Audit artifact duplication signal; candidate for archive consolidation. |

## Production Gap Map

P0 blockers before any automated purge/merge:

| Blocker | Why it matters | Required gate |
|---|---|---|
| Full-tree scan timeouts | Native and Python scanners exceeded 120 seconds. | Add bounded scan profiles and hard excludes for generated/cached/vendor surfaces. |
| Dirty worktree | 134 status rows and 254 untracked files make attribution unsafe. | Snapshot current state and classify user changes before mutation. |
| Massive generated surfaces | `02_FORGE`, `03_VAULT`, `audit-kickbox-audio`, and `.worktrees` dominate scan cost. | Mark generated/archive/worktree roots as separate audit lanes. |
| Duplicate dependency manifests | Many lockfiles and package manifests may be valid but increase operational ambiguity. | Build a package ownership DAG before consolidation. |
| Stale green triage | Latest GREEN triage is from 2026-06-26, not current. | Rerun rapid triage after scan policy is bounded. |

P1 cleanup candidates:

| Candidate | Proposed action |
|---|---|
| Repeated Sir Codex purge reports | Consolidate into `03_VAULT/runtime_state/sir_codex_directory_purge/` index plus archive manifest. |
| Root-level phase/completion reports | Move historical non-operational status reports into dated `docs/archive/` buckets after link checks. |
| Multiple package lockfiles | Keep per active app; archive stale prototype lockfiles only after package map proves inactivity. |
| `.worktrees` inside repo root | Exclude from routine scans; keep if intentionally used for feature work. |
| `audit-kickbox-audio` | Treat as isolated audit lane, not default Camelot core scope. |

## Recommended Bounded Audit DAG

```yaml
directory_audit_dag:
  root: C:\Users\vizio\CAMELOT_OS
  mode: non_mutating
  lanes:
    - id: source_core
      include:
        - control_plane
        - squires
        - bin
        - scripts
        - tests
        - 01_KERNEL
      exclude:
        - "**/__pycache__/**"
        - "**/.ruff_cache/**"
      gate: run first
    - id: forge_apps
      include:
        - 02_FORGE
        - apps
        - dashboards
      exclude:
        - "**/node_modules/**"
        - "**/.next/**"
        - "**/dist/**"
        - "**/build/**"
      gate: package map required
    - id: vault_runtime
      include:
        - 03_VAULT
      exclude:
        - "03_VAULT/runtime_state/backups/**"
        - "03_VAULT/runtime_state/assimilation_7/**"
      gate: ledger-safe read-only
    - id: archive_and_worktrees
      include:
        - 99_ARCHIVE
        - 99_HISTORY
        - .worktrees
        - audit-kickbox-audio
      gate: report-only, excluded from default triage
```

## Iron Gate

Mutation is halted. The next safe command is not purge or merge; it is bounded validation:

```powershell
cd C:\Users\vizio\CAMELOT_OS
.\.venv\Scripts\python.exe -m control_plane.camelot_cli triage --rapid --json --timeout 300
```

Only after rapid triage is current should the next phase generate a concrete mutation proposal with file-by-file actions and rollback paths.

Awaiting explicit `//GO` for a bounded Scorpion Sting plan, or `//REZERO` to abort.
