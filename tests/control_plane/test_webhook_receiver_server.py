# SPDX-License-Identifier: MIT
"""Contract tests for the webhook receiver HTTP wrapper (loopback :9000).

Pins:
- routing: /webhook/health answers 200; POST /webhook/* is the ingest path
- HMAC contract: valid signature -> 200 DEPLOYED receipt; invalid -> 401 UNAUTHORIZED
- fail-closed: the server refuses to start without GITHUB_WEBHOOK_SECRET
- no external network: every test binds an ephemeral loopback port in-process
"""

from __future__ import annotations

import hashlib
import hmac
import json
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from control_plane.infra.vps_github_webhook import CamelotVPSWebhookHandler
from control_plane.infra.webhook_server import build_handler, main

SECRET = "test_sovereign_secret_2026"
RECEIVER = CamelotVPSWebhookHandler(
    secret=SECRET, state_dir=Path(tempfile.mkdtemp(prefix="webhook_receipts_"))
)


def _start_ephemeral():
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), build_handler(RECEIVER))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _sig(payload: bytes) -> str:
    return "sha256=" + hmac.new(SECRET.encode(), payload, hashlib.sha256).hexdigest()


def _post(port: int, path: str, body: bytes | None, headers: dict) -> tuple[int, dict]:
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def _push_payload() -> bytes:
    return json.dumps(
        {
            "ref": "refs/heads/main",
            "after": "a" * 40,
            "repository": {"full_name": "Cyberdad247/Camelot-VPS"},
        }
    ).encode("utf-8")


def test_health_route_answers_200() -> None:
    server = _start_ephemeral()
    try:
        status, payload = _post(server.server_address[1], "/webhook/health", None, {})
    finally:
        server.shutdown()
    assert status == 200
    assert payload["status"] == "ok"


def test_valid_signature_gets_200_receipt() -> None:
    server = _start_ephemeral()
    port = server.server_address[1]
    payload = _push_payload()
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": _sig(payload),
        "X-GitHub-Event": "push",
    }
    try:
        status, body = _post(port, "/webhook/camelot-vps", payload, headers)
    finally:
        server.shutdown()
    assert status == 200
    assert body["verified"] is True
    # Deploy mode is off in tests: verified pushes are ACCEPTED, never a
    # claimed DEPLOYED (the executor finalizes the receipt when enabled).
    assert body["build_status"] == "ACCEPTED"
    assert len(body["commit_sha"]) == 40


def test_invalid_signature_gets_401() -> None:
    server = _start_ephemeral()
    port = server.server_address[1]
    payload = _push_payload()
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": "sha256=" + "f" * 64,
        "X-GitHub-Event": "push",
    }
    try:
        status, body = _post(port, "/webhook/camelot-vps", payload, headers)
    finally:
        server.shutdown()
    assert status == 401
    assert body["verified"] is False
    assert body["build_status"] == "UNAUTHORIZED"


def test_unknown_route_gets_404() -> None:
    server = _start_ephemeral()
    try:
        status, _ = _post(server.server_address[1], "/not-a-route", b"{}", {"Content-Type": "application/json"})
    finally:
        server.shutdown()
    assert status == 404


def test_handler_fails_closed_without_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        CamelotVPSWebhookHandler(state_dir=Path(tempfile.mkdtemp(prefix="webhook_closed_")))


def test_main_refuses_to_start_without_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)
    assert main([]) == 2
