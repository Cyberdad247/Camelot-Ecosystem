# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Integration test for the autonomous Rust memory governor daemon (squires_rs)."""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BINARY_NAME = "squires_rs.exe" if sys.platform == "win32" else "squires_rs"
BINARY_PATH = REPO_ROOT / "target" / "release" / BINARY_NAME


def test_rust_binary_exists():
    """Verify that squires_rs release binary was compiled."""
    assert BINARY_PATH.exists(), f"Binary not found at {BINARY_PATH}. Run 'cargo build --release -p squires_rs'"


def test_squires_rs_pagekeeper_json():
    """Verify squires_rs pagekeeper --json output format and compliance."""
    result = subprocess.run(
        [str(BINARY_PATH), "pagekeeper", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    data = json.loads(result.stdout)
    assert "total_phys_mb" in data
    assert "avail_phys_mb" in data
    assert "used_phys_mb" in data
    assert "utilization_pct" in data
    assert data["node_ceiling_mb"] == 4096.0
    assert data["node_compliant"] is True
    assert "action_taken" in data


def test_squires_rs_daemon_max_cycles(tmp_path):
    """Verify daemon executes bounded cycles and writes atomic heartbeat."""
    hb_file = tmp_path / "pagekeeper_heartbeat.json"
    result = subprocess.run(
        [
            str(BINARY_PATH),
            "daemon",
            "--interval",
            "1",
            "--max-cycles",
            "2",
            "--heartbeat",
            str(hb_file),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    assert "Cycle #1" in result.stdout
    assert "Cycle #2" in result.stdout
    assert "Daemon exiting gracefully" in result.stdout
    assert hb_file.exists()

    with open(hb_file, "r", encoding="utf-8") as f:
        hb_data = json.load(f)

    assert hb_data["daemon"] == "PAGEKEEPER_RS"
    assert hb_data["cycle"] == 2
    assert "pid" in hb_data
    assert "memory" in hb_data
    assert "status" in hb_data
    assert hb_data["status"] in ("HEALTHY", "HIGH_PRESSURE")
