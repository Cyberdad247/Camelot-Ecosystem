# SPDX-License-Identifier: MIT
"""Failing-first test for Cribo bundle validator (Task 3)."""

from unittest.mock import patch, MagicMock
from control_plane.infra.cribo_bundle_validator import CriboBundleValidator


def test_cribo_validator_missing_entry(tmp_path):
    validator = CriboBundleValidator()
    entry = tmp_path / "non_existent.py"
    out = tmp_path / "bundle.py"
    res = validator.bundle_and_validate(entry, out)
    assert res["success"] is False
    assert "not found" in res["error"]


def test_cribo_validator_success(tmp_path):
    validator = CriboBundleValidator()
    entry = tmp_path / "main.py"
    entry.write_text("def run():\n    return 42\n", encoding="utf-8")
    out = tmp_path / "bundle.py"

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "Bundled 1 file(s). Savings: 35%"
    mock_proc.stderr = ""

    with patch("subprocess.run", return_value=mock_proc):
        # simulate bundle written
        out.write_text("def run():\n    return 42\n", encoding="utf-8")
        res = validator.bundle_and_validate(entry, out)
        assert res["success"] is True
        assert res["savings_pct"] >= 0
        assert res["bundle_bytes"] > 0
