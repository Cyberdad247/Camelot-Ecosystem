"""Pytest fixtures for VFS preflight slice #1 Task 1."""
import sys
from pathlib import Path

import pytest


@pytest.fixture
def tmp_vfs_root(tmp_path: Path) -> Path:
    """Synthetic vfs/ mirror with required .md manifests present.

    Used by catalog-integrity tests in Task 3+ (the catalog YAML files
    themselves are added in Task 5).
    """
    root = tmp_path / "vfs"
    (root / "checks").mkdir(parents=True)
    for fname in (
        "preflight.md", "systeminstructions.md", "skills.md",
        "rosters.md", "protocols.md",
    ):
        (root / fname).write_text(
            f"---\nid: {fname.replace('.md', '')}\n---\n# synthetic\n"
        )
    return root


@pytest.fixture
def tmp_preflight_root(tmp_path: Path) -> Path:
    """Synthetic 03_VAULT/runtime_state/ root, isolated per test."""
    root = tmp_path / "preflight_root"
    root.mkdir()
    return root
