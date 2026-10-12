---
description: Print a CloudBrain retrieval lease scope URI for the VPS hub (offline).
---

Print lease scope for `$ARGUMENTS` (expected `<workspace> <notebook>`):

1. Run `python -m control_plane.infra.vps_hub_client --lease-scope $ARGUMENTS`.
2. Return the `cloudbrain://notebooklm/<workspace>/<notebook>` URI verbatim.

Focus: $ARGUMENTS
