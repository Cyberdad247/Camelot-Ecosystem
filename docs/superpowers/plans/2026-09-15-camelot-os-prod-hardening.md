# CAMELOT-OS Production Hardening Parallel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development for parallel task swarm. Each section is a standalone, reviewable stream. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Achieve production-ready architecture, security, infra, tests, docs, and merge discipline for CAMELOT-OS with parallel executing agents.

**Architecture:** Each major domain (architecture, security, secrets, infra, testing, docs, merge) assigned to a subagent. Parallel development is coordinated via the bio-kinetic swarm and cartridge protocols—cross-verification is enforced after each section. 

**Tech Stack:** Python 3.11+, TypeScript (node), Git, squire colony (SCANNING), Runic Router, Tailscale mesh, modern CI

**Spec:** AGENTS.md (root), .agents/skills/multi-repo-branch-audit/SKILL.md, .agents/skills/writing-plans/SKILL.md, docs/blueprint.md, docs/design.md

## Global Constraints
- All secrets removed from tracked code.
- No hardcoded tokens, passwords, or private API keys.
- .env, .env.local are gitignored and checked.
- All logic must have unit/integration tests.
- Changes >10 lines or that touch main/infra get scoped review before merge.
- All runic/agent rules enforced per project AGENTS.md and parent CAMELOT_OS/AGENTS.md.
- Docs and blueprints updated to match state.

---

## PARALLEL TASK MATRIX

### 1. Architecture/Modularity
- [ ] Review and document boundaries of all critical modules (routing, state, security, gateway, colony)
- [ ] Refactor for better separation of concerns if necessary
- [ ] Ensure core boot, REPL, router, orchestrator are cleanly surfaced
- [ ] Add+validate module-level docstrings
- [ ] Output: architecture diagram, modularity notes

### 2. Security & Secrets Hygiene
- [ ] Prune repo for all .env, key, token, password fingerprints
- [ ] Enforce gitignore on .env and secrets
- [ ] Sweep for hardcoded secrets (manual/automated, scoped scans for large dirs)
- [ ] Add/Improve HITL gates, mTLS and rate-limiting checks
- [ ] Output: secret audit log, .env gitignore proof, HITL/mTLS config

### 3. Dependencies/Infra/Setup
- [ ] Audit/lock all major dependency manifests (requirements.txt, pyproject.toml, package.json, go.mod)
- [ ] Ensure reproducible setup: up-to-date install/docs, no build breakage
- [ ] Validate bootstrapping commands/scripts work from fresh environment
- [ ] Output: dependency audit, setup reproducibility log

### 4. Test Coverage/Verification
- [ ] Enumerate all test suites, coverage, types
- [ ] Author missing unit/integration/security/repro tests
- [ ] Run all tests in CI and verify pass/fail/hit-gate discipline
- [ ] Output: pass/fail matrix, coverage summary, patched failing tests

### 5. Documentation & Blueprints
- [ ] Update/expand docs/blueprint.md, AGENTS.md for true system boundaries
- [ ] Ensure guides for setup, dev, boot, squire pipeline are present and readable
- [ ] Link all pending architectural or merge changes to docs
- [ ] Output: docs diff, blueprint update log

### 6. Merge Hygiene & Multi-Branch Unification
- [ ] Map all active feature/support branches
- [ ] Identify the best patterns/features per branch
- [ ] Write integration/merge plan (feature unification steps, base branch, test plan)
- [ ] Output: merge plan, conflict map, integration checklist

---

## Parallelization Protocol
- Each stream proceeds independently in a branch or cartridge.
- Cross-verification checkpoints after each section: no merge unless HITL+test pass and diffs acknowledged.
- Final review and approval required before unified merge to main.

> This plan is saved here as your engineering contract. Approve to begin the swarm.
