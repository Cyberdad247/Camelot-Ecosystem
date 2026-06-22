# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""Phase 4 autonomy hardening — Ed25519 signatures + term-based leader election."""
import asyncio

import pytest

pytest.importorskip("cryptography")

from control_plane.distributed_ledger_consensus import (  # noqa: E402
    ConsensusMessage,
    ConsensusPhase,
    DistributedConsensus,
    NodeRole,
)

_PHASE = list(ConsensusPhase)[0]


def _msg(node_id: str) -> ConsensusMessage:
    return ConsensusMessage(
        node_id=node_id, phase=_PHASE, entry_id="e1", sequence=1,
        timestamp=123.0, data={"x": 1},
    )


def test_ed25519_signature_verifies_across_nodes():
    a = DistributedConsensus("A", ["B"])
    b = DistributedConsensus("B", ["A"])
    b.register_public_key("A", a.public_key_hex())

    m = _msg("A")
    m.signature = a._sign_message(m.to_json())
    assert b._verify_signature(m) is True


def test_tampered_message_fails_verification():
    a = DistributedConsensus("A", ["B"])
    b = DistributedConsensus("B", ["A"])
    b.register_public_key("A", a.public_key_hex())

    m = _msg("A")
    m.signature = a._sign_message(m.to_json())
    m.data = {"x": 999}  # tamper after signing
    assert b._verify_signature(m) is False


def test_unknown_sender_rejected_in_strict_mode():
    a = DistributedConsensus("A", ["B"])
    b = DistributedConsensus("B", ["A"], strict_signatures=True)  # B never registers A's key

    m = _msg("A")
    m.signature = a._sign_message(m.to_json())
    assert b._verify_signature(m) is False


def test_unknown_sender_lenient_fallback_when_not_strict():
    # Default (non-strict) preserves the live cluster: unknown sender + non-empty
    # signature passes the legacy check (no regression until key exchange lands).
    a = DistributedConsensus("A", ["B"])
    b = DistributedConsensus("B", ["A"])  # not strict, no key registered

    m = _msg("A")
    m.signature = a._sign_message(m.to_json())
    assert b._verify_signature(m) is True


def test_request_vote_raft_rules():
    n = DistributedConsensus("N", ["X", "Y"])
    assert n.request_vote(1, "X") is True       # higher term, first vote
    assert n.current_term == 1 and n.voted_for == "X"
    assert n.request_vote(1, "Y") is False       # already voted this term
    assert n.request_vote(1, "X") is True        # idempotent for same candidate
    assert n.request_vote(0, "Z") is False       # stale term
    assert n.request_vote(2, "Y") is True        # higher term resets the vote
    assert n.current_term == 2 and n.voted_for == "Y"


def test_election_wins_only_on_quorum():
    n = DistributedConsensus("N", ["X", "Y"], quorum=2)

    async def grant(peer, term):
        return True  # peers all grant → quorum reached

    n._request_peer_vote = grant
    asyncio.run(n._become_candidate())
    assert n.role == NodeRole.LEADER
    assert n.leader_id == "N" and n.current_term == 1


def test_election_steps_down_without_quorum():
    n = DistributedConsensus("N", ["X", "Y"], quorum=2)

    async def deny(peer, term):
        return False  # no peer votes → only self-vote (1) < quorum

    n._request_peer_vote = deny
    asyncio.run(n._become_candidate())
    assert n.role == NodeRole.FOLLOWER
