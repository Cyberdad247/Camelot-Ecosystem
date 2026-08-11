class VocalEnclaveProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bufferSize = 2048;
    this.buffer = new Float32Array(this.bufferSize);
    this.pointer = 0;
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (input.length > 0) {
      const channelData = input[0];
      for (let i = 0; i < channelData.length; i++) {
        this.buffer[this.pointer++] = channelData[i];
        if (this.pointer >= this.bufferSize) {
          // Send buffer to main thread
          this.port.postMessage({
            eventType: 'audio_data',
            pcmData: new Float32Array(this.buffer)
          });
          this.pointer = 0; // reset
        }
      }
    }
    return true; // Keep processor alive
  }
}

registerProcessor('vocal_enclave_processor', VocalEnclaveProcessor);
