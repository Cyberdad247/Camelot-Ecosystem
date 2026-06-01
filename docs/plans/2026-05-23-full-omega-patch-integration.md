# OMEGA-PATCH: Full Architectural Convergence Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bridge the remaining "Dark" capability gaps in the V1000.0 memory and inference layers by implementing HMAC salting, speculative autotuning, and LSM-tree tiered storage.

**Architecture:** We will implement a three-pillar convergence strategy: (1) Hardening multi-tenant isolation via HMAC-SHA256 cache salting. (2) Gating inference overhead through a hardware-aware speculative autotuner. (3) Optimizing KV-cache prefetching using an LSM-tree tiered storage policy.

**Tech Stack:** Rust (Edition 2024), Python (3.13), HMAC-SHA256, SGLang-LSM logic, Z3 Logic Gates.

---

### Task 1: HMAC-SHA256 Cache Salting (Isolation Hardening)

**Files:**
- Modify: `01_KERNEL/memory/mempalace_l2.py`
- Test: `tests/test_mempalace_security.py`

**Step 1: Write the failing test**
Create `test_cache_salting_collision_resistance` to verify that two tenants with identical prefixes but different IDs produce distinct cache keys.

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_mempalace_security.py`
Expected: FAIL (Keys will be identical without salting).

**Step 3: Implement minimal code**
Integrate `hmac.new()` with a system-level secret and the `tenant_id` into the cache key generation logic.

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_mempalace_security.py`
Expected: PASS.

**Step 5: Commit**
`git commit -m "feat(security): implement HMAC-SHA256 cache salting for tenant isolation"`

---

### Task 2: Hardware-Aware Speculative Autotuner

**Files:**
- Create: `01_KERNEL/merlin/Engines/speculative_autotuner.py`
- Modify: `01_KERNEL/merlin/Engines/merlin_llm.py`
- Test: `tests/test_speculative_autotuner.py`

**Step 1: Write the failing test**
Add a test that simulates a low accept rate (< 0.2) and verifies that the autotuner disables speculative decoding for that model/hardware combo.

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_speculative_autotuner.py`

**Step 3: Implement minimal code**
Implement the `SpeculativeAutotuner` class that tracks `accept_rate` statistics and gates the `draft_model` usage based on a profit-loss latency matrix.

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_speculative_autotuner.py`

**Step 5: Commit**
`git commit -m "feat(inference): add hardware-aware speculative autotuner gating"`

---

### Task 3: LSM-Tree KV Tiered Storage Policy

**Files:**
- Create: `01_KERNEL/memory/lsm_kv_policy.py`
- Modify: `01_KERNEL/merlin/context/cache_manager.py`
- Test: `tests/test_lsm_kv_storage.py`

**Step 1: Write the failing test**
Add `test_lsm_tiered_compaction` to verify that cold KV blocks are correctly merged and compressed into the next storage tier without loss of semantic metadata.

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_lsm_kv_storage.py`

**Step 3: Implement minimal code**
Implement the LSM-tree style tiered management policy (levels 0-2) for the `CacheManager`, prioritizing prefetching for high-hotness prefix blocks.

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_lsm_kv_storage.py`

**Step 5: Commit**
`git commit -m "feat(memory): implement LSM-tree tiered storage policy for KV-cache"`

---

### Task 4: Final Convergence & Lattice Anchor

**Files:**
- Modify: `03_VAULT/PROVENANCE_LEDGER.md`
- Modify: `01_KERNEL/ARCHITECTURE.md`

**Step 1: Verify all tests**
Run: `pytest tests/` and `cargo test`

**Step 2: Update Architecture status**
Set status to `V1000.0_CONVERGED_COSMIC`.

**Step 3: Commit**
`git commit -m "chore: final OMEGA-PATCH convergence and epoch anchoring"`
