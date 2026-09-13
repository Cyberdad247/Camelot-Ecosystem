---
name: multi-repo-branch-audit
description: Use when auditing a Git repository with multiple divergent branches to identify the best architecture from each, find secrets/leaks, and produce an integration plan to merge all best patterns into one unified branch. Orchestrates AnyaGate compilation, multi-knight dispatch (SIR_BORIS architecture, SIR_SENTINEL security, MERLIN_OMEGA deep reasoning, SIR_CODEX implementation), squire colony secret scanning, and diff analysis across all branches.
---

# Multi-Repo Branch Audit

Audit a Git repository with multiple divergent branches, identify the best architecture from each, and produce an integration plan to merge all best patterns into one unified branch.

This skill orchestrates the full Camelot-OS knight roster for comprehensive repo analysis: architecture review, security audit, deep reasoning on integration strategy, and implementation planning.

## When To Use

Use this when the user asks to:

- audit a repo with multiple feature branches;
- compare branch architectures and find the best patterns;
- merge multiple branches into one unified branch;
- find secrets or credential leaks across branches;
- create an integration plan for branch consolidation;
- analyze which branch has the best code for each component;
- consolidate divergent development efforts.

## Inputs Required

| Input | Required | Description |
|---|---|---|
| `repo_url` | Yes | Git repository URL (HTTPS or SSH) |
| `branch_pattern` | No | Glob pattern for branches to audit (default: all) |
| `focus_areas` | No | Specific areas to audit: `architecture`, `security`, `ui`, `db`, `tests` |
| `unified_branch_name` | No | Name for the output branch (default: `feat/unified-v1000`) |

## Pipeline

```
Phase 1: DISCOVERY    → Clone repo, list all branches, compute diff stats
Phase 2: ANALYSIS     → Read key files from each branch, understand architecture
Phase 3: ANYA_GATE    → Compile audit intent through APEE v6.5
Phase 4: KNIGHT_DISPATCH → Route to SIR_BORIS, SIR_SENTINEL, MERLIN_OMEGA, SIR_CODEX
Phase 5: SECRET_SCAN  → Squire Colony GHOST scan across all branches
Phase 6: SYNTHESIS    → Produce audit report, integration plan, forged prompts
Phase 7: EXECUTION    → Create unified branch, port best files, resolve conflicts
```

## Phase 1: Discovery

```bash
# Clone the repository
git clone <repo_url> /tmp/<repo_name>-audit

# List all branches
git ls-remote --heads <repo_url>

# For each branch, compute diff stats against main
git diff --stat main..feat/<branch_name>
```

Record:
- Total branches found
- Commits ahead/behind for each
- Files changed per branch (additions/deletions)
- Which branches are already merged to main

## Phase 2: Analysis

For each branch, read the key architectural files:

| File | What to Look For |
|---|---|
| `server.ts` / `main.py` | Server architecture, routing pattern |
| `router.ts` / `runic_router.py` | Command routing, dispatch logic |
| `state.ts` / `state.py` | State management pattern |
| `security.ts` / `security.py` | Auth, HMAC, rate limiting |
| `package.json` / `pyproject.toml` | Dependencies, scripts |
| `tailwind.config.*` | UI design system |
| `*.test.ts` / `test_*.py` | Test coverage |

For each component, rate:
- **Architecture** (1-10): Clean separation, modularity, extensibility
- **Security** (1-10): Auth, input validation, rate limiting, HITL gates
- **Features** (1-10): Completeness, production-readiness
- **Tests** (1-0): Coverage, quality, integration tests
- **Documentation** (1-10): Comments, README, inline docs

## Phase 3: AnyaGate Compilation

Compile the audit intent through the AnyaGate APEE v6.5 pipeline:

```python
from control_plane.core.anya_gate import AnyaGate

gate = AnyaGate()
result = gate.process(f'''MULTI-KNIGHT AUDIT: {repo_name} — {branch_count} branches to unify
BRANCHES: {branch_list}
AUDIT SCOPE: (1) Architecture — evaluate server patterns across branches, identify best routing/state/broadcast approach. (2) Security — auth, signing, rate limiting, HITL gates. (3) UI/PWA — components, hooks, context. (4) DB/Tests — migrations, validators, test suites. (5) INTEGRATION PLAN — merge all best patterns into one optimized branch.''')
print(result.render())
```

The gate will route to the appropriate knight (typically SIR_BORIS for architecture audits).

## Phase 4: Knight Dispatch

Dispatch to 4 knights via the runic router:

### SIR_FORGE — Architecture Audit + Implementation Plan

```python
from control_plane.runes.runic_router import route_rune

r = route_rune('//FORGE', f'''AUDIT: {repo_name} — {branch_count} branches: {branch_details}. Evaluate server patterns, identify best routing/state/broadcast approach, security architecture, UI/PWA patterns, DB/Tests, and produce integration plan for unified branch.''')
```

**Knight:** sir_forge | **Mode:** KINETIC

### SIR_SENTINEL — Security Audit

```python
r = route_rune('//SCAN', f'''SECURITY AUDIT: {repo_name} — auth, signing, rate limiting, HITL gates, secrets hygiene across {branch_count} branches''')
```

**Knight:** sir_ghost (privacy scan mode) | **Mode:** SENTINEL

### MERLIN_OMEGA — Deep Integration Reasoning

```python
r = route_rune('//THINK', f'''INTEGRATION ANALYSIS: {repo_name} — Compare {branch_a} vs {branch_b}. Determine optimal merge strategy that preserves features while adopting efficiency. Identify conflict zones and resolution strategy.''')
```

**Knight:** merlin_omega | **Mode:** ORACLE

### SIR_CODEX — Implementation Plan

```python
r = route_rune('Omega_CODEX', f'''IMPLAN: {repo_name} — create {unified_branch_name} branch merging best of all {branch_count} branches''')
```

**Knight:** sir_codex | **Mode:** ORACLE

## Phase 5: Secret Scan

Run Squire Colony GHOST scan across all branches:

```bash
# Run full triage pipeline
python -m squires.colony triage /tmp/<repo_name>-audit --auto-approve

# Cross-branch secret scan
for branch in $(git branch -r | grep -v HEAD); do
  git checkout $branch
  grep -rn --include="*.ts" --include="*.js" --include="*.json" \
    -E "(sk-ant-|sk-[a-zA-Z0-9]{32,}|AIza|AKIA|PRIVATE KEY)" . \
    | grep -v node_modules
done
```

Check:
- `.env` files tracked in git (should be none)
- `.gitignore` excludes `.env` patterns
- No hardcoded API keys, passwords, or tokens
- Test fixtures flagged as false positives

## Phase 6: Synthesis

Generate three reports:

### 1. Audit Report (`docs/reports/REPO_AUDIT_<date>.md`)

```markdown
# Multi-Knight Audit Report
## <repo_name> — Branch Unification Analysis

### Branch Map
| Branch | Key Innovation | Lines Changed | Verdict |
|---|---|---|---|
| main | Baseline | ... | Stable foundation |
| feat/X | Feature Y | ... | BASE for unified |
| feat/Z | Pattern W | ... | PORT only |

### Architecture Comparison
| Feature | Branch A | Branch B | Winner |
|---|---|---|---|
| Routing | ... | ... | ... |
| State | ... | ... | ... |
| Security | ... | ... | ... |

### Integration Strategy
Phase 1: Create unified branch from best base
Phase 2: Port unique modules from other branches
Phase 3: Restore removed components if needed
Phase 4: Resolve conflicts
Phase 5: Verify (typecheck, test, build)
Phase 6: Update docs

### Files to Preserve
From branch A: [list]
From branch B: [list]
DELETE: [list]
```

### 2. Knight Prompts (`docs/reports/REPO_KNIGHT_PROMPTS_<date>.md`)

All 8 forged prompts for reproducible dispatch:

```markdown
## Prompt 1: SIR_FORGE — Architecture Audit
//FORGE AUDIT: <repo> — <branches>. Evaluate patterns, produce integration plan.

## Prompt 2: SIR_SENTINEL — Security Audit
//SCAN SECURITY AUDIT: <repo> — auth, signing, rate limits across branches.

## Prompt 3: MERLIN_OMEGA — Deep Reasoning
//THINK INTEGRATION: <repo> — <branch_a> vs <branch_b> merge strategy.

## Prompt 4: SIR_BORIS — Architecture Review
Omega_BORIS ARCHITECTURE: <repo> — server patterns, state, broadcast.

## Prompt 5: SIR_SENTINEL — Security Hardening
Omega_SENTINEL SECURITY: <repo> — HMAC, mTLS, rate limits, HITL.

## Prompt 6: MERLIN_OMEGA — Strategic Reasoning
Omega_MERLIN DEEP REASONING: <repo> — branch integration decision tree.

## Prompt 7: SIR_CODEX — Implementation Plan
Omega_CODEX IMPLAN: <repo> — create <unified_branch> steps.

## Prompt 8: ANYA_Omega — Gate Validation
Omega_ANYA GATE: <repo> unified branch — architecture, security, tests, build.
```

### 3. Secret Audit (`docs/reports/REPO_SECRET_AUDIT_<date>.md`)

```markdown
## Scan Summary
| Metric | Value |
|---|---|
| Files Scanned | ... |
| Risk Score | .../100 |
| Real Secrets | ... |

## Cross-Branch Results
| Branch | Secrets Found |
|---|---|
| main | ... |
| feat/X | ... |

## Verdict
CLEAN / ISSUES FOUND
```

## Phase 7: Execution (Optional)

If the user requests branch creation:

```bash
# Create unified branch from best base
git checkout -b <unified_branch_name> feat/<best_base>

# Port unique modules
git checkout feat/<other_branch> -- <file_path>

# Verify
npm run typecheck  # or equivalent
npm run test
npm run build

# Commit
git add -A
git commit -m "feat: unify <branch_count> branches into <unified_branch_name>"
```

## Knight Composition

### Audit Architect (SIR_BORIS)

- **Archetype:** `ArchitectKnight`
- **Purpose:** Evaluate server patterns, state management, broadcast architecture
- **Skills:** architecture review, code analysis, pattern comparison
- **Output:** Architecture comparison matrix, integration strategy

### Security Sentinel (SIR_SENTINEL)

- **Archetype:** `SentinelKnight`
- **Purpose:** Audit auth, signing, rate limiting, secrets hygiene
- **Skills:** security audit, secret scanning, HITL gate review
- **Output:** Security matrix, hardening recommendations

### Deep Reasoner (MERLIN_OMEGA)

- **Archetype:** `OracleKnight`
- **Purpose:** Analyze branch divergence, produce merge strategy
- **Skills:** deep reasoning, decision tree analysis, conflict resolution
- **Output:** Conflict zone map, optimal merge sequence

### Implementation Planner (SIR_CODEX)

- **Archetype:** `ForgeKnight`
- **Purpose:** Create step-by-step implementation plan
- **Skills:** code generation, branch management, verification
- **Output:** Phase-by-phase execution plan with commands

### Sovereign Gate (ANYA_OMEGA)

- **Archetype:** `GateKnight`
- **Purpose:** Validate unified branch integrity
- **Skills:** APEE pipeline, architecture validation, build verification
- **Output:** Gate verdict (APPROVED/BLOCKED)

## Safety Rules

- Do not push branches without explicit user permission
- Do not delete branches without confirmation
- Do not commit secrets or credentials
- Do not run destructive git commands (reset, force-push)
- Always verify builds before claiming success
- Report false positives from secret scans
- Preserve all branch refs until user confirms deletion

## Output Artifacts

| Artifact | Path | Description |
|---|---|---|
| Audit Report | `docs/reports/REPO_AUDIT_<date>.md` | Full multi-knight analysis |
| Knight Prompts | `docs/reports/REPO_KNIGHT_PROMPTS_<date>.md` | Reproducible dispatch prompts |
| Secret Audit | `docs/reports/REPO_SECRET_AUDIT_<date>.md` | Security scan results |
| Colony Report | `colony_report.md` | CLARITY_CORE generated report |
| Unified Branch | `feat/unified-v1000` | Merged branch (if created) |

## Quick Reference

```bash
# Full audit pipeline
python -m squires.colony triage <repo_path> --auto-approve

# Dispatch all knight prompts
python -c "
from control_plane.runes.runic_router import route_rune
for rune, task in PROMPTS:
    r = route_rune(rune, task)
    print(f'{rune} → {r.knight} | {r.mode} | queued={r.queued}')
"

# Create unified branch
git checkout -b feat/unified-v1000 feat/<best_base>
git checkout feat/<other> -- <file>
npm run typecheck && npm run test && npm run build
```
