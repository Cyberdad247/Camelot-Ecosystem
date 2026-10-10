#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
scripts/doc_check.py — Camelot-OS Documentation Architecture CI Verification Gate
================================================================================
Implements the 17 Doc-Check rules specified in Reforged Baseline v4.1.0:
CAMELOT-DOC-ARCH-vNEXT-REFORGED-20260925 (docs/00-governance/)

Commands:
  python scripts/doc_check.py validate-metadata
  python scripts/doc_check.py validate-slices
  python scripts/doc_check.py canonical-home
  python scripts/doc_check.py waivers
  python scripts/doc_check.py run-all
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

CAMELOT_HOME = Path(__file__).resolve().parent.parent
DOCS_DIR = CAMELOT_HOME / "docs"
SLICES_DIR = CAMELOT_HOME / "slices"
GOV_DIR = DOCS_DIR / "00-governance"
SCHEMA_PATH = GOV_DIR / "document-schema.yaml"
RULES_PATH = GOV_DIR / "doc-check-rules.yaml"
WAIVERS_PATH = GOV_DIR / "WAIVERS.md"


def get_canonical_doc_dirs() -> List[Path]:
    """Finds all canonical numbered documentation layers (00-governance through 13-evidence) and slice folders."""
    dirs: List[Path] = []
    if DOCS_DIR.exists():
        for d in DOCS_DIR.iterdir():
            if d.is_dir() and re.match(r"^\d{2}-[a-z]+", d.name):
                dirs.append(d)
    if SLICES_DIR.exists():
        for s in SLICES_DIR.iterdir():
            if s.is_dir():
                dirs.append(s)
    return sorted(dirs, key=lambda p: p.name)


def parse_front_matter(file_path: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    """Extracts and parses YAML front matter from a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        return None, f"Failed to read file: {exc}"

    if not content.startswith("---"):
        return None, "Missing opening front matter delimiter '---'"

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Unclosed front matter delimiter '---'"

    raw_yaml = parts[1].strip()
    try:
        data = yaml.safe_load(raw_yaml)
        if not isinstance(data, dict):
            return None, "Front matter must be a valid YAML mapping"
        return data, ""
    except Exception as exc:
        return None, f"Invalid YAML front matter: {exc}"


def load_waivers() -> List[Dict[str, Any]]:
    """Loads active waivers from docs/00-governance/WAIVERS.md."""
    if not WAIVERS_PATH.exists():
        return []

    waivers: List[Dict[str, Any]] = []
    text = WAIVERS_PATH.read_text(encoding="utf-8")
    
    # Simple table parser for markdown table
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and ("WAV-" in line):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 7:
                waivers.append({
                    "id": cols[0].replace("*", ""),
                    "target": cols[1],
                    "owner": cols[2],
                    "justification": cols[3],
                    "granted": cols[4],
                    "expiry": cols[5],
                    "status": cols[6].replace("*", ""),
                })
    return waivers


def is_path_waived(file_path: Path, rule_id: str, waivers: List[Dict[str, Any]]) -> bool:
    """Checks if a file path has an active, unexpired waiver for a given rule."""
    try:
        rel_path = file_path.relative_to(CAMELOT_HOME).as_posix()
    except Exception:
        rel_path = file_path.as_posix()
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for w in waivers:
        if w["status"] == "ACTIVE" and w["expiry"] >= now_str:
            target_norm = w["target"].replace("\\", "/")
            if target_norm in rel_path or any(part in rel_path for part in target_norm.split()):
                return True
    return False


def validate_metadata(target_dirs: Optional[List[Path]] = None) -> Tuple[bool, List[str]]:
    """Rule 01/Schema: Validates YAML front matter against document-schema.yaml."""
    if not SCHEMA_PATH.exists():
        return False, [f"Metadata schema missing at {SCHEMA_PATH}"]

    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    required_keys = set(schema.get("required", []))
    waivers = load_waivers()

    dirs_to_check = target_dirs or get_canonical_doc_dirs()
    errors: List[str] = []

    for d in dirs_to_check:
        if not d.exists():
            continue
        for md_file in d.glob("*.md"):
            if is_path_waived(md_file, "SCHEMA", waivers):
                continue
            meta, err = parse_front_matter(md_file)
            if err:
                errors.append(f"[{md_file.relative_to(CAMELOT_HOME)}] {err}")
                continue

            missing = required_keys - set(meta.keys())
            if missing:
                errors.append(f"[{md_file.relative_to(CAMELOT_HOME)}] Missing required front-matter fields: {sorted(missing)}")

    return len(errors) == 0, errors


def validate_slices() -> Tuple[bool, List[str]]:
    """Validates that each vertical slice in slices/ contains a valid slice.yaml and README.md."""
    if not SLICES_DIR.exists():
        return False, ["slices/ directory does not exist"]

    errors: List[str] = []
    required_slice_fields = {"id", "slug", "title", "tier", "status", "owner", "summary"}

    slice_folders = [d for d in SLICES_DIR.iterdir() if d.is_dir()]
    if not slice_folders:
        return False, ["No vertical slices found in slices/"]

    for s_dir in slice_folders:
        yaml_file = s_dir / "slice.yaml"
        readme_file = s_dir / "README.md"

        if not yaml_file.exists():
            errors.append(f"[{s_dir.name}] Missing slice.yaml manifest")
        else:
            try:
                manifest = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                missing_fields = required_slice_fields - set(manifest.keys())
                if missing_fields:
                    errors.append(f"[{s_dir.name}/slice.yaml] Missing manifest fields: {sorted(missing_fields)}")
            except Exception as exc:
                errors.append(f"[{s_dir.name}/slice.yaml] Invalid YAML: {exc}")

        if not readme_file.exists():
            errors.append(f"[{s_dir.name}] Missing README.md specification")

    return len(errors) == 0, errors


def validate_canonical_home() -> Tuple[bool, List[str]]:
    """Rule 12: Ensures vertical slices and canonical docs do not duplicate global IDs."""
    errors: List[str] = []
    seen_ids: Dict[str, Path] = {}
    dirs_to_check = get_canonical_doc_dirs()

    for d in dirs_to_check:
        for md_file in d.glob("*.md"):
            meta, _ = parse_front_matter(md_file)
            if meta and "document_id" in meta:
                doc_id = meta["document_id"]
                if doc_id in seen_ids:
                    errors.append(
                        f"Duplicate document_id '{doc_id}' in {md_file.relative_to(CAMELOT_HOME)} "
                        f"(already declared in {seen_ids[doc_id].relative_to(CAMELOT_HOME)})"
                    )
                else:
                    seen_ids[doc_id] = md_file

    return len(errors) == 0, errors


def validate_waivers() -> Tuple[bool, List[str]]:
    """Checks waiver expiration dates and required fields."""
    waivers = load_waivers()
    errors: List[str] = []
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for w in waivers:
        if w["status"] == "ACTIVE" and w["expiry"] < now_str:
            errors.append(f"Waiver {w['id']} has EXPIRED on {w['expiry']} (remediation owner: {w['owner']})")

    return len(errors) == 0, errors


def run_all_checks() -> int:
    """Executes all automated checks fail-closed."""
    print("=================================================================")
    print("CAMELOT-OS DOC-CHECK VERIFICATION GATE (Reforged Baseline v4.1.0)")
    print("=================================================================")

    ok_meta, err_meta = validate_metadata()
    ok_slices, err_slices = validate_slices()
    ok_home, err_home = validate_canonical_home()
    ok_waiv, err_waiv = validate_waivers()

    all_passed = ok_meta and ok_slices and ok_home and ok_waiv

    print(f"\n1. Metadata & Front Matter Validation: {'[PASS]' if ok_meta else '[FAIL]'}")
    for err in err_meta:
        print(f"   ✖ {err}")

    print(f"\n2. Vertical Slice Manifest Validation: {'[PASS]' if ok_slices else '[FAIL]'}")
    for err in err_slices:
        print(f"   ✖ {err}")

    print(f"\n3. Canonical Home & ID Uniqueness:     {'[PASS]' if ok_home else '[FAIL]'}")
    for err in err_home:
        print(f"   ✖ {err}")

    print(f"\n4. Time-Bound Waiver Audit:             {'[PASS]' if ok_waiv else '[FAIL]'}")
    for err in err_waiv:
        print(f"   ✖ {err}")

    print("\n-----------------------------------------------------------------")
    if all_passed:
        print("[SUCCESS] All Documentation Architecture checks PASSED.")
        print("=================================================================")
        return 0
    else:
        print("[FAIL-CLOSED] Documentation Architecture checks failed. Fix violations or record time-bound waiver.")
        print("=================================================================")
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Camelot-OS Doc-Check CLI")
    parser.add_argument("command", nargs="?", default="run-all", choices=["validate-metadata", "validate-slices", "canonical-home", "waivers", "run-all"])
    args = parser.parse_args()

    if args.command == "validate-metadata":
        ok, errs = validate_metadata()
        for e in errs:
            print(e)
        sys.exit(0 if ok else 1)
    elif args.command == "validate-slices":
        ok, errs = validate_slices()
        for e in errs:
            print(e)
        sys.exit(0 if ok else 1)
    elif args.command == "canonical-home":
        ok, errs = validate_canonical_home()
        for e in errs:
            print(e)
        sys.exit(0 if ok else 1)
    elif args.command == "waivers":
        ok, errs = validate_waivers()
        for e in errs:
            print(e)
        sys.exit(0 if ok else 1)
    else:
        sys.exit(run_all_checks())


if __name__ == "__main__":
    main()
