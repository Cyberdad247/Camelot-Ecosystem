---
document_id: SLICE-VS-004
artifact_type: SLICE_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L3
owner: sir_sentinel
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
contracts: ['CONTRACT-CAPABILITY-LEASE-001']
code_paths: ['control_plane/security/', '01_KERNEL/core/aegis_shield/']
tests: ['tests/test_agent_slab_sync.py']
evidence: []
---

# VS-004: Sentinel Authority & Capability Leases
@ctx|camelot-os.dev/ukg/v10001/slice/vs-004 @typ|Vertical_Slice_Spec id|Ω_VS_004

## 1. Executive Summary
Time-bound, attenuated capability leases governing agent permissions and tool calls.

## 2. Invariants & Exit Criteria
- **[INVARIANT]**: Strict lease expiry enforcement
- **[INVARIANT]**: Attenuation inheritance verification

## 3. Bound Contracts & Code Paths
- **Contracts**: CONTRACT-CAPABILITY-LEASE-001
- **Governed Code Paths**: control_plane/security/, 01_KERNEL/core/aegis_shield/
- **Automated Verification**: tests/test_agent_slab_sync.py
