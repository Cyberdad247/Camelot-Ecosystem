"""Watchtower: NUL integrity probe, pressure assessment, tick wiring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from control_plane.infra import watchtower
from control_plane.infra.watchtower import (
    assess,
    nul_probe,
    tick,
    watchtower_tick,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _reset_watchtower_state():
    """Module-level level/finding cache must not leak between tests."""
    watchtower._state["level"] = None
    watchtower._state["findings"] = ()
    yield
    watchtower._state["level"] = None
    watchtower._state["findings"] = ()


def _make_home(tmp_path: Path) -> Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "control_plane").mkdir()
    return tmp_path


def test_nul_probe_flags_only_text_contamination(tmp_path: Path) -> None:
    home = _make_home(tmp_path)
    (home / "scripts" / "corrupt.ps1").write_bytes(b"$x = 1\r\n\x00$y = 2\r\n")
    (home / "scripts" / "clean.py").write_text("print('ok')\n", encoding="utf-8")
    (home / "scripts" / "fixture.pyc").write_bytes(b"\x93\x00\r\n\x00")

    findings = nul_probe(home=home)

    assert len(findings) == 1, f"binary fixtures must be exempt, got {findings}"
    assert "corrupt.ps1" in findings[0]
    assert "1 nul bytes" in findings[0]


def test_nul_probe_respects_byte_cap(tmp_path: Path) -> None:
    home = _make_home(tmp_path)
    (home / "scripts" / "big.md").write_bytes(b"a" * 100 + b"\x00")

    assert nul_probe(home=home, max_bytes=50) == []
    assert len(nul_probe(home=home, max_bytes=1000)) == 1


def test_scan_walks_all_three_roots_and_skips_junk_dirs(tmp_path: Path) -> None:
    home = _make_home(tmp_path)
    for root in ("scripts", "tests", "control_plane"):
        (home / root / "sample.py").write_text("x = 1\n", encoding="utf-8")
    junk = home / "control_plane" / "node_modules" / "pkg"
    junk.mkdir(parents=True)
    (junk / "dep.js").write_bytes(b"\x00")

    hits = nul_probe(home=home)

    assert hits == [], f"skipped dirs must not be scanned, got {hits}"
    files = {p.name for p in watchtower.iter_scan_files(home=home)}
    assert files == {"sample.py"}


@pytest.mark.skipif(__import__("os").name != "nt", reason="psapi counters are Windows-only")
def test_resource_snapshot_shape() -> None:
    snap = watchtower.resource_snapshot(cpu_sample_s=0.05)
    assert snap["commit_pct"] is not None and 0 <= snap["commit_pct"] <= 100
    assert snap["physical_available_bytes"] > 0
    assert snap["cpu_pct"] is None or 0 <= snap["cpu_pct"] <= 100


@pytest.mark.parametrize(
    ("snapshot", "findings", "expected"),
    [
        ({"commit_pct": 96.0, "physical_available_bytes": 4 * 1024**3}, [], "CRITICAL"),
        ({"commit_pct": 90.0, "physical_available_bytes": 4 * 1024**3}, [], "WARN"),
        ({"commit_pct": 50.0, "physical_available_bytes": 512 * 1024**2}, [], "WARN"),
        ({"commit_pct": 50.0, "physical_available_bytes": 4 * 1024**3}, [], "GREEN"),
        ({"commit_pct": 50.0, "physical_available_bytes": 4 * 1024**3},
         ["a.py (1 nul bytes)"], "CRITICAL"),
        ({"commit_pct": None, "physical_available_bytes": None}, [], "GREEN"),
    ],
)
def test_assess_thresholds(snapshot, findings, expected) -> None:
    assert assess(snapshot, findings) == expected


def test_tick_scans_on_cycle_zero_and_writes_heartbeat(tmp_path: Path) -> None:
    home = _make_home(tmp_path)
    (home / "scripts" / "bad.ps1").write_bytes(b"a\x00b")

    telemetry = tick(0, home=home, cpu_sample_s=0.05)

    assert telemetry["nul_scan"] is True
    assert telemetry["level"] == "CRITICAL"
    assert len(telemetry["nul_findings"]) == 1
    assert telemetry["source"] == "watchtower"

    hb = home / "03_VAULT" / "runtime_state" / "harness_heartbeat.jsonl"
    assert hb.exists()
    record = json.loads(hb.read_text(encoding="utf-8").splitlines()[-1])
    assert record["source"] == "watchtower"
    assert record["level"] == "CRITICAL"


def test_tick_off_cycle_reuses_cached_findings(tmp_path: Path) -> None:
    home = _make_home(tmp_path)
    (home / "scripts" / "bad.ps1").write_bytes(b"a\x00b")

    first = tick(0, home=home, cpu_sample_s=0.05)
    second = tick(1, home=home, cpu_sample_s=0.05)

    assert first["nul_scan"] is True
    assert second["nul_scan"] is False
    # cached verdict keeps the alert visible between full scans
    assert len(second["nul_findings"]) == 1
    assert second["level"] == "CRITICAL"


def test_watchtower_tick_never_raises(monkeypatch) -> None:
    def boom(_cycle: int) -> dict:
        raise RuntimeError("telemetry exploded")

    monkeypatch.setattr(watchtower, "tick", boom)
    telemetry = watchtower_tick(3)

    assert telemetry["level"] == "UNKNOWN"
    assert "RuntimeError" in telemetry["error"]


def test_harness_wiring_calls_watchtower_each_cycle() -> None:
    source = (REPO_ROOT / "control_plane" / "infra" / "harness.py").read_text(
        encoding="utf-8"
    )
    assert "watchtower_tick(self._watchtower_cycle)" in source
    assert "self._watchtower_cycle += 1" in source
    assert "self._watchtower_cycle = 0" in source


def test_pagekeeper_rs_probe() -> None:
    from control_plane.infra.watchtower import pagekeeper_rs_probe
    probe = pagekeeper_rs_probe()
    assert probe["daemon"] == "PAGEKEEPER_RS"
    assert "status" in probe
    assert probe["node_ceiling_mb"] == 4096.0
    assert probe["node_compliant"] is True
    assert "resident_mb" in probe


def test_watchtower_visual_and_html(tmp_path: Path) -> None:
    from control_plane.infra.watchtower import (
        export_html_dashboard,
        render_watchtower_visual,
        tick,
    )
    telemetry = tick(0, cpu_sample_s=0.01)
    visual = render_watchtower_visual(telemetry)
    assert "WATCHTOWER SOVEREIGN TELEMETRY COCKPIT" in visual
    assert "PAGEKEEPER_RS" in visual
    assert "CYBERTRONIA" in visual

    html_file = tmp_path / "test_dashboard.html"
    res_path = export_html_dashboard(telemetry, output_path=html_file)
    assert res_path.exists()
    content = res_path.read_text(encoding="utf-8")
    assert "Watchtower Sovereign Dashboard" in content
    assert "PageKeeper RS" in content
