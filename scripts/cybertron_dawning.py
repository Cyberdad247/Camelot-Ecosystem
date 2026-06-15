# -*- coding: utf-8 -*-
"""Cybertron Dawning Harness for Camelot-OS.

Runs the //DAWNING protocol: OS map audit, Lady M cloudbrain pulse, and
project-isolated workspace scaffolding.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_STATE_DIR = REPO_ROOT / "03_VAULT" / "runtime_state"
DAWNING_STATE_FILE = RUNTIME_STATE_DIR / "cybertron_dawning_latest.json"
DAWNING_SYNC_PAYLOAD_FILE = RUNTIME_STATE_DIR / "cybertron_dawning_sync_payload.json"
PROJECTS_DIR = REPO_ROOT / ".camelot" / "projects"

AUDIT_TARGETS = (
    "01_KERNEL",
    "02_FORGE",
    "03_VAULT",
    "control_plane",
    "scripts",
    ".agent",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_project_name(project_name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", project_name.strip())
    slug = slug.strip("._-")
    return slug or "default_nexus"


def _count_files(path: Path, limit: int = 5000) -> int:
    if not path.exists():
        return 0
    count = 0
    try:
        for child in path.rglob("*"):
            if child.is_file():
                count += 1
                if count >= limit:
                    return count
        return count
    except OSError:
        return -1


def run_os_map_audit() -> dict[str, Any]:
    print("[LUKAS_FORGE] Executing bare-metal OS map audit and topological mapping...")
    nodes = []
    for relative in AUDIT_TARGETS:
        path = REPO_ROOT / relative
        nodes.append(
            {
                "node": relative,
                "exists": path.exists(),
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
                "file_count": _count_files(path),
            }
        )

    audit = {
        "protocol": "CYBERTRON_DAWNING",
        "event_type": "OS_MAP_AUDIT",
        "timestamp": _utc_now(),
        "repo_root": str(REPO_ROOT),
        "nodes": nodes,
    }
    RUNTIME_STATE_DIR.mkdir(parents=True, exist_ok=True)
    DAWNING_STATE_FILE.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print("[LUKAS_FORGE] Mapped 01_KERNEL, 02_FORGE, 03_VAULT, control_plane, scripts, and .agent.")
    return audit


def sync_lady_m(project_name: str, audit: dict[str, Any]) -> dict[str, Any]:
    print("[LADY_M] Synchronizing LanceDB and Trellis fixed KV-pool via cloudbrain pulse...")
    result: dict[str, Any] = {
        "status": "local_recorded",
        "event_type": "DAWNING_SYNC",
        "project": project_name,
        "audit_state": str(DAWNING_STATE_FILE),
    }
    try:
        RUNTIME_STATE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "event_type": "DAWNING_SYNC",
            "command": "//DAWNING",
            "results": {
                "status": "CYBERTRON_CLOUD_BRAIN_SYNC_AND_DAWNING_COMPLETE",
                "project": project_name,
                "audit": audit,
            },
        }
        DAWNING_SYNC_PAYLOAD_FILE.write_text(json.dumps(payload), encoding="utf-8")
        code = (
            "import json, sys; "
            "from pathlib import Path; "
            "from control_plane.cloudbrain_sync import sync_after_event; "
            "payload=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); "
            "sync_after_event(**payload)"
        )
        subprocess.run(
            [sys.executable, "-c", code, str(DAWNING_SYNC_PAYLOAD_FILE)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        )
        result["status"] = "sync_invoked"
        print("[LADY_M] BrainSync CRDT ledger pulse invoked.")
    except subprocess.TimeoutExpired:
        result["status"] = "sync_warn"
        result["warning"] = "cloudbrain sync timed out after 20 seconds"
        print("[WARN] Cloudbrain sync timed out after 20 seconds")
    except subprocess.CalledProcessError as exc:
        result["status"] = "sync_warn"
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        result["warning"] = stderr or stdout or f"cloudbrain sync exited {exc.returncode}"
        print(f"[WARN] Cloudbrain sync exception: {result['warning']}")
    except Exception as exc:  # noqa: BLE001 - sync must not block local dawning.
        result["status"] = "sync_warn"
        result["warning"] = str(exc)
        print(f"[WARN] Cloudbrain sync exception: {exc}")
    return result


def create_project_isolation(project_name: str) -> dict[str, Any]:
    safe_name = _safe_project_name(project_name)
    project_dir = PROJECTS_DIR / safe_name
    project_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "blueprint.md": "# Project Blueprint\n\nCybertron Dawning isolated project surface.\n",
        "task.md": "# Tasks\n\n- [ ] Define the first implementation task.\n",
        "verification.md": "# Verification\n\n- [ ] Record the focused verification command and result.\n",
    }
    for filename, contents in files.items():
        target = project_dir / filename
        if not target.exists():
            target.write_text(contents, encoding="utf-8")

    manifest = {
        "project": safe_name,
        "requested_name": project_name,
        "protocol": "CYBERTRON_DAWNING",
        "created_or_verified_at": _utc_now(),
        "files": sorted(files),
    }
    (project_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[LUKAS_FORGE] Forged unique project directory: {project_dir}")
    return {"project": safe_name, "path": str(project_dir), "manifest": manifest}


def run_dawning(project_name: str = "default_nexus") -> int:
    safe_name = _safe_project_name(project_name)
    print("=== OMEGA BOOT SEQUENCE: //DAWNING ===")
    audit = run_os_map_audit()
    sync_result = sync_lady_m(safe_name, audit)
    project = create_project_isolation(project_name)

    state = {
        **audit,
        "event_type": "DAWNING_COMPLETE",
        "completed_at": _utc_now(),
        "project": project,
        "lady_m": sync_result,
        "pantheon": ["Merlin", "Lady M", "Alex", "Octavian", "Lukas", "Apis", "Sir Codex"],
    }
    DAWNING_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print("=== PANTHEON AWAKENED: Merlin, Lady M, Alex, Octavian, Lukas, Apis, Sir Codex ===")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Camelot-OS //DAWNING protocol.")
    parser.add_argument("project_name", nargs="?", default="default_nexus")
    args = parser.parse_args(argv)
    return run_dawning(args.project_name)


if __name__ == "__main__":
    sys.exit(main())
