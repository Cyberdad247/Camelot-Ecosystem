# SPDX-License-Identifier: MIT
"""Unit tests for Agent-Reach Bifrost Bridge Cartridge & HITL Governance."""

import pytest
from control_plane.cartridges.agent_reach_bridge import AgentReachBridgeCartridge, PERMITTED_KNIGHTS


@pytest.fixture
def bridge():
    return AgentReachBridgeCartridge()


def test_knight_rbac_permitted(bridge):
    for knight in PERMITTED_KNIGHTS:
        assert bridge.verify_knight_access(knight) is True


def test_knight_rbac_unauthorized_blocked(bridge):
    assert bridge.verify_knight_access("RANDOM_ROGUE_AGENT") is False
    res = bridge.execute_reach(
        knight_id="RANDOM_ROGUE_AGENT",
        channel="twitter",
        action="search",
        query_or_url="AI trends",
        hitl_approved=True
    )
    assert res.status == "UNAUTHORIZED_KNIGHT"
    assert res.content is None


def test_hitl_gate_blocks_unapproved_live_queries(bridge):
    res = bridge.execute_reach(
        knight_id="LADY_APIS",
        channel="reddit",
        action="search",
        query_or_url="machine learning",
        hitl_approved=False,
        lease_id=None
    )
    assert res.status == "HITL_GATE_BLOCKED"
    assert res.hitl_required is True
    assert res.content is None


def test_hitl_gate_allows_approved_query(bridge):
    res = bridge.execute_reach(
        knight_id="LADY_APIS",
        channel="github",
        action="search",
        query_or_url="Cyberdad247/Agent-Reach",
        hitl_approved=True
    )
    assert res.status == "SUCCESS"
    assert res.content is not None
    assert res.audit_hash.startswith("sha256:")
    assert res.hitl_required is False


def test_sentinel_lease_allows_query(bridge):
    res = bridge.execute_reach(
        knight_id="KNIGHT_STRATEGOS",
        channel="twitter",
        action="search",
        query_or_url="fintech",
        hitl_approved=False,
        lease_id="lease_reach_test_01"
    )
    assert res.status == "SUCCESS"
    assert res.content is not None


def test_diagnostic_doctor_does_not_require_hitl(bridge):
    res = bridge.execute_reach(
        knight_id="SIR_CODEX",
        channel="system",
        action="doctor",
        query_or_url="",
        hitl_approved=False
    )
    assert res.status == "SUCCESS"
    assert res.content["status"] == "OPERATIONAL"
