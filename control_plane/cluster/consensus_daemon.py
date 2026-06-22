"""
HTTP daemon wrapper for DistributedConsensus.

Replaces the stubbed in-process ``_send_message`` (which only put messages on a
local queue that nothing drained) with real HTTP delivery to peers'
``/consensus/message`` endpoint. That is the single change needed to turn the
PBFT algorithm into a cluster that actually reaches agreement across processes.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List

from control_plane.distributed_ledger_consensus import (
    ConsensusMessage,
    ConsensusPhase,
    DistributedConsensus,
    NodeRole,
)

from .http_daemon import HttpDaemon, call_async, fire_async, post_json
from control_plane.observability import traced_op


class HttpConsensusNode(DistributedConsensus):
    """DistributedConsensus that delivers protocol messages over HTTP."""

    def __init__(
        self,
        node_id: str,
        peers: List[str],
        peer_addrs: Dict[str, str],
        loop: asyncio.AbstractEventLoop,
        quorum: int = 2,
        is_leader: bool = False,
    ) -> None:
        super().__init__(node_id, peers, quorum=quorum)
        self.peer_addrs = peer_addrs  # node_id -> base URL (http://host:port)
        self._loop = loop
        if is_leader:
            self.role = NodeRole.LEADER
            self.leader_id = node_id

    async def _send_message(self, peer: str, message: ConsensusMessage) -> None:
        """Override: deliver to peer over HTTP instead of a dead local queue."""
        base = self.peer_addrs.get(peer)
        if not base:
            return
        url = f"{base}/consensus/message"
        payload = {
            "node_id": message.node_id,
            "phase": message.phase.value,
            "entry_id": message.entry_id,
            "sequence": message.sequence,
            "timestamp": message.timestamp,
            "data": message.data,
            "signature": message.signature,
        }
        # Fire-and-forget so a slow/down peer never stalls the broadcast loop,
        # but retry delivery: BFT cannot complete if a protocol message is lost.
        self._loop.run_in_executor(
            None, lambda: post_json(url, payload, timeout=2.0, retries=3)
        )


def _msg_from_body(body: dict) -> ConsensusMessage:
    return ConsensusMessage(
        node_id=body["node_id"],
        phase=ConsensusPhase(body["phase"]),
        entry_id=body["entry_id"],
        sequence=int(body["sequence"]),
        timestamp=float(body["timestamp"]),
        data=body.get("data", {}),
        signature=body.get("signature", ""),
    )


def register_routes(daemon: HttpDaemon, node: HttpConsensusNode) -> None:
    def consensus_message(body: dict, loop):
        msg = _msg_from_body(body)
        fire_async(loop, node.receive_message(msg))
        return 202, {"accepted": True}

    def consensus_propose(body: dict, loop):
        entry = body.get("entry", body)
        entry_id = call_async(loop, node.propose_entry(entry))
        return 200, {"entry_id": entry_id, "leader": node.role.value == "leader"}

    def consensus_status(body: dict, loop):
        return 200, node.get_status()

    daemon.route("POST", "/consensus/message", traced_op("consensus.message")(consensus_message))
    daemon.route("POST", "/consensus/propose", traced_op("consensus.propose")(consensus_propose))
    daemon.route("GET", "/consensus/status", consensus_status)
