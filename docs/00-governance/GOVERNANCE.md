---
document_id: GOV-CONST-001
artifact_type: GOVERNANCE_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L0
owner: architecture.council
applies_to:
  - Camelot-OS
  - Camelot-VPS
  - Cybertronia
  - Excalibur
supersedes:
  - CAMELOT-OS-CONSTITUTION-v1.0
related:
  - GOV-PRECEDENCE-001
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces: []
contracts:
  - camelot-capability-lease/2
  - camelot-receipt/2
code_paths:
  - control_plane/
  - 01_KERNEL/
tests:
  - tests/control_plane/test_agent_slab_sync.py
  - tests/test_doc_check.py
evidence:
  - EVD-CORE-RELEASE-001
---

# Camelot-OS Constitutional Governance & Living Axioms
@ctx|camelot-os.dev/ukg/v10001/governance @typ|Constitutional_Charter id|Ω_GOVERNANCE_V10001

## 🏛️ Prime Constitutional Axioms

```
COGNITION MAY BE DISTRIBUTED.
AUTHORITY MAY NOT.

DO NOT TRUST A FLAG WHEN YOU CAN VERIFY A RECORD.
DO NOT TRUST A MODEL WHEN YOU CAN VERIFY EVIDENCE.
DO NOT TRUST CONNECTIVITY AS PERMISSION.
DO NOT TRUST A SUCCESS RESPONSE AS CANONICAL STATE.
DO NOT DELETE HISTORY TO ROLLBACK.

BIND THE MANIFEST.
ATTENUATE THE LEASE.
FENCE THE EPOCH.
CONSTRAIN THE RUNTIME.
VERIFY THE EVIDENCE.
RESOLVE THE OUTCOME.
ADMIT THE RECEIPT.
PROJECT THE TRUTH.
```

---

## ⚖️ Sovereign Roles & Authority Boundaries

1. **King Arthur (ARTHUR_OMEGA)**: The ultimate human sovereign and root lease authority (Vizion / VaShawn O. Head). Arthur exclusively resolves final lifecycle progressions (`PROMOTE` or `RETREAT`).
2. **Sir Sentinel (SIR_SENTINEL)**: The sole policy evaluation and capability lease attenuation authority. No kinetic, filesystem, or network action may execute without a Sentinel-issued lease token.
3. **Excalibur Mobile Sentinel**: Binds human operator approval directly to exact, immutable `EffectManifest` cryptographic digests over Tailscale mesh.
4. **Sir Gideon (SIR_GIDEON)**: Independent evidence auditor. Audits proof bundles, test receipts, and verification chains without trusting caller assertion flags.
5. **State Service**: Projects admitted Ledger receipts to client viewports and HUDs. The UI cannot infer completion; state is strictly downstream of cryptographic receipts.
6. **Anya Ω (ANYA_FIRST & ANYA_LAST)**: Modality hypervisor and prompt optimizer. Translates intent into formal proposals, but holds zero execution authority on its own (`PROPOSAL_ONLY`).
