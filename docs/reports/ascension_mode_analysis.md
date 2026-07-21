# Ascension Mode Analysis

## Current Reading

Ascension mode should be treated as a governance and readiness state, not an automatic mutation state.

Lady M currently provides:

- squire triage
- dead-artifact purge
- staged repo merge
- briefing generation

For Ascension mode, only the triage and briefing concepts should be active by default. Purge, merge, and external notification should remain separate operator-approved actions.

## Implemented

- `control_plane/ascension_mode.py`
- `bin/ascension_mode.py`
- `tests/control_plane/test_ascension_mode.py`

## What Ascension Mode Measures

- dynamic Camelot version source
- Lady M risk score
- Cloudbrain artifact availability
- selected swarm/governance artifact freshness
- readiness score and state

## Current Recommendation

Use Ascension mode as a report-first command:

```powershell
& .\.venv\Scripts\python.exe bin\ascension_mode.py --root .
```

Then sync the resulting `03_VAULT/runtime_state/ascension_mode_latest.json` through the existing Cloudbrain sync path.

## Effective Implementation Pattern

- Phase 1: read-only analysis
- Phase 2: operator review
- Phase 3: targeted remediation tasks
- Phase 4: ledger reconcile and Cloudbrain sync
- Phase 5: enable execution mode only behind HITL approval

