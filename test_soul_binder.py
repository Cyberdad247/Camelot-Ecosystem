import importlib.util
import sys
from unittest.mock import patch

# Dynamically import the module due to the 01_KERNEL prefix
module_name = "soul_binder"
file_path = "01_KERNEL/agora/agents/soul_binder.py"

spec = importlib.util.spec_from_file_location(module_name, file_path)
soul_binder = importlib.util.module_from_spec(spec)
sys.modules[module_name] = soul_binder
spec.loader.exec_module(soul_binder)


def test_generate_soul_prompt_success():
    """Test the happy path where generation succeeds."""
    mock_response = {"response": "Refined personality response"}

    with patch("requests.post") as mock_post:
        # Configure the mock response
        mock_post.return_value.json.return_value = mock_response

        result = soul_binder.generate_soul_prompt("merlin", {"O": 0.95})

        # Verify the outcome
        assert result == "Refined personality response"
        mock_post.assert_called_once()


def test_generate_soul_prompt_exception():
    """Test the failure path where requests.post raises an exception."""
    with patch("requests.post") as mock_post:
        # Configure mock to raise an exception
        mock_post.side_effect = Exception("Connection refused")

        result = soul_binder.generate_soul_prompt("merlin", {"O": 0.95})

        # Verify it gracefully handles the exception and returns None
        assert result is None
        mock_post.assert_called_once()
