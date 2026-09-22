---
description: Cybertronia VPS hub status for CAMELOT-OS. Reports vendored contracts, endpoints, and CloudBrain lease scope without touching the live hub.
---

Report VPS hub bridge status:

1. Run `python -m control_plane.runes.runic_router --rune VPS_HUB --task "$ARGUMENTS"`.
2. For raw detail run `python -m control_plane.infra.vps_hub_client --status`.
3. To validate a local artifact against a hub contract: `python -m control_plane.infra.vps_hub_client --validate <schema> <file>`.
4. Never add `--live` without explicit human approval — live TCP probes hit the production hub.

Focus: $ARGUMENTS
