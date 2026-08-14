# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from pathlib import Path

# Add bin/ directory to sys.path
bin_dir = str(Path(__file__).resolve().parent.parent / "bin")
if bin_dir not in sys.path:
    sys.path.insert(0, bin_dir)

from onboarding import gather_system_diagnostics


def test_gather_system_diagnostics():
    diagnostics = gather_system_diagnostics()
    assert "status" in diagnostics
    assert diagnostics["status"] == "ready"
    assert "env" in diagnostics
    assert "python" in diagnostics["env"]
    assert "git" in diagnostics["env"]
    assert "integrations" in diagnostics
    assert "appwrite" in diagnostics["integrations"]
    assert "vfs" in diagnostics
    assert "scaffolded" in diagnostics["vfs"]
