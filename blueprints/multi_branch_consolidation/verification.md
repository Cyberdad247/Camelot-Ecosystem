# Multi-Branch Consolidation — Verification & Acceptance Criteria (mbc-v1)

> **Document Version**: 1.0.0
> **Classification**: OPERATIONAL — SIR_SENTINEL reviewed
> **Date**: 2026-09-26
> **Owner**: SIR_BORIS (Architect) · SIR_SENTINEL / PALADIN_OCTEM (Verification Gates)

---

## 1. Verification Philosophy

### 1.1 Core Principles

| Principle | Enforcement |
|---|---|
| **Evidence-Grounded** | Every claim has a reproducible CLI command producing verifiable output. No aspirational assertions accepted as passing. |
| **Three-Tier Testing** | Unit → Integration → System. No phase gate opens without all three tiers green at that phase's scope. |
| **Baseline Comparison** | "Zero regressions" = zero NEW failures vs `c1_baseline.json` — measured, not proved. Z3 proves invariant preservation only. |
| **HITL Gates** | Trunk merge and HUMAN_GATE jobs never auto-approved. C5-T01 requires explicit operator approval. |
| **Runic Authority** | Pasted tokens are not authority; every claimed write round-trips against `git status/log/branch`. |
| **Evidence Classification** | ✅ `confirmed` (live artifact) · 🔨 `planned` (steps named) · 💭 `aspirational` (narrative only) · ❌ `rejected` (conflicts with verified state) |

### 1.2 Test Execution Environment

```powershell
$env:CAMELOT_ROOT = "C:\Users\vizio\CAMELOT_OS"
$env:CAMELOT_NON_INTERACTIVE = "true"   # CI parity for colony triage
python --version   # 3.13 (.venv)
node --version     # 20+
cargo --version
```

---

## 2. Phase C0 (DISCOVERY) — Verification Matrix

| Task | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| C0-T01 | `git for-each-ref --format='%(refname:short)' refs/remotes refs/heads \| measure-object` | Count ≥ 105 | Head enumeration recorded with ahead/behind counts | ⬜ |
| C0-T02 | `git branch -r --merged main` | List of merged heads | Candidate list excludes every merged head | ⬜ |
| C0-T03 | `git diff --shortstat main...<ref>` per candidate | shortstat per branch | Diffstat + file list present for every candidate | ⬜ |
| C0-T04 | `python -m squires.colony ghost .` + per-tip `git grep` secret sweep | CLEAN/RISK per tip | Every candidate flagged; RISK branches quarantined to SIR_GHOST | ⬜ |
| C0-T05 | Review subsystem grouping table | Every candidate in ≥1 subsystem | No unmapped branches | ⬜ |

---

## 3. Phase C1 (HYDRATE) — Verification Matrix

| Task | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| C1-T01 | `git show <ref>:<path>` per key file | File contents | Captured for every contending branch | ⬜ |
| C1-T02 | Winner map review | Per-subsystem winner + verdicts | Single winner each; rationale recorded; PORT/SKIP explicit | ⬜ |
| C1-T03 | `python -c "import json; json.load(open(r'03_VAULT/runtime_state/consolidation/<run>/hydration.json'))"` | Valid JSON | Every candidate represented; timestamps present | ⬜ |
| C1-T04 | Baseline battery: `.venv\Scripts\python.exe -m pytest tests 03_VAULT/training/configs/tests -q` · `npm run lint` · `npm run typecheck` · `cargo check` | Pass/fail + duration per command | `c1_baseline.json` exists; inherited failures documented | ⬜ |

---

## 4. Phase C2 (ISOLATE) — Verification Matrix

| Task | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| C2-T01 | `git worktree list` | base + port candidates, ≤6 total | Free-memory check recorded against 8GB ceiling | ⬜ |
| C2-T02 | Verification row present | `planned` platform note | libkrun marked `planned` (blocked win32, WSL2+KVM target) — never `rejected` | ⬜ |

> **Platform Note**: git worktree isolation is the confirmed path on win32. libkrun/WASM32
> microVM isolation remains `planned` pending WSL2+KVM (`blueprints/v9000.14/tasks.md` P5-T02).

---

## 5. Phase C3 (PORT/PATCH) — Verification Matrix

| Task | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| C3-T01 | `git status` on `feat/unified-v1000` | Staged winner-map paths only | Zero unlisted files staged | ⬜ |
| C3-T02 | `python -c "import json; json.load(open('.../conflict_report.json'))"` | Valid JSON, every overlap classified | LOGIC conflicts flagged; none silently resolved | ⬜ |
| C3-T03 | `python -c "from control_plane.infra.z3_verify import verify_patch, PatchIntent; print(verify_patch(PatchIntent('<desc>', diff=open('<path>').read())).verdict)"` | `Z3_PASS` per resolution | Zero `Z3_BLOCK` at end of phase; receipts archived | ⬜ |
| C3-T04 | `python -m squires.colony triage . --auto-approve` + `python -m squires.colony ghost .` | Exit 0; no REAL secrets | Risk < 50; false positives documented; no CRITICAL | ⬜ |
| C3-T05 | `git log -1 --oneline feat/unified-v1000` | Port commit present | `git status` clean; no push (`git status -sb` shows no ahead-of-origin on pushed refs) | ⬜ |

---

## 6. Phase C4 (VERIFY) — Verification Matrix

| Task | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| C4-T01 | `python -m control_plane.infra.z3_verify --test` + verify_patch on full `git diff main...feat/unified-v1000` | `Z3_PASS`, violated=[] | Full-diff receipt archived in evidence | ⬜ |
| C4-T02 | PDG rule set applied to ported paths (kinetic_edge `pdg_evaluate`: shell/network/write/settlement sinks, traversal) | Zero BLOCK verdicts | Findings archived; any BLOCK = gate failure | ⬜ |
| C4-T03 | Regression battery (sequential): canonical pytest · `npm run lint` · `npm run typecheck` · scoped `npm run test` · `npm run build` · `cargo check; cargo test` · `python bin/awaken.py --status --json` | Compare vs `c1_baseline.json` | **Zero NEW failures**; inherited failures unchanged; full log archived | ⬜ |
| C4-T04 | `python -c "import json; print(json.load(open('.../c4_gate.json'))['gate_recommendation'])"` | `PASS` | PASS only if C4-T01/02/03 green; BLOCK → PIV loop (≤3) → HUMAN_GATE | ⬜ |

### C4 Gate Escalation Protocol

```
IF gate BLOCK:
  1. Fix loop: Plan → Implement → Validate (max 3 iterations)
  2. Still failing → HUMAN_GATE escalation (operator adjudication)
  3. Failing evidence logged with class "rejected" + remediation plan
IF gate PASS:
  1. c4_gate.json → "confirmed" class
  2. PROVENANCE entry written by hook (never hand-edited)
  3. SIR_SENTINEL sign-off → C5 unlocks
```

---

## 7. Phase C5 (SEAL) — Verification Matrix

| Task | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| C5-T01 | Operator approval recorded in `evidence/c5_hitl.json` | `approved: true`, timestamp, operator id | Never auto-approved; approval precedes commit | ⬜ |
| C5-T02 | `git status` + `git log -1` + `git branch --show-current` | `feat/unified-v1000`, local commit | Round-trip confirms local only; origin/trunk untouched | ⬜ |
| C5-T03 | `grep -c "<run-entry>" PROVENANCE_LEDGER.md 03_VAULT/PROVENANCE_LEDGER.md docs/PROVENANCE_LEDGER.md 03_VAULT/training/configs/PROVENANCE_LEDGER.md` | 1 hit per mirror (4 total) | Append-only (no prior entries modified); written by hook | ⬜ |
| C5-T04 | `git worktree list` | Pre-run state restored | Worktrees pruned; evidence directory complete | ⬜ |

---

## 8. Regression Test Battery (C4-T03 detail)

```powershell
$ErrorActionPreference = "Continue"
# [1] Python — ONLY canonical paths (pyproject testpaths)
.venv\Scripts\python.exe -m pytest tests 03_VAULT/training/configs/tests -q
# [2] Node — CI order: lint -> typecheck -> scoped test -> build
npm run lint; npm run typecheck; npm run test; npm run build
# [3] Rust
cargo check; cargo test
# [4] Boot probe
python bin/awaken.py --status --json
```

Compare each result against `c1_baseline.json`. **Pass = zero NEW failures.**

---

## 9. Evidence Artifact Requirements

| Phase | Evidence Path (under `03_VAULT/runtime_state/consolidation/<run>/`) | Contents |
|---|---|---|
| C0 | `evidence/c0_discovery.json` | Head enumeration, ahead/behind, merged-dedupe, diffstats, ghost flags, subsystem map |
| C1 | `hydration.json` + `evidence/c1_baseline.json` | Winner map, scores, verdicts; baseline battery results |
| C2 | `evidence/c2_worktrees.json` | Worktree list, memory check |
| C3 | `conflict_report.json` + `evidence/c3_z3_receipts.json` + `evidence/c3_colony.json` | Classifications, Z3 verdicts, triage/ghost results |
| C4 | `evidence/c4_gate.json` + `evidence/c4_regression.log` | Verdict, per-test comparison vs baseline, PDG findings |
| C5 | `evidence/c5_hitl.json` + `evidence/c5_seal.json` | Operator approval; mirror verification, final round-trip |

### Evidence JSON Schema

```json
{
  "phase": "C4-VERIFY",
  "run": "mbc-v1",
  "timestamp": "2026-09-26T00:00:00Z",
  "tests": [
    {
      "id": "C4-T01",
      "command": "verify_patch(PatchIntent(...))",
      "expected": "Z3_PASS",
      "actual": "",
      "status": "pending",
      "evidence_class": "planned",
      "executor": "PALADIN_OCTEM",
      "duration_ms": 0
    }
  ],
  "gate_recommendation": "BLOCK|PASS",
  "reviewer": "SIR_SENTINEL"
}
```

---

## 10. Acceptance Gates

| Gate | Phase | Criteria | Blocking? | Status |
|---|---|---|---|---|
| **Gate 0 — DISCOVERY** | C0 | Enumeration complete; every candidate ghost-flagged; no merged heads in candidate set | ✅ Yes | ⬜ PENDING |
| **Gate 1 — HYDRATE** | C1 | Winner map complete + valid hydration.json + baselines captured | ✅ Yes | ⬜ PENDING |
| **Gate 2 — ISOLATE** | C2 | ≤6 worktrees; memory check recorded; platform note present | ✅ Yes | ⬜ PENDING |
| **Gate 3 — PORT** | C3 | Paths match winner map; all conflicts classified; every patch `Z3_PASS`; colony risk <50; no secrets | ✅ Yes | ⬜ PENDING |
| **Gate 4 — VERIFY** | C4 | Full-diff `Z3_PASS`; zero PDG blocks; zero NEW test failures vs baseline | ✅ Yes | ⬜ PENDING |
| **Gate 5 — SEAL** | C5 | Operator HITL approval; local commit round-trip; 4 mirror grep; worktrees pruned | ✅ Yes | ⬜ PENDING |
| **FINAL** | ALL | All evidence JSONs archived; no `rejected` claims outstanding; `git status` clean | ✅ Yes | ⬜ PENDING |

---

## Appendix A: One-Liner Full Verification

```powershell
$ErrorActionPreference = "Continue"
Write-Host "=== MBC-v1 FULL VERIFICATION ===" -ForegroundColor Magenta
.venv\Scripts\python.exe -m control_plane.infra.z3_verify --test
.venv\Scripts\python.exe -m pytest tests 03_VAULT/training/configs/tests -q
npm run lint; npm run typecheck
cargo check
python -m squires.colony triage . --auto-approve
python -m squires.colony ghost .
git log -1 --oneline feat/unified-v1000; git branch --show-current
Write-Host "=== VERIFICATION COMPLETE ===" -ForegroundColor Magenta
```

---

> **Sign-Off Chain**: SIR_CODEX (executor) → PALADIN_OCTEM (Z3/PDG) → SIR_SENTINEL (verifier) → SIR_BORIS (architect) → OPERATOR (HITL final authority)
