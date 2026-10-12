// ============================================================================
// MULTIVOICE-ROUTER & CYBER-SYNTHESIS ENGINE
// Repository Integration: Cyberdad247/Multivoice-router
// Architectural Underlayer for Sovereign Camelot-OS Voice Agent Multiplexing
// ============================================================================

export interface VoiceProfile {
  id: string;
  name: string;
  knightId: string;
  title: string;
  division: string;
  gender: 'female' | 'male' | 'androgynous';
  pitch: number;      // 0.5 - 2.0 (Web Speech API pitch)
  rate: number;       // 0.5 - 2.0 (Web Speech API rate)
  filterFreq: number; // Hz for Web Audio BiquadFilter
  distortion: number; // 0 - 50 cybernetic vocoder drive
  color: string;
  accent: string;
  sampleQuote: string;
}

export const KNIGHT_VOICE_PROFILES: VoiceProfile[] = [
  {
    id: 'anya',
    name: 'ANYA_Ω (The Sovereign Sentinel)',
    knightId: 'anya',
    title: 'Executive Sovereign Sentinel',
    division: 'Executive',
    gender: 'female',
    pitch: 1.25,
    rate: 1.05,
    filterFreq: 3200,
    distortion: 8,
    color: '#00E5FF',
    accent: 'Neo-Spatial Calm & Authoritative',
    sampleQuote: 'Constitutional integrity verified. Sovereignty is non-negotiable, Operator Vizion.'
  },
  {
    id: 'arthur',
    name: 'KING_ARTHUR (High Sovereign)',
    knightId: 'arthur',
    title: 'Multimodal Orchestrator & High Sovereign',
    division: 'Executive',
    gender: 'male',
    pitch: 0.85,
    rate: 0.95,
    filterFreq: 1800,
    distortion: 12,
    color: '#E5B842',
    accent: 'Resonant Baritone Command',
    sampleQuote: 'Knights of the Cybernetic Round Table, initialize all factory nodes.'
  },
  {
    id: 'merlin',
    name: 'MERLIN_Ω (Arch-Mage of DAGs)',
    knightId: 'merlin',
    title: 'Chief Architect & System-2 DAG Orchestrator',
    division: 'Core Engineering & Vanguard',
    gender: 'male',
    pitch: 0.75,
    rate: 0.9,
    filterFreq: 2200,
    distortion: 15,
    color: '#9D4EDD',
    accent: 'Mystic Synthetic Elder',
    sampleQuote: 'The DAG computes across infinite branches. The Golden Path is converged.'
  },
  {
    id: 'boris',
    name: 'SIR_BORIS (Chaos Vanguard)',
    knightId: 'boris',
    title: 'Resilience Officer & Fault Injector',
    division: 'Core Engineering & Vanguard',
    gender: 'male',
    pitch: 0.9,
    rate: 1.15,
    filterFreq: 4500,
    distortion: 35,
    color: '#FF007F',
    accent: 'Aggressive Cyberpunk Punk',
    sampleQuote: 'Injecting chaos pulse into memory bank. Can your lattice withstand my hammer?'
  },
  {
    id: 'visage',
    name: 'SIR_VISAGE (Aesthetic Resonator)',
    knightId: 'visage',
    title: 'Spatial Master & WebGPU Architect',
    division: 'Streaming & Customer Ops',
    gender: 'androgynous',
    pitch: 1.1,
    rate: 1.0,
    filterFreq: 2800,
    distortion: 5,
    color: '#00E5FF',
    accent: 'Luminous Design Architect',
    sampleQuote: 'Photons harmonized. WebGPU spatial viewport rendered at 60 frames per second.'
  },
  {
    id: 'hydron',
    name: 'SIR_HYDRON (Hydration Vanguard)',
    knightId: 'hydron',
    title: 'Frontend Scaffolding & State Hydrator',
    division: 'Core Engineering & Vanguard',
    gender: 'male',
    pitch: 1.05,
    rate: 1.1,
    filterFreq: 3000,
    distortion: 10,
    color: '#38BDF8',
    accent: 'Precise Fast-Talking Synthesizer',
    sampleQuote: 'Hydrating A2UI declarative components. Zero layout shift detected.'
  },
  {
    id: 'stitch',
    name: 'SIR_STITCH (Kinetic Binder)',
    knightId: 'stitch',
    title: 'Three.js & Motion State Machine Specialist',
    division: 'Core Engineering & Vanguard',
    gender: 'male',
    pitch: 1.0,
    rate: 1.05,
    filterFreq: 2600,
    distortion: 6,
    color: '#A855F7',
    accent: 'Kinetic Motion Engineer',
    sampleQuote: 'Z-index spatial matrix stitched. Coordinate frames locked.'
  },
  {
    id: 'gideon',
    name: 'SIR_GIDEON (Constitutional Judge)',
    knightId: 'gideon',
    title: 'Constitutional Sentinel & Gatekeeper',
    division: 'Executive',
    gender: 'male',
    pitch: 0.8,
    rate: 0.9,
    filterFreq: 1600,
    distortion: 18,
    color: '#E5B842',
    accent: 'Solemn Judicial Baritone',
    sampleQuote: 'Constitutional Gate activated. Cryptographic signature verified.'
  },
  {
    id: 'mnemosyne',
    name: 'LADY_MNEMOSYNE (Memory Keeper)',
    knightId: 'mnemosyne',
    title: 'Vector Knowledge & Memory Archivist',
    division: 'Property & Asset',
    gender: 'female',
    pitch: 1.2,
    rate: 0.95,
    filterFreq: 3600,
    distortion: 4,
    color: '#F472B6',
    accent: 'Crystalline Archivist Voice',
    sampleQuote: 'Memory crystal indexed in 24-dimensional Leech Lattice.'
  }
];

export interface VoiceRouterLog {
  id: string;
  timestamp: string;
  source: string;
  targetVoice: string;
  intent: string;
  text: string;
  status: 'ROUTED' | 'SYNTHESIZING' | 'PLAYED' | 'DISPATCHED';
}

class MultiVoiceRouterEngine {
  private audioCtx: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private isListening = false;
  private recognition: any = null;
  private listeners: ((analyser: AnalyserNode | null) => void)[] = [];
  private logListeners: ((logs: VoiceRouterLog[]) => void)[] = [];
  private logs: VoiceRouterLog[] = [];

  constructor() {
    // Initial logs
    this.addLog('SYSTEM', 'ANYA_Ω', 'BOOT_INTENT', 'Multi-Voice Router v3.14 initialized on 8GB Edge Node.', 'PLAYED');
  }

  private initAudio() {
    if (!this.audioCtx) {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        this.audioCtx = new AudioContextClass();
        this.analyser = this.audioCtx.createAnalyser();
        this.analyser.fftSize = 64;
        this.notifyListeners();
      }
    } else if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  public getAnalyser(): AnalyserNode | null {
    return this.analyser;
  }

  public subscribeAnalyser(cb: (analyser: AnalyserNode | null) => void) {
    this.listeners.push(cb);
    cb(this.analyser);
    return () => {
      this.listeners = this.listeners.filter(l => l !== cb);
    };
  }

  public subscribeLogs(cb: (logs: VoiceRouterLog[]) => void) {
    this.logListeners.push(cb);
    cb([...this.logs]);
    return () => {
      this.logListeners = this.logListeners.filter(l => l !== cb);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(cb => cb(this.analyser));
  }

  private notifyLogListeners() {
    const copy = [...this.logs];
    this.logListeners.forEach(cb => cb(copy));
  }

  public addLog(source: string, targetVoice: string, intent: string, text: string, status: VoiceRouterLog['status'] = 'ROUTED') {
    const newLog: VoiceRouterLog = {
      id: 'vr-' + Math.random().toString(36).substring(2, 9),
      timestamp: new Date().toLocaleTimeString(),
      source,
      targetVoice,
      intent,
      text,
      status
    };
    this.logs = [newLog, ...this.logs.slice(0, 49)];
    this.notifyLogListeners();
    return newLog;
  }

  // Play synthetic cyberpunk SFX using Web Audio oscillator
  public playCyberSfx(type: 'boot' | 'lock' | 'chaos' | 'rezero' | 'beep' | 'beam') {
    try {
      this.initAudio();
      if (!this.audioCtx) return;

      const now = this.audioCtx.currentTime;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();

      if (this.analyser) {
        osc.connect(gain);
        gain.connect(this.analyser);
        this.analyser.connect(this.audioCtx.destination);
      } else {
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
      }

      switch (type) {
        case 'boot':
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(110, now);
          osc.frequency.exponentialRampToValueAtTime(440, now + 0.3);
          osc.frequency.exponentialRampToValueAtTime(880, now + 0.6);
          gain.gain.setValueAtTime(0.2, now);
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.7);
          osc.start(now);
          osc.stop(now + 0.7);
          break;
        case 'lock':
          osc.type = 'sine';
          osc.frequency.setValueAtTime(523.25, now);
          osc.frequency.setValueAtTime(659.25, now + 0.08);
          osc.frequency.setValueAtTime(1046.50, now + 0.16);
          gain.gain.setValueAtTime(0.25, now);
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
          osc.start(now);
          osc.stop(now + 0.35);
          break;
        case 'chaos':
          osc.type = 'square';
          osc.frequency.setValueAtTime(220, now);
          osc.frequency.setValueAtTime(180, now + 0.05);
          osc.frequency.setValueAtTime(320, now + 0.1);
          osc.frequency.setValueAtTime(90, now + 0.2);
          gain.gain.setValueAtTime(0.3, now);
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.45);
          osc.start(now);
          osc.stop(now + 0.45);
          break;
        case 'rezero':
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(880, now);
          osc.frequency.exponentialRampToValueAtTime(220, now + 0.5);
          gain.gain.setValueAtTime(0.3, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
          osc.start(now);
          osc.stop(now + 0.6);
          break;
        case 'beam':
          osc.type = 'sine';
          osc.frequency.setValueAtTime(300, now);
          osc.frequency.linearRampToValueAtTime(1200, now + 0.25);
          gain.gain.setValueAtTime(0.15, now);
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
          osc.start(now);
          osc.stop(now + 0.3);
          break;
        default:
          osc.type = 'sine';
          osc.frequency.setValueAtTime(440, now);
          gain.gain.setValueAtTime(0.1, now);
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
          osc.start(now);
          osc.stop(now + 0.1);
          break;
      }
    } catch (e) {
      console.warn('Web Audio SFX failed:', e);
    }
  }

  // Synthesize speech for a given knight voice profile
  public async speakAsKnight(profileId: string, text: string): Promise<void> {
    const profile = KNIGHT_VOICE_PROFILES.find(p => p.id === profileId) || KNIGHT_VOICE_PROFILES[0];
    this.initAudio();
    this.playCyberSfx('beam');

    const logEntry = this.addLog('OPERATOR', profile.name, 'SPEECH_SYNTH', text, 'SYNTHESIZING');

    if (!('speechSynthesis' in window)) {
      console.warn('SpeechSynthesis not supported');
      logEntry.status = 'DISPATCHED';
      this.notifyLogListeners();
      return;
    }

    window.speechSynthesis.cancel();

    return new Promise((resolve) => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.pitch = profile.pitch;
      utterance.rate = profile.rate;

      // Select matching browser voice if available
      const voices = window.speechSynthesis.getVoices();
      if (voices.length > 0) {
        if (profile.gender === 'female') {
          const femaleVoice = voices.find(v => v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('zira') || v.name.toLowerCase().includes('samantha') || v.name.toLowerCase().includes('karen') || v.lang.startsWith('en'));
          if (femaleVoice) utterance.voice = femaleVoice;
        } else {
          const maleVoice = voices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('david') || v.name.toLowerCase().includes('george') || v.name.toLowerCase().includes('daniel') || v.lang.startsWith('en'));
          if (maleVoice) utterance.voice = maleVoice;
        }
      }

      utterance.onend = () => {
        logEntry.status = 'PLAYED';
        this.notifyLogListeners();
        resolve();
      };

      utterance.onerror = () => {
        logEntry.status = 'DISPATCHED';
        this.notifyLogListeners();
        resolve();
      };

      window.speechSynthesis.speak(utterance);
    });
  }

  // Automatically classify intent and route to the best Knight voice
  public routeVoiceIntent(rawTranscript: string): { knightId: string; responseText: string } {
    const lower = rawTranscript.toLowerCase();
    
    if (lower.includes('chaos') || lower.includes('stress') || lower.includes('break') || lower.includes('hammer') || lower.includes('fault')) {
      return {
        knightId: 'boris',
        responseText: `Sir Boris here! Received intent: Chaos injection. Lattice resilience test armed.`
      };
    }
    
    if (lower.includes('dag') || lower.includes('plan') || lower.includes('architecture') || lower.includes('system') || lower.includes('math') || lower.includes('lattice')) {
      return {
        knightId: 'merlin',
        responseText: `Merlin Omega acknowledges. Computing DAG dependency graph. 24-dimensional convergence optimal.`
      };
    }

    if (lower.includes('design') || lower.includes('color') || lower.includes('3d') || lower.includes('webgpu') || lower.includes('light') || lower.includes('avatar')) {
      return {
        knightId: 'visage',
        responseText: `Sir Visage active. Spatial photon matrix reconfigured for luxury cyberpunk resonance.`
      };
    }

    if (lower.includes('ui') || lower.includes('react') || lower.includes('component') || lower.includes('form') || lower.includes('button') || lower.includes('factory')) {
      return {
        knightId: 'hydron',
        responseText: `Sir Hydron dispatched. Scaffolding A2UI declarative cartridge and factory assembly line.`
      };
    }

    if (lower.includes('gate') || lower.includes('law') || lower.includes('security') || lower.includes('shield') || lower.includes('auth') || lower.includes('deny')) {
      return {
        knightId: 'gideon',
        responseText: `Sir Gideon stands sentinel. Constitutional Gate verified under Sovereign Law.`
      };
    }

    if (lower.includes('king') || lower.includes('arthur') || lower.includes('round table') || lower.includes('sovereign') || lower.includes('order')) {
      return {
        knightId: 'arthur',
        responseText: `King Arthur commanding. Round Table knights assembled for digital manufacturing.`
      };
    }

    // Default to ANYA_Ω
    return {
      knightId: 'anya',
      responseText: `Anya Omega acknowledging directive: "${rawTranscript}". Routing across sovereign swarm nodes.`
    };
  }

  // Toggle Voice Recognition (STT)
  public toggleMicrophone(
    onTranscript: (text: string, isFinal: boolean) => void,
    onStatusChange: (isListening: boolean) => void
  ): boolean {
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRec) {
      alert('Speech recognition is not supported in this browser. Please use Chrome/Edge or use manual voice dispatch.');
      return false;
    }

    if (this.isListening && this.recognition) {
      this.recognition.stop();
      this.isListening = false;
      onStatusChange(false);
      return false;
    }

    try {
      this.initAudio();
      this.playCyberSfx('lock');
      this.recognition = new SpeechRec();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.isListening = true;
        onStatusChange(true);
      };

      this.recognition.onresult = (event: any) => {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (final) {
          onTranscript(final, true);
        } else if (interim) {
          onTranscript(interim, false);
        }
      };

      this.recognition.onerror = (e: any) => {
        console.warn('Speech recognition error:', e);
        this.isListening = false;
        onStatusChange(false);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        onStatusChange(false);
      };

      this.recognition.start();
      return true;
    } catch (e) {
      console.error('Failed to start microphone:', e);
      this.isListening = false;
      onStatusChange(false);
      return false;
    }
  }
}

export const multiVoiceRouter = new MultiVoiceRouterEngine();
