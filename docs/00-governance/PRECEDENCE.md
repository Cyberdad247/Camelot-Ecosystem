---
document_id: GOV-PRECEDENCE-001
artifact_type: GOVERNANCE_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L0
owner: architecture.council
applies_to:
  - Camelot-OS
  - Camelot-VPS
  - Cybertronia
supersedes: []
related:
  - GOV-CONST-001
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces: []
contracts: []
code_paths: []
tests:
  - tests/test_doc_check.py
evidence: []
---

# Camelot-OS Document Precedence Hierarchy
@ctx|camelot-os.dev/ukg/v10001/precedence @typ|Precedence_Charter id|Ω_PRECEDENCE_V10001

## 📌 The 6-Layer Authority Hierarchy

When any conflict or ambiguity arises between documents or architectural descriptions, the following hierarchy is strictly enforced (higher layer supersedes lower):

```
Layer L0: Constitutional Governance (docs/00-governance/)
   │  └── Overrides all business, technical, and operational claims.
   ▼
Layer L1: Strategic Intent & Requirements (docs/01-business/, docs/02-product/, docs/03-requirements/)
   │  └── Governs what is built; cannot violate L0 constitutional boundaries.
   ▼
Layer L2: Macro-Architecture & Context (docs/04-architecture/, docs/10-decisions/)
   │  └── Specifies system boundaries, node topology, and hardware invariants.
   ▼
Layer L3: Detailed Design & Contracts (docs/05-design/, docs/06-contracts/)
   │  └── Machine-readable schemas, state machines, and RPC specifications.
   ▼
Layer L4: Operations & Experience (docs/07-experience/, docs/08-verification/, docs/09-operations/)
   │  └── UI semantics, test plans, runbooks, and deployment scripts.
   ▼
Layer L5: Reflection & Telemetry (docs/11-traceability/, docs/12-reflection/, docs/13-evidence/)
      └── Historical drift records, tech debt registers, and release proofs.
```

---

## ⚡ Canonical Conflict Resolution Rule
1. **No Downstream Redefinition**: An L3 or L4 document must never redefine a rule, term, or boundary declared in an L0, L1, or L2 document.
2. **Canonical-Home Rule**: Every architectural concern belongs to exactly one canonical document (e.g. non-functional requirements live strictly in `03-requirements/NFR-CATALOG.md`). All other documents link to it.
