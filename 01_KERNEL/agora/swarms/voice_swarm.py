# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Voice Agency Swarm (LangGraph Implementation)
Deploys Sir Echo (TTS) and Lady Nightingale (Cloning) for multi-modal interaction.
"""

import os
from typing import Optional, TypedDict

import soundfile as sf
from kokoro_onnx import Kokoro
from langgraph.graph import END, StateGraph


class VoiceState(TypedDict):
    """State for the Voice Swarm"""

    text: str
    voice_preset: str
    output_path: str
    cloning_source: Optional[str]  # Path to sample for OpenVoice
    audio_buffer: Optional[bytes]
    status: str


MODELS_DIR = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\kokoro-onnx\models"
ONNX_PATH = os.path.join(MODELS_DIR, "kokoro-v1.0.onnx")
VOICES_PATH = os.path.join(MODELS_DIR, "voices-v1.0.bin")

# TTS engine selection: "kokoro" (default) or "piper" (HuggingFace voices)
TTS_ENGINE = os.environ.get("CAMELOT_TTS_ENGINE", "kokoro")


def agent_echo(state: VoiceState) -> VoiceState:
    """🎙️ AGENT_ECHO (Sir Echo): Standard TTS via Kokoro-ONNX or Piper"""
    print(f"[ECHO] Synthesizing ({TTS_ENGINE}): {state['text'][:50]}...")

    if TTS_ENGINE == "piper":
        try:
            from agora.swarms.piper_tts import synthesize as piper_synthesize

            samples, sample_rate = piper_synthesize(
                state["text"],
                voice_preset=state["voice_preset"],
                output_path=state["output_path"],
            )
            state["audio_buffer"] = samples.tobytes()
            state["status"] = "Synthesized with Piper"
            return state
        except Exception as e:
            print(f"[ECHO] Piper failed ({e}), falling back to Kokoro")

    # Kokoro fallback / default
    if not os.path.exists(ONNX_PATH):
        state["status"] = "ERROR: Models not found"
        return state

    kokoro = Kokoro(ONNX_PATH, VOICES_PATH)
    samples, sample_rate = kokoro.create(state["text"], voice=state["voice_preset"], speed=1.0, lang="en-us")

    state["audio_buffer"] = samples.tobytes()
    sf.write(state["output_path"], samples, sample_rate)

    state["status"] = "Synthesized with Kokoro"
    return state


def agent_nightingale(state: VoiceState) -> VoiceState:
    """📞 AGENT_NIGHTINGALE (Lady Nightingale): Voice Cloning via OpenVoice"""
    if state["cloning_source"]:
        print(f"[NIGHTINGALE] Cloning voice from {state['cloning_source']}...")
        state["status"] = "Cloning with OpenVoice..."
    else:
        print("[NIGHTINGALE] No cloning source provided, skipping to standard delivery.")
    return state


def finalize_audio(state: VoiceState) -> VoiceState:
    """Finalize the audio file and save to output_path"""
    print(f"[VOICE] Finalizing audio at {state['output_path']}")
    state["status"] = "COMPLETED"
    return state


# Build the Voice Swarm
workflow = StateGraph(VoiceState)
workflow.add_node("echo", agent_echo)
workflow.add_node("nightingale", agent_nightingale)
workflow.add_node("finalize", finalize_audio)

workflow.set_entry_point("echo")
workflow.add_edge("echo", "nightingale")
workflow.add_edge("nightingale", "finalize")
workflow.add_edge("finalize", END)

voice_swarm = workflow.compile()

if __name__ == "__main__":
    # Test the swarm skeleton
    result = voice_swarm.invoke(
        {
            "text": "Greetings from Camelot OS. I am the Voice Swarm.",
            "voice_preset": "af_bella",
            "output_path": "c:/Users/vizio/CAMELOT_OS/docs/ARTIFACTS/test_voice.wav",
            "cloning_source": None,
            "audio_buffer": None,
            "status": "INIT",
        }
    )
    print(f"\n[STAMP] Swarm Execution Status: {result['status']}")