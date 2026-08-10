# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
KBA Tools — KickBox Audio services for the Camelot-OS drone node
================================================================
Governed tools a KBA drone exposes through the bifrost→sandbox bridge. Each tool
is REAL wiring with HONEST degradation: on a provisioned drone the voice backends
(piper TTS, a transcription engine) are present and the tool does real work; on a
box without them, the tool returns a clear ``available: false`` rather than faking
output. Nothing here fabricates audio it did not produce.

Register them onto a ToolRegistry:

    from cartridge.tool_registry import ToolRegistry
    from cartridge.kba_tools import register_kba_tools, KBA_TOOL_IDS
    reg = ToolRegistry(with_builtins=True)
    register_kba_tools(reg)

The KBA cartridge manifest must list these ids in ``allowed_tools`` for the sandbox
to permit them.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

KBA_TOOL_IDS = ["kba.status", "kba.echo", "kba.tts", "kba.transcribe", "kba.voices"]


def _backends() -> Dict[str, bool]:
    """Detect which KBA voice backends are actually available on this host."""
    return {
        "piper_tts": shutil.which("piper") is not None,
        "whisper": shutil.which("whisper") is not None or shutil.which("whisper-cli") is not None,
        "ffmpeg": shutil.which("ffmpeg") is not None,
    }


def _kba_status(_params: Dict[str, Any]) -> Dict[str, Any]:
    b = _backends()
    return {
        "service": "KickBox Audio",
        "time": datetime.now(timezone.utc).isoformat(),
        "backends": b,
        "ready": b["piper_tts"] or b["whisper"],
    }


def _kba_echo(params: Dict[str, Any]) -> Dict[str, Any]:
    """Roundtrip / liveness probe for the KBA drone."""
    return {"pong": params.get("value", ""), "at": datetime.now(timezone.utc).isoformat()}


def _kba_voices(_params: Dict[str, Any]) -> Dict[str, Any]:
    """List installed piper voice models (*.onnx), honestly empty if none present."""
    voices: list[str] = []
    for root in (Path.home() / ".local/share/piper", Path("/opt/piper/voices"),
                 Path.home() / "piper_voices"):
        if root.is_dir():
            voices += [p.stem for p in root.glob("*.onnx")]
    return {"voices": sorted(set(voices)), "backend_present": _backends()["piper_tts"]}


def _kba_tts(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize speech with piper if available. Returns the output wav path.
    Requires params: {"text": str, optional "voice": model path, "out": path}.
    """
    text = str(params.get("text", "")).strip()
    if not text:
        raise ValueError("kba.tts: 'text' is required")
    if not _backends()["piper_tts"]:
        return {"available": False, "reason": "piper backend not installed on this drone"}

    out = params.get("out") or str(Path(tempfile.gettempdir()) / f"kba_tts_{int(datetime.now().timestamp())}.wav")
    cmd = ["piper", "--output_file", out]
    voice = params.get("voice")
    if voice:
        cmd += ["--model", str(voice)]
    try:
        subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True,
                       timeout=30, check=True, shell=False)
        return {"available": True, "engine": "piper", "audio_path": out,
                "chars": len(text)}
    except (subprocess.SubprocessError, OSError) as e:
        return {"available": True, "engine": "piper", "error": f"synthesis failed: {e}"}


def _kba_transcribe(params: Dict[str, Any]) -> Dict[str, Any]:
    """Transcribe an audio file with a whisper CLI if available (honest fallback)."""
    audio = params.get("audio_path")
    if not audio:
        raise ValueError("kba.transcribe: 'audio_path' is required")
    if not Path(str(audio)).exists():
        return {"available": True, "error": f"audio not found: {audio}"}
    engine = shutil.which("whisper-cli") or shutil.which("whisper")
    if not engine:
        return {"available": False, "reason": "no whisper backend installed on this drone"}
    try:
        res = subprocess.run([engine, str(audio), "--output_format", "txt"],
                             capture_output=True, text=True, timeout=120, shell=False)
        return {"available": True, "engine": Path(engine).stem,
                "stdout": res.stdout[-2000:], "returncode": res.returncode}
    except (subprocess.SubprocessError, OSError) as e:
        return {"available": True, "error": f"transcription failed: {e}"}


def register_kba_tools(registry: Any) -> list[str]:
    """Register all KBA tools onto a ToolRegistry. Returns the registered ids."""
    registry.register("kba.status", _kba_status)
    registry.register("kba.echo", _kba_echo)
    registry.register("kba.tts", _kba_tts)
    registry.register("kba.transcribe", _kba_transcribe)
    registry.register("kba.voices", _kba_voices)
    return list(KBA_TOOL_IDS)


if __name__ == "__main__":
    import json

    from cartridge.tool_registry import ToolRegistry
    r = ToolRegistry()
    register_kba_tools(r)
    print("KBA tools:", r.tool_ids)
    print("status ->", json.dumps(r.executor("kba.status", {})["data"], indent=2))
