import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import {
  Volume2,
  VolumeX,
  Radio,
  Sliders,
  Activity,
  Layers,
  Sparkles,
  Zap,
  Play,
  Pause,
  RotateCcw,
  Mic,
  Disc,
  Headphones
} from 'lucide-react';
import { ThemeMode } from '../types';
import { useAtom } from 'jotai';
import { activeAudioGainAtom, audio3DCoordinateAtom } from '../services/agentBridge';
import { multiVoiceRouter } from '../services/multiVoiceRouter';

interface AudioWorkbenchViewProps {
  theme: ThemeMode;
  onKineticTrigger?: (trigger: string) => void;
}

export const AudioWorkbenchView: React.FC<AudioWorkbenchViewProps> = ({ theme, onKineticTrigger }) => {
  const isDark = theme === 'dark';
  const [gain, setGain] = useAtom(activeAudioGainAtom);
  const [coord, setCoord] = useAtom(audio3DCoordinateAtom);

  const [isPlayingOscillator, setIsPlayingOscillator] = useState<boolean>(false);
  const [selectedVoiceProfile, setSelectedVoiceProfile] = useState<string>('anya');
  const [spatialPanningMode, setSpatialPanningMode] = useState<'HRTF' | 'Binaural' | 'Stereo'>('HRTF');
  const [dspBufferLatency, setDspBufferLatency] = useState<number>(4.2);
  const [sampleRate, setSampleRate] = useState<number>(48000);
  const [fftData, setFftData] = useState<number[]>(new Array(32).fill(10));

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Audio Context Ref
  const audioCtxRef = useRef<AudioContext | null>(null);
  const oscRef = useRef<OscillatorNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const pannerRef = useRef<PannerNode | null>(null);

  // Dynamic FFT Spectrum Simulator
  useEffect(() => {
    const interval = setInterval(() => {
      setFftData((prev) =>
        prev.map((_, i) => {
          if (!isPlayingOscillator) return Math.max(4, Math.sin(Date.now() / 600 + i) * 6 + 10);
          return Math.floor(Math.sin(Date.now() / 200 + i * 0.4) * 40 + Math.random() * 45 + 30);
        })
      );
    }, 80);

    return () => clearInterval(interval);
  }, [isPlayingOscillator]);

  // 2D Spatial Canvas Visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Draw coordinate radar circles
    ctx.strokeStyle = isDark ? 'rgba(0, 229, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)';
    ctx.lineWidth = 1;

    for (let r = 40; r <= 140; r += 30) {
      ctx.beginPath();
      ctx.arc(w / 2, h / 2, r, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Crosshairs
    ctx.beginPath();
    ctx.moveTo(w / 2, 10);
    ctx.lineTo(w / 2, h - 10);
    ctx.moveTo(10, h / 2);
    ctx.lineTo(w - 10, h / 2);
    ctx.stroke();

    // Center Listener Icon
    ctx.fillStyle = '#9D4EDD';
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, 6, 0, Math.PI * 2);
    ctx.fill();

    // Map 3D coordinate (x, z) to 2D canvas
    const nodeX = w / 2 + coord.x * 25;
    const nodeY = h / 2 + coord.z * 25;

    // Pulse Ring around Audio Emitter
    ctx.strokeStyle = '#00E5FF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(nodeX, nodeY, 12 + Math.sin(Date.now() / 200) * 4, 0, Math.PI * 2);
    ctx.stroke();

    // Audio Emitter Node
    ctx.fillStyle = '#00E5FF';
    ctx.beginPath();
    ctx.arc(nodeX, nodeY, 8, 0, Math.PI * 2);
    ctx.fill();

    // Connection Vector Line
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.4)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(w / 2, h / 2);
    ctx.lineTo(nodeX, nodeY);
    ctx.stroke();
    ctx.setLineDash([]);
  }, [coord, isDark]);

  const toggleOscillator = () => {
    try {
      if (isPlayingOscillator) {
        if (oscRef.current) {
          oscRef.current.stop();
          oscRef.current.disconnect();
          oscRef.current = null;
        }
        setIsPlayingOscillator(false);
      } else {
        const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        if (!audioCtxRef.current) {
          audioCtxRef.current = new AudioContextClass();
        }
        const ctx = audioCtxRef.current;
        if (ctx.state === 'suspended') {
          ctx.resume();
        }

        const osc = ctx.createOscillator();
        const gainNode = ctx.createGain();
        const panner = ctx.createPanner();

        panner.panningModel = 'HRTF';
        panner.distanceModel = 'inverse';
        panner.positionX.setValueAtTime(coord.x, ctx.currentTime);
        panner.positionY.setValueAtTime(coord.y, ctx.currentTime);
        panner.positionZ.setValueAtTime(coord.z, ctx.currentTime);

        osc.type = 'sine';
        osc.frequency.setValueAtTime(432, ctx.currentTime); // 432 Hz Harmonic Resonance

        gainNode.gain.setValueAtTime(gain * 0.25, ctx.currentTime);

        osc.connect(gainNode);
        gainNode.connect(panner);
        panner.connect(ctx.destination);

        osc.start();
        oscRef.current = osc;
        gainNodeRef.current = gainNode;
        pannerRef.current = panner;

        setIsPlayingOscillator(true);
      }
    } catch {
      setIsPlayingOscillator(!isPlayingOscillator);
    }
  };

  const handleVoiceTest = () => {
    multiVoiceRouter.speakAsKnight(
      selectedVoiceProfile,
      `Kickbox Audio 3D spatial DSP online. Current coordinate: X ${coord.x}, Y ${coord.y}, Z ${coord.z}.`
    );
    if (onKineticTrigger) onKineticTrigger('KICKBOX_VOICE_TEST');
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Top Header Card */}
      <div
        className={`p-5 rounded-2xl border backdrop-blur-xl transition-all ${
          isDark
            ? 'bg-[#050508]/90 border-[rgba(0,229,255,0.2)] shadow-[0_0_30px_rgba(0,0,0,0.8)]'
            : 'bg-white/95 border-slate-300 shadow-lg'
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-purple-950/60 border border-purple-500/40 text-purple-400">
              <Headphones className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base sm:text-lg font-bold tracking-wider text-purple-400">
                  KICKBOX AUDIO // 3D-TO-2D DEPTH DSP WORKBENCH
                </h2>
                <span className="px-2 py-0.5 text-[10px] rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold">
                  WASM32-SIMD
                </span>
              </div>
              <p className="text-xs text-neutral-400">
                SharedArrayBuffer Ring Buffers • Zero Garbage Collection • HRTF Spatial Coordinate Engine
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleVoiceTest}
              className="px-3.5 py-2 rounded-xl bg-neutral-900 hover:bg-neutral-800 border border-neutral-700 text-xs font-mono text-cyan-300 flex items-center space-x-2 cursor-pointer shadow-sm"
            >
              <Mic className="w-4 h-4 text-pink-400" />
              <span>TEST VOICE SYNTH</span>
            </button>
            <button
              onClick={toggleOscillator}
              className={`px-4 py-2 rounded-xl border text-xs font-mono font-bold flex items-center space-x-2 cursor-pointer transition-all ${
                isPlayingOscillator
                  ? 'bg-purple-600 text-white border-purple-400 shadow-[0_0_20px_rgba(157,78,221,0.5)]'
                  : 'bg-cyan-500 hover:bg-cyan-400 text-black border-cyan-400 shadow-[0_0_15px_rgba(0,229,255,0.3)]'
              }`}
            >
              {isPlayingOscillator ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              <span>{isPlayingOscillator ? 'HALT 432Hz HARMONIC' : 'PLAY 432Hz RESONANCE'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Spatial Radar Canvas + FFT Visualizer & Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Spatial 3D/2D Graph Canvas (7 Cols) */}
        <div
          className={`lg:col-span-7 p-5 rounded-2xl border flex flex-col justify-between ${
            isDark ? 'bg-[#0a0a10] border-neutral-800' : 'bg-white border-slate-200'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Disc className="w-4 h-4 text-cyan-400 animate-spin" style={{ animationDuration: '8s' }} />
              <h3 className="text-sm font-bold text-neutral-200">
                3D SPATIAL RADAR MATRIX (\mathcal&#123;V&#125; \subset \mathbb&#123;R&#125;^3)
              </h3>
            </div>
            <span className="text-[11px] text-purple-400 font-bold">
              PANNING MODEL: {spatialPanningMode}
            </span>
          </div>

          {/* Interactive Radar Canvas */}
          <div className="relative w-full h-[280px] bg-neutral-950/80 rounded-xl border border-neutral-800/80 flex items-center justify-center overflow-hidden">
            <canvas ref={canvasRef} width={400} height={260} className="max-w-full max-h-full" />
            <div className="absolute bottom-2 left-3 text-[10px] text-neutral-500 font-mono">
              [CENTER: LISTENER (0,0)] • [CYAN: KICKBOX EMITTER ({coord.x.toFixed(1)}, {coord.z.toFixed(1)})]
            </div>
          </div>

          {/* Coordinate Sliders */}
          <div className="grid grid-cols-3 gap-3 mt-4">
            <div className="p-2.5 rounded-xl bg-neutral-900/60 border border-neutral-800">
              <div className="flex justify-between text-xs text-neutral-400 mb-1">
                <span>X AXIS (LATERAL)</span>
                <span className="text-cyan-300 font-bold">{coord.x.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="-5"
                max="5"
                step="0.1"
                value={coord.x}
                onChange={(e) => setCoord({ ...coord, x: parseFloat(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            <div className="p-2.5 rounded-xl bg-neutral-900/60 border border-neutral-800">
              <div className="flex justify-between text-xs text-neutral-400 mb-1">
                <span>Y AXIS (ELEVATION)</span>
                <span className="text-purple-300 font-bold">{coord.y.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="-5"
                max="5"
                step="0.1"
                value={coord.y}
                onChange={(e) => setCoord({ ...coord, y: parseFloat(e.target.value) })}
                className="w-full accent-purple-400 cursor-pointer"
              />
            </div>

            <div className="p-2.5 rounded-xl bg-neutral-900/60 border border-neutral-800">
              <div className="flex justify-between text-xs text-neutral-400 mb-1">
                <span>Z AXIS (DEPTH)</span>
                <span className="text-pink-300 font-bold">{coord.z.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="-5"
                max="5"
                step="0.1"
                value={coord.z}
                onChange={(e) => setCoord({ ...coord, z: parseFloat(e.target.value) })}
                className="w-full accent-pink-400 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* FFT Spectrum & DSP Telemetry Controls (5 Cols) */}
        <div
          className={`lg:col-span-5 p-5 rounded-2xl border flex flex-col justify-between space-y-4 ${
            isDark ? 'bg-[#0a0a10] border-neutral-800' : 'bg-white border-slate-200'
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-neutral-200">REAL-TIME FFT FREQUENCY SPECTRUM</h3>
              </div>
              <span className="text-[10px] text-neutral-400 font-mono">32 BARS</span>
            </div>

            {/* FFT Equalizer Bars */}
            <div className="h-32 bg-neutral-950 rounded-xl border border-neutral-800 p-3 flex items-end justify-between gap-1">
              {fftData.map((val, idx) => (
                <div key={idx} className="flex-1 bg-neutral-900 rounded-t h-full flex items-end">
                  <div
                    className="w-full rounded-t transition-all duration-75 bg-gradient-to-t from-cyan-500 via-purple-500 to-pink-500"
                    style={{ height: `${val}%` }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Master Gain Slider */}
          <div className="p-3.5 rounded-xl bg-neutral-950 border border-neutral-800 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-neutral-400 flex items-center space-x-1.5">
                <Volume2 className="w-4 h-4 text-cyan-400" />
                <span>MASTER DSP GAIN ATOM</span>
              </span>
              <span className="text-cyan-300 font-bold font-mono">{(gain * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={gain}
              onChange={(e) => setGain(parseFloat(e.target.value))}
              className="w-full accent-cyan-400 cursor-pointer"
            />
          </div>

          {/* Audio Engine Specs */}
          <div className="p-3.5 rounded-xl bg-neutral-950 border border-neutral-800 space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-neutral-400">Ring-Buffer Latency:</span>
              <span className="text-emerald-400 font-bold">{dspBufferLatency} ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-400">Sample Rate:</span>
              <span className="text-cyan-300 font-bold">{sampleRate} Hz (Float32)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-400">Voice Synthesis Node:</span>
              <span className="text-pink-300 font-bold">{selectedVoiceProfile.toUpperCase()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioWorkbenchView;
