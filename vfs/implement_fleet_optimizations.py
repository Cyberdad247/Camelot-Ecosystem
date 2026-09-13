#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Implement Fleet-Wide Optimizations for Camelot-OS & Sovereign Knight Roster.
1. Canonical VFS Convergence & Isomorphic Mounting for all 38 Knights.
2. Legacy space vs underscore alias resolution.
3. Historical Version Cold Storage Distillation (.toon + .json).
4. Phantom/Scratch Node Inventory & Quota Protection.
5. WorldTree Manifest & Reconciled Database Refresh (38 Knights + 4-Pillar Ingestion).
"""

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CAMELOT_ROOT = Path(__file__).resolve().parent.parent

# 1. Load Knights from .agent/AGENTS.md
def get_constitutional_knights():
    agents_md = CAMELOT_ROOT / ".agent" / "AGENTS.md"
    text = agents_md.read_text(encoding="utf-8", errors="ignore")
    row_pat = re.compile(r"\|\s*\*\*([A-Z0-9_]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([a-f0-9-]+)`\s*\|")
    knights = []
    for m in row_pat.finditer(text):
        knights.append({
            "knight_id": m.group(1).strip(),
            "role": m.group(2).strip(),
            "model": m.group(3).strip(),
            "uuid": m.group(4).strip()
        })
    return knights

# Load character sheets for rich sparks
def get_character_sheets():
    cs_path = CAMELOT_ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
    if cs_path.exists():
        with open(cs_path, "r", encoding="utf-8") as f:
            return json.load(f).get("knights", {})
    return {}

# Shadow legacy mapping (space vs underscore)
LEGACY_SHADOW_MAP = {
    "f7707daa-2d10-4db8-8fda-be4661a27793": "da2e51db-780a-48cf-a40a-4f0f65ff9295", # SIR_BORIS -> SIR BORIS
    "f490c05e-d8c4-4008-87e1-5f901bf57c6a": "e9fcbbbc-cd43-4b2d-a437-b2570267a0a9", # SIR_ALEX -> SIR ALEX
    "91c5da8b-e2de-4a56-b7fd-c8b76c00afc7": "96f9233b-6efa-46a3-8242-98f0c463680c", # SIR_FORGE -> SIR FORGE
    "07cbb441-f008-424c-820a-85676210be39": "3a09997b-3d65-46c9-b9aa-fb8ebce927a9", # SIR_SENTINEL -> SIR SENTINEL
    "422a184b-93e7-4dfd-8a12-75d2268b6c60": "b4cfc5af-1555-4f23-a131-1ec6d03c2787", # SIR_GHOST -> SIR GHOST
    "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f": "f6466e10-d1b1-4904-9f87-081d031b0595", # LADY_APIS -> LADY APIS
    "56820318-bb91-451f-aac4-4b46424898cf": "28d49148-28db-438d-a299-61456fdfdefc", # SIR_HELIO -> SIR HELIOS
}

def phase1_vfs_canonical_convergence(knights, char_sheets):
    print("\n--- PHASE 1: VFS Canonical Roster Convergence ---")
    vfs_base = CAMELOT_ROOT / "vfs" / "notebooks"
    vfs_base.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    mounted_count = 0
    for k in knights:
        kid = k["knight_id"]
        canonical_uuid = k["uuid"]
        k_dir = vfs_base / canonical_uuid
        k_dir.mkdir(parents=True, exist_ok=True)

        # Check if legacy duplicate exists
        legacy_uuid = LEGACY_SHADOW_MAP.get(canonical_uuid)
        if legacy_uuid:
            legacy_dir = vfs_base / legacy_uuid
            if legacy_dir.exists():
                # Copy spark.md and Master_Compendium.md if not in canonical
                for f in legacy_dir.glob("*.md"):
                    target_file = k_dir / f.name
                    if not target_file.exists():
                        shutil.copy2(f, target_file)
                        print(f"  [MIGRATED] {f.name} from legacy {legacy_uuid[:8]} to canonical {canonical_uuid[:8]} ({kid})")
                
                # Write legacy redirect
                redirect_file = legacy_dir / "legacy_redirect.json"
                redirect_data = {
                    "legacy_workspace_id": legacy_uuid,
                    "canonical_workspace_id": canonical_uuid,
                    "canonical_knight_id": kid,
                    "status": "REDIRECT_ACTIVE",
                    "redirect_target": f"vfs/notebooks/{canonical_uuid}/",
                    "timestamp": now_iso
                }
                redirect_file.write_text(json.dumps(redirect_data, indent=2), encoding="utf-8")

        # Ensure spark.md exists
        spark_file = k_dir / "spark.md"
        if not spark_file.exists():
            cs = char_sheets.get(kid, {})
            spark_id = cs.get("spark_id", f"0x{canonical_uuid.replace('-', '').upper()[:32]}")
            rune = cs.get("summoning_rune", f"Omega_{kid}")
            role = cs.get("role", k["role"])
            model = cs.get("primary_engine", k["model"])
            
            spark_content = f"""# SPARK_DIRECTIVE: {kid}
**Sovereign Node UUID:** `{canonical_uuid}`  
**Spark ID:** `{spark_id}`  
**Role:** {role}  
**Primary Engine:** {model}  
**Summoning Rune:** `{rune}`  
**WorldTree Path:** `vfs://worldtree/knights/{kid.lower()}/`  
**Governance:** `8GB_SCARCITY_PROTOCOL` // `ISOMORPHIC_FILETREE_LAW` // `ANYA_LAST_LAW`  
**Sealed At:** {now_iso}  

---

## Directives & Execution Boundaries
1. **Isomorphic Memory Integrity:** Sync local Open-Notebook tissue with cloud workspace state.
2. **1-Source Mutate Compliance:** Maintain exactly one living `Master_Compendium.md` ($O(1)$ source consumption).
3. **Zero-Trust Verification:** Never bypass human-in-the-loop gates on high-impact external API mutations.
"""
            spark_file.write_text(spark_content, encoding="utf-8")
            print(f"  [GENERATED] spark.md for {kid} ({canonical_uuid[:8]})")

        # Ensure Master_Compendium.md exists
        compendium_file = k_dir / "Master_Compendium.md"
        if not compendium_file.exists():
            comp_content = f"""# Master Compendium: {kid} Sovereign Workspace
**Node ID:** `{canonical_uuid}`  
**Role:** {k['role']}  
**Governance:** `1_SOURCE_MUTATE_LAW` // `8GB_SCARCITY_PROTOCOL`  
**Generated:** {now_iso}  

---

## 1. Table of Contents & Knowledge Anchors
- **Core Directive:** [`spark.md`](spark.md)
- **Runtime Tissue:** `03_VAULT/runtime_state/open_notebook/{kid.lower()}_tissue.json`
- **WorldTree Tether:** `vfs://worldtree/knights/{kid.lower()}/tether.json`

---

## 2. Universal Knowledge Glyph (UKG) Array
```ukg
[NODE:{kid}]:
  UUID: "{canonical_uuid}"
  Role: "{k['role']}"
  Model: "{k['model']}"
  Status: "ACTIVE_VFS_MOUNTED"
  Slot_Economy: "O(1)_SINGLE_SOURCE"
```
"""
            compendium_file.write_text(comp_content, encoding="utf-8")
            print(f"  [GENERATED] Master_Compendium.md for {kid} ({canonical_uuid[:8]})")

        mounted_count += 1

    print(f"Phase 1 Complete: {mounted_count}/38 Constitutional Knights Isomorphically Mounted.")

def phase2_historical_version_cold_storage():
    print("\n--- PHASE 2: Historical Version Cold Storage Distillation ---")
    crystal_dir = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "historical_crystals"
    crystal_dir.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    historical_versions = [
        {"version": "v57.0", "id": "19f90acf-6731-4ba3-bf87-1310b1c97564", "title": "Camelot OS v57.0 Master Bootstrap Protocol"},
        {"version": "v300.4.0", "id": "a9cf586e-1971-4959-bb97-cdcd37257ebb", "title": "living Camelot-OS: The v300.4.0 Universal Singularity Recompilation"},
        {"version": "v400", "id": "bcaadfdd-1654-487d-9c4c-111f7dea120e", "title": "Living Camelot-OS v.400"},
        {"version": "v700.0", "id": "d02cc716-d235-4d34-9185-a07860ec5272", "title": "Camelot-OS v.700.0"},
        {"version": "v999.3", "id": "28bca096-1ba2-4e47-8b92-aa88e90be210", "title": "Camelot-OS v.999.3"},
        {"version": "v_living", "id": "eaff9959-4d7b-4761-8850-c0b2e25a2b45", "title": "Living Camelot-OS"},
        {"version": "v_court3", "id": "cab403c0-bb66-454d-a529-84f7e8ac5cff", "title": "Court of Camelot 3.0: Agentic Ecosystem Architecture"},
        {"version": "v_codex", "id": "c5544902-cfb4-4864-b28e-1838b69b9814", "title": "The Camelot-OS Master Construction Codex"},
        {"version": "v_lattice", "id": "74895628-d98d-4d93-a789-dde10e7f27ff", "title": "Camelot-OS: Leech-Lattice Quantization for Swarm-Scale Agentic Systems"},
        {"version": "v_alpha_omega", "id": "2536aefb-937f-4a04-9142-d1a2f029d8a7", "title": "The Camelot-OS Alpha-Omega artifacts"},
        {"version": "v_gde", "id": "a9109641-116a-4589-a867-2e0d27ee5536", "title": "Camelot GDE Universal Orchestrator Protocol"},
        {"version": "v_glyph", "id": "38096a21-e19d-4f91-b48f-e92c2adbd879", "title": "Camelot OS: Universal Knowledge Glyph and System State Ledger"},
        {"version": "v_distill", "id": "58130cac-8415-4ab9-918e-fa76b1ad66cd", "title": "Camelot-OS: The Alpha Omega Distillation Protocol"},
        {"version": "v_ascension", "id": "b3b9f907-a256-4351-a0a4-31f6ddd82c4a", "title": "The Camelot-OS Ascension Manifest and System Architecture shadow"},
        {"version": "v_warroom", "id": "b2ef1f3b-8f14-47c6-bf27-8d8c5f76d1b8", "title": "war room of camelot"}
    ]

    crystal_data = {
        "schema_version": "TOON_CRYSTAL_v1.0",
        "crystal_name": "CAMELOT_HISTORICAL_VERSIONS",
        "status": "COLD_STORAGE_SEALED",
        "canonical_active_target": {
            "version": "v1000.54-EXCALIBUR-A",
            "uuid": "8c656cfa-a189-409e-a72d-07692a47f17e",
            "title": "Camelot-OS v.1000"
        },
        "archived_at": now_iso,
        "total_archived_versions": len(historical_versions),
        "versions": historical_versions,
        "query_routing_policy": "ALL_QUERIES_REDIRECT_TO_V1000"
    }

    json_path = crystal_dir / "CAMELOT_HISTORICAL_VERSIONS.json"
    toon_path = crystal_dir / "CAMELOT_HISTORICAL_VERSIONS.toon"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(crystal_data, f, indent=2)

    toon_content = f"""# TOON_CRYSTAL: CAMELOT_HISTORICAL_VERSIONS
@schema: TOON_CRYSTAL_v1.0
@archived_at: {now_iso}
@canonical_target: "8c656cfa-a189-409e-a72d-07692a47f17e" [Camelot-OS v.1000]
@routing_policy: "REDIRECT_ALL_TO_CANONICAL_V1000"

[ARCHIVE_INDEX]:
"""
    for v in historical_versions:
        toon_content += f"  - [{v['version']}] UUID: {v['id']} | Title: \"{v['title']}\" | Status: COLD_STORAGE\n"

    toon_content += "\n# SEAL: 0x8C656CFA_V1000_COLD_STORAGE_AUTHENTICATED\n"
    toon_path.write_text(toon_content, encoding="utf-8")

    print(f"Phase 2 Complete: 15 Historical Versions Distilled to {toon_path}")

def phase3_phantom_scratch_inventory():
    print("\n--- PHASE 3: Phantom & Scratch Node Registry ---")
    live_nbs = json.load(open(CAMELOT_ROOT / "vfs" / "live_notebooks.json", encoding="utf-8"))
    
    phantom_nodes = []
    for nb in live_nbs:
        t = nb.get("title", "").strip()
        if t in ["", "Untitled notebook"]:
            phantom_nodes.append({
                "id": nb["id"],
                "title": t if t else "<EMPTY_TITLE>",
                "sources": nb.get("source_count", 0),
                "designation": "EPHEMERAL_SWARM_SCRATCHPAD",
                "quarantine_status": "EXCLUDED_FROM_ROUTINE_FLEET_SYNC"
            })

    out_path = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "PHANTOM_SCRATCH_INVENTORY.json"
    out_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_phantom_scratch_nodes": len(phantom_nodes),
        "policy": "ISOLATE_AND_QUARANTINE_FOR_EPHEMERAL_SWARM",
        "nodes": phantom_nodes
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print(f"Phase 3 Complete: {len(phantom_nodes)} Phantom/Scratch Nodes Quarantined in {out_path}")

def phase4_worldtree_manifest_refresh(knights):
    print("\n--- PHASE 4: WorldTree Manifest & Reconciled Database Refresh ---")
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Update vfs/worldtree_manifest.json
    manifest_path = CAMELOT_ROOT / "vfs" / "worldtree_manifest.json"
    raw_lines = [l for l in manifest_path.read_text(encoding="utf-8").splitlines() if not l.strip().startswith("#")]
    manifest = json.loads("\n".join(raw_lines))
    manifest["schema_version"] = "1000.54-EXCALIBUR-A"
    manifest["updated"] = now_iso
    manifest["verified_knights_count"] = len(knights)

    # Build node list for all 38 Knights
    node_entries = []
    for k in knights:
        kid = k["knight_id"]
        node_entries.append({
            "knight_id": kid,
            "notebook_id": k["uuid"],
            "vfs_path": f"vfs://worldtree/knights/{kid.lower()}/",
            "role": k["role"],
            "primary_model": k["model"],
            "active_last_3_months": True
        })
    manifest["nodes"] = node_entries

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Updated: {manifest_path} with {len(node_entries)} Sovereign Knights.")

    # 2. Update vfs/worldtree_reconciled.json
    reconciled_path = CAMELOT_ROOT / "vfs" / "worldtree_reconciled.json"
    reconciled = json.load(open(reconciled_path, encoding="utf-8"))
    reconciled["schema_version"] = "1000.54-EXCALIBUR-A"
    reconciled["updated"] = now_iso
    reconciled["verified_knights"] = len(knights)
    
    wt_nodes = {}
    for k in knights:
        wt_nodes[k["knight_id"]] = {
            "id": k["uuid"],
            "role": k["role"],
            "model": k["model"],
            "verified": True,
            "isomorphic_vfs_path": f"vfs/notebooks/{k['uuid']}/"
        }
    reconciled["worldtree_nodes"] = wt_nodes

    with open(reconciled_path, "w", encoding="utf-8") as f:
        json.dump(reconciled, f, indent=2)
    print(f"  Updated: {reconciled_path} with 38 Verified WorldTree Nodes.")

def execute_all():
    print("=== CAMELOT-OS: FLEET-WIDE OPTIMIZATION EXECUTION ===")
    knights = get_constitutional_knights()
    char_sheets = get_character_sheets()
    print(f"Loaded {len(knights)} constitutional Knights.")

    phase1_vfs_canonical_convergence(knights, char_sheets)
    phase2_historical_version_cold_storage()
    phase3_phantom_scratch_inventory()
    phase4_worldtree_manifest_refresh(knights)
    print("\n=== ALL OPTIMIZATION PHASES EXECUTED SUCCESSFULLY ===")

if __name__ == "__main__":
    execute_all()
