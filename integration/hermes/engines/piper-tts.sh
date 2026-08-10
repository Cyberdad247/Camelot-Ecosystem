#!/usr/bin/env bash
# Piper adapter for the Hermes `command` TTS engine (Phase 4B prep).
#
# CONTRACT (integration/hermes/src/engines.mjs :: commandTts)
#   argv[1] = the text to speak
#   argv[2] = path where this script must write a WAV
#   exit 0  = a readable WAV now exists at argv[2]
#   exit !0 = engine failure -> Hermes errors -> the console keeps the TEXT
#             reply visible and falls back to browser speechSynthesis. A TTS
#             failure must never hide the answer.
#
# NOTHING here downloads a voice or installs a binary. Both are yours.
#
# Configure:
#   PIPER_BIN     path to the piper executable        [required]
#   PIPER_MODEL   path to a .onnx voice               [required]
#   PIPER_CONFIG  path to the voice .onnx.json        [default: $PIPER_MODEL.json]
#   PIPER_SPEAKER speaker id for multi-speaker voices [optional]
set -uo pipefail

PIPER_BIN=${PIPER_BIN:-}
PIPER_MODEL=${PIPER_MODEL:-}
PIPER_CONFIG=${PIPER_CONFIG:-${PIPER_MODEL:+$PIPER_MODEL.json}}
PIPER_SPEAKER=${PIPER_SPEAKER:-}

die() { echo "piper-tts: $*" >&2; exit 1; }

[[ -n $PIPER_BIN ]]   || die "PIPER_BIN is not set (path to the piper executable)"
[[ -x $PIPER_BIN ]]   || die "PIPER_BIN is not executable: $PIPER_BIN"
[[ -n $PIPER_MODEL ]] || die "PIPER_MODEL is not set (path to a .onnx voice)"
[[ -r $PIPER_MODEL ]] || die "PIPER_MODEL is not readable: $PIPER_MODEL"

text=${1:-}
out=${2:-}
[[ -n $text ]] || die "usage: piper-tts.sh <text> <out-wav-path>"
[[ -n $out ]]  || die "usage: piper-tts.sh <text> <out-wav-path>"

args=(--model "$PIPER_MODEL" --output_file "$out")
[[ -n $PIPER_CONFIG && -r $PIPER_CONFIG ]] && args+=(--config "$PIPER_CONFIG")
[[ -n $PIPER_SPEAKER ]] && args+=(--speaker "$PIPER_SPEAKER")

# Text goes in on stdin so punctuation and quoting are never re-parsed by a
# shell. Piper logs to stderr; discard it so only the WAV matters.
printf '%s' "$text" | "$PIPER_BIN" "${args[@]}" >/dev/null 2>/dev/null \
  || die "piper exited non-zero"

[[ -s $out ]] || die "piper produced no audio at $out"
# Sanity: a real RIFF/WAVE header, not a truncated or error file.
head -c 4 "$out" | grep -q RIFF || die "piper output is not a RIFF WAV"
