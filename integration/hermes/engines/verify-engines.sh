#!/usr/bin/env bash
# Phase 4B prep: verify and BENCHMARK local speech engines independently,
# before enabling either of them in Hermes.
#
# This script never enables anything and never touches a running stack. It
# answers three questions per engine, separately, so an 8 GB box can be
# budgeted honestly:
#     1. Is it installed and correctly configured?
#     2. Does it satisfy the Hermes command contract?
#     3. What does one utterance cost in wall time and peak RSS?
#
# Usage:
#   WHISPER_BIN=... WHISPER_MODEL=... ./verify-engines.sh stt
#   PIPER_BIN=...   PIPER_MODEL=...   ./verify-engines.sh tts
#   ...both env sets...                ./verify-engines.sh          # both
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHAT=${1:-both}
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT   # engine audio stays ephemeral, same as Hermes

pass=0
fail=0
ok()   { pass=$((pass+1)); printf '   ✔ %s\n' "$1"; }
bad()  { fail=$((fail+1)); printf '   ✘ %s\n' "$1"; }
step() { printf '── %s\n' "$1"; }

# Peak RSS + wall time for one command. Falls back gracefully where
# /usr/bin/time is absent (busybox, some minimal images).
measure() { # outvar-prefix -- command...
  local prefix=$1; shift
  local t0 t1 rss="n/a (install GNU time for peak RSS: apt install time)"
  t0=$(date +%s%3N)
  if [[ -x /usr/bin/time ]]; then
    /usr/bin/time -v "$@" >"$WORK/out" 2>"$WORK/time" || return 1
    rss=$(awk '/Maximum resident set size/ {printf "%.0fMB", $NF/1024}' "$WORK/time")
  else
    "$@" >"$WORK/out" 2>/dev/null || return 1
  fi
  t1=$(date +%s%3N)
  printf -v "${prefix}_ms" '%s' "$(( t1 - t0 ))"
  printf -v "${prefix}_rss" '%s' "$rss"
  eval "export ${prefix}_ms ${prefix}_rss"
  return 0
}

# A deterministic 2-second 16 kHz mono WAV: 1.4s of tone then silence. Enough
# for an engine to produce *something*; the content is irrelevant because we
# are measuring cost and contract conformance, not accuracy.
make_test_wav() {
  python3 - "$1" <<'EOF'
import math, struct, sys, wave
path = sys.argv[1]
sr = 16000
frames = []
for i in range(int(sr * 1.4)):
    frames.append(int(math.sin(2 * math.pi * 220 * i / sr) * 0.35 * 32767))
frames.extend([0] * int(sr * 0.6))
with wave.open(path, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(b''.join(struct.pack('<h', f) for f in frames))
EOF
}

verify_stt() {
  step "whisper.cpp (STT)"
  if [[ -z ${WHISPER_BIN:-} || -z ${WHISPER_MODEL:-} ]]; then
    bad "WHISPER_BIN / WHISPER_MODEL not set — install whisper.cpp and a model first"
    return
  fi
  local wav="$WORK/probe.wav"
  make_test_wav "$wav"

  if measure stt "$HERE/whisper-stt.sh" "$wav"; then
    local transcript
    transcript=$(cat "$WORK/out")
    ok "ran in ${stt_ms}ms (peak RSS ${stt_rss}) on 2.0s of audio"
    ok "contract: exit 0, stdout is a plain transcript ($(printf '%s' "$transcript" | wc -c) bytes)"
    [[ -n $transcript ]] && printf '     transcript: %s\n' "$transcript" \
                         || printf '     transcript: (empty — treated as no speech, nothing is submitted)\n'
    # Real-time factor: below 1.0 means faster than the audio it transcribes.
    printf '     real-time factor: %s\n' \
      "$(python3 -c "print(f'{$stt_ms/2000:.2f}x')")"
  else
    bad "whisper-stt.sh failed — see the message above; voice will fall back to typed input"
  fi
}

verify_tts() {
  step "Piper (TTS)"
  if [[ -z ${PIPER_BIN:-} || -z ${PIPER_MODEL:-} ]]; then
    bad "PIPER_BIN / PIPER_MODEL not set — install Piper and a voice first"
    return
  fi
  local out="$WORK/speech.wav"
  local text="Staging is green. Four of four services healthy."

  if measure tts "$HERE/piper-tts.sh" "$text" "$out"; then
    if [[ -s $out ]] && head -c 4 "$out" | grep -q RIFF; then
      local bytes
      bytes=$(wc -c <"$out")
      ok "ran in ${tts_ms}ms (peak RSS ${tts_rss}) for a 48-character sentence"
      ok "contract: wrote a $(python3 -c "print(f'{$bytes/1024:.0f}')")KB RIFF WAV at the requested path"
    else
      bad "piper-tts.sh exited 0 but produced no valid WAV"
    fi
  else
    bad "piper-tts.sh failed — see the message above; playback will fall back to browser speech synthesis"
  fi
}

case "$WHAT" in
  stt) verify_stt ;;
  tts) verify_tts ;;
  both) verify_stt; echo; verify_tts ;;
  *) echo "usage: verify-engines.sh [stt|tts|both]" >&2; exit 2 ;;
esac

echo
printf 'engine verification: %d passed, %d failed\n' "$pass" "$fail"
if [[ $fail -eq 0 ]]; then
  cat <<'NOTE'

Both engines are ready to be enabled EXPLICITLY. Budget them against the
8 GB target using the peak RSS above before turning anything on, and do not
run whisper + piper + a local LLM together until the numbers say they fit.
Enable with (nothing starts automatically):

  ENABLE_HERMES_VOICE=true \
  HERMES_STT_ENGINE=command HERMES_STT_CMD=<repo>/integration/hermes/engines/whisper-stt.sh \
  HERMES_TTS_ENGINE=command HERMES_TTS_CMD=<repo>/integration/hermes/engines/piper-tts.sh \
  make dev-up
NOTE
fi
[[ $fail -eq 0 ]]
