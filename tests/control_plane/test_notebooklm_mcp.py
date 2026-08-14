# SPDX-License-Identifier: MIT

"""Tests for NotebookLM MCP server (file-system pivot).

PR #4 of NOTES_MNEMOSYNE_WIRING.md.

Coverage:
  * slugify produces filesystem-safe cache filenames
  * export_notebook writes to CACHE_DIR under a slugified stem
  * list_local_notebooks evicts TTL-expired files
  * delete_local_notebook roundtrip
  * delete of a missing slug returns False (HUMAN_GATE idempotent)
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Import via bin/ namespace — the module lives at CAMELOT_OS/bin/notebooklm_mcp_server.py
import bin.notebooklm_mcp_server as mcp_server  # noqa: E402


@pytest.fixture
def tmp_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(mcp_server, "CACHE_DIR", tmp_path)
    monkeypatch.setenv("NOTEBOOK_CACHE_TTL", "30")
    yield tmp_path


def test_slugify_lowercases_and_dedashes() -> None:
    assert mcp_server.slugify("Hello World!") == "hello-world"
    assert mcp_server.slugify("  KEbab-CASE 99  ") == "kebab-case-99"
    assert mcp_server.slugify("___") == "untitled"
    assert mcp_server.slugify("") == "untitled"


def test_export_writes_to_cache_under_slugified_stem(
    tmp_cache: Path,
) -> None:
    from unittest.mock import patch

    with patch.object(mcp_server, "_scrape_notebook_html", return_value="<h1>TestNb</h1>"):
        out = mcp_server.export_notebook("notebooklm.google.com/test-page")
    out_path = Path(out)
    assert out_path.exists()
    assert out_path.parent == tmp_cache
    assert "test-page" in out_path.name


def test_list_evicts_old_files(tmp_cache: Path) -> None:
    old = tmp_cache / "old.md"
    old.write_text("# old", encoding="utf-8")
    far_past = time.time() - 86400 * 60  # 60 days old (TTL is 30)
    os.utime(old, (far_past, far_past))

    recent = tmp_cache / "recent.md"
    recent.write_text("# recent", encoding="utf-8")

    remaining = mcp_server.list_local_notebooks()
    assert "old.md" not in remaining
    assert "recent.md" in remaining


def test_delete_roundtrip(tmp_cache: Path) -> None:
    f = tmp_cache / "x.md"
    f.write_text("data", encoding="utf-8")
    assert mcp_server.delete_local_notebook("x") is True
    assert not f.exists()


def test_delete_missing_returns_false(tmp_cache: Path) -> None:
    assert mcp_server.delete_local_notebook("nope-not-cached") is False


def test_cache_path_creates_directory(tmp_path: Path) -> None:
    target_dir = tmp_path / "deep" / "notebooklm_cache"
    import bin.notebooklm_mcp_server as mod
    mod.CACHE_DIR = target_dir
    p = mod.cache_path("slug")
    assert p.parent == target_dir
    assert p == target_dir / "slug.md"
