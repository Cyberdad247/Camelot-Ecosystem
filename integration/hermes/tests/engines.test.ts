// Hermes fixture engine tests: energy gating, confidence shaping, WAV output.

import { describe, expect, it } from 'vitest';
// @ts-expect-error zero-dep plain ESM module
import { fixtureTts, makeFixtureStt, pcmStats, pcm16ToWav, SILENCE_RMS } from '../src/engines.mjs';

function sine(amplitude: number, ms: number, sampleRate = 16000): Int16Array {
  const pcm = new Int16Array((sampleRate * ms) / 1000);
  for (let i = 0; i < pcm.length; i++) {
    pcm[i] = Math.round(Math.sin((2 * Math.PI * 440 * i) / sampleRate) * amplitude * 32767);
  }
  return pcm;
}

describe('hermes fixture STT', () => {
  it('silence produces NO transcript (nothing submittable)', async () => {
    const stt = makeFixtureStt();
    const result = await stt(new Int16Array(16000), 16000);
    expect(result.transcript).toBeNull();
    expect(result.confidence).toBe(0);
  });

  it('too-short blips produce no transcript', async () => {
    const stt = makeFixtureStt();
    const result = await stt(sine(0.5, 100), 16000);
    expect(result.transcript).toBeNull();
  });

  it('clear speech-energy audio yields a scripted transcript with high confidence', async () => {
    const stt = makeFixtureStt(['prepare a deployment review']);
    const result = await stt(sine(0.5, 800), 16000);
    expect(result.transcript).toBe('prepare a deployment review');
    expect(result.confidence).toBeGreaterThanOrEqual(0.9);
  });

  it('quiet audio yields LOW confidence (review gate engages downstream)', async () => {
    const stt = makeFixtureStt(['create a change request']);
    const quiet = sine(0.02, 800); // just above the silence floor
    const result = await stt(quiet, 16000);
    expect(result.transcript).toBe('create a change request');
    expect(result.confidence).toBeLessThan(0.75);
  });

  it('script cycles deterministically', async () => {
    const stt = makeFixtureStt(['one', 'two']);
    expect((await stt(sine(0.5, 500), 16000)).transcript).toBe('one');
    expect((await stt(sine(0.5, 500), 16000)).transcript).toBe('two');
    expect((await stt(sine(0.5, 500), 16000)).transcript).toBe('one');
  });
});

describe('hermes fixture TTS + wav', () => {
  it('emits a valid RIFF/WAVE mono 16-bit file, deterministic per text', () => {
    const a = fixtureTts('Staging is green.');
    const b = fixtureTts('Staging is green.');
    const c = fixtureTts('The change request is filed.');
    expect(a.subarray(0, 4).toString()).toBe('RIFF');
    expect(a.subarray(8, 12).toString()).toBe('WAVE');
    expect(a.equals(b)).toBe(true);
    expect(a.equals(c)).toBe(false);
  });

  it('pcmStats reports silence below the gate', () => {
    const { rms } = pcmStats(new Int16Array(1600), 16000);
    expect(rms).toBeLessThan(SILENCE_RMS);
  });

  it('wav header length matches payload', () => {
    const pcm = sine(0.3, 100);
    const wav = pcm16ToWav(pcm, 16000);
    expect(wav.length).toBe(44 + pcm.length * 2);
  });
});
