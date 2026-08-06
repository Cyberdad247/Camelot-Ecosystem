import sys
import os
import unittest.mock

sys.path.insert(0, os.path.abspath('01_KERNEL'))

mock_fusion = unittest.mock.MagicMock()
with unittest.mock.patch.dict(sys.modules, {'fusion': mock_fusion, 'fusion.fusion_router': mock_fusion}):
    from EXCALIBUR.core.excalibur import process_intent  # noqa: E402

def test_process_intent_system_health():
    result = process_intent("What is the status of the system?")
    assert result["action"] == "SYSTEM_HEALTH_CHECK"
    assert result["priority"] == "LOW"
    assert result["target"] == "Merlin_Omega"
    assert "timestamp" in result

def test_process_intent_research():
    result = process_intent("Can you search for the latest news?")
    assert result["action"] == "DISPATCH_RESEARCH_AGENT"
    assert result["priority"] == "MEDIUM"
    assert result["target"] == "Morgana_Swarm"
    assert "timestamp" in result

def test_process_intent_kinetic():
    result = process_intent("Please deploy the new version.")
    assert result["action"] == "INITIATE_KINETIC_SEQUENCE"
    assert result["priority"] == "HIGH"
    assert result["target"] == "Sir_Lukas"
    assert "timestamp" in result

def test_process_intent_generic():
    result = process_intent("Hello there!")
    assert result["action"] == "GENERIC_PROCESS"
    assert result["payload"] == "Hello there!"
    assert result["target"] == "UKG_Vault"
    assert "timestamp" in result
