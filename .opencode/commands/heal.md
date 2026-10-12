---
description: Self-repair loop for CAMELOT-OS. Diagnoses root cause systematically before fixing.
---

Heal this issue:

1. Run `python -m control_plane.runes.runic_router --rune HEAL --task "$ARGUMENTS"`.
2. Diagnose root cause first (reproduce, isolate, verify) — never guess-fix.
3. Apply the minimal fix, then re-run the failing verification (test, typecheck, or health probe).
4. If the fix touches HUMAN_GATE paths, risk>=50 areas, or protected artifacts, stop and report for human confirmation instead.

Issue: $ARGUMENTS
