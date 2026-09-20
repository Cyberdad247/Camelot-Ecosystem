# SPDX-License-Identifier: MIT
"""Export Knight Character Sheets from JSON to full YAML format in VFS and Vault."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
JSON_SRC = ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
VFS_YAML = ROOT / "vfs" / "roster.yaml"
VAULT_YAML = ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.yaml"

def main():
    data = json.loads(JSON_SRC.read_text(encoding="utf-8"))
    knights = data.get("knights", {})
    print(f"Loaded {len(knights)} knight character sheets from {JSON_SRC}")

    yaml_header = (
        "# %YAML 1.2\n"
        "# --- SOVEREIGN KNIGHT ROSTER & FULL CHARACTER SHEETS ---\n"
        "# Context: camelot-os.dev/ukg/v10001/knight_roster\n"
        f"# Total Knights: {len(knights)}\n"
        f"# WorldTree Root Tether: {data.get('worldtree_home_uuid')}\n"
        f"# Sovereign Operator: {data.get('sovereign_operator')}\n\n"
    )

    yaml_body = yaml.dump(data, sort_keys=False, allow_unicode=True, indent=2)

    VFS_YAML.write_text(yaml_header + yaml_body, encoding="utf-8")
    print(f"Exported full YAML roster to {VFS_YAML} ({VFS_YAML.stat().st_size:,} bytes)")

    VAULT_YAML.write_text(yaml_header + yaml_body, encoding="utf-8")
    print(f"Exported full YAML character sheets to {VAULT_YAML} ({VAULT_YAML.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
