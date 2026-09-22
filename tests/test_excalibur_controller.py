# SPDX-License-Identifier: MIT

"""Tests for excalibur_controller.

Run with:
    .venv/Scripts/python.exe -m pytest tests/test_excalibur_controller.py -v
"""

from __future__ import annotations

import ast
import json
import re
import secrets
import sys
import unittest.mock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make repo root importable so `import excalibur_controller` works regardless
# of pytest invocation cwd.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import excalibur_controller as ec  # noqa: E402

# ------------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def deterministic_token(monkeypatch: pytest.MonkeyPatch) -> str:
    """Pin the auth token so tests are stable across runs."""
    token = "test-token-do-not-use-in-prod-deadbeef"
    monkeypatch.setenv("EXCALIBUR_AUTH_TOKEN", token)
    monkeypatch.setattr(ec, "AUTH_TOKEN", token)
    yield token


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Ensure every test starts from the canonical initial state."""
    ec.SYSTEM_STATE.update(
        {
            "merlin": "ORCHESTRATING",
            "anya": "STREAMING_AUDIO",
            "lukas": "AWAITING_PRD",
            "sentinel": "IRON_GATE_SECURE",
            "gate_paused": True,
        }
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(ec.app)


# ------------------------------------------------------------------------------
# Bug regression tests
# ------------------------------------------------------------------------------


def test_lowercase_false_bug_is_fixed(client: TestClient, deterministic_token: str) -> None:
    """The original controller crashed on POST /api/go with `NameError: name 'false' is not defined`.

    This test guards against that regression: the call must return 200 and HTML.
    """
    response = client.post("/api/go", headers={"X-Camelot-Auth": deterministic_token})
    assert response.status_code == 200, response.text
    assert "EXECUTION VECTOR RELEASED" in response.text
    assert response.headers["content-type"].startswith("text/html")


def test_no_unused_dead_imports() -> None:
    source = Path(ec.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.asname or alias.name)
    assert "time" not in imported, "`time` import must be removed (was unused)."
    assert "Header" not in imported, "`Header` import must be removed (was unused)."


# ------------------------------------------------------------------------------
# Read endpoints (open)
# ------------------------------------------------------------------------------


def test_status_returns_html_fragment_with_luxora_palette(client: TestClient) -> None:
    response = client.get("/api/status")
    assert response.status_code == 200
    body = response.text
    assert "[MERLIN_Omega]" in body
    assert "[ANYA_Omega]" in body
    assert "[LUKAS]" in body
    assert "[SIR_SENTINEL]" in body
    assert "text-luxora" in body
    assert "text-royal" in body
    assert "PAUSED" in body


def test_status_returns_html_fragment_with_alternative_branches(client: TestClient) -> None:
    # Use patch.dict to avoid mutating the global state for other tests
    with unittest.mock.patch.dict(
        ec.SYSTEM_STATE,
        {
            "merlin": "SLEEP_MODE",
            "lukas": "COMPILING_AST",
            "gate_paused": False,
        },
    ):
        response = client.get("/api/status")
        assert response.status_code == 200
        body = response.text

    # Check for merlin text-green-400
    assert "text-green-400" in body
    assert "SLEEP_MODE" in body

    # Check for lukas text-luxora animate-pulse
    assert "COMPILING_AST" in body

    # Check for LIVE badge instead of PAUSED
    assert "LIVE" in body
    assert "PAUSED" not in body


def test_health_returns_ok(client: TestClient) -> None:
    assert client.get("/health").text == "ok"


def test_version_metadata(client: TestClient) -> None:
    data = client.get("/version").json()
    assert data["name"] == "EXCALIBUR v1000 Controller"
    assert data["version"] == "1.0.0"


def test_dashboard_served(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "EXCALIBUR" in response.text
    assert "htmx" in response.text.lower()
    # Inline data: favicon link in <head> must defeat the implicit /favicon.ico
    # request browsers fire on every page load.
    assert 'rel="icon"' in response.text, "dashboard must declare an inline favicon link"


# ------------------------------------------------------------------------------
# Auth-gated mutations
# ------------------------------------------------------------------------------


def test_go_requires_auth_header(client: TestClient) -> None:
    response = client.post("/api/go")
    assert response.status_code == 401
    body = response.text.lower()
    assert "x-camelot-auth" in body or "token" in body


def test_go_rejects_bad_token(client: TestClient) -> None:
    response = client.post("/api/go", headers={"X-Camelot-Auth": "wrong-token"})
    assert response.status_code == 401


def test_go_releases_gate_and_updates_state(client: TestClient, deterministic_token: str) -> None:
    headers = {"X-Camelot-Auth": deterministic_token}
    response = client.post("/api/go", headers=headers)
    assert response.status_code == 200
    assert "EXECUTION VECTOR RELEASED" in response.text

    status_body = client.get("/api/status").text
    assert "SLEEP_MODE" in status_body
    assert "COMPILING_AST" in status_body
    assert "LIVE" in status_body  # gate is no longer paused
    assert "PAUSED" not in status_body


def test_rezero_requires_auth_header(client: TestClient) -> None:
    response = client.post("/api/rezero")
    assert response.status_code == 401


def test_rezero_rolls_back_to_paused(client: TestClient, deterministic_token: str) -> None:
    headers = {"X-Camelot-Auth": deterministic_token}
    client.post("/api/go", headers=headers)
    assert "LIVE" in client.get("/api/status").text

    response = client.post("/api/rezero", headers=headers)
    assert response.status_code == 200
    assert "REZERO ROLLBACK EXECUTED" in response.text

    status_body = client.get("/api/status").text
    assert "AWAITING_PRD" in status_body
    assert "PAUSED" in status_body


def test_test_reset_helper_disabled_without_debug_flag(
    client: TestClient, deterministic_token: str
) -> None:
    """Without EXCALIBUR_DEBUG=1 the route must 404 (production build guard)."""
    headers = {"X-Camelot-Auth": deterministic_token}
    client.post("/api/go", headers=headers)
    assert "LIVE" in client.get("/api/status").text

    response = client.post("/api/_test/reset")
    assert response.status_code == 404


def test_test_reset_helper_enabled_with_debug_flag(
    monkeypatch: pytest.MonkeyPatch, deterministic_token: str
) -> None:
    """With EXCALIBUR_DEBUG=1 set, the route resets state cleanly."""
    monkeypatch.setenv("EXCALIBUR_DEBUG", "1")
    client = TestClient(ec.app)
    headers = {"X-Camelot-Auth": deterministic_token}
    client.post("/api/go", headers=headers)
    assert "LIVE" in client.get("/api/status").text

    response = client.post("/api/_test/reset")
    assert response.status_code == 200
    assert "ORCHESTRATING" in client.get("/api/status").text
    assert "PAUSED" in client.get("/api/status").text


# ------------------------------------------------------------------------------
# CORS allow-list
# ------------------------------------------------------------------------------


def test_default_cors_uses_regex_not_wildcards() -> None:
    """Browsers always include the explicit port in Origin headers, so the safe
    default is an empty `allow_origins` plus a regex that matches localhost on
    any port. Literal wildcard is forbidden."""
    assert ec.DEFAULT_ALLOWED_ORIGINS == ()
    assert ec.DEFAULT_ALLOW_ORIGIN_REGEX
    assert "*" not in ec.DEFAULT_ALLOW_ORIGIN_REGEX
    # Assertion-by-behavior: compile the regex and verify it matches the
    # origins we expect (browser-typical) and rejects attacker origins.
    compiled = re.compile(ec.DEFAULT_ALLOW_ORIGIN_REGEX)
    assert compiled.match("http://localhost")
    assert compiled.match("http://localhost:8811")
    assert compiled.match("http://127.0.0.1:5500")
    assert compiled.match("http://[::1]")
    assert compiled.match("http://[::1]:8811")
    assert compiled.match("https://localhost:443")
    assert not compiled.match("http://evil.example.com")
    assert not compiled.match("http://attacker.com#localhost")
    assert not compiled.match("http://localhost.evil.com")


def test_cors_credentials_disabled_and_no_wildcard() -> None:
    """Production-fix: credentials are off and the live middleware has no wildcard.

    We branch on the Starlette middleware API version: in older versions the
    `Middleware` wrapper exposes its constructor kwargs as `.options`; in newer
    versions they are stored under `.kwargs`. We assert either way.
    """
    from fastapi.middleware.cors import CORSMiddleware as _CORS

    for m in ec.app.user_middleware:
        if m.cls is _CORS:
            opts = getattr(m, "options", None) or getattr(m, "kwargs", None) or {}
            assert opts.get("allow_credentials") is False, (
                "allow_credentials must stay off; the dashboard uses a plain "
                "X-Camelot-Auth header, not cookies."
            )
            origins = opts.get("allow_origins") or []
            assert "*" not in origins, "Wildcard origins are forbidden."
            assert opts.get("allow_origin_regex"), "Regex must be configured."
            return
    pytest.fail("CORSMiddleware was not registered on the app.")


def test_cors_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXCALIBUR_ALLOW_ORIGINS", "https://app.example.com, https://ops.example.com")
    parsed = ec._parse_allowed_origins()  # noqa: SLF001 - intentional introspection
    assert parsed == ["https://app.example.com", "https://ops.example.com"]


# ------------------------------------------------------------------------------
# SSE stream payload shape
# ------------------------------------------------------------------------------


def test_stream_is_event_stream(client: TestClient) -> None:
    with client.stream("GET", "/api/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        chunks: list[str] = []
        seen_text = False
        for line in response.iter_lines():
            chunks.append(line)
            if '"text_chunk"' in line and '"Analyzing' in line:
                seen_text = True
                break
            if len(chunks) > 400:
                break
    assert seen_text, "Expected at least one SSE data chunk containing the first phrase."


def test_audio_chunk_has_base64_pcm(client: TestClient) -> None:
    """The real-voice SSE event carries base64-encoded little-endian int16 PCM."""
    import base64 as _b64
    import struct as _struct

    with client.stream("GET", "/api/stream") as response:
        assert response.status_code == 200
        line: str | None = None
        for raw in response.iter_lines():
            if raw.startswith("data: ") and '"audio_chunk"' in raw:
                line = raw
                break
        assert line is not None, "Expected an SSE chunk with audio_chunk."

    payload = json.loads(line[6:])
    assert payload["sample_rate"] == ec._AUDIO_SR
    assert payload["channels"] == 1
    assert payload["samples"] == ec._AUDIO_SR * ec._AUDIO_CHUNK_MS // 1000
    assert payload["is_phrase_start"] is True
    assert "text_chunk" in payload and payload["text_chunk"]

    pcm = _b64.b64decode(payload["audio_chunk"])
    expected_bytes = payload["samples"] * 2  # 16-bit = 2 bytes per sample
    assert len(pcm) == expected_bytes, f"PCM length {len(pcm)} != {expected_bytes}"
    # Round-trip the first sample as int16 little-endian.
    first = _struct.unpack("<h", pcm[:2])[0]
    assert -32768 <= first <= 32767


# ------------------------------------------------------------------------------
# Timing-safe token comparison
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Camelot Mesh-compatible JSONL event log
# -----------------------------------------------------------------------------


def test_emit_event_writes_jsonl_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, deterministic_token: str
) -> None:
    log = tmp_path / "events.jsonl"
    monkeypatch.setattr(ec, "EVENT_LOG_FILE", log)

    ec._emit_event(
        "synthetic",
        knight="test",
        before={"k": "v1"},
        after={"k": "v2"},
        client="test/fixture",
        metadata={"reason": "unit-test"},
    )
    assert log.exists()
    line = log.read_text(encoding="utf-8").strip()
    record = json.loads(line)
    assert record["kind"] == "synthetic"
    assert record["knight"] == "test"
    assert record["before"] == {"k": "v1"}
    assert record["after"] == {"k": "v2"}
    assert record["client"] == "test/fixture"
    assert record["metadata"] == {"reason": "unit-test"}
    assert record["ts"].endswith("Z")
    assert "T" in record["ts"]


def test_post_go_appends_event_with_before_after(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, deterministic_token: str
) -> None:
    log = tmp_path / "events.jsonl"
    monkeypatch.setattr(ec, "EVENT_LOG_FILE", log)
    monkeypatch.delenv("EXCALIBUR_DEBUG", raising=False)

    headers = {"X-Camelot-Auth": deterministic_token}
    client = TestClient(ec.app)
    response = client.post("/api/go", headers=headers)
    assert response.status_code == 200
    assert log.exists()

    records = [
        json.loads(line)
        for line in log.read_text(encoding="utf-8").strip().splitlines()
        if line
    ]
    assert records, "expected at least one event after /api/go"
    last = records[-1]
    assert last["kind"] == "go"
    assert last["knight"] == "operator"
    assert last["before"]["gate_paused"] is True
    assert last["after"]["gate_paused"] is False
    assert last["metadata"]["auth_scheme"] == "X-Camelot-Auth"


def test_post_rezero_appends_event_with_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, deterministic_token: str
) -> None:
    log = tmp_path / "events.jsonl"
    monkeypatch.setattr(ec, "EVENT_LOG_FILE", log)
    monkeypatch.delenv("EXCALIBUR_DEBUG", raising=False)

    client = TestClient(ec.app)
    headers = {"X-Camelot-Auth": deterministic_token}
    client.post("/api/go", headers=headers)
    response = client.post("/api/rezero", headers=headers)
    assert response.status_code == 200

    records = [
        json.loads(line)
        for line in log.read_text(encoding="utf-8").strip().splitlines()
        if line
    ]
    last = records[-1]
    assert last["kind"] == "rezero"
    assert last["before"]["gate_paused"] is False
    assert last["after"]["gate_paused"] is True


def test_emit_event_never_raises_on_bad_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Even if the event-log file is unwritable, _emit_event must not raise."""
    monkeypatch.setattr(ec, "EVENT_LOG_FILE", Path("Z:/definitely/missing/events.jsonl"))
    try:
        ec._emit_event("synthetic", knight="osc")
    except Exception as exc:
        raise AssertionError(f"_emit_event must swallow OSError, got: {exc!r}")


def test_emit_event_uses_modern_timezone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `ts` field should be timezone-aware (suffix `Z`)."""
    log = tmp_path / "events.jsonl"
    monkeypatch.setattr(ec, "EVENT_LOG_FILE", log)
    ec._emit_event("synthetic")
    record = json.loads(log.read_text(encoding="utf-8").strip())
    assert record["ts"].endswith("Z")
    # ISO 8601 with timezone offset is accepted; we just want a recent stamp.
    assert record["ts"][0:4].isdigit()


def test_derive_client_ip_prefers_xff_when_trusted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXCALIBUR_TRUST_PROXY", "1")

    class _StubClient:
        host = "10.0.0.1"

    class _StubRequest:
        headers = {"x-forwarded-for": "203.0.113.7, 10.0.0.1"}
        client = _StubClient()

    assert ec._derive_client_ip(_StubRequest()) == "203.0.113.7"


def test_derive_client_ip_falls_back_when_proxy_untrusted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("EXCALIBUR_TRUST_PROXY", raising=False)

    class _StubClient:
        host = "10.0.0.1"

    class _StubRequest:
        headers = {"x-forwarded-for": "203.0.113.7"}
        client = _StubClient()

    assert ec._derive_client_ip(_StubRequest()) == "10.0.0.1"


def test_derive_client_ip_anon_when_no_client(monkeypatch: pytest.MonkeyPatch) -> None:
    class _StubRequest:
        headers: dict = {}
        client = None

    assert ec._derive_client_ip(_StubRequest()) == "anon"


# ------------------------------------------------------------------------------
# Frontend suppression contract (SSE warning filters)
# -----------------------------------------------------------------------------


def test_dashboard_installs_sse_suppression_handlers(client: TestClient) -> None:
    body = client.get("/").text
    assert "installExcaliburSseSuppression" in body
    assert "error" in body
    assert "unhandledrejection" in body
    assert "htmx:sseError" in body
    assert "EventSource" in body


# ------------------------------------------------------------------------------
# Portable-exe spec validity
# -----------------------------------------------------------------------------


def test_excalibur_spec_exists_and_pyinstaller_safe() -> None:
    spec = Path(ROOT) / "excalibur.spec"
    assert spec.exists(), "excalibur.spec must be present at the repo root"
    text = spec.read_text(encoding="utf-8")
    assert "Analysis(" in text and "EXE(" in text and "COLLECT(" in text
    assert "excalibur_controller.py" in text
    assert "excalibur_dashboard.html" in text


def test_excalibur_entry_shim_defines_main() -> None:
    shim = Path(ROOT) / "excalibur.py"
    assert shim.exists(), "excalibur.py entry-shim must be present"
    text = shim.read_text(encoding="utf-8")
    assert "def main()" in text
    assert "excalibur_main" in text
    assert "uvicorn.run" in text


def test_auth_uses_timing_safe_compare(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression guard: token comparison must go through secrets.compare_digest."""
    called = {"flag": False}
    real = secrets.compare_digest

    def spy(a: str, b: str) -> bool:  # type: ignore[no-redef]
        called["flag"] = True
        return real(a, b)

    monkeypatch.setattr(secrets, "compare_digest", spy)
    client = TestClient(ec.app)
    response = client.post("/api/go", headers={"X-Camelot-Auth": ec.AUTH_TOKEN})
    assert response.status_code == 200
    assert called["flag"], (
        "_require_token must call secrets.compare_digest to be timing-safe."
    )
