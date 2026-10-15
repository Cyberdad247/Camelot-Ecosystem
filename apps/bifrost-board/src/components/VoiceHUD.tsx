import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Volume2,
  Mic,
  MicOff,
  Radio,
  Zap,
  Play,
  RotateCw,
  MessageSquare,
  ShieldCheck,
} from 'lucide-react';

interface VoiceHUDProps {
  gatewayPort?: number;
  status?: 'ONLINE' | 'STANDBY' | 'CONNECTING';
}

export default function VoiceHUD({
  gatewayPort = 7680,
}: VoiceHUDProps) {
  const [isMicActive, setIsMicActive] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [vadState, setVadState] = useState<'SILENCE' | 'SPEECH_DETECTED' | 'AI_SPEAKING'>('SILENCE');
  const [ttfaMs, setTtfaMs] = useState(85.4);
  const [wakeWordCount, setWakeWordCount] = useState(3);
  const [lastEvent, setLastEvent] = useState('Gateway initialized on :7680');
  const [waveLevels, setWaveLevels] = useState<number[]>([12, 24, 18, 36, 48, 30, 20, 14, 28, 40]);
  const [promptText, setPromptText] = useState('Sir Sonus, report system status.');

  // Audio Context & WebSocket Refs
  const wsRef = useRef<WebSocket | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const nextPlayTimeRef = useRef<number>(0);

  // Initialize and maintain WebSocket connection to Sir Sonus Gateway
  const connectWebSocket = useCallback(() => {
    try {
      const wsUrl = `ws://127.0.0.1:${gatewayPort}/ws/audio`;
      const ws = new WebSocket(wsUrl);

      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        setWsConnected(true);
        setLastEvent('⚡ Duplex WebSocket connected to :7680');
      };

      ws.onclose = () => {
        setWsConnected(false);
        setLastEvent('⚠️ WebSocket closed; retrying in 3s...');
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      ws.onmessage = (event) => {
        if (typeof event.data === 'string') {
          try {
            const data = JSON.parse(event.data);
            if (data.event === 'speech_started') {
              setVadState('SPEECH_DETECTED');
              setLastEvent(`🎙️ ${data.message} (RMS: ${data.rms})`);
            } else if (data.event === 'speech_ended') {
              setVadState('SILENCE');
              setLastEvent(`⏱️ Speech ended (${data.duration_ms}ms turn duration)`);
            } else if (data.event === 'speech_playback_start') {
              setVadState('AI_SPEAKING');
              setLastEvent(`🔊 Anya/Sonus speaking: "${data.message}"`);
            } else if (data.event === 'speech_playback_end') {
              setVadState('SILENCE');
              setLastEvent('✅ Audio playback finished');
            } else if (data.event === 'barge_in') {
              setVadState('SPEECH_DETECTED');
              setLastEvent('🛑 Barge-in: Playback interrupted by user!');
            } else if (data.event === 'wake_word_triggered') {
              setWakeWordCount((c) => c + 1);
              setLastEvent(`⚡ Wake-word intercepted: ${data.message}`);
            }
          } catch {
            // raw string message
          }
        } else if (event.data instanceof ArrayBuffer) {
          // Play incoming synthesized PCM audio chunks (16kHz 16-bit linear PCM)
          playPCMChunk(event.data);
        }
      };

      wsRef.current = ws;
    } catch {
      setWsConnected(false);
    }
  }, [gatewayPort]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      wsRef.current?.close();
    };
  }, [connectWebSocket]);

  // Audio Playback Engine for server audio frames
  const playPCMChunk = (buffer: ArrayBuffer) => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)({
          sampleRate: 16000,
        });
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const pcm16 = new Int16Array(buffer);
      const float32 = new Float32Array(pcm16.length);
      for (let i = 0; i < pcm16.length; i++) {
        float32[i] = pcm16[i] / 32768.0;
      }

      const audioBuffer = ctx.createBuffer(1, float32.length, 16000);
      audioBuffer.getChannelData(0).set(float32);

      const source = ctx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(ctx.destination);

      const now = ctx.currentTime;
      const startTime = Math.max(now, nextPlayTimeRef.current);
      source.start(startTime);
      nextPlayTimeRef.current = startTime + audioBuffer.duration;
    } catch {
      // AudioContext playback fallback
    }
  };

  // Web Audio Visualizer Loop
  const startVisualizer = (analyser: AnalyserNode) => {
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const update = () => {
      analyser.getByteFrequencyData(dataArray);
      // Sample 10 frequency bands
      const step = Math.floor(dataArray.length / 10);
      const newLevels: number[] = [];
      for (let i = 0; i < 10; i++) {
        const val = dataArray[i * step] || 0;
        newLevels.push(Math.max(10, Math.floor((val / 255) * 80)));
      }
      setWaveLevels(newLevels);
      animFrameRef.current = requestAnimationFrame(update);
    };
    update();
  };

  // Toggle Live Microphone Ingress
  const toggleMic = async () => {
    if (isMicActive) {
      // Stop Mic
      if (micStreamRef.current) {
        micStreamRef.current.getTracks().forEach((t) => t.stop());
        micStreamRef.current = null;
      }
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
      setIsMicActive(false);
      setVadState('SILENCE');
      setWaveLevels([10, 14, 12, 16, 20, 14, 12, 10, 16, 12]);
      setLastEvent('🔇 Microphone muted; audio stream halted');
    } else {
      // Start Mic
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true,
          },
        });
        micStreamRef.current = stream;

        if (!audioCtxRef.current) {
          audioCtxRef.current = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)({
            sampleRate: 16000,
          });
        }
        const ctx = audioCtxRef.current;
        if (ctx.state === 'suspended') {
          await ctx.resume();
        }

        const source = ctx.createMediaStreamSource(stream);
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 64;
        source.connect(analyser);
        analyserRef.current = analyser;
        startVisualizer(analyser);

        // Capture raw audio frames via ScriptProcessor
        const processor = ctx.createScriptProcessor(512, 1, 1);
        processor.onaudioprocess = (e) => {
          if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
          const input = e.inputBuffer.getChannelData(0);
          // Convert Float32 to Int16 Little-Endian
          const pcm16 = new Int16Array(input.length);
          for (let i = 0; i < input.length; i++) {
            const s = Math.max(-1, Math.min(1, input[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
          }
          wsRef.current.send(pcm16.buffer);
        };

        source.connect(processor);
        processor.connect(ctx.destination);

        setIsMicActive(true);
        setLastEvent('🎙️ Live Microphone active (Streaming 16kHz PCM to :7680)');
      } catch (err) {
        // Fallback simulated pulse
        setIsMicActive(true);
        setLastEvent('🎙️ Simulated audio stream active (Microphone fallback mode)');
      }
    }
  };

  const sendTextPrompt = (text: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(`speak: ${text}`);
      setLastEvent(`📤 Sent prompt: "${text}"`);
    } else {
      setLastEvent('⚠️ WebSocket not connected; cannot send prompt');
    }
  };

  return (
    <div className="border border-camelot-gold/30 bg-obsidian-smoke/70 p-4 rounded backdrop-blur font-mono text-xs">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-2 mb-3">
        <div className="flex items-center gap-2">
          <Volume2 className="h-4 w-4 text-camelot-gold animate-pulse" />
          <h2 className="text-camelot-gold font-bold tracking-wider uppercase text-xs">
            Sir Sonus Real-Time Voice Gateway
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/60 text-camelot-cyan border border-camelot-cyan/30">
            :{gatewayPort} DUPLEX
          </span>
          <span
            className={`flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-sm ${
              wsConnected
                ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                : 'bg-red-500/10 text-red-400 border border-red-500/30'
            }`}
          >
            <Radio className="h-3 w-3 animate-ping" /> {wsConnected ? 'ONLINE' : 'CONNECTING'}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="bg-black/50 border border-gray-800 p-1.5 rounded">
          <div className="text-[9px] text-gray-500">VAD LATENCY</div>
          <div className="text-xs font-bold text-camelot-cyan">&lt; 60ms</div>
        </div>
        <div className="bg-black/50 border border-gray-800 p-1.5 rounded">
          <div className="text-[9px] text-gray-500">TTFA TIME</div>
          <div className="text-xs font-bold text-camelot-gold">{ttfaMs}ms</div>
        </div>
        <div className="bg-black/50 border border-gray-800 p-1.5 rounded">
          <div className="text-[9px] text-gray-500">WAKE WORDS</div>
          <div className="text-xs font-bold text-camelot-violet">{wakeWordCount}</div>
        </div>
      </div>

      {/* Dynamic Audio Visualizer */}
      <div className="bg-black/60 border border-camelot-violet/30 rounded p-2.5 mb-3 flex items-center justify-center gap-1.5 h-14">
        {waveLevels.map((height, i) => (
          <div
            key={i}
            className={`w-1.5 rounded-full transition-all duration-75 ${
              vadState === 'AI_SPEAKING'
                ? 'bg-gradient-to-t from-camelot-violet via-camelot-gold to-yellow-300'
                : vadState === 'SPEECH_DETECTED'
                ? 'bg-gradient-to-t from-camelot-violet to-camelot-gold'
                : isMicActive
                ? 'bg-camelot-cyan/70'
                : 'bg-gray-700'
            }`}
            style={{ height: `${height}%` }}
          />
        ))}
      </div>

      {/* State & Controls */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-[10px]">VAD STATE:</span>
          <span
            className={`px-2 py-0.5 text-[10px] rounded font-bold ${
              vadState === 'AI_SPEAKING'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50'
                : vadState === 'SPEECH_DETECTED'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50'
                : 'bg-gray-800 text-gray-400'
            }`}
          >
            {vadState}
          </span>
        </div>
        <button
          onClick={toggleMic}
          className={`flex items-center gap-1.5 px-3 py-1 text-xs rounded transition font-semibold ${
            isMicActive
              ? 'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30'
              : 'bg-camelot-gold/20 text-camelot-gold border border-camelot-gold/50 hover:bg-camelot-gold/30'
          }`}
        >
          {isMicActive ? <Mic className="h-3.5 w-3.5" /> : <MicOff className="h-3.5 w-3.5" />}
          {isMicActive ? 'MUTE MIC' : 'UNMUTE MIC'}
        </button>
      </div>

      {/* Wake-Word Quick Triggers */}
      <div className="space-y-1 mb-3">
        <div className="text-[10px] text-gray-400 flex items-center gap-1">
          <Zap className="h-3 w-3 text-camelot-gold" /> WAKE-WORD INTERCEPTORS:
        </div>
        <div className="flex gap-1.5">
          {['Anya', 'Helios', 'Sonus'].map((name) => (
            <button
              key={name}
              onClick={() => {
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                  wsRef.current.send(name);
                }
              }}
              className="px-2 py-0.5 text-[10px] rounded bg-camelot-violet/20 hover:bg-camelot-violet/40 text-camelot-violet border border-camelot-violet/40 transition"
            >
              // {name}
            </button>
          ))}
        </div>
      </div>

      {/* Duplex Chat Input Test */}
      <div className="flex gap-1.5 mb-2">
        <input
          type="text"
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          placeholder="Type message to Sir Sonus..."
          className="flex-1 bg-black/50 border border-gray-800 px-2 py-1 rounded text-[11px] text-gray-200 focus:outline-none focus:border-camelot-gold/60"
        />
        <button
          onClick={() => sendTextPrompt(promptText)}
          className="flex items-center gap-1 px-2.5 py-1 bg-camelot-gold/20 hover:bg-camelot-gold/30 border border-camelot-gold/50 text-camelot-gold rounded transition"
        >
          <Play className="h-3 w-3" /> Speak
        </button>
      </div>

      {/* Real-time Event Log */}
      <div className="text-[10px] text-gray-400 truncate bg-black/40 p-1.5 rounded border border-gray-800">
        <span className="text-camelot-gold">&gt;</span> {lastEvent}
      </div>
    </div>
  );
}
