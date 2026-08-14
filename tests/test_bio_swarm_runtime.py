# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from control_plane.bio_swarm_runtime import (
    BioSwarmPaths,
    preflight_bio_swarm,
    read_bio_swarm_status,
    run_bio_swarm_once,
    write_bio_swarm_runtime_status,
)

from control_plane import camelot_cli


def test_status_reports_missing_binary_as_blocked(tmp_path: Path) -> None:
    paths = BioSwarmPaths.for_root(tmp_path)

    status = read_bio_swarm_status(paths)

    assert status["status"] == "BINARY_MISSING"
    assert status["binary_exists"] is False
    assert status["state_exists"] is False


def test_preflight_passes_with_binary_and_writable_state(tmp_path: Path) -> None:
    paths = BioSwarmPaths.for_root(tmp_path)
    binary = paths.binary_candidates[0]
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_text("fake binary", encoding="utf-8")

    status = preflight_bio_swarm(paths)

    assert status["status"] == "PREFLIGHT_PASS"
    assert status["issues"] == []
    assert status["binary_path"] == str(binary)


def test_runtime_status_artifact_is_persisted(tmp_path: Path) -> None:
    paths = BioSwarmPaths.for_root(tmp_path)
    binary = paths.binary_candidates[0]
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_text("fake binary", encoding="utf-8")

    artifact = write_bio_swarm_runtime_status(paths)

    payload = json.loads(paths.state_path.read_text(encoding="utf-8"))
    assert artifact["status"] == "READY"
    assert payload["status"] == "READY"
    assert payload["binary_sha256"]


def test_once_runs_binary_and_writes_release_artifact(tmp_path: Path, monkeypatch) -> None:
    paths = BioSwarmPaths.for_root(tmp_path)
    binary = paths.binary_candidates[0]
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_text("fake binary", encoding="utf-8")

    def fake_run(command, **kwargs):
        assert command[:2] == [str(binary), "--once"]
        assert "--json" in command
        assert kwargs["timeout"] == 15
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"status": "PASS", "tasks_done": 1, "tasks_fail": 0}),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bio_swarm_once(paths, fixture=True, timeout=15)

    release = json.loads(paths.release_path.read_text(encoding="utf-8"))
    assert result["status"] == "PASS"
    assert release["verdict"] == "PASS"
    assert release["binary_sha256"]
    assert paths.queue_path.exists()


def test_cli_parser_accepts_bio_swarm_commands() -> None:
    parser = camelot_cli._build_parser()

    args = parser.parse_args(["bio-swarm", "once", "--fixture", "--timeout", "7", "--json"])

    assert args.command == "bio-swarm"
    assert args.bio_swarm_action == "once"
    assert args.fixture is True
    assert args.timeout == 7
    assert args.json_output is True
