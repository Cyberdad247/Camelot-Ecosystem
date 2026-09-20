# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from control_plane.audio.s26_audio_bridge import S26AudioBridgeEngine


def test_s26_audio_bridge_session_and_streaming():
    engine = S26AudioBridgeEngine(node_id="vashawns-s26-ultra")
    
    # 1. Start full-duplex session
    session = engine.start_session("sess_test_001")
    assert session.status == "STREAMING"
    assert session.average_latency_ms < 50.0
    
    # 2. Process incoming voice frame (sub-50ms)
    raw_audio = b"\x00\x01\x02\x03" * 240
    packet = engine.process_incoming_frame(
        session_id="sess_test_001",
        sequence_num=1,
        raw_pcm_bytes=raw_audio,
        is_vad_active=True,
        is_barge_in=False,
        simulated_latency_ms=22.4
    )
    
    assert packet.packet_id == "pkt_sess_test_001_1"
    assert packet.codec == "opus"
    assert packet.latency_glass_to_ear_ms == 22.4
    assert len(packet.checksum) == 16
    
    # 3. Process Barge-In Interruption frame
    barge_packet = engine.process_incoming_frame(
        session_id="sess_test_001",
        sequence_num=2,
        raw_pcm_bytes=raw_audio,
        is_vad_active=True,
        is_barge_in=True,
        simulated_latency_ms=18.5
    )
    
    assert barge_packet.is_barge_in is True
    assert engine.sessions["sess_test_001"].barge_in_count == 1
    assert engine.sessions["sess_test_001"].status == "INTERRUPTED"
    
    # 4. Close Session
    closed = engine.close_session("sess_test_001")
    assert closed.status == "CLOSED"
    assert closed.packets_received == 2
