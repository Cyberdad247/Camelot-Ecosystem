"""Tests for the bridge module."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import bridge


def test_version_exists():
    assert bridge.__version__


def test_is_available_returns_bool():
    result = bridge.is_available()
    assert isinstance(result, bool)


def test_assess_risk_clean():
    result = bridge.assess_risk_bridged("build a login page")
    assert result["level"] in ("LOW", "HIGH", "CRITICAL")
    assert "source" in result


def test_assess_risk_dangerous():
    result = bridge.assess_risk_bridged("delete all files rm -rf /")
    assert result["level"] in ("HIGH", "CRITICAL")
    assert result["requires_approval"] is True


def test_bridge_status_structure():
    status = bridge.get_bridge_status()
    assert "os_available" in status
    assert "os_root" in status
    assert "components" in status
    assert isinstance(status["components"], dict)


def test_memory_store_without_kernel():
    """Should return False gracefully when kernel unavailable."""
    result = bridge.memory_store("test", "event")
    assert isinstance(result, bool)


def test_memory_query_without_kernel():
    result = bridge.memory_query({"type": "test"})
    assert isinstance(result, list)


def test_kernel_process_intent_without_kernel():
    result = bridge.kernel_process_intent("TEST_INTENT")
    assert isinstance(result, dict)
    if not bridge.is_available():
        assert result.get("status") == "unavailable"


def test_titan_bridge_fallback_is_usable():
    titan = bridge.get_titan_omega()
    assert titan is not None
    assert "graph" in titan
    assert "flux" in titan
    titan["flux"].store_event("cli-test", "event-1")
    assert titan["flux"].get_session_events("cli-test")


def test_excalibur_bridge_returns_routing_dict():
    result = bridge.kernel_process_intent("status report")
    assert isinstance(result, dict)
    assert "action" in result
    assert "target" in result


def test_thread_safety():
    """Verify component loading lock exists."""
    assert bridge._components_lock is not None
    import threading
    assert isinstance(bridge._components_lock, type(threading.Lock()))
