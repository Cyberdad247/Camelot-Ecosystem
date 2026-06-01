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

