---
document_id: SLICE-VS-011
artifact_type: SLICE_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L3
owner: sir_boris
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
contracts: ['CONTRACT-LEDGER-PROJECTION-001']
code_paths: ['PROVENANCE_LEDGER.md', 'scripts/sync_provenance.py', 'control_plane/infra/htmx_server.py']
tests: ['tests/test_htmx_webgpu_and_jev.py']
evidence: []
---

# VS-011: Authoritative Ledger & UI State Projection
@ctx|camelot-os.dev/ukg/v10001/slice/vs-011 @typ|Vertical_Slice_Spec id|Ω_VS_011

## 1. Executive Summary
Single root PROVENANCE_LEDGER.md authority and 8 fail-closed UI verified state projections.

## 2. Invariants & Exit Criteria
- **[INVARIANT]**: Mirror drift == 0
- **[INVARIANT]**: Strict 8 verified UI states enforced

## 3. Bound Contracts & Code Paths
- **Contracts**: CONTRACT-LEDGER-PROJECTION-001
- **Governed Code Paths**: PROVENANCE_LEDGER.md, scripts/sync_provenance.py, control_plane/infra/htmx_server.py
- **Automated Verification**: tests/test_htmx_webgpu_and_jev.py
