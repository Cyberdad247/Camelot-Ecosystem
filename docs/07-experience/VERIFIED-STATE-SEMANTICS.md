---
document_id: UIUX-SPEC-0001
artifact_type: UIUX_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L4
owner: sir_boris
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - PR-002
contracts: []
code_paths:
  - control_plane/infra/htmx_server.py
  - apps/pwa/
tests:
  - tests/test_htmx_webgpu_and_jev.py
evidence: []
---

# UI Verified-State Semantics & Machine Specification
@ctx|camelot-os.dev/ukg/v10001/experience/ui_state @typ|UI_State_Machine_Spec id|Ω_UI_STATE_0001

## 1. The 8 Fail-Closed UI States
The Camelot-OS frontend strictly renders one of eight verified state badges downstream of cryptographic receipts:
1. `PENDING`: Awaiting lease clearance or Anya Gate evaluation.
2. `DENIED`: Rejected by Anya Gate or Sentinel invariant audit.
3. `APPROVED`: Validated and signed by human or automated policy.
4. `EXECUTING`: Active kinetic execution within WASM microVM sandbox.
5. `VERIFIED`: Proven by Z3 and recorded in authoritative provenance ledger.
6. `FAILED`: Kinetic run terminated due to exception or timeout.
7. `STALE`: Lease epoch expired or state superseded by newer receipt.
8. `REVOKED`: Manually or automatically revoked by Sentinel authority.
