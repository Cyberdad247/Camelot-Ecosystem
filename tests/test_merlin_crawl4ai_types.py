import importlib.util
import sys
from unittest.mock import MagicMock, patch

# The `01_KERNEL/merlin/Engines/crawl4ai` module has a known, pre-existing circular import dependency involving `async_configs`, `ExtractionStrategy`, `types`, and `LLMConfig` that causes `ImportError` in isolated test scripts but is an expected baseline.
# To work around this circular import dependency while testing, we can use `importlib` carefully.

def test_create_llm_config():
    base_path = "01_KERNEL/merlin/Engines/crawl4ai"
    pkg_name = "01_KERNEL.merlin.Engines.crawl4ai"

    mock_dotenv = MagicMock()
    mock_requests = MagicMock()
    mock_pkg = MagicMock()

    mock_async_configs = MagicMock()
    mock_LLMConfig = MagicMock()
    mock_LLMConfig.return_value = "mocked_config_instance"
    mock_async_configs.LLMConfig = mock_LLMConfig

    mock_proxy_strategy = MagicMock()

    with patch.dict("sys.modules", {
        "dotenv": mock_dotenv,
        "requests": mock_requests,
        pkg_name: mock_pkg,
        f"{pkg_name}.async_configs": mock_async_configs,
        f"{pkg_name}.proxy_strategy": mock_proxy_strategy
    }):
        # Load types
        types_spec = importlib.util.spec_from_file_location(
            f"{pkg_name}.types",
            f"{base_path}/types.py"
        )
        types_mod = importlib.util.module_from_spec(types_spec)
        sys.modules[f"{pkg_name}.types"] = types_mod

        types_mod.__package__ = pkg_name
        types_spec.loader.exec_module(types_mod)

        # Test the function
        config = types_mod.create_llm_config(provider="test_provider", api_token="test_token")

        # Verify the results
        assert config == "mocked_config_instance"
        mock_LLMConfig.assert_called_once_with(provider="test_provider", api_token="test_token")
