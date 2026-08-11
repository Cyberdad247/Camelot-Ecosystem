# -*- coding: utf-8 -*-
"""Runic router tests for the Hermes_Prime runes — parse / normalize / route.

Mirrors the conventions of tests/test_boot_omniroute.py and
tests/test_cybertron_dawning.py (QUEUE_FILE monkeypatch, detect_and_route,
queued-entry assertions) for the three Harmony runes and Omega_HermesPrime.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from control_plane import runic_router

REPO_ROOT = Path(__file__).resolve().parents[1]
PHIAL_PATH = REPO_ROOT / "01_KERNEL" / "titan" / "phials" / "hermes_prime_phial.py"


@pytest.fixture
def router(monkeypatch, tmp_path):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    return runic_router


def _real_engine(tmp_path):
    """Real PhialEngine isolated on tmp paths (no repo state pollution)."""
    spec = importlib.util.spec_from_file_location("hp_phial_route", PHIAL_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return (mod, mod.PhialEngine(state_path=tmp_path / "state.json", base_dir=tmp_path))


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------


def test_normalize_harmony_runes_uppercases(router):
    assert router.normalize_rune("//sync_vfs_workspace") == "//SYNC_VFS_WORKSPACE"
    assert router.normalize_rune("//SYNC_VFS_WORKSPACE") == "//SYNC_VFS_WORKSPACE"
    assert router.normalize_rune("//forge_hermes_prime_files") == "//FORGE_HERMES_PRIME_FILES"
    assert router.normalize_rune("//ignite_self_evolution_loop") == "//IGNITE_SELF_EVOLUTION_LOOP"


def test_normalize_omega_hermes_prime_case_insensitive(router):
    assert router.normalize_rune("Omega_HermesPrime") == "Omega_HermesPrime"
    assert router.normalize_rune("omega_hermesprime") == "Omega_HermesPrime"
    assert router.normalize_rune("OMEGA_HERMESPRIME") == "Omega_HermesPrime"


def test_normalize_unknown_unchanged(router):
    assert router.normalize_rune("//NOPE") == "//NOPE"


# ---------------------------------------------------------------------------
# parse
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        ("//SYNC_VFS_WORKSPACE", ("//SYNC_VFS_WORKSPACE", "")),
        ("//FORGE_HERMES_PRIME_FILES build", ("//FORGE_HERMES_PRIME_FILES", "build")),
        ("//ignite_self_evolution_loop cycle", ("//IGNITE_SELF_EVOLUTION_LOOP", "cycle")),
        ("Omega_HermesPrime deep audit", ("Omega_HermesPrime", "deep audit")),
        ("omega_hermesprime", ("Omega_HermesPrime", "")),
    ],
)
def test_parse_hermes_prime_runes(router, text, expected):
    assert router.parse_rune(text) == expected


@pytest.mark.parametrize("text", ["plain text with no rune", "//NOPE", "Omega_UNKNOWN"])
def test_parse_unknown_returns_none(router, text):
    assert router.parse_rune(text) is None


# ---------------------------------------------------------------------------
# route
# ---------------------------------------------------------------------------


def test_route_sync_vfs_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: _real_engine(tmp_path))

    result = runic_router.detect_and_route("//SYNC_VFS_WORKSPACE")

    assert result is not None
    assert result.rune == "//SYNC_VFS_WORKSPACE"
    assert result.knight == "hermes_prime"
    assert result.mode == "ORACLE"
    assert result.queued is True
    assert result.metadata["action"] == "sync_vfs_workspace"
    assert result.metadata["status"] == "SYNCED"

    queued = json.loads((tmp_path / "harness_queue.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert queued["knight"] == "hermes_prime"
    assert queued["directive"] == "//SYNC_VFS_WORKSPACE"


def test_route_forge_hermes_prime_files_scaffolds(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: _real_engine(tmp_path))

    result = runic_router.detect_and_route("//FORGE_HERMES_PRIME_FILES")

    assert result is not None
    assert result.rune == "//FORGE_HERMES_PRIME_FILES"
    assert result.knight == "hermes_prime"
    assert result.mode == "FORGE"
    assert result.queued is True
    assert result.metadata["action"] == "forge_hermes_prime_files"
    assert result.metadata["status"] == "SCAFFOLDED"
    # empty tmp base -> all five scaffold files created by the real engine
    assert set(result.metadata["created"]) == {
        "soul.md", "spark.md", "harness.md", "skills.md", "merlin_notebook_blend.md",
    }
    # idempotent: second route finds everything present
    second = runic_router.detect_and_route("//FORGE_HERMES_PRIME_FILES")
    assert second.metadata["status"] == "OK"
    assert second.metadata["created"] == []


def test_route_ignite_self_evolution_loop_runs_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: _real_engine(tmp_path))

    result = runic_router.detect_and_route("//IGNITE_SELF_EVOLUTION_LOOP forage nexus")

    assert result is not None
    assert result.rune == "//IGNITE_SELF_EVOLUTION_LOOP"
    assert result.knight == "hermes_prime"
    assert result.mode == "SWARM"
    assert result.queued is True
    m = result.metadata
    assert m["action"] == "ignite_self_evolution_loop"
    assert m["framework"] == "MGV + AlphaEvolve"
    assert m["seed"] == "forage nexus"
    assert m["status"] == "CYCLE_COMPLETE"
    assert m["cycle_id"].startswith("hp-")
    assert m["verdict"] in ("DEPLOY", "REVISE", "ABORT")
    assert "weights_before" in m and "weights_after" in m and "blacklist" in m

    queued = json.loads((tmp_path / "harness_queue.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert queued["knight"] == "hermes_prime"
    assert queued["directive"] == "//IGNITE_SELF_EVOLUTION_LOOP forage nexus"


def test_route_omega_hermes_prime_dispatch(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)

    result = runic_router.detect_and_route("Omega_HermesPrime deep audit")

    assert result is not None
    assert result.rune == "Omega_HermesPrime"
    assert result.knight == "hermes_prime"
    assert result.mode == "ORACLE"
    assert result.queued is True
    assert "research" in result.metadata["description"]

    queued = json.loads((tmp_path / "harness_queue.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert queued["knight"] == "hermes_prime"
    assert queued["directive"] == "Omega_HermesPrime deep audit"


def test_route_degrades_gracefully_when_engine_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: (None, None))

    result = runic_router.detect_and_route("//IGNITE_SELF_EVOLUTION_LOOP")

    assert result is not None
    assert result.knight == "hermes_prime"
    assert result.queued is True
    assert result.metadata["status"] == "UNAVAILABLE"


def test_unknown_rune_still_escalates_to_sir_boris(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)

    # not detected as a known rune at all...
    assert runic_router.detect_and_route("//NOPE") is None

    # ...and direct routing escalates instead of matching hermes_prime
    result = runic_router.route_rune("//NOPE")
    assert result.knight == "sir_boris"
    assert result.directive == "UNKNOWN_RUNE: //NOPE"
