# SPDX-License-Identifier: MIT

"""Unit tests for the Secret Photo Viewer FastAPI app.

Run with:
    python -m pytest tests/test_photo_viewer_api.py
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

import bcrypt
import pytest
from fastapi.testclient import TestClient
from PIL import Image as PILImage

import gradio_photo_viewer as spv


def _sized_image_bytes(size: tuple[int, int] = (400, 400)) -> bytes:
    img = PILImage.new("RGB", size, color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    staging_dir = tmp_path / "staged"
    staging_dir.mkdir()
    config = spv.AppConfig(
        host="127.0.0.1",
        port=0,
        staging_dir=staging_dir,
        max_upload_size=1024 * 1024,
        iframe_height="600px",
        log_level="INFO",
    )
    app = spv.create_app(config=config)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def small_limit_client(tmp_path: Path) -> TestClient:
    staging_dir = tmp_path / "staged"
    staging_dir.mkdir()
    config = spv.AppConfig(
        host="127.0.0.1",
        port=0,
        staging_dir=staging_dir,
        max_upload_size=1024,  # 1 KB cap to make the small test image exceed it.
        iframe_height="600px",
        log_level="INFO",
    )
    app = spv.create_app(config=config)
    with TestClient(app) as test_client:
        yield test_client


def _make_image_bytes() -> bytes:
    # Use a larger image to guarantee a compressed size above the 1 KB cap used
    # by the oversized-upload fixture.
    return _sized_image_bytes((400, 400))


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_metrics_endpoint(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "spv_upload_requests_total" in body
    assert "spv_staged_files_count" in body
    assert "spv_health_checks_total" in body


def test_metrics_record_upload(client: TestClient) -> None:
    response = client.post(
        "/api/staged",
        files={"upload": ("test.jpg", io.BytesIO(_make_image_bytes()), "image/jpeg")},
    )
    assert response.status_code == 200

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    body = metrics_response.text
    assert 'spv_upload_requests_total{status="success"}' in body


def test_viewer_html_served(client: TestClient) -> None:
    response = client.get("/secret-photo-viewer.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_upload_valid_image(client: TestClient) -> None:
    response = client.post(
        "/api/staged",
        files={"upload": ("test.jpg", io.BytesIO(_make_image_bytes()), "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "staged"
    assert data["filename"].endswith(".jpg")
    assert data["width"] == 400
    assert data["height"] == 400


def test_api_key_required(tmp_path: Path) -> None:
    staging_dir = tmp_path / "staged"
    staging_dir.mkdir()
    config = spv.AppConfig(
        host="127.0.0.1",
        port=0,
        staging_dir=staging_dir,
        api_key="secret-123",
        log_level="CRITICAL",
    )
    app = spv.create_app(config=config)
    with TestClient(app) as test_client:
        # Missing key
        assert test_client.get("/api/staged").status_code == 401
        # Wrong key
        assert test_client.get("/api/staged", headers={"X-API-Key": "wrong"}).status_code == 401
        # Correct key
        assert test_client.get("/api/staged", headers={"X-API-Key": "secret-123"}).status_code == 200


def test_api_key_applies_to_upload(tmp_path: Path) -> None:
    staging_dir = tmp_path / "staged"
    staging_dir.mkdir()
    config = spv.AppConfig(
        host="127.0.0.1",
        port=0,
        staging_dir=staging_dir,
        api_key="secret-123",
        log_level="CRITICAL",
    )
    app = spv.create_app(config=config)
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/staged",
            files={"upload": ("test.jpg", io.BytesIO(_make_image_bytes()), "image/jpeg")},
        )
        assert response.status_code == 401

        response = test_client.post(
            "/api/staged",
            files={"upload": ("test.jpg", io.BytesIO(_make_image_bytes()), "image/jpeg")},
            headers={"X-API-Key": "secret-123"},
        )
        assert response.status_code == 200


def test_upload_invalid_extension(client: TestClient) -> None:
    response = client.post(
        "/api/staged",
        files={"upload": ("malware.exe", io.BytesIO(b"not an image"), "application/octet-stream")},
    )
    assert response.status_code == 400


def test_upload_invalid_image_content(client: TestClient) -> None:
    response = client.post(
        "/api/staged",
        files={"upload": ("fake.jpg", io.BytesIO(b"not a real jpeg"), "image/jpeg")},
    )
    assert response.status_code == 400


def test_upload_oversized_image(small_limit_client: TestClient) -> None:
    # The small test image is a valid JPEG larger than the 1 KB cap.
    response = small_limit_client.post(
        "/api/staged",
        files={"upload": ("test.jpg", io.BytesIO(_make_image_bytes()), "image/jpeg")},
    )
    assert response.status_code == 413


def test_list_and_delete_staged(client: TestClient) -> None:
    upload_response = client.post(
        "/api/staged",
        files={"upload": ("test.jpg", io.BytesIO(_make_image_bytes()), "image/jpeg")},
    )
    assert upload_response.status_code == 200
    filename = upload_response.json()["filename"]

    list_response = client.get("/api/staged")
    assert list_response.status_code == 200
    assert filename in list_response.json()

    get_response = client.get(f"/api/staged/{filename}")
    assert get_response.status_code == 200

    delete_response = client.delete(f"/api/staged/{filename}")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"

    list_response = client.get("/api/staged")
    assert filename not in list_response.json()


def test_s3_storage_flow(tmp_path: Path) -> None:
    from moto import mock_aws

    with mock_aws():
        # Create the mocked bucket.
        import boto3

        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="spv-staging")

        config = spv.AppConfig(
            host="127.0.0.1",
            port=0,
            staging_dir=tmp_path / "staged",
            storage_backend="s3",
            s3_bucket="spv-staging",
            s3_access_key="minioadmin",
            s3_secret_key="minioadmin",
            log_level="CRITICAL",
        )
        app = spv.create_app(config=config)
        with TestClient(app) as test_client:
            response = test_client.post(
                "/api/staged",
                files={"upload": ("test.jpg", io.BytesIO(_make_image_bytes()), "image/jpeg")},
            )
            assert response.status_code == 200
            filename = response.json()["filename"]

            list_response = test_client.get("/api/staged")
            assert list_response.status_code == 200
            assert filename in list_response.json()

            get_response = test_client.get(f"/api/staged/{filename}")
            assert get_response.status_code == 200

            delete_response = test_client.delete(f"/api/staged/{filename}")
            assert delete_response.status_code == 200

            list_response = test_client.get("/api/staged")
            assert filename not in list_response.json()


# -----------------------------------------------------------------------------
# Password authentication tests
# -----------------------------------------------------------------------------

def _basic_auth_header(password: str, username: str = "user") -> str:
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


@pytest.fixture
def password_config(tmp_path: Path) -> spv.AppConfig:
    password = "my-secret-password"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
    staging_dir = tmp_path / "staged"
    staging_dir.mkdir()
    return spv.AppConfig(
        host="127.0.0.1",
        port=0,
        staging_dir=staging_dir,
        password_hash=password_hash,
        log_level="CRITICAL",
    )


def test_password_required_for_routes(password_config: spv.AppConfig) -> None:
    app = spv.create_app(config=password_config)
    with TestClient(app) as test_client:
        response = test_client.get("/")
        assert response.status_code == 401
        assert response.headers.get("www-authenticate") == 'Basic realm="Secret Photo Viewer"'

        response = test_client.get("/secret-photo-viewer.html")
        assert response.status_code == 401


def test_password_allows_access(password_config: spv.AppConfig) -> None:
    app = spv.create_app(config=password_config)
    with TestClient(app) as test_client:
        response = test_client.get("/", headers={"Authorization": _basic_auth_header("my-secret-password")})
        assert response.status_code == 200

        response = test_client.get("/secret-photo-viewer.html", headers={"Authorization": _basic_auth_header("my-secret-password")})
        assert response.status_code == 200


def test_password_wrong_password(password_config: spv.AppConfig) -> None:
    app = spv.create_app(config=password_config)
    with TestClient(app) as test_client:
        response = test_client.get("/", headers={"Authorization": _basic_auth_header("wrong-password")})
        assert response.status_code == 401


def test_password_health_exempt(password_config: spv.AppConfig) -> None:
    app = spv.create_app(config=password_config)
    with TestClient(app) as test_client:
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_password_metrics_exempt(password_config: spv.AppConfig) -> None:
    app = spv.create_app(config=password_config)
    with TestClient(app) as test_client:
        response = test_client.get("/metrics")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")


# -----------------------------------------------------------------------------
# Password hash generation tests
# -----------------------------------------------------------------------------

def test_generate_password_hash_produces_valid_bcrypt() -> None:
    hash_value = spv.generate_password_hash("super-secret")
    assert hash_value.startswith("$2b$")
    assert bcrypt.checkpw(b"super-secret", hash_value.encode("ascii"))


def test_generate_password_hash_rejects_empty() -> None:
    with pytest.raises(ValueError, match="Password cannot be empty"):
        spv.generate_password_hash("")


# -----------------------------------------------------------------------------
# Gradio upload auth tests
# -----------------------------------------------------------------------------

class _FakeRequest:
    def __init__(self, headers: dict[str, str]):
        self.headers = headers


def test_check_request_auth_no_auth_configured() -> None:
    config = spv.AppConfig(api_key=None, password_hash=None)
    req = _FakeRequest({})
    assert spv._check_request_auth(config, req) is True


def test_check_request_auth_api_key() -> None:
    config = spv.AppConfig(api_key="secret-key", password_hash=None)
    assert spv._check_request_auth(config, _FakeRequest({"x-api-key": "wrong"})) is False
    assert spv._check_request_auth(config, _FakeRequest({"x-api-key": "secret-key"})) is True


def test_check_request_auth_basic_password() -> None:
    password = "my-secret"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
    config = spv.AppConfig(api_key=None, password_hash=password_hash)
    auth_header = base64.b64encode(f"user:{password}".encode("utf-8")).decode("ascii")
    assert spv._check_request_auth(config, _FakeRequest({})) is False
    assert spv._check_request_auth(config, _FakeRequest({"authorization": f"Basic {auth_header}"})) is True


def test_check_request_auth_prefers_api_key_over_password() -> None:
    password = "my-secret"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
    config = spv.AppConfig(api_key="secret-key", password_hash=password_hash)
    assert spv._check_request_auth(config, _FakeRequest({"x-api-key": "secret-key"})) is True


def test_password_and_api_key_bypass(tmp_path: Path) -> None:
    password = "my-secret-password"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
    staging_dir = tmp_path / "staged"
    staging_dir.mkdir()
    config = spv.AppConfig(
        host="127.0.0.1",
        port=0,
        staging_dir=staging_dir,
        api_key="secret-api-key",
        password_hash=password_hash,
        log_level="CRITICAL",
    )
    app = spv.create_app(config=config)
    with TestClient(app) as test_client:
        # Without either auth, /api/staged is blocked by the app password.
        response = test_client.get("/api/staged")
        assert response.status_code == 401

        # API key alone should bypass the app password and satisfy the endpoint.
        response = test_client.get("/api/staged", headers={"X-API-Key": "secret-api-key"})
        assert response.status_code == 200

        # Basic auth with correct password should also work.
        response = test_client.get("/api/staged", headers={"Authorization": _basic_auth_header("my-secret-password")})
        assert response.status_code == 200
