import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add morgana directory to sys.path
morgana_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '02_FORGE', 'PORTAL_CORE', 'Modal', 'morgana'))
sys.path.insert(0, morgana_dir)

from morgana_core import morgana_brain_v2, morgana_brain, MorganaRequest

def test_morgana_brain_v2_delegates_to_morgana_brain():
    """Test that morgana_brain_v2 calls morgana_brain correctly"""
    req = MorganaRequest(task="analyze this", mock_mode=True)

    # We patch morgana_brain within the module morgana_core
    with patch('morgana_core.morgana_brain') as mock_morgana_brain:
        mock_morgana_brain.return_value = {"status": "success", "mocked": True}

        # When calling the local function of morgana_brain_v2
        result = morgana_brain_v2.local(req)

        # Verify it delegated to morgana_brain
        mock_morgana_brain.assert_called_once_with(req)
        assert result == {"status": "success", "mocked": True}

def test_morgana_brain_v2_mock_mode():
    """Test morgana_brain_v2 end-to-end with mock_mode=True"""
    req = MorganaRequest(task="analyze this", mock_mode=True)

    # In order for morgana_brain_v2 to call the actual logic of morgana_brain,
    # we need to ensure that the function call delegates to morgana_brain.local
    # when we call morgana_brain_v2.local, because in the modal app morgana_brain
    # is a modal Function, not a regular python function. So in python it needs to call .local()

    with patch('morgana_core.morgana_brain', side_effect=morgana_brain.local):
        res = morgana_brain_v2.local(req)
        assert "morgana" in res
        assert "[MOCK_REPLY]" in res["morgana"]
        assert "meta" in res
        assert res["meta"]["mode"] == "RESEARCH"
