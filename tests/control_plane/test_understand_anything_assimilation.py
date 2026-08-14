# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from pathlib import Path

from control_plane.understand_anything_assimilation import write_understand_anything_artifacts


def test_write_understand_anything_artifacts_creates_graph(tmp_path: Path) -> None:
    (tmp_path / "control_plane").mkdir()
    (tmp_path / "03_VAULT" / "runtime_state").mkdir(parents=True)
    (tmp_path / "control_plane" / "alpha.py").write_text("import beta\n\ndef run():\n    return 1\n", encoding="utf-8")
    (tmp_path / "control_plane" / "beta.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "03_VAULT" / "runtime_state" / "CloudBrain_Link.md").write_text("# link\n", encoding="utf-8")

    result = write_understand_anything_artifacts(tmp_path, max_files=10)

    graph = json.loads(result.graph_path.read_text(encoding="utf-8"))
    assert graph["schema"].endswith("/v1")
    assert graph["stats"]["nodes"] >= 5
    assert any(edge["type"] == "imports" for edge in graph["edges"])
    assert result.report_path.exists()
