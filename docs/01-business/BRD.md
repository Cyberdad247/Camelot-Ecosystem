---
document_id: BRD-0001
artifact_type: BRD
version: 4.1.0
status: CANONICAL
authority_layer: L1
owner: arthur_omega
applies_to:
  - Camelot-OS
  - Cybertronia
  - Camelot-VPS
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

# Business Requirements Document (BRD)
@ctx|camelot-os.dev/ukg/v10001/business/brd @typ|Business_Requirements_Doc id|Ω_BRD_0001

## 1. Sovereign Vision & Purpose
Camelot-OS is a sovereign agentic operating system designed to run on personal edge hardware with absolute local privacy, zero cloud lock-in, and thermodynamic execution efficiency.

## 2. Business Requirements
- **BR-001 (Sovereign Self-Hosting)**: The core operating system must be capable of bootstrapping, routing, and executing agentic workflows without internet connectivity.
- **BR-002 (Edge Scarcity Protocol)**: Edge nodes must enforce a strict 4GB RAM ceiling (4096 MB max working set), reserving up to 8GB only for the central sovereign server hub.
- **BR-003 (Zero-Cloud PII Protection)**: User secrets, cryptographic keys, and personal credentials must never be transmitted across cloud LLM APIs; all secret scanning routes via SIR_GHOST.
- **BR-004 (Multi-Agent Swarm Convergence)**: Knights must collaborate via compressed symbolic RPC (Triple-QFT Symbolect) to eliminate token waste and guarantee verifiable execution state.
