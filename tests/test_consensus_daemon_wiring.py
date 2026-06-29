# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""Phase 4 daemon wiring — real HTTP key exchange + RequestVote across two nodes."""
import asyncio
import socket

import pytest

pytest.importorskip("cryptography")
pytest.importorskip("prometheus_client")

from control_plane.cluster.consensus_daemon import (  # noqa: E402
    HttpConsensusNode,
    register_routes,
)
from control_plane.cluster.http_daemon import HttpDaemon  # noqa: E402
from control_plane.distributed_ledger_consensus import (  # noqa: E402
    ConsensusMessage,
    ConsensusPhase,
)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_two_node_key_exchange_strict_and_requestvote():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    pa, pb = _free_port(), _free_port()
    a = HttpConsensusNode("A", ["B"], {"B": f"http://127.0.0.1:{pb}"}, loop, quorum=2)
    b = HttpConsensusNode("B", ["A"], {"A": f"http://127.0.0.1:{pa}"}, loop, quorum=2)
    da, db = HttpDaemon("127.0.0.1", pa, loop), HttpDaemon("127.0.0.1", pb, loop)
    register_routes(da, a)
    register_routes(db, b)
    da.start()
    db.start()
    try:
        # Key exchange over HTTP → both flip strict_signatures on.
        loop.run_until_complete(
            asyncio.gather(
                a.bootstrap_keys(attempts=10, delay=0.1),
                b.bootstrap_keys(attempts=10, delay=0.1),
            )
        )
        assert a.strict_signatures and b.strict_signatures
        assert "B" in a._public_keys and "A" in b._public_keys

        # A signs a message; B verifies it under strict mode (real Ed25519).
        m = ConsensusMessage(
            node_id="A", phase=list(ConsensusPhase)[0], entry_id="e1",
            sequence=1, timestamp=1.0, data={"k": 1},
        )
        m.signature = a._sign_message(m.to_json())
        assert b._verify_signature(m) is True

        # RequestVote RPC: A asks B for a vote in term 5 → granted.
        granted = loop.run_until_complete(a._request_peer_vote("B", term=5))
        assert granted is True
        assert b.current_term == 5 and b.voted_for == "A"
    finally:
        da.stop()
        db.stop()
        loop.close()
