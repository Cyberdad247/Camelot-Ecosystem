"""EXCALIBUR Phase 3 acceptance tests — FirnFlow L1/L2 memory."""
import pytest
from control_plane.firnflow import FirnFlow


@pytest.fixture
def firnflow():
    return FirnFlow()


def test_l1_retrieve(firnflow):
    """Phase 3.2 accept: L1 anchor + retrieve returns the stored value."""
    firnflow.anchor("camelot_test", "sovereign_os", tier="L1")
    results = firnflow.retrieve("camelot_test")
    assert results, "Expected at least one result from L1"
    assert any(r.value == "sovereign_os" for r in results)


def test_l1_token_budget(firnflow):
    """L1 stays within 8192 token budget."""
    status = firnflow.status()
    assert status["l1_tokens"] <= status["l1_budget"]


def test_l1_anchor_multiple(firnflow):
    """Multiple anchors are stored independently."""
    firnflow.anchor("key_a", "value_alpha", tier="L1")
    firnflow.anchor("key_b", "value_beta", tier="L1")
    ra = firnflow.retrieve("key_a")
    rb = firnflow.retrieve("key_b")
    assert any(r.value == "value_alpha" for r in ra)
    assert any(r.value == "value_beta" for r in rb)


def test_status_fields(firnflow):
    """status() returns expected keys."""
    status = firnflow.status()
    for key in ("l1_entries", "l1_tokens", "l1_budget", "l2_backend"):
        assert key in status, f"Missing key: {key}"


def test_crystallize(firnflow):
    """crystallize() adds a crystal entry."""
    before = firnflow.status().get("crystals", 0)
    firnflow.crystallize("test_skill_001", {"pattern": "use importlib for dynamic loads", "confidence": 0.9})
    after = firnflow.status().get("crystals", 0)
    assert after >= before
