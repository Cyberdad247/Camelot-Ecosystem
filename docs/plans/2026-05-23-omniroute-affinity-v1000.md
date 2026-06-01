# OmniRoute Affinity Routing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement Stateful Affinity Routing and a DualMap-lite SLO escape hatch within the OmniRoute control plane to maximize KV-cache hits.

**Architecture:** We will extend the `cli_intercept.py` and `soul_router.py` logic to hash incoming prompts into `template_id` affinity keys. The router will track TTFT (Time To First Token) SLA per engine and dynamically fallback to load-balancing if an engine becomes a hotspot.

**Tech Stack:** Python (OmniRoute, hashlib, time).

---

### Task 1: Semantic Affinity Key Generation

**Files:**
- Modify: `control_plane/cli_intercept.py`
- Test: `tests/test_affinity_routing.py`

**Step 1: Write the failing test for affinity key generation**

```python
import pytest
from control_plane.cli_intercept import generate_affinity_key

def test_affinity_key_consistency():
    # Identical structural prompts should yield the same affinity key
    prompt1 = "Summarize this file: C:/path/a.py"
    prompt2 = "Summarize this file: C:/path/b.py"
    
    key1 = generate_affinity_key(prompt1)
    key2 = generate_affinity_key(prompt2)
    assert key1 == key2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_affinity_routing.py`
Expected: FAIL (ImportError)

**Step 3: Implement `generate_affinity_key`**

```python
import re
import hashlib

def generate_affinity_key(intent: str) -> str:
    """Generate a cache affinity key by abstracting out dynamic values."""
    # Strip paths, UUIDs, and numbers to find the structural template
    structural = re.sub(r'[a-zA-Z0-9_\-\./]+\.[a-z]{2,4}', '<FILE>', intent)
    structural = re.sub(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '<UUID>', structural)
    structural = re.sub(r'\b\d+\b', '<NUM>', structural)
    
    return hashlib.md5(structural.encode()).hexdigest()[:8]
```

**Step 4: Update `DispatchResult` to include `affinity_key`.**

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_affinity_routing.py`
Expected: PASS

**Step 6: Commit**

```bash
git add control_plane/cli_intercept.py tests/test_affinity_routing.py
git commit -m "feat(omniroute): implement semantic affinity key generation"
```

---

### Task 2: DualMap-lite SLO Escape Hatch

**Files:**
- Modify: `control_plane/soul_router.py`

**Step 1: Add a simulated TTFT tracking dictionary to the SoulRouter class.**

**Step 2: Update the routing logic to check if the target engine's TTFT breaches the SLO threshold (e.g., > 2000ms).**

**Step 3: If breached, fallback to the next available engine in the `fallback_models` list, appending `[DUALMAP_ESCAPE]` to the reason.**

**Step 4: Commit**

```bash
git add control_plane/soul_router.py
git commit -m "feat(omniroute): implement DualMap-lite TTFT SLO escape hatch"
```
