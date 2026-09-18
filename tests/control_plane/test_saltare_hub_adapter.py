# SPDX-License-Identifier: MIT
"""Failing-first test for Saltare hub adapter (Task 2)."""

from unittest.mock import patch, MagicMock
from control_plane.infra.saltare_hub_adapter import SaltareHubAdapter


def test_saltare_adapter_init_defaults():
    adapter = SaltareHubAdapter()
    assert adapter.local_port == 8090
    assert adapter.url == "http://127.0.0.1:8090/v1/tools/execute"


def test_saltare_dispatch_hub_tool_success():
    adapter = SaltareHubAdapter()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "SUCCESS",
        "result": {"stdout": "file processed", "exit_code": 0}
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        res = adapter.dispatch_hub_tool("format_file", {"path": "src/main.rs"})
        assert res["success"] is True
        assert res["result"]["exit_code"] == 0
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["tool"] == "format_file"
        assert kwargs["json"]["arguments"]["path"] == "src/main.rs"


def test_saltare_dispatch_offline_fallback():
    adapter = SaltareHubAdapter()
    with patch("requests.post", side_effect=ConnectionRefusedError("Port 8090 unreachable")):
        res = adapter.dispatch_hub_tool("ping", {})
        assert res["success"] is False
        assert "unreachable" in res["error"].lower()
