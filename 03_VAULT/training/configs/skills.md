# Camelot Shared Skills Registry

Approved evolution rules are appended here after governance review.
---
## 2026-05-23T18:28:39.551699+00:00 :: SIR_HELIO
- Objective: Synchronize local state to Cloud Brain via //sync
- Learning: The local python CLI auth token can expire silently, but the MCP ethereal surface retains a separate, radiant auth heartbeat.
- Approved Rule: When cloudbrain sync commands fail due to auth expiration, fallback to manual ethereal synchronization using MCP notebook tools instead of halting the ascension.
- Verification:
  - `Verify mcp_notebooklm_note list succeeds when local CLI fails.`
- Scope:
  - control_plane/cloudbrain_sync.py
