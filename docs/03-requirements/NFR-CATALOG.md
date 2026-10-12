---
document_id: NFR-CATALOG-0001
artifact_type: SRS
version: 4.1.0
status: CANONICAL
authority_layer: L1
owner: sir_sentinel
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - SRS-0001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - BR-002
  - BR-003
contracts: []
code_paths:
  - control_plane/rtk/
tests:
  - tests/test_doc_check.py
evidence: []
---

# Non-Functional Requirements Catalog
@ctx|camelot-os.dev/ukg/v10001/requirements/nfr @typ|NFR_Catalog id|Ω_NFR_CATALOG_0001

## 1. Quality Invariants
- **NFR-RAM-EDGE**: Node working set memory must never exceed 4096 MB (enforced by working set trimming).
- **NFR-RAM-SERVER**: Central Sovereign Server Hub memory must never exceed 8192 MB.
- **NFR-HOTPATH-RULE-7**: Zero percent (0%) Python or Node.js in the kinetic hotpath; 100% native Rust, Go, Zig, or WASM.
- **NFR-LATENCY-BIFROST**: Inter-node message transit latency must remain under 12 ms over Tailscale mesh.
- **NFR-UI-PROJECTION**: UI states must strictly map to the 8 fail-closed projection states downstream of cryptographic receipts.
