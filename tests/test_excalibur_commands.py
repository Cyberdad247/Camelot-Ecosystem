import os
import sys
from unittest.mock import MagicMock, patch
import pytest

# Ensure 01_KERNEL can be resolved
sys.path.insert(0, os.path.abspath("01_KERNEL"))

@pytest.fixture(scope="module")
def app_client():
    # Use patch.dict to avoid polluting sys.modules globally.
    # We mock 'fusion' because the excalibur router imports it directly,
    # and we want this test to be isolated from the broader Camelot project's
    # potentially complex or missing dependencies.
    with patch.dict(sys.modules, {"fusion": MagicMock(), "fusion.fusion_router": MagicMock()}):
        from EXCALIBUR.core.excalibur import app
        from fastapi.testclient import TestClient
        yield TestClient(app)

def test_execute_command_system_health(app_client):
    response = app_client.post("/command?intent=check system health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["decision"]["action"] == "SYSTEM_HEALTH_CHECK"
    assert data["decision"]["priority"] == "LOW"
    assert data["decision"]["target"] == "Merlin_Omega"

def test_execute_command_research(app_client):
    response = app_client.post("/command?intent=search for something")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["decision"]["action"] == "DISPATCH_RESEARCH_AGENT"
    assert data["decision"]["priority"] == "MEDIUM"
    assert data["decision"]["target"] == "Morgana_Swarm"

def test_execute_command_kinetic(app_client):
    response = app_client.post("/command?intent=execute order 66")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["decision"]["action"] == "INITIATE_KINETIC_SEQUENCE"
    assert data["decision"]["priority"] == "HIGH"
    assert data["decision"]["target"] == "Sir_Lukas"

def test_execute_command_generic(app_client):
    response = app_client.post("/command?intent=hello there")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["decision"]["action"] == "GENERIC_PROCESS"
    assert data["decision"]["payload"] == "hello there"
    assert data["decision"]["target"] == "UKG_Vault"
