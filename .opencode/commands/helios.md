---
description: Sir Helios NotebookLM link verification for CAMELOT-OS. Checks the tri-brain dynamic source (session, SDK, live probe) without exposing secrets.
---

Verify the NotebookLM link through Sir Helios:

1. Run `python -m control_plane.runes.runic_router --rune HELIOS --task "$ARGUMENTS"`.
2. For raw detail run `python -m control_plane.infra.helios_notebooklm_guard` (add `--offline` for session forensics only, `--no-mirror` to skip tissue writes).
3. Read the verdict: CONNECTED (all three tri-brain consumers fed), DEGRADED (session/SDK present, live probe failed — re-login hints included), OFFLINE (no session or SDK).
4. If DEGRADED/OFFLINE, the remediation is `.venv\Scripts\notebooklm login` — run by the human, never by the agent.

Focus: $ARGUMENTS
