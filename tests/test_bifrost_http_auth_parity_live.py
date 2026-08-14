# SPDX-License-Identifier: MIT

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

import pytest


def _http_status(url: str, token: str | None = None) -> int:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["x-camelot-token"] = token
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=2.0) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except (OSError, urllib.error.URLError, TimeoutError):
        return 0


def _load_token() -> str | None:
    token_path = Path.home() / ".camelot" / "bifrost.token"
    try:
        token = token_path.read_text(encoding="ascii").strip()
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None
    return token or None


def test_live_http_auth_parity_between_rust_and_go_sidecar():
    token = _load_token()
    if not token:
        pytest.skip("missing ~/.camelot/bifrost.token for live parity test")

    rust_health = _http_status("http://127.0.0.1:8001/health")
    sidecar_health = _http_status("http://127.0.0.1:8011/health")
    if rust_health != 200 or sidecar_health != 200:
        pytest.skip(
            f"live services unavailable for parity test (rust={rust_health}, sidecar={sidecar_health})"
        )

    vectors = [
        ("none", None, 401),
        ("invalid", "invalid-token", 401),
        ("valid", token, 200),
    ]
    for label, candidate, expected in vectors:
        rust_status = _http_status("http://127.0.0.1:8001/bifrost/status", candidate)
        sidecar_status = _http_status("http://127.0.0.1:8011/v1/bifrost/status", candidate)
        assert rust_status == expected, f"rust status mismatch for {label}: {rust_status}"
        assert sidecar_status == expected, f"sidecar status mismatch for {label}: {sidecar_status}"
        assert rust_status == sidecar_status, (
            f"parity mismatch for {label}: rust={rust_status} sidecar={sidecar_status}"
        )

