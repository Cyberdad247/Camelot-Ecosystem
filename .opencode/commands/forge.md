---
description: Kinetic build loop for CAMELOT-OS. Dispatches //FORGE then verifies lint, typecheck, test, build.
---

Dispatch the runic build for this task, then verify it:

1. Run `python -m control_plane.runes.runic_router --rune FORGE --task "$ARGUMENTS"`.
2. For JS changes verify in order: `npm run lint`, `npm run typecheck`, scoped test, build.
3. For Python changes run scoped `pytest tests/<file>.py -x -q` only — never sweep repo root.
4. For Rust changes run `cargo check`, then `cargo test`.
5. Report evidence (commands run + results). Never claim completion without execution output.

Task: $ARGUMENTS
