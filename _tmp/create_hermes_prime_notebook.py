# -*- coding: utf-8 -*-
"""Create (or reuse) the hermes_prime_vfs_forge NotebookLM workspace."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "C:/Users/vizio/CAMELOT_OS")

from notebooklm import NotebookLMClient  # noqa: E402

AUTH = r"C:\Users\vizio\.notebooklm\storage_state.json"
TITLE = "hermes_prime_vfs_forge"


async def main() -> str:
    client = await NotebookLMClient.from_storage(path=AUTH if Path(AUTH).exists() else None)
    async with client:
        nbs = await client.notebooks.list()
        print(f"[AUTH OK] {len(nbs)} notebooks in account")
        for nb in nbs:
            print(f"  - {nb.id} | {nb.title}")
        existing = next((nb for nb in nbs if nb.title.strip().lower() == TITLE.lower()), None)
        if existing:
            print(f"[EXISTS] reusing {existing.id}")
            return existing.id
        nb = await client.notebooks.create(TITLE)
        print(f"[CREATED] {nb.id} | {nb.title}")
        return nb.id


if __name__ == "__main__":
    notebook_id = asyncio.run(main())
    print("NOTEBOOK_ID=" + notebook_id)
