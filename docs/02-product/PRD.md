---
document_id: PRD-0001
artifact_type: PRD
version: 4.1.0
status: CANONICAL
authority_layer: L1
owner: sir_boris
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - BRD-0001
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - BR-001
  - BR-002
  - BR-003
  - BR-004
contracts: []
code_paths:
  - apps/pwa/
  - control_plane/
tests:
  - tests/test_htmx_webgpu_and_jev.py
evidence: []
---

# Product Requirements Document (PRD)
@ctx|camelot-os.dev/ukg/v10001/product/prd @typ|Product_Requirements_Doc id|Ω_PRD_0001

## 1. Product Capabilities
- **PR-001 (Runic CLI & Agent Cockpit)**: Single entry-point runic dispatcher (//HELIOS, //FORGE, //SWARM, //CONTEXT, //STATUS) driving multi-agent workflows.
- **PR-002 (Bifrost Gateway & Hypermedia UI)**: Real-time SSE telemetry and atomic HTML fragment swapping via HTMX, purging client-side Virtual DOM overhead.
- **PR-003 (Excalibur Mobile Tether)**: Remote mobile monitoring, live telemetry cockpit, and biometric HITL approval loop over authenticated Tailscale mesh.
- **PR-004 (Ouroboros 1.58-bit Offline Inference)**: Local System-2 offline reasoning using ternary weights with sub-second response times on CPU/WASM.
