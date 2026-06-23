"""Repository-side ledger update and sync utilities for Camelot-OS."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "PROVENANCE_LEDGER.md"
MIRROR_LEDGER_PATHS = [
    REPO_ROOT / "03_VAULT" / "PROVENANCE_LEDGER.md",
    REPO_ROOT / "03_VAULT" / "training" / "configs" / "PROVENANCE_LEDGER.md",
    REPO_ROOT / "docs" / "PROVENANCE_LEDGER.md",
]


def _read_bifrost_token() -> str | None:
    token_path = Path.home() / ".camelot" / "bifrost.token"
    try:
        token = token_path.read_text(encoding="ascii").strip()
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None
    return token or None


def ledger_status() -> dict[str, Any]:
    exists = LEDGER_PATH.exists()
    size = LEDGER_PATH.stat().st_size if exists else 0
    tail = ""
    mirrors = []
    if exists:
        root_text = LEDGER_PATH.read_text(encoding="utf-8", errors="replace")
        tail = "\n".join(root_text.splitlines()[-12:])
        mirrors = [
            {
                "path": str(path),
                "exists": path.exists(),
                "aligned": path.exists() and path.read_text(encoding="utf-8", errors="replace") == root_text,
            }
            for path in MIRROR_LEDGER_PATHS
        ]
    return {
        "ledger_path": str(LEDGER_PATH),
        "exists": exists,
        "size_bytes": size,
        "tail": tail,
        "mirrors": mirrors,
        "mirrors_aligned": bool(mirrors) and all(item["aligned"] for item in mirrors),
    }


def append_provenance_entry(*, title: str, actor: str, scope: list[str], verification: list[str], tag: str) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y-%m-%d")
    block_lines = [
        "---",
        f"## [{timestamp}] {title}",
        f"- **Actor**: {actor}",
        "- **Scope**:",
    ]
    block_lines.extend(f"  - {item}" for item in scope)
    block_lines.append("- **Verification performed**:")
    block_lines.extend(f"  - `{item}`" for item in verification)
    block_lines.append(f"- **Tag**: {tag}")
    block = "\n".join(block_lines) + "\n"
    with LEDGER_PATH.open("a", encoding="utf-8") as handle:
        if LEDGER_PATH.stat().st_size > 0:
            with LEDGER_PATH.open("rb") as reader:
                reader.seek(-1, 2)
                if reader.read(1) != b"\n":
                    handle.write("\n")
        handle.write(block)
    return {
        "status": "UPDATED",
        "ledger_path": str(LEDGER_PATH),
        "title": title,
        "tag": tag,
    }


def reconcile_ledger_mirrors() -> dict[str, Any]:
    """Copy the root provenance ledger to tracked mirror locations."""
    if not LEDGER_PATH.exists():
        return {"status": "MISSING_ROOT_LEDGER", "ledger_path": str(LEDGER_PATH), "mirrors": []}

    root_text = LEDGER_PATH.read_text(encoding="utf-8", errors="replace")
    mirrors: list[dict[str, Any]] = []
    for path in MIRROR_LEDGER_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        before = path.read_text(encoding="utf-8", errors="replace") if path.exists() else None
        if before != root_text:
            path.write_text(root_text, encoding="utf-8")
            action = "updated" if before is not None else "created"
        else:
            action = "already_aligned"
        mirrors.append({"path": str(path), "action": action, "aligned": True})

    return {
        "status": "RECONCILED",
        "ledger_path": str(LEDGER_PATH),
        "mirrors": mirrors,
        "mirrors_aligned": True,
    }


async def sync_to_kernel(intent: str, *, kernel_url: str = "http://127.0.0.1:8001") -> dict[str, Any]:
    health_url = f"{kernel_url.rstrip('/')}/health"
    dispatch_url = f"{kernel_url.rstrip('/')}/agent/dispatch"
    token = _read_bifrost_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["x-camelot-token"] = token
    async with httpx.AsyncClient(timeout=10.0) as client:
        health = await client.get(health_url)
        health.raise_for_status()
        result = await client.post(
            dispatch_url,
            headers=headers,
            json={"intent": intent, "agent_id": "MERLIN", "execution_target": "ledger_sync"},
        )
        result.raise_for_status()
        return {
            "status": "SYNCED",
            "kernel_url": kernel_url,
            "dispatch_url": dispatch_url,
            "auth": "token" if token else "missing",
            "health": health.json(),
            "result": result.json(),
        }
