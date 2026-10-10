---
document_id: ADR-0003
artifact_type: ADR
version: 4.1.0
status: CANONICAL
authority_layer: L2
owner: architecture.council
applies_to:
  - Camelot-OS
  - Camelot-VPS
  - Cybertronia
supersedes:
  - CAMELOT-DOC-ARCH-vNEXT-20260922
related:
  - GOV-CONST-001
  - GOV-PRECEDENCE-001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces: []
contracts: []
code_paths:
  - docs/00-governance/
  - scripts/doc_check.py
tests:
  - tests/test_doc_check.py
evidence:
  - EVD-DOCS-REFORGE-001
---

# ADR-0003: Camelot-OS Documentation Architecture Reforge
@ctx|camelot-os.dev/ukg/v10001/adr/0003 @typ|Architecture_Decision_Record id|Ω_ADR_0003

## Context
Prior documentation across Camelot-OS was rich in constitutional rigor but suffered from fragmented ownership, overlapping scopes, monolithic markdown files, and lack of automated CI verification. This produced context drift during multi-agent collaboration and made programmatic verification difficult.

## Decision
We formally adopt **Documentation Architecture vNEXT — Reforged Baseline v4.1.0**:
1. **Vertical-Slice & Layered Layout**:
   - `docs/00-governance/`: Global constitutional rules and invariants.
   - `docs/01-business/` through `docs/09-operations/`: Clear 10-tier hierarchy with strict Canonical-Home rules.
   - `docs/10-decisions/`: Immutable ADRs.
   - `docs/11-traceability/` through `docs/13-evidence/`: Trace chains and release proofs.
2. **Machine-Checkable Front Matter**:
   Every document file begins with structured YAML front matter validated against `docs/00-governance/document-schema.yaml`.
3. **Automated CI Doc-Check Tooling**:
   17 linting and traceability rules enforced fail-closed via `scripts/doc_check.py`.
4. **Time-Bound Waiver Registry**:
   Legacy documentation paths operate under explicit, time-boxed exceptions declared in `docs/00-governance/WAIVERS.md`.
5. **UI Verified-State Enforcement**:
   UI states are constrained to 8 fail-closed projection states downstream of Ledger receipts: `[PENDING, DENIED, APPROVED, EXECUTING, VERIFIED, FAILED, STALE, REVOKED]`.

## Consequences
* **Positive**: Eliminates documentation drift; turns documentation into an executable software contract; guarantees zero-trust authority boundaries.
* **Negative**: Requires front-matter metadata maintenance and strict doc-check compliance during pull requests.
