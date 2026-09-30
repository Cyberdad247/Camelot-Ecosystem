from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def test_health_check_uninitialized_pipeline(monkeypatch):
    monkeypatch.setattr(main, "pipeline", None)

    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "Pipeline uninitialized"}


def test_health_check_initialized_pipeline(monkeypatch):
    mock_pipeline = MagicMock()
    mock_pipeline.knights = ["Knight1", "Knight2"]
    monkeypatch.setattr(main, "pipeline", mock_pipeline)

    mock_webrtc = MagicMock()
    mock_webrtc.is_initialized = True
    monkeypatch.setattr(main, "native_webrtc_engine", mock_webrtc)

    monkeypatch.setattr(main, "redis_client", True)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["active_knights"] == ["Knight1", "Knight2"]
    assert data["zero_copy_shm_active"] is True
    assert data["native_cxx_webrtc_active"] is True
    assert data["redis_ha_nonce_active"] is True
    assert data["prometheus_metrics_active"] is True
    assert "timestamp" in data
