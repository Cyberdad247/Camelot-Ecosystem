# 🛡️ Camelot-OS Git Branch Hygiene & Swarm Execution Guide
> **Document Status**: Production Ready | **Compliance Enforced**: Yes

This document establishes the official branch naming conventions, hygiene strategies, and swarm execution flows for the **Camelot-OS** repository.

---

## 📊 Overview: Git Clutter & Fetch Overhead
Over time, active development repositories accumulate hundreds of branches. This leads to:
1. **Network Overhead**: Fetching remote tracking states slows down proportionally with the number of references (`git fetch --all`).
2. **IDE Lag**: Most modern IDEs parse all refs for branch matching, which causes significant indexing delay with 130+ branches.
3. **Cognitive Load**: Harder for developers to identify active workspace streams.

Implementing the **5-Phase Swarm Pipeline** will optimize the repository structure from **130+ branches** down to a clean **20-25 active branches**.

---

## 🏷️ Branch Naming Taxonomy
All branches created in this repository must use one of the following prefixes to pass local and remote pre-commit hooks:

| Prefix | Description | Example |
|---|---|---|
| `feat/` | New features, capabilities, or major architecture grafts | `feat/zero-kv-cache` |
| `fix/` | Bug fixes, repair patches, and hotfixes | `fix/latency-patch` |
| `chore/` | Build scripts, dependencies, config tweaks, and infra tasks | `chore/reconcile-ledger` |
| `docs/` | Documentation additions, revisions, and reports | `docs/v9000.14-go-live` |
| `perf/` | Code optimization or performance enhancements | `perf/ssm-core-recurrence` |
| `refactor/` | Code structure improvements without functional changes | `refactor/ouroboros-types` |
| `test/` | Automated test suites and verification suites | `test/forge-ci-verify` |
| `ci/` | GitHub Actions, workflows, and automation pipelines | `ci/linter-setup` |
| `claude/` | Autonomous agent work streams (Knight execution nodes) | `claude/jules-task-342` |

---

## 🚀 The 5-Phase Pipeline
The `swarm_executor.py` coordinates 5 execution phases:

### Phase 1: Audit
- Gathers local and remote branch tracking lists.
- Dynamically assigns a **Delete Score** (0-100) based on category classification and inactivity age.
- Category rules:
  - `auto_test` -> Delete Score: 100
  - `jules_task` -> Delete Score: 80
  - `fix` -> Delete Score: 40-60 (higher if merged)
  - `feature` -> Keep if active

### Phase 2: Validation (Concurrently Run)
- **Naming Compliance**: Evaluates branch compliance metrics.
- **Main Protection**: Validates primary branch protection structure.
- **Threshold check**: Boundary checking: `PASS` (<= 25 branches) | `WARN` (26 - 50 branches) | `FAIL` (> 50 branches).

### Phase 3: Optimization
- Generates prioritizations: High Priority Deletions, Medium Priority Deletions, and Keep list.
- Computes estimated monthly time savings on network operations.

### Phase 4: Generation (Concurrently Run)
- Generates `delete_branches_swarm.sh`: safe, phased, interactive branch deletion script.
- Generates `validate_cleanup.sh`: validation test suite to run post-cleanup.

### Phase 5: Reporting
- Generates JSON report logs in `data/` for audit logs.
- Outputs console metrics summary.

---

## 🎯 How to Execute

### Option 1: Swarm Orchestration (Recommended)
Executes all 5 phases automatically, creating report files and scripts:
```bash
bash scripts/run_swarm.sh
```

### Option 2: Simulation Mode
Simulate a large 135-branch footprint to test and verify the engine's scaling bounds:
```bash
bash scripts/run_swarm.sh --simulate
```

### Option 3: Legacy Individual Verification
Run individual CLI commands if needed:
```bash
python scripts/branch_cleanup_audit.py
python scripts/branch_validation.py
```

---

## 🔒 Enabling Enforcement Hooks
To ensure naming compliance going forward, install the pre-commit and pre-push hook:
```bash
bash .githooks/install-hooks.sh
```
This will prevent committing to or pushing non-compliant branches, showing a helpful error and naming guide.
