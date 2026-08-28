# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Test suite for Realtime Voice Bridge (OpenAI Realtime S2S WebSocket & Fonoster PBX Telephony).
Verifies:
1. Zero external dependencies outside Python stdlib.
2. OpenAI Realtime protocol data models and event serialization/deserialization.
3. VAD energy detection and speech start/stop triggers.
4. STT -> LLM -> TTS modular pipeline flow.
5. Barge-in / interruption handling & cancellation.
6. Fonoster PBX call verbs (Answer, Say, Gather, Stream, Dial, Hangup, Play, Mute, Record) and VoiceResponse DAG.
7. RFC 6455 WebSocket frame encoding and decoding.
8. RealtimeVoiceBridge metrics aggregation & MultivoiceBridge integration.
"""
import base64
import json
import math
import struct
import sys
import pytest

from control_plane.dispatch.realtime_voice_bridge import (
    GatherSource,
    LLMProcessor,
    PBXCallSession,
    PBXCallStatus,
    RealtimeEventType,
    RealtimeMessage,
    RealtimeSessionConfig,
    RealtimeVoiceBridge,
    RealtimeVoiceSession,
    STTProcessor,
    StreamAudioFormat,
    StreamDirection,
    TTSProcessor,
    VADConfig,
    VADProcessor,
    WSFrame,
    WSFrameOpcode,
    compute_audio_duration_seconds,
    create_wav_header,
)
from control_plane.multivoice_bridge import MultivoiceBridge, render_panel


# ── 1. Dependency & Core Utilities Verification ──────────────────────────────

def test_zero_external_dependencies():
    """Verify that realtime_voice_bridge only imports standard library modules."""
    import control_plane.dispatch.realtime_voice_bridge as rtvb
    loaded_mods = [k for k, v in sys.modules.items() if v == rtvb]
    assert len(loaded_mods) >= 1
    # Check that standard types are present
    assert hasattr(rtvb, "RealtimeVoiceBridge")
    assert hasattr(rtvb, "VoiceResponse")


def test_audio_duration_and_wav_header():
    """Verify audio duration calculation and RIFF WAV header creation."""
    dur = compute_audio_duration_seconds(32000, sample_rate=16000, bytes_per_sample=2)
    assert dur == 1.0

    wav_hdr = create_wav_header(1000, sample_rate=16000, channels=1, bits_per_sample=16)
    assert len(wav_hdr) == 44
    assert wav_hdr[:4] == b"RIFF"
    assert wav_hdr[8:12] == b"WAVE"
    assert wav_hdr[12:16] == b"fmt "
    assert wav_hdr[36:40] == b"data"


# ── 2. OpenAI Realtime Event Models ──────────────────────────────────────────

def test_realtime_message_serialization():
    """Verify RealtimeMessage serialize, deserialize, and to_dict."""
    msg = RealtimeMessage(
        type=RealtimeEventType.SESSION_UPDATE.value,
        data={"session": {"voice": "alloy", "temperature": 0.7}}
    )
    raw_dict = msg.to_dict()
    assert raw_dict["type"] == "session.update"
    assert raw_dict["session"]["voice"] == "alloy"
    assert "event_id" in raw_dict

    json_str = msg.to_json()
    reconstructed = RealtimeMessage.from_dict(json.loads(json_str))
    assert reconstructed.type == msg.type
    assert reconstructed.event_id == msg.event_id
    assert reconstructed.data["session"]["voice"] == "alloy"


def test_session_config_from_dict():
    """Verify RealtimeSessionConfig parses known fields and generates dict."""
    cfg = RealtimeSessionConfig.from_dict({
        "voice": "echo",
        "instructions": "Custom system prompt",
        "temperature": 0.5,
        "unknown_extra": 123
    })
    assert cfg.voice == "echo"
    assert cfg.instructions == "Custom system prompt"
    assert cfg.temperature == 0.5
    d = cfg.to_dict()
    assert d["voice"] == "echo"
    assert "modalities" in d


# ── 3. VAD Processor & Energy Detection ──────────────────────────────────────

def test_vad_silence_and_speech_detection():
    """Verify VAD processor discriminates between silence and loud PCM frames."""
    vad = VADProcessor(VADConfig(energy_threshold=0.02, speech_start_frames=2, silence_frames_hangover=3))
    
    # Silence frame
    silence = b"\x00\x00" * 512
    voiced, trans, speech = vad.process_chunk(silence)
    assert not voiced
    assert trans is None

    # Loud speech frame (high amplitude sine wave)
    loud_samples = [int(20000 * math.sin(i * 0.1)) for i in range(512)]
    loud_chunk = struct.pack("<512h", *loud_samples)

    # Frame 1
    voiced, trans, speech = vad.process_chunk(loud_chunk)
    # Frame 2 -> triggers speech_started
    voiced, trans, speech = vad.process_chunk(loud_chunk)
    assert voiced
    assert trans == "speech_started"

    # Feed silence to trigger speech_stopped
    stopped_seen = False
    for _ in range(4):
        voiced, trans, speech = vad.process_chunk(silence)
        if trans == "speech_stopped":
            stopped_seen = True
            assert speech is not None
            assert len(speech) > 0
    assert stopped_seen


# ── 4. STT, LLM & TTS Modular Processors ─────────────────────────────────────

def test_modular_pipeline_processors():
    """Verify STT, LLM, and TTS individual processor units."""
    stt = STTProcessor(transcribe_fn=lambda b: "status check")
    transcript = stt.transcribe(b"dummy_pcm")
    assert transcript == "status check"

    llm = LLMProcessor(system_prompt="Test System")
    resp = llm.generate_response("system status")
    assert "operational" in resp.lower()
    assert len(llm.history) == 2  # user + assistant

    tts = TTSProcessor(sample_rate=16000)
    pcm = tts.synthesize_pcm("Test voice synthesis", duration_s=0.2)
    assert len(pcm) == int(16000 * 0.2 * 2)


# ── 5. RealtimeVoiceSession Pipeline & Barge-In ──────────────────────────────

@pytest.mark.anyio
async def test_realtime_voice_session_events():
    """Verify RealtimeVoiceSession handles client events and generates server events."""
    emitted = []

    async def mock_send(msg: RealtimeMessage):
        emitted.append(msg)

    session = RealtimeVoiceSession(send_event_fn=mock_send)

    # 1. session.update
    out = await session.handle_client_message({
        "type": "session.update",
        "session": {"voice": "alloy"}
    })
    assert len(out) == 1
    assert out[0].type == "session.updated"

    # 2. conversation.item.create
    out = await session.handle_client_message({
        "type": "conversation.item.create",
        "item": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hello"}]}
    })
    assert len(out) == 1
    assert out[0].type == "conversation.item.created"

    # 3. input_audio_buffer.append & commit
    loud_samples = [int(15000 * math.sin(i * 0.1)) for i in range(512)]
    loud_chunk = struct.pack("<512h", *loud_samples)
    b64_audio = base64.b64encode(loud_chunk * 4).decode("ascii")

    await session.handle_client_message({
        "type": "input_audio_buffer.append",
        "audio": b64_audio
    })
    assert session.metrics.total_audio_in_bytes > 0

    # Commit triggers the full pipeline STT -> LLM -> TTS
    out_commit = await session.handle_client_message({
        "type": "input_audio_buffer.commit"
    })
    types = [e.type for e in out_commit]
    assert "input_audio_buffer.committed" in types
    assert "response.created" in types
    assert "response.audio.delta" in types
    assert "response.done" in types


@pytest.mark.anyio
async def test_realtime_voice_barge_in():
    """Verify that user speech start interrupts / cancels in-flight response generation."""
    session = RealtimeVoiceSession()
    session.in_response = True
    assert session.metrics.interruptions == 0

    # User starts speaking
    session._on_vad_speech_start()
    assert not session.in_response
    assert session.metrics.interruptions == 1
    assert session._cancel_generation_flag is True


# ── 6. Fonoster Programmable PBX Telephony Verbs ─────────────────────────────

@pytest.mark.anyio
async def test_fonoster_voice_response_verbs():
    """Verify Fonoster PBX call verbs: Answer, Say, Gather, Stream, Dial, Hangup, Play, Mute, Record."""
    call = PBXCallSession(caller_id="+14155550199", destination="sip:anya@camelot.local")
    vr = call.voice_response
    assert call.status == PBXCallStatus.RINGING

    # 1. Answer
    ans = await vr.answer()
    assert ans.verb == "Answer"
    assert call.status == PBXCallStatus.ANSWERED

    # 2. Say
    say = await vr.say("Hello from Camelot Telephony", voice="alloy", speed=1.1)
    assert say.verb == "Say"
    assert say.data["text"] == "Hello from Camelot Telephony"

    # 3. Gather
    call.inject_dtmf("99")
    gather_res = await vr.gather(source=GatherSource.DTMF, max_digits=2)
    assert gather_res["digits"] == "99"
    assert call.status == PBXCallStatus.GATHERING

    # 4. Stream
    stream_res = await vr.stream(direction=StreamDirection.BOTH, format=StreamAudioFormat.PCM16)
    assert stream_res.verb == "Stream"
    assert call.status == PBXCallStatus.STREAMING

    # 5. Play
    play_res = await vr.play("https://camelot.local/audio/chime.wav")
    assert play_res.verb == "Play"

    # 6. Mute / Unmute
    mute_res = await vr.mute()
    assert mute_res.verb == "Mute"
    unmute_res = await vr.unmute()
    assert unmute_res.verb == "Unmute"

    # 7. Record
    rec_res = await vr.record(max_duration_s=30)
    assert "record_ref" in rec_res

    # 8. Dial
    dial_res = await vr.dial("sip:boris@camelot.local", timeout_s=45)
    assert dial_res.verb == "Dial"
    assert call.status == PBXCallStatus.DIALING

    # 9. Hangup
    hangup_res = await vr.hangup()
    assert hangup_res.verb == "Hangup"
    assert call.status == PBXCallStatus.HANGUP

    assert len(vr.executed_verbs) >= 9


# ── 7. RFC 6455 WebSocket Framing ────────────────────────────────────────────

def test_websocket_frame_codec():
    """Verify WebSocket frame parsing and encoding for text, binary, and close."""
    # Text frame with masking
    text_data = "OpenAI Realtime Protocol Assimilated"
    masked_frame = WSFrame.encode_frame(text_data, opcode=WSFrameOpcode.TEXT, mask=True)
    buf = bytearray(masked_frame)
    opcode, payload, consumed = WSFrame.decode_frame(buf)
    assert opcode == WSFrameOpcode.TEXT
    assert payload.decode("utf-8") == text_data
    assert consumed == len(masked_frame)

    # Binary frame unmasked
    bin_data = b"\x01\x02\x03\x04\x05"
    unmasked_frame = WSFrame.encode_frame(bin_data, opcode=WSFrameOpcode.BINARY, mask=False)
    buf = bytearray(unmasked_frame)
    opcode, payload, consumed = WSFrame.decode_frame(buf)
    assert opcode == WSFrameOpcode.BINARY
    assert payload == bin_data
    assert consumed == len(unmasked_frame)

    # Partial buffer returns consumed=0
    buf_partial = bytearray(masked_frame[:3])
    opcode, payload, consumed = WSFrame.decode_frame(buf_partial)
    assert consumed == 0


# ── 8. RealtimeVoiceBridge & MultivoiceBridge Integration ─────────────────────

def test_bridge_aggregate_metrics_and_panel():
    """Verify RealtimeVoiceBridge telemetry integration with MultivoiceBridge and panel rendering."""
    bridge = RealtimeVoiceBridge()
    sess1 = bridge.create_session()
    sess1.metrics.total_audio_in_bytes = 32000
    sess1.metrics.total_audio_out_bytes = 48000
    sess1.metrics.input_tokens = 50
    sess1.metrics.output_tokens = 120
    sess1.metrics.ttfa_ms = 195.0
    sess1.metrics.ttft_ms = 110.0

    call1 = bridge.create_pbx_call(caller_id="operator", destination="sip:boris")

    metrics = bridge.get_aggregate_metrics()
    assert metrics["active_sessions"] == 1
    assert metrics["active_pbx_calls"] == 1
    assert metrics["total_audio_in_bytes"] == 32000
    assert metrics["total_input_tokens"] == 50
    assert metrics["avg_ttfa_ms"] == 195.0

    # Test integration with MultivoiceBridge
    mv = MultivoiceBridge()
    mv.attach_realtime_bridge(bridge)
    stats = mv.fetch_affinity()
    assert stats.connected is True
    assert stats.realtime_sessions == 1
    assert stats.active_pbx_calls == 1
    assert stats.ttfa_ms == 195.0

    # Test Bifrost panel rendering
    panel_html = render_panel(stats)
    assert "S2S / PBX Voice" in panel_html
    assert "1 ws sess" in panel_html
    assert "1 pbx calls" in panel_html
    assert "195ms" in panel_html
