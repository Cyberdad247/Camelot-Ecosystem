from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from bin import camelot_shell_setup
from control_plane.infra import cockpit


def _bind_runtime(monkeypatch, tmp_path: Path) -> None:
    runtime = tmp_path / "03_VAULT" / "runtime_state"
    logs = tmp_path / "logs"
    runtime.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cockpit, "CAMELOT_HOME", tmp_path)
    monkeypatch.setattr(cockpit, "RUNTIME_STATE", runtime)
    monkeypatch.setattr(cockpit, "CACHE_PATH", runtime / "cockpit_prompt_latest.json")
    monkeypatch.setattr(cockpit, "LAST_COMMAND_PATH", runtime / "cockpit_last_command.json")
    monkeypatch.setattr(cockpit, "QUEUE_FILE", logs / "harness_queue.jsonl")
    monkeypatch.setattr(cockpit, "DONE_FILE", logs / "worker_done.txt")
    monkeypatch.setattr(cockpit, "WARP_SYNC_PATH", runtime / "warp_workflow_sync_latest.json")
    monkeypatch.setattr(cockpit, "KNIGHT_CONFIG_PATH", runtime / "knight_configuration_latest.json")
    monkeypatch.setattr(cockpit, "AWAKEN_BOOT_PATH", runtime / "awaken_boot_latest.json")


def test_prompt_payload_marks_missing_snapshot_stale(monkeypatch, tmp_path: Path):
    _bind_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(cockpit, "_maybe_spawn_refresh", lambda *_, **__: None)
    monkeypatch.setattr(cockpit, "_system_metrics", lambda: {"cpu_percent": 10.0, "memory_percent": 20.0})

    payload = cockpit.prompt_payload()

    assert payload["status"] == "MISSING"
    assert payload["stale"] is True
    assert payload["stale_reason"] == "snapshot_missing"


def test_refresh_snapshot_writes_truthful_cache(monkeypatch, tmp_path: Path):
    _bind_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        cockpit,
        "_system_metrics",
        lambda: {
            "cpu_percent": 12.5,
            "memory_percent": 48.1,
            "memory_used_gb": 7.1,
            "memory_total_gb": 16.0,
            "source": "psutil",
        },
    )
    monkeypatch.setattr(
        cockpit,
        "_service_metrics",
        lambda: {"state": "GREEN", "green": 6, "total": 6, "probes": {"CLIProxy": True}},
    )
    monkeypatch.setattr(cockpit, "_queue_stats", lambda: {"total": 4, "done": 2, "pending": 2})

    payload = cockpit.refresh_snapshot(trigger="test")
    prompt = cockpit.prompt_payload(spawn_refresh=False)

    assert payload["trigger"] == "test"
    assert prompt["stale"] is False
    assert prompt["system"]["cpu_percent"] == 12.5
    assert prompt["queue"]["pending"] == 2
    assert "registers" not in prompt
    assert cockpit.CACHE_PATH.exists()


def test_prompt_payload_marks_expired_cache_stale(monkeypatch, tmp_path: Path):
    _bind_runtime(monkeypatch, tmp_path)
    old = cockpit.utc_now() - timedelta(seconds=cockpit.PROMPT_TTL_SECONDS + 2)
    cockpit.CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cockpit.CACHE_PATH.write_text(
        json.dumps(
            {
                "status": "OK",
                "generated_utc": old.isoformat(),
                "ttl_seconds": cockpit.PROMPT_TTL_SECONDS,
                "system": {},
                "services": {},
                "queue": {},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cockpit, "_maybe_spawn_refresh", lambda *_, **__: None)

    payload = cockpit.prompt_payload()

    assert payload["stale"] is True
    assert payload["stale_reason"] == "expired"


def test_cockpit_exec_routes_runic_input(monkeypatch, tmp_path: Path):
    _bind_runtime(monkeypatch, tmp_path)

    class _Result:
        rune = "//STATUS"
        knight = "sir_boris"
        directive = "//STATUS"
        mode = "ORACLE"
        task_id = "rune-test"
        queued = True
        queue_error = None
        metadata = {"action": "system_status"}

    monkeypatch.setattr(cockpit, "route_rune", lambda rune, param, context=None: _Result())

    payload = cockpit.cockpit_exec("//STATUS")

    assert payload["routed"] is True
    assert payload["rune"] == "//STATUS"
    assert payload["knight"] == "sir_boris"
    assert payload["status"] == "ROUTED"
    assert cockpit.LAST_COMMAND_PATH.exists()


def test_cockpit_exec_preserves_shell_passthrough(monkeypatch, tmp_path: Path):
    _bind_runtime(monkeypatch, tmp_path)

    payload = cockpit.cockpit_exec("dir")

    assert payload["routed"] is False
    assert payload["classification"] == "shell"
    assert payload["status"] == "SHELL_PASSTHROUGH"


def test_powershell_shell_setup_contains_cockpit_helpers():
    script = camelot_shell_setup._powershell_cockpit_script()

    assert "Enter-CamelotCockpit" in script
    assert "Exit-CamelotCockpit" in script
    assert "camelot --json cockpit prompt" in script


def test_camelot_parser_accepts_cockpit_commands():
    from control_plane.runes.camelot_cli import _build_parser

    parser = _build_parser()
    args = parser.parse_args(["cockpit", "exec", "//STATUS"])

    assert args.command == "cockpit"
    assert args.cockpit_command == "exec"
    assert args.input == ["//STATUS"]


def test_camelot_main_cockpit_refresh_json(monkeypatch, capsys):
    from bin import bifrost
    from control_plane.runes import camelot_cli

    class _Config:
        config_path = "test-config"

        def get_profile(self, profile):
            return object()

    class _Provenance:
        def log_verification(self, run):
            return None

    monkeypatch.setattr(bifrost, "enforce", lambda: "local-owner:test")
    monkeypatch.setattr(camelot_cli, "ConfigManager", lambda: _Config())
    monkeypatch.setattr(camelot_cli, "ProvenanceManager", lambda: _Provenance())
    monkeypatch.setattr(camelot_cli, "refresh_snapshot", lambda trigger="manual": {"status": "OK", "trigger": trigger})
    monkeypatch.setattr("sys.argv", ["camelot", "--json", "cockpit", "refresh"])

    assert camelot_cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "OK"
    assert payload["trigger"] == "manual"
