# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Universal Agent Skill Harmonizer (Omarchy Cross-Harness Standard)
================================================================
Harmonizes and synchronizes agent skills across all sovereign harnesses:
- Authoritative root: C:\\Users\\vizio\\.agents\\skills & CAMELOT_OS\\.agents\\skills
- Targets:
    ~/.claude/skills          (Claude Code / Sir Boris)
    ~/.codex/skills           (OpenAI Codex / Sir Codex)
    ~/.gemini/config/skills   (Google Antigravity CLI / Sir Helios)
    ~/.hermes/skills          (Nous Hermes Prime / Hermes OS)
    ~/.agents/skills          (Universal Harness Root)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

LOG = logging.getLogger("SyncAgentSkills")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

USER_HOME = Path.home()
REPO_ROOT = Path(__file__).resolve().parent.parent

AUTHORITATIVE_SKILL_ROOTS = [
    USER_HOME / ".agents" / "skills",
    REPO_ROOT / ".agents" / "skills",
]

TARGET_HARNESS_PATHS = {
    "claude": USER_HOME / ".claude" / "skills",
    "codex": USER_HOME / ".codex" / "skills",
    "gemini": USER_HOME / ".gemini" / "config" / "skills",
    "hermes": USER_HOME / ".hermes" / "skills",
    "universal": USER_HOME / ".agents" / "skills",
}


def scan_authoritative_skills() -> Dict[str, Path]:
    """Discovers all skills containing a valid SKILL.md."""
    skills: Dict[str, Path] = {}
    for root in AUTHORITATIVE_SKILL_ROOTS:
        if not root.exists():
            continue
        for item in root.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skills[item.name] = item
    return skills


def sync_skills(dry_run: bool = False) -> Dict[str, Any]:
    """Synchronizes discovered skills into all harness directories."""
    discovered = scan_authoritative_skills()
    stats: Dict[str, Any] = {
        "authoritative_skills_count": len(discovered),
        "harnesses_updated": {},
        "errors": [],
    }

    LOG.info(f"Discovered {len(discovered)} authoritative skills across roots.")

    for harness_name, target_dir in TARGET_HARNESS_PATHS.items():
        synced_count = 0
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)

        for skill_name, skill_source in discovered.items():
            dest = target_dir / skill_name
            if dry_run:
                synced_count += 1
                continue

            try:
                # If destination exists and is a symlink, check target
                if dest.is_symlink() or dest.exists():
                    # Keep existing valid target or update if needed
                    pass
                else:
                    try:
                        # Attempt directory symlink
                        os.symlink(skill_source, dest, target_is_directory=True)
                    except OSError:
                        # Fallback to copy on Windows when unprivileged
                        shutil.copytree(skill_source, dest, dirs_exist_ok=True)
                synced_count += 1
            except Exception as e:
                stats["errors"].append(f"{harness_name}/{skill_name}: {e}")

        stats["harnesses_updated"][harness_name] = {
            "path": str(target_dir),
            "skills_synced": synced_count,
        }

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Universal Agent Skill Harmonizer")
    parser.add_argument("--dry-run", action="store_true", help="Report planned sync without writing")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    results = sync_skills(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Universal Skill Sync Complete: {results['authoritative_skills_count']} skills mapped.")
        for h, info in results["harnesses_updated"].items():
            print(f"  [{h.upper()}] -> {info['path']} ({info['skills_synced']} skills)")


if __name__ == "__main__":
    main()
