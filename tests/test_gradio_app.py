import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath('01_KERNEL')) # noqa: E402

from EXCALIBUR.system.gradio_app import send_intent


@patch("EXCALIBUR.system.gradio_app.requests.post")
@patch("EXCALIBUR.system.gradio_app.datetime")
def test_send_intent_success(mock_datetime, mock_post):
    mock_datetime.now.return_value.strftime.return_value = "12:00:00"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "decision": {
            "action": "HEAL",
            "target": "SWARM"
        }
    }
    mock_post.return_value = mock_response

    result = send_intent("Test message", [])

    mock_post.assert_called_once()
    assert "12:00:00" in result
    assert "Action: HEAL" in result
    assert "Target: SWARM" in result

@patch("EXCALIBUR.system.gradio_app.requests.post")
@patch("EXCALIBUR.system.gradio_app.datetime")
def test_send_intent_success_default_decision(mock_datetime, mock_post):
    mock_datetime.now.return_value.strftime.return_value = "12:00:00"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    result = send_intent("Test message", [])

    mock_post.assert_called_once()
    assert "12:00:00" in result
    assert "Action: PROCESSED" in result
    assert "Target: UKG" in result

@patch("EXCALIBUR.system.gradio_app.requests.post")
@patch("EXCALIBUR.system.gradio_app.datetime")
def test_send_intent_non_200(mock_datetime, mock_post):
    mock_datetime.now.return_value.strftime.return_value = "12:30:00"

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    result = send_intent("Bad intent", [])

    mock_post.assert_called_once()
    assert "12:30:00" in result
    assert "[ERROR]" in result
    assert "status 500" in result

@patch("EXCALIBUR.system.gradio_app.requests.post")
@patch("EXCALIBUR.system.gradio_app.datetime")
def test_send_intent_exception(mock_datetime, mock_post):
    mock_datetime.now.return_value.strftime.return_value = "13:00:00"

    mock_post.side_effect = Exception("Connection timeout")

    result = send_intent("Timeout intent", [])

    mock_post.assert_called_once()
    assert "13:00:00" in result
    assert "[ERROR]" in result
    assert "Failed to link with Kernel: Connection timeout" in result
