"""Tests for the OpenCodex bridge (control_plane.core.ocx_bridge)."""

from unittest.mock import patch

from control_plane.core.ocx_bridge import (
    KNIGHT_TIER_MAP,
    OCXBridge,
    ProviderModel,
    KnightTierConfig,
    get_bridge,
    is_opencodex_available,
    resolve_knight_model,
)


class TestProviderModel:
    """ProviderModel data class."""

    def test_wire_id(self):
        """wire_id produces provider/model format."""
        pm = ProviderModel("anthropic", "claude-opus-5")
        assert pm.wire_id == "anthropic/claude-opus-5"

    def test_wire_id_with_base_url(self):
        """wire_id ignores base_url."""
        pm = ProviderModel("ollama", "qwen3:8b", base_url="http://localhost:11434")
        assert pm.wire_id == "ollama/qwen3:8b"


class TestKnightTierMap:
    """Tier map coverage and structure."""

    def test_all_engines_have_tiers(self):
        """Every expected engine string has a tier config."""
        expected_engines = [
            "claude_code", "gemini_flash", "antigravity.cli",
            "integration_brain", "open_source", "openai_codex",
            "local_qwen", "open_coder", "agents_a1", "default",
        ]
        for engine in expected_engines:
            assert engine in KNIGHT_TIER_MAP, f"Missing tier for {engine}"

    def test_local_only_engines(self):
        """Local-only engines have local_only=True."""
        for engine in ("local_qwen", "open_coder", "agents_a1"):
            config = KNIGHT_TIER_MAP[engine]
            assert config.local_only is True
            assert config.primary.base_url  # should have Ollama URL

    def test_cloud_engines_have_fallbacks(self):
        """Cloud engines have at least one fallback."""
        for engine in ("claude_code", "gemini_flash", "antigravity.cli"):
            config = KNIGHT_TIER_MAP[engine]
            assert len(config.fallbacks) >= 1
            assert config.local_only is False

    def test_default_tier_exists(self):
        """Default tier is the catch-all."""
        default = KNIGHT_TIER_MAP["default"]
        assert default.tier == "G2"
        assert default.primary.provider == "google"


class TestOCXBridge:
    """OCXBridge resolution and health logic."""

    def setup_method(self):
        self.bridge = OCXBridge(base_url="http://127.0.0.1:10100")

    def test_resolve_local_only_knight(self):
        """Local-only knights resolve to Ollama directly."""
        model, url, key = self.bridge.resolve("sir_ghost", engine="local_qwen")
        assert model == "qwen3:8b"
        assert "11434" in url
        assert key == ""

    def test_resolve_cloud_knight_when_offline(self):
        """When opencodex is down, cloud knights fall back to cliproxy."""
        with patch.object(self.bridge, "is_ready", return_value=False):
            model, url, key = self.bridge.resolve("sir_boris", engine="claude_code")
            assert model == "claude-opus-5"
            assert "8080" in url

    def test_resolve_cloud_knight_when_online(self):
        """When opencodex is ready, cloud knights route through it."""
        with patch.object(self.bridge, "is_ready", return_value=True):
            model, url, key = self.bridge.resolve("sir_boris", engine="claude_code")
            assert model == "anthropic/claude-opus-5"
            assert "10100" in url

    def test_resolve_unknown_engine_uses_default(self):
        """Unknown engine strings fall back to default tier."""
        model, url, key = self.bridge.resolve("sir_unknown", engine="nonexistent")
        # When opencodex is online: google/gemini-3-pro-preview (slug codec)
        # When offline: gemini-3-pro-preview (raw model ID)
        assert "gemini-3-pro-preview" in model

    def test_resolve_with_fallback_chain(self):
        """Fallback chain includes primary + all fallbacks."""
        with patch.object(self.bridge, "is_ready", return_value=True):
            chain = self.bridge.resolve_with_fallback("sir_boris", engine="claude_code")
            assert len(chain) >= 2  # primary + at least 1 fallback
            assert chain[0][0] == "anthropic/claude-opus-5"

    def test_resolve_with_fallback_offline(self):
        """Offline fallback chain is just the primary."""
        with patch.object(self.bridge, "is_ready", return_value=False):
            chain = self.bridge.resolve_with_fallback("sir_boris", engine="claude_code")
            assert len(chain) == 1

    def test_get_combo_config(self):
        """Combo config has strategy and targets."""
        config = self.bridge.get_combo_config(engine="claude_code")
        assert config["strategy"] == "failover"
        assert len(config["targets"]) >= 2
        assert config["targets"][0]["provider"] == "anthropic"

    def test_health_when_offline(self):
        """Health returns unreachable status when offline."""
        with patch("control_plane.core.ocx_bridge._http_get", return_value=None):
            result = self.bridge.health()
            assert result["status"] == "unreachable"

    def test_list_providers_when_offline(self):
        """list_providers returns empty list when offline."""
        with patch("control_plane.core.ocx_bridge._http_get", return_value=None):
            result = self.bridge.list_providers()
            assert result == []


class TestModuleSingleton:
    """Module-level singleton and convenience functions."""

    def test_get_bridge_returns_singleton(self):
        """get_bridge() returns the same instance."""
        b1 = get_bridge()
        b2 = get_bridge()
        assert b1 is b2

    def test_resolve_knight_model_delegates(self):
        """resolve_knight_model delegates to the bridge."""
        with patch.object(OCXBridge, "resolve", return_value=("test-model", "http://test", "")):
            model, url, key = resolve_knight_model("sir_test", engine="default")
            assert model == "test-model"

    def test_is_opencodex_available(self):
        """is_opencodex_available checks readiness."""
        with patch.object(OCXBridge, "is_ready", return_value=True):
            assert is_opencodex_available() is True
        with patch.object(OCXBridge, "is_ready", return_value=False):
            assert is_opencodex_available() is False
