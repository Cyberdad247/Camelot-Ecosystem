# Architecture Reference: MicroVM Boot Constraints & Minimal Executable Boundaries

**Document ID:** `CAMELOT-ARCH-REF-MICROVM-512B`  
**Classification:** Design Constraint / Academic Reference (Non-Deployed)  
**Baseline Anchor:** `CAMELOT-DOC-BASELINE-v3.4.2-20261011`  
**Origin:** Extracted from Assimilation Analysis: State Attestation Manifest (DST/MCR #8)  
**Date:** 2026-10-11  

---

## 1. Abstract & Provenance

This document records the lower-bound execution boundary model inspired by Oscar Toledo Gutiérrez's 512-byte x86 assembly constraint as an architectural reference for Camelot-OS microVM and WASM edge pills. 

> [!NOTE]
> **Engineering Boundary Notice:** This model is strictly an **architectural reference** and theoretical constraint floor. It is **not deployed** via Kernel Copy-on-Write (CoW) page sharing. Any future implementation requires explicit test receipts, benchmarks, and formal Z3 verification under the Paladin Octem gate.

---

## 2. The Toledo 512-Byte Constraint Model

In *Programming Boot Sector Games*, Oscar Toledo Gutiérrez demonstrated that complete, interactive game loops and state machines can execute within the historical BIOS boot sector limit:

* **Size Constraint:** Exactly $\le 512$ bytes of binary code and data.
* **Physical Address:** Loaded by BIOS into memory address `0x0000:0x7C00`.
* **Execution Mode:** 16-bit x86 Real Mode.
* **Termination Signature:** Word `0xAA55` at byte offsets 510–511.

```text
+-------------------------------------------------------+---------+
| Executable Real-Mode Machine Code & State (510 Bytes) | 0x55AA  |
+-------------------------------------------------------+---------+
0x7C00                                                  0x7DFE   0x7DFF
```

---

## 3. Applicability to Camelot-OS Edge Runtimes

Within the Camelot-OS 4 GB RAM edge-node architecture, the 512-byte model serves as a boundary condition for:

1. **Minimal-Footprint "Digital RNA":**
   Establishing a design floor for sub-millisecond ephemeral task runners (Nano-Knights, Squire probes).
2. **WASM Micro-Payload Headers:**
   Serving as an analogy for bare-minimum initialization vectors in WASI sandboxes without standard library bloat (Rule 7 Zero Hotpath Bloat compliance).
3. **Hardware-Constrained MicroVM Bootstrapping:**
   Informing lightweight bootloader envelopes for virtualized isolated execution units.

---

## 4. Architectural Guardrails & Invariants

* **No Kernel Modification:** No custom OS kernel drivers or unsafe CoW memory hacks are assumed or authorized.
* **Zero Hotpath Bloat (Rule 7):** Edge execution must rely on native Rust/Go/WASM primitives rather than heavy interpreted runtimes.
* **Memory Ceiling (Global Law 03):** Edge drones must strictly operate within the 4 GB RAM node ceiling, with proactive pruning triggered at 3.6 GB.
