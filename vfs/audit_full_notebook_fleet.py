#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Comprehensive Audit of Full Notebook Directory & Sovereign Knight Roster.
Cross-references live_notebooks.json (275 notebooks), .agent/AGENTS.md (38 Knights),
open_notebook runtime tissues, and local isomorphic VFS mounts.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CAMELOT_ROOT = Path(__file__).resolve().parent.parent

def audit_fleet():
    # 1. Load live notebooks
    with open(CAMELOT_ROOT / "vfs" / "live_notebooks.json", "r", encoding="utf-8") as f:
        live_nbs = json.load(f)

    id_to_nb = {nb["id"]: nb for nb in live_nbs}
    title_to_nb = {nb.get("title", "").strip(): nb for nb in live_nbs}

    # 2. Extract Knights from .agent/AGENTS.md
    agents_md_path = CAMELOT_ROOT / ".agent" / "AGENTS.md"
    knight_roster = []
    if agents_md_path.exists():
        text = agents_md_path.read_text(encoding="utf-8", errors="ignore")
        # Match table rows: | **SIR_BORIS** | Lead Architect... | Gemini... | `f7707daa...` |
        row_pat = re.compile(r"\|\s*\*\*([A-Z0-9_]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([a-f0-9-]+)`\s*\|")
        for m in row_pat.finditer(text):
            knight_roster.append({
                "knight": m.group(1).strip(),
                "role": m.group(2).strip(),
                "model": m.group(3).strip(),
                "uuid": m.group(4).strip()
            })

    # 3. Check Open-Notebook local tissues
    open_nb_dir = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "open_notebook"
    existing_tissues = list(open_nb_dir.glob("*.json")) if open_nb_dir.exists() else []
    tissue_names = {p.stem: p for p in existing_tissues}

    # 4. Check VFS mounts
    vfs_nb_dir = CAMELOT_ROOT / "vfs" / "notebooks"
    existing_vfs_mounts = [d.name for d in vfs_nb_dir.iterdir() if d.is_dir()] if vfs_nb_dir.exists() else []

    # 5. Cross-reference Knights
    knight_audit = []
    for k in knight_roster:
        kid = k["knight"].lower()
        uuid = k["uuid"]
        
        has_cloud_match = uuid in id_to_nb
        matched_title = id_to_nb[uuid].get("title") if has_cloud_match else None
        
        # Check tissue matching
        has_tissue = any(kid in tname or uuid[:8] in tname for tname in tissue_names)
        
        # Check local vfs
        has_vfs = uuid in existing_vfs_mounts
        
        knight_audit.append({
            "knight": k["knight"],
            "role": k["role"],
            "model": k["model"],
            "canonical_uuid": uuid,
            "cloud_matched": has_cloud_match,
            "cloud_title": matched_title,
            "local_tissue_active": has_tissue,
            "local_vfs_mounted": has_vfs
        })

    # 6. Categorize the 275 live notebooks
    taxonomy = defaultdict(list)
    knight_uuids = {k["uuid"] for k in knight_roster}
    
    for nb in live_nbs:
        nid = nb["id"]
        title = nb.get("title", "").strip()
        tl = title.lower()
        
        if nid in knight_uuids or "sovereign_workspace" in tl or any(k in tl for k in ["sir_", "lady_", "sir ", "lady ", "merlin", "arthur", "anya"]):
            taxonomy["sovereign_knights"].append(nb)
        elif "camelot" in tl:
            taxonomy["camelot_core_versions"].append(nb)
        elif "hiveide" in tl or "inspira" in tl:
            taxonomy["inspira_hiveide"].append(nb)
        elif "audio" in tl or "kickbox" in tl or "sonus" in tl or "bifrost" in tl:
            taxonomy["audio_transport"].append(nb)
        elif any(w in tl for w in ["market", "business", "legal", "venture", "trademark", "wealth"]):
            taxonomy["business_commerce"].append(nb)
        elif any(w in tl for w in ["prompt", "ai ", "llm", "rag", "eval", "agent", "swarm", "vector", "model"]):
            taxonomy["ai_research_skills"].append(nb)
        else:
            taxonomy["knowledge_archive"].append(nb)

    # 7. Identify duplicates & consolidation candidates
    duplicates = []
    # Title normalizer
    clean_titles = defaultdict(list)
    for nb in live_nbs:
        t = re.sub(r"[^a-zA-Z0-9]", "", nb.get("title", "").lower())
        clean_titles[t].append(nb)
        
    for ct, nblist in clean_titles.items():
        if len(nblist) > 1:
            duplicates.append([{"id": x["id"], "title": x["title"]} for x in nblist])

    audit_summary = {
        "timestamp": CAMELOT_ROOT.name,
        "total_cloud_notebooks": len(live_nbs),
        "total_knights_in_constitution": len(knight_roster),
        "knights_matched_in_cloud": sum(1 for k in knight_audit if k["cloud_matched"]),
        "knights_with_local_tissue": sum(1 for k in knight_audit if k["local_tissue_active"]),
        "knights_with_vfs_mounts": sum(1 for k in knight_audit if k["local_vfs_mounted"]),
        "fleet_taxonomy_counts": {k: len(v) for k, v in taxonomy.items()},
        "duplicate_clusters_found": len(duplicates),
        "knight_roster_audit": knight_audit,
        "duplicate_clusters": duplicates[:15]
    }

    out_path = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "FULL_FLEET_NOTEBOOK_AUDIT_REPORT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)

    print(f"AUDIT COMPLETE.")
    print(f"Total Cloud Notebooks: {len(live_nbs)}")
    print(f"Knights in Constitution: {len(knight_roster)}")
    print(f"Knights with Cloud Match: {sum(1 for k in knight_audit if k['cloud_matched'])}/{len(knight_roster)}")
    print(f"Knights with Local Tissue: {sum(1 for k in knight_audit if k['local_tissue_active'])}/{len(knight_roster)}")
    print(f"Knights with Local VFS: {sum(1 for k in knight_audit if k['local_vfs_mounted'])}/{len(knight_roster)}")
    print(f"Duplicate/Near-Identical Clusters: {len(duplicates)}")
    print(f"Report written to: {out_path}")

if __name__ == "__main__":
    audit_fleet()
