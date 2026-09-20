const WRITE_INDEX = 0;
const READ_INDEX = 1;
const DROPPED_COUNT = 2;
const CLOSED_FLAG = 3;

export type SharedPcmRingHandles = {
  control: SharedArrayBuffer;
  samples: SharedArrayBuffer;
  capacity: number;
};

export class SharedPcmRing {
  readonly handles: SharedPcmRingHandles;
  private readonly control: Int32Array;
  private readonly samples: Int16Array;

  constructor(capacitySamples = 32_000) {
    if (!Number.isInteger(capacitySamples) || capacitySamples < 3_200) {
      throw new Error("PCM ring capacity must be at least 3,200 samples.");
    }
    const control = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 4);
    const samples = new SharedArrayBuffer(Int16Array.BYTES_PER_ELEMENT * capacitySamples);
    this.handles = { control, samples, capacity: capacitySamples };
    this.control = new Int32Array(control);
    this.samples = new Int16Array(samples);
  }

  read(maxSamples: number): Int16Array {
    const write = Atomics.load(this.control, WRITE_INDEX);
    let read = Atomics.load(this.control, READ_INDEX);
    const available = write >= read ? write - read : this.samples.length - read + write;
    const count = Math.min(Math.max(0, maxSamples), available);
    const output = new Int16Array(count);
    for (let index = 0; index < count; index += 1) {
      output[index] = this.samples[read];
      read = (read + 1) % this.samples.length;
    }
    Atomics.store(this.control, READ_INDEX, read);
    return output;
  }

  droppedSamples(): number {
    return Atomics.load(this.control, DROPPED_COUNT);
  }

  close(): void {
    Atomics.store(this.control, CLOSED_FLAG, 1);
  }
}

export function sharedPcmAvailable(): boolean {
  return typeof SharedArrayBuffer !== "undefined" && globalThis.crossOriginIsolated === true;
}
