import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("01_KERNEL")) # noqa: E402

from EXCALIBUR.system.gradio_app import send_intent  # noqa: E402


@patch("EXCALIBUR.system.gradio_app.requests.post")
def test_send_intent_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "decision": {
            "action": "HEAL",
            "target": "NODE_1"
        }
    }
    mock_post.return_value = mock_response

    result = send_intent("fix node 1", [])

    assert "[MERLIN_Omega] :: Action: HEAL | Target: NODE_1" in result
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "intent" in kwargs["params"]
    assert kwargs["params"]["intent"] == "fix node 1"

@patch("EXCALIBUR.system.gradio_app.requests.post")
def test_send_intent_success_default_values(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {} # missing decision entirely
    mock_post.return_value = mock_response

    result = send_intent("status", [])

    assert "[MERLIN_Omega] :: Action: PROCESSED | Target: UKG" in result

@patch("EXCALIBUR.system.gradio_app.requests.post")
def test_send_intent_error_status(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    result = send_intent("break", [])

    assert "[ERROR] :: Kernel responded with status 500" in result

@patch("EXCALIBUR.system.gradio_app.requests.post")
def test_send_intent_exception(mock_post):
    mock_post.side_effect = Exception("Connection Timeout")

    result = send_intent("timeout", [])

    assert "[ERROR] :: Failed to link with Kernel: Connection Timeout" in result
