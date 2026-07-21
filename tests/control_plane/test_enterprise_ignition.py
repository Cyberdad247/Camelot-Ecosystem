from __future__ import annotations

from control_plane.enterprise_ignition import render_markdown, run_enterprise_ignition


def test_enterprise_ignition_payload_has_operator_surfaces() -> None:
    payload = run_enterprise_ignition(write=False)

    assert payload["status"] in {"ENTERPRISE_READY", "ENTERPRISE_DEGRADED"}
    assert "camelot ignite" in payload["operator_commands"]
    assert "camelot chat" in payload["operator_commands"]

    layers = {layer["name"]: layer for layer in payload["layers"]}
    assert "chat_interface" in layers
    assert "ui_dashboard" in layers
    assert "bifrost_bridge" in layers
    assert layers["chat_interface"]["evidence"]["command"] == "camelot chat"


def test_enterprise_ignition_markdown_lists_layers() -> None:
    payload = run_enterprise_ignition(write=False)
    markdown = render_markdown(payload)

    assert "# Camelot Enterprise CLI Ignition Audit" in markdown
    assert "`camelot ignite`" in markdown
    assert "`chat_interface`" in markdown

