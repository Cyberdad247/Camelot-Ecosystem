import sys
from pathlib import Path
from unittest.mock import MagicMock

# Allow imports from 01_KERNEL directly
sys.path.insert(0, str(Path("01_KERNEL").absolute()))

# Mocking modules that cause ImportError during import
sys.modules["haystack"] = MagicMock()
sys.modules["haystack.dataclasses"] = MagicMock()
# Try mock what fails in chronos.py
sys.modules["rag"] = MagicMock()
sys.modules["rag.lightrag_engine"] = MagicMock()
sys.modules["kernel"] = MagicMock()
sys.modules["kernel.rag"] = MagicMock()
sys.modules["kernel.rag.lightrag_engine"] = MagicMock()
sys.modules["lightrag"] = MagicMock()

import pytest
# Import file directly by modifying sys.path to point to rag dir
sys.path.insert(0, str(Path("01_KERNEL/merlin/rag").absolute()))
# And let's mock MerlinGenerator too directly since we don't need its real implementation to test evaluation
sys.modules["integrations"] = MagicMock()
sys.modules["integrations.merlin_haystack_generator"] = MagicMock()
sys.modules["integrations.merlin_haystack_generator"].MerlinGenerator = MagicMock()

from recursive_search import ReflectionEngine


@pytest.fixture
def engine():
    return ReflectionEngine()


def test_evaluate_coverage_valid_json(engine):
    engine.evaluator.run = MagicMock(return_value={
        "replies": ["""
```json
{
    "score": 4,
    "missing": "The specifics of feature X",
    "needs_recursion": true
}
```
        """]
    })

    documents = [{"content": "Doc 1"}, {"content": "Doc 2"}]
    result = engine.evaluate_coverage("Tell me about feature X", documents)

    assert result["score"] == 4
    assert result["missing"] == "The specifics of feature X"
    assert result["needs_recursion"] is True


def test_evaluate_coverage_valid_json_no_markdown(engine):
    engine.evaluator.run = MagicMock(return_value={
        "replies": ["""
{
    "score": 9,
    "missing": "None",
    "needs_recursion": false
}
        """]
    })

    documents = [{"content": "Doc 1"}, {"content": "Doc 2"}]
    result = engine.evaluate_coverage("What is Y?", documents)

    assert result["score"] == 9
    assert result["missing"] == "None"
    assert result["needs_recursion"] is False


def test_evaluate_coverage_fallback_heuristic(engine):
    engine.evaluator.run = MagicMock(return_value={
        "replies": ["I couldn't evaluate this, error formatting JSON..."]
    })

    documents = [{"content": "Doc 1"}]
    result = engine.evaluate_coverage("Tell me about feature X", documents)

    assert result["score"] == 5
    assert result["missing"] == "Low document count"
    assert result["needs_recursion"] is True

    documents_2 = [{"content": "Doc 1"}, {"content": "Doc 2"}]
    result_2 = engine.evaluate_coverage("Tell me about feature X", documents_2)

    assert result_2["score"] == 10
    assert result_2["missing"] == "None"
    assert result_2["needs_recursion"] is False

def test_evaluate_coverage_empty_docs(engine):
    result = engine.evaluate_coverage("Query", [])

    assert result["score"] == 0
    assert result["missing"] == "No documents found."
    assert result["needs_recursion"] is True
