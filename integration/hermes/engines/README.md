# Local speech engines (Phase 4B prep)

Adapters that let **whisper.cpp** (STT) and **Piper** (TTS) drive Anya through
the `command` engine hooks Hermes already has. Nothing here is enabled, and
nothing here installs software or downloads a model — those are yours to do,
deliberately.

> **Status: prep only.** Phase 4B proper is blocked until the Acer hardware
> gate for Phases 2–4A is committed with a PASS. These wrappers are safe to
> land early because they change no running behavior: Hermes still defaults to
> its fixture engines, and these scripts are inert until you point
> `HERMES_STT_CMD` / `HERMES_TTS_CMD` at them.

## The contract they satisfy

From `../src/engines.mjs`:

| Engine | Invocation | Success | Failure |
|---|---|---|---|
| STT | `cmd <wav-path>` | exit 0, transcript on **stdout** (empty = no speech) | non-zero → visible notice, **falls back to typed input** |
| TTS | `cmd <text> <out-wav-path>` | exit 0, a readable RIFF WAV at that path | non-zero → **text reply stays visible**, falls back to browser `speechSynthesis` |

Two rules the wrappers enforce, because getting them wrong is a safety
problem rather than a cosmetic one:

- **Never invent a transcript to avoid an error.** A fabricated transcript can
  drive a real policy decision. Missing binary, missing model, or a non-zero
  engine exit all fail loudly; the user types instead.
- **Never let log noise reach stdout.** whisper.cpp logs to stderr; the
  wrapper discards it so only speech can become a turn. Bracketed non-speech
  markers (`[BLANK_AUDIO]`, `(wind blowing)`) are stripped to empty, which the
  contract treats as "nothing was said".

## 1. Install the engines yourself

**whisper.cpp** — <https://github.com/ggml-org/whisper.cpp>

```bash
git clone https://github.com/ggml-org/whisper.cpp && cd whisper.cpp
cmake -B build && cmake --build build -j --config Release
# Download exactly one model, by hand. tiny.en or base.en suit an 8 GB box;
# larger models are where memory pressure starts.
./models/download-ggml-model.sh base.en
# -> build/bin/whisper-cli  and  models/ggml-base.en.bin
```

**Piper** — <https://github.com/rhasspy/piper>

```bash
# Download a release binary and one voice (.onnx + .onnx.json) by hand.
# en_US-lessac-medium is a reasonable first voice.
```

## 2. Verify and benchmark them separately — before enabling anything

```bash
cd integration/hermes/engines

WHISPER_BIN=~/whisper.cpp/build/bin/whisper-cli \
WHISPER_MODEL=~/whisper.cpp/models/ggml-base.en.bin \
./verify-engines.sh stt

PIPER_BIN=~/piper/piper \
PIPER_MODEL=~/piper/voices/en_US-lessac-medium.onnx \
./verify-engines.sh tts
```

Each run reports wall time, **peak RSS**, contract conformance, and — for STT —
a real-time factor (below `1.00x` means it transcribes faster than the audio
lasts). Peak RSS needs GNU time (`apt install time`); without it you get
timings only.

**Budget before you enable.** The control stack is ~105 MB with voice on. Add
each engine's measured peak RSS against the 8 GB target, and do **not** run
whisper + Piper + a local LLM together until the numbers say they fit. Enable
one engine at a time and re-measure.

## 3. Enable explicitly

```bash
cd integration
ENABLE_HERMES_VOICE=true \
HERMES_STT_ENGINE=command \
HERMES_STT_CMD=$PWD/hermes/engines/whisper-stt.sh \
HERMES_TTS_ENGINE=command \
HERMES_TTS_CMD=$PWD/hermes/engines/piper-tts.sh \
WHISPER_BIN=... WHISPER_MODEL=... PIPER_BIN=... PIPER_MODEL=... \
make dev-up
```

Omit either pair to keep that half on the deterministic fixture engine. The
console's voice bar shows which engines are live (`stt=command tts=command`).

### Configuration

| Variable | Purpose |
|---|---|
| `WHISPER_BIN` / `WHISPER_MODEL` | required for STT |
| `WHISPER_LANG` | language hint, default `en` |
| `WHISPER_THREADS` | CPU threads, default `4` — keep low on an 8 GB laptop |
| `PIPER_BIN` / `PIPER_MODEL` | required for TTS |
| `PIPER_CONFIG` | voice JSON, defaults to `$PIPER_MODEL.json` |
| `PIPER_SPEAKER` | speaker id for multi-speaker voices |

## Audio privacy is unchanged

Hermes writes the utterance to a temp WAV, hands the path to the wrapper, and
deletes the directory in a `finally` block. The wrappers read that file and
write nothing outside the paths they are given. What persists is what always
persisted: the audio SHA-256, transcript hash, timing, provider status, and
the redacted policy/audit records.

## Rolling back

Drop `HERMES_STT_CMD` / `HERMES_TTS_CMD` (or set the engines back to
`fixture`) and `make dev-up`. Nothing else changes — no processes to stop, no
state to clean up.

## Tests

`../tests/engine-wrappers.test.ts` proves contract conformance using **stub
binaries**, so it runs on any machine with neither engine installed. It drives
the real `commandStt` / `commandTts` from `engines.mjs` against the wrappers —
conformance against the actual caller, not a restatement of it — and covers
missing binary, missing model, log noise on stderr, `[BLANK_AUDIO]` stripping,
empty results, truncated/non-WAV output, and shell-quoting safety.
