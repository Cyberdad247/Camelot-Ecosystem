---
document_id: SLICE-VS-009
artifact_type: SLICE_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L3
owner: lukas_omega
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - ADR-0003
  - GOV-CONST-001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces: []
contracts: ['CONTRACT-EXEC-RUNTIME-001']
code_paths: ['04_KINETIC/', '02_FORGE/kinetic/', 'control_plane/rtk/']
tests: ['tests/test_reya_assimilation.py', 'tests/test_reya_handshake_protocol.py']
evidence: []
---

# VS-009: Bare-Metal Kinetic Execution Runtime
@ctx|camelot-os.dev/ukg/v10001/slice/vs-009 @typ|Vertical_Slice_Spec id|Ω_VS_009

## 1. Executive Summary
Native Linux/Windows process control, CoW microVMs, WASM32 sandboxing, and 4GB RAM limits.

## 2. Invariants & Exit Criteria
- **[INVARIANT]**: Node working set strictly <= 4096MB
- **[INVARIANT]**: 0% Python on kinetic hotpath

## 3. Bound Contracts & Code Paths
- **Contracts**: CONTRACT-EXEC-RUNTIME-001
- **Governed Code Paths**: 04_KINETIC/, 02_FORGE/kinetic/, control_plane/rtk/
- **Automated Verification**: tests/test_reya_assimilation.py, tests/test_reya_handshake_protocol.py
