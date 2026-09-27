# SPDX-License-Identifier: MIT
#-*- coding: utf-8 -*-
"""Unit tests for the squires.colony CLI `graph` command (graft wrapper)."""
from __future__ import annotations

import pytest

from squires import colony


@pytest.fixture
def fake_graft(monkeypatch):
    """Patch shutil.which + subprocess.run; return the captured argv/kwargs."""
    calls: dict = {}

    class _Result:
        returncode = 0

    def _which(name):
        return "C:/fake/npm/graft.cmd" if name == "graft" else None

    def _run(argv, **kwargs):
        calls["argv"] = argv
        calls["kwargs"] = kwargs
        return _Result()

    monkeypatch.setattr(colony.shutil, "which", _which)
    monkeypatch.setattr(colony.subprocess, "run", _run)
    return calls


def test_graph_defaults_to_map(fake_graft, tmp_path):
    colony.main(["graph", str(tmp_path)])
    assert fake_graft["argv"][0] == "C:/fake/npm/graft.cmd"
    assert fake_graft["argv"][1:] == ["map"]
    assert fake_graft["kwargs"]["cwd"] == str(tmp_path)


def test_graph_query_builds_ask(fake_graft, tmp_path):
    colony.main(
        ["graph", str(tmp_path), "--query", "who", "calls", "route_rune"]
    )
    assert fake_graft["argv"][1:] == ["ask", "who calls route_rune", "--source"]


def test_graph_subprocess_failure_propagates(monkeypatch, tmp_path):
    class _Result:
        returncode = 3

    monkeypatch.setattr(colony.shutil, "which", lambda n: "C:/fake/graft.cmd")
    monkeypatch.setattr(colony.subprocess, "run", lambda *a, **k: _Result())
    with pytest.raises(SystemExit) as exc:
        colony.main(["graph", str(tmp_path)])
    assert exc.value.code == 3


def test_graph_missing_cli_exits_1(monkeypatch, tmp_path):
    monkeypatch.setattr(colony.shutil, "which", lambda n: None)
    with pytest.raises(SystemExit) as exc:
        colony.main(["graph", str(tmp_path)])
    assert exc.value.code == 1


def test_graph_missing_path_exits_1(fake_graft, tmp_path):
    with pytest.raises(SystemExit) as exc:
        colony.main(["graph", str(tmp_path / "nope")])
    assert exc.value.code == 1
    assert "argv" not in fake_graft


def test_status_reports_graft_graph(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(colony, "_RICH", False)
    colony.cmd_status(tmp_path, None)
    assert "Graft:" in capsys.readouterr().out
    (tmp_path / "graft").mkdir()
    (tmp_path / "graft" / "manifest.json").write_text("{}", encoding="utf-8")
    colony.cmd_status(tmp_path, None)
    assert "✅" in capsys.readouterr().out
