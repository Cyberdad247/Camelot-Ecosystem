// Phase 4B prep: the whisper.cpp and Piper wrappers must satisfy the Hermes
// `command` engine contract EXACTLY, and must fail loudly-but-safely when the
// engine is missing.
//
// These tests never require whisper.cpp or Piper to be installed: they drive
// the wrappers with stub binaries, and — critically — run the real
// commandStt/commandTts from engines.mjs against them, so conformance is
// proven against the actual caller rather than a restatement of it.

import { execFile } from 'node:child_process';
import { chmodSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
// @ts-expect-error zero-dep plain ESM module
import { commandStt, commandTts, pcm16ToWav } from '../src/engines.mjs';

const run = promisify(execFile);
const enginesDir = fileURLToPath(new URL('../engines/', import.meta.url));
const WHISPER_WRAPPER = join(enginesDir, 'whisper-stt.sh');
const PIPER_WRAPPER = join(enginesDir, 'piper-tts.sh');

let work: string;

/** A stub that behaves like the real binary for contract purposes. */
function stub(name: string, body: string): string {
  const path = join(work, name);
  writeFileSync(path, `#!/usr/bin/env bash\n${body}\n`);
  chmodSync(path, 0o755);
  return path;
}

function speechWav(): Buffer {
  const sr = 16000;
  const pcm = new Int16Array(sr); // 1 second
  for (let i = 0; i < pcm.length; i++) {
    pcm[i] = Math.round(Math.sin((2 * Math.PI * 220 * i) / sr) * 0.4 * 32767);
  }
  return pcm16ToWav(pcm, sr);
}

beforeAll(() => {
  work = mkdtempSync(join(tmpdir(), 'engine-wrappers-'));
});

afterAll(() => {
  // Nothing sensitive here, but mirror the ephemeral-audio discipline.
});

describe('whisper.cpp STT wrapper', () => {
  it('refuses clearly when the binary is not configured', async () => {
    await expect(
      run('bash', [WHISPER_WRAPPER, '/nonexistent.wav'], { env: { PATH: process.env['PATH'] ?? '' } }),
    ).rejects.toMatchObject({ code: 1 });
  });

  it('refuses when the model file is missing (never invents a transcript)', async () => {
    const bin = stub('whisper-ok', 'echo "should not be reached"');
    await expect(
      run('bash', [WHISPER_WRAPPER, '/nonexistent.wav'], {
        env: { PATH: process.env['PATH'] ?? '', WHISPER_BIN: bin, WHISPER_MODEL: '/nope/model.bin' },
      }),
    ).rejects.toMatchObject({ code: 1 });
  });

  it('emits only the transcript on stdout', async () => {
    const bin = stub(
      'whisper-cli',
      // Real whisper.cpp writes logs to stderr and text to stdout.
      'echo "loading model..." >&2\necho "prepare a deployment review"',
    );
    const model = join(work, 'ggml-tiny.bin');
    writeFileSync(model, 'stub');
    const wav = join(work, 'a.wav');
    writeFileSync(wav, speechWav());

    const { stdout } = await run('bash', [WHISPER_WRAPPER, wav], {
      env: { PATH: process.env['PATH'] ?? '', WHISPER_BIN: bin, WHISPER_MODEL: model },
    });
    expect(stdout).toBe('prepare a deployment review');
    expect(stdout).not.toContain('loading model');
  });

  it('strips non-speech markers so silence never becomes a turn', async () => {
    const bin = stub('whisper-blank', 'echo "[BLANK_AUDIO]"');
    const model = join(work, 'ggml-tiny.bin');
    const wav = join(work, 'b.wav');
    writeFileSync(wav, speechWav());

    const { stdout } = await run('bash', [WHISPER_WRAPPER, wav], {
      env: { PATH: process.env['PATH'] ?? '', WHISPER_BIN: bin, WHISPER_MODEL: model },
    });
    // Empty stdout == "no usable speech" in the Hermes contract, which the
    // console turns into "nothing was submitted".
    expect(stdout.trim()).toBe('');
  });

  it('satisfies commandStt end to end (real caller, stub engine)', async () => {
    const bin = stub('whisper-e2e', 'echo "read staging status"');
    const model = join(work, 'ggml-tiny.bin');
    process.env['WHISPER_BIN'] = bin;
    process.env['WHISPER_MODEL'] = model;

    const pcm = new Int16Array(16000);
    const result = await commandStt(WHISPER_WRAPPER, pcm, 16000);
    expect(result).toEqual({ transcript: 'read staging status', confidence: 0.9, engine: 'command' });

    delete process.env['WHISPER_BIN'];
    delete process.env['WHISPER_MODEL'];
  });

  it('an empty engine result becomes "no transcript", not a fabricated turn', async () => {
    const bin = stub('whisper-empty', 'echo ""');
    process.env['WHISPER_BIN'] = bin;
    process.env['WHISPER_MODEL'] = join(work, 'ggml-tiny.bin');

    const result = await commandStt(WHISPER_WRAPPER, new Int16Array(16000), 16000);
    expect(result.transcript).toBeNull();
    expect(result.confidence).toBe(0);

    delete process.env['WHISPER_BIN'];
    delete process.env['WHISPER_MODEL'];
  });
});

describe('Piper TTS wrapper', () => {
  it('refuses clearly when the binary is not configured', async () => {
    await expect(
      run('bash', [PIPER_WRAPPER, 'hello', join(work, 'x.wav')], {
        env: { PATH: process.env['PATH'] ?? '' },
      }),
    ).rejects.toMatchObject({ code: 1 });
  });

  it('writes a RIFF WAV at the requested path', async () => {
    const voice = join(work, 'voice.onnx');
    writeFileSync(voice, 'stub');
    // Stub piper: reads text on stdin, writes a valid WAV to --output_file.
    const bin = stub(
      'piper',
      `out=""
while [[ $# -gt 0 ]]; do
  case "$1" in --output_file) out="$2"; shift 2;; *) shift;; esac
done
cat >/dev/null
printf 'RIFF' > "$out"
head -c 40 /dev/zero >> "$out"`,
    );
    const out = join(work, 'speech.wav');
    await run('bash', [PIPER_WRAPPER, 'Staging is green.', out], {
      env: { PATH: process.env['PATH'] ?? '', PIPER_BIN: bin, PIPER_MODEL: voice },
    });
    expect(readFileSync(out).subarray(0, 4).toString()).toBe('RIFF');
  });

  it('fails rather than returning a truncated or non-WAV file', async () => {
    const voice = join(work, 'voice.onnx');
    const bin = stub(
      'piper-bad',
      `out=""
while [[ $# -gt 0 ]]; do
  case "$1" in --output_file) out="$2"; shift 2;; *) shift;; esac
done
cat >/dev/null
echo "an error message, not audio" > "$out"`,
    );
    await expect(
      run('bash', [PIPER_WRAPPER, 'hello', join(work, 'bad.wav')], {
        env: { PATH: process.env['PATH'] ?? '', PIPER_BIN: bin, PIPER_MODEL: voice },
      }),
    ).rejects.toMatchObject({ code: 1 });
  });

  it('satisfies commandTts end to end (real caller, stub engine)', async () => {
    const voice = join(work, 'voice.onnx');
    const bin = stub(
      'piper-e2e',
      `out=""
while [[ $# -gt 0 ]]; do
  case "$1" in --output_file) out="$2"; shift 2;; *) shift;; esac
done
cat >/dev/null
printf 'RIFF' > "$out"
head -c 40 /dev/zero >> "$out"`,
    );
    process.env['PIPER_BIN'] = bin;
    process.env['PIPER_MODEL'] = voice;

    const wav = await commandTts(PIPER_WRAPPER, 'Staging is green.');
    expect(Buffer.from(wav).subarray(0, 4).toString()).toBe('RIFF');

    delete process.env['PIPER_BIN'];
    delete process.env['PIPER_MODEL'];
  });

  it('quoting is safe: text with quotes and newlines reaches the engine intact', async () => {
    const voice = join(work, 'voice.onnx');
    const captured = join(work, 'captured.txt');
    const bin = stub(
      'piper-echo',
      `out=""
while [[ $# -gt 0 ]]; do
  case "$1" in --output_file) out="$2"; shift 2;; *) shift;; esac
done
cat > "${captured}"
printf 'RIFF' > "$out"
head -c 40 /dev/zero >> "$out"`,
    );
    const tricky = `He said "staging is green"; then $(rm -rf /) and \`whoami\``;
    await run('bash', [PIPER_WRAPPER, tricky, join(work, 'q.wav')], {
      env: { PATH: process.env['PATH'] ?? '', PIPER_BIN: bin, PIPER_MODEL: voice },
    });
    // Verbatim: no shell re-parsing, no command substitution executed.
    expect(readFileSync(captured, 'utf8')).toBe(tricky);
  });
});
