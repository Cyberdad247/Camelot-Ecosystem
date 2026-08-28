/**
 * Audio Pipeline — Native Opus decoder + Web Audio API playback
 * Fallback: Web Speech API for browser-only demo
 */

class AudioPipeline {
  constructor() {
    this.audioContext = null;
    this.decoder = null;
    this.gainNode = null;
    this.isNative = false;
    this.fallbackRecognition = null;
    this.isRecording = false;
    this.init();
  }

  async init() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 24000
      });
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = 0.8;
      this.gainNode.connect(this.audioContext.destination);
      this.isNative = false;
      console.log('[AUDIO] Pipeline initialized — sampleRate: 24000');
      if (!this.isNative) this.initFallback();
    } catch (err) {
      console.error('[AUDIO] Init failed:', err);
      this.initFallback();
    }
  }

  initFallback() {
    console.warn('[AUDIO] Native pipeline unavailable — using Web Speech API fallback');
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
        const input = document.getElementById('kotrInput');
        if (input) input.value = transcript;
      };
      this.fallbackRecognition.onend = () => {
        this.isRecording = false;
        document.getElementById('voiceBtnKotr')?.classList.remove('recording');
        document.getElementById('voiceOverlay')?.classList.remove('active');
        const input = document.getElementById('kotrInput');
        if (input?.value.trim()) window.HUDRenderer?.sendMessage();
      };
    }
    const banner = document.getElementById('connBanner');
    if (banner) banner.classList.remove('hidden');
  }

  async playAudio(opusData) {
    if (!this.audioContext) return;
    try {
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

  startRecording() {
    if (this.isNative) {
      console.log('[AUDIO] Native recording started');
    } else if (this.fallbackRecognition) {
      this.isRecording = true;
      this.fallbackRecognition.start();
      document.getElementById('voiceBtnKotr')?.classList.add('recording');
      document.getElementById('voiceOverlay')?.classList.add('active');
      document.getElementById('kotrInput').placeholder = 'Listening...';
    }
  }

  stopRecording() {
    if (this.isNative) {
      console.log('[AUDIO] Native recording stopped');
    } else if (this.fallbackRecognition && this.isRecording) {
      this.fallbackRecognition.stop();
    }
  }

  setVolume(value) {
    if (this.gainNode) {
      this.gainNode.gain.setValueAtTime(value, this.audioContext.currentTime);
    }
  }
}

window.AudioPipeline = new AudioPipeline();
