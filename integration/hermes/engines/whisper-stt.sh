#!/usr/bin/env bash
# whisper.cpp adapter for the Hermes `command` STT engine (Phase 4B prep).
#
# CONTRACT (integration/hermes/src/engines.mjs :: commandStt)
#   argv[1] = path to a 16 kHz mono PCM16 WAV that Hermes wrote
#   stdout  = the transcript, or empty for "no usable speech"
#   exit 0  = success (empty stdout is a legitimate "silence" result)
#   exit !0 = engine failure -> Hermes returns an error -> the console shows a
#             visible notice and falls back to TYPED INPUT. Never invent a
#             transcript to avoid an error: a fabricated transcript could
#             trigger a policy decision the user never asked for.
#
# NOTHING here downloads a model or installs a binary. Both are yours to
# install; this wrapper only refuses clearly when they are missing.
#
# Configure (all optional except the two paths):
#   WHISPER_BIN     path to whisper-cli (or legacy `main`)   [required]
#   WHISPER_MODEL   path to a ggml-*.bin model               [required]
#   WHISPER_LANG    language hint, default "en"
#   WHISPER_THREADS CPU threads, default 4 (keep low on an 8 GB box)
set -uo pipefail

WHISPER_BIN=${WHISPER_BIN:-}
WHISPER_MODEL=${WHISPER_MODEL:-}
WHISPER_LANG=${WHISPER_LANG:-en}
WHISPER_THREADS=${WHISPER_THREADS:-4}

die() { echo "whisper-stt: $*" >&2; exit 1; }

[[ -n $WHISPER_BIN ]]   || die "WHISPER_BIN is not set (path to whisper-cli)"
[[ -x $WHISPER_BIN ]]   || die "WHISPER_BIN is not executable: $WHISPER_BIN"
[[ -n $WHISPER_MODEL ]] || die "WHISPER_MODEL is not set (path to a ggml model)"
[[ -r $WHISPER_MODEL ]] || die "WHISPER_MODEL is not readable: $WHISPER_MODEL"

wav=${1:-}
[[ -n $wav ]] || die "usage: whisper-stt.sh <wav-path>"
[[ -r $wav ]] || die "input wav is not readable: $wav"

# -nt      no timestamps
# -np      no progress prints
# stderr is discarded: whisper.cpp logs there, and only the transcript may
# reach stdout or Hermes would treat log noise as speech.
transcript=$("$WHISPER_BIN" \
  -m "$WHISPER_MODEL" \
  -f "$wav" \
  -l "$WHISPER_LANG" \
  -t "$WHISPER_THREADS" \
  -nt -np 2>/dev/null) || die "whisper.cpp exited non-zero"

# Collapse whitespace and drop whisper's bracketed non-speech markers
# ([BLANK_AUDIO], [ Silence ], (wind blowing) …) — those are not utterances,
# and letting them through would submit a bogus turn.
printf '%s' "$transcript" \
  | tr '\n' ' ' \
  | sed -E 's/\[[^]]*\]//g; s/\([^)]*\)//g; s/[[:space:]]+/ /g; s/^ //; s/ $//'
