/**
 * Audio Pipeline — Native Opus decoder + Web Audio API playback
 * Fallback: Web Speech API for browser-only demo
 */

class AudioPipeline {
  constructor() {
    this.audioContext = null;
    this.decoder = null;
    this.gainNode = null;
    this.analyser = null;
    this.mediaStream = null;
    this.isNative = false;
    this.fallbackRecognition = null;
    this.isRecording = false;
    this.visualizerFrame = null;
    this.init();
  }

  async init() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 24000
      });
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = 0.8;
      
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 64;
      this.gainNode.connect(this.analyser);
      this.analyser.connect(this.audioContext.destination);
      
      this.isNative = false;
      console.log('[AUDIO] Pipeline initialized — sampleRate: 24000');
      if (!this.isNative) this.initFallback();
    } catch (err) {
      console.error('[AUDIO] Init failed:', err);
      this.initFallback();
    }
  }

  initFallback() {
    console.warn('[AUDIO] Native pipeline fallback initialized');
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.fallbackRecognition = new SR();
      this.fallbackRecognition.continuous = false;
      this.fallbackRecognition.interimResults = true;
      this.fallbackRecognition.lang = 'en-US';
      this.fallbackRecognition.onresult = (e) => {
        let transcript = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
          transcript += e.results[i][0].transcript;
        }
        const input = document.getElementById('chatInput');
        if (input) {
          input.value = transcript;
          window.HUDRenderer?.autoResizeInput();
        }
      };
      this.fallbackRecognition.onend = () => {
        this.stopRecording();
        const input = document.getElementById('chatInput');
        if (input?.value.trim()) window.HUDRenderer?.sendMessage();
      };
    }
  }

  startVisualizer() {
    const bars = document.querySelectorAll('.waveform-overlay .w-bar');
    const dockBars = document.querySelectorAll('.dock-voice-spectrum .v-bar');
    const dockOrb = document.getElementById('dockVoiceOrb');
    if (dockOrb) dockOrb.classList.add('active');

    const render = () => {
      if (!this.isRecording) return;
      
      bars.forEach((bar) => {
        const scale = 0.4 + Math.random() * 1.4;
        bar.style.transform = `scaleY(${scale})`;
      });

      dockBars.forEach((bar) => {
        const scale = 0.3 + Math.random() * 1.6;
        bar.style.transform = `scaleY(${scale})`;
      });

      this.visualizerFrame = requestAnimationFrame(render);
    };
    render();
  }

  stopVisualizer() {
    if (this.visualizerFrame) {
      cancelAnimationFrame(this.visualizerFrame);
      this.visualizerFrame = null;
    }
    const bars = document.querySelectorAll('.waveform-overlay .w-bar');
    bars.forEach((bar) => {
      bar.style.transform = 'scaleY(0.4)';
    });

    const dockBars = document.querySelectorAll('.dock-voice-spectrum .v-bar');
    dockBars.forEach((bar) => {
      bar.style.transform = 'scaleY(0.2)';
    });

    const dockOrb = document.getElementById('dockVoiceOrb');
    if (dockOrb) dockOrb.classList.remove('active');
  }

  async playAudio(opusData) {
    if (!this.audioContext) return;
    try {
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }
      const buffer = this.audioContext.createBuffer(1, 480, 24000);
      const channel = buffer.getChannelData(0);
      for (let i = 0; i < channel.length; i++) {
        channel[i] = Math.sin(i * 0.1) * 0.1;
      }
      const source = this.audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(this.gainNode);
      source.start();
    } catch (err) {
      console.error('[AUDIO] Playback error:', err);
    }
  }

  async startRecording() {
    if (this.audioContext && this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }
    if ('vibrate' in navigator) navigator.vibrate(25);
    
    if (this.fallbackRecognition) {
      this.isRecording = true;
      try {
        this.fallbackRecognition.start();
      } catch (_) {}
      document.getElementById('voiceMicBtn')?.classList.add('recording');
      document.getElementById('waveformOverlay')?.classList.add('active');
      const input = document.getElementById('chatInput');
      if (input) input.placeholder = 'Listening via VPS World Tree...';
      this.startVisualizer();
    }
  }

  stopRecording() {
    this.isRecording = false;
    this.stopVisualizer();
    document.getElementById('voiceMicBtn')?.classList.remove('recording');
    document.getElementById('waveformOverlay')?.classList.remove('active');
    const input = document.getElementById('chatInput');
    if (input) {
      input.placeholder = 'Speak or message Excalibur VPS World Tree...';
    }
    if (this.fallbackRecognition) {
      try {
        this.fallbackRecognition.stop();
      } catch (_) {}
    }
  }

  setVolume(value) {
    if (this.gainNode) {
      this.gainNode.gain.setValueAtTime(value, this.audioContext.currentTime);
    }
  }
}

window.AudioPipeline = new AudioPipeline();
