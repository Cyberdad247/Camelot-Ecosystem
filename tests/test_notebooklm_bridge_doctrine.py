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
