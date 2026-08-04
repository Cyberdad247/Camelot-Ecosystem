import sys
import os
import unittest.mock
from fastapi.testclient import TestClient

# Mock missing dependencies
mock_fusion = unittest.mock.MagicMock()
mock_fusion_router = unittest.mock.MagicMock()
mock_fusion.fusion_router = mock_fusion_router

with unittest.mock.patch.dict(sys.modules, {'fusion': mock_fusion, 'fusion.fusion_router': mock_fusion_router}):
    kernel_path = os.path.abspath('01_KERNEL')
    if kernel_path not in sys.path:
        sys.path.insert(0, kernel_path)

    from EXCALIBUR.core.excalibur import app

client = TestClient(app)

def test_health_check_simulation_mode(monkeypatch):
    monkeypatch.delenv("MODE", raising=False)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ONLINE", "identity": "Merlin_Omega", "mode": "SIMULATION"}

def test_health_check_root(monkeypatch):
    monkeypatch.delenv("MODE", raising=False)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ONLINE", "identity": "Merlin_Omega", "mode": "SIMULATION"}

def test_health_check_custom_mode(monkeypatch):
    monkeypatch.setenv("MODE", "PRODUCTION")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ONLINE", "identity": "Merlin_Omega", "mode": "PRODUCTION"}
