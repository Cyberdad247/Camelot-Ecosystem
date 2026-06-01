# [MemPalace L2 NVMe Index] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Initialize a persistent local vector index (L2 MemPalace) using ChromaDB (Rust-core) to enable high-speed retrieval of project memory and success genes.

**Architecture:** We will implement a `MemPalaceL2` class that manages a persistent ChromaDB instance stored on the local NVMe. It will follow the "Wing -> Room -> Drawer" schema from the v1.0 Spec, allowing scoped searches across different projects and knights.

**Tech Stack:** Python, ChromaDB (Rust-core backend), Sentence-Transformers (Local embeddings).

---

### Task 1: MemPalace L2 Scaffolding & Env

**Files:**
- Create: `01_KERNEL/memory/mempalace_l2.py`
- Test: `tests/test_mempalace_l2.py`

**Step 1: Document environment requirement**
*Note: Operator must run `pip install chromadb` separately as per security mandates.*

**Step 2: Write the failing test for L2 initialization**

```python
import pytest
from pathlib import Path
from 01_KERNEL.memory.mempalace_l2 import MemPalaceL2

def test_mempalace_l2_init(tmp_path):
    # This will fail because the module doesn't exist yet
    l2 = MemPalaceL2(storage_path=tmp_path)
    assert l2.client is not None
    assert l2.storage_path == tmp_path
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_mempalace_l2.py`
Expected: FAIL (ModuleNotFoundError)

**Step 4: Implement minimal MemPalaceL2 class**

```python
import chromadb
from pathlib import Path

class MemPalaceL2:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.client = chromadb.PersistentClient(path=str(storage_path))
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_mempalace_l2.py`
Expected: PASS (Requires chromadb in venv)

**Step 6: Commit**

```bash
git add 01_KERNEL/memory/mempalace_l2.py tests/test_mempalace_l2.py
git commit -m "feat(memory): initial MemPalace L2 scaffold"
```

---

### Task 2: Wing/Room/Drawer Schema & Scoped Retrieval

**Files:**
- Modify: `01_KERNEL/memory/mempalace_l2.py`
- Test: `tests/test_mempalace_l2.py`

**Step 1: Write the failing test for scoped search**

```python
def test_scoped_search():
    l2 = MemPalaceL2(storage_path=Path("./tmp_l2"))
    # Add to specific wing/room
    l2.store(wing="camelot", room="audit", content="Success Gene #1", tags=["v1000"])
    
    # Search within scope
    results = l2.search(query="Success", wing="camelot", room="audit")
    assert len(results) > 0
    
    # Search outside scope should be empty
    results_other = l2.search(query="Success", wing="other_project")
    assert len(results_other) == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_mempalace_l2.py`
Expected: FAIL (AttributeError)

**Step 3: Implement `store` and `search` with collection mapping**

```python
def _get_collection_name(self, wing: str, room: str):
    return f"{wing}_{room}"

def store(self, wing, room, content, tags):
    coll = self.client.get_or_create_collection(self._get_collection_name(wing, room))
    # ... insertion logic ...

def search(self, query, wing, room=None):
    # ... retrieval logic ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_mempalace_l2.py`
Expected: PASS

**Step 5: Commit**

```bash
git add 01_KERNEL/memory/mempalace_l2.py
git commit -m "feat(memory): implement scoped Wing/Room retrieval in L2"
```

---

### Task 3: Provenance Integration (Automatic Feeding)

**Files:**
- Modify: `control_plane/provenance.py`
- Modify: `01_KERNEL/memory/mempalace_l2.py`

**Step 1: Add `log_to_mempalace` hook in ProvenanceManager**

**Step 2: Update `log_verification` to automatically index results in the L2 "audit" room.**

**Step 3: Verify via integration test**

**Step 4: Commit**

```bash
git commit -m "feat(governance): link Provenance Ledger to MemPalace L2"
```
