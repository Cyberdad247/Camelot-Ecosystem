# SPDX-License-Identifier: MIT

"""Hermes_Prime harness execution — queued Harmony runes / Omega_HermesPrime
tasks must actually execute against the PhialEngine (closes the queue-consumer
gap), and must be skipped when privacy-overridden to sir_ghost.

Mirrors test_cybertron_dawning.py harness conventions: real SovereignHarness
._run_knight with a real PhialEngine isolated on tmp_path (no repo state
pollution), and the router's engine loader monkeypatched per-test.
"""
import asyncio
import importlib.util

import pytest

from control_plane import runic_router
from control_plane.harness import HarnessTask, SovereignHarness


@pytest.fixture
def phial_module():
    spec = importlib.util.spec_from_file_location(
        "hermes_prime_phial_harness_test",
        runic_router.CAMELOT_HOME / "01_KERNEL" / "titan" / "phials" / "hermes_prime_phial.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def isolated_engine(tmp_path, phial_module, monkeypatch):
    """Real PhialEngine rooted at tmp_path, wired into the router's loader."""
    engine = phial_module.PhialEngine(
        state_path=tmp_path / "state.json",
        base_dir=tmp_path,
    )
    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: (None, engine))
    return engine


def test_harness_executes_hermes_prime_sync(isolated_engine):
    task = HarnessTask(id="hp-sync", knight="hermes_prime", directive="//SYNC_VFS_WORKSPACE", priority=1)

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "//SYNC_VFS_WORKSPACE"
    assert result["action"] == "sync_vfs_workspace"
    assert result["status"] == "SYNCED"
    assert result["files"] == []  # fresh workspace — nothing scanned yet
    assert len(result["missing"]) == 5  # all scaffold files absent


def test_harness_executes_hermes_prime_forge(isolated_engine, tmp_path):
    task = HarnessTask(id="hp-forge", knight="hermes_prime", directive="//FORGE_HERMES_PRIME_FILES", priority=1)

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "//FORGE_HERMES_PRIME_FILES"
    assert result["action"] == "forge_hermes_prime_files"
    assert result["status"] == "SCAFFOLDED"
    assert len(result["created"]) == 5
    vfs_dir = tmp_path / "Knights" / "Hermes_Prime"
    assert (vfs_dir / "soul.md").exists()
    assert (vfs_dir / "spark.md").exists()
    assert (vfs_dir / "harness.md").exists()
    assert (vfs_dir / "skills.md").exists()
    assert (vfs_dir / "merlin_notebook_blend.md").exists()


def test_harness_executes_hermes_prime_ignite(isolated_engine):
    task = HarnessTask(
        id="hp-ignite",
        knight="hermes_prime",
        directive="//IGNITE_SELF_EVOLUTION_LOOP forage the nexus scaffold",
        priority=1,
    )

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "//IGNITE_SELF_EVOLUTION_LOOP"
    assert result["action"] == "ignite_self_evolution_loop"
    assert result["status"] == "CYCLE_COMPLETE"
    assert result["seed"] == "forage the nexus scaffold"
    assert result["cycle_id"].startswith("hp-")
    assert "weights_after" in result
    assert "blacklist" in result


def test_harness_executes_omega_hermesprime(isolated_engine):
    task = HarnessTask(id="hp-omega", knight="hermes_prime", directive="Omega_HermesPrime deep audit", priority=1)

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "Omega_HermesPrime"
    assert result["action"] == "ignite_self_evolution_loop"
    assert result["status"] == "CYCLE_COMPLETE"
    assert result["seed"] == "deep audit"
    assert result["cycle_id"].startswith("hp-")


def test_harness_hermes_prime_knight_runs_cycle_for_plain_directive(isolated_engine):
    task = HarnessTask(id="hp-directive", knight="hermes_prime", directive="synthesize R&D yields", priority=1)

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["status"] == "CYCLE_COMPLETE"
    assert result["seed"] == "synthesize R&D yields"
    assert result["cycle_id"].startswith("hp-")


def test_harness_skips_hermes_prime_execution_after_privacy_override(monkeypatch):
    calls = []

    class _FakeEngine:
        def sync_vfs(self):
            calls.append("sync")
            return {"status": "SYNCED"}

        def forge_scaffold(self):
            calls.append("forge")
            return {"status": "SCAFFOLDED"}

        def run_cycle(self, seed):
            calls.append(("cycle", seed))
            return {"status": "CYCLE_COMPLETE"}

    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: (None, _FakeEngine()))

    task = HarnessTask(
        id="hp-privacy",
        knight="sir_ghost",
        directive="//IGNITE_SELF_EVOLUTION_LOOP scan the secret key",
        priority=1,
    )

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "//IGNITE_SELF_EVOLUTION_LOOP"
    assert result["status"] == "accepted_no_requeue"
    assert "direct hermes_prime execution skipped" in result["reason"]
    assert calls == []  # engine must never execute under the privacy override


def test_harness_skips_omega_hermes_prime_after_privacy_override(monkeypatch):
    # Same recording-fake protection as the other privacy test — if the guard
    # ever regresses, this fails loudly instead of touching production state.
    calls = []

    class _FakeEngine:
        def sync_vfs(self):
            calls.append("sync")
            return {"status": "SYNCED"}

        def forge_scaffold(self):
            calls.append("forge")
            return {"status": "SCAFFOLDED"}

        def run_cycle(self, seed):
            calls.append(("cycle", seed))
            return {"status": "CYCLE_COMPLETE"}

    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: (None, _FakeEngine()))

    task = HarnessTask(
        id="hp-omega-privacy",
        knight="sir_ghost",
        directive="Omega_HermesPrime inspect local token",
        priority=1,
    )

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "Omega_HermesPrime"
    assert result["status"] == "accepted_no_requeue"
    assert "direct hermes_prime execution skipped" in result["reason"]
    assert calls == []


def test_harness_degrades_when_hermes_prime_engine_unavailable(monkeypatch):
    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: (None, None))

    task = HarnessTask(id="hp-unavailable", knight="hermes_prime", directive="//SYNC_VFS_WORKSPACE", priority=1)

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "//SYNC_VFS_WORKSPACE"
    assert result["status"] == "UNAVAILABLE"
    assert "deferred" in result["detail"]


def test_harness_returns_error_when_engine_raises(monkeypatch):
    class _BoomEngine:
        def sync_vfs(self):
            raise RuntimeError("engine exploded")

    monkeypatch.setattr(runic_router, "_load_hermes_prime_engine", lambda: (None, _BoomEngine()))

    task = HarnessTask(id="hp-error", knight="hermes_prime", directive="//SYNC_VFS_WORKSPACE", priority=1)

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "//SYNC_VFS_WORKSPACE"
    assert result["status"] == "ERROR"
    assert "engine exploded" in result["error"]
