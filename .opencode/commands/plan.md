---
description: Architecture and task breakdown for CAMELOT-OS. Produces an ordered plan with verification steps, no code.
---

Produce a build plan for this task:

1. Run `python -m control_plane.runes.runic_router --rune PLAN --task "$ARGUMENTS"`.
2. Break the work into ordered, implementable tasks with explicit verification per task (lint/typecheck/test/build as applicable).
3. Flag secrets, HUMAN_GATE touchpoints, and risk>=50 areas up front — those need human confirmation and must never be auto-approved.
4. Output the plan only. Do not write code.

Task: $ARGUMENTS
