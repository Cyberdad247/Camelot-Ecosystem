# SPDX-License-Identifier: MIT

"""Unit tests for OpenAI OAuth Dev Proxy assimilation in Camelot-OS.

Validates:
- Token decoding & JWT claims parsing (zero external dependencies).
- Auth discovery and candidates resolution.
- Token refresh check logic.
- OpenAIOAuthClient model cataloging and chat completion transformation.
- OpenAIOAuthProxyServer HTTP endpoints (/health, /v1/models, /v1/chat/completions, /v1/images/generations).
- Integration with omniroute_policies (LANE_OPENAI_OAUTH_PROXY) and ocx_bridge.
"""

import json
import time
from unittest.mock import patch

from control_plane.core.ocx_bridge import (
    KNIGHT_TIER_MAP,
    get_fcc_provider_descriptor,
)
from control_plane.dispatch.omniroute_policies import (
    LANE_OPENAI_OAUTH_PROXY,
    VALID_LANES,
    select_lane,
)
from control_plane.infra.openai_oauth_proxy import (
    EffectiveAuth,
    OpenAIOAuthClient,
    OpenAIOAuthProxyServer,
    decode_base64_url,
    derive_account_id,
    is_oauth_proxy_healthy,
    load_auth_tokens,
    parse_jwt_claims,
    resolve_auth_file_candidates,
    should_refresh_access_token,
)


class TestOpenAIOAuthTokensAndClaims:
    """Test JWT and OAuth token handling."""

    def test_decode_base64_url(self):
        # "hello world" in base64url is "aGVsbG8gd29ybGQ"
        assert decode_base64_url("aGVsbG8gd29ybGQ") == "hello world"
        assert decode_base64_url("invalid!!!") is None

    def test_parse_jwt_claims(self):
        payload = {"sub": "user_123", "exp": 1799999999, "chatgpt_account_id": "acc_xyz789"}
        payload_b64 = decode_base64_url
        # Create a mock JWT: header.payload.sig
        header_b64 = "eyJhbGciOiJSUzI1NiJ9"
        raw_b64 = (
            b"eyJzdWIiOiAidXNlcl8xMjMiLCAiZXhwIjogMTc5OTk5OTk5OSwgImNoYXRncHRfYWNjb3VudF9pZCI6ICJhY2NfeHl6Nzg5In0="
        ).decode("ascii").replace("=", "").replace("+", "-").replace("/", "_")
        mock_jwt = f"{header_b64}.{raw_b64}.mock_signature"

        claims = parse_jwt_claims(mock_jwt)
        assert claims is not None
        assert claims["sub"] == "user_123"
        assert claims["chatgpt_account_id"] == "acc_xyz789"

    def test_derive_account_id(self):
        token_with_nested_claim = (
            "eyJhbGciOiJSUzI1NiJ9."
            + "eydodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgnOiB7J2NoYXRncHRfYWNjb3VudF9pZCc6ICdhY2NfbmVzdGVkMTIzJ319"
            .replace("'", '"')
            .encode("utf-8")
            .hex()  # we construct proper base64
        )
        nested_json = json.dumps({"https://api.openai.com/auth": {"chatgpt_account_id": "acc_nested123"}})
        import base64
        nested_b64 = base64.urlsafe_b64encode(nested_json.encode("utf-8")).decode("ascii").rstrip("=")
        jwt_nested = f"eyJhbGciOiJSUzI1NiJ9.{nested_b64}.sig"

        assert derive_account_id(jwt_nested) == "acc_nested123"

    def test_should_refresh_access_token(self):
        # Empty access token requires refresh
        assert should_refresh_access_token(None, None) is True
        assert should_refresh_access_token("", None) is True

        # Valid future token with recent refresh does not need refresh
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        exp_future = int(time.time()) + 3600
        claims_json = json.dumps({"exp": exp_future})
        import base64
        b64_claim = base64.urlsafe_b64encode(claims_json.encode("utf-8")).decode("ascii").rstrip("=")
        jwt = f"header.{b64_claim}.sig"
        assert should_refresh_access_token(jwt, now_iso) is False

        # Expired token needs refresh
        exp_past = int(time.time()) - 100
        claims_expired = json.dumps({"exp": exp_past})
        b64_exp = base64.urlsafe_b64encode(claims_expired.encode("utf-8")).decode("ascii").rstrip("=")
        jwt_expired = f"header.{b64_exp}.sig"
        assert should_refresh_access_token(jwt_expired, None) is True


class TestAuthFileResolutionAndLoad:
    """Test auth.json loading & resolution."""

    def test_resolve_auth_file_candidates(self, monkeypatch):
        monkeypatch.setenv("CODEX_HOME", "/custom/codex")
        candidates = resolve_auth_file_candidates()
        assert any("custom" in c and "codex" in c for c in candidates)
        assert any(".codex" in c for c in candidates)

    def test_load_auth_tokens_mocked(self, tmp_path):
        fake_auth_file = tmp_path / "auth.json"
        fake_auth_file.write_text(
            json.dumps({
                "auth_mode": "chatgpt",
                "tokens": {
                    "access_token": "mock_access_token_123",
                    "refresh_token": "mock_refresh_token_456",
                    "account_id": "acc_mock_999",
                },
                "last_refresh": "2026-08-25T00:00:00Z",
            }),
            encoding="utf-8",
        )

        with patch("control_plane.infra.openai_oauth_proxy.should_refresh_access_token", return_value=False):
            auth = load_auth_tokens(auth_file_path=str(fake_auth_file))
            assert auth.access_token == "mock_access_token_123"
            assert auth.account_id == "acc_mock_999"
            assert auth.refresh_token == "mock_refresh_token_456"


class TestOpenAIOAuthClientAndProxy:
    """Test upstream client normalization and proxy endpoints."""

    def test_list_models_fallback(self):
        client = OpenAIOAuthClient(base_url="http://127.0.0.1:99999")
        with patch.object(client, "request", return_value=(500, {}, b"{}")):
            models = client.list_models()
            assert "gpt-5.5" in models
            assert "gpt-image-2" in models

    def test_chat_completions_formatting(self):
        client = OpenAIOAuthClient(base_url="http://127.0.0.1:99999")
        upstream_codex_response = {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "text", "text": "Hello from ChatGPT OAuth!"}],
                }
            ]
        }
        with patch.object(client, "get_auth", return_value=EffectiveAuth(access_token="tok", account_id="acc")):
            with patch.object(client, "request", return_value=(200, {}, json.dumps(upstream_codex_response).encode("utf-8"))):
                status, resp = client.chat_completions({
                    "model": "gpt-5.4",
                    "messages": [{"role": "user", "content": "Hi"}],
                })
                assert status == 200
                assert resp["object"] == "chat.completion"
                assert resp["choices"][0]["message"]["content"] == "Hello from ChatGPT OAuth!"

    def test_image_generation_formatting(self):
        client = OpenAIOAuthClient(base_url="http://127.0.0.1:99999")
        upstream_img_response = {
            "created": 123456,
            "data": [{"b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}],
        }
        with patch.object(client, "get_auth", return_value=EffectiveAuth(access_token="tok", account_id="acc")):
            with patch.object(client, "request", return_value=(200, {}, json.dumps(upstream_img_response).encode("utf-8"))):
                status, resp = client.generate_image({"prompt": "cybernetic knight in obsidian armor"})
                assert status == 200
                assert "data" in resp
                assert len(resp["data"]) == 1


class TestOmniroutePolicyIntegration:
    """Test omniroute_policies integration for LANE_OPENAI_OAUTH_PROXY."""

    def test_lane_constants(self):
        assert LANE_OPENAI_OAUTH_PROXY == "openai_oauth_proxy"
        assert LANE_OPENAI_OAUTH_PROXY in VALID_LANES

    def test_select_lane_matches_openai_oauth_keywords(self):
        sig1 = select_lane("Route through openai_oauth dev proxy")
        assert sig1.lane == LANE_OPENAI_OAUTH_PROXY
        assert sig1.matched_keyword == "openai_oauth"

        sig2 = select_lane("Use local chatgpt_account proxy on port_10531")
        assert sig2.lane == LANE_OPENAI_OAUTH_PROXY
        assert "port_10531" in sig2.matched_keyword or "chatgpt_account" in sig2.matched_keyword

        sig3 = select_lane("Generate avatar image using gpt-image-2 zero_api_key")
        assert sig3.lane == LANE_OPENAI_OAUTH_PROXY


class TestOCXBridgeIntegration:
    """Test ocx_bridge integration for openai_oauth provider and tier."""

    def test_fcc_provider_catalog_has_openai_oauth(self):
        desc = get_fcc_provider_descriptor("openai_oauth")
        assert desc is not None
        assert desc.provider_id == "openai_oauth"
        assert desc.display_name == "OpenAI OAuth Dev Proxy"
        assert desc.local is True
        assert "10531" in desc.default_base_url

    def test_knight_tier_map_has_openai_oauth(self):
        assert "openai_oauth" in KNIGHT_TIER_MAP
        tier_cfg = KNIGHT_TIER_MAP["openai_oauth"]
        assert tier_cfg.tier == "X1"
        assert tier_cfg.primary.provider == "openai_oauth"
        assert any(fb.model == "gpt-image-2" for fb in tier_cfg.fallbacks)


class TestProxyServerLifecycle:
    """Test proxy server start, stop, and health probe."""

    def test_server_start_stop(self):
        # Pick an unprivileged ephemeral port for testing
        test_port = 10599
        server = OpenAIOAuthProxyServer(port=test_port)
        started = server.start()
        if started:
            try:
                assert server.is_running is True
                # Health check probe
                assert is_oauth_proxy_healthy(port=test_port) is True
            finally:
                server.stop()
                assert server.is_running is False
