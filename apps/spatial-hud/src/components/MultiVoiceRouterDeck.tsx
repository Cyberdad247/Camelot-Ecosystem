import React, { useState, useEffect, useRef } from 'react';
import { 
  multiVoiceRouter, 
  KNIGHT_VOICE_PROFILES, 
  VoiceProfile, 
  VoiceRouterLog 
} from '../services/multiVoiceRouter';
import { ThemeMode } from '../types';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Radio, 
  Sparkles, 
  Send, 
  Layers, 
  Zap, 
  Activity, 
  Sliders, 
  Cpu 
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface MultiVoiceRouterDeckProps {
  theme?: ThemeMode;
  onExecuteIntent?: (intent: string) => void;
}

export const MultiVoiceRouterDeck: React.FC<MultiVoiceRouterDeckProps> = ({
  theme = 'dark',
  onExecuteIntent
}) => {
  const isDark = theme === 'dark';
  
  const [selectedVoice, setSelectedVoice] = useState<VoiceProfile>(KNIGHT_VOICE_PROFILES[0]);
  const [isListening, setIsListening] = useState(false);
  const [customText, setCustomText] = useState('');
  const [voiceLogs, setVoiceLogs] = useState<VoiceRouterLog[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [lastTranscript, setLastTranscript] = useState('');
  const [routedAgent, setRoutedAgent] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Subscribe to logs
  useEffect(() => {
    const unsubLogs = multiVoiceRouter.subscribeLogs((logs) => {
      setVoiceLogs(logs);
    });
    return unsubLogs;
  }, []);

  // Real-time Canvas Waveform / Spectrum Visualizer Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    const bufferLength = 64;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      animId = requestAnimationFrame(draw);
      const analyser = multiVoiceRouter.getAnalyser();

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (analyser) {
        analyser.getByteFrequencyData(dataArray);
      } else {
        // Ambient fallback wave
        for (let i = 0; i < bufferLength; i++) {
          dataArray[i] = Math.sin(Date.now() * 0.005 + i * 0.2) * 40 + 60;
        }
      }

      const barWidth = (canvas.width / bufferLength) * 1.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height;

        const grad = ctx.createLinearGradient(0, canvas.height, 0, 0);
        grad.addColorStop(0, isDark ? '#00E5FF' : '#0284c7');
        grad.addColorStop(0.5, isDark ? '#9D4EDD' : '#7c3aed');
        grad.addColorStop(1, isDark ? '#FF007F' : '#db2777');

        ctx.fillStyle = grad;
        ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
        x += barWidth;
      }
    };

    draw();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [isDark]);

  // Handle STT Microphone toggle
  const handleToggleMic = () => {
    multiVoiceRouter.toggleMicrophone(
      (transcript, isFinal) => {
        setLastTranscript(transcript);
        if (isFinal) {
          const routeResult = multiVoiceRouter.routeVoiceIntent(transcript);
          setRoutedAgent(routeResult.knightId);
          multiVoiceRouter.speakAsKnight(routeResult.knightId, routeResult.responseText);
          if (onExecuteIntent) {
            onExecuteIntent(transcript);
          }
        }
      },
      (listening) => {
        setIsListening(listening);
      }
    );
  };

  // Handle Manual Speech Trigger
  const handleSpeak = async () => {
    if (!customText.trim()) return;
    setIsSpeaking(true);
    await multiVoiceRouter.speakAsKnight(selectedVoice.id, customText);
    setIsSpeaking(false);
    setCustomText('');
  };

  // Quick dispatch quote
  const handleQuoteClick = async (profile: VoiceProfile) => {
    setSelectedVoice(profile);
    setIsSpeaking(true);
    await multiVoiceRouter.speakAsKnight(profile.id, profile.sampleQuote);
    setIsSpeaking(false);
  };

  return (
    <div className={`w-full border p-4 lg:p-6 backdrop-blur-md flex flex-col gap-6 ${
      isDark 
        ? 'bg-[#080511]/90 border-cyan-500/30 text-white shadow-2xl' 
        : 'bg-white/95 border-cyan-600/30 text-slate-900 shadow-xl'
    }`}>
      
      {/* HEADER: MULTIVOICE ROUTER TITLE & REPO BADGE */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b pb-4 border-cyan-500/20">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-none text-black font-bold shadow-lg shadow-cyan-500/20">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-black tracking-widest uppercase font-mono">
                MULTIVOICE-ROUTER ENGINE
              </h2>
              <span className={`text-[10px] px-2 py-0.5 font-mono font-bold border ${
                isDark ? 'bg-purple-950/80 border-purple-500 text-purple-300' : 'bg-purple-100 border-purple-400 text-purple-800'
              }`}>
                Cyberdad247/Multivoice-router
              </span>
            </div>
            <p className="text-xs opacity-75 font-mono mt-0.5">
              Real-time Web Audio Synthesizer & Sovereign Knight Voice Multiplexer
            </p>
          </div>
        </div>

        {/* Live Status Indicators */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className={`px-2.5 py-1 border flex items-center gap-1.5 ${
            isListening 
              ? 'bg-rose-500/20 border-rose-500 text-rose-400 animate-pulse' 
              : isDark ? 'bg-[#0E091D] border-cyan-500/30 text-cyan-400' : 'bg-cyan-50 border-cyan-300 text-cyan-800'
          }`}>
            <span className={`w-2 h-2 rounded-full ${isListening ? 'bg-rose-500' : 'bg-cyan-400'}`} />
            <span>MIC: {isListening ? 'LIVE BROADCAST' : 'STANDBY'}</span>
          </div>

          <button
            onClick={handleToggleMic}
            className={`px-3 py-1 text-xs font-bold font-mono border transition-all flex items-center gap-1.5 active:scale-95 ${
              isListening
                ? 'bg-rose-600 hover:bg-rose-700 text-white border-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.5)]'
                : 'bg-cyan-500 hover:bg-cyan-400 text-black border-cyan-300 shadow-[0_0_10px_rgba(0,229,255,0.3)]'
            }`}
          >
            {isListening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
            <span>{isListening ? 'STOP MIC' : 'LISTEN (STT)'}</span>
          </button>
        </div>
      </div>

      {/* TOP GRID: WAVEFORM OSCILLOSCOPE & QUICK SFX GENERATOR */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        
        {/* Real-time Oscilloscope Canvas (Cols 1-2) */}
        <div className={`lg:col-span-2 border p-3 flex flex-col justify-between ${
          isDark ? 'bg-[#050507] border-cyan-500/20' : 'bg-slate-50 border-slate-300'
        }`}>
          <div className="flex items-center justify-between text-[10px] font-mono mb-2">
            <span className={isDark ? 'text-cyan-400 font-bold' : 'text-cyan-700 font-bold'}>
              AUDIO_SPECTRUM_OSCILLOSCOPE // 64-BAND FFT
            </span>
            <span className="opacity-70 font-mono">SAMPLING: 44.1 kHz</span>
          </div>

          <div className="w-full h-24 relative overflow-hidden bg-black/40 border border-cyan-500/10">
            <canvas ref={canvasRef} width={500} height={96} className="w-full h-full block" />
          </div>

          {lastTranscript && (
            <div className={`mt-2 p-2 border text-[11px] font-mono flex items-center justify-between ${
              isDark ? 'bg-purple-950/40 border-purple-500/40 text-purple-200' : 'bg-purple-50 border-purple-300 text-purple-900'
            }`}>
              <span>TRANSCRIPT: "{lastTranscript}"</span>
              {routedAgent && (
                <span className="font-bold text-amber-400">ROUTED TO: {routedAgent.toUpperCase()}</span>
              )}
            </div>
          )}
        </div>

        {/* Synthetic Cyberpunk SFX Rack */}
        <div className={`border p-3 flex flex-col justify-between ${
          isDark ? 'bg-[#050507] border-purple-500/20' : 'bg-slate-50 border-slate-300'
        }`}>
          <div className="text-[10px] font-mono font-bold text-purple-400 mb-2 flex items-center justify-between">
            <span>WEB AUDIO SFX HARNESS</span>
            <Sparkles className="w-3 h-3 text-amber-400" />
          </div>

          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
            <button
              onClick={() => multiVoiceRouter.playCyberSfx('boot')}
              className={`p-2 border font-bold transition-all active:scale-95 ${
                isDark ? 'bg-cyan-500/10 hover:bg-cyan-500/20 border-cyan-500/40 text-cyan-300' : 'bg-cyan-100 hover:bg-cyan-200 border-cyan-300 text-cyan-900'
              }`}
            >
              //sfx:boot
            </button>
            <button
              onClick={() => multiVoiceRouter.playCyberSfx('lock')}
              className={`p-2 border font-bold transition-all active:scale-95 ${
                isDark ? 'bg-amber-500/10 hover:bg-amber-500/20 border-amber-500/40 text-amber-300' : 'bg-amber-100 hover:bg-amber-200 border-amber-300 text-amber-900'
              }`}
            >
              //sfx:lock_on
            </button>
            <button
              onClick={() => multiVoiceRouter.playCyberSfx('chaos')}
              className={`p-2 border font-bold transition-all active:scale-95 ${
                isDark ? 'bg-rose-500/10 hover:bg-rose-500/20 border-rose-500/40 text-rose-300' : 'bg-rose-100 hover:bg-rose-200 border-rose-300 text-rose-900'
              }`}
            >
              //sfx:chaos_pulse
            </button>
            <button
              onClick={() => multiVoiceRouter.playCyberSfx('rezero')}
              className={`p-2 border font-bold transition-all active:scale-95 ${
                isDark ? 'bg-purple-500/10 hover:bg-purple-500/20 border-purple-500/40 text-purple-300' : 'bg-purple-100 hover:bg-purple-200 border-purple-300 text-purple-900'
              }`}
            >
              //sfx:rezero_hum
            </button>
          </div>

          <div className="text-[9px] font-mono opacity-60 mt-2 text-center">
            Zero external audio assets. 100% Web Audio API oscillator synthesis.
          </div>
        </div>
      </div>

      {/* MIDDLE SECTION: KNIGHT VOICE CHANNELS MATRIX */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="font-bold uppercase tracking-wider text-cyan-400">
            ACTIVE VOICE MULTIPLEX CHANNELS ({KNIGHT_VOICE_PROFILES.length} PROFILES)
          </span>
          <span className="opacity-70 text-[11px]">Click voice to preview synthesis</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {KNIGHT_VOICE_PROFILES.map((profile) => {
            const isSelected = selectedVoice.id === profile.id;
            return (
              <div
                key={profile.id}
                onClick={() => handleQuoteClick(profile)}
                className={`p-3 border cursor-pointer transition-all ${
                  isSelected 
                    ? isDark 
                      ? 'bg-[#150E24] border-cyan-400 shadow-[0_0_12px_rgba(0,229,255,0.2)]' 
                      : 'bg-cyan-50 border-cyan-500 shadow-md'
                    : isDark 
                      ? 'bg-[#0A0710]/70 border-white/10 hover:border-cyan-500/40' 
                      : 'bg-white border-slate-200 hover:border-cyan-400'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold font-mono" style={{ color: profile.color }}>
                    {profile.name}
                  </span>
                  <span className={`text-[9px] px-1.5 py-0.2 font-mono border ${
                    isDark ? 'bg-black/50 border-white/20 text-neutral-300' : 'bg-slate-100 border-slate-300 text-slate-700'
                  }`}>
                    {profile.division}
                  </span>
                </div>

                <div className="text-[10px] opacity-75 font-mono mb-2">
                  Pitch: {profile.pitch}x | Rate: {profile.rate}x | {profile.accent}
                </div>

                <p className="text-[10px] italic leading-snug opacity-90 line-clamp-2 border-l-2 pl-2 border-cyan-500/40">
                  "{profile.sampleQuote}"
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* BOTTOM ROW: TEXT-TO-SPEECH DISPATCH & LIVE VOICE ROUTING LOGS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2">
        
        {/* Custom Synthesizer Input */}
        <div className={`border p-4 flex flex-col justify-between ${
          isDark ? 'bg-[#050507] border-cyan-500/20' : 'bg-slate-50 border-slate-300'
        }`}>
          <div className="flex items-center justify-between text-xs font-mono mb-2">
            <span className="font-bold text-cyan-400">MANUAL VOICE DISPATCH (TTS)</span>
            <span className="text-[10px] text-amber-400 font-mono">SELECTED: {selectedVoice.name}</span>
          </div>

          <textarea
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            placeholder={`Enter text to synthesize in ${selectedVoice.name}'s voice profile...`}
            rows={3}
            className={`w-full p-2.5 text-xs font-mono border focus:outline-none mb-3 ${
              isDark 
                ? 'bg-[#0E091D] border-cyan-500/40 text-white placeholder-neutral-500 focus:border-cyan-400' 
                : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:border-cyan-600'
            }`}
          />

          <div className="flex items-center justify-between gap-3">
            <div className="text-[10px] font-mono opacity-70">
              Web Speech API + Biquad Filter Envelope
            </div>

            <button
              onClick={handleSpeak}
              disabled={isSpeaking || !customText.trim()}
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-black font-bold font-mono text-xs border border-cyan-300 transition-all flex items-center gap-1.5 active:scale-95 disabled:opacity-50"
            >
              <Volume2 className="w-4 h-4" />
              <span>{isSpeaking ? 'SYNTHESIZING...' : 'SYNTHESIZE SPEECH'}</span>
            </button>
          </div>
        </div>

        {/* Voice Router Logs */}
        <div className={`border p-4 flex flex-col justify-between ${
          isDark ? 'bg-[#050507] border-purple-500/20' : 'bg-slate-50 border-slate-300'
        }`}>
          <div className="flex items-center justify-between text-xs font-mono mb-2">
            <span className="font-bold text-purple-400">VOICE ROUTER EVENT STREAM</span>
            <span className="text-[10px] text-emerald-400 font-bold">ROUTER: ACTIVE</span>
          </div>

          <div className="space-y-2 max-h-36 overflow-y-auto pr-1 font-mono text-[10px]">
            {voiceLogs.map((log) => (
              <div
                key={log.id}
                className={`p-1.5 border flex items-center justify-between ${
                  isDark ? 'bg-[#0E091D] border-white/10 text-neutral-300' : 'bg-white border-slate-200 text-slate-800'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="opacity-50 text-[9px]">{log.timestamp}</span>
                  <span className="font-bold text-cyan-400">{log.targetVoice}</span>
                  <span className="opacity-80 line-clamp-1">"{log.text}"</span>
                </div>
                <span className="text-[8px] px-1 py-0.2 bg-purple-950 text-purple-300 border border-purple-600">
                  {log.status}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
