from __future__ import annotations

from pathlib import Path

from control_plane.infra.provenance import ProvenanceManager
from control_plane.infra import harness
from control_plane.infra.harness import HarnessTask, SovereignHarness
import asyncio


def test_provenance_manager_degrades_without_mempalace_secret(monkeypatch, tmp_path: Path) -> None:
    """Command startup must not fail merely because optional L2 memory is unavailable."""
    monkeypatch.delenv("MEMPALACE_SECRET", raising=False)

    manager = ProvenanceManager(vault_path=tmp_path / "missions")

    assert manager.mempalace is None
    assert manager.memory_status["state"] == "degraded"
    assert manager.memory_status["reason"] == "MEMPALACE_SECRET is not set"


def test_boot_harness_uses_hidden_infra_entrypoint(monkeypatch, tmp_path: Path) -> None:
    """The normal boot path must not create a second Windows terminal."""
    monkeypatch.setattr(harness, "PID_FILE", tmp_path / "harness.pid")
    monkeypatch.setattr(harness.time, "sleep", lambda _: None)
    calls: list[tuple[list[str], dict]] = []

    class Process:
        pid = 42

        def poll(self):
            return None

    monkeypatch.setattr(
        harness.subprocess,
        "Popen",
        lambda command, **kwargs: calls.append((command, kwargs)) or Process(),
    )

    ok, _ = harness.boot_harness(Path(harness.CAMELOT_HOME))

    assert ok
    assert calls[0][0][-1].endswith("control_plane\\infra\\harness.py")
    flags = calls[0][1]["creationflags"]
    assert flags & getattr(harness.subprocess, "CREATE_NO_WINDOW", 0)
    assert not flags & getattr(harness.subprocess, "CREATE_NEW_CONSOLE", 0)


def test_merlin_plan_task_writes_a_plan_artifact(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(harness, "CAMELOT_HOME", tmp_path)
    task = HarnessTask(id="plan-1", knight="merlin_omega", directive="//PLAN inspect boot")

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["status"] == "PLANNED"
    assert Path(result["artifact_path"]).is_file()


def test_queue_state_marks_claimed_task_complete(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(harness, "QUEUE_STATE_FILE", tmp_path / "queue-state.jsonl")
    worker = SovereignHarness()

    worker._record_task_state("job-1", "claimed")
    worker._record_task_state("job-1", "completed", result={"status": "PLANNED"})

    assert worker._task_states()["job-1"]["state"] == "completed"


def test_requeue_allows_only_plan_directives(monkeypatch, tmp_path: Path) -> None:
    queue = tmp_path / "queue.jsonl"
    queue.write_text('{"id":"plan-1","knight":"merlin_omega","directive":"//PLAN inspect boot"}\n', encoding="utf-8")
    monkeypatch.setattr(harness, "QUEUE_FILE", queue)

    assert harness.requeue_legacy_task("plan-1") is True
    assert '"queue_version": 2' in queue.read_text(encoding="utf-8")


def test_anya_task_writes_gate_artifact(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(harness, "CAMELOT_HOME", tmp_path)
    task = HarnessTask(id="anya-1", knight="anya_omega", directive="Omega_ANYA inspect boot")

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["status"] == "GATED"
    assert Path(result["artifact_path"]).is_file()
