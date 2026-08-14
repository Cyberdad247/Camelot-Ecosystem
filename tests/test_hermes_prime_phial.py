# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""Tests for the Hermes_Prime PhialEngine (MGV + Ouroboros + re-weighting)."""
import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PHIAL_PATH = REPO_ROOT / "01_KERNEL" / "titan" / "phials" / "hermes_prime_phial.py"


def _load_phial():
    spec = importlib.util.spec_from_file_location("hp_phial_test", PHIAL_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def phial(tmp_path):
    """Engine isolated on tmp base_dir + tmp state file."""
    mod = _load_phial()
    vfs = tmp_path / "Knights" / "Hermes_Prime"
    vfs.mkdir(parents=True)
    (vfs / "soul.md").write_text("# Hermes_Prime soul\n", encoding="utf-8")
    engine = mod.PhialEngine(state_path=tmp_path / "state.json", base_dir=tmp_path)
    return mod, engine, tmp_path


def test_initial_weights(phial):
    mod, engine, _ = phial
    assert engine.weights["deploy_threshold"] == 0.70
    assert 0.0 <= engine.weights["forage_breadth"] <= 1.0


def test_run_cycle_completes_and_persists(phial):
    mod, engine, tmp_path = phial
    result = engine.run_cycle("forage os and the nexus scaffold")
    assert result["status"] == "CYCLE_COMPLETE"
    assert result["verdict"] in ("DEPLOY", "REVISE", "ABORT")
    assert 0.0 <= result["pass_ratio"] <= 1.0
    assert set(result["hypotheses"][0]) == {"kind", "target", "label"}
    assert (tmp_path / "state.json").exists()
    # memory bank fed
    assert engine.state()["memory_records"] >= 1


def test_failure_reweights_blacklist_and_weights(phial):
    mod, engine, tmp_path = phial
    missing = str(tmp_path / "definitely" / "missing.md")
    before = dict(engine.weights)
    r1 = engine.run_cycle(f"verify {missing}")
    assert r1["failed"] >= 1
    # the missing target is now known-bad
    assert engine.blacklist.get(missing, 0.0) > 0.0
    # weights must have moved (AlphaEvolve) and stay clamped
    for k in ("forage_breadth", "verify_strictness", "deploy_threshold"):
        assert 0.0 <= engine.weights[k] <= 1.0
    assert engine.weights != before


def test_ouroboros_memory_compounds_failures(phial):
    mod, engine, tmp_path = phial
    missing = str(tmp_path / "nope" / "ghost.md")
    engine.run_cycle(f"verify {missing}")
    first = engine.blacklist.get(missing, 0.0)
    engine.run_cycle(f"verify {missing}")
    second = engine.blacklist.get(missing, 0.0)
    # tail feeds the head — the penalty must strictly compound (decay 0.9 + 1)
    assert second > first


def test_probe_hits_corpus_and_misses(phial):
    mod, engine, tmp_path = phial
    # "soul" is in the corpus (soul.md); "zygotic_quark" is not
    hyps = [mod.Hypothesis("probe", "soul", "probe:1"), mod.Hypothesis("probe", "zygotic_quark", "probe:2")]
    outcomes = engine.verify(hyps)
    assert outcomes[0].passed is True
    assert outcomes[1].passed is False


def test_forge_scaffold_idempotent(tmp_path):
    mod = _load_phial()
    engine = mod.PhialEngine(state_path=tmp_path / "s.json", base_dir=tmp_path)
    first = engine.forge_scaffold()
    assert first["status"] == "SCAFFOLDED"
    assert set(first["created"]) == set(mod._SCAFFOLD_FILES)
    second = engine.forge_scaffold()
    assert second["status"] == "OK"
    assert second["created"] == []


def test_sync_vfs_reports_files_and_missing(phial):
    mod, engine, _ = phial
    sync = engine.sync_vfs()
    assert sync["status"] == "SYNCED"
    assert "soul.md" in sync["scaffold_present"]
    assert "spark.md" in sync["missing"]
    assert any(f["name"] == "soul.md" for f in sync["files"])


def test_deploy_writes_artifact(phial):
    mod, engine, _ = phial
    deploy = engine.deploy_artifact("verified nexus")
    assert deploy["status"] == "DEPLOYED"
    path = Path(deploy["artifact"])
    assert path.exists()
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["knight"] == "HERMES_PRIME"
    assert engine.stats["artifacts_deployed"] >= 1


def test_persistence_survives_reload(tmp_path):
    mod = _load_phial()
    state_path = tmp_path / "persist.json"
    e1 = mod.PhialEngine(state_path=state_path, base_dir=tmp_path)
    e1.run_cycle("forage os")
    e2 = mod.PhialEngine(state_path=state_path, base_dir=tmp_path)
    assert e2.stats["cycles_run"] == e1.stats["cycles_run"]
    assert e2.memory == e1.memory
    assert e2.weights == e1.weights


def test_reset_clears_state(phial):
    mod, engine, _ = phial
    engine.run_cycle("forage os")
    reset = engine.reset()
    assert reset["status"] == "RESET"
    assert engine.memory == []
    assert engine.blacklist == {}
    assert engine.weights == mod._DEFAULT_WEIGHTS


# --------------------------------------------------------------------------
# runic router wiring (//SYNC_VFS_WORKSPACE, //FORGE_HERMES_PRIME_FILES,
# //IGNITE_SELF_EVOLUTION_LOOP) — engine faked to keep tests hermetic
# --------------------------------------------------------------------------
class _FakeEngine:
    def sync_vfs(self):
        return {"action": "sync", "status": "SYNCED", "files": [], "scaffold_present": [], "missing": []}

    def forge_scaffold(self):
        return {"action": "forge", "status": "OK", "created": [], "present": ["soul.md"]}

    def run_cycle(self, seed="default"):
        return {"cycle_id": "hp-fake", "seed": seed, "status": "CYCLE_COMPLETE", "verdict": "DEPLOY", "pass_ratio": 1.0}


@pytest.fixture
def router(monkeypatch, tmp_path):
    from control_plane import runic_router

    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: (None, _FakeEngine()))
    return runic_router


@pytest.mark.parametrize(
    "rune,action",
    [
        ("//SYNC_VFS_WORKSPACE", "sync_vfs_workspace"),
        ("//FORGE_HERMES_PRIME_FILES", "forge_hermes_prime_files"),
        ("//IGNITE_SELF_EVOLUTION_LOOP", "ignite_self_evolution_loop"),
    ],
)
def test_router_wiring(router, rune, action):
    result = router.detect_and_route(rune)
    assert result is not None
    assert result.knight == "hermes_prime"
    assert result.metadata["action"] == action
    assert result.queued is True


def test_router_ignite_returns_engine_cycle(router):
    result = router.detect_and_route("//IGNITE_SELF_EVOLUTION_LOOP audit the nexus")
    assert result.metadata["verdict"] == "DEPLOY"
    assert result.metadata["cycle_id"] == "hp-fake"
    assert result.metadata["framework"] == "MGV + AlphaEvolve"


def test_omega_hermes_prime_dispatch(router):
    result = router.detect_and_route("Omega_HermesPrime deep audit")
    assert result is not None
    assert result.knight == "hermes_prime"
    assert result.queued is True
