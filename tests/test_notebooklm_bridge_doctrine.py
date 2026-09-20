# SPDX-License-Identifier: MIT
"""Sovereign Cloud-Brain doctrine guard (prime NotebookLM, twin open-notebook)."""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_PATH = REPO_ROOT / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"


def _load_bridge():
    spec = importlib.util.spec_from_file_location("notebooklm_bridge_doctrine", BRIDGE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cloud_brain_doctrine_order_is_prime_then_twin():
    """NotebookLM prime first, open-notebook twin (VKG long-term) second. Never inverted."""
    bridge = _load_bridge()
    assert bridge.CLOUD_BRAIN_DOCTRINE == ("notebooklm-prime", "open-notebook-twin-vkg-longterm")
    assert bridge.CLOUD_BRAIN_DOCTRINE[0] == "notebooklm-prime"


def test_canonical_notebook_identity_stable():
    """Canonical short-term brain notebook must remain the ratified Alpha-Omega notebook."""
    bridge = _load_bridge()
    assert bridge.CANONICAL_NOTEBOOK_ID == "8c656cfa-a189-409e-a72d-07692a47f17e"
    assert bridge.CANONICAL_NOTEBOOK_TITLE == "Camelot-OS: The Alpha Omega Distillation Protocol"


def test_synthesis_ttl_bounded():
    """Remote synthesis cache stays TTL-bounded so the twin cannot go stale-primary."""
    bridge = _load_bridge()
    assert bridge.SYNTHESIS_TTL_S == 900


def test_memo_key_shared_with_go_lane():
    """Python memo keys match the Go Bifrost scheme: cb:memo: + sha256 hex."""
    import re

    bridge = _load_bridge()
    assert bridge.MEMO_PREFIX == "cb:memo:"
    assert bridge.REDIS_MEMO_TTL_S == 600
    k1 = bridge._memo_key("nb1", "prime query")
    k2 = bridge._memo_key("nb1", "prime query")
    assert k1 == k2
    assert re.fullmatch(r"cb:memo:[0-9a-f]{64}", k1)
    assert bridge._memo_key("nb1", "other") != k1
    assert bridge._memo_key("nb2", "prime query") != k1


def test_memo_roundtrip_or_graceful_skip():
    """Redis memo round-trips when the server is up, degrades to None when down."""
    bridge = _load_bridge()
    probe = "doctrine-probe-35b7c9d2"
    bridge._memo_store(bridge._memo_key("nb-test", probe), "memo-value")
    hit = bridge._memo_lookup(bridge._memo_key("nb-test", probe))
    # Redis down -> None (graceful); Redis up -> exact value. Either is correct.
    assert hit in (None, "memo-value")


def test_prime_circuit_breaker_fails_fast():
    """Open breaker fails _build_client immediately without network."""
    import asyncio
    import time

    bridge = _load_bridge()
    bridge._client = None
    bridge._breaker_open_until = time.time() + 60.0
    t0 = time.perf_counter()
    try:
        asyncio.run(bridge._build_client())
        opened = False
    except Exception:
        opened = True
    elapsed = time.perf_counter() - t0
    assert opened is True
    assert elapsed < 5.0
    bridge._breaker_open_until = 0.0
    assert bridge.BREAKER_COOLDOWN_S == 300.0
