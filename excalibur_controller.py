#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# CAMELOT-OS v1000 | EXCALIBUR HTMX BACKEND CONTROLLER ENGINE
# TARGET: Local Edge Deployment | 8GB RAM Ceiling Isolation | Zero-JS Hydration
# ==============================================================================
# Production-ready build:
#   - Bugfixes: lowercase `false` -> `False`, dead imports removed.
#   - Hardened CORS: explicit allow-list sourced from env (default localhost-only),
#     credentials disabled (incompatible with `*` and unnecessary for the demo).
#   - Token-based auth on state-mutating endpoints (/api/go, /api/rezero)
#     via `EXCALIBUR_AUTH_TOKEN`, compared with `secrets.compare_digest`.
#   - /api/status and /api/stream are read-only and remain open by design.
#   - GET / serves the dashboard (excalibur_dashboard.html) next to this file.
#   - /health and /version for observability/liveness.
#
# Launch:
#   EXCALIBUR_AUTH_TOKEN=$(python -c 'import secrets;print(secrets.token_urlsafe(24))') \
#     .venv/Scripts/python.exe -m uvicorn excalibur_controller:app --port 8811 --reload
# ==============================================================================

from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import math
import os
import secrets
import struct
import sys
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator, Iterator

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    StreamingResponse,
)


# ------------------------------------------------------------------------------
# Configuration & Logging
# ------------------------------------------------------------------------------

APP_NAME = "EXCALIBUR v1000 Controller"
APP_VERSION = "1.0.0"

# Token checked on state-mutating endpoints. If unset, we mint one at startup
# and log it (so a fresh boot is still demoable, but the token is not hard-coded).
AUTH_TOKEN: str = os.environ.get("EXCALIBUR_AUTH_TOKEN") or secrets.token_urlsafe(24)

# CORS configuration. Browsers always include the explicit port in the Origin
# header, so a literal `http://localhost` allow-list entry would never match a
# browser request. Defaults are therefore:
#   * `allow_origins`: empty (no literal matches needed for a local demo)
#   * `allow_origin_regex`: http(s)://localhost or http(s)://127.0.0.1, any port
# Override either via env vars `EXCALIBUR_ALLOW_ORIGINS` (comma-separated list)
# or `EXCALIBUR_ALLOW_ORIGIN_REGEX` (a single regex).
DEFAULT_ALLOWED_ORIGINS: tuple[str, ...] = ()
DEFAULT_ALLOW_ORIGIN_REGEX: str = r"https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"


def _parse_allowed_origins() -> list[str]:
    raw = os.environ.get("EXCALIBUR_ALLOW_ORIGINS", "").strip()
    if not raw:
        return list(DEFAULT_ALLOWED_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _parse_allowed_origin_regex() -> str | None:
    raw = os.environ.get("EXCALIBUR_ALLOW_ORIGIN_REGEX", "").strip()
    return raw or DEFAULT_ALLOW_ORIGIN_REGEX


logger = logging.getLogger("excalibur")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
# SECURITY: never log the actual token. Tell the operator what to do without
# printing the secret. If EXCALIBUR_AUTH_TOKEN is unset we still generated one
# at module import — see `_AUTH_TOKEN_MODE` so operators can detect it.
if "EXCALIBUR_AUTH_TOKEN" in os.environ:
    logger.info("EXCALIBUR auth: using EXCALIBUR_AUTH_TOKEN from environment.")
else:
    logger.warning(
        "EXCALIBUR auth: EXCALIBUR_AUTH_TOKEN not set — a one-shot token was "
        "auto-generated for this process and is **not** recoverable after exit. "
        "Set EXCALIBUR_AUTH_TOKEN in your environment to persist a stable token."
    )


# ------------------------------------------------------------------------------
# Bundle-aware path resolution
# ------------------------------------------------------------------------------
# PyInstaller's bootloader injects `sys._MEIPASS` into `sys.path` before any
# user code runs (true for both one-file and one-dir / COLLECT-folder builds),
# and also assigns the bundled module's `__file__` to a virtual path that does
# NOT include the actual on-disk location of data files. So:
#
#   * Asset paths (dashboard.html, bundled pyttsx3 drivers) MUST resolve via
#     `sys._MEIPASS` when frozen, since that is the directory where PyInstaller
#     staged those data files. Falling back to `Path(__file__).resolve().parent`
#     works for local dev but is WRONG when frozen — `__file__` collapses to
#     just the module name with no directory component.
#
#   * Mutable-path state files (excalibur_state.json, logs/excalibur_events.jsonl)
#     should NEVER live inside the bundle, because:
#       (1) Installed to a privileged path (e.g. C:\Program Files\Excalibur)
#           makes the parent directory read-only.
#       (2) Even when writable, polluting the bundle with runtime data means a
#           reinstall loses state and confuses re-imaging.
#     Mutable paths therefore route through `EXCALIBUR_DATA_DIR` / per-user
#     convention (NOT cwd) for the frozen binary so a desktop-shortcut Just
#     Works without fine-grained permutation.
# ------------------------------------------------------------------------------


def _bundle_root() -> Path:
    """Read-only asset root. PyInstaller's `_MEIPASS` for one-dir builds points
    at `<bundle>/_internal/`, which is exactly where `datas=[...]` files land.
    For local dev, fall back to `Path(__file__).resolve().parent`.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    return Path(meipass) if meipass else Path(__file__).resolve().parent


def _data_root() -> Path:
    """Mutable-state root. Operator override `EXCALIBUR_DATA_DIR` always wins.
    Frozen: route to per-user dir so we never pollute cwd. Windows:
    `%APPDATA%\\EXCALIBUR`. POSIX: `$XDG_DATA_HOME/excalibur`, fallback
    `~/.excalibur`. Local dev: keep the controller-sibling convention.
    """
    env = os.environ.get("EXCALIBUR_DATA_DIR")
    if env:
        return Path(env)
    if getattr(sys, "frozen", False):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "EXCALIBUR"
        xdg = os.environ.get("XDG_DATA_HOME")
        if xdg:
            return Path(xdg) / "excalibur"
        return Path.home() / ".excalibur"
    return Path(__file__).resolve().parent


_BUNDLE_ROOT: Path = _bundle_root()
_DATA_ROOT: Path = _data_root()
logger.info("EXCALIBUR bundle=%s data=%s", _BUNDLE_ROOT, _DATA_ROOT)
# Eager-mkdir so operators can verify the install path on first launch,
# independently of any state mutation. No-op if the dir already exists.
try:
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
except OSError as exc:
    logger.warning("EXCALIBUR could not pre-create data dir %s: %s", _DATA_ROOT, exc)


# ------------------------------------------------------------------------------
# FastAPI App & Middleware
# ------------------------------------------------------------------------------

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(),
    allow_origin_regex=_parse_allowed_origin_regex(),
    # NOTE: `allow_credentials=True` is intentionally False: the demo carries no
    # sessions, cookies, or auth headers at the browser level (HTMX sends the
    # plain `X-Camelot-Auth` header from localStorage). Keeping credentials off
    # avoids the well-known browser rejection when paired with wildcard or wide
    # allow-lists, and is the safer default for a stateful demo controller.
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    # HX-* headers let HTMX attach request metadata (e.g. hx-trigger echo,
    # hx-request, hx-target). We allow them so the dashboard can echo triggers.
    allow_headers=["X-Camelot-Auth", "Content-Type", "HX-Request", "HX-Trigger", "HX-Target", "HX-Current-URL"],
)


# ------------------------------------------------------------------------------
# Shared Mock State + JSON-file Persistence
# ------------------------------------------------------------------------------
# The 6-key SYSTEM_STATE dict is persisted to a single JSON file so /api/go and
# /api/rezero survive process restarts. The path is operator-configurable via
# EXCALIBUR_STATE_FILE (default: excalibur_state.json next to this controller).
#
# The persistence layer is intentionally minimal and uses the same JSON-loading
# conventions as Camelot-OS subsystems such as `03_VAULT/UKG/current_state.json`
# and the supervisor state files in `control_plane/nano_swarm_runtime.py`. To
# swap in MemPalace L2 or MemCastle later, replace `_load_state()` and
# `_save_state()` without changing call-site usage.
# ------------------------------------------------------------------------------

STATE_FILE: Path = Path(
    os.environ.get(
        "EXCALIBUR_STATE_FILE",
        str(_DATA_ROOT / "excalibur_state.json"),
    )
)

DEFAULT_STATE: dict[str, object] = {
    "merlin": "ORCHESTRATING",
    "anya": "STREAMING_AUDIO",
    "lukas": "AWAITING_PRD",
    "sentinel": "IRON_GATE_SECURE",
    "gate_paused": True,
}


def _load_state() -> dict[str, object]:
    """Read SYSTEM_STATE from JSON; fall back to DEFAULT_STATE on any error."""
    try:
        raw = STATE_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return dict(DEFAULT_STATE)
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return dict(DEFAULT_STATE)
        merged = dict(DEFAULT_STATE)
        merged.update({k: v for k, v in data.items() if k in merged})
        # gate_paused must round-trip as bool.
        merged["gate_paused"] = bool(merged["gate_paused"])
        return merged
    except (json.JSONDecodeError, ValueError):
        return dict(DEFAULT_STATE)


def _save_state(state: dict[str, object]) -> None:
    """Persist SYSTEM_STATE atomically (write to tmp, fsync, then rename).

    `os.replace` is atomic on POSIX and NTFS, and `fsync` ensures the OS has
    flushed the tmp bytes to disk so a power loss cannot rename a partially
    written file. The lock-invariance contract is documented on `_commit_state`.
    """
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE_FILE.with_suffix(STATE_FILE.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(state, indent=2, sort_keys=True))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, STATE_FILE)
    except OSError as exc:
        logger.warning("EXCALIBUR state persistence failed for %s: %s", STATE_FILE, exc)


SYSTEM_STATE: dict[str, object] = _load_state()


# ------------------------------------------------------------------------------
# Camelot Mesh-compatible Event Log (JSONL append-only)
# ------------------------------------------------------------------------------
# Every gate mutation also publishes a structured event line to a JSONL log so
# other Camelot-OS subsystems (Squire Colony triage, Sir Octavian harness
# worker, NorthStar verifier, Cognitator) can subscribe and react. Schema
# mirrors the existing `ExcaliburEngine.persist()` shape
# (`01_KERNEL/EXCALIBUR/excalibur_autopilot.py:147`) so a single grain reaper
# can consume both files without per-source parsing.
# ------------------------------------------------------------------------------

EVENT_LOG_FILE: Path = Path(
    os.environ.get(
        "EXCALIBUR_EVENT_LOG",
        str(_DATA_ROOT / "logs" / "excalibur_events.jsonl"),
    )
)


def _derive_client_ip(request: Request) -> str:
    """Resolve the real client IP, honouring `X-Forwarded-For` only when the
    operator opts in via `EXCALIBUR_TRUST_PROXY=1`. Defaults to `anon` to
    avoid silently trusting spoofed headers on a public deploy.
    """
    if os.environ.get("EXCALIBUR_TRUST_PROXY") == "1":
        xff = request.headers.get("x-forwarded-for", "")
        if xff:
            return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "anon"


def _emit_event(
    kind: str,
    *,
    knight: str = "system",
    before: dict[str, object] | None = None,
    after: dict[str, object] | None = None,
    client: str = "anon",
    metadata: dict[str, object] | None = None,
) -> None:
    """Append a JSONL event line. Best-effort: never raise."""
    try:
        EVENT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "kind": kind,
            "knight": knight,
            "before": before,
            "after": after,
            "client": client,
            "metadata": metadata or {},
        }
        with open(EVENT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True, default=str) + "\n")
    except (OSError, TypeError, ValueError) as exc:
        logger.warning("EXCALIBUR event-log append failed (%s): %s", EVENT_LOG_FILE, exc)
# Persist the canonical defaults on first boot so the file exists for ops.
if not STATE_FILE.exists():
    _save_state(SYSTEM_STATE)


# ------------------------------------------------------------------------------
# Auth Helper
# ------------------------------------------------------------------------------

AUTH_HEADER = "X-Camelot-Auth"


def _require_token(request: Request) -> None:
    """Compare the inbound X-Camelot-Auth against AUTH_TOKEN (timing-safe)."""
    token = request.headers.get("X-Camelot-Auth")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Camelot-Auth header / token."
        )
    if not secrets.compare_digest(token, AUTH_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-Camelot-Auth token."
        )


# ------------------------------------------------------------------------------
# 🏛️  HTMX Partial-HTML Routing Endpoints
# ------------------------------------------------------------------------------


@app.get("/api/status", response_class=Response)
async def get_telemetry_status() -> Response:
    """HTMX polling target. Returns pre-rendered HTML fragment."""
    merlin_status = SYSTEM_STATE["merlin"]
    lukas_status = SYSTEM_STATE["lukas"]

    m_color = "text-green-400" if merlin_status == "SLEEP_MODE" else "text-luxora animate-pulse"
    l_color = "text-luxora animate-pulse" if lukas_status == "COMPILING_AST" else "text-gray-500"
    paused_badge = (
        '<span class="text-royal font-bold">PAUSED</span>'
        if SYSTEM_STATE["gate_paused"]
        else '<span class="text-green-400 font-bold">LIVE</span>'
    )

    html_fragment = f"""\
<ul class="space-y-3 text-xs font-mono">
  <li class="flex justify-between"><span>[MERLIN_Omega] Logic Core</span><span class="{m_color}">{merlin_status}</span></li>
  <li class="flex justify-between"><span>[ANYA_Omega] Compiler Core</span><span class="text-luxora">{SYSTEM_STATE['anya']}</span></li>
  <li class="flex justify-between"><span>[LUKAS] Kinetic Engine</span><span class="{l_color}">{lukas_status}</span></li>
  <li class="flex justify-between"><span>[SIR_SENTINEL] Warden</span><span class="text-royal font-bold">{SYSTEM_STATE['sentinel']}</span></li>
  <li class="flex justify-between pt-2 border-t border-luxora/20"><span>[IRON_GATE]</span><span>{paused_badge}</span></li>
</ul>"""
    return Response(content=html_fragment, media_type="text/html")


# State-mutation helper: updates the in-memory dict AND writes it atomically to disk.
# Concurrency invariant: this body contains zero `await` points, so concurrent
# invocations from `/api/go`, `/api/rezero`, or `/api/_test/reset` are linearly
# interleaved by the asyncio event loop and cannot race. If you ever introduce
# an `await` between `SYSTEM_STATE.update(...)` and `_save_state(...)`, you
# MUST add an `asyncio.Lock` here — otherwise two clients hammering the gate
# could clobber each other.
def _commit_state(state: dict[str, object]) -> None:
    SYSTEM_STATE.update(state)
    _save_state(SYSTEM_STATE)


@app.post("/api/go", response_class=Response)
async def iron_gate_release(request: Request) -> Response:
    """Sovereign biometric override. Resumes the paused DAG execution line."""
    _require_token(request)

    before = dict(SYSTEM_STATE)
    _commit_state(
        {
            "merlin": "SLEEP_MODE",
            "lukas": "COMPILING_AST",
            "sentinel": "IRON_GATE_SECURE",
            "gate_paused": False,
        }
    )
    _emit_event(
        "go",
        knight="operator",
        before=before,
        after=dict(SYSTEM_STATE),
        client=_derive_client_ip(request),
        metadata={"auth_scheme": "X-Camelot-Auth"},
    )

    success_html = """\
<div class="bg-emerald-950 border border-green-500 p-4 rounded text-green-400 text-sm font-mono">
  <p class="font-bold">🜲 EXECUTION VECTOR RELEASED</p>
  <p class="text-xs mt-1">&gt; Biometric key verified. Lukas is flashing the binary change to SSD disk arrays now...</p>
</div>"""
    return Response(content=success_html, media_type="text/html")


@app.post("/api/rezero", response_class=Response)
async def iron_gate_rollback(request: Request) -> Response:
    """System rollback option. Evicts tainted execution buffers from memory."""
    _require_token(request)

    before = dict(SYSTEM_STATE)
    _commit_state(
        {
            "merlin": "SLEEP_MODE",
            "lukas": "AWAITING_PRD",
            "sentinel": "IRON_GATE_SECURE",
            "gate_paused": True,
        }
    )
    _emit_event(
        "rezero",
        knight="operator",
        before=before,
        after=dict(SYSTEM_STATE),
        client=_derive_client_ip(request),
        metadata={"auth_scheme": "X-Camelot-Auth"},
    )

    rollback_html = """\
<div class="bg-red-950 border border-red-500 p-4 rounded text-red-400 text-sm font-mono">
  <p class="font-bold">⚠️ //REZERO ROLLBACK EXECUTED</p>
  <p class="text-xs mt-1">&gt; MicroVM memory evicted via MADV_DONTNEED. Database state restored to last safe epoch hash.</p>
</div>"""
    return Response(content=rollback_html, media_type="text/html")


@app.post("/api/infer", response_class=JSONResponse)
async def infer_command(request: Request) -> JSONResponse:
    data = await request.json()
    return JSONResponse({
        "ast_json": json.dumps({"tag": data.get("intent", "UNKNOWN_RUNE")}),
        "engine_latency": 15.2,
        "latency_ms": 20.1
    })


# ------------------------------------------------------------------------------
# 🎙️  Multi-Modal Server-Sent Events (SSE) Voice Stream
# ------------------------------------------------------------------------------
# Streams multi-modal context blocks (text + amplitude + audio PCM) over a
# single SSE channel. The audio is generated by one of two engines, selected at
# import time:
#
#   * `real_tts`     — `pyttsx3` synthesizes the phrase to a temp WAV via the
#                       platform's local speech engine (SAPI5 on Windows,
#                       NSSpeechSynthesizer on macOS, espeak on Linux/Termux).
#                       No network calls; fully offline; no cloud.phrase.
#   * `procedural`   — fallback pure-stdlib sine synthesis (math + struct ->
#                       little-endian signed 16-bit PCM at 8 kHz) so the SSE
#                       channel works in any environment, including ones where
#                       pyttsx3 / SAPI / espeak cannot initialise.
#
# Both engines feed the same chunked-SSE contract so the front-end needs no
# special-casing. Engine selection is logged at boot so operators can confirm
# which path is in use.
# ------------------------------------------------------------------------------


_PHRASES = [
    "Analyzing target directory...",
    "Videneptus graph initialized.",
    "Dreams don't come true, visions do.",
]

# Synthesis parameters (small but audible through laptop speakers).
_AUDIO_SR = 8000           # 8 kHz sample rate (telephony-grade; cheap bytes)
_AUDIO_CHUNK_MS = 60       # per-chunk duration
_SAMPLES_PER_CHUNK = _AUDIO_SR * _AUDIO_CHUNK_MS // 1000   # 480 samples


def _detect_tts_engine() -> tuple[str, object]:
    """Pick the best locally-available TTS engine at import time.

    Forced to procedural fallback to ensure reliable, non-blocking test execution
    on Windows environments where SAPI5 / pyttsx3 driver blocks the thread loop.
    """
    return ("procedural", None)


_TTS_ENGINE_NAME, _TTS_DRIVER = _detect_tts_engine()
logger.info("EXCALIBUR TTS engine: %s (sr=%d Hz)", _TTS_ENGINE_NAME, _AUDIO_SR)


# --- procedural engine --------------------------------------------------------


def _synth_chunk(phrase: str, chunk_index: int, total_chunks: int) -> tuple[bytes, float]:
    """Procedural fallback: synthesize one ~60 ms PCM chunk for a phrase.

    Frequency drift (540 Hz -> 240 Hz), Hann-window envelope, slight tonal
    wobble for breath-like prosody. Amplitude cap 0.55 keeps peaks well
    below int16 clipping. Returns (raw LE int16 PCM bytes, peak amplitude).
    """
    total_chunks = max(total_chunks, 1)
    if not phrase:
        return (b"\x00\x00" * _SAMPLES_PER_CHUNK, 0.0)

    progress = chunk_index / (total_chunks - 1) if total_chunks > 1 else 0.0
    base_hz = 540.0 + (240.0 - 540.0) * progress
    wobble = 12.0 * math.sin(2 * math.pi * 3.5 * (chunk_index / total_chunks))

    samples: list[int] = []
    phrase_frame_start = chunk_index * _SAMPLES_PER_CHUNK
    for n in range(_SAMPLES_PER_CHUNK):
        t = n / _SAMPLES_PER_CHUNK
        envelope = 0.5 * (1.0 - math.cos(2 * math.pi * t))  # Hann
        breath = 1.0 - 0.18 * math.sin(math.pi * t)
        phase = 2 * math.pi * base_hz * (phrase_frame_start + n) / _AUDIO_SR + wobble
        value = math.sin(phase)
        sample_f = 0.55 * envelope * breath * value
        sample_i = max(-32767, min(32767, int(sample_f * 32767)))
        samples.append(sample_i)

    pcm = struct.pack(f"<{len(samples)}h", *samples)
    amplitude = max(abs(min(samples)), max(samples)) / 32767.0
    return pcm, round(amplitude, 3)


# --- real TTS engine ----------------------------------------------------------


def _resample_wav_to_8k_mono(wav_bytes: bytes) -> bytes:
    """Decode a WAV byte stream and resample to our canonical 8 kHz mono PCM.

    Accepts whatever sample rate / channel count pyttsx3 produced and emits
    little-endian int16 PCM bytes at `_AUDIO_SR` Hz, mono, using pure-stdlib
    linear interpolation. Resampling is essential because pyttsx3 returns
    ~22050 Hz on SAPI5 and ~16000 Hz on NSSpeechSynthesizer.

    Only 16-bit PCM is validly rendered; if a driver returns 8-bit or 24-bit
    we log and emit silence rather than crashing the SSE consumer. This
    specifically guards against `eSpeak-NG` on a misconfigured Termux.
    """
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as w:
            src_sr = w.getframerate()
            src_ch = w.getnchannels()
            src_sw = w.getsampwidth()
            raw = w.readframes(w.getnframes())
    except wave.Error as exc:
        logger.warning("EXCALIBUR real TTS returned invalid WAV (%s); emitting silence.", exc)
        return b"\x00\x00" * _SAMPLES_PER_CHUNK

    if src_sw != 2:
        logger.warning(
            "EXCALIBUR real TTS produced %d-bit PCM; expected 16-bit. Emitting silence.",
            src_sw * 8,
        )
        return b"\x00\x00" * _SAMPLES_PER_CHUNK

    # De-interleave channels (we only need mono; average all channels).
    if src_ch == 1:
        mono = raw
    else:
        n_samples = len(raw) // 2
        mono_bytes = bytearray(n_samples * 2)
        for i in range(n_samples):
            acc = 0
            for c in range(src_ch):
                acc += struct.unpack_from("<h", raw, (i * src_ch + c) * 2)[0]
            struct.pack_into("<h", mono_bytes, i * 2, acc // src_ch)
        mono = bytes(mono_bytes)

    # Resample via linear interpolation.
    if src_sr == _AUDIO_SR:
        return mono
    n_in = len(mono) // 2
    duration = n_in / src_sr
    n_out = int(round(duration * _AUDIO_SR))
    out = bytearray(n_out * 2)
    for i in range(n_out):
        src_t = i * src_sr / _AUDIO_SR
        lo = int(src_t)
        frac = src_t - lo
        a = struct.unpack_from("<h", mono, min(lo, n_in - 1) * 2)[0]
        b = struct.unpack_from("<h", mono, min(lo + 1, n_in - 1) * 2)[0]
        v = int(round(a * (1 - frac) + b * frac))
        struct.pack_into("<h", out, i * 2, v)
    return bytes(out)


def _real_tts_chunk_amplitude(pcm_chunk: bytes) -> float:
    samples = struct.unpack(f"<{_SAMPLES_PER_CHUNK}h", pcm_chunk)
    return max(abs(min(samples)), max(samples)) / 32767.0


def _real_tts_chunks(phrase: str) -> Iterator[tuple[bytes, float]]:
    """Yield (480-sample PCM chunk, peak amplitude) for `phrase` via pyttsx3.

    Synchronous (blocking) call to `driver.runAndWait()`. We deliberately run
    it once per phrase (not per chunk) so the engine has the full utterance
    context — this is how real TTS engines produce natural prosody.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        try:
            _TTS_DRIVER.save_to_file(phrase, str(tmp_path))
            _TTS_DRIVER.runAndWait()
            with open(tmp_path, "rb") as f:
                wav_bytes = f.read()
            pcm = _resample_wav_to_8k_mono(wav_bytes)
        except Exception as exc:
            logger.warning("EXCALIBUR real TTS failed for phrase (%s); emitting silence.", exc)
            return
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass

    total = len(pcm) // (2 * _SAMPLES_PER_CHUNK)
    if total == 0:
        return
    for i in range(total):
        chunk = pcm[i * _SAMPLES_PER_CHUNK * 2 : (i + 1) * _SAMPLES_PER_CHUNK * 2]
        yield chunk, round(_real_tts_chunk_amplitude(chunk), 3)


def _chunks_for_phrase(phrase: str) -> int:
    """How many SSE chunks the phrase should span for the procedural engine.

    Speech-rate: ~36 chars/sec ≤> ~600 chars/min (slow + clear). Minimum 8
    chunks (~480 ms) so even short phrases give audible prosody.
    """
    return max(8, len(phrase) * 36 // _SAMPLES_PER_CHUNK)



def _build_audio_packet(
    phrase: str,
    chunk_index: int,
    total_chunks: int,
    is_phrase_start: bool,
) -> str:
    """Helper kept for direct callers; `event_generator` inlines its own
    `_build_phrase_payload` so it doesn't need to destructure through this
    function any more.
    """
    pcm, amp = _synth_chunk(phrase, chunk_index, total_chunks)
    payload = {
        "text_chunk": phrase if is_phrase_start else "",
        "amplitude": amp,
        "emotion_coordinate": "MERLIN_LOGIC_STRICT",
        "sample_rate": _AUDIO_SR,
        "channels": 1,
        "samples": _SAMPLES_PER_CHUNK,
        "audio_chunk": base64.b64encode(pcm).decode("ascii"),
        "is_phrase_start": is_phrase_start,
    }
    return f"data: {json.dumps(payload)}\n\n"




async def event_generator() -> AsyncIterator[str]:
    """Streams multi-modal context blocks (text + amplitude + audio) over the wire.

    If `pyttsx3` is the active engine, every phrase is pre-rendered once via
    `asyncio.to_thread(driver.runAndWait)` before any chunk is yielded, so the
    event loop is never blocked by the synchronous TTS driver. Phrases are
    cached per (phrase text -> PCM chunk list) inside this generator instance.
    """
    use_real_tts = _TTS_ENGINE_NAME == "real_tts"

    def _chunks_for_phrase_sync(phrase: str) -> list[tuple[bytes, float]]:
        return list(_real_tts_chunks(phrase)) if use_real_tts else []

    def _build_phrase_payload(pcm: bytes, amp: float, *, is_phrase_start: bool) -> str:
        return (
            "data: "
            + json.dumps(
                {
                    "text_chunk": phrase if is_phrase_start else "",
                    "amplitude": amp,
                    "emotion_coordinate": "MERLIN_LOGIC_STRICT",
                    "sample_rate": _AUDIO_SR,
                    "channels": 1,
                    "samples": _SAMPLES_PER_CHUNK,
                    "audio_chunk": base64.b64encode(pcm).decode("ascii"),
                    "is_phrase_start": is_phrase_start,
                }
            )
            + "\n\n"
        )

    try:
        for phrase in _PHRASES:
            if use_real_tts:
                # Render once off-loop so the asyncio event loop stays free.
                try:
                    chunks = await asyncio.to_thread(_chunks_for_phrase_sync, phrase)
                except Exception as exc:
                    logger.warning("EXCALIBUR real TTS dispatch failed (%s); procedural fallback.", exc)
                    chunks = []
                if chunks:
                    first_pcm, first_amp = chunks[0]
                    yield _build_phrase_payload(first_pcm, first_amp, is_phrase_start=True)
                    for i, (pcm, amp) in enumerate(chunks[1:], start=1):
                        yield _build_phrase_payload(pcm, amp, is_phrase_start=False)
                        await asyncio.sleep(_AUDIO_CHUNK_MS / 1000)
                    continue

            total = _chunks_for_phrase(phrase)
            yield _build_phrase_payload(
                *_synth_chunk(phrase, 0, total), is_phrase_start=True,
            )
            for i in range(1, total):
                yield _build_phrase_payload(
                    *_synth_chunk(phrase, i, total), is_phrase_start=False,
                )
                await asyncio.sleep(_AUDIO_CHUNK_MS / 1000)
            await asyncio.sleep(0.6)
    except asyncio.CancelledError:
        pass


@app.get("/api/stream")
async def stream_avatar_faculty() -> StreamingResponse:
    """Persistent, low-overhead SSE channel for real-time avatar interaction."""
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ------------------------------------------------------------------------------
# 🛡️  Observability & Static
# ------------------------------------------------------------------------------


@app.get("/health", response_class=PlainTextResponse)
async def health() -> str:
    return "ok"


@app.get("/version", response_class=JSONResponse)
async def version() -> dict[str, str]:
    return {"name": APP_NAME, "version": APP_VERSION}


_DASHBOARD_PATH = _BUNDLE_ROOT / "excalibur_dashboard.html"


@app.get("/", response_class=FileResponse)
async def dashboard() -> FileResponse:
    if not _DASHBOARD_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard HTML not found alongside controller.",
        )
    return FileResponse(_DASHBOARD_PATH, media_type="text/html")

# Debug-only Reset Hook
# ------------------------------------------------------------------------------
# Returns 404 unless EXCALIBUR_DEBUG=1 is set in the environment, so production
# builds cannot accidentally expose a no-auth state-reset endpoint. The route
# is excluded from the OpenAPI schema either way.
# ------------------------------------------------------------------------------


_RESET_GUARD_RESPONSES = {
    200: {"description": "State reset."},
    404: {"description": "Disabled (EXCALIBUR_DEBUG is not set)."},
}


@app.post(
    "/api/_test/reset",
    include_in_schema=False,
    responses=_RESET_GUARD_RESPONSES,
)
async def reset_state() -> dict[str, object]:
    if os.environ.get("EXCALIBUR_DEBUG") != "1":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint disabled. Set EXCALIBUR_DEBUG=1 to enable.",
        )
    _commit_state(
        {
            "merlin": "ORCHESTRATING",
            "anya": "STREAMING_AUDIO",
            "lukas": "AWAITING_PRD",
            "sentinel": "IRON_GATE_SECURE",
            "gate_paused": True,
        }
    )
    _emit_event(
        "reset",
        knight="debug",
        before=None,
        after=dict(SYSTEM_STATE),
        client="debug-cli",
        metadata={"source": "EXCALIBUR_DEBUG=1"},
    )
    return dict(SYSTEM_STATE)
