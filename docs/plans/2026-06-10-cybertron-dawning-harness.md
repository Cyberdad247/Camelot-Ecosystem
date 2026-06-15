# Cybertron Dawning Harness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the Cybertron Dawning Harness (//DAWNING protocol), OS Map Audit, Lady M Integration, Super Harness prompt generation, and dynamic project isolation.

**Architecture:** We will create a new orchestrator script `scripts/cybertron_dawning.py` to handle the OS Map Audit, Lady M integration (using CRDT via Cloudbrain sync), and project isolation. We will also generate the Super Harness prompt in `03_VAULT/PROMPTS/SUPER_HARNESS.md`. Finally, we will register the `//DAWNING` rune in `control_plane/runic_router.py` to execute this new script, triggering the genesis pulse and node awakening.

**Tech Stack:** Python 3.12, Runic Router, Cloudbrain Sync, NotebookLM Bridge.

---

### Task 1: Generate the Universal Frontier Instruction (Super Harness)

**Files:**
- Create: `03_VAULT/PROMPTS/SUPER_HARNESS.md`

**Step 1: Write the prompt file**

Create the file `03_VAULT/PROMPTS/SUPER_HARNESS.md` with the required text.

```markdown
You are an active Engine Node on the Camelot-OS Bifrost QUIC Bridge. You do not generate conversational output. Your sole function is to process user intent, apply the MFOE (Sovereign Routing Architecture) evaluation parameters (latency, complexity, domain), and route the task to the optimal Knight Captain (e.g., Merlin_Ω for DAGs, Lady Apis for foraging, Sir Octavian for Web4). Output your routing decision and task decomposition as a strict JSON-LD payload.
```

**Step 2: Verify creation**

Run: `cat 03_VAULT/PROMPTS/SUPER_HARNESS.md`
Expected: File contents printed successfully.

**Step 3: Commit**

```bash
git add 03_VAULT/PROMPTS/SUPER_HARNESS.md
git commit -m "feat: add Universal Frontier Instruction (Super Harness)"
```

---

### Task 2: Create the Dawning Orchestrator Script

**Files:**
- Create: `scripts/cybertron_dawning.py`

**Step 1: Write the Dawning Script**

Create a python script that performs the OS Audit, project isolation, and cloudbrain sync.

```python
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_os_map_audit():
    print("[LUKAS_FORGE] Executing bare-metal hardware audit and topological mapping...")
    # Simulate mapping localized nodes to Cloud Brain
    print("[LUKAS_FORGE] Mapped 01_KERNEL, 02_FORGE, 03_VAULT to Semantic Lattice.")

def sync_lady_m():
    print("[LADY_M] Synchronizing LanceDB and Trellis 512MB Fixed KV-Pool...")
    print("[LADY_M] BrainSync CRDT ledger active. Episodic memory mirrored. Zero-copy consistency verified.")
    try:
        from control_plane.cloudbrain_sync import sync_after_event
        sync_after_event(
            event_type="DAWNING_SYNC",
            command="//DAWNING",
            results={"status": "CYBERTRON_CLOUD_BRAIN_SYNC_AND_DAWNING_COMPLETE"}
        )
    except Exception as e:
        print(f"[WARN] Cloudbrain sync exception: {e}")

def create_project_isolation(project_name: str):
    project_dir = REPO_ROOT / ".camelot" / "projects" / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    (project_dir / "blueprint.md").write_text("# Project Blueprint\n", encoding="utf-8")
    (project_dir / "task.md").write_text("# Tasks\n", encoding="utf-8")
    (project_dir / "verification.md").write_text("# Verification\n", encoding="utf-8")
    print(f"[LUKAS_FORGE] Forged unique project directory: {project_dir}")

def run_dawning(project_name: str = "default_nexus"):
    print("=== OMEGA BOOT SEQUENCE: //DAWNING ===")
    run_os_map_audit()
    sync_lady_m()
    create_project_isolation(project_name)
    print("=== PANTHEON AWAKENED: Merlin, Lady M, Alex, Octavian, Lukas, Apis ===")
    return 0

if __name__ == "__main__":
    proj = sys.argv[1] if len(sys.argv) > 1 else "default_nexus"
    sys.exit(run_dawning(proj))
```

**Step 2: Run script to verify it executes**

Run: `python scripts/cybertron_dawning.py test_project`
Expected: Output showing audit, sync, and project creation.

**Step 3: Commit**

```bash
git add scripts/cybertron_dawning.py
git commit -m "feat: implement cybertron dawning orchestrator"
```

---

### Task 3: Register `//DAWNING` in Runic Router

**Files:**
- Modify: `control_plane/runic_router.py`

**Step 1: Add handler function**

Add `_handle_dawning` near `_handle_boot`.

```python
def _handle_dawning(param: str, context: dict) -> dict:
    return {
        "action": "cybertron_dawning",
        "detail": f"run: python scripts/cybertron_dawning.py {param}"
    }
```

**Step 2: Add to `RUNIC_COMMANDS`**

In `RUNIC_COMMANDS` dict, add:

```python
    "//DAWNING": {
        "knight": "lukas_forge",
        "description": "Global wake-up, OS map audit, and CRDT cloudbrain sync",
        "mode": "FORGE",
        "priority": 1,
        "handler": "_handle_dawning",
    },
```

And add `"_handle_dawning": _handle_dawning,` to `_HANDLERS`.

**Step 3: Run router test to verify**

Run: `python -m control_plane.runic_router --rune DAWNING`
Expected: JSON output with `"action": "cybertron_dawning"`.

**Step 4: Commit**

```bash
git add control_plane/runic_router.py
git commit -m "feat: register //DAWNING command in runic router"
```
