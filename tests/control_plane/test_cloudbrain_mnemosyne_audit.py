from __future__ import annotations

from control_plane.cloudbrain_mnemosyne_audit import (
    _classify_queue_event,
    render_markdown,
    run_lady_mnemosyne_cloudbrain_audit,
)


def test_classifies_notebooklm_null_rpc() -> None:
    event = {
        "event_type": "heimdall_watch",
        "command": "perimeter_scan",
        "error": "RPCError: RPC CYK0Xb returned null result data",
    }

    result = _classify_queue_event(event)

    assert result["classification"] == "notebooklm_rpc_null_result"
    assert "Retry" in result["recommendation"]


def test_audit_report_is_lady_mnemosyne_owned() -> None:
    payload = run_lady_mnemosyne_cloudbrain_audit(write=False)

    assert payload["owner"]["owner"] == "LADY_MNEMOSYNE"
    assert payload["schema"] == "camelot.lady-mnemosyne-cloudbrain-audit/v1"
    assert any(item["primary_owner"] == "LADY_MNEMOSYNE" for item in payload["assignments"])


def test_render_markdown_includes_queue_and_owner() -> None:
    payload = run_lady_mnemosyne_cloudbrain_audit(write=False)
    markdown = render_markdown(payload)

    assert "Lady Mnemosyne Cloudbrain Audit" in markdown
    assert "LADY_MNEMOSYNE" in markdown
    assert "Queue" in markdown
