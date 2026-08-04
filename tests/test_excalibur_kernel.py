import os
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "01_KERNEL", "EXCALIBUR"))
sys.path.insert(0, os.path.join(ROOT, "01_KERNEL"))

with patch.dict(sys.modules, {"fusion": MagicMock(), "fusion.fusion_router": MagicMock()}):
    from EXCALIBUR.core.excalibur import app  # noqa: E402

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["identity"] == "Merlin_Omega"
    assert "mode" in data


def test_root_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["identity"] == "Merlin_Omega"
    assert "mode" in data
