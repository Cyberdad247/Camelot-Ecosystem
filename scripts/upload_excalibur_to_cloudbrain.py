#!/usr/bin/env python3
"""Upload the v1000-EXCALIBUR-A architecture source to NotebookLM Cloud Brain.

Run after `notebooklm login`:
    .venv/Scripts/python.exe scripts/upload_excalibur_to_cloudbrain.py
"""
import asyncio
import sys
import io
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from notebooklm import NotebookLMClient

REPO = Path(__file__).resolve().parent.parent
SOURCE_FILE = REPO / "docs" / "plans" / "EXCALIBUR_A_cloudbrain_source.md"
NOTEBOOK_TITLE = "Camelot-OS v.1000.0-EXCALIBUR-A"


async def main() -> int:
    content = SOURCE_FILE.read_text(encoding="utf-8")
    client = await NotebookLMClient.from_storage()
    async with client:
        nb = await client.notebooks.create(NOTEBOOK_TITLE)
        print(f"Created notebook {nb.id}  '{nb.title}'")
        src = await client.sources.add_text(
            nb.id,
            "EXCALIBUR-A Architecture & Build State (2026-06-01)",
            content,
            wait=True,
            wait_timeout=120.0,
        )
        sid = getattr(src, "id", src)
        print(f"Added source {sid}")
        print(f"NOTEBOOK_ID={nb.id}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}")
        if "Authentication expired" in str(exc) or "login" in str(exc):
            print("\n>> Run:  .venv/Scripts/notebooklm.exe login   then re-run this script.")
        raise SystemExit(1)
