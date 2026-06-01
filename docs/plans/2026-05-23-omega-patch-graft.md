# OMEGA-PATCH: Phase 1 (Grafting the Core) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate MatMul-free Ternary Logic and Mamba-Mem Linear Recurrence into the Ouroboros Engine to bridge the V1000.0 capability gap.

**Architecture:** We will replace existing FP8 kernels with BitNet b1.58 ternary logic in Rust and overlay the Firnflow memory palace with a Selective State Space Model (SSM) filter for linear context scaling.

**Tech Stack:** Rust (Edition 2024), BitNet b1.58, Mamba-2 SSM, UKG (Universal Knowledge Graph).

---

### Task 1: Ternary Quantizer Refinement

**Files:**
- Modify: `01_KERNEL/reasoning/ouroboros_engine/src/quantizer.rs`
- Test: `01_KERNEL/reasoning/ouroboros_engine/tests/test_quantization.rs`

**Step 1: Write the failing test**
Update `test_bitnet_quantization_clipping` to verify exact ternary output for edge cases.

**Step 2: Run test to verify it fails**
Run: `cargo test --test test_quantization`

**Step 3: Implement minimal code**
Refine the quantizer to strictly enforce the {-1, 0, 1} ternary mapping with hardware-native scaling.

**Step 4: Run test to verify it passes**
Run: `cargo test --test test_quantization`

**Step 5: Commit**
`git commit -m "feat(ouroboros): refine ternary quantizer logic"`

---

### Task 2: Mamba-Firn SSM Recurrence Integration

**Files:**
- Modify: `01_KERNEL/reasoning/ouroboros_engine/src/mamba.rs`
- Modify: `01_KERNEL/reasoning/ouroboros_engine/src/lib.rs`
- Test: `01_KERNEL/reasoning/ouroboros_engine/tests/test_inference.rs`

**Step 1: Write the failing test**
Add `test_ssm_state_persistence` to verify linear state update consistency across long sequences.

**Step 2: Run test to verify it fails**
Run: `cargo test --test test_inference`

**Step 3: Implement minimal code**
Replace the forward pass placeholder with a Selective Scan (SSM) kernel that compresses context into latent summaries.

**Step 4: Run test to verify it passes**
Run: `cargo test --test test_inference`

**Step 5: Commit**
`git commit -m "feat(ouroboros): implement Mamba-Firn linear recurrence"`

---

### Task 3: OMEGA-PATCH Convergence

**Files:**
- Modify: `01_KERNEL/reasoning/ouroboros_bridge.py`
- Test: `01_KERNEL/tests/test_ouroboros_bridge.py`

**Step 1: Write the failing test**
Update the Python bridge test to expect the OMEGA-PATCH capabilities in the status report.

**Step 2: Run test to verify it fails**
Run: `pytest 01_KERNEL/tests/test_ouroboros_bridge.py`

**Step 3: Implement minimal code**
Expose the ternary and SSM capabilities through the Python-to-Rust bridge.

**Step 4: Run test to verify it passes**
Run: `pytest 01_KERNEL/tests/test_ouroboros_bridge.py`

**Step 5: Commit**
`git commit -m "feat(kernel): anchor OMEGA-PATCH in global lattice"`
