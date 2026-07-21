# Scorpion Sting Plan - 2026-07-01

Scope: `C:\Users\vizio\CAMELOT_OS`

Input authorization: `//GO`

Execution stance: bounded, evidence-first, no destructive mutation. This plan is the file-by-file mutation proposal required before purge, merge, or archive work. No deletion is approved by this document.

## Current Gate State

Current rapid triage command:

```powershell
.\.venv\Scripts\python.exe -m control_plane.camelot_cli triage --rapid --json --timeout 300
```

Result: `BLOCKED`

Generated artifacts:

- `03_VAULT/runtime_state/system_triage/triage_20260701T044034Z.json`
- `03_VAULT/runtime_state/system_triage/triage_20260701T044034Z.md`

Required blockers:

| Blocker | Status | Evidence | Action |
|---|---:|---|---|
| `provenance-ledger-alignment` | FAIL | Root ledger exists, all 3 mirror ledgers are not aligned. | Reconcile only after explicit approval because mirror files are already dirty. |
| `notebooklm-live` | UNVERIFIED | Triage reports expired/invalid NotebookLM auth. | Reauthenticate in an interactive terminal; this shell's `nlm login` hung for 120 seconds. |

Non-required warning:

| Warning | Status | Evidence | Action |
|---|---:|---|---|
| `cloudbrain-sync-queue` | WARN | 4 queued Cloud Brain events. | Inspect after NotebookLM auth is healthy; flush only after review. |

Positive validation:

- Source of truth present.
- Excalibur preflight verdict: `GO`.
- Required boot contract present.
- Bio-Swarm runtime ready.
- Targeted control-plane tests passed: `8 passed`.
- Rust kernel compile passed for Aegis and Ouroboros.
- Verification ledger chain valid: `630 entries`.
- Tracked-source read-only guard passed.

## Iron Gate Rule

Do not run purge, delete, move, or merge operations while either required blocker is active.

The only mutations allowed before blocker clearance are:

1. Generate reports under `docs/reports/`.
2. Reconcile provenance ledger mirrors if explicitly authorized.
3. Refresh NotebookLM auth in an interactive terminal.

## Gate 0 - Auth And Ledger Clearance

### 0.1 NotebookLM Reauth

Run from a real interactive terminal if this API shell hangs:

```powershell
cd C:\Users\vizio\CAMELOT_OS
nlm login
```

Then rerun:

```powershell
.\.venv\Scripts\python.exe -m control_plane.camelot_cli triage --rapid --json --timeout 300
```

Acceptance:

- `notebooklm-live` is `PASS`.

Rollback:

- No repo rollback; this changes local NotebookLM credentials only.

### 0.2 Provenance Ledger Mirror Reconcile

Current ledger status command:

```powershell
.\.venv\Scripts\python.exe -m control_plane.camelot_cli --json ledger status
```

Current evidence:

- `PROVENANCE_LEDGER.md`: exists, 279,772 bytes.
- `03_VAULT/PROVENANCE_LEDGER.md`: exists, not aligned.
- `03_VAULT/training/configs/PROVENANCE_LEDGER.md`: exists, not aligned.
- `docs/PROVENANCE_LEDGER.md`: exists, not aligned.

Proposed mutation command:

```powershell
.\.venv\Scripts\python.exe -m control_plane.camelot_cli --json ledger reconcile
```

Files expected to change:

- `03_VAULT/PROVENANCE_LEDGER.md`
- `03_VAULT/training/configs/PROVENANCE_LEDGER.md`
- `docs/PROVENANCE_LEDGER.md`

Acceptance:

```powershell
.\.venv\Scripts\python.exe -m control_plane.camelot_cli --json ledger status
.\.venv\Scripts\python.exe -m control_plane.camelot_cli triage --rapid --json --timeout 300
```

Required outcome:

- `mirrors_aligned: true`
- `provenance-ledger-alignment` is `PASS`.

Rollback:

```powershell
git diff -- 03_VAULT/PROVENANCE_LEDGER.md 03_VAULT/training/configs/PROVENANCE_LEDGER.md docs/PROVENANCE_LEDGER.md
```

If the reconcile copied unintended content, restore those three files from the pre-reconcile backup or from git only after explicit user approval.

## Gate 1 - Bounded Scan Policy

Problem: full-tree scans exceed the 120-second operational window because generated and audit-heavy surfaces dominate the tree.

Proposed scan lanes:

| Lane | Include | Exclude | Purpose |
|---|---|---|---|
| `core_runtime` | `control_plane`, `squires`, `bin`, `scripts`, `tests`, `01_KERNEL` | `**/__pycache__/**`, `**/.ruff_cache/**`, `**/target/**` | Validate executable Camelot core. |
| `forge_apps` | `02_FORGE`, `apps`, `dashboards` | `**/node_modules/**`, `**/.next/**`, `**/dist/**`, `**/build/**`, generated glyph folders | Validate active JS/TS apps without dependency trees. |
| `vault_ledgers` | `03_VAULT` | runtime backups, assimilation scratch folders, generated evidence blobs | Validate ledgers and canonical runtime state. |
| `archives` | `99_ARCHIVE`, `99_HISTORY`, `.worktrees`, `audit-kickbox-audio` | none | Report-only; excluded from default triage. |

Proposed artifact to add in the next implementation pass:

- `.camelot/audit_lanes.yaml`

Acceptance:

- Core lane completes under 120 seconds.
- Forge app lane completes under 120 seconds after generated/vendor excludes.
- Archive lane is never part of default rapid triage.

Rollback:

- Remove `.camelot/audit_lanes.yaml`.

## Gate 2 - Mutation Bundles

Each bundle must be executed independently. Do not combine bundles in one commit or one terminal session.

### Bundle A - Ledger Mirror Alignment

Type: low-risk required repair.

Action:

- Run `camelot ledger reconcile`.
- Inspect diff.
- Rerun rapid triage.

Files:

- `03_VAULT/PROVENANCE_LEDGER.md`
- `03_VAULT/training/configs/PROVENANCE_LEDGER.md`
- `docs/PROVENANCE_LEDGER.md`

Do not touch:

- `PROVENANCE_LEDGER.md`
- `03_VAULT/Missions/verification_ledger.jsonl`

### Bundle B - Audit Artifact Indexing

Type: safe organization, no deletion.

Problem files:

- `03_VAULT/runtime_state/sir_codex_directory_purge/*/sir_codex_directory_purge_report.json`
- `03_VAULT/runtime_state/sir_codex_directory_purge/*/sir_codex_scorpion_review.md`

Observed count:

- 10 `sir_codex_directory_purge_report.json`
- 10 `sir_codex_scorpion_review.md`

Proposed action:

- Add `03_VAULT/runtime_state/sir_codex_directory_purge/INDEX.md`.
- Record each audit folder, source scope, report path, and review path.
- Do not move or delete existing audit artifacts in this bundle.

Acceptance:

- Index lists all existing report/review pairs.
- No report JSON or review MD files removed.

Rollback:

- Delete only the new `INDEX.md`.

### Bundle C - Root Report Archive Proposal

Type: gated move-only cleanup.

Problem:

- Root contains many dated or phase-specific reports that make source-of-truth discovery noisy.

Candidate examples:

- `HIVE_BRIDGE_FINAL.md`
- `COMPLETE_DELIVERY_SUMMARY.md`
- `DISTANCE_TRAVEL_TEST_RESULTS.md`
- `EXECUTION_COMPLETE.md`
- `INFRASTRUCTURE_COMPLETE.md`
- `DEPLOYMENT_LIVE_2026-06-18.md`
- `PHASE_H_DAY2_COMPLETION.md`
- `PHASE_H_DAY3_COMPLETION.md`
- `PHASE_H_DAY4_COMPLETION.md`
- `PHASE_H_WEEK1_SIGNOFF.md`
- `PHASE_H_WEEK2_DAY1_COMPLETION.md`
- `PHASE_H_WEEK2_DAY2_COMPLETION.md`
- `PHASE_H_WEEK2_DAY3_COMPLETION.md`
- `PHASE_H_WEEK2_DAY4_COMPLETION.md`
- `PHASE_H_WEEK2_FINAL_SIGNOFF.md`
- `PHASE_H_WEEK3_DAY1_COMPLETION.md`

Proposed destination:

- `docs/archive/root_reports/`

Preconditions:

- `rg -n "<filename>" .` for each candidate to detect inbound links.
- If linked by live docs or code, leave in place and add a pointer instead.

Acceptance:

- No broken links from `README.md`, `AGENTS.md`, `docs/`, or `control_plane/`.
- Moved files are listed in `docs/archive/root_reports/INDEX.md`.

Rollback:

- Move files back to root using the index.

### Bundle D - Package Ownership Map

Type: analysis-only before dependency cleanup.

Problem:

- 22 tracked `package.json` files.
- 11 tracked `package-lock.json` files.
- 27 tracked `Cargo.toml` files.
- 19 tracked `Cargo.lock` files.

Proposed action:

- Add `docs/reports/package_ownership_map_2026-07-01.md`.
- Classify every package/crate as one of:
  - active runtime
  - active test fixture
  - generated artifact
  - vendored reference
  - archive candidate

No lockfile deletion is permitted until this map exists.

Acceptance:

- Every lockfile has an owner and verification command.
- Duplicate package surfaces are explained or assigned an archive candidate status.

Rollback:

- Delete only the new ownership map.

## Commands For Next Approval

If the user approves ledger reconcile:

```powershell
cd C:\Users\vizio\CAMELOT_OS
.\.venv\Scripts\python.exe -m control_plane.camelot_cli --json ledger reconcile
.\.venv\Scripts\python.exe -m control_plane.camelot_cli --json ledger status
.\.venv\Scripts\python.exe -m control_plane.camelot_cli triage --rapid --json --timeout 300
```

If the user approves analysis-only cleanup prep:

```powershell
cd C:\Users\vizio\CAMELOT_OS
git ls-files | rg "(package.json|package-lock.json|Cargo.toml|Cargo.lock)$"
git ls-files | rg "sir_codex_(directory_purge_report|scorpion_review)"
```

## Halt State

Scorpion Sting planning is complete. Execution remains halted for destructive or move operations.

Awaiting one of:

- `//GO ledger reconcile`
- `//GO audit index`
- `//GO package map`
- `//GO root archive proposal`
- `//REZERO`
