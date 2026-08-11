from __future__ import annotations

import json
from pathlib import Path

from control_plane.infra import cloudbrain_sync


def _patch_queue(monkeypatch, tmp_path: Path) -> Path:
    queue_path = tmp_path / "03_VAULT" / "runtime_state" / "cloudbrain_sync_queue.jsonl"
    monkeypatch.setattr(cloudbrain_sync, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(cloudbrain_sync, "QUEUE_PATH", queue_path)
    return queue_path


def test_sync_after_event_queues_failed_cloudbrain_sync(monkeypatch, tmp_path):
    queue_path = _patch_queue(monkeypatch, tmp_path)

    def _raise():
        raise RuntimeError("network blocked")

    monkeypatch.setattr(cloudbrain_sync, "_load_notebooklm_bridge", _raise)

    result = cloudbrain_sync.sync_after_event(
        event_type="pytest",
        command="camelot pytest",
        results={"status": "OK"},
    )

    assert result["triggered"] is True
    assert result["queued"] is True
    assert result["queue_path"] == str(queue_path)
    events = cloudbrain_sync._read_queue()
    assert len(events) == 1
    assert events[0]["event_type"] == "pytest"
    assert events[0]["command"] == "camelot pytest"
    assert "network blocked" in events[0]["error"]


def test_sync_queue_status_reports_backlog(monkeypatch, tmp_path):
    queue_path = _patch_queue(monkeypatch, tmp_path)
    queue_path.parent.mkdir(parents=True)
    queue_path.write_text(
        json.dumps(
            {
                "id": "queued-1",
                "created_utc": "2026-05-12T00:00:00+00:00",
                "updated_utc": "2026-05-12T00:00:00+00:00",
                "event_type": "ledger_update",
                "command": "ledger update",
                "result_summary": "{}",
                "attempts": 0,
                "last_error": "blocked",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    status = cloudbrain_sync.sync_queue_status()

    assert status["status"] == "QUEUE_STATUS"
    assert status["pending"] == 1


def test_flush_sync_queue_removes_successful_events(monkeypatch, tmp_path):
    queue_path = _patch_queue(monkeypatch, tmp_path)
    queue_path.parent.mkdir(parents=True)
    queue_path.write_text(
        json.dumps(
            {
                "id": "queued-1",
                "created_utc": "2026-05-12T00:00:00+00:00",
                "updated_utc": "2026-05-12T00:00:00+00:00",
                "event_type": "ledger_update",
                "command": "ledger update",
                "result_summary": "{'status': 'OK'}",
                "attempts": 0,
                "last_error": "blocked",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    class _Bridge:
        async def async_sync_state(self, *, extra_summary):
            assert "ledger_update" in extra_summary
            return {"status": "synced"}

    monkeypatch.setattr(cloudbrain_sync, "_load_notebooklm_bridge", lambda: _Bridge())

    result = cloudbrain_sync.flush_sync_queue()

    assert result["status"] == "FLUSHED"
    assert result["flushed"] == 1
    assert result["pending"] == 0
    assert not queue_path.exists()


def test_flush_sync_queue_keeps_failed_events(monkeypatch, tmp_path):
    queue_path = _patch_queue(monkeypatch, tmp_path)
    queue_path.parent.mkdir(parents=True)
    queue_path.write_text(
        json.dumps(
            {
                "id": "queued-1",
                "created_utc": "2026-05-12T00:00:00+00:00",
                "updated_utc": "2026-05-12T00:00:00+00:00",
                "event_type": "ledger_update",
                "command": "ledger update",
                "result_summary": "{}",
                "attempts": 0,
                "last_error": "blocked",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    def _raise():
        raise RuntimeError("still blocked")

    monkeypatch.setattr(cloudbrain_sync, "_load_notebooklm_bridge", _raise)

    result = cloudbrain_sync.flush_sync_queue()

    assert result["status"] == "PARTIAL"
    assert result["flushed"] == 0
    assert result["pending"] == 1
    event = cloudbrain_sync._read_queue()[0]
    assert "still blocked" in event["last_error"]


def test_camelot_parser_accepts_cloudbrain_queue_commands():
    from control_plane.runes.camelot_cli import _build_parser

    parser = _build_parser()

    status_args = parser.parse_args(["cloudbrain", "queue", "status"])
    flush_args = parser.parse_args(["cloudbrain", "queue", "flush", "--limit", "2"])

    assert status_args.command == "cloudbrain"
    assert status_args.cloudbrain_command == "queue"
    assert status_args.cloud_queue_command == "status"
    assert flush_args.cloud_queue_command == "flush"
    assert flush_args.limit == 2


def test_camelot_main_cloudbrain_queue_status_passes_bifrost_gate(monkeypatch, capsys):
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
    monkeypatch.setattr(
        camelot_cli,
        "sync_queue_status",
        lambda: {
            "status": "READY",
            "queue_path": "test-queue.jsonl",
            "pending": 0,
            "events": [],
        },
    )
    monkeypatch.setattr(
        "sys.argv",
        ["camelot", "--json", "cloudbrain", "queue", "status"],
    )

    assert camelot_cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "READY"
    assert payload["pending"] == 0
