import asyncio
import json
import subprocess
import sys
from types import SimpleNamespace

from control_plane.harness import HarnessTask, SovereignHarness

from control_plane import runic_router
from scripts import cybertron_dawning


def test_dawning_rune_routes_and_queues(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")

    result = runic_router.detect_and_route(
        "//DAWNING alpha-nexus",
        context={"surface": "pytest"},
    )

    assert result is not None
    assert result.rune == "//DAWNING"
    assert result.knight == "sir_forge"
    assert result.mode == "FORGE"
    assert result.queued is True
    assert result.metadata["action"] == "cybertron_dawning"
    assert result.metadata["lead_bio_knight"] == "lukas_forge"
    assert result.metadata["project"] == "alpha-nexus"
    assert result.metadata["detail"].endswith('"alpha-nexus"')

    queued = json.loads((tmp_path / "harness_queue.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert queued["knight"] == "sir_forge"
    assert queued["directive"] == "//DAWNING alpha-nexus"


def test_dawning_rune_quotes_project_names_with_spaces(tmp_path, monkeypatch):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")

    result = runic_router.detect_and_route("//dawning Mixed Case Project")

    assert result is not None
    assert result.rune == "//DAWNING"
    assert result.metadata["project"] == "Mixed Case Project"
    assert result.metadata["detail"].endswith('"Mixed Case Project"')


def test_project_isolation_sanitizes_name(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    monkeypatch.setattr(cybertron_dawning, "PROJECTS_DIR", projects_dir)

    result = cybertron_dawning.create_project_isolation("../Alpha Nexus!")

    project_dir = projects_dir / "Alpha_Nexus"
    assert result["project"] == "Alpha_Nexus"
    assert project_dir.is_dir()
    assert (project_dir / "blueprint.md").exists()
    assert (project_dir / "task.md").exists()
    assert (project_dir / "verification.md").exists()
    manifest = json.loads((project_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["requested_name"] == "../Alpha Nexus!"


def test_run_dawning_preserves_requested_name_in_manifest(tmp_path, monkeypatch):
    state_dir = tmp_path / "runtime_state"
    projects_dir = tmp_path / "projects"
    monkeypatch.setattr(cybertron_dawning, "RUNTIME_STATE_DIR", state_dir)
    monkeypatch.setattr(cybertron_dawning, "DAWNING_STATE_FILE", state_dir / "latest.json")
    monkeypatch.setattr(cybertron_dawning, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(
        cybertron_dawning,
        "sync_lady_m",
        lambda project_name, audit: {"status": "local_recorded", "project": project_name},
    )

    assert cybertron_dawning.run_dawning("Mixed Case Project") == 0

    manifest = json.loads((projects_dir / "Mixed_Case_Project" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["project"] == "Mixed_Case_Project"
    assert manifest["requested_name"] == "Mixed Case Project"


def test_lady_m_sync_timeout_records_warning(tmp_path, monkeypatch):
    state_dir = tmp_path / "runtime_state"
    monkeypatch.setattr(cybertron_dawning, "RUNTIME_STATE_DIR", state_dir)
    monkeypatch.setattr(cybertron_dawning, "DAWNING_STATE_FILE", state_dir / "latest.json")
    monkeypatch.setattr(cybertron_dawning, "DAWNING_SYNC_PAYLOAD_FILE", state_dir / "payload.json")

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(cybertron_dawning.subprocess, "run", raise_timeout)

    result = cybertron_dawning.sync_lady_m("timeout_project", {"nodes": []})

    assert result["status"] == "sync_warn"
    assert "timed out" in result["warning"]


def test_harness_skips_dawning_execution_after_privacy_override():
    task = HarnessTask(
        id="privacy-dawning",
        knight="sir_ghost",
        directive="//DAWNING secret-project",
        priority=1,
    )

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["rune"] == "//DAWNING"
    assert result["status"] == "accepted_no_requeue"
    assert "direct dawning execution skipped" in result["reason"]


def test_harness_executes_dawning_for_forge(monkeypatch):
    calls = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="dawning ok", stderr="")

    monkeypatch.setattr("control_plane.harness.subprocess.run", fake_run)

    task = HarnessTask(
        id="forge-dawning",
        knight="sir_forge",
        directive="//DAWNING alpha nexus",
        priority=1,
    )

    result = asyncio.run(SovereignHarness()._run_knight(task))

    assert result["status"] == "dawning_complete"
    assert result["returncode"] == 0
    assert result["project"] == "alpha nexus"
    assert calls
    args, kwargs = calls[0]
    assert args[0][:2] == [
        sys.executable,
        str(cybertron_dawning.REPO_ROOT / "scripts" / "cybertron_dawning.py"),
    ]
    assert args[0][2] == "alpha nexus"
    assert kwargs["cwd"] == str(cybertron_dawning.REPO_ROOT)
    assert kwargs["timeout"] == 120
