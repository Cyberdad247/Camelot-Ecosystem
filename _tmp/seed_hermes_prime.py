# -*- coding: utf-8 -*-
"""Seed the hermes_prime_vfs_forge workspace with Hermes_Prime VFS content."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "C:/Users/vizio/CAMELOT_OS")

from notebooklm import NotebookLMClient  # noqa: E402

AUTH = r"C:\Users\vizio\.notebooklm\storage_state.json"
NOTEBOOK_ID = "28f89cb6-5048-4b5d-9e94-376082d24744"
VFS = Path("C:/Users/vizio/CAMELOT_OS/Knights/Hermes_Prime")
FILES = ["soul.md", "spark.md", "harness.md", "skills.md", "merlin_notebook_blend.md"]

PROTOCOL = (
    "HERMES_PRIME_NEXUS — Sovereign MetaCompiler Knight Forge blueprint.\n"
    "ROOT: MERLIN_Ω acts as SYSTEM_2_ORCHESTRATOR.\n"
    "MOD1 (Phial Engine Self-Evolution): continuous R&D loop; symbolect routing "
    "👤(Intent_Seed) ➔ 🧲(Prime_Forage) ➔ 🧪(Hypothesize/Test) ➔ 📈(Evolve_Phial_Weights) ➔ <🏆>(Deploy_Artifact).\n"
    "MOD2 (VFS Artifact Specifications): soul = Pragmatic Realist archetype; spark = MGV framework + AlphaEvolve; "
    "harness = Prime Intellect bridge + tool bindings; skills = symbolect execution paths.\n"
    "Harmony Runes: //SYNC_VFS_WORKSPACE, //FORGE_HERMES_PRIME_FILES, //IGNITE_SELF_EVOLUTION_LOOP.\n"
    "Engine: 01_KERNEL/titan/phials/hermes_prime_phial.py (MGV + Ouroboros + weight re-weighting)."
)


async def main() -> None:
    client = await NotebookLMClient.from_storage(path=AUTH if Path(AUTH).exists() else None)
    async with client:
        nbs = await client.notebooks.list()
        nb = next((n for n in nbs if n.id == NOTEBOOK_ID), None)
        if not nb:
            print(f"[ERROR] notebook {NOTEBOOK_ID} not found in account")
            return
        print(f"[TARGET] {nb.id} | {nb.title}")
        for name in FILES:
            p = VFS / name
            if not p.exists():
                print(f"[SKIP] {name} missing on disk")
                continue
            content = p.read_text(encoding="utf-8")
            await client.sources.add_text(nb.id, content=content, title=f"Hermes_Prime :: {name}")
            print(f"[SOURCE] {name} pushed")
        await client.notes.create(nb.id, title="HERMES_PRIME_NEXUS Protocol", content=PROTOCOL)
        print("[NOTE] protocol note pushed")


if __name__ == "__main__":
    asyncio.run(main())
