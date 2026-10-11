# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
scripts/scaffold_canonical_docs.py — Scaffold Canonical Docs L1 to L5
====================================================================
Generates standard canonical documentation files matching document-schema.yaml:
- docs/01-business/BRD.md
- docs/02-product/PRD.md
- docs/03-requirements/SRS.md
- docs/03-requirements/NFR-CATALOG.md
- docs/04-architecture/SAD.md
- docs/05-design/LLDD.md
- docs/06-contracts/CAPABILITY-LEASES.md
- docs/07-experience/VERIFIED-STATE-SEMANTICS.md
- docs/08-verification/TEST-PLAN.md
- docs/09-operations/RUNBOOK.md
- docs/11-traceability/TRACEABILITY-MATRIX.md
- docs/12-reflection/DEBT-REGISTER.md
- docs/13-evidence/EVIDENCE-CATALOG.md
"""

from __future__ import annotations
from pathlib import Path

CAMELOT_HOME = Path(__file__).resolve().parent.parent
DOCS_ROOT = CAMELOT_HOME / "docs"

DOCS = [
    {
        "path": DOCS_ROOT / "01-business" / "BRD.md",
        "content": """---
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
"""
    },
    {
        "path": DOCS_ROOT / "02-product" / "PRD.md",
        "content": """---
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
"""
    },
    {
        "path": DOCS_ROOT / "03-requirements" / "SRS.md",
        "content": """---
document_id: SRS-0001
artifact_type: SRS
version: 4.1.0
status: CANONICAL
authority_layer: L1
owner: sir_codex
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - PRD-0001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - PR-001
  - PR-002
  - PR-003
  - PR-004
contracts: []
code_paths:
  - control_plane/anya_gate.py
  - control_plane/runes/runic_router.py
tests:
  - tests/test_doc_check.py
evidence: []
---

# Software Requirements Specification (SRS)
@ctx|camelot-os.dev/ukg/v10001/requirements/srs @typ|Software_Requirements_Spec id|Ω_SRS_0001

## 1. Functional Requirements
- **FR-001 (Anya Gate Ingress/Egress)**: All incoming intents must be normalized and sanitized by Anya Gate prior to council dispatch; all council output must be synthesized and token-compressed by Anya prior to presentation.
- **FR-002 (Pre-Execution Effect Manifest)**: Every agent action proposing mutations must generate a formal effect manifest specifying target paths, hashes, and operation types.
- **FR-003 (Deterministic Replay Audit)**: Every state mutation recorded in PROVENANCE_LEDGER.md must be replayable deterministically.
- **FR-004 (Position-Addressed VFS)**: Assets must be indexed via vfs://worldtree/ coordinates and staged in 03_VAULT/runtime_state/ prior to permanent crystal promotion.
"""
    },
    {
        "path": DOCS_ROOT / "03-requirements" / "NFR-CATALOG.md",
        "content": """---
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
"""
    },
    {
        "path": DOCS_ROOT / "04-architecture" / "SAD.md",
        "content": """---
document_id: SAD-0001
artifact_type: SAD
version: 4.1.0
status: CANONICAL
authority_layer: L2
owner: merlin_omega
applies_to:
  - Camelot-OS
  - Cybertronia
  - Camelot-VPS
supersedes: []
related:
  - SRS-0001
  - NFR-CATALOG-0001
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - PR-001
  - PR-002
contracts: []
code_paths:
  - control_plane/
  - 01_KERNEL/
  - 04_KINETIC/
tests:
  - tests/test_htmx_webgpu_and_jev.py
evidence: []
---

# System Architecture Document (SAD)
@ctx|camelot-os.dev/ukg/v10001/architecture/sad @typ|System_Architecture_Doc id|Ω_SAD_0001

## 1. The 7-Layer Septem Regna Architecture
```
L7: Modality Hypervisor & User Glass (HTMX, AION-HUD, WebGPU/Vulkan)
L6: Runic Router & Agent Council (Merlin, Helios, Boris, Codex, Sentinel)
L5: Security Perimeters & Z3 Proofs (Paladin Octem, Aegis Shield, WASM Sandboxes)
L4: Transport & Networking Mesh (Go Bifrost Bridge, mTLS, Tailscale Sockets)
L3: Cognitive Kernel & Memory Lattice (Ouroboros 1.58-bit SSM, 24D Leech Lattice)
L2: Kinetic Actuator & Hardware Engine (Rust 1.96, Zig IPC, Reya OS Daemons)
L1: Bare-Metal Substrate (Windows Host, Linux MicroVMs, CoW Memory Slabs)
```

## 2. Distributed Node Topologies
- **Cybertronia (100.118.224.52)**: Primary local Windows orchestrator & local runtime root.
- **VPS Hub / Hermes Prime (100.110.180.18)**: Central cloud relay, background trajectory loop, and persistent DB.
- **Excalibur Mobile Sentinel (100.106.246.126)**: Mobile kinetic cockpit and biometric HITL approval terminal.
"""
    },
    {
        "path": DOCS_ROOT / "05-design" / "LLDD.md",
        "content": """---
document_id: LLDD-0001
artifact_type: LLDD
version: 4.1.0
status: CANONICAL
authority_layer: L3
owner: sir_boris
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - SAD-0001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - FR-001
  - FR-002
contracts: []
code_paths:
  - control_plane/runners/jev_offline_engine.py
  - control_plane/infra/htmx_server.py
tests:
  - tests/test_htmx_webgpu_and_jev.py
evidence: []
---

# Low-Level Detailed Design (LLDD)
@ctx|camelot-os.dev/ukg/v10001/design/lldd @typ|Low_Level_Detailed_Design id|Ω_LLDD_0001

## 1. Engine Components
- **Jev Omega Offline Engine**:
  - `ConfidenceThresholdCircuitBreaker`: Evaluates query confidence against threshold theta >= 0.75; escalates to council upon ambiguity.
  - `IdenticMemoryEventQueue`: Non-blocking async queue decoupling memory persistence from the kinetic execution loop.
  - `CandyEQWrapper`: Emotional calibration wrapper providing conversational warmth without polluting raw WASM execution payloads.
- **HTMX Server & SSE Streaming Engine**:
  - Pure atomic HTML fragment emitter with sub-50ms push updates.
  - Integrated 8 verified UI state badge projection.
"""
    },
    {
        "path": DOCS_ROOT / "06-contracts" / "CAPABILITY-LEASES.md",
        "content": """---
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
"""
    },
    {
        "path": DOCS_ROOT / "07-experience" / "VERIFIED-STATE-SEMANTICS.md",
        "content": """---
document_id: UIUX-SPEC-0001
artifact_type: UIUX_SPEC
version: 4.1.0
status: CANONICAL
authority_layer: L4
owner: sir_boris
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - PR-002
contracts: []
code_paths:
  - control_plane/infra/htmx_server.py
  - apps/pwa/
tests:
  - tests/test_htmx_webgpu_and_jev.py
evidence: []
---

# UI Verified-State Semantics & Machine Specification
@ctx|camelot-os.dev/ukg/v10001/experience/ui_state @typ|UI_State_Machine_Spec id|Ω_UI_STATE_0001

## 1. The 8 Fail-Closed UI States
The Camelot-OS frontend strictly renders one of eight verified state badges downstream of cryptographic receipts:
1. `PENDING`: Awaiting lease clearance or Anya Gate evaluation.
2. `DENIED`: Rejected by Anya Gate or Sentinel invariant audit.
3. `APPROVED`: Validated and signed by human or automated policy.
4. `EXECUTING`: Active kinetic execution within WASM microVM sandbox.
5. `VERIFIED`: Proven by Z3 and recorded in authoritative provenance ledger.
6. `FAILED`: Kinetic run terminated due to exception or timeout.
7. `STALE`: Lease epoch expired or state superseded by newer receipt.
8. `REVOKED`: Manually or automatically revoked by Sentinel authority.
"""
    },
    {
        "path": DOCS_ROOT / "08-verification" / "TEST-PLAN.md",
        "content": """---
document_id: TEST-PLAN-0001
artifact_type: TEST_PLAN
version: 4.1.0
status: CANONICAL
authority_layer: L4
owner: sir_codex
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - ADR-0003
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - FR-001
  - FR-002
contracts: []
code_paths:
  - tests/
tests:
  - tests/test_doc_check.py
  - tests/test_htmx_webgpu_and_jev.py
evidence: []
---

# Master System Test Plan
@ctx|camelot-os.dev/ukg/v10001/verification/test_plan @typ|Master_Test_Plan id|Ω_TEST_PLAN_0001

## 1. Automated Verification Suites
- **Doc-Check Suite (`tests/test_doc_check.py`)**: Validates front-matter schemas, waiver expiries, and ID uniqueness.
- **Engine Suite (`tests/test_htmx_webgpu_and_jev.py`)**: Tests Jev confidence circuit breakers, async memory queues, and HTMX endpoints.
- **Reya OS Suite (`tests/test_reya_*.py`)**: Validates IPC slabs, daemon governors, and multivoice audio fabric.
"""
    },
    {
        "path": DOCS_ROOT / "09-operations" / "RUNBOOK.md",
        "content": """---
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
"""
    },
    {
        "path": DOCS_ROOT / "11-traceability" / "TRACEABILITY-MATRIX.md",
        "content": """---
document_id: TRACE-MATRIX-0001
artifact_type: TRACEABILITY
version: 4.1.0
status: CANONICAL
authority_layer: L5
owner: sir_sentinel
applies_to:
  - Camelot-OS
  - Cybertronia
supersedes: []
related:
  - BRD-0001
  - PRD-0001
  - SRS-0001
implementation_state: COMPLETE
last_verified: 2026-10-04
traces:
  - BR-001
  - BR-002
  - BR-003
  - BR-004
contracts: []
code_paths:
  - docs/
tests:
  - tests/test_doc_check.py
evidence: []
---

# End-to-End Requirements Traceability Matrix
@ctx|camelot-os.dev/ukg/v10001/traceability/matrix @typ|Traceability_Matrix id|Ω_TRACE_MATRIX_0001

| Business Req | Product Req | Functional Req | Automated Test | Evidence Bundle |
| :--- | :--- | :--- | :--- | :--- |
| **BR-001** (Sovereign Self-Hosting) | **PR-001** (Runic CLI) | **FR-001** (Anya Gate) | `tests/test_doc_check.py` | `EVD-DOCS-REFORGE-001` |
| **BR-002** (Edge Scarcity Protocol) | **PR-002** (Bifrost Gateway) | **FR-002** (Effect Manifest) | `tests/test_htmx_webgpu_and_jev.py` | `EVD-DOCS-REFORGE-001` |
| **BR-003** (Zero-Cloud PII) | **PR-003** (Excalibur Cockpit) | **FR-003** (Replay Audit) | `tests/test_agent_slab_sync.py` | `EVD-DOCS-REFORGE-001` |
| **BR-004** (Swarm Convergence) | **PR-004** (Ouroboros 1.58-bit) | **FR-004** (VFS Promotion) | `tests/test_reya_assimilation.py` | `EVD-DOCS-REFORGE-001` |
"""
    },
    {
        "path": DOCS_ROOT / "12-reflection" / "DEBT-REGISTER.md",
        "content": """---
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
"""
    },
    {
        "path": DOCS_ROOT / "13-evidence" / "EVIDENCE-CATALOG.md",
        "content": """---
document_id: EVD-CAT-0001
artifact_type: EVIDENCE
version: 4.1.0
status: CANONICAL
authority_layer: L5
owner: sir_sentinel
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
  - PROVENANCE_LEDGER.md
tests:
  - tests/test_doc_check.py
evidence:
  - EVD-DOCS-REFORGE-001
---

# Cryptographic Evidence Catalog
@ctx|camelot-os.dev/ukg/v10001/evidence/catalog @typ|Evidence_Catalog id|Ω_EVIDENCE_CATALOG_0001

## 1. Attested Evidence Receipts
- **EVD-DOCS-REFORGE-001**: Verification bundle for Documentation Architecture Reforge v4.1.0, covering all 17 automated and review-gated doc-check rules, 16 vertical slices, and 100% test pass.
"""
    }
]

def scaffold_all() -> None:
    for doc in DOCS:
        p: Path = doc["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(doc["content"], encoding="utf-8")
        print(f"Created canonical document: {p.relative_to(CAMELOT_HOME)}")
    print(f"Done! Created {len(DOCS)} canonical documents.")

if __name__ == "__main__":
    scaffold_all()
