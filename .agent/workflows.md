# Workflow Backplane

These workflows map the master bootstrap topology language onto existing
Camelot-OS commands and verification habits.

## NDR+S Genesis Chain

Use for new feature or system integration work.

1. Clarify the target and source of truth.
2. Use `//PLAN` semantics or a written plan for complex work.
3. Implement through SIR_FORGE/Codex-style focused patches.
4. Verify with tests, status probes, or route-specific checks.
5. Run SIR_SENTINEL-style privacy/security review when files or credentials are involved.
6. Let existing hooks handle ledger writes; do not edit provenance ledgers directly.

## Forge-Sting Loop

Use for bug fixes and regressions.

1. Reproduce the failure or inspect the live entrypoint first.
2. Add or identify the smallest verification that would catch the issue.
3. Patch the minimum code or config needed.
4. Re-run the targeted check.
5. Escalate to broader tests only when the touched surface is shared or high risk.

## Harmony Gate Checklist

Use for dashboards, frontend surfaces, and production-facing workflows.

1. Confirm the actual route/app target before editing.
2. Verify visible browser behavior when a UI is changed.
3. Check performance only with real measurements, not fixed HUD claims.
4. Check accessibility, layout stability, and responsive text fit.
5. Confirm secrets remain server-only and are not exposed in client env names.

## Command Mapping

- `//BOOT --hud`: document as `//BOOT` plus dashboard/status verification; no new runtime alias in this pass.
- `//SYNC --mode ALPHA-OMEGA --verify-1bit`: document as `Omega_SYNC`; no new runtime alias in this pass.
- `//FORGE [STACK:Target]`: map to existing `//FORGE <task>`.
- `//SWARM [Task]`: map to existing `//SWARM <task>`.
- `//CONTRACT [Brief]`: queue SIR_FORGE to build the portable package with `python scripts/build_portable.py --test`.
