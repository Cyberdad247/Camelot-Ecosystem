---
document_id: CONTRACT-SPEC-0001
artifact_type: CONTRACT_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L3
owner: sir_sentinel
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - SAD-0001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - FR-002
contracts:
  - CONTRACT-CAPABILITY-LEASE-001
code_paths:
  - control_plane/security/
tests:
  - tests/test_agent_slab_sync.py
evidence: []
---

# Sentinel Capability Leases Specification
@ctx|camelot-os.dev/ukg/v10001/contracts/leases @typ|Contract_Specification id|Ω_CAPABILITY_LEASES_0001

## 1. Lease Model
Every agent operation proposing kinetic side-effects must hold a cryptographically signed capability lease:
- **Principal**: Agent Knight identifier.
- **Resource Path**: Target URI (e.g. vfs://worldtree/crystals/).
- **Permissions**: Bitmask of [READ, WRITE, EXECUTE, ATTEST].
- **TTL**: Strict time-to-live (<= 300s).
- **Epoch**: Monotonically increasing authority counter.
