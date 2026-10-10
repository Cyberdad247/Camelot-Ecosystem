---
document_id: GOV-WAIVERS-001
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
code_paths:
  - scripts/doc_check.py
tests:
  - tests/test_doc_check.py
evidence: []
---

# Camelot-OS Governance Waiver & Exception Registry
@ctx|camelot-os.dev/ukg/v10001/waivers @typ|Waiver_Registry id|Ω_WAIVERS_V10001

## 1. Operational Rules
1. **Time-Bound**: Every waiver MUST declare an explicit expiration date ($\le 60\text{ days}$).
2. **Accountability**: Every waiver MUST assign a designated Knight or engineering lead as the remediation owner.
3. **Fail-Closed**: Any expired waiver immediately reverts to `BLOCKING`, halting CI doc-check.
4. **Zero-Waiver Policy for Production**: Production releases (`PRODUCTION_CLEARED`) strictly forbid active waivers in the release scope.

---

## 2. Active Waiver Registry

| Waiver ID | Target Path / Rule | Remediation Owner | Justification | Granted Date | Expiry Date | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **WAV-2026-001** | `docs/historical/` (RULE-01, RULE-02) | `MERLIN_Ω` | Legacy archive docs prior to Reforged Baseline v4.1.0. | 2026-10-04 | 2026-12-04 | **ACTIVE** |
| **WAV-2026-002** | `docs/seeds/` (RULE-03) | `ANYA_Ω` | Initializing prompt seeds and experimental glyph prototypes. | 2026-10-04 | 2026-11-04 | **ACTIVE** |

---

## 3. Waiver Resolution Protocol
Upon reaching remediation, the owner must:
1. Update target files to conform to `docs/00-governance/document-schema.yaml`.
2. Verify with `python scripts/doc_check.py`.
3. Mark waiver status as `REMEDIATED` in this ledger.
