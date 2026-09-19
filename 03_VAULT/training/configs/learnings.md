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

---
## 2026-08-24T14:38:11.344942+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - Page.wait_for_timeout: Target page, context or browser has been closed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: Page.wait_for_timeout: Target page, context or browser has been closed
---
## 2026-08-24T14:39:12.558846+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - Page.wait_for_timeout: Target page, context or browser has been closed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: Page.wait_for_timeout: Target page, context or browser has been closed
---
## 2026-09-08T15:09:19.254322+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - MEMPALACE_SECRET is not set. MemPalaceL2 requires it to salt HMAC drawer IDs; refusing to use a hardcoded fallback. Generate one with: python -c "import secrets; print(secrets.token_hex(32))" and export it in the environment.
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: MEMPALACE_SECRET is not set. MemPalaceL2 requires it to salt HMAC drawer IDs; refusing to use a hardcoded fallback. Generate one with: python -c "import secrets; print(secrets.token_hex(32))" and export it in the environment.
---
## 2026-09-10T17:07:51.041798+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - MEMPALACE_SECRET is not set. MemPalaceL2 requires it to salt HMAC drawer IDs; refusing to use a hardcoded fallback. Generate one with: python -c "import secrets; print(secrets.token_hex(32))" and export it in the environment.
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: MEMPALACE_SECRET is not set. MemPalaceL2 requires it to salt HMAC drawer IDs; refusing to use a hardcoded fallback. Generate one with: python -c "import secrets; print(secrets.token_hex(32))" and export it in the environment.
---
## 2026-09-10T17:59:07.364832+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - MEMPALACE_SECRET is not set. MemPalaceL2 requires it to salt HMAC drawer IDs; refusing to use a hardcoded fallback. Generate one with: python -c "import secrets; print(secrets.token_hex(32))" and export it in the environment.
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: MEMPALACE_SECRET is not set. MemPalaceL2 requires it to salt HMAC drawer IDs; refusing to use a hardcoded fallback. Generate one with: python -c "import secrets; print(secrets.token_hex(32))" and export it in the environment.
---
## 2026-09-13T13:39:18.156664+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'compliant'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'compliant'
---
## 2026-09-13T13:39:40.754542+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'ScarcityGuardian' object has no attribute 'host_role'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'ScarcityGuardian' object has no attribute 'host_role'
---
## 2026-09-13T13:39:59.148979+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'AuthorityVector' object has no attribute 'tuple'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'AuthorityVector' object has no attribute 'tuple'
---
## 2026-09-13T13:40:44.985238+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'BoundedExecutionEnvelope' object has no attribute 'success'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'BoundedExecutionEnvelope' object has no attribute 'success'
---
## 2026-09-13T13:41:02.336934+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'Receipt' object has no attribute 'block_height'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'Receipt' object has no attribute 'block_height'
---
## 2026-09-13T13:41:39.849307+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'IdempotencyDecision' object has no attribute 'status'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'IdempotencyDecision' object has no attribute 'status'
---
## 2026-09-13T13:41:55.688347+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'str' object has no attribute 'value'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'str' object has no attribute 'value'
---
## 2026-09-13T13:42:05.060486+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'GideonVerdict' object has no attribute 'risk_tier'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'GideonVerdict' object has no attribute 'risk_tier'
---
## 2026-09-13T13:42:42.506842+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - 'ArthurResolution' object has no attribute 'status'
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: 'ArthurResolution' object has no attribute 'status'
---
## 2026-09-17T14:59:28.742441+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - All connection attempts failed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: All connection attempts failed
---
## 2026-09-18T02:16:59.879989+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - Page.wait_for_timeout: Target page, context or browser has been closed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: Page.wait_for_timeout: Target page, context or browser has been closed
---
## 2026-09-18T02:21:51.552793+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - Page.wait_for_timeout: Target page, context or browser has been closed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: Page.wait_for_timeout: Target page, context or browser has been closed
---
## 2026-09-19T00:12:43.508298+00:00 :: SIR_BORIS
- Objective: Global CLI Execution
- Failures:
  - Page.wait_for_timeout: Target page, context or browser has been closed
- Learning: Caught unhandled exception in main loop.
- Proposed Mutation: Patch affected path and implement guardrail for: Page.wait_for_timeout: Target page, context or browser has been closed
