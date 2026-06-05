"""OMEGA Defense Nexus Phase 0 acceptance tests — new knight imports + personas."""
import importlib.util
import sys
from pathlib import Path
import pytest

CAMELOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMELOT))

KNIGHTS_DIR = CAMELOT / "01_KERNEL" / "iron_gate" / "DEFENSE_GRID" / "knights"


def _load_knight(name: str):
    spec = importlib.util.spec_from_file_location(name, KNIGHTS_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------
# SirHeimdall
# ------------------------------------------------------------------

def test_heimdall_import():
    mod = _load_knight("heimdall")
    assert hasattr(mod, "SirHeimdall")
    assert hasattr(mod, "FingerprintVector")
    assert hasattr(mod, "WatchReport")


def test_heimdall_scan_returns_report():
    mod = _load_knight("heimdall")
    h = mod.SirHeimdall(repo_root=CAMELOT)
    report = h.scan_fingerprint_vectors()
    assert hasattr(report, "vectors")
    assert hasattr(report, "is_clean")
    assert isinstance(report.vectors, list)


def test_heimdall_watch_report_fields():
    mod = _load_knight("heimdall")
    report = mod.WatchReport(vectors=[], scan_path="/test", timestamp="2026-06-05T00:00:00Z")
    assert report.is_clean is True
    assert report.critical_count == 0


# ------------------------------------------------------------------
# SirGalahad
# ------------------------------------------------------------------

def test_galahad_import():
    mod = _load_knight("galahad")
    assert hasattr(mod, "SirGalahad")


def test_galahad_zero_trace_write(tmp_path):
    mod = _load_knight("galahad")
    g = mod.SirGalahad()
    target = tmp_path / "test_output.txt"
    written = g.zero_trace_write(target, "sovereign content")
    assert written.exists()
    assert written.read_text() == "sovereign content"
    # Timestamp should be scrubbed to fixed epoch
    assert target.stat().st_mtime == pytest.approx(946684800.0, abs=1.0)


def test_galahad_stealth_exec_sanitizes_env():
    mod = _load_knight("galahad")
    g = mod.SirGalahad()
    result = g.stealth_exec(["python", "-c", "import os; print(os.environ.get('COMPUTERNAME','ANON'))"])
    assert result.returncode == 0
    assert "sovereign_node" in result.stdout or "ANON" in result.stdout


# ------------------------------------------------------------------
# SirNemesisPrime
# ------------------------------------------------------------------

def test_nemesis_import():
    mod = _load_knight("nemesis_prime")
    assert hasattr(mod, "SirNemesisPrime")
    assert hasattr(mod, "NeutralizeResult")


def test_nemesis_quarantine(tmp_path):
    mod = _load_knight("nemesis_prime")
    # Create a dummy suspicious file
    target = tmp_path / "suspicious.exe"
    target.write_text("bad actor")
    quarantine_dir = tmp_path / "quarantine"
    n = mod.SirNemesisPrime(quarantine_dir=quarantine_dir)
    result = n.quarantine(target)
    assert result.success is True
    assert not target.exists()
    assert list(quarantine_dir.glob("*.exe"))


def test_nemesis_counter_telemetry_requires_approval():
    mod = _load_knight("nemesis_prime")
    n = mod.SirNemesisPrime()
    result = n.counter_telemetry("evil.telemetry.com", approved=False)
    assert result.hitl_required is True
    assert result.success is False


# ------------------------------------------------------------------
# KNIGHT_PERSONAS in camelot_context
# ------------------------------------------------------------------

def test_omega_personas_registered():
    from bin.camelot_context import load_knight_persona
    for knight_id in ("sir_heimdall", "sir_galahad", "sir_nemesis_prime",
                       "sir_socrates", "lady_mnemosyne", "lady_alexandria"):
        persona = load_knight_persona(knight_id)
        assert persona, f"Missing persona for {knight_id}"
        assert len(persona) > 20, f"Persona too short for {knight_id}"
