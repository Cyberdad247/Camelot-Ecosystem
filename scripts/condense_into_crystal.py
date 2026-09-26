#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# scripts/condense_into_crystal.py
# Condenses research notes into a VKG (Visual/Viking Knowledge Graph) Crystal
# for WorldTree navigation and Merlin ForgePlan integration.

from __future__ import annotations

import argparse
import json
import hashlib
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CRYSTAL_DIR = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_crystals"
NAV_INDEX_PATH = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_nav_index.json"

# ── Ensure output directory exists ──────────────────────────────────────────
CRYSTAL_DIR.mkdir(parents=True, exist_ok=True)


def _crystal_id(knight: str, notebook_title: str) -> str:
    """Deterministic VKG crystal ID from knight + title hash."""
    raw = f"{knight}:{notebook_title}".encode("utf-8")
    return "VKG_" + hashlib.sha256(raw).hexdigest()[:16].upper()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _extract_triplets(manifest: str) -> list[dict[str, str]]:
    """Very small extractor for head/relation/tail from manifest Content."""
    triplets: list[dict[str, str]] = []
    # Match patterns like "Mojo compiles GPU" or "Rust runs on bare metal"
    for m in re.finditer(r"([A-Z][a-z]+)\s+(compiles|runs|routes|governs|protects?|drives?)\s+([A-Z][a-z]+)", manifest):
        triplets.append({
            "head": m.group(1),
            "relation": m.group(2),
            "tail": m.group(3),
        })
    return triplets


def condense(
    *,
    knight: str,
    notebook_title: str,
    sources_count: int,
    manifest_text: str,
    category: str = "RESEARCH_ENRICHMENT",
) -> dict[str, Any]:
    """Produce a VKG crystal dict following the canonical schema."""
    now = datetime.now(timezone.utc).isoformat()
    crystal_id = _crystal_id(knight, notebook_title)

    # De-duplicate against existing crystals
    existing_ids = {
        Path(f).stem.replace("vkg_", "").replace(".json", "")
        for f in CRYSTAL_DIR.glob("*.json")
        if "vkg_" in Path(f).name
    }
    if crystal_id.lower().replace("VKG_", "") in existing_ids:
        print(f"[WARN] Crystal ID already exists; returning cached structure.")
        # Return the most recent matching crystal
        for f in sorted(CRYSTAL_DIR.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("crystal_id", "").lower().replace("VKG_", "") == crystal_id.lower().replace("VKG_", ""):
                return data

    triplets = _extract_triplets(manifest_text)
    manifest_sha = _sha256_text(manifest_text)

    crystal = {
        "crystal_id": crystal_id,
        "notebook_id": hashlib.sha256(notebook_title.encode("utf-8")).hexdigest()[:16],
        "notebook_title": notebook_title,
        "sources_count": sources_count,
        "category": category,
        "knight": knight.upper(),
        "manifest_content": manifest_text,
        "manifest_sha256": manifest_sha,
        "triplets": triplets,
        "created_at": now,
    }

    # Write crystal file
    crystal_path = CRYSTAL_DIR / f"{crystal_id.lower().replace('VKG_', 'vkg_')}.json"
    crystal_path.write_text(json.dumps(crystal, indent=2), encoding="utf-8")
    print(f"[CRYSTAL] Written {crystal_path}")

    # Update navigation index
    _update_nav_index(crystal)

    return crystal


def _update_nav_index(crystal: dict[str, Any]) -> None:
    """Append crystal entry to the WorldTree navigation index."""
    if NAV_INDEX_PATH.exists():
        index = json.loads(NAV_INDEX_PATH.read_text(encoding="utf-8"))
    else:
        index = {"crystals": [], "updated_at": datetime.now(timezone.utc).isoformat()}

    # Avoid duplicates by crystal_id
    crystal_ids = {c.get("crystal_id") for c in index.get("crystals", [])}
    if crystal["crystal_id"] not in crystal_ids:
        index["crystals"].append(
            {
                "crystal_id": crystal["crystal_id"],
                "knight": crystal["knight"],
                "notebook_title": crystal["notebook_title"],
                "category": crystal["category"],
                "vfs_coord": f"vfs://worldtree/knights/{crystal['knight'].lower()}/domain_nodes/{crystal['notebook_id']}",
                "added_at": crystal["created_at"],
            }
        )
        index["updated_at"] = datetime.now(timezone.utc).isoformat()
        NAV_INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")
        print(f"[NAV] Updated {NAV_INDEX_PATH}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Condense research notes into a VKG Crystal for WorldTree."
    )
    parser.add_argument("--knight", required=True, help="Knight ID (e.g. SIR_BORIS)")
    parser.add_argument("--title", required=True, help="Notebook/source title")
    parser.add_argument("--sources", type=int, default=0, help="Verified source count")
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to manifest text file or 'inline:' followed by text",
    )
    parser.add_argument(
        "--category",
        default="RESEARCH_ENRICHMENT",
        help="VKG category tag",
    )
    args = parser.parse_args(argv)

    # Resolve manifest text
    if args.manifest.startswith("inline:"):
        manifest_text = args.manifest[len("inline:"):].strip()
    else:
        manifest_path = Path(args.manifest)
        if not manifest_path.exists():
            print(f"[ERR] Manifest file not found: {manifest_path}", file=sys.stderr)
            return 1
        manifest_text = manifest_path.read_text(encoding="utf-8", errors="replace")

    crystal = condense(
        knight=args.knight,
        notebook_title=args.title,
        sources_count=args.sources,
        manifest_text=manifest_text,
        category=args.category,
    )

    # Pretty-print the result
    print("\n--- Generated VKG Crystal ---")
    print(json.dumps(crystal, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())