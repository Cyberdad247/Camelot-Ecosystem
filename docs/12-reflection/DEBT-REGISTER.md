---
document_id: DEBT-REG-0001
artifact_type: TRACEABILITY
version: 4.1.0
status: CANONICAL
authority_layer: L5
owner: merlin_omega
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces: []
contracts: []
code_paths:
  - docs/
tests:
  - tests/test_doc_check.py
evidence: []
---

# Architectural Debt & Drift Register
@ctx|camelot-os.dev/ukg/v10001/reflection/debt @typ|Technical_Debt_Register id|Ω_DEBT_REGISTER_0001

## 1. Managed Technical Debt
- **DEBT-001 (Legacy Markdown Headers)**: Unmanaged legacy markdown files in `docs/historical/` undergoing staged assimilation under waiver `WAV-2026-001`.
- **DEBT-002 (B904 Lint Debt)**: Non-blocking exception chaining in legacy Python modules scheduled for refactor under v4.2.
