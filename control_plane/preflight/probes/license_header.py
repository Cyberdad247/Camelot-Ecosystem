"""FOSS license marker probe — flags files without a recognized SPDX header.

Per VFS_PREFLIGHT_DESIGN.md §4 `foss_validation_constraints` (sequence 020).
Surfaced via probes.license_header_run.py in Task 6.
"""
from __future__ import annotations
from pathlib import Path
import re

SPDX_PATTERNS = [
    re.compile(r"\bSPDX-License-Identifier:\s*([A-Za-z0-9\-\.\+]+)"),
    re.compile(r"Copyright\s+\(c\)\s+\d{4}"),
]
SKIP_EXTS = {
    ".md", ".txt", ".json", ".lock", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".gitignore", ".gitattributes",
}


def scan(roots: list[Path]) -> list[Path]:
    """Return source files (non-skipped ext) missing a recognized marker.

    Empty list means OK. Skipped extensions include documentation,
    config, and lock files which have no license-header convention.
    """
    flagged: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in SKIP_EXTS:
                continue
            try:
                head = p.read_text(
                    encoding="utf-8", errors="ignore"
                )[:4096]
            except OSError:
                continue
            if any(rx.search(head) for rx in SPDX_PATTERNS):
                continue
            flagged.append(p)
    return flagged
