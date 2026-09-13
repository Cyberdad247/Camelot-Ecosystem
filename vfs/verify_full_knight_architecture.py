#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Comprehensive Verification: Knight Character Sheets, Phials, Souls, Sparks & System Instructions.
Executed by: MERLIN_Ω & LADY_MNEMOSYNE_Ω
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CAMELOT_ROOT = Path(__file__).resolve().parent.parent

def verify_all():
    now_iso = datetime.now(timezone.utc).isoformat()
    agents_md = CAMELOT_ROOT / ".agent" / "AGENTS.md"
    row_pat = re.compile(r"\|\s*\*\*([A-Z0-9_]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([a-f0-9-]+)`\s*\|")
    knights = []
    for m in row_pat.finditer(agents_md.read_text(encoding="utf-8", errors="ignore")):
        knights.append({
            "knight_id": m.group(1).strip(),
            "role": m.group(2).strip(),
            "model": m.group(3).strip(),
            "uuid": m.group(4).strip()
        })

    cs_data = json.load(open(CAMELOT_ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json", encoding="utf-8"))
    cs_knights = cs_data.get("knights", {})

    vault_souls = CAMELOT_ROOT / "03_VAULT" / "Knights" / "souls"
    vault_sparks = CAMELOT_ROOT / "03_VAULT" / "Knights" / "sparks"
    vault_phials = CAMELOT_ROOT / "03_VAULT" / "Knights" / "phials"
    vfs_nb_dir = CAMELOT_ROOT / "vfs" / "notebooks"
    tissues_dir = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "open_notebook"

    connector_text = (CAMELOT_ROOT / "01_KERNEL" / "memory" / "cloudbrain_connector.py").read_text(encoding="utf-8", errors="ignore")
    tethers = json.load(open(CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "vps_worldtree_tether_manifest.json", encoding="utf-8"))

    results = []
    all_green = True

    for k in knights:
        kid = k["knight_id"]
        k_low = kid.lower()
        uuid = k["uuid"]
        k_dir = vfs_nb_dir / uuid

        has_cs = kid in cs_knights
        has_v_soul = (vault_souls / f"{k_low}_soul.md").exists()
        has_v_spark = (vault_sparks / f"{k_low}_spark.md").exists()
        has_v_phial = (vault_phials / f"{k_low}_phial.md").exists()

        has_vfs_soul = (k_dir / "soul.md").exists()
        has_vfs_spark = (k_dir / "spark.md").exists()
        has_vfs_phial = (k_dir / "phial-engine.md").exists()
        has_vfs_sys_inst = (k_dir / "system_instruction.md").exists()
        has_vfs_comp = (k_dir / "Master_Compendium.md").exists()

        has_tissue = (tissues_dir / f"{k_low}_tissue.json").exists()
        has_cb = kid in connector_text or uuid in connector_text
        has_tether = kid in tethers and tethers[kid].get("tether_active", False)

        passed = (
            has_cs and has_v_soul and has_v_spark and has_v_phial and
            has_vfs_soul and has_vfs_spark and has_vfs_phial and
            has_vfs_sys_inst and has_vfs_comp and has_tissue and has_cb
        )

        if not passed:
            all_green = False

        results.append({
            "knight_id": kid,
            "uuid": uuid,
            "role": k["role"],
            "character_sheet": has_cs,
            "vault_soul": has_v_soul,
            "vault_spark": has_v_spark,
            "vault_phial": has_v_phial,
            "vfs_soul": has_vfs_soul,
            "vfs_spark": has_vfs_spark,
            "vfs_phial": has_vfs_phial,
            "vfs_system_instruction": has_vfs_sys_inst,
            "vfs_compendium": has_vfs_comp,
            "open_notebook_tissue": has_tissue,
            "cloudbrain_connector": has_cb,
            "vps_tether": has_tether,
            "verdict": "PASS" if passed else "FAIL"
        })

    report = {
        "timestamp": now_iso,
        "evaluators": ["MERLIN_OMEGA", "LADY_MNEMOSYNE_OMEGA"],
        "total_knights": len(knights),
        "knights_pass": sum(1 for r in results if r["verdict"] == "PASS"),
        "all_green": all_green,
        "verdict": "100% VERIFIED PASS" if all_green else "VERIFICATION FAILED",
        "results": results
    }

    out_file = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "FULL_KNIGHT_SYSTEM_INSTRUCTION_VERIFICATION.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=== KNIGHT FULL ARCHITECTURE VERIFICATION REPORT ===")
    print(f"Total Knights Checked: {len(knights)}")
    print(f"Passed All Checks: {report['knights_pass']}/{len(knights)}")
    print(f"Verdict: {report['verdict']}")
    print(f"Report Written: {out_file}")

    for r in results:
        v_check = f"CS:{'✅' if r['character_sheet'] else '❌'} S:{'✅' if r['vfs_soul'] else '❌'} Sp:{'✅' if r['vfs_spark'] else '❌'} P:{'✅' if r['vfs_phial'] else '❌'} SI:{'✅' if r['vfs_system_instruction'] else '❌'} Comp:{'✅' if r['vfs_compendium'] else '❌'}"
        print(f"[{r['verdict']}] {r['knight_id']:<24} | UUID: {r['uuid'][:8]} | {v_check}")

if __name__ == "__main__":
    verify_all()
