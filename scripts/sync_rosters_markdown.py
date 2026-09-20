# SPDX-License-Identifier: MIT
"""Regenerate vfs/rosters.md to harmonize with the full 54-Knight character sheets."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_SRC = ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
ROSTERS_MD = ROOT / "vfs" / "rosters.md"

def main():
    data = json.loads(JSON_SRC.read_text(encoding="utf-8"))
    knights = data.get("knights", {})
    total = len(knights)

    lines = [
        "---",
        "id: rosters",
        "title: Cognitive Cartridge Council & Sovereign Knight Lookup",
        'context: "camelot-os.dev/ukg/v10001/vfs_master_scaffold"',
        "type: Root_Floorplan",
        "---",
        "# Cognitive Cartridge Council",
        f"Master lookup directory of the Sovereign Knight Persona Matrix ({total} Knights).",
        "All Knights tether into the WorldTree Root Node (`a0a4bfb9-e847-4c38-be39-7aee398f0795`) and mirror dynamic state into `vfs://worldtree/knights/<knight_id>/` and `03_VAULT/runtime_state/open_notebook/<knight_id>_tissue.json`.",
        "",
        "> **Full YAML Character Sheets:** [`vfs/roster.yaml`](roster.yaml) and [`03_VAULT/training/configs/knight_character_sheets.yaml`](../03_VAULT/training/configs/knight_character_sheets.yaml)",
        "",
        "## Specialist Omni-Router Matrix",
        "| Knight ID | Domain / Role | Primary Substrate | CloudBrain Node UUID | Summoning Rune |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for kid, info in knights.items():
        name = info.get("name", kid)
        role = info.get("role", info.get("title", "Knight of Camelot"))
        engine = info.get("primary_engine", "Gemini 3.8 Flash")
        uuid = info.get("cloudbrain_uuid", "a0a4bfb9-e847-4c38-be39-7aee398f0795")
        rune = info.get("summoning_rune", f"Omega_{kid.title().replace('_', '')}")
        lines.append(f"| **{kid}** | {role} | {engine} | `{uuid}` | `{rune}` |")

    lines.append("")
    ROSTERS_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated {ROSTERS_MD} with all {total} knights.")

if __name__ == "__main__":
    main()
