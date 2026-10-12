---
description: Boot sequence for CAMELOT-OS. Rehydrates session state and starts sidecars including opencodex.
---

Boot CAMELOT-OS:

1. Run `python bin/awaken.py --status` first to see current state.
2. If down, run `python -m control_plane.runes.runic_router --rune BOOT --task "$ARGUMENTS"`.
3. Confirm sidecars: CLIProxyAPI (:8080) then opencodex (:10100) via `control_plane/core/ocx_bridge.py` health probes.
4. Report which services are live and which failed with log paths.

Focus: $ARGUMENTS
