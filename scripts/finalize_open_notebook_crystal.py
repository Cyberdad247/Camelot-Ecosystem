#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# scripts/finalize_open_notebook_crystal.py
# Finalizes unstructured text or research notes into:
#   1. Graphify semantic triplets (Subject-Predicate-Object)
#   2. Triple-QFT Symbolect Glyph & Anchor Tokens
#   3. Machine-actionable VKG Crystal (.json) in 03_VAULT/runtime_state/open_notebook/vkg_crystals/
#   4. Immutable UKG Crystal node (.json + .toon) in 03_VAULT/UKG/nodes/
#   5. Updated WorldTree navigation index (vkg_nav_index.json)

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "control_plane"))

logger = logging.getLogger("FinalizeVKGCrystal")

# Destination Directories
VKG_CRYSTAL_DIR = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_crystals"
UKG_NODES_DIR = REPO_ROOT / "03_VAULT" / "UKG" / "nodes"
NAV_INDEX_PATH = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_nav_index.json"

VKG_CRYSTAL_DIR.mkdir(parents=True, exist_ok=True)
UKG_NODES_DIR.mkdir(parents=True, exist_ok=True)

WORLDTREE_ROOT_UUID = "a0a4bfb9-e847-4c38-be39-7aee398f0795"


def _generate_crystal_id(knight_id: str, title: str) -> str:
    """Deterministic crystal ID derived from knight_id and title."""
    seed = f"{knight_id.upper()}:{title.strip()}".encode("utf-8")
    h = hashlib.sha256(seed).hexdigest()[:16].upper()
    return f"VKG_{h}"


def extract_triplets_with_graphify(text: str) -> List[Dict[str, str]]:
    """Extract semantic triplets using control_plane/graphify.py with rule-based fallback."""
    try:
        from control_plane.graphify import extract_triplets
        raw_triplets = extract_triplets(text)
        return [{"head": t.head, "relation": t.relation, "tail": t.tail} for t in raw_triplets]
    except Exception as e:
        logger.warning(f"Graphify extraction fallback: {e}")
        triplets = []
        for m in re.finditer(r"([A-Z][a-zA-Z0-9_]+)\s+(routes?|validates?|compiles?|stores?|executes?|runs?|governs?|protects?)\s+([A-Za-z0-9_\- ]+)", text):
            triplets.append({
                "head": m.group(1),
                "relation": m.group(2),
                "tail": m.group(3).strip(),
            })
        return triplets


def compile_glyph_and_symbolect(text: str, title: str) -> Dict[str, Any]:
    """Compile Triple-QFT Symbolect glyph and anchor tokens."""
    try:
        from scripts.symbolect_transpiler import TripleQFTTranspiler
        trans = TripleQFTTranspiler()
        res = trans.compile(f"{title}: {text[:500]}")
        return {
            "glyph": res.get("symbolect", "|🧠⊗(⚡💬)⟩"),
            "anchor_tokens": res.get("anchor_tokens", []),
            "status": res.get("status", "RADIANT"),
        }
    except Exception as e:
        logger.warning(f"Symbolect compilation fallback: {e}")
        # Clean fallback
        words = [w for w in re.findall(r"\b[A-Za-z0-9_]+\b", f"{title} {text[:200]}") if len(w) > 3][:6]
        return {
            "glyph": f"|🧠⊗(⚡💬)⟩ ⟨Omega:{'|'.join(words)}⟩",
            "anchor_tokens": words,
            "status": "FALLBACK",
        }


def _update_nav_index(entry: Dict[str, Any]) -> None:
    """Update WorldTree navigation index with the finalized crystal."""
    index: Dict[str, Any] = {"crystals": [], "updated_at": datetime.now(timezone.utc).isoformat()}
    if NAV_INDEX_PATH.exists():
        try:
            index = json.loads(NAV_INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    existing_ids = {c.get("crystal_id") for c in index.get("crystals", [])}
    if entry["crystal_id"] not in existing_ids:
        index.setdefault("crystals", []).append({
            "crystal_id": entry["crystal_id"],
            "knight": entry["knight"],
            "title": entry["title"],
            "category": entry["category"],
            "vfs_coordinate": entry["vfs_coordinate"],
            "glyph": entry.get("glyph"),
            "added_at": entry["created_at"],
        })
        index["updated_at"] = datetime.now(timezone.utc).isoformat()
        NAV_INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")


def finalize_open_notebook_crystal(
    *,
    knight_id: str,
    title: str,
    text: str,
    category: str = "CAMELOT_SYSTEMS_ARCHITECTURE",
    sources_count: int = 1,
) -> Dict[str, Any]:
    """
    Finalize unstructured text into a validated VKG Crystal with Graphify triplets and Symbolect Glyph.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    cid = _generate_crystal_id(knight_id, title)
    text_sha = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()

    # 1. Graphify semantic extraction
    triplets = extract_triplets_with_graphify(text)

    # 2. Triple-QFT Symbolect & Glyph compilation
    symbolect_meta = compile_glyph_and_symbolect(text, title)

    # 3. Assemble VKG Crystal Payload
    vfs_coord = f"vfs://worldtree/crystals/{cid.lower()}.vkg"
    crystal_payload = {
        "crystal_id": cid,
        "schema_version": "v1000-VKG-SINGULARITY",
        "anya_seal": "ANYA_IS_THE_GATE",
        "category": category,
        "knight": knight_id.upper(),
        "title": title,
        "glyph": symbolect_meta["glyph"],
        "anchor_tokens": symbolect_meta["anchor_tokens"],
        "sources_count": sources_count,
        "manifest_sha256": text_sha,
        "triplets": triplets,
        "triplet_count": len(triplets),
        "vfs_coordinate": vfs_coord,
        "created_at": now_iso,
        "finalized_content": text,
    }

    # 4. Save to local VFS runtime state
    vkg_file = VKG_CRYSTAL_DIR / f"{cid.lower()}.json"
    vkg_file.write_text(json.dumps(crystal_payload, indent=2), encoding="utf-8")

    # 5. Mirror to UKG nodes (.json and .toon)
    ukg_json_file = UKG_NODES_DIR / f"{cid}.json"
    ukg_json_file.write_text(json.dumps(crystal_payload, indent=2), encoding="utf-8")

    toon_summary = (
        f"type:VKG_CRYSTAL | id:{cid} | knight:{knight_id.upper()} | date:{now_iso[:10]} | "
        f"title:{title.replace('|', '_')} | glyph:{symbolect_meta['glyph']} | "
        f"triplets:{len(triplets)} | status:FINALIZED_RADIANT | provenance_sha:{text_sha[:16]}"
    )
    ukg_toon_file = UKG_NODES_DIR / f"{cid}.toon"
    ukg_toon_file.write_text(toon_summary, encoding="utf-8")

    # 6. Update Navigation Index
    _update_nav_index(crystal_payload)

    return crystal_payload


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Finalize unstructured text into a VKG Crystal with Graphify and Glyph compression."
    )
    parser.add_argument("--knight", required=True, help="Knight ID (e.g. SIR_HELIOS, SIR_BORIS)")
    parser.add_argument("--title", required=True, help="Crystal Title")
    parser.add_argument("--text", required=True, help="Path to text file or 'inline:<content>'")
    parser.add_argument("--category", default="CAMELOT_SYSTEMS_ARCHITECTURE", help="Category tag")
    parser.add_argument("--sources", type=int, default=1, help="Count of verified sources")
    args = parser.parse_args(argv)

    if args.text.startswith("inline:"):
        content = args.text[len("inline:"):].strip()
    else:
        p = Path(args.text)
        if not p.exists():
            print(f"[ERR] File not found: {p}", file=sys.stderr)
            return 1
        content = p.read_text(encoding="utf-8", errors="replace")

    res = finalize_open_notebook_crystal(
        knight_id=args.knight,
        title=args.title,
        text=content,
        category=args.category,
        sources_count=args.sources,
    )

    print(json.dumps({
        "status": "FINALIZED_OK",
        "crystal_id": res["crystal_id"],
        "glyph": res["glyph"],
        "anchor_tokens": res["anchor_tokens"],
        "triplets_extracted": res["triplet_count"],
        "vfs_coordinate": res["vfs_coordinate"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
