"""OMEGA Defense Nexus Phase 1 acceptance tests — ColonyNexus."""
import importlib.util as _ilu
import sys
from pathlib import Path

import pytest

CAMELOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMELOT))

def _load(rel: str, name: str):
    spec = _ilu.spec_from_file_location(name, CAMELOT / rel)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

ColonyNexus = _load(
    "01_KERNEL/iron_gate/DEFENSE_GRID/colony_nexus.py", "colony_nexus"
).ColonyNexus
ColonyState = sys.modules["colony_nexus"].ColonyState


# ── Fixtures ─────────────────────────────────────────────────────────────────

_CRITICAL_REPORT = """\
# CLARITY_CORE Colony Report
**Generated:** 2026-06-05 00:00 UTC

## Executive Summary

| Metric | Value |
|--------|-------|
| Risk Score | 100.0 / 100 |
| Risk Label | **CRITICAL** |
| HITL Required | Yes |

## Findings

- 797 potential secret(s) detected — CRITICAL
- 4283 duplicate file(s) detected
- 209 unused imports (dead code)
- Large codebase: 5,136,881 lines
"""

_LOW_REPORT = """\
# CLARITY_CORE Colony Report
**Generated:** 2026-06-05 00:00 UTC

## Executive Summary

| Metric | Value |
|--------|-------|
| Risk Score | 12.0 / 100 |
| Risk Label | **LOW** |
| HITL Required | No |

## Findings

- 0 potential secret(s) detected
- 5 duplicate file(s) detected
- 3 unused imports (dead code)
- Large codebase: 10,000 lines
"""


@pytest.fixture
def critical_report(tmp_path):
    p = tmp_path / "colony_report.md"
    p.write_text(_CRITICAL_REPORT, encoding="utf-8")
    return p


@pytest.fixture
def low_report(tmp_path):
    p = tmp_path / "colony_report.md"
    p.write_text(_LOW_REPORT, encoding="utf-8")
    return p


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_colony_nexus_parses_critical(critical_report):
    nx = ColonyNexus(report_path=critical_report, hermes_enabled=False)
    state = nx.scan()
    assert state.risk_score == pytest.approx(100.0)
    assert state.risk_label == "CRITICAL"
    assert state.hitl_tier == "HUMAN_GATE"
    assert state.risk_entropy == pytest.approx(1.0)
    assert state.is_critical is True
    assert state.requires_human_gate is True


def test_colony_nexus_parses_low(low_report):
    nx = ColonyNexus(report_path=low_report, hermes_enabled=False)
    state = nx.scan()
    assert state.risk_score == pytest.approx(12.0)
    assert state.risk_label == "LOW"
    assert state.hitl_tier == "AUTO"
    assert state.risk_entropy == pytest.approx(0.12)
    assert state.is_critical is False
    assert state.requires_human_gate is False


def test_colony_nexus_extracts_secrets(critical_report):
    nx = ColonyNexus(report_path=critical_report, hermes_enabled=False)
    state = nx.scan()
    assert state.secrets_count == 797
    assert state.duplicates_count == 4283
    assert state.unused_imports == 209


def test_colony_nexus_missing_report():
    nx = ColonyNexus(report_path=Path("/nonexistent/colony_report.md"), hermes_enabled=False)
    state = nx.scan()
    assert state.risk_score == 0.0
    assert state.risk_label == "LOW"
    assert state.hitl_tier == "AUTO"


def test_colony_nexus_risk_entropy_for_gate(critical_report):
    nx = ColonyNexus(report_path=critical_report, hermes_enabled=False)
    entropy = nx.risk_entropy_for_gate()
    assert 0.0 <= entropy <= 1.0
    assert entropy == pytest.approx(1.0)


def test_colony_nexus_hermes_delta_fires(critical_report, monkeypatch):
    """Hermes publish called when score delta ≥ threshold on first scan."""
    published = []

    class _FakeBus:
        def publish(self, channel, payload):
            published.append((channel, payload))

    monkeypatch.setattr(
        "control_plane.hermes_bridge.HermesBus", _FakeBus, raising=False
    )
    # Patch import inside colony_nexus module
    colony_mod = sys.modules["colony_nexus"]
    original = colony_mod.ColonyNexus._emit_hermes

    emit_calls = []

    def _patched_emit(self, state, delta):
        emit_calls.append((state.risk_score, delta))

    colony_mod.ColonyNexus._emit_hermes = _patched_emit

    try:
        nx = colony_mod.ColonyNexus(report_path=critical_report, hermes_enabled=True)
        nx.scan()
        assert len(emit_calls) == 1
        assert emit_calls[0][0] == pytest.approx(100.0)
    finally:
        colony_mod.ColonyNexus._emit_hermes = original
