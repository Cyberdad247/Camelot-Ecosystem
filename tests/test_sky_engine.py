import sys
import importlib.util
from unittest.mock import MagicMock
import pytest


# Mock modal to avoid attempting remote connections or loading Modal locally.
modal_mock = MagicMock()
def passthrough_decorator(func=None, **kwargs):
    if func:
        return func
    def decorator(f):
        # Attach a mock .remote to allow f.remote(...) calls to succeed
        f.remote = MagicMock(return_value={"mock": "data"})
        return f
    return decorator

# Setup mock attributes to simulate Modal components
modal_mock.App.return_value.function = passthrough_decorator
modal_mock.web_endpoint = passthrough_decorator
# Also mock modal.Image so image = modal.Image... works
modal_mock.Image.debian_slim.return_value.pip_install.return_value = MagicMock()

# Inject mock into sys.modules before importing sky_engine
sys.modules["modal"] = modal_mock


# Load the sky_engine module using importlib
spec = importlib.util.spec_from_file_location("sky_engine", "01_KERNEL/merlin/sky_engine.py")
sky_engine = importlib.util.module_from_spec(spec)
sys.modules["sky_engine"] = sky_engine
spec.loader.exec_module(sky_engine)


def test_invoke_with_data():
    """Test invoke extracts query and context and calls deep_thought_protocol."""
    item = {
        "query": "What is the meaning of life?",
        "context": {"user_id": 42}
    }

    # We re-mock remote to verify this specific call
    sky_engine.deep_thought_protocol.remote = MagicMock(return_value={"test": "success"})

    result = sky_engine.invoke(item)

    assert result == {"test": "success"}
    sky_engine.deep_thought_protocol.remote.assert_called_once_with(
        "What is the meaning of life?", {"user_id": 42}
    )

def test_invoke_empty_dict():
    """Test invoke handles missing fields gracefully."""
    item = {}

    sky_engine.deep_thought_protocol.remote = MagicMock(return_value={"test": "success_empty"})

    result = sky_engine.invoke(item)

    assert result == {"test": "success_empty"}
    sky_engine.deep_thought_protocol.remote.assert_called_once_with("", {})

def test_deep_thought_protocol():
    """Test deep_thought_protocol returns the expected structure."""
    query = "test query"
    context = {"test": "context"}

    result = sky_engine.deep_thought_protocol(query, context)

    assert "insight" in result
    assert "test query" in result["insight"]
    assert result["source_truth"] == "Verified via 12 sources (Simulated)"
    assert result["symbollect"] == "[💎Gold][⚡Zap]"
