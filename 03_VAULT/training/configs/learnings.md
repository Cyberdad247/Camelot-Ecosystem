# Camelot Learnings Log

This file records execution friction, proposed fixes, and review outcomes.
---
## 2026-05-23T18:28:39.550190+00:00 :: SIR_HELIO
- Objective: Synchronize local state to Cloud Brain via //sync
- Failures:
  - Local notebooklm-py CLI fails with 'Authentication expired or invalid'
- Learning: The local python CLI auth token can expire silently, but the MCP ethereal surface retains a separate, radiant auth heartbeat.
- Proposed Mutation: When cloudbrain sync commands fail due to auth expiration, fallback to manual ethereal synchronization using MCP notebook tools instead of halting the ascension.
---
## 2026-06-06T02:20:13.404547+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - write_codex_integration() got an unexpected keyword argument 'ledger'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: write_codex_integration() got an unexpected keyword argument 'ledger'
---
## 2026-06-21T08:01:11.406325+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - All connection attempts failed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: All connection attempts failed
---
## 2026-08-18T19:48:30.789670+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - [ONNXRuntimeError] : 1 : FAIL : Load model from C:\Users\vizio\.cache\chroma\onnx_models\all-MiniLM-L6-v2\onnx\model.onnx failed:bad allocation in upsert.
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: [ONNXRuntimeError] : 1 : FAIL : Load model from C:\Users\vizio\.cache\chroma\onnx_models\all-MiniLM-L6-v2\onnx\model.onnx failed:bad allocation in upsert.
---
## 2026-08-18T19:55:42.068256+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - Page.wait_for_timeout: Target page, context or browser has been closed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: Page.wait_for_timeout: Target page, context or browser has been closed
---
## 2026-08-18T19:55:58.210298+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://notebooklm.google.com/", waiting until "load"

- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://notebooklm.google.com/", waiting until "load"

