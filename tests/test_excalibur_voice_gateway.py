# SPDX-License-Identifier: MIT
from unittest.mock import patch, MagicMock
from control_plane.dispatch.excalibur_voice_gateway import (
    trigger_voice_capture,
    send_voice_response,
    check_excalibur_status
)

def test_check_excalibur_status_offline():
    status = check_excalibur_status()
    assert "status" in status

def test_send_voice_response_mocked():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp
        
        res = send_voice_response("Hail Camelot", "SIR_BORIS")
        assert res is True

def test_trigger_voice_capture_mocked():
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'AUDIO_PAYLOAD_BYTES'
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp
        
        audio = trigger_voice_capture(duration=1)
        assert audio == b'AUDIO_PAYLOAD_BYTES'
