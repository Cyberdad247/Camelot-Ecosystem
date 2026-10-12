---
document_id: SLICE-VS-017
artifact_type: SLICE_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L3
owner: lady_apis
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
contracts:
  - CONTRACT-RESEARCH-INTEL-001
code_paths:
  - squires/nullclaw/
  - control_plane/anya_gate.py
tests:
  - tests/test_doc_check.py
evidence: []
---

# VS-017: Research Intelligence & Untrusted Source Admission
@ctx|camelot-os.dev/ukg/v10001/slice/vs-017 @typ|Vertical_Slice_Spec id|Ω_VS_017

## 1. Executive Summary
OSINT intake, untrusted source admission, quarantine tiering (M4 to M1), and bio-kinetic swarm foraging conducted by Lady Apis. Protects the core memory lattice from adversarial injection and hallucinatory drift.

## 2. Invariants & Exit Criteria
- **[INVARIANT]**: Strict quarantine tiering (M4) for untrusted external payloads prior to CAS promotion.
- **[INVARIANT]**: Lossless recovery verification via Golay G24 extended binary coding.
- **[INVARIANT]**: Autonomous bio-kinetic swarm foraging bounded to <= 150 tok/pulse.

## 3. Bound Contracts & Code Paths
- **Contracts**: CONTRACT-RESEARCH-INTEL-001
- **Governed Code Paths**: squires/nullclaw/, control_plane/anya_gate.py
- **Automated Verification**: tests/test_doc_check.py
