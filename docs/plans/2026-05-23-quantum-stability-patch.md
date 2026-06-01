# Ω_QUANTUM_STABILITY_PATCH Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the Sweep-03 architectural hardening: Trellis Recursive Compressor, ChunkKV Semantic Pruning, OpenSRE MCP Hive-Link, and Hybrid J-MoE Recurrence Overlay.

**Architecture:** We will extend the existing Ouroboros Rust engine to support the Hybrid J-MoE overlay (Mamba-2 interleaving) and Trellis fixed-size KV-pool. We will upgrade the Python memory and SRE layers for semantic chunking and MCP-based remediation.

**Tech Stack:** Rust (Ouroboros Engine), Python (SRE/Memory Layers).

---

### Task 1: Trellis KV-Gate (Fixed Memory Pool)

**Files:**
- Modify: `01_KERNEL/reasoning/ouroboros_engine/src/mamba.rs`
- Create: `01_KERNEL/reasoning/ouroboros_engine/src/trellis.rs`
- Test: `01_KERNEL/reasoning/ouroboros_engine/tests/test_trellis.rs`

**Step 1: Write the failing test for Trellis 512MB fixed pool limit**

```rust
use ouroboros_engine::trellis::TrellisPool;

#[test]
fn test_trellis_forget_gate_enforces_limit() {
    let mut pool = TrellisPool::new(512); // 512 MB
    // Simulate exceeding the limit
    pool.allocate_chunk(600);
    assert!(pool.current_usage() <= 512);
    assert_eq!(pool.eviction_count(), 1);
}
```

**Step 2: Run test to verify it fails**

Run: `cargo test -p ouroboros_engine`
Expected: FAIL (unresolved import)

**Step 3: Implement minimal Trellis pool logic**

```rust
pub struct TrellisPool {
    limit_mb: usize,
    current_mb: usize,
    evictions: usize,
}

impl TrellisPool {
    pub fn new(limit: usize) -> Self { Self { limit_mb: limit, current_mb: 0, evictions: 0 } }
    pub fn allocate_chunk(&mut self, size: usize) {
        self.current_mb += size;
        if self.current_mb > self.limit_mb {
            self.current_mb = self.limit_mb;
            self.evictions += 1;
        }
    }
    pub fn current_usage(&self) -> usize { self.current_mb }
    pub fn eviction_count(&self) -> usize { self.evictions }
}
```

**Step 4: Run test to verify it passes**

Run: `cargo test -p ouroboros_engine`
Expected: PASS

**Step 5: Commit**

```bash
git add 01_KERNEL/reasoning/ouroboros_engine/
git commit -m "feat(ouroboros): implement Trellis KV-Gate fixed memory pool"
```

---

### Task 2: ChunkKV Semantic Pruning Integration

**Files:**
- Create: `01_KERNEL/memory/chunk_kv.py`
- Test: `tests/test_chunk_kv.py`

**Step 1: Write the failing test for semantic boundary eviction**

```python
from 01_KERNEL.memory.chunk_kv import ChunkKVPolicy

def test_semantic_boundary_eviction():
    policy = ChunkKVPolicy()
    text = "Sentence 1. Sentence 2. Fragment"
    # Should only evict up to full sentences
    pruned = policy.prune(text, target_tokens=10)
    assert pruned.endswith(".")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_chunk_kv.py`
Expected: FAIL

**Step 3: Implement minimal ChunkKV policy**

```python
class ChunkKVPolicy:
    def prune(self, text: str, target_tokens: int) -> str:
        # Simplistic semantic boundary enforcement: stop at last period
        last_period = text.rfind(".")
        if last_period != -1:
            return text[:last_period + 1]
        return text
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_chunk_kv.py`
Expected: PASS

**Step 5: Commit**

```bash
git add 01_KERNEL/memory/chunk_kv.py tests/test_chunk_kv.py
git commit -m "feat(memory): implement ChunkKV semantic pruning logic"
```

---

### Task 3: MCP Hive-Link for OpenSRE

**Files:**
- Modify: `control_plane/symbiotic_maintenance.py` (or corresponding SRE agent)

**Step 1: Write the failing test for MCP integration**

**Step 2: Update SRE loop to instantiate a basic MCP client for cluster querying**

**Step 3: Commit**

```bash
git add control_plane/symbiotic_maintenance.py
git commit -m "feat(sre): integrate MCP Hive-Link for OpenSRE remediation"
```

---

### Task 4: Recurrence Overlay (Hybrid J-MoE)

**Files:**
- Modify: `01_KERNEL/reasoning/ouroboros_engine/src/lib.rs`

**Step 1: Implement layer interleaving logic (Every 4th layer = Mamba-2)**

**Step 2: Commit**

```bash
git commit -m "feat(ouroboros): implement Hybrid J-MoE layer interleaving"
```
