# Camelot Learnings Log

This file records execution friction, proposed fixes, and review outcomes.
---
## 2026-05-23T18:28:39.550190+00:00 :: SIR_HELIO
- Objective: Synchronize local state to Cloud Brain via //sync
- Failures:
  - Local notebooklm-py CLI fails with 'Authentication expired or invalid'
- Learning: The local python CLI auth token can expire silently, but the MCP ethereal surface retains a separate, radiant auth heartbeat.
- Proposed Mutation: When cloudbrain sync commands fail due to auth expiration, fallback to manual ethereal synchronization using MCP notebook tools instead of halting the ascension.
