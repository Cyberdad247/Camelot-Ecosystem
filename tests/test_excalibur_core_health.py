import os
import sys
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import APIRouter
import pytest

# Adjust sys.path so we can import the module correctly
kernel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '01_KERNEL'))
if kernel_path not in sys.path:
    sys.path.insert(0, kernel_path)

# Mock fusion module to prevent ModuleNotFoundError
mock_router = APIRouter()
sys.modules['fusion'] = type('MockFusion', (), {})
sys.modules['fusion.fusion_router'] = type('MockFusionRouter', (), {'router': mock_router})

from EXCALIBUR.core.excalibur import app

client = TestClient(app)

def test_health_check_simulation_mode():
    with patch.dict(os.environ, {"MODE": "SIMULATION"}):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ONLINE",
            "identity": "Merlin_Omega",
            "mode": "SIMULATION"
        }

def test_health_check_root_endpoint():
    with patch.dict(os.environ, {"MODE": "SIMULATION"}):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ONLINE",
            "identity": "Merlin_Omega",
            "mode": "SIMULATION"
        }

def test_health_check_production_mode():
    with patch.dict(os.environ, {"MODE": "PRODUCTION"}):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ONLINE",
            "identity": "Merlin_Omega",
            "mode": "PRODUCTION"
        }
