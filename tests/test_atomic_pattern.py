import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "01_KERNEL" / "agora" / "swarms" / "atomic_pattern.py"


def load_atomic_pattern():
    """Load the atomic_pattern module dynamically."""

    # Mocking atomic_agents to avoid resolving BaseAgent/BaseAgentConfig which moved in v1.1.11
    sys.modules["atomic_agents.lib.base.base_agent"] = MagicMock()
    sys.modules["atomic_agents.lib.base.base_io_schema"] = MagicMock()

    spec = importlib.util.spec_from_file_location("atomic_pattern", TARGET_FILE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["atomic_pattern"] = module

    spec.loader.exec_module(module)
    return module


@pytest.fixture
def atomic_pattern():
    return load_atomic_pattern()


def test_research_node_happy_path(atomic_pattern):
    """Test the research node with valid input and mock output."""
    initial_state = {"query": "test query", "research_findings": [], "confidence": 0.0}

    with (
        patch("atomic_pattern.ResearchAgent") as MockAgent,
        patch("atomic_pattern.ResearchAgentConfig"),
        patch("atomic_pattern.ResearchInput"),
    ):
        mock_instance = MockAgent.return_value

        mock_result = MagicMock()
        mock_result.findings = ["mocked finding 1", "mocked finding 2"]
        mock_result.confidence = 0.95
        mock_instance.run.return_value = mock_result

        result = atomic_pattern.research_node(initial_state)

        assert result["query"] == "test query"
        assert result["research_findings"] == ["mocked finding 1", "mocked finding 2"]
        assert result["confidence"] == 0.95

        MockAgent.assert_called_once()
        mock_instance.run.assert_called_once()


def test_build_research_workflow(atomic_pattern):
    """Test the graph building workflow."""
    with patch("atomic_pattern.StateGraph") as MockStateGraph:
        mock_graph = MockStateGraph.return_value

        workflow = atomic_pattern.build_research_workflow()

        MockStateGraph.assert_called_once_with(atomic_pattern.CamelotState)
        mock_graph.add_node.assert_called_once_with("research", atomic_pattern.research_node)
        mock_graph.set_entry_point.assert_called_once_with("research")
        mock_graph.add_edge.assert_called_once()
        mock_graph.compile.assert_called_once()

        assert workflow == mock_graph.compile.return_value


def test_research_node_agent_error(atomic_pattern):
    """Test the research node when the atomic agent raises an exception."""
    initial_state = {"query": "error query", "research_findings": [], "confidence": 0.0}

    with (
        patch("atomic_pattern.ResearchAgent") as MockAgent,
        patch("atomic_pattern.ResearchAgentConfig"),
        patch("atomic_pattern.ResearchInput"),
    ):
        mock_instance = MockAgent.return_value
        mock_instance.run.side_effect = RuntimeError("Agent failed")

        with pytest.raises(RuntimeError, match="Agent failed"):
            atomic_pattern.research_node(initial_state)

        MockAgent.assert_called_once()
        mock_instance.run.assert_called_once()
