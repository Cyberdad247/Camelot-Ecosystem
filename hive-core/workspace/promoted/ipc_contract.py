
# SPDX-License-Identifier: MIT
"""Sir Boris Crucible Contract: Zero-Copy IPC Invariants."""
from typing import Final, NamedTuple

MAX_PAYLOAD_BYTES: Final[int] = 262144
COW_CEILING_MIB: Final[float] = 0.12

class IPCPacket(NamedTuple):
    channel_id: str
    sequence_no: int
    payload_size: int
    is_zero_copy: bool

def validate_packet(packet: IPCPacket) -> bool:
    if packet.payload_size > MAX_PAYLOAD_BYTES:
        return False
    return packet.is_zero_copy
