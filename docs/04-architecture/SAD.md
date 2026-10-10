---
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
