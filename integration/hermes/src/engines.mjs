// Hermes STT/TTS engines. Default "fixture" engines are deterministic and
// model-free: STT gates on real audio energy and serves scripted utterances;
// TTS synthesizes an audible WAV melody derived from the text. The "command"
// engines invoke a user-configured external binary (whisper.cpp, piper, …) —
// explicitly configured, NEVER auto-started or downloaded (8 GB rule).
//
// Raw audio is ephemeral: STT processes buffers in memory; the command
// engine's temp WAV is unlinked in a finally block.

import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { mkdtemp, rm, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export const DEFAULT_STT_SCRIPT = [
  'read staging status',
  'prepare a deployment review',
  'create a change request to scale the api tier',
];

/** RMS below this is silence — no transcript, nothing submittable. */
export const SILENCE_RMS = 0.01;
/** RMS above this earns full fixture confidence. */
const CLEAR_SPEECH_RMS = 0.06;
export const MIN_UTTERANCE_MS = 220;

export function pcmStats(pcm16, sampleRate) {
  let sumSq = 0;
  for (const s of pcm16) {
    const f = s / 32768;
    sumSq += f * f;
  }
  const rms = pcm16.length ? Math.sqrt(sumSq / pcm16.length) : 0;
  return { rms, durationMs: (pcm16.length / sampleRate) * 1000 };
}

export function makeFixtureStt(script = DEFAULT_STT_SCRIPT) {
  let index = 0;
  return async function fixtureStt(pcm16, sampleRate) {
    const { rms, durationMs } = pcmStats(pcm16, sampleRate);
    if (rms < SILENCE_RMS || durationMs < MIN_UTTERANCE_MS) {
      return { transcript: null, confidence: 0, engine: 'fixture' };
    }
    const transcript = script[index % script.length];
    index += 1;
    // Quiet audio -> low confidence -> the console's review gate engages.
    const clarity = Math.min(1, (rms - SILENCE_RMS) / (CLEAR_SPEECH_RMS - SILENCE_RMS));
    const confidence = Math.round((0.55 + 0.4 * clarity) * 100) / 100;
    return { transcript, confidence, engine: 'fixture' };
  };
}

export async function commandStt(command, pcm16, sampleRate) {
  const dir = await mkdtemp(join(tmpdir(), 'hermes-stt-'));
  const wavPath = join(dir, 'utterance.wav');
  try {
    await writeFile(wavPath, pcm16ToWav(pcm16, sampleRate));
    const stdout = await run(command, [wavPath]);
    const transcript = stdout.trim();
    return transcript
      ? { transcript, confidence: 0.9, engine: 'command' }
      : { transcript: null, confidence: 0, engine: 'command' };
  } finally {
    await rm(dir, { recursive: true, force: true }); // audio stays ephemeral
  }
}

/** Deterministic audible WAV derived from the text (fixture TTS). */
export function fixtureTts(text, sampleRate = 16000) {
  const hash = createHash('sha256').update(text).digest();
  const words = Math.max(2, Math.min(24, text.split(/\s+/).length));
  const noteMs = 90;
  const samplesPerNote = Math.floor((sampleRate * noteMs) / 1000);
  const pcm = new Int16Array(words * samplesPerNote);
  for (let w = 0; w < words; w++) {
    const freq = 220 + (hash[w % hash.length] % 48) * 12;
    for (let i = 0; i < samplesPerNote; i++) {
      const t = i / sampleRate;
      const envelope = Math.sin((Math.PI * i) / samplesPerNote);
      pcm[w * samplesPerNote + i] = Math.round(
        Math.sin(2 * Math.PI * freq * t) * envelope * 0.35 * 32767,
      );
    }
  }
  return pcm16ToWav(pcm, sampleRate);
}

export async function commandTts(command, text) {
  const dir = await mkdtemp(join(tmpdir(), 'hermes-tts-'));
  const wavPath = join(dir, 'speech.wav');
  try {
    await run(command, [text, wavPath]);
    return await readFile(wavPath);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}

export function pcm16ToWav(pcm16, sampleRate) {
  const dataLength = pcm16.length * 2;
  const buffer = Buffer.alloc(44 + dataLength);
  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write('WAVE', 8);
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20); // PCM
  buffer.writeUInt16LE(1, 22); // mono
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * 2, 28);
  buffer.writeUInt16LE(2, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write('data', 36);
  buffer.writeUInt32LE(dataLength, 40);
  for (let i = 0; i < pcm16.length; i++) buffer.writeInt16LE(pcm16[i], 44 + i * 2);
  return buffer;
}

function run(command, args) {
  return new Promise((resolve, reject) => {
    execFile(command, args, { timeout: 30_000, maxBuffer: 1 << 20 }, (err, stdout) => {
      if (err) reject(err);
      else resolve(String(stdout));
    });
  });
}
