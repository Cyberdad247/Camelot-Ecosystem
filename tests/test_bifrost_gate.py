from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIFROST_PATH = ROOT / "bin" / "bifrost.py"


def _load_bifrost_module(tag: str):
    module_name = f"bifrost_test_{tag}"
    spec = importlib.util.spec_from_file_location(module_name, BIFROST_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_trusted_owner_env_parsing(monkeypatch):
    monkeypatch.setenv("BIFROST_TRUSTED_TAILNET_OWNERS", "alice@tail, bob@tail ,,")
    mod = _load_bifrost_module("owners")
    assert mod.TRUSTED_TAILNET_OWNERS == {"alice@tail", "bob@tail"}


def test_loopback_owner_can_require_token(monkeypatch):
    monkeypatch.setenv("BIFROST_REQUIRE_TOKEN_ON_LOOPBACK", "1")
    mod = _load_bifrost_module("loopback_token")

    # Simulate owner session without token when strict loopback token mode is enabled.
    monkeypatch.setattr(mod.getpass, "getuser", lambda: mod.CAMELOT_OWNER)
    monkeypatch.setattr(mod, "verify_token", lambda _: False)

    ok, reason = mod.verify_caller(remote_addr="127.0.0.1", presented_token=None)
    assert not ok
    assert reason == "local-owner-token-required"


def test_client_certificate_roaming_verification(monkeypatch):
    monkeypatch.setenv("BIFROST_ALLOW_ANY_VALID_CERT", "1")
    mod = _load_bifrost_module("cert_roaming")

    # Present a dummy cert DER from a non-tailnet IP
    ok, reason = mod.verify_caller(
        remote_addr="198.51.100.42",
        client_cert_der=b"dummy_cert_der"
    )
    assert ok
    assert "mtls" in reason


def test_client_certificate_invalid(monkeypatch):
    monkeypatch.setenv("BIFROST_ALLOW_ANY_VALID_CERT", "0")
    monkeypatch.setenv("BIFROST_TRUSTED_CERT_CNS", "valid-client")
    mod = _load_bifrost_module("cert_invalid")

    # Present an untrusted cert
    ok, reason = mod.verify_caller(
        remote_addr="198.51.100.42",
        client_cert_der=b"invalid_cert_der"
    )
    assert not ok
    assert "untrusted client certificate" in reason


def test_oidc_roaming_verification(monkeypatch):
    monkeypatch.setenv("BIFROST_OIDC_ISSUERS", "https://accounts.google.com")
    mod = _load_bifrost_module("oidc_roaming")

    # Mock token decoding
    # JWT with iss matching the trusted list, and not expired
    import time
    import json
    import base64
    header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').decode().rstrip("=")
    payload_data = {
        "iss": "https://accounts.google.com",
        "exp": time.time() + 1000,
        "aud": "camelot-os",
        "sub": "user_123"
    }
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
    token = f"{header}.{payload}.signature"

    ok, reason = mod.verify_caller(
        remote_addr="198.51.100.42",
        oidc_token=token
    )
    assert ok
    assert "oidc-jwt" in reason


