"""Gradio wrapper for the Secret Photo Viewer.

Run with:
    python gradio_photo_viewer.py

This launches a Gradio app that embeds ``secret-photo-viewer.html`` in an
iframe so it can be viewed from a headless environment through any modern
browser. The HTML file is served from the project root via a dedicated
FastAPI route, so the original JavaScript, IndexedDB, and Tailwind features
keep working.

Uploaded photos are staged in a local directory and then imported into the
iframe's IndexedDB vault when the vault is unlocked.

Production notes
----------------
Configuration is read from environment variables. The server binds to all
interfaces by default, exposes a ``/health`` endpoint, and ships with
security headers, rate limiting, and Pillow-based image validation.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import io

import bcrypt
import logging
import mimetypes
import os
import re
import shutil
import secrets
import sys
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

import asyncio
from contextlib import asynccontextmanager

import gradio as gr
import httpx
import uvicorn
from fastapi import Body, Depends, FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel
from PIL import Image
from prometheus_client import Counter, Gauge, Histogram, generate_latest


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("secret_photo_viewer")


# ---------------------------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------------------------
UPLOAD_REQUESTS = Counter(
    "spv_upload_requests_total",
    "Total number of upload requests to /api/staged",
    ["status"],
)
UPLOAD_BYTES = Counter(
    "spv_upload_bytes_total",
    "Total number of image bytes successfully staged",
)
UPLOAD_DURATION = Histogram(
    "spv_upload_duration_seconds",
    "Time spent processing upload requests",
)
STAGED_FILES = Gauge(
    "spv_staged_files_count",
    "Current number of files in the staging directory",
)
STAGED_BYTES_GAUGE = Gauge(
    "spv_staged_files_bytes",
    "Total size in bytes of files in the staging directory",
)
HEALTH_CHECKS = Counter(
    "spv_health_checks_total",
    "Total number of requests to /health",
)
CLEANUP_REMOVED = Counter(
    "spv_cleanup_removed_total",
    "Total number of staged files removed by cleanup",
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AppConfig:
    host: str = "0.0.0.0"
    port: int = 7860
    staging_dir: Path = field(default_factory=lambda: Path("staged_uploads").resolve())
    max_upload_size: int = 10 * 1024 * 1024
    iframe_height: str = "700px"
    log_level: str = "INFO"
    # Files older than this are considered stale and removed on startup.
    staging_max_age_seconds: int = 3600
    # Rate limiting: max requests per window for /api/staged mutations.
    rate_limit_requests: int = 20
    rate_limit_window_seconds: int = 60
    # Optional API key to protect /api/staged endpoints.
    api_key: str | None = None
    # Optional app-level password hash (bcrypt). When set, all endpoints except
    # /health require HTTP Basic Auth. /api/staged endpoints can still use
    # X-API-Key as an bypass when both password and API key are configured.
    password_hash: str | None = None
    # Storage backend: "local" or "s3".
    storage_backend: str = "local"
    # Redis URL for distributed rate limiting. When omitted, falls back to in-memory.
    redis_url: str | None = None
    # S3/MinIO settings (used when storage_backend="s3").
    s3_endpoint: str | None = None
    s3_bucket: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    # Google Sign-In / Google Photos integration (optional).
    google_client_id: str | None = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            host=os.getenv("SPV_HOST", "0.0.0.0"),
            port=int(os.getenv("SPV_PORT", "7860")),
            staging_dir=Path(os.getenv("SPV_STAGING_DIR", "staged_uploads")).resolve(),
            max_upload_size=int(os.getenv("SPV_MAX_UPLOAD_SIZE", str(10 * 1024 * 1024))),
            iframe_height=os.getenv("SPV_IFRAME_HEIGHT", "700px"),
            log_level=os.getenv("SPV_LOG_LEVEL", "INFO"),
            staging_max_age_seconds=int(os.getenv("SPV_STAGING_MAX_AGE_SECONDS", "3600")),
            rate_limit_requests=int(os.getenv("SPV_RATE_LIMIT_REQUESTS", "20")),
            rate_limit_window_seconds=int(os.getenv("SPV_RATE_LIMIT_WINDOW_SECONDS", "60")),
            api_key=os.getenv("SPV_API_KEY"),
            password_hash=os.getenv("SPV_PASSWORD_HASH"),
            storage_backend=os.getenv("SPV_STORAGE_BACKEND", "local").lower(),
            redis_url=os.getenv("SPV_REDIS_URL"),
            s3_endpoint=os.getenv("SPV_S3_ENDPOINT"),
            s3_bucket=os.getenv("SPV_S3_BUCKET"),
            s3_access_key=os.getenv("SPV_S3_ACCESS_KEY"),
            s3_secret_key=os.getenv("SPV_S3_SECRET_KEY"),
            google_client_id=os.getenv("SPV_GOOGLE_CLIENT_ID"),
        )


# Common image MIME types / extensions that the vault accepts.
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}

APP_ROOT = Path(__file__).parent.resolve()
HTML_FILE = APP_ROOT / "secret-photo-viewer.html"
VIEWER_PATH = "/secret-photo-viewer.html"


# ---------------------------------------------------------------------------
# Storage backends
# ---------------------------------------------------------------------------
class StorageBackend(Protocol):
    """Abstract protocol for staging photo storage."""

    def save(self, filename: str, content: bytes) -> None:
        ...

    def list(self) -> list[str]:
        ...

    def get(self, filename: str) -> Response:
        ...

    def delete(self, filename: str) -> None:
        ...

    def count(self) -> int:
        """Return the current number of staged files."""
        ...

    def total_bytes(self) -> int:
        """Return the total size in bytes of staged files."""
        ...


class LocalStorage:
    """Local filesystem staging storage (single-node or shared volume)."""

    def __init__(self, staging_dir: Path):
        self.staging_dir = staging_dir
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> None:
        dest = self.staging_dir / filename
        with dest.open("wb") as f:
            f.write(content)

    def list(self) -> list[str]:
        return [f.name for f in self.staging_dir.iterdir() if f.is_file()]

    def get(self, filename: str) -> Response:
        file_path = (self.staging_dir / Path(filename).name).resolve()
        if not str(file_path).startswith(str(self.staging_dir)) or not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(str(file_path))

    def delete(self, filename: str) -> None:
        file_path = (self.staging_dir / Path(filename).name).resolve()
        if str(file_path).startswith(str(self.staging_dir)) and file_path.exists():
            file_path.unlink()

    def count(self) -> int:
        if not self.staging_dir.exists():
            return 0
        return sum(1 for f in self.staging_dir.iterdir() if f.is_file())

    def total_bytes(self) -> int:
        if not self.staging_dir.exists():
            return 0
        total = 0
        for path in self.staging_dir.iterdir():
            if not path.is_file():
                continue
            try:
                total += path.stat().st_size
            except OSError:
                continue
        return total


class S3Storage:
    """S3/MinIO-backed staging storage for multi-replica deployments."""

    def __init__(self, config: AppConfig):
        import boto3
        from botocore.config import Config as BotocoreConfig

        s3_config = BotocoreConfig(
            retries={"max_attempts": 3, "mode": "standard"},
        )
        self.s3 = boto3.client(
            "s3",
            endpoint_url=config.s3_endpoint,
            aws_access_key_id=config.s3_access_key,
            aws_secret_access_key=config.s3_secret_key,
            config=s3_config,
        )
        self.bucket = config.s3_bucket

    def save(self, filename: str, content: bytes) -> None:
        self.s3.put_object(Bucket=self.bucket, Key=filename, Body=content)

    def list(self) -> list[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix="")
        return [obj["Key"] for obj in response.get("Contents", [])]

    def get(self, filename: str) -> Response:
        from botocore.exceptions import ClientError

        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=filename)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown") if hasattr(exc, "response") else "Unknown"
            if code == "NoSuchKey":
                raise HTTPException(status_code=404, detail="Not found") from exc
            raise HTTPException(status_code=500, detail="Failed to fetch staged file") from exc
        return StreamingResponse(obj["Body"], media_type="application/octet-stream")

    def delete(self, filename: str) -> None:
        self.s3.delete_object(Bucket=self.bucket, Key=filename)


def _create_storage(config: AppConfig) -> StorageBackend:
    if config.storage_backend == "s3":
        return S3Storage(config)
    return LocalStorage(config.staging_dir)


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
class RateLimiter(Protocol):
    """Protocol for sliding-window rate limiters."""

    def is_allowed(self, key: str) -> bool:
        ...


class InMemoryRateLimiter:
    """Simple in-process sliding-window rate limiter.

    Suitable for single-node deployments or deployments behind a sticky load
    balancer. For multi-replica deployments, use :class:`RedisRateLimiter`.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window = self._windows[key]
        cutoff = now - self.window_seconds
        while window and window[0] <= cutoff:
            window.popleft()
        if len(window) >= self.max_requests:
            return False
        window.append(now)
        return True


class RedisRateLimiter:
    """Redis-backed sliding-window rate limiter for multi-replica deployments."""

    def __init__(self, redis_url: str, max_requests: int, window_seconds: int):
        import redis

        self.r = redis.from_url(redis_url)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, key: str) -> bool:
        import redis

        now = time.time()
        cutoff = now - self.window_seconds
        try:
            pipe = self.r.pipeline()
            pipe.zremrangebyscore(key, 0, cutoff)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, self.window_seconds)
            _, _, count, _ = pipe.execute()
        except redis.RedisError as exc:
            logger.warning("Redis rate limiter failed for key %s: %s", key, exc)
            # Fail open on Redis errors so a transient Redis outage doesn't
            # block all uploads.
            return True
        return count <= self.max_requests


def _create_rate_limiter(config: AppConfig) -> RateLimiter:
    if config.redis_url:
        return RedisRateLimiter(config.redis_url, config.rate_limit_requests, config.rate_limit_window_seconds)
    return InMemoryRateLimiter(config.rate_limit_requests, config.rate_limit_window_seconds)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _build_iframe_html(src: str, height: str) -> str:
    """Return an iframe that fills the Gradio component."""
    normalized_height = height.strip()
    if normalized_height and not re.search(
        r"\d+(?:\.\d+)?\s*(?:px|em|rem|vh|vw|vmin|vmax|%|ex|ch|cm|mm|in|pt|pc|lh|rlh)$",
        normalized_height,
        re.IGNORECASE,
    ):
        normalized_height = f"{normalized_height}px"
    return (
        f"""<iframe src=\"{src}\" """
        f"""style=\"width:100%; height:{normalized_height}; border:none; border-radius:12px;\" """
        """allow=\"clipboard-read; clipboard-write\" title=\"Secret Photo Viewer\">"""
        "</iframe>"
    )


def _is_image_filename(name: str) -> bool:
    ext = Path(name).suffix.lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def _validate_image_bytes(content: bytes) -> tuple[str, int, int] | None:
    """Validate that *content* is a real image.

    Returns a tuple of (format, width, height) on success, or None if the bytes
    do not decode as a supported image. This uses Pillow and defends against
    polyglot/malicious files that simply carry an image extension.
    """
    try:
        with Image.open(io.BytesIO(content)) as img:
            img.verify()
            fmt = img.format.lower() if img.format else None
            if fmt not in {"jpeg", "png", "gif", "webp", "bmp", "svg"}:
                return None
            # Re-open after verify to read dimensions.
            with Image.open(io.BytesIO(content)) as img2:
                width, height = img2.size
                return (fmt, width, height)
    except Exception as exc:
        logger.debug("Image validation failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------
def _verify_basic_auth_header(auth_header: str | None, password_hash: str | None) -> bool:
    """Verify an HTTP Basic Auth password against a bcrypt hash.

    The username portion of the credentials is ignored. Returns True when
    *password_hash* is set and the provided password matches.
    """
    if not password_hash or not auth_header or not auth_header.startswith("Basic "):
        return False
    try:
        encoded = auth_header[6:]
        decoded = base64.b64decode(encoded).decode("utf-8")
        _, password = decoded.split(":", 1)
        return bool(
            bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
        )
    except (ValueError, UnicodeDecodeError, bcrypt.BcryptError):
        return False


def _check_request_auth(config: AppConfig, req: gr.Request) -> bool:
    """Verify that a Gradio request carries valid credentials.

    Returns True when no password or API key is configured, or when the
    request presents a valid ``X-API-Key`` header or HTTP Basic Auth password.
    """
    if not (config.password_hash or config.api_key):
        return True
    if config.api_key:
        api_key = req.headers.get("x-api-key", "")
        if secrets.compare_digest(api_key, config.api_key):
            return True
    if config.password_hash:
        auth_header = req.headers.get("authorization", "")
        if _verify_basic_auth_header(auth_header, config.password_hash):
            return True
    return False


def generate_password_hash(password: str | None = None) -> str:
    """Generate a bcrypt hash of *password*.

    If *password* is not provided, the user is prompted interactively twice
    for confirmation. The generated hash can be used as ``SPV_PASSWORD_HASH``.

    Raises:
        ValueError: If the password is empty or the interactive confirmation
            does not match.
    """
    if password is None:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            raise ValueError("Passwords do not match")
    if not password:
        raise ValueError("Password cannot be empty")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


# ---------------------------------------------------------------------------
# Staging helpers
# ---------------------------------------------------------------------------
def _clean_old_staged_files(storage: StorageBackend, max_age_seconds: int) -> int:
    """Remove local staged files older than *max_age_seconds*.

    S3/MinIO cleanup is delegated to bucket lifecycle policies, so this only
    operates on the local filesystem backend.

    Returns the number of files removed.
    """
    if not isinstance(storage, LocalStorage):
        return 0
    if not storage.staging_dir.exists():
        return 0
    cutoff = time.time() - max_age_seconds
    removed = 0
    for path in storage.staging_dir.iterdir():
        if path.is_file() and path.stat().st_mtime < cutoff:
            try:
                path.unlink()
                removed += 1
            except OSError as exc:
                logger.warning("Failed to remove stale staged file %s: %s", path, exc)
    if removed:
        CLEANUP_REMOVED.inc(removed)
    return removed


# ---------------------------------------------------------------------------
# FastAPI endpoints
# ---------------------------------------------------------------------------
def _verify_api_key(request: Request) -> None:
    """Dependency that enforces the optional API key on /api/staged endpoints.

    The key is read from the ``X-API-Key`` header and compared using a
    constant-time comparison. When no API key is configured, this dependency
    is a no-op, preserving backward compatibility.

    When an app-level password is also configured, the request may
    alternatively authenticate via HTTP Basic Auth.
    """
    config: AppConfig = request.app.state.config
    # App-level password auth already handled at the middleware level, but
    # re-check here so Basic Auth works for /api/staged too.
    if config.password_hash and _verify_basic_auth_header(
        request.headers.get("authorization"), config.password_hash
    ):
        return
    if config.api_key is None:
        return
    header_key = request.headers.get("X-API-Key")
    if header_key is None or not secrets.compare_digest(header_key, config.api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _list_staged(request: Request, _auth: None = Depends(_verify_api_key)) -> JSONResponse:
    storage: StorageBackend = request.app.state.storage
    return JSONResponse(storage.list())


def _get_staged(filename: str, request: Request, _auth: None = Depends(_verify_api_key)) -> Response:
    storage: StorageBackend = request.app.state.storage
    return storage.get(filename)


def _delete_staged(filename: str, request: Request, _auth: None = Depends(_verify_api_key)) -> JSONResponse:
    storage: StorageBackend = request.app.state.storage
    storage.delete(filename)
    return JSONResponse({"status": "deleted"})


def _rate_limit_dependency(request: Request) -> None:
    """Dependency that enforces the per-IP sliding-window rate limit."""
    limiter: RateLimiter = request.app.state.limiter
    client = request.client
    key = f"{client.host}:{request.url.path}" if client else "unknown"
    if not limiter.is_allowed(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


async def _post_staged(
    request: Request,
    upload: UploadFile = File(...),
    _rate_limit: None = Depends(_rate_limit_dependency),
    _auth: None = Depends(_verify_api_key),
) -> JSONResponse:
    with UPLOAD_DURATION.time():
        config: AppConfig = request.app.state.config  # type: ignore[attr-defined]
        storage: StorageBackend = request.app.state.storage

        filename = upload.filename or "upload"
        if not _is_image_filename(filename):
            UPLOAD_REQUESTS.labels(status="invalid_type").inc()
            raise HTTPException(status_code=400, detail="Unsupported file type")

        try:
            content = upload.file.read(config.max_upload_size + 1)
            if len(content) > config.max_upload_size:
                UPLOAD_REQUESTS.labels(status="oversized").inc()
                raise HTTPException(status_code=413, detail="File too large")

            image_info = _validate_image_bytes(content)
            if image_info is None:
                UPLOAD_REQUESTS.labels(status="invalid_content").inc()
                raise HTTPException(status_code=400, detail="Invalid or unsupported image content")

            ext = Path(filename).suffix.lower() or f".{image_info[0]}"
            safe_name = f"{uuid.uuid4().hex}{ext.lower()}"
            storage.save(safe_name, content)
            UPLOAD_REQUESTS.labels(status="success").inc()
            UPLOAD_BYTES.inc(len(content))
            logger.info("Staged upload: %s (%dx%d)", safe_name, image_info[1], image_info[2])
            return JSONResponse({"filename": safe_name, "status": "staged", "width": image_info[1], "height": image_info[2]})
        except HTTPException:
            raise
        except Exception as exc:
            UPLOAD_REQUESTS.labels(status="error").inc()
            logger.exception("Failed to stage upload: %s", exc)
            raise HTTPException(status_code=500, detail="Failed to stage upload") from exc


def _serve_viewer() -> FileResponse:
    return FileResponse(str(HTML_FILE), media_type="text/html")


def _health(request: Request) -> JSONResponse:
    HEALTH_CHECKS.inc()
    config: AppConfig = request.app.state.config
    storage_backend = "s3" if isinstance(request.app.state.storage, S3Storage) else "local"
    return JSONResponse(
        {
            "status": "ok",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "storage_backend": storage_backend,
        }
    )


def _metrics() -> PlainTextResponse:
    return PlainTextResponse(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# ---------------------------------------------------------------------------
# Google Sign-In / Google Photos integration
# ---------------------------------------------------------------------------
class _GoogleVerifyRequest(BaseModel):
    id_token: str


class _GooglePhotosRequest(BaseModel):
    access_token: str
    page_token: str | None = None


class _GoogleStageRequest(BaseModel):
    access_token: str
    base_url: str


def _verify_google_id_token(token: str, client_id: str) -> dict:
    """Verify a Google ID token and return its decoded claims."""
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    id_info = google_id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
    # verify_oauth2_token already checks issuer/audience; this is a defensive
    # extra guard in case the underlying library behavior ever changes.
    if id_info.get("aud") != client_id:
        raise ValueError("Token audience does not match configured client ID")
    return id_info


def _google_available(config: AppConfig) -> bool:
    """Return True when Google Sign-In is configured and the SDK is installed."""
    if not config.google_client_id:
        return False
    try:
        from google.oauth2 import id_token  # noqa: F401
        from google.auth.transport import requests  # noqa: F401
        return True
    except ImportError:
        return False


async def _google_config(request: Request) -> JSONResponse:
    config: AppConfig = request.app.state.config
    return JSONResponse({"client_id": config.google_client_id})


async def _google_verify(
    request: Request,
    body: _GoogleVerifyRequest,
    _auth: None = Depends(_verify_api_key),
) -> JSONResponse:
    config: AppConfig = request.app.state.config
    if not _google_available(config):
        raise HTTPException(status_code=503, detail="Google Sign-In is not configured")
    try:
        id_info = await asyncio.to_thread(_verify_google_id_token, body.id_token, config.google_client_id)
        return JSONResponse(
            {
                "sub": id_info.get("sub"),
                "email": id_info.get("email"),
                "name": id_info.get("name"),
                "picture": id_info.get("picture"),
            }
        )
    except ValueError as exc:
        logger.warning("Google ID token verification failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid Google ID token") from exc
    except Exception as exc:
        logger.warning("Google ID token verification failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid Google ID token") from exc


async def _google_photos(
    request: Request,
    body: _GooglePhotosRequest,
    _auth: None = Depends(_verify_api_key),
) -> JSONResponse:
    config: AppConfig = request.app.state.config
    if not _google_available(config):
        raise HTTPException(status_code=503, detail="Google Sign-In is not configured")
    headers = {"Authorization": f"Bearer {body.access_token}"}
    params: dict[str, str] = {"pageSize": "100"}
    if body.page_token:
        params["pageToken"] = body.page_token
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://photoslibrary.googleapis.com/v1/mediaItems",
            headers=headers,
            params=params,
        )
    if response.status_code != 200:
        detail = response.text or "Failed to fetch Google Photos"
        raise HTTPException(status_code=response.status_code, detail=detail)
    return JSONResponse(response.json())


async def _google_stage(
    media_item_id: str,
    request: Request,
    body: _GoogleStageRequest,
    _auth: None = Depends(_verify_api_key),
) -> JSONResponse:
    config: AppConfig = request.app.state.config
    if not _google_available(config):
        raise HTTPException(status_code=503, detail="Google Sign-In is not configured")
    storage: StorageBackend = request.app.state.storage
    # Append a reasonable resolution modifier if none is present.
    download_url = body.base_url
    if "=" not in download_url:
        download_url = f"{download_url}=w2048-h2048"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            download_url,
            headers={"Authorization": f"Bearer {body.access_token}"},
            follow_redirects=True,
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch Google Photos item")
    content = response.content
    image_info = _validate_image_bytes(content)
    if image_info is None:
        raise HTTPException(status_code=400, detail="Google Photos item is not a supported image")
    ext = f".{image_info[0]}"
    safe_name = f"{uuid.uuid4().hex}{ext.lower()}"
    storage.save(safe_name, content)
    return JSONResponse({"filename": safe_name, "status": "staged"})


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------
class BasicAuthMiddleware:
    """Enforce HTTP Basic Auth when an app password is configured.

    The password is stored as a bcrypt hash in ``config.password_hash``.
    If no password is configured, the middleware is a no-op.

    ``/health`` and ``/metrics`` are exempt so health probes and Prometheus
    scrapes do not need credentials. Requests that present a valid
    ``X-API-Key`` header bypass Basic Auth, allowing headless scripts to keep
    using the API key for ``/api/staged``.
    """

    def __init__(self, app: Any, config: AppConfig):
        self.app = app
        self.config = config

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # No password configured; no authentication required.
        if not self.config.password_hash:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        # /health and /metrics remain unauthenticated so health probes and
        # Prometheus scrapes work without credentials.
        if path in ("/health", "/metrics"):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))

        # API key bypass for headless/script access to /api/staged.
        if self.config.api_key:
            api_key = headers.get(b"x-api-key", b"").decode("utf-8")
            if secrets.compare_digest(api_key, self.config.api_key):
                await self.app(scope, receive, send)
                return

        # HTTP Basic Auth verification.
        auth_header = headers.get(b"authorization", b"").decode("utf-8")
        if _verify_basic_auth_header(auth_header, self.config.password_hash):
            await self.app(scope, receive, send)
            return

        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"www-authenticate", b'Basic realm="Secret Photo Viewer"'),
                    (b"content-type", b"text/plain"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": b"Unauthorized", "more_body": False})


class SecurityHeadersMiddleware:
    """Attach a restrictive but functional set of security headers."""

    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def _send_with_headers(message: Any) -> None:
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                extra = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"SAMEORIGIN"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                    (
                        b"content-security-policy",
                        b"default-src 'self'; "
                        b"script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://accounts.google.com/gsi/client https://accounts.google.com; "
                        b"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://accounts.google.com; "
                        b"font-src 'self' https://fonts.gstatic.com; "
                        b"img-src 'self' blob: data: https://*.googleusercontent.com https://*.googleapis.com; "
                        b"connect-src 'self' https://photoslibrary.googleapis.com https://www.googleapis.com https://oauth2.googleapis.com https://accounts.google.com; "
                        b"frame-src 'self' https://accounts.google.com; "
                        b"frame-ancestors 'self';",
                    ),
                ]
                headers.extend(extra)
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, _send_with_headers)


def _stage_uploads(config: AppConfig, filepaths: list[str] | None, req: gr.Request) -> str:
    """Copy uploaded files into the configured staging backend.

    This helper is defined at module level so it can be unit-tested directly.
    """
    # Defense-in-depth: Gradio event handlers can be triggered over
    # WebSockets, which bypass the HTTP-only BasicAuthMiddleware. Re-check
    # credentials here so the upload cannot be used without auth.
    if not _check_request_auth(config, req):
        raise gr.Error("Unauthorized: provide a valid password or API key")

    if not filepaths:
        return "No files to stage."
    count = 0
    skipped = 0
    storage = _create_storage(config)
    for filepath in filepaths:
        src = Path(filepath)
        if not src.exists():
            continue
        if not _is_image_filename(src.name):
            skipped += 1
            continue
        content = src.read_bytes()
        image_info = _validate_image_bytes(content)
        if image_info is None:
            skipped += 1
            continue
        safe_name = f"{uuid.uuid4().hex}{src.suffix.lower()}"
        storage.save(safe_name, content)
        count += 1
    msg = f"Staged {count} photo(s)."
    if skipped:
        msg += f" Skipped {skipped} invalid file(s)."
    if count:
        msg += " Unlock the vault to import them."
    return msg


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
def create_blocks(config: AppConfig) -> gr.Blocks:
    """Create the Gradio Blocks UI with the embedded Secret Photo Viewer."""
    if not HTML_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {HTML_FILE.name}. Run this script from the project root."
        )

    with gr.Blocks(title="Secret Photo Viewer — Headless") as blocks:
        gr.Markdown("# 🔐 Secret Photo Viewer — Headless")
        gr.Markdown(
            "This Gradio interface embeds the standalone ``secret-photo-viewer.html`` "
            "application below. Create a PIN on first run, then unlock to view your vault."
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Direct link")
                gr.Textbox(
                    label="",
                    value="secret-photo-viewer.html",
                    interactive=False,
                    info="Open this path under the Gradio local URL if you prefer it outside the iframe.",
                )

            with gr.Column(scale=1):
                gr.Markdown("### Headless launch info")
                gr.Textbox(
                    label="",
                    value="python gradio_photo_viewer.py --server_name 0.0.0.0 --server_port 7860",
                    interactive=False,
                    info="Run this command on the host and access the URL printed in the terminal.",
                )

        gr.Markdown("---")

        gr.Markdown("### Headless Upload")
        upload = gr.File(
            label="Upload photos to the vault",
            file_count="multiple",
            type="filepath",
        )

        # Gradio's File component does not reliably trigger its backend events
        # when a headless browser manipulates the hidden file input directly.
        # This native file input is exposed for automation tools (e.g.
        # Playwright) and re-uses the same /api/staged endpoint that the
        # Gradio File component uses, so the verification script does not need
        # a separate API fallback.
        headless_html = """
        <div id="headless-upload-wrapper" style="width:0; height:0; overflow:hidden;">
            <input
                id="headless-upload"
                type="file"
                accept="image/*"
                multiple
                style="opacity:0; position:absolute; width:1px; height:1px;"
                aria-label="Headless upload"
            />
        </div>
        """
        gr.HTML(value=headless_html)

        with gr.Row():
            sync_status = gr.Textbox(
                label="Sync status",
                value="Upload files, then unlock the vault to import them.",
                interactive=False,
            )

        gr.HTML(value=_build_iframe_html("secret-photo-viewer.html", config.iframe_height))

        def _stage_uploads_event(filepaths: list[str] | None, req: gr.Request) -> str:
            """Thin Gradio event wrapper around the reusable staging helper."""
            return _stage_uploads(config, filepaths, req)

        _NOTIFY_IFRAME_JS = """
        () => {
            const root = document.querySelector('gradio-app')?.shadowRoot || document;
            const iframe = root.querySelector('iframe[title="Secret Photo Viewer"]');
            if (iframe && iframe.contentWindow) {
                iframe.contentWindow.postMessage({ type: 'SYNC_STAGED' }, window.location.origin);
            }
        }
        """

        # Use .change() instead of .upload() so both the visible Gradio File
        # component and the hidden headless input trigger the staging handler
        # when a file is selected programmatically or by a user.
        upload.change(
            fn=_stage_uploads_event,
            inputs=upload,
            outputs=sync_status,
            js=_NOTIFY_IFRAME_JS,
        )

        # Attach the headless upload listener after the page loads so the
        # native file input is present in the DOM. We use a MutationObserver
        # because gr.HTML is rendered asynchronously and the element may not
        # exist when blocks.load() first runs.
        _HEADLESS_UPLOAD_JS = r"""
        function() {
            const root = document.querySelector('gradio-app')?.shadowRoot || document;
            function attachHeadlessUpload() {
                const input = root.querySelector('#headless-upload');
                if (!input || input._headlessListenerAttached) return;
                input.addEventListener('change', async function() {
                    if (!input.files || input.files.length === 0) return;
                    const formData = new FormData();
                    for (const file of input.files) {
                        formData.append('upload', file, file.name);
                    }
                    try {
                        const response = await fetch('/api/staged', {
                            method: 'POST',
                            body: formData,
                        });
                        if (!response.ok) {
                            console.error('Headless upload failed:', response.status, await response.text());
                            return;
                        }
                        const iframe = root.querySelector('iframe[title="Secret Photo Viewer"]');
                        if (iframe && iframe.contentWindow) {
                            iframe.contentWindow.postMessage({ type: 'SYNC_STAGED' }, window.location.origin);
                        }
                    } catch (err) {
                        console.error('Headless upload error:', err);
                    }
                });
                input._headlessListenerAttached = true;
                window.headlessUploadReady = true;
            }
            attachHeadlessUpload();
            const observer = new MutationObserver(function(mutations) {
                if (root.querySelector('#headless-upload')) {
                    attachHeadlessUpload();
                }
            });
            const observeTarget = root === document ? document.body : root;
            observer.observe(observeTarget, { childList: true, subtree: true });
        }
        """
        blocks.load(fn=lambda: None, inputs=None, outputs=None, js=_HEADLESS_UPLOAD_JS)

    return blocks


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
async def _periodic_cleanup(config: AppConfig, storage: StorageBackend) -> None:
    """Run forever and remove staged files older than the configured max age.

    Does nothing when staging cleanup is disabled (max age <= 0).
    """
    if config.staging_max_age_seconds <= 0:
        return
    while True:
        try:
            await asyncio.sleep(config.staging_max_age_seconds or 3600)
            removed = _clean_old_staged_files(storage, config.staging_max_age_seconds)
            if removed:
                logger.info("Periodic cleanup removed %d stale staged file(s)", removed)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover
            logger.exception("Periodic cleanup failed: %s", exc)
            await asyncio.sleep(60)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> Any:
    config: AppConfig = app.state.config
    storage: StorageBackend = app.state.storage
    if config.staging_max_age_seconds > 0:
        _clean_old_staged_files(storage, config.staging_max_age_seconds)
        task = asyncio.create_task(_periodic_cleanup(config, storage))
    else:
        task = None
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


def create_app(config: AppConfig | None = None) -> FastAPI:
    """Create a FastAPI app with the Gradio UI and custom staging routes."""
    if config is None:
        config = AppConfig.from_env()

    config.staging_dir.mkdir(parents=True, exist_ok=True)

    if not HTML_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {HTML_FILE.name}. Run this script from the project root."
        )

    fastapi_app = FastAPI(lifespan=_lifespan)
    fastapi_app.state.config = config
    fastapi_app.state.limiter = _create_rate_limiter(config)
    fastapi_app.state.storage = _create_storage(config)

    # Authentication and security middleware. BasicAuth is added last so it
    # wraps the app first and rejects unauthorized requests before they reach
    # any route handler (Starlette runs the last-added middleware outermost).
    fastapi_app.add_middleware(SecurityHeadersMiddleware)  # type: ignore[arg-type]
    fastapi_app.add_middleware(BasicAuthMiddleware, config=config)  # type: ignore[arg-type]

    # Register custom routes before mounting Gradio so the static file and API
    # endpoints are served alongside the Gradio UI.
    fastapi_app.get("/api/staged", include_in_schema=False)(_list_staged)
    fastapi_app.post("/api/staged", include_in_schema=False)(_post_staged)
    fastapi_app.get("/api/staged/{filename}", include_in_schema=False)(_get_staged)
    fastapi_app.delete("/api/staged/{filename}", include_in_schema=False)(_delete_staged)
    fastapi_app.get("/api/google/config", include_in_schema=False)(_google_config)
    fastapi_app.post("/api/google/verify", include_in_schema=False)(_google_verify)
    fastapi_app.post("/api/google/photos", include_in_schema=False)(_google_photos)
    fastapi_app.post("/api/google/photos/{media_item_id}/stage", include_in_schema=False)(_google_stage)
    fastapi_app.get(VIEWER_PATH, include_in_schema=False)(_serve_viewer)
    fastapi_app.get("/health", include_in_schema=False)(_health)

    # Prometheus metrics endpoint. Implemented as a direct route so Gradio
    # routing doesn't accidentally swallow the scrape request.
    fastapi_app.get("/metrics", include_in_schema=False)(_metrics)

    # Dynamic gauges reflect the staging directory state at scrape time.
    def _staged_files_count() -> int:
        if not config.staging_dir.exists():
            return 0
        return sum(1 for f in config.staging_dir.iterdir() if f.is_file())

    def _staged_files_bytes() -> int:
        if not config.staging_dir.exists():
            return 0
        total = 0
        for path in config.staging_dir.iterdir():
            if not path.is_file():
                continue
            try:
                total += path.stat().st_size
            except OSError:
                continue
        return total

    STAGED_FILES.set_function(_staged_files_count)
    STAGED_BYTES_GAUGE.set_function(_staged_files_bytes)

    blocks = create_blocks(config=config)
    gr.mount_gradio_app(fastapi_app, blocks, path="/")

    # Clean up stale staged files at startup (local backend only).
    removed = _clean_old_staged_files(fastapi_app.state.storage, config.staging_max_age_seconds)
    if removed:
        logger.info("Removed %d stale staged file(s) at startup", removed)

    return fastapi_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Secret Photo Viewer — Gradio headless display")
    parser.add_argument("--server_name", default=None, help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--server_port", type=int, default=None, help="Port to bind (default: 7860)")
    parser.add_argument(
        "--iframe_height",
        default=None,
        help="CSS height for the embedded iframe (default: 700px).",
    )
    parser.add_argument(
        "--generate-password-hash",
        action="store_true",
        dest="generate_password_hash",
        help="Generate a bcrypt password hash for use with SPV_PASSWORD_HASH, then exit.",
    )
    args = parser.parse_args()

    if args.generate_password_hash:
        print(generate_password_hash())
        sys.exit(0)

    config = AppConfig.from_env()
    overrides: dict[str, Any] = {}
    if args.server_name is not None:
        overrides["host"] = args.server_name
    if args.server_port is not None:
        overrides["port"] = args.server_port
    if args.iframe_height is not None:
        overrides["iframe_height"] = args.iframe_height

    if overrides:
        config = AppConfig(**{**config.__dict__, **overrides})

    app = create_app(config=config)
    logging.getLogger().setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
    logger.info("Starting server on %s:%d", config.host, config.port)
    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    main()
