# Publication Surface Inventory

**Compiler:** Sir Codex via Anya Gate
**Date:** 2026-07-09
**Scope:** First P0 tranche from `tasks.md` - map GUI surface, CLI surface, cloudbrain config/env surface, and release-critical subprocess entrypoints.

## Routing Notes

- `//PLAN` routed to `merlin_omega`, but the repo surfaced a stale `Plan.json` from an older PWA overhaul, so it was not used as the source of truth for this tranche.
- `//CODEX` routed to `sir_codex` for the actual implementation tranche.
- The runtime emitted `CLOUD_BRAIN` warning text noting `sir_codex` is unmapped for cloudbrain sync, which means cloudbrain sync is not yet fully wired to that knight lane.

## GUI Surface

Primary GUI root:

- `02_FORGE/PORTAL_CORE/Anya_Dashboard`

Current shipped surface in that app:

- Vite app entry: `src/main.tsx`
- UI shell: `src/App.tsx`
- layout/navigation: `src/components/layout/AppShell.tsx`, `src/components/layout/Sidebar.tsx`
- hub/operator panels: `src/features/hub/SystemHub.tsx`, `src/features/hub/ConfigPanel.tsx`, `src/features/hub/FleetPanel.tsx`
- command and runtime features: `src/features/camelot-os/CamelotOsCommand.tsx`, `src/features/camelot-os/camelotOsClient.ts`
- dashboard-specific state and telemetry: `src/features/agency/FactoryDashboard.tsx`, `src/features/defense-grid/DefenseGridConsole.tsx`, `src/features/swarm/SwarmMonitor.tsx`, `src/features/research/ResearchDepartment.tsx`
- visual and knight surfaces: `src/features/knights/*`, `src/features/brain/*`, `src/features/cartridges/*`
- tests: `src/__tests__/*`, `tests/e2e/dashboard.spec.ts`
- release/deploy config: `vercel.json`, `vite.config.ts`, `playwright.config.ts`, `vitest.config.ts`, `PRODUCTION.md`

Assessment:

- The GUI is a real Vite/React surface with feature modularity, not a stub.
- It already has test coverage scaffolding and a deployment config, which is good for publication readiness.
- The next implementation pass should verify the operator-readiness flow, not just the build.

## CLI Surface

Primary CLI entrypoints:

- `control_plane.camelot_cli:main`
- `bin.camelot:main`
- `bin.knight_session:main`

Command families in the control-plane CLI:

- `chat`, `route`, `triage`, `orchestrator`
- `ledger` subcommands: `status`, `audit`, `reconcile`, `sync`, `update`
- `toon` subcommands: `compile`, `sample`
- `glyph` subcommands: `list`, `load`, `activate`, `expand`, `audit`, `execute`
- `forge-unify` subcommands: `activate`, `status`, `route`, `forensic-check`
- `cloudbrain` subcommands: `status`, `config`, `sync`, `queue`, `research-health`, `northstar-health`, `blueprint-health`, `precise-health`, `eldergod-health`, `memory`, `eldergod`, `research`, `northstar`, `blueprint`, `precise`
- `sarda`, `team`, `cockpit`, `codex`, `shadow`, `bio-swarm`, `nano-swarm`, `microcubed`, `gemini-ext`, `evolve`, `scripts`, `ctx7`

Assessment:

- The CLI is the real production control plane.
- It already exposes the major publication-critical surfaces: cloudbrain, ledger, cockpit, and verification.
- The implementation still contains several subprocess-heavy branches that need tighter publication gating.

## Cloudbrain Config Surface

Primary env/config keys:

- `CAMELOT_CLOUDBRAIN_URL`
- `CAMELOT_LIVING_NOTEBOOK_URL`
- `CAMELOT_RESEARCH_AGENCY_URL`
- `CAMELOT_RESEARCH_AGENCY_HEALTH_URL`
- `CAMELOT_NORTHSTAR_URL`
- `CAMELOT_NORTHSTAR_HEALTH_URL`
- `CAMELOT_BLUEPRINT_URL`
- `CAMELOT_BLUEPRINT_HEALTH_URL`
- `CAMELOT_PRECISE_MODE_URL`
- `CAMELOT_PRECISE_MODE_HEALTH_URL`
- `CAMELOT_EXCALIBUR_BRIDGE_URL`
- `CAMELOT_EXCALIBUR_HEALTH_URL`
- `CAMELOT_OS_HOME`
- `CAMELOT_ACTIVE_KNIGHT`
- `CAMELOT_OS_STREAM_DELAY`
- `CAMELOT_OS_PROGRESS_DELAY`
- `CLIPROXY_BASE`
- `CLIPROXY_KEY`
- `OLLAMA_BASE`
- `SIR_OCTAVIAN_BASE`
- `SIR_SONUS_BASE`
- `BIFROST_GATEWAY_BASE`

Assessment:

- `control_plane.config_manager` already centralizes the publication-relevant endpoint map.
- The CLI warns when `CAMELOT_CLOUDBRAIN_URL` still points at a NotebookLM URL and expects the living notebook URL to move to `CAMELOT_LIVING_NOTEBOOK_URL`.
- `cloudbrain_sync.py` sets `CAMELOT_OS_HOME` automatically, which is useful for runtime consistency.

## Execution Surfaces

Highest-risk subprocess or shell-adjacent sites found in this tranche:

- `bin/run_uiux_workflow.py` uses `shell=True` for shell-style UI/UX workflow commands.
- `bin/worker_service.py` launches PowerShell with `-ExecutionPolicy Bypass`.
- `control_plane/boot_sequence.py` launches multiple subprocesses and PowerShell fallbacks.
- `control_plane/camelot_cli.py` runs the sync script and gateway commands directly.
- `control_plane/cockpit.py` can spawn subprocesses for refresh work.
- `control_plane/dependency_engine.py` can execute package/install commands through its helper path.
- `control_plane/organize_engine.py` can invoke git branch creation through the execution helper.
- `control_plane/qr_pill_orchestrator.py` includes shell-based launch logic.

Assessment:

- These are not automatically defects, but they are the exact places where publication gating and operator approval matter.
- The repo should not claim publication readiness until these paths are either constrained, audited, or explicitly documented as operator-only.

## Publication Gaps

- GUI inventory is real and broad, but the publication plan still needs a single operator-facing readiness story.
- CLI inventory is broad, but shell-spawn paths need sharper trust boundaries.
- Cloudbrain config is centralized, but the knight routing for sync is not fully aligned yet.
- `sir_codex` execution is working for local routing, but cloudbrain sync is not mapped to it.

## Next Execution Tranche

1. Tighten the operator/read-only split in the GUI.
2. Verify the exact cloudbrain sync path and wire it to the right knight lane.
3. Turn the shell-adjacent execution surfaces into an explicit allowlist for publication.
4. Add or update verification coverage for the real publication paths.
