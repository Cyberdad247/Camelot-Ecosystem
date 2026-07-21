import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const packageUrl = new URL("../../../packages/voice-first-runtime/", import.meta.url);

test("shared microphone arbiter rejects contention and releases deterministically", async () => {
  const { MicrophoneArbiter } = await import(new URL("src/microphone-arbiter.ts", packageUrl));
  const arbiter = new MicrophoneArbiter();
  const transitions = [];
  const unsubscribe = arbiter.subscribe((state) => transitions.push(state.holderId));

  const anya = arbiter.acquire("anya", "dictation");
  assert.equal(anya.ok, true);
  const interphase = arbiter.acquire("interphase", "voice-first capture");
  assert.deepEqual(interphase, { ok: false, currentHolder: "anya", reason: "dictation" });
  assert.equal(arbiter.acquire("anya", "dictation").ok, true);
  if (anya.ok) anya.release();
  assert.equal(arbiter.snapshot().holderId, null);
  assert.deepEqual(transitions, [null, "anya", null]);
  unsubscribe();
});

test("worklet ring overflow drops the oldest sample and marks discontinuity", async () => {
  const code = await readFile(new URL("worklets/voice-capture.worklet.js", packageUrl), "utf8");
  let Processor;
  class AudioWorkletProcessorStub {
    constructor() {
      this.port = { onmessage: null, postMessage() {} };
    }
  }
  const context = vm.createContext({
    AudioWorkletProcessor: AudioWorkletProcessorStub,
    Int16Array,
    Int32Array,
    Atomics,
    Math,
    sampleRate: 48_000,
    currentTime: 0,
    registerProcessor(_name, implementation) {
      Processor = implementation;
    },
  });
  vm.runInContext(code, context);

  const controlBuffer = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 4);
  const sampleBuffer = new SharedArrayBuffer(Int16Array.BYTES_PER_ELEMENT * 3_200);
  const processor = new Processor({
    processorOptions: {
      frameSamples: 1_600,
      ring: { control: controlBuffer, samples: sampleBuffer, capacity: 3_200 },
    },
  });
  const input = Int16Array.from({ length: 3_200 }, (_, index) => index);
  assert.equal(processor.writeShared(input), true);

  const control = new Int32Array(controlBuffer);
  assert.equal(Atomics.load(control, 2), 1);
  assert.equal(Atomics.load(control, 1), 1);
  assert.equal(Atomics.load(control, 0), 0);
});
