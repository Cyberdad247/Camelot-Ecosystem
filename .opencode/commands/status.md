---
description: System status for CAMELOT-OS. Reports boot state, service health, and git position.
---

Report CAMELOT-OS status:

1. Run `python -m control_plane.runes.runic_router --rune STATUS --task "$ARGUMENTS"`.
2. Round-trip against live state: `git status`, `git log --oneline -10`, `git branch --show-current`.
3. Summarize service health (Bifrost :3001/health, PWA :3000), queue depth if reported, and any blocked or HUMAN_GATE items.

Focus: $ARGUMENTS
