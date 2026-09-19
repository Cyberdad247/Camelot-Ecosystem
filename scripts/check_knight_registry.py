#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""CI gate: knight registry consistency (souls, sheets, builder roster).

Checks:
  1. Every canonical soul (1:1 with sheet keys) carries the VERSION tag.
     Legacy/alias souls are info-only.
  2. knight_character_sheets.json total_knights == len(knights).
  3. Builder roster (get_constitutional_knights) drops no sheet keys.

Exit code 0 = registry healthy, 1 = violations found.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "vfs"))
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

def main():
    errors = []

    souls = sorted((ROOT / "03_VAULT" / "Knights" / "souls").glob("*_soul.md"))
    if not souls:
        errors.append("no souls found")

    cs_path = ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
    cs = json.loads(cs_path.read_text(encoding="utf-8"))
    knights = cs.get("knights", {})
    if cs.get("total_knights") != len(knights):
        errors.append(f"total_knights={cs.get('total_knights')} != len(knights)={len(knights)}")

    # Canonical souls map 1:1 to sheet keys (<key.lower()>_soul.md).
    canonical = {f"{k.lower()}_soul.md" for k in knights}
    legacy = 0
    for s in souls:
        if s.name in canonical:
            if VERSION not in s.read_text(encoding="utf-8", errors="ignore"):
                errors.append(f"canonical soul missing tag: {s.name}")
        else:
            legacy += 1

    from build_knight_system_instructions import get_constitutional_knights
    roster = {k["knight_id"] for k in get_constitutional_knights()}
    dropped = [k for k in knights if k not in roster]
    if dropped:
        errors.append(f"builder drops {len(dropped)} sheet keys: {dropped[:5]}")
    nouuid = [k["knight_id"] for k in get_constitutional_knights() if not k["uuid"]]
    if nouuid:
        errors.append(f"roster entries without uuid: {nouuid[:5]}")

    print(f"souls={len(souls)} (legacy/alias={legacy}) sheets={len(knights)} roster={len(roster)} tag={VERSION}")
    if errors:
        print("VIOLATIONS:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("REGISTRY HEALTHY")
    return 0

if __name__ == "__main__":
    sys.exit(main())
