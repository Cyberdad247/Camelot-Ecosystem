---
description: Validate a local JSON artifact against a vendored VPS hub contract (offline, fail-closed).
---

Validate `$ARGUMENTS` (expected `<schema> <file>`):

1. Run `python -m control_plane.infra.vps_hub_client --validate $ARGUMENTS`.
2. Require `ok: true` with zero errors. Report schema `$id` on success.
3. On failure report each `path: message` error; do not retry with a different schema unasked.

Focus: $ARGUMENTS
