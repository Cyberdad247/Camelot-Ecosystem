# Multi-Branch Consolidation — Task DAG (mbc-v1)

| Metric | Count |
| :--- | :--- |
| Total Tasks | 24 |
| Critical Path (P0) | 9 |

## Phase C0: DISCOVERY
- [ ] **C0-T01** [P0] (SIR_BORIS) Size: S - `git fetch --all --prune`; enumerate all heads (93 remote + 12 local); record ahead/behind vs `main`.
  - *Criteria*: `git for-each-ref` count + per-branch `rev-list --left-right --count main...<ref>` written to evidence JSON.
- [ ] **C0-T02** [P0] (SIR_BORIS) Size: S - Dedupe: mark heads already merged into `main` (`git branch -r --merged main`); drop merged/obsolete heads from the candidate set.
  - *Criteria*: Candidate list excludes every merged head; count recorded.
- [ ] **C0-T03** [P0] (SIR_BORIS) Size: M - Per-branch diffstat vs `main` (`git diff --shortstat main...<ref>` + `--name-only`), ref-only (no checkout).
  - *Criteria*: Diffstat + changed-file list per candidate branch in hydration scratch.
- [ ] **C0-T04** [P0] (SIR_SENTINEL) Size: M - Secret gate part 1: `squires.colony ghost` per candidate tip (worktree-less: `git grep` pattern sweep over `git ls-tree -r <ref>` for `secret|token|key|password|sk-ant|AKIA|PRIVATE KEY`), risk-score table.
  - *Criteria*: Every candidate has a CLEAN/RISK flag; any RISK branch quarantined to SIR_GHOST, excluded from porting until adjudicated.
- [ ] **C0-T05** [P1] (SIR_BORIS) Size: S - Classify scope: group candidates by subsystem (control_plane, apps/*, packages/*, 01_KERNEL, etc.) for the component contest.
  - *Criteria*: Every candidate mapped to ≥1 subsystem.

## Phase C1: HYDRATE (component contest)
- [ ] **C1-T01** [P0] (LADY_MNEMOSYNE) Size: M, Deps: [C0-T03] - Read key files per subsystem-contending branch (`server.*`, `runic_router.py`, `state.*`, `security.*`, `package.json`, `pyproject.toml`, `tailwind.config.*`, tests) via `git show <ref>:<path>` — no checkout.
  - *Criteria*: Key-file contents captured for every contending branch.
- [ ] **C1-T02** [P0] (SIR_BORIS) Size: M, Deps: [C1-T01] - Score matrix per contending branch: architecture / security / features / tests / docs (1-10); pick **winner per subsystem** + explicit PORT-only / SKIP verdicts.
  - *Criteria*: Winner map covers every subsystem with ≥2 contenders; single winner each; verdict rationale recorded.
- [ ] **C1-T03** [P0] (LADY_MNEMOSYNE) Size: S, Deps: [C1-T02] - Write `03_VAULT/runtime_state/consolidation/<run>/hydration.json`: heads, diffstats, ghost flags, scores, winner map, timestamps.
  - *Criteria*: `python -c "import json; json.load(open(...))"` passes; every candidate represented.
- [ ] **C1-T04** [P0] (SIR_FORGE) Size: M, Deps: [C1-T02] - Baseline capture on `main` worktree: canonical pytest sample, `npm run lint`, `npm run typecheck`, `cargo check` → `evidence/c1_baseline.json` with pass/fail + durations.
  - *Criteria*: Baseline JSON exists with recorded results; any pre-existing failure noted as inherited (not caused by consolidation).

## Phase C2: ISOLATE
- [ ] **C2-T01** [P0] (SIR_BORIS) Size: S, Deps: [C1-T03] - Create worktrees ONLY for `main` (base) + winner branches actually being ported (≤6): `git worktree add .worktrees/consolidation/<short-name> <ref>`.
  - *Criteria*: `git worktree list` shows base + port candidates; total ≤6; 8GB free-memory check recorded.
- [ ] **C2-T02** [P2] (SIR_FORGE) Size: S - Platform note row: libkrun microVM isolation = `planned`, blocked win32 (WSL2+KVM target), `forkd_runner.sh` fallback — never marked `rejected`.
  - *Criteria*: Verification matrix contains the platform-note row.

## Phase C3: PORT/PATCH
- [ ] **C3-T01** [P0] (SIR_CODEX) Size: M, Deps: [C2-T01] - Create `feat/unified-v1000` from `main`; port winning files per subsystem: `git checkout <winner-ref> -- <path>` (path-level, never whole-branch merge).
  - *Criteria*: `git status` on `feat/unified-v1000` shows exactly the winner-map paths staged; no unlisted files.
- [ ] **C3-T02** [P0] (SIR_CODEX) Size: M, Deps: [C3-T01] - AST conflict classifier: for each ported file changed on both sides, Python `ast.parse` (py) / text-diff (ts/rs) classifies RENAME vs LOGIC vs DOCS conflict → `conflict_report.json`.
  - *Criteria*: Every overlapping file classified; LOGIC conflicts flagged for manual resolution.
- [ ] **C3-T03** [P0] (SIR_CODEX) Size: M, Deps: [C3-T02] - Resolve flagged conflicts; each resolution passed through `control_plane.infra.z3_verify.verify_patch(PatchIntent(description, diff))` — any `Z3_BLOCK` halts the port.
  - *Criteria*: Every resolution patch has a `Z3_PASS` receipt in evidence; zero `Z3_BLOCK` at end of phase.
- [ ] **C3-T04** [P0] (SIR_GHOST) Size: M, Deps: [C3-T01] - Secret gate part 2: `squires.colony ghost` + `squires.colony triage` across the staged unified tree (CAMELOT_NON_INTERACTIVE=true).
  - *Criteria*: No REAL secrets; triage risk <50; false positives documented.
- [ ] **C3-T05** [P1] (MERLIN_Ω) Size: S, Deps: [C3-T03, C3-T04] - Commit staged port on `feat/unified-v1000` (local only, no push).
  - *Criteria*: `git log -1` on `feat/unified-v1000` shows the port commit; `git status` clean.

## Phase C4: VERIFY
- [ ] **C4-T01** [P0] (PALADIN_OCTEM) Size: S, Deps: [C3-T05] - Z3 invariants on the full consolidation diff: `verify_patch(PatchIntent("consolidate branches", diff=git diff main...feat/unified-v1000))` → `Z3_PASS`.
  - *Criteria*: Verdict `Z3_PASS`, violated list empty; receipt archived.
- [ ] **C4-T02** [P0] (PALADIN_OCTEM) Size: M, Deps: [C3-T05] - PDG taint rules on cross-branch data flows: kinetic_edge `pdg_evaluate` rule set (untrusted→shell/network/write/settlement sinks, path traversal) applied to ported code paths.
  - *Criteria*: Zero PDG BLOCK verdicts on ported paths; findings archived.
- [ ] **C4-T03** [P0] (SIR_FORGE) Size: XL, Deps: [C3-T05] - Regression battery (sequential, one worktree): canonical pytest paths (`.venv\Scripts\python.exe -m pytest tests 03_VAULT/training/configs/tests`), `npm run lint`, `npm run typecheck`, scoped `npm run test`, `npm run build`, `cargo check; cargo test`, `python bin/awaken.py --status --json`.
  - *Criteria*: Compare vs `c1_baseline.json` — zero NEW failures; all pre-existing failures unchanged (inherited); full log archived.
- [ ] **C4-T04** [P1] (SIR_SENTINEL) Size: S, Deps: [C4-T01, C4-T02, C4-T03] - Gate verdict: write `evidence/c4_gate.json` with `gate_recommendation: PASS|BLOCK`, reviewer SIR_SENTINEL.
  - *Criteria*: PASS only if C4-T01/02/03 all green vs baselines; BLOCK escalates to PIV loop (max 3) then HUMAN_GATE.

## Phase C5: SEAL
- [ ] **C5-T01** [P0] (ANYA_Ω) Size: S, Deps: [C4-T04] - **HITL HUMAN_GATE checkpoint**: present gate verdict + diffstat to operator; explicit approval required (never auto-approved).
  - *Criteria*: Operator approval recorded in evidence before any commit.
- [ ] **C5-T02** [P0] (ANYA_Ω) Size: S, Deps: [C5-T01] - Confirm commit lands on `feat/unified-v1000` ONLY (no push, no `main` merge — trunk merge requires separate explicit operator directive).
  - *Criteria*: `git status`/`git log`/`git branch` round-trip proves local branch, origin untouched.
- [ ] **C5-T03** [P0] (ANYA_Ω) Size: S, Deps: [C5-T02] - Provenance: let `provenance-mirror-sync` hook write the entry; verify all 4 mirrors by `grep` (NEVER hand-edit).
  - *Criteria*: All 4 mirrors show the entry; append-only (no prior entries modified).
- [ ] **C5-T04** [P1] (SIR_BORIS) Size: S, Deps: [C5-T03] - Prune consolidation worktrees; archive evidence JSONs; final `git worktree list` + `git status` round-trip.
  - *Criteria*: Worktrees removed; evidence directory complete; worktree list back to pre-run state.

## Phase C6: FOLLOW-UP (deferred)
- [ ] **C6-T01** [P2] (SIR_FORGE) Size: L - Register first-class capability: `control_plane/runers/multi_branch_consolidation_runner.py` + `//MERGE_TRUNK` rune in `runic_router` (pattern: `marketing_assimilation_runner.py`), HUMAN_GATE-registered.
  - *Criteria*: `python -m control_plane.runes.runic_router --rune //MERGE_TRUNK --task "..."` dispatches; `--list` shows it.
