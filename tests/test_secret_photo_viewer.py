# SPDX-License-Identifier: MIT

"""Backend unit tests for the Secret Photo Viewer staging API.

These tests exercise the ``/api/staged`` endpoints and the Gradio
``_stage_uploads`` helper without launching a browser.
"""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from gradio_photo_viewer import AppConfig, _stage_uploads, create_app


@pytest.fixture
def app_config(tmp_path: Path) -> AppConfig:
    """Return a test configuration with a temporary staging directory."""
    return AppConfig(
        host="127.0.0.1",
        port=7860,
        staging_dir=tmp_path / "staging",
        max_upload_size=10 * 1024 * 1024,
        api_key="test-api-key",
        password_hash=None,
    )


@pytest.fixture
def client(app_config: AppConfig) -> TestClient:
    """Return a FastAPI TestClient wired to a test app."""
    app = create_app(app_config)
    return TestClient(app)


def _png_bytes() -> bytes:
    """Return a small valid PNG image as bytes."""
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="PNG")
    return buf.getvalue()


def test_list_staged_empty(client: TestClient) -> None:
    resp = client.get("/api/staged", headers={"X-API-Key": "test-api-key"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_post_get_delete_cycle(client: TestClient) -> None:
    data = _png_bytes()
    resp = client.post(
        "/api/staged",
        files={"upload": ("test.png", io.BytesIO(data), "image/png")},
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 200
    payload = resp.json()
    filename = payload["filename"]
    assert payload["status"] == "staged"
    assert payload["width"] == 10
    assert payload["height"] == 10

    resp = client.get("/api/staged", headers={"X-API-Key": "test-api-key"})
    assert resp.status_code == 200
    assert filename in resp.json()

    resp = client.get(f"/api/staged/{filename}", headers={"X-API-Key": "test-api-key"})
    assert resp.status_code == 200

    resp = client.delete(f"/api/staged/{filename}", headers={"X-API-Key": "test-api-key"})
    assert resp.status_code == 200

    resp = client.get("/api/staged", headers={"X-API-Key": "test-api-key"})
    assert resp.json() == []


def test_unsupported_file_type(client: TestClient) -> None:
    resp = client.post(
        "/api/staged",
        files={"upload": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 400
    assert "Unsupported" in resp.json()["detail"]


def test_invalid_image_content(client: TestClient) -> None:
    resp = client.post(
        "/api/staged",
        files={"upload": ("fake.png", io.BytesIO(b"not an image"), "image/png")},
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 400
    assert "Invalid" in resp.json()["detail"]


def test_oversized_file(tmp_path: Path) -> None:
    config = AppConfig(
        host="127.0.0.1",
        port=7860,
        staging_dir=tmp_path / "staging",
        max_upload_size=10,
        api_key="test-api-key",
    )
    app = create_app(config)
    client = TestClient(app)
    resp = client.post(
        "/api/staged",
        files={"upload": ("big.png", io.BytesIO(_png_bytes()), "image/png")},
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 413
    assert "too large" in resp.json()["detail"].lower()


def test_missing_api_key_is_rejected(app_config: AppConfig) -> None:
    app_config = app_config.__dict__.copy()
    app_config["api_key"] = "different-key"
    app = create_app(AppConfig(**app_config))
    client = TestClient(app)
    resp = client.get("/api/staged", headers={"X-API-Key": "test-api-key"})
    assert resp.status_code == 401


def test_stage_uploads_handler(tmp_path: Path) -> None:
    """Exercise the Gradio ``_stage_uploads`` helper directly."""
    image_path = tmp_path / "photo.png"
    image_path.write_bytes(_png_bytes())
    config = AppConfig(
        host="127.0.0.1",
        port=7860,
        staging_dir=tmp_path / "staging",
        api_key="test-api-key",
    )
    req = MagicMock()
    req.headers = {"x-api-key": "test-api-key"}
    result = _stage_uploads(config, [str(image_path)], req)
    assert "Staged 1 photo(s)" in result
