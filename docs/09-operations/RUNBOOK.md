---
document_id: RUNBOOK-0001
artifact_type: RUNBOOK
version: 4.1.0
status: CANONICAL
authority_layer: L4
owner: lukas_omega
applies_to:
  - Camelot-OS
  - Cybertronia
  - Camelot-VPS
supersedes: []
related:
  - SAD-0001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - BR-001
contracts: []
code_paths:
  - bin/awaken.py
tests:
  - tests/test_doc_check.py
evidence: []
---

# Camelot-OS Operational Runbook
@ctx|camelot-os.dev/ukg/v10001/operations/runbook @typ|Operational_Runbook id|Ω_RUNBOOK_0001

## 1. Startup & Awakening
```powershell
# Awaken full system
python bin/awaken.py --status --json

# Launch HTMX Telemetry & Doc-Check Server
python -m control_plane.infra.htmx_server --port 8096

# Run automated doc-check gate
python scripts/doc_check.py run-all
```

## 2. Emergency Failover & Memory Trimming
- If node RSS exceeds 3.5GB, trigger immediate garbage collection and trim working set.
