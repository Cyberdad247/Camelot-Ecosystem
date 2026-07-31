"""Tests for excalibur core.

Run with:
    PYTHONPATH=. uv run pytest tests/test_excalibur.py -v
"""

from __future__ import annotations

import os
import sys
import unittest.mock

# Mock dependencies before importing 01_KERNEL modules
# using unittest.mock.patch.dict as required by instructions
unittest.mock.patch.dict(
    sys.modules,
    {
        "uvicorn": unittest.mock.MagicMock(),
        "fastapi": unittest.mock.MagicMock(),
        "fusion": unittest.mock.MagicMock(),
        "fusion.fusion_router": unittest.mock.MagicMock(),
    },
).start()

# Make 01_KERNEL importable
sys.path.insert(0, os.path.abspath("01_KERNEL"))

from EXCALIBUR.core.excalibur import process_intent  # noqa: E402


def test_process_intent_system_health():
    """Test routing for system health/status intents."""
    result = process_intent("What is the system status?")
    assert result["action"] == "SYSTEM_HEALTH_CHECK"
    assert result["priority"] == "LOW"
    assert result["target"] == "Merlin_Omega"
    assert "timestamp" in result

    result2 = process_intent("report health")
    assert result2["action"] == "SYSTEM_HEALTH_CHECK"


def test_process_intent_research():
    """Test routing for research/information intents."""
    result = process_intent("Research the latest AI models")
    assert result["action"] == "DISPATCH_RESEARCH_AGENT"
    assert result["priority"] == "MEDIUM"
    assert result["target"] == "Morgana_Swarm"
    assert "timestamp" in result

    result2 = process_intent("who is Alan Turing?")
    assert result2["action"] == "DISPATCH_RESEARCH_AGENT"


def test_process_intent_kinetic_action():
    """Test routing for kinetic/action intents."""
    result = process_intent("deploy the application to production")
    assert result["action"] == "INITIATE_KINETIC_SEQUENCE"
    assert result["priority"] == "HIGH"
    assert result["target"] == "Sir_Lukas"
    assert "timestamp" in result

    result2 = process_intent("execute command: ls -la")
    assert result2["action"] == "INITIATE_KINETIC_SEQUENCE"


def test_process_intent_generic():
    """Test routing for generic/unrecognized intents."""
    result = process_intent("hello world")
    assert result["action"] == "GENERIC_PROCESS"
    assert result["payload"] == "hello world"
    assert result["target"] == "UKG_Vault"
    assert "timestamp" in result
