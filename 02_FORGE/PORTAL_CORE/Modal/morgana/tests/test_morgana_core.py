import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockDecorator:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, func):
        return func

class MockApp:
    def __init__(self, *args, **kwargs):
        pass
    def function(self, *args, **kwargs):
        return MockDecorator()

mock_modal = MagicMock()
mock_modal.App = MockApp
mock_modal.fastapi_endpoint = MagicMock(return_value=MockDecorator())

# Mocking the module dependencies before importing it
sys.modules['modal'] = mock_modal
sys.modules['appwrite.client'] = MagicMock()
sys.modules['appwrite.services.databases'] = MagicMock()
sys.modules['appwrite.id'] = MagicMock()
sys.modules['circuitbreaker'] = MagicMock()
sys.modules['circuitbreaker.circuit'] = MagicMock(return_value=MockDecorator())
sys.modules['structlog'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.asymmetric'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()


from morgana_core import MorganaRequest, morgana_brain, morgana_brain_v2

def test_morgana_brain_v2_delegates_to_morgana_brain():
    # Setup
    req = MorganaRequest(task="Test task", mock_mode=True)

    # We want to patch morgana_brain within the module where it's used
    with patch('morgana_core.morgana_brain') as mock_morgana_brain:
        mock_morgana_brain.return_value = {"status": "success", "mocked": True}

        # Execute
        result = morgana_brain_v2(req)

        # Assert
        mock_morgana_brain.assert_called_once_with(req)
        assert result == {"status": "success", "mocked": True}
