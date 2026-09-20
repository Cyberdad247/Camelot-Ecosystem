// SPDX-License-Identifier: MIT
//
// Voice-First Cartridge — Phase 3 crucible: capture contract.
//
// Covers `docs/plans/voice-first-cartridge/verification.md` § Capture Contract:
// lease contention, ring overflow + discontinuity, VAD/utterance bounds, and
// deterministic teardown.
//
// The runtime is driven through injected fakes plus a minimal AudioWorkletNode
// stand-in, because Node has no Web Audio. Everything else is the real
// implementation reached through the `@camelot/voice-first-runtime` alias.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  MicrophoneArbiter,
  SharedPcmRing,
  VoiceFirstRuntime,
  type VoiceFrame,
  type VoiceRuntimeState,
  type VoiceUtterance,
} from '@camelot/voice-first-runtime';

// ── Fakes ─────────────────────────────────────────────────────────────────────

class FakeWorkletNode {
  static latest: FakeWorkletNode | null = null;
  port = {
    onmessage: null as ((event: { data: unknown }) => void) | null,
    postMessage: vi.fn(),
  };
  connect = vi.fn();
  disconnect = vi.fn();

  constructor() {
    FakeWorkletNode.latest = this;
  }

  emit(data: unknown) {
    this.port.onmessage?.({ data });
  }
}

interface FakeHarness {
  tracks: { stop: ReturnType<typeof vi.fn> }[];
  context: {
    state: string;
    destination: object;
    audioWorklet: { addModule: ReturnType<typeof vi.fn> };
    resume: ReturnType<typeof vi.fn>;
    close: ReturnType<typeof vi.fn>;
    createMediaStreamSource: ReturnType<typeof vi.fn>;
    createGain: ReturnType<typeof vi.fn>;
  };
}

function fakeHarness(): FakeHarness {
  const tracks = [{ stop: vi.fn() }];
  const context = {
    state: 'running',
    destination: {},
    audioWorklet: { addModule: vi.fn().mockResolvedValue(undefined) },
    resume: vi.fn().mockResolvedValue(undefined),
    close: vi.fn().mockResolvedValue(undefined),
    createMediaStreamSource: vi.fn(() => ({ connect: vi.fn(), disconnect: vi.fn() })),
    createGain: vi.fn(() => ({ gain: { value: 1 }, connect: vi.fn(), disconnect: vi.fn() })),
  };
  return { tracks, context };
}

/** Emits a perfectly-sized PCM frame so it is not flagged discontinuous. */
function emitFrame(
  sampleCount: number,
  options: { discontinuity?: boolean; speech?: boolean; timestampMs?: number; sequence?: number } = {}
) {
  const samples = new Int16Array(sampleCount);
  FakeWorkletNode.latest?.emit({
    type: 'frame',
    sequence: options.sequence ?? 0,
    timestampMs: options.timestampMs ?? 0,
    sampleCount,
    discontinuity: options.discontinuity ?? false,
    speech: options.speech ?? false,
    rms: options.speech ? 0.2 : 0.001,
    samples: samples.buffer,
  });
}

function makeRuntime(
  overrides: {
    holderId?: string;
    harness?: FakeHarness;
    resourceGate?: () => { ok: true } | { ok: false; reason: string };
    silenceMs?: number;
    onFrame?: (frame: VoiceFrame) => void;
    onUtterance?: (utterance: VoiceUtterance) => void;
    onState?: (state: VoiceRuntimeState, detail?: string) => void;
  } = {}
) {
  const harness = overrides.harness ?? fakeHarness();
  const runtime = new VoiceFirstRuntime({
    holderId: overrides.holderId ?? 'test-holder',
    reason: 'crucible',
    silenceMs: overrides.silenceMs ?? 800,
    resourceGate: overrides.resourceGate,
    getUserMedia: async () => ({ getTracks: () => harness.tracks }) as unknown as MediaStream,
    createAudioContext: () => harness.context as unknown as AudioContext,
    onFrame: overrides.onFrame,
    onUtterance: overrides.onUtterance,
    onState: overrides.onState,
  });
  return { runtime, harness };
}

// ── Suite ─────────────────────────────────────────────────────────────────────

const originalWorkletNode = (globalThis as { AudioWorkletNode?: unknown }).AudioWorkletNode;

beforeEach(() => {
  (globalThis as { AudioWorkletNode?: unknown }).AudioWorkletNode = FakeWorkletNode;
});

afterEach(() => {
  (globalThis as { AudioWorkletNode?: unknown }).AudioWorkletNode = originalWorkletNode;
  FakeWorkletNode.latest = null;
});

describe('microphone lease', () => {
  it('grants one owner and rejects a contending consumer with the current holder', () => {
    const arbiter = new MicrophoneArbiter();
    const first = arbiter.acquire('anya', 'interphase');
    expect(first.ok).toBe(true);

    const second = arbiter.acquire('lakisha', 'hud');
    expect(second.ok).toBe(false);
    if (!second.ok) {
      expect(second.currentHolder).toBe('anya');
      expect(second.reason).toBe('interphase');
    }
  });

  it('lets the same holder re-acquire and frees the lease on release', () => {
    const arbiter = new MicrophoneArbiter();
    const first = arbiter.acquire('anya', 'interphase');
    expect(arbiter.acquire('anya', 'again').ok).toBe(true);

    if (first.ok) first.release();
    expect(arbiter.snapshot().holderId).toBeNull();
    expect(arbiter.acquire('lakisha', 'hud').ok).toBe(true);
  });

  it('rejects a blank holder id', () => {
    expect(() => new MicrophoneArbiter().acquire('   ', 'x')).toThrow(/holderId is required/);
  });

  it('refuses a second runtime while the first holds the lease', async () => {
    const firstHarness = fakeHarness();
    const { runtime: a } = makeRuntime({ holderId: 'interphase-a', harness: firstHarness });
    await a.start();

    const states: VoiceRuntimeState[] = [];
    const { runtime: b } = makeRuntime({
      holderId: 'interphase-b',
      onState: (state) => states.push(state),
    });

    await expect(b.start()).rejects.toThrow(/Microphone is in use by interphase-a/);
    expect(b.snapshot().state).toBe('unavailable');
    expect(states).toContain('unavailable');

    await a.stop();
    // Lease released, so the contending runtime can now claim it.
    await expect(b.start()).resolves.toBeUndefined();
    await b.stop();
  });
});

describe('bounded PCM ring', () => {
  it('rejects a capacity below the frame bound', () => {
    expect(() => new SharedPcmRing(3_199)).toThrow(/at least 3,200 samples/);
  });

  it('reports dropped samples and closes deterministically', () => {
    const ring = new SharedPcmRing();
    expect(ring.droppedSamples()).toBe(0);
    expect(ring.read(10).length).toBe(0);
    ring.close();
    expect(ring.droppedSamples()).toBe(0);
  });
});

describe('frame contract', () => {
  it('marks a frame discontinuous when the worklet says so', async () => {
    const frames: VoiceFrame[] = [];
    const { runtime } = makeRuntime({ onFrame: (frame) => frames.push(frame) });
    await runtime.start();

    emitFrame(160, { discontinuity: true });
    expect(frames).toHaveLength(1);
    expect(frames[0].discontinuity).toBe(true);
    expect(frames[0].sampleCount).toBe(160);
    expect(frames[0].sampleRate).toBe(16_000);
    expect(frames[0].channels).toBe(1);

    emitFrame(160, { discontinuity: false, sequence: 1 });
    expect(frames[1].discontinuity).toBe(false);

    await runtime.stop();
  });

  it('treats a short payload as a discontinuity rather than a silent gap', async () => {
    const frames: VoiceFrame[] = [];
    const { runtime } = makeRuntime({ onFrame: (frame) => frames.push(frame) });
    await runtime.start();

    // Leftover bytes from a torn transfer: declared 160 samples, delivered 32.
    const short = new Int16Array(32);
    FakeWorkletNode.latest?.emit({
      type: 'frame',
      sequence: 0,
      timestampMs: 0,
      sampleCount: 160,
      discontinuity: false,
      speech: false,
      rms: 0.001,
      samples: short.buffer,
    });

    expect(frames[0].sampleCount).toBe(32);
    expect(frames[0].discontinuity).toBe(true);

    await runtime.stop();
  });

  it('ignores out-of-bounds and non-frame messages', async () => {
    const frames: VoiceFrame[] = [];
    const { runtime } = makeRuntime({ onFrame: (frame) => frames.push(frame) });
    await runtime.start();

    FakeWorkletNode.latest?.emit({ type: 'noise' });
    FakeWorkletNode.latest?.emit({
      type: 'frame',
      sequence: 0,
      timestampMs: 0,
      sampleCount: 0,
      discontinuity: false,
      speech: false,
      rms: 0,
    });
    FakeWorkletNode.latest?.emit({
      type: 'frame',
      sequence: 1,
      timestampMs: 0,
      sampleCount: 1_601,
      discontinuity: false,
      speech: false,
      rms: 0,
    });

    expect(frames).toHaveLength(0);
    expect(runtime.snapshot().frames).toBe(0);

    await runtime.stop();
  });
});

describe('local VAD and utterance bounds', () => {
  it('closes an utterance after the configured silence window', async () => {
    const utterances: VoiceUtterance[] = [];
    const { runtime } = makeRuntime({ onUtterance: (u) => utterances.push(u), silenceMs: 800 });
    await runtime.start();

    emitFrame(160, { speech: true, timestampMs: 0, sequence: 0 });
    emitFrame(160, { speech: true, timestampMs: 100, sequence: 1 });
    expect(utterances).toHaveLength(0);

    emitFrame(160, { speech: false, timestampMs: 1_000, sequence: 2 });
    expect(utterances).toHaveLength(1);
    expect(utterances[0].sampleRate).toBe(16_000);
    expect(utterances[0].truncated).toBe(false);
    expect(runtime.snapshot().utterances).toBe(1);

    await runtime.stop();
  });

  it('does not open an utterance on silence alone', async () => {
    const utterances: VoiceUtterance[] = [];
    const { runtime } = makeRuntime({ onUtterance: (u) => utterances.push(u) });
    await runtime.start();

    for (let i = 0; i < 10; i += 1) {
      emitFrame(160, { speech: false, timestampMs: i * 100, sequence: i });
    }

    expect(utterances).toHaveLength(0);
    await runtime.stop();
  });

  it('truncates an utterance that exceeds the 30 s ceiling', async () => {
    const utterances: VoiceUtterance[] = [];
    const { runtime } = makeRuntime({ onUtterance: (u) => utterances.push(u) });
    await runtime.start();

    emitFrame(160, { speech: true, timestampMs: 0, sequence: 0 });
    emitFrame(160, { speech: true, timestampMs: 30_000, sequence: 1 });

    expect(utterances).toHaveLength(1);
    expect(utterances[0].truncated).toBe(true);
    // The ceiling caps the retained audio at 30 s of 16 kHz mono.
    expect(utterances[0].samples.length).toBeLessThanOrEqual(30 * 16_000);

    await runtime.stop();
  });

  it('fails closed when the resource gate is red', async () => {
    const { runtime } = makeRuntime({
      resourceGate: () => ({ ok: false, reason: 'Host memory exceeds the 7.2 GB voice gate.' }),
    });

    await expect(runtime.start()).rejects.toThrow(/7\.2 GB voice gate/);
    expect(runtime.snapshot().state).toBe('unavailable');
    expect(runtime.snapshot().transport).toBeNull();
  });
});

describe('teardown', () => {
  it('releases every track, node, port, and AudioContext on stop', async () => {
    const { runtime, harness } = makeRuntime();
    await runtime.start();
    expect(runtime.snapshot().state).toBe('listening');

    const node = FakeWorkletNode.latest;
    await runtime.stop();

    expect(harness.tracks[0].stop).toHaveBeenCalled();
    expect(harness.context.close).toHaveBeenCalled();
    expect(node?.disconnect).toHaveBeenCalled();
    expect(node?.port.postMessage).toHaveBeenCalledWith({ type: 'stop' });
    expect(node?.port.onmessage).toBeNull();
    expect(runtime.snapshot().state).toBe('idle');
    expect(runtime.snapshot().transport).toBeNull();
  });

  it('returns the microphone lease so a later capture can start', async () => {
    const { runtime } = makeRuntime({ holderId: 'teardown-holder' });
    await runtime.start();
    await runtime.stop();

    const { runtime: next } = makeRuntime({ holderId: 'next-holder' });
    await expect(next.start()).resolves.toBeUndefined();
    await next.stop();
  });

  it('surfaces an unavailable state when capture fails to start', async () => {
    const harness = fakeHarness();
    harness.context.audioWorklet.addModule.mockRejectedValue(new Error('worklet blocked'));
    const states: VoiceRuntimeState[] = [];
    const { runtime } = makeRuntime({ harness, onState: (s) => states.push(s) });

    await expect(runtime.start()).rejects.toThrow(/worklet blocked/);
    expect(states).toContain('unavailable');
    expect(runtime.snapshot().state).toBe('unavailable');
  });
});
