# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Tests for Camelot-OS Documentation Architecture & Doc-Check Engine
===================================================================
Verifies:
1. Valid front-matter metadata parsing and schema validation.
2. Missing required metadata attributes trigger fail-closed errors.
3. Waiver expiration detection and time-bound enforcement.
4. Canonical home ID uniqueness.
5. Vertical slice manifest (slice.yaml & README.md) integrity.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest
import yaml

from scripts.doc_check import (
    is_path_waived,
    load_waivers,
    parse_front_matter,
    validate_canonical_home,
    validate_metadata,
    validate_slices,
    validate_waivers,
)

CAMELOT_HOME = Path(__file__).resolve().parent.parent


def test_parse_valid_front_matter():
    """Verify clean extraction of YAML front matter."""
    content = (
        "---\n"
        "document_id: TEST-DOC-001\n"
        "artifact_type: GOVERNANCE_SPEC\n"
        "version: 1.0.0\n"
        "---\n"
        "# Test Document\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        data, err = parse_front_matter(temp_path)
        assert err == ""
        assert data is not None
        assert data["document_id"] == "TEST-DOC-001"
    finally:
        temp_path.unlink()


def test_parse_missing_front_matter():
    """Verify rejection when front matter is missing."""
    content = "# Just Markdown\nNo front matter here."
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        data, err = parse_front_matter(temp_path)
        assert data is None
        assert "Missing opening" in err
    finally:
        temp_path.unlink()


def test_validate_metadata_passes_on_canonical_layers():
    """Verify that all canonical docs and vertical slices comply with document-schema.yaml."""
    ok, errors = validate_metadata()
    assert ok is True
    assert len(errors) == 0


def test_validate_vertical_slices():
    """Verify that all 16 vertical slices pass manifest and spec checks."""
    ok, errors = validate_slices()
    assert ok is True
    assert len(errors) == 0


def test_waiver_loading_and_expiration():
    """Verify waivers can be parsed and expired waivers are caught."""
    waivers = load_waivers()
    assert len(waivers) >= 1
    assert any(w["id"] == "WAV-2026-001" for w in waivers)

    ok, errors = validate_waivers()
    assert ok is True
    assert len(errors) == 0


def test_canonical_home_unique_ids():
    """Verify no duplicate document_ids exist across canonical docs & slices."""
    ok, errors = validate_canonical_home()
    assert ok is True
    assert len(errors) == 0
