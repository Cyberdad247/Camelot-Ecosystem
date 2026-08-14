# SPDX-License-Identifier: MIT

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
# Directories that are never authored FOSS code: VCS metadata,
# vendored/submodule trees, generated output, and build artifacts.
# Excluding them keeps the boot gate O(authored files) and inside the
# AC2 runtime budget even when a root contains a vendored monorepo.
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "target",
    "__pycache__", ".venv", ".pytest_cache", ".turbo", ".next",
    "generated", "vendor", "third_party", ".cargo",
}
# Safety valve: stop collecting after this many flags. A tree this far
# off-license cannot change the REJECTED verdict by scanning further.
MAX_FLAGGED = 5000


def _inside_skipped_dir(root: Path, p: Path) -> bool:
    try:
        rel = p.relative_to(root)
    except ValueError:
        return False
    return any(part in SKIP_DIRS for part in rel.parts)


def scan(roots: list[Path]) -> list[Path]:
    """Return source files (non-skipped ext) missing a recognized marker.

    Empty list means OK. Skipped extensions include documentation,
    config, and lock files which have no license-header convention;
    skipped dirs include vendored/generated/build trees (SKIP_DIRS).
    Collection stops at MAX_FLAGGED so a pathological tree cannot hang
    the boot gate.
    """
    flagged: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if _inside_skipped_dir(root, p):
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
            if len(flagged) >= MAX_FLAGGED:
                return flagged
    return flagged
