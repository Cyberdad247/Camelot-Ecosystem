const WRITE_INDEX = 0;
const READ_INDEX = 1;
const DROPPED_COUNT = 2;
const CLOSED_FLAG = 3;

class CamelotVoiceCaptureProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const config = options.processorOptions ?? {};
    this.targetSampleRate = config.targetSampleRate ?? 16000;
    this.frameSamples = Math.min(1600, Math.max(160, config.frameSamples ?? 1600));
    this.vadThreshold = config.vadThreshold ?? 0.01;
    this.sequence = 0;
    this.accumulator = 0;
    this.frame = new Int16Array(this.frameSamples);
    this.frameOffset = 0;
    this.active = true;
    this.control = config.ring ? new Int32Array(config.ring.control) : null;
    this.ring = config.ring ? new Int16Array(config.ring.samples) : null;
    this.port.onmessage = (event) => {
      if (event.data?.type === "stop") this.active = false;
    };
  }

  writeShared(samples) {
    if (!this.control || !this.ring || Atomics.load(this.control, CLOSED_FLAG) === 1) return false;
    let write = Atomics.load(this.control, WRITE_INDEX);
    let read = Atomics.load(this.control, READ_INDEX);
    let discontinuity = false;
    for (let index = 0; index < samples.length; index += 1) {
      const next = (write + 1) % this.ring.length;
      if (next === read) {
        read = (read + 1) % this.ring.length;
        Atomics.store(this.control, READ_INDEX, read);
        Atomics.add(this.control, DROPPED_COUNT, 1);
        discontinuity = true;
      }
      this.ring[write] = samples[index];
      write = next;
    }
    Atomics.store(this.control, WRITE_INDEX, write);
    return discontinuity;
  }

  emitFrame() {
    let energy = 0;
    for (let index = 0; index < this.frame.length; index += 1) {
      const sample = this.frame[index] / 32768;
      energy += sample * sample;
    }
    const rms = Math.sqrt(energy / this.frame.length);
    const payload = {
      type: "frame",
      sequence: this.sequence++,
      timestampMs: currentTime * 1000,
      sampleCount: this.frame.length,
      discontinuity: false,
      speech: rms >= this.vadThreshold,
      rms,
    };
    if (this.ring) {
      payload.discontinuity = this.writeShared(this.frame);
      this.port.postMessage(payload);
    } else {
      const copy = this.frame.slice();
      this.port.postMessage({ ...payload, samples: copy.buffer }, [copy.buffer]);
    }
    this.frameOffset = 0;
  }

  process(inputs, outputs) {
    if (!this.active) return false;
    const input = inputs[0]?.[0];
    const output = outputs[0]?.[0];
    if (output) output.fill(0);
    if (!input) return true;
    for (let index = 0; index < input.length; index += 1) {
      this.accumulator += this.targetSampleRate;
      if (this.accumulator < sampleRate) continue;
      this.accumulator -= sampleRate;
      const sample = Math.max(-1, Math.min(1, input[index]));
      this.frame[this.frameOffset++] = sample < 0 ? Math.round(sample * 32768) : Math.round(sample * 32767);
      if (this.frameOffset === this.frame.length) this.emitFrame();
    }
    return true;
  }
}

registerProcessor("camelot-voice-capture", CamelotVoiceCaptureProcessor);
