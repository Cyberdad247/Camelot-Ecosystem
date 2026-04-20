"""Repository-side ledger update and sync utilities for Camelot-OS."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "PROVENANCE_LEDGER.md"


def ledger_status() -> dict[str, Any]:
    exists = LEDGER_PATH.exists()
    size = LEDGER_PATH.stat().st_size if exists else 0
    tail = ""
    if exists:
        tail = "\n".join(LEDGER_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[-12:])
    return {
        "ledger_path": str(LEDGER_PATH),
        "exists": exists,
        "size_bytes": size,
        "tail": tail,
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
        handle.write(block)
    return {
        "status": "UPDATED",
        "ledger_path": str(LEDGER_PATH),
        "title": title,
        "tag": tag,
    }


async def sync_to_kernel(intent: str, *, kernel_url: str = "http://127.0.0.1:8001") -> dict[str, Any]:
    health_url = f"{kernel_url.rstrip('/')}/health"
    command_url = f"{kernel_url.rstrip('/')}/command"
    async with httpx.AsyncClient(timeout=10.0) as client:
        health = await client.get(health_url)
        health.raise_for_status()
        result = await client.post(command_url, params={"intent": intent})
        result.raise_for_status()
        return {
            "status": "SYNCED",
            "kernel_url": kernel_url,
            "health": health.json(),
            "result": result.json(),
        }
