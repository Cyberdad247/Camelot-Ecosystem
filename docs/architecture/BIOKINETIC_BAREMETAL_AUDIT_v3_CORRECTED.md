# Biokinetic Squire Colony Bare-Metal Audit System — v3 (Corrected)

**Status:** evidence-classified correction of v2.0
**Date:** 2026-10-04
**Supersedes:** `Biokinetic_Squire_Colony_BareMetal_Audit_System-v2.md` (not present in this
repository — authored in an external Studio panel; this document is the in-repo replacement)

Every claim below carries one of the four evidence classes defined in `harness.md:33-36`:
`confirmed` (verified by current files/commands/tests), `planned` (implementable, not built),
`aspirational` (direction only, no repo evidence), `rejected` (conflicts with verified state).

---

## 1. Why this document exists

v2.0 asserted five architectural pillars. On verification against the working tree, three did not
survive contact with the code. v2 is not wrong about wanting a resource auditor — that part is
real and is now built — but it described simulated telemetry and one misapplied technique as
hardware characteristics. This document states what is actually true.

Verification commands are listed per claim so any reader can reproduce the finding.

---

## 2. Pillar audit

### 2.1 "Parallel MicroVM Swarm Topology" — `aspirational`, and partly `rejected`

v2 claimed a `forkd` Copy-on-Write micro-agent swarm with a **Δ ≤ 0.12 MiB** page footprint and
**≤ 1.01 ms** cold-start latency across five Squire node roles.

| Fact | Class | Evidence |
|---|---|---|
| `forkd_runner.sh` is 34 lines with two subcommands: write 32 bytes of entropy, and shell out to `qemu-img` for a qcow2 overlay | `confirmed` | `01_KERNEL/core/microvm_cages/forkd_runner.sh` |
| It contains no hypervisor, no CoW page accounting, and nothing that could emit Δ or cold-start figures | `confirmed` | same file, full read |
| `hive_engine.py` MicroVMSandbox / Δ ≤ 0.12 MiB telemetry **is a Python simulation** | `confirmed` | `blueprints/multi_branch_consolidation/blueprint.md:41` |
| libkrun microVM isolation is **BLOCKED on win32**; `forkd_runner.sh` is the fallback, never marked rejected | `confirmed` | `blueprints/multi_branch_consolidation/blueprint.md:41`, `tasks.md:33` |
| Real microVM isolation on this host | `planned` | WSL2 + KVM target, `docs/architecture/scope-review-cybertron-ascension-2026-06-25.md:18` |
| The five named roles (`SQUIRE_JANITOR_CORE`, `SQUIRE_MYRMIDON_MERGE`, `SQUIRE_VFS_SCAFFOLDER`, `SQUIRE_TELEMETRY_RESOURCE`, `SQUIRE_CONFORMITY_INJECTOR`) | `aspirational` | no matching symbols anywhere in the repo |
| Δ ≤ 0.12 MiB and ≤ 1.01 ms as *measured hardware properties* | `rejected` | no measurement path exists; the figures originate in a simulation |

**Correction:** Δ and cold-start latency are **unmeasured**. They may not be cited as hardware
characteristics. Any spec or dashboard asserting them as measured is wrong.

### 2.2 "Net b1.58 ternary quantization enforcing an 8.0 GB RAM ceiling" — `rejected`

v2 bundled ternary weight quantization with a physical RAM ceiling as if one governed the other.

| Fact | Class | Evidence |
|---|---|---|
| A `BitLinearQuantizer` exists | `confirmed` | `01_KERNEL/ml_persona_engineer/quantization.py` |
| Ternary quantization is a **weight format for neural networks**; it reduces model weight storage | `confirmed` | standard technique (BitNet b1.58) |
| Physical RAM ceilings are enforced by the OS memory manager (job objects / cgroups), **not** by quantizing `W_ij` | `confirmed` | OS architecture |
| BitNet b1.58 can enforce this host's RAM ceiling | `rejected` | category error — no mechanism connects the two |

**Correction:** the two concerns are independent. RAM ceilings are an OS-configuration concern;
quantization is a model-storage concern. Bundling them is a category error.

### 2.3 "Triple-QFT semantic noise stripping, >90% signal purity" — `aspirational`

| Fact | Class | Evidence |
|---|---|---|
| Triple-QFT is **Quantization, Qualification & Flow-Transformation** — a three-stage rewrite of natural-language intent into runic directives | `confirmed` | `01_KERNEL/protocols/triple_qft_compilation.md:5` |
| A working zero-dependency implementation exists (18 KB of string manipulation) | `confirmed` | `scripts/symbolect_transpiler.py` |
| "Signal purity" is a metric Triple-QFT emits | `rejected` | no such measurement exists in the implementation |

**Correction:** Triple-QFT is a **prompt/format compiler**, not a signal-processing transform. The
">90% purity" figure has no defined metric behind it. Note also that "QFT" is overloaded in this
repo across at least four meanings (Quantum Fluff Trimming, Quantization-Qualification-Flow,
Question Formulation Technique, and academic QFT) — see `01_KERNEL/protocols/Ω_THINK_TANK_PRIME.md:22`.
Disambiguate before citing.

### 2.4 "5-Value Recommendation Engine" — `confirmed` (delivered, measured)

This pillar was sound and is now implemented. See §3.

### 2.5 "Universal TOON Bootstrap Crystal v2.0" and NotebookLM folder taxonomy — `planned`

TOON encoding is real (`control_plane/runes/toon_encoder.py`); the specific "Bootstrap Crystal v2.0"
manifest and the `01_SOURCES/` / `02_NOTEBOOK_MAPPING/` taxonomy are not present in-repo. Treat as
`planned` until a manifest file lands.

---

## 3. What is actually built and verified

The auditable half of v2 exists as two tools plus a regression suite. All numbers below are read
from the live system at run time via `psutil` / `os.scandir` — nothing is modelled or extrapolated.

| Artifact | Purpose |
|---|---|
| `scripts/vfs_janitorial_sweep.py` | Read-only RAM + disk audit. SAFE / REVIEW / PROTECT tiers. |
| `scripts/purge_unused_resources.py` | Allowlisted purge; dry-run by default; `--apply` to delete. |
| `tests/test_vfs_janitorial_sweep.py` | 52 tests, 0 skipped. Regression cover for every guard. |

### 3.1 Safety model

- `PROTECT` — `.venv`, `node_modules`, `.git`, `.worktrees`, all of `03_VAULT`, every
  `PROVENANCE_LEDGER.md` mirror. Never deletable, even under a spoofed tier (`freed == 0` is
  asserted by test).
- `SAFE` / `REVIEW` — regenerable output only, **and only when git confirms zero tracked files**
  beneath the candidate. Git, not the directory name, is the authority on generated vs. authored.
- Symlinked directories are never purge candidates — we do not own what they reference.
- `data/` and `_tmp/` are pruned from the walk.

### 3.2 Bugs found and fixed during construction

Recorded because each was a live data-loss path, not a cosmetic defect.

1. **Path corruption.** `(Path('.') / name).resolve()` anchored to `os.getcwd()` instead of the
   supplied root. Run from any subdirectory, the real `target/` was recorded as `apps/target` and
   phantom `apps/apps/...` paths were invented — `--apply` would have deleted a live source tree and
   left the actual cache in place. Now built lexically via `os.path.normpath`.
2. **Symlink escape.** A directory symlink named `build` pointing outside the root was reported as
   a purge candidate. Now skipped.
3. **Name collision.** A source directory named `target`/`build`/`dist` would have been swept. Now
   rescued by the git-tracked check — which fires on the real repo for
   `02_FORGE/apps/anya-lyte/.expo` (46 committed Metro polyfill files).
4. **Dead prune constant.** `PRUNE_DIRS` was declared but never applied, so the walk descended into
   `data/` (pytest's basetemp), inflating the audit by 71 phantom directories.
5. **Cross-tool boundary drift.** `purge_pycache` deleted `03_VAULT/__pycache__` while the sweep
   protected it. Now regression-tested from both sides.
6. **`purge_unused_resources` deleted `.venv` and `node_modules`** outright. This was the most
   dangerous defect and is fixed; nested clones were moved to `RETIRED_TARGETS` and are never purged.

### 3.3 Measured host state (2026-10-04)

```
total       7.71 GB
used        7.26 GB  (94.2%)
available   0.38-0.49 GB
swap        0.65-1.03 GB of 8.00 GB
```

v2 described a "hard 90% GC interrupt trigger" as a *design target*. On this host it has **already
tripped**. `--fail-on-critical` exits `2` at or above the threshold, so this is CI-enforceable.

Reclaimable build output: **SAFE 43 dirs / 0.63 GB**, `REVIEW 34 dirs / 0.04 GB`,
`PROTECT 42 dirs / 9.93 GB` (never removed).

---

## 4. Invariants for future work

1. **Never cite a simulated number as a measurement.** The Δ ≤ 0.12 MiB / 1.01 ms figures are the
   canonical example. If a number cannot be produced by a command on this host, it is `aspirational`.
2. **Git decides generated vs. authored**, never the directory name.
3. **`03_VAULT` and the four `PROVENANCE_LEDGER.md` mirrors are untouchable** by any sweep tool.
4. **Measurements and models must be visually distinguishable** in every report and ledger entry.
5. **Label claims with the `harness.md` evidence class** when reporting status.

---

## 5. Reproduction commands

```powershell
# Audit (read-only)
.venv\Scripts\python.exe scripts\vfs_janitorial_sweep.py
.venv\Scripts\python.exe scripts\vfs_janitorial_sweep.py --json
.venv\Scripts\python.exe scripts\vfs_janitorial_sweep.py --fail-on-critical   # exit 2 at >=90%

# Purge (dry run by default)
.venv\Scripts\python.exe scripts\purge_unused_resources.py
.venv\Scripts\python.exe scripts\purge_unused_resources.py --apply

# Guard regression suite
.venv\Scripts\python.exe -m pytest tests\test_vfs_janitorial_sweep.py -q

# Rejected claims, reproduced
git ls-files -- 01_KERNEL/core/microvm_cages/forkd_runner.sh
Get-Content blueprints\multi_branch_consolidation\blueprint.md | Select-String "simulation"
```

## 6. Open items

- Real microVM isolation remains `planned`, blocked on WSL2 + KVM. Not attempted here.
- 0.63 GB of SAFE build output is staged but **not deleted** — awaiting explicit `--apply`.
- Host memory is the live constraint (94%+). It is not a code problem; closing `opencode.exe`
  (~0.55 GB) and `MemCompression` (~0.68 GB) requires operator action.