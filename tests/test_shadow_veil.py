"""OMEGA Defense Nexus Phase 2 — Shadow Veil tests.

Tests the Heimdall→Hermes→Nemesis AUTO response pipeline.
All live file-system and network ops are either mocked or use tmpdir.
hosts-file amendment (counter_telemetry) remains HUMAN_GATE and is
verified structurally only.
"""
from __future__ import annotations

import importlib.util as _ilu
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path


CAMELOT = Path(__file__).resolve().parents[1]
KNIGHTS_DIR = CAMELOT / "01_KERNEL/iron_gate/DEFENSE_GRID/knights"
SHADOW_VEIL_DIR = CAMELOT / "01_KERNEL/iron_gate/DEFENSE_GRID/shadow_veil"
sys.path.insert(0, str(CAMELOT))


def _load(rel: str, name: str):
    spec = _ilu.spec_from_file_location(name, CAMELOT / rel)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_shadow_veil():
    return _load(
        "01_KERNEL/iron_gate/DEFENSE_GRID/shadow_veil/shadow_pipeline.py",
        "sv_test_pipeline",
    )


# ── Test 1: ShadowVeil instantiates and loads Heimdall + Nemesis ─────────────

def test_shadow_veil_init_loads_knights():
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)
    assert sv._heimdall is not None, "SirHeimdall should load from knights/"
    assert sv._nemesis is not None, "SirNemesisPrime should load from knights/"
    st = sv.status()
    assert st.heimdall_ok is True
    assert st.nemesis_ok is True


# ── Test 2: ShadowStatus fields are correct after init ───────────────────────

def test_shadow_status_initial_values():
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)
    st = sv.status()
    assert st.active is False
    assert st.threats_detected == 0
    assert st.auto_responses == 0
    assert st.hitl_pending == 0
    assert st.thread_alive is False


# ── Test 3: scan_once runs Heimdall and updates status ───────────────────────

def test_scan_once_populates_vector_count():
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)
    st = sv.scan_once()
    # vector_count ≥ 0 after a real scan (live repo has fingerprint vectors)
    assert st.last_scan_at > 0.0
    assert isinstance(st.vector_count, int) and st.vector_count >= 0


# ── Test 4: scan_once increments threats_detected on non-zero vectors ─────────

def test_scan_once_increments_threats_detected(monkeypatch):
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)

    # Simulate a report with 2 vectors
    @dataclass
    class FakeVector:
        vector_type: str = "METADATA"
        source: str = "some_file.py"
        severity: str = "MEDIUM"

    @dataclass
    class FakeReport:
        vectors: list = field(default_factory=list)
        critical_count: int = 0
        is_clean: bool = True
        scan_path: str = ""
        timestamp: float = field(default_factory=time.time)

    fake_report = FakeReport(
        vectors=[FakeVector(), FakeVector()],
        critical_count=0,
        is_clean=False,
    )

    monkeypatch.setattr(sv._heimdall, "scan_fingerprint_vectors", lambda: fake_report)
    st = sv.scan_once()
    assert st.threats_detected == 1
    assert st.vector_count == 2


# ── Test 5: NETWORK threat → counter_telemetry HUMAN_GATE queued ─────────────

def test_network_threat_queues_hitl_not_auto():
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)
    sv._dispatch_nemesis_response({"type": "NETWORK", "source": "telemetry.evil.com", "severity": "CRITICAL"})
    st = sv.status()
    # hitl_pending increases, auto_responses stays 0
    assert st.hitl_pending == 1
    assert st.auto_responses == 0


# ── Test 6: PROCESS threat → terminate_process called AUTO ───────────────────

def test_process_threat_dispatches_terminate(monkeypatch):
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)
    terminated = []
    monkeypatch.setattr(sv._nemesis, "terminate_process", lambda pid: terminated.append(pid) or type("R", (), {"success": True})())
    sv._dispatch_nemesis_response({"type": "PROCESS", "source": "proc", "pid": 1234, "severity": "HIGH"})
    assert 1234 in terminated
    assert sv.status().auto_responses == 1


# ── Test 7: FILE threat → quarantine AUTO only if file exists ─────────────────

def test_file_threat_quarantines_existing_file(monkeypatch):
    d = Path(tempfile.mkdtemp(prefix="sv_test_"))
    try:
        target = d / "suspect.py"
        target.write_text("malicious code")
        mod = _load_shadow_veil()
        sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)
        quarantined = []
        monkeypatch.setattr(sv._nemesis, "quarantine", lambda p: quarantined.append(str(p)) or type("R", (), {"success": True})())
        sv._dispatch_nemesis_response({"type": "FILE", "source": str(target), "severity": "HIGH"})
        assert len(quarantined) == 1
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Test 8: FILE threat for non-existent file → no quarantine called ─────────

def test_file_threat_skips_nonexistent_file():
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False)
    sv._dispatch_nemesis_response({"type": "FILE", "source": "/nonexistent/ghost.py", "severity": "HIGH"})
    assert sv.status().auto_responses == 0


# ── Test 9: start/stop controls thread_alive ─────────────────────────────────

def test_start_stop_thread_lifecycle(monkeypatch):
    mod = _load_shadow_veil()
    sv = mod.ShadowVeil(repo_root=CAMELOT, hermes_enabled=False, scan_interval=9999)
    # Stub scan to avoid actual heimdall scan in background thread
    monkeypatch.setattr(sv._heimdall, "scan_fingerprint_vectors", lambda: type("R", (), {
        "vectors": [], "critical_count": 0, "is_clean": True, "scan_path": "", "timestamp": time.time()
    })())
    sv.start()
    time.sleep(0.1)  # give thread a moment to start
    assert sv.status().thread_alive is True
    assert sv.status().active is True
    sv.stop()
    time.sleep(0.1)
    assert sv.status().active is False


# ── Test 10: counter_telemetry HUMAN_GATE guard is structural ────────────────

def test_counter_telemetry_human_gate_guard():
    """Verify SirNemesisPrime refuses hosts amendment without approved=True."""
    mod = _load(
        "01_KERNEL/iron_gate/DEFENSE_GRID/knights/nemesis_prime.py",
        "sv_nemesis_test",
    )
    nemesis = mod.SirNemesisPrime(quarantine_dir=Path(tempfile.mkdtemp(prefix="sv_quarantine_")))
    result = nemesis.counter_telemetry("evil.telemetry.com", approved=False)
    assert result.hitl_required is True
    assert result.success is False
    assert "HUMAN_GATE" in result.detail
