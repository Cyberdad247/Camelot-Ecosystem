import { useEffect, useState, useRef, useTransition } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

// ── VRAM Protection Governor (SIR_BORIS Protocol) ────────────────────────────
function VramGovernor() {
  const { gl, scene } = useThree();

  useEffect(() => {
    return () => {
      // Disposes geometries, materials, and textures recursively on unmount
      scene.traverse((object) => {
        if (!(object instanceof THREE.Mesh)) return;

        if (object.geometry) {
          object.geometry.dispose();
        }

        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((mat) => mat.dispose());
          } else {
            object.material.dispose();
          }
        }
      });

      gl.dispose();
      gl.forceContextLoss();
      console.log('[SIR_BORIS] VRAM Governor: Disposed WebGL structures.');
    };
  }, [gl, scene]);

  return null;
}

// ── Animated Wireframe Globe (R3F) ───────────────────────────────────────────
function AvatarGlobe({ audioActive }: { audioActive: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);

  useEffect(() => {
    let frameId: number;
    const animate = () => {
      if (meshRef.current) {
        meshRef.current.rotation.y += audioActive ? 0.04 : 0.008;
        meshRef.current.rotation.x += audioActive ? 0.02 : 0.004;
      }
      frameId = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(frameId);
  }, [audioActive]);

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[2.2, 24, 24]} />
      <meshBasicMaterial
        color={audioActive ? "#FFD700" : "#00E5FF"}
        wireframe
      />
    </mesh>
  );
}

type Tab = 'NEXUS' | 'VOX' | 'HERMES' | 'FORGE';

export default function CamelotLayout() {
  const [activeTab, setActiveTab] = useState<Tab>('NEXUS');
  const [telemetry, setTelemetry] = useState({
    lattice: 'RADIANT',
    ramUsage: 42.5,
    cpuUsage: 18.2,
    networkLag: 5,
    activeAgents: 6,
  });
  
  const [messages, setMessages] = useState<string[]>([
    "[SYSTEM] Camelot-OS Boot Initialized.",
    "[BIFROST] Connected to sidecar port :8011."
  ]);
  const [inputVal, setInputVal] = useState('');
  const [, startTransition] = useTransition();

  // ── Voice Router / OpenPersona State ───────────────────────────────────────
  const [activePersona, setActivePersona] = useState('Anya');
  const [voiceSettings, setVoiceSettings] = useState({
    pitch: 1.0,
    speed: 1.0,
    bufferSize: 4096,
  });
  const [audioActive, setAudioActive] = useState(false);
  const visualizerCanvasRef = useRef<HTMLCanvasElement>(null);

  // ── Telemetry history for SVG sparklines ────────────────────────────────────
  const [cpuHistory, setCpuHistory] = useState<number[]>([12, 18, 15, 22, 19, 14, 18, 25, 21, 18]);
  const [ramHistory, setRamHistory] = useState<number[]>([42.1, 42.3, 42.2, 42.5, 42.6, 42.5, 42.7, 42.8, 42.5, 42.9]);

  // ── Bifrost SSE Conduit ───────────────────────────────────────────────────
  useEffect(() => {
    const eventSource = new EventSource('/bifrost/stream');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        startTransition(() => {
          setTelemetry((prev) => ({ ...prev, ...data }));
          if (data.cpuUsage !== undefined) {
            setCpuHistory((h) => [...h.slice(1), data.cpuUsage]);
          }
          if (data.ramUsage !== undefined) {
            setRamHistory((h) => [...h.slice(1), data.ramUsage]);
          }
        });
      } catch (err) {
        // Fallback simulated updates if SSE server is offline
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, []);

  // ── Mock telemetry ticking ────────────────────────────────────────────────
  useEffect(() => {
    const interval = setInterval(() => {
      setTelemetry((prev) => {
        const nextCpu = Math.max(5, Math.min(95, prev.cpuUsage + (Math.random() - 0.5) * 6));
        const nextRam = Math.max(10, Math.min(90, prev.ramUsage + (Math.random() - 0.5) * 2));
        const nextLag = Math.max(2, Math.min(80, prev.networkLag + Math.floor((Math.random() - 0.5) * 3)));
        
        setCpuHistory((h) => [...h.slice(1), parseFloat(nextCpu.toFixed(1))]);
        setRamHistory((h) => [...h.slice(1), parseFloat(nextRam.toFixed(1))]);
        
        return {
          ...prev,
          cpuUsage: parseFloat(nextCpu.toFixed(1)),
          ramUsage: parseFloat(nextRam.toFixed(1)),
          networkLag: nextLag,
        };
      });
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  // ── Web Audio simulated waveform visualizer ─────────────────────────────────
  useEffect(() => {
    let animationFrameId: number;
    const canvas = visualizerCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const render = () => {
      ctx.fillStyle = '#05050A';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = audioActive ? '#FFD700' : '#00E5FF';
      ctx.lineWidth = 2;
      ctx.beginPath();

      const sliceWidth = canvas.width / 40;
      let x = 0;

      for (let i = 0; i < 40; i++) {
        const amplitude = audioActive
          ? (Math.sin(i * 0.4 + Date.now() * 0.02) * 20 + (Math.random() - 0.5) * 15)
          : (Math.sin(i * 0.2 + Date.now() * 0.005) * 5);
        const y = canvas.height / 2 + amplitude;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      ctx.stroke();
      animationFrameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [audioActive]);

  // ── Speech trigger / Persona.js test ──────────────────────────────────────
  const triggerSpeech = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.pitch = voiceSettings.pitch;
      utterance.rate = voiceSettings.speed;
      
      utterance.onstart = () => setAudioActive(true);
      utterance.onend = () => setAudioActive(false);
      utterance.onerror = () => setAudioActive(false);
      
      window.speechSynthesis.speak(utterance);
    } else {
      // Direct console animation fallback if Speech Synthesis not supported
      setAudioActive(true);
      setTimeout(() => setAudioActive(false), 2000);
    }
  };

  const handleCommandSubmit = async () => {
    if (!inputVal.trim()) return;
    const cmd = inputVal;
    setInputVal('');
    setMessages((prev) => [...prev, `[USER] ${cmd}`]);

    if (!cmd.startsWith('/') && !cmd.startsWith('//')) {
      // Trigger Ouroboros on-device inference API
      try {
        setMessages((prev) => [...prev, `[SSM] Prompting Ouroboros engine...`]);
        const response = await fetch('/api/infer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ intent: cmd, state_dim: 256 })
        });
        const data = await response.json();
        if (data.error) {
          setMessages((prev) => [...prev, `[SSM_ERROR] ${data.error}`]);
        } else {
          const ast = JSON.parse(data.ast_json);
          setMessages((prev) => [
            ...prev,
            `[SSM_AST] Matched node: "${ast.tag}"`,
            `[SSM_LATENCY] Engine: ${data.engine_latency.toFixed(2)}ms | Wall: ${data.latency_ms.toFixed(2)}ms`
          ]);
          triggerSpeech(`Overhaul node ${ast.tag} predicted.`);
        }
      } catch (err: any) {
        setMessages((prev) => [...prev, `[SSM_FETCH_FAILED] ${err.message}`]);
      }
    } else {
      setMessages((prev) => [...prev, `[OMNIRUTE] Dispatched command: ${cmd}`]);
      triggerSpeech("Rune dispatched successfully.");
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#05050A] text-[#00E5FF] font-mono select-none overflow-hidden border border-[#00E5FF]/20">
      
      {/* ── HEADER ── */}
      <header className="flex justify-between items-center px-6 py-4 border-b border-[#00E5FF]/20 bg-[#12121A]/70 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="h-8 w-8 border border-[#FFD700] bg-black flex items-center justify-center text-[#FFD700] font-black text-lg shadow-[0_0_8px_rgba(255,215,0,0.3)]">
            Ω
          </div>
          <div>
            <h1 className="text-sm font-black tracking-[0.25em] text-white">CAMELOT-OS</h1>
            <p className="text-[10px] text-[#00E5FF]/50 uppercase tracking-widest">Digital Factory Dashboard • v9000.102</p>
          </div>
        </div>

        {/* Tab Selection Navigation */}
        <nav className="flex gap-2">
          {(['NEXUS', 'VOX', 'HERMES', 'FORGE'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-xs font-bold border transition-all ${
                activeTab === tab
                  ? 'bg-[#FFD700]/10 border-[#FFD700] text-[#FFD700] shadow-[0_0_10px_rgba(255,215,0,0.2)]'
                  : 'bg-black/40 border-[#00E5FF]/30 text-[#00E5FF]/60 hover:text-[#00E5FF] hover:border-[#00E5FF]'
              }`}
            >
              {tab === 'NEXUS' && '⚡ NEXUS'}
              {tab === 'VOX' && '🎤 VOX'}
              {tab === 'HERMES' && '💻 HERMES'}
              {tab === 'FORGE' && '🛠️ FORGE'}
            </button>
          ))}
        </nav>
      </header>

      {/* ── MAIN CONTENT GRID ── */}
      <main className="flex-1 p-6 overflow-hidden flex gap-6">
        
        {/* Left Interactive 3D Canvas / Avatar Block */}
        <section className="w-1/3 border border-[#00E5FF]/20 bg-[#12121A]/40 rounded-lg overflow-hidden p-4 flex flex-col gap-4">
          <div className="flex justify-between items-center border-b border-[#00E5FF]/20 pb-2">
            <span className="text-xs font-black tracking-widest text-[#FFD700]">🔮 OPEN_PERSONA MESH</span>
            <span className={`h-2 w-2 rounded-full ${audioActive ? 'bg-[#FFD700] animate-ping' : 'bg-[#00E5FF]'}`} />
          </div>
          
          <div className="flex-1 bg-black/80 rounded border border-[#00E5FF]/10 overflow-hidden relative">
            <Canvas camera={{ position: [0, 0, 6] }}>
              <ambientLight intensity={0.5} />
              <pointLight position={[10, 10, 10]} />
              <AvatarGlobe audioActive={audioActive} />
              <OrbitControls enableZoom={false} />
              <VramGovernor />
            </Canvas>

            {/* Scanning Overlay lines */}
            <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,rgba(0,229,255,0.02)_0%,rgba(0,0,0,0.4)_100%)]" />
            <div className="absolute top-2 left-2 text-[9px] text-[#00E5FF]/40">RENDER STATE: ACTIVE • VRAM GOVERNED</div>
          </div>

          <div className="border border-[#00E5FF]/20 bg-black/60 p-3 rounded flex flex-col gap-2">
            <div className="flex justify-between text-[11px]">
              <span>ACTIVE PROFILE:</span>
              <span className="text-[#FFD700] font-bold uppercase">{activePersona}</span>
            </div>
            <div className="flex justify-between text-[11px]">
              <span>SPEECH ENGINE:</span>
              <span>WebAudio / KittenTTS Proxy</span>
            </div>
          </div>
        </section>

        {/* Right Dynamic Overhaul Tab Container */}
        <section className="flex-1 border border-[#00E5FF]/20 bg-[#12121A]/40 rounded-lg p-6 flex flex-col overflow-hidden">
          
          {/* TAB 1: NEXUS */}
          {activeTab === 'NEXUS' && (
            <div className="flex-1 flex flex-col gap-6 overflow-y-auto">
              <div className="flex justify-between items-center border-b border-[#00E5FF]/20 pb-2">
                <span className="text-sm font-black tracking-widest text-[#FFD700]">⚡ SYSTEM NEXUS & TELEMETRY</span>
                <span className="text-[10px] bg-[#39FF14]/20 border border-[#39FF14] text-[#39FF14] px-2 py-0.5 font-bold">STATE: RADIANT</span>
              </div>

              {/* Bento Grid */}
              <div className="grid grid-cols-2 gap-4">
                
                {/* Gauge Card 1 */}
                <div className="border border-[#00E5FF]/15 bg-black/40 p-4 rounded flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-[#00E5FF]/70">CPU EXECUTION RATE</span>
                    <span className="text-xs text-[#39FF14] font-bold">{telemetry.cpuUsage}%</span>
                  </div>
                  <div className="w-full bg-[#00E5FF]/10 h-2 rounded-full overflow-hidden">
                    <div className="bg-[#00E5FF] h-full transition-all duration-500" style={{ width: `${telemetry.cpuUsage}%` }} />
                  </div>
                  <div className="flex justify-center mt-2">
                    <svg className="w-full h-8" viewBox="0 0 100 20">
                      <path
                        d={`M 0,${20 - cpuHistory[0]} ` + cpuHistory.map((v, i) => `L ${i * 11},${20 - v / 5}`).join(' ')}
                        fill="none"
                        stroke="#00E5FF"
                        strokeWidth="1.5"
                      />
                    </svg>
                  </div>
                </div>

                {/* Gauge Card 2 */}
                <div className="border border-[#00E5FF]/15 bg-black/40 p-4 rounded flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-[#00E5FF]/70">L1.5 RAM ALLOCATION</span>
                    <span className="text-xs text-[#FFD700] font-bold">{telemetry.ramUsage}%</span>
                  </div>
                  <div className="w-full bg-[#FFD700]/10 h-2 rounded-full overflow-hidden">
                    <div className="bg-[#FFD700] h-full transition-all duration-500" style={{ width: `${telemetry.ramUsage}%` }} />
                  </div>
                  <div className="flex justify-center mt-2">
                    <svg className="w-full h-8" viewBox="0 0 100 20">
                      <path
                        d={`M 0,${20 - ramHistory[0] / 5} ` + ramHistory.map((v, i) => `L ${i * 11},${20 - v / 5}`).join(' ')}
                        fill="none"
                        stroke="#FFD700"
                        strokeWidth="1.5"
                      />
                    </svg>
                  </div>
                </div>

              </div>

              {/* System status details */}
              <div className="border border-[#00E5FF]/15 bg-black/40 p-4 rounded flex flex-col gap-2">
                <span className="text-xs font-bold text-[#FFD700] border-b border-[#00E5FF]/10 pb-1">ACTIVE SYSTEM CARTRIDGES</span>
                <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                  <div className="flex justify-between">
                    <span>system-ui (PWA)</span>
                    <span className="text-[#39FF14]">● ONLINE</span>
                  </div>
                  <div className="flex justify-between">
                    <span>voice-router</span>
                    <span className="text-[#39FF14]">● ONLINE</span>
                  </div>
                  <div className="flex justify-between">
                    <span>omni-eye-dashboard</span>
                    <span className="text-[#39FF14]">● ONLINE</span>
                  </div>
                  <div className="flex justify-between">
                    <span>ouroboros-inference</span>
                    <span className="text-[#39FF14]">● ONLINE</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: VOX CONSOLE */}
          {activeTab === 'VOX' && (
            <div className="flex-1 flex flex-col gap-6 overflow-y-auto">
              <div className="flex justify-between items-center border-b border-[#00E5FF]/20 pb-2">
                <span className="text-sm font-black tracking-widest text-[#FFD700]">🎤 MULTI-PERSONA VOICE ROUTER</span>
                <span className="text-[10px] text-[#00E5FF]/60">SAMPLE RATE: 44.1KHZ</span>
              </div>

              {/* Visual Waveform Screen */}
              <div className="h-28 bg-black rounded border border-[#00E5FF]/20 relative overflow-hidden">
                <canvas ref={visualizerCanvasRef} width={450} height={112} className="w-full h-full" />
                <div className="absolute bottom-2 right-2 text-[9px] text-[#00E5FF]/30">KICKBOX AUDIO BUFFER ACTIVE</div>
              </div>

              {/* Persona selection grid */}
              <div className="flex flex-col gap-2">
                <span className="text-xs font-bold text-[#FFD700]">ACTIVE PERSONA SELECTION</span>
                <div className="grid grid-cols-5 gap-2">
                  {['Anya', 'Boris', 'Merlin', 'Helio', 'Stitch'].map((p) => (
                    <button
                      key={p}
                      onClick={() => {
                        setActivePersona(p);
                        triggerSpeech(`Active profile switched to ${p}.`);
                      }}
                      className={`py-2 text-xs font-black border transition-all ${
                        activePersona === p
                          ? 'bg-[#FFD700]/10 border-[#FFD700] text-[#FFD700]'
                          : 'bg-black/50 border-[#00E5FF]/20 text-[#00E5FF]/50 hover:border-[#00E5FF]'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              {/* Sliders */}
              <div className="grid grid-cols-2 gap-4 border-t border-[#00E5FF]/10 pt-4">
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between text-xs">
                    <span>VOICE PITCH</span>
                    <span className="text-[#FFD700] font-bold">{voiceSettings.pitch}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={voiceSettings.pitch}
                    onChange={(e) => setVoiceSettings((prev) => ({ ...prev, pitch: parseFloat(e.target.value) }))}
                    className="w-full accent-[#00E5FF] bg-black h-1 rounded"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between text-xs">
                    <span>SPEECH SPEED</span>
                    <span className="text-[#FFD700] font-bold">{voiceSettings.speed}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={voiceSettings.speed}
                    onChange={(e) => setVoiceSettings((prev) => ({ ...prev, speed: parseFloat(e.target.value) }))}
                    className="w-full accent-[#FFD700] bg-black h-1 rounded"
                  />
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: HERMES CORE */}
          {activeTab === 'HERMES' && (
            <div className="flex-1 flex flex-col gap-4 overflow-hidden">
              <div className="flex justify-between items-center border-b border-[#00E5FF]/20 pb-2">
                <span className="text-sm font-black tracking-widest text-[#FFD700]">💻 HERMES OS & CMUX GRID</span>
                <span className="text-[10px] text-[#00E5FF]/60">active channels: 4/4</span>
              </div>

              {/* CMUX Grid Emulation */}
              <div className="flex-1 grid grid-cols-2 gap-3 min-h-0 overflow-y-auto">
                <div className="border border-[#00E5FF]/10 bg-black/60 p-2 rounded flex flex-col gap-1 text-[10px] overflow-hidden">
                  <span className="text-[#FFD700] font-bold tracking-wider border-b border-[#00E5FF]/10 pb-0.5">CMUX 1: BIFROST_SIDECAR</span>
                  <div className="flex-1 font-mono text-[9px] text-[#00E5FF]/70 whitespace-pre-wrap overflow-y-auto">
                    {"[INFO] ws server started on :8011\n[INFO] connection authenticated\n[INFO] buffer flush complete"}
                  </div>
                </div>

                <div className="border border-[#00E5FF]/10 bg-black/60 p-2 rounded flex flex-col gap-1 text-[10px] overflow-hidden">
                  <span className="text-[#FFD700] font-bold tracking-wider border-b border-[#00E5FF]/10 pb-0.5">CMUX 2: WATCHDOG_DAEMON</span>
                  <div className="flex-1 font-mono text-[9px] text-[#00E5FF]/70 whitespace-pre-wrap overflow-y-auto">
                    {"[OK] watchdog checking ports...\n[OK] all ports responsive\n[OK] memory within safe limits"}
                  </div>
                </div>

                <div className="border border-[#00E5FF]/10 bg-black/60 p-2 rounded flex flex-col gap-1 text-[10px] overflow-hidden">
                  <span className="text-[#FFD700] font-bold tracking-wider border-b border-[#00E5FF]/10 pb-0.5">CMUX 3: OMNIROUTE_ROUTER</span>
                  <div className="flex-1 font-mono text-[9px] text-[#00E5FF]/70 whitespace-pre-wrap overflow-y-auto">
                    {"[ROUT] proxy set /bifrost -> :8001\n[ROUT] proxy set /goRouter -> :8077\n[ROUT] proxy set /api -> :3000"}
                  </div>
                </div>

                <div className="border border-[#00E5FF]/10 bg-black/60 p-2 rounded flex flex-col gap-1 text-[10px] overflow-hidden">
                  <span className="text-[#FFD700] font-bold tracking-wider border-b border-[#00E5FF]/10 pb-0.5">CMUX 4: INF_ENGINE</span>
                  <div className="flex-1 font-mono text-[9px] text-[#00E5FF]/70 whitespace-pre-wrap overflow-y-auto">
                    {"[SSM] warm model initialized in RAM\n[SSM] execution dimension set to 256\n[SSM] engine ready"}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: FORGE FACTORY */}
          {activeTab === 'FORGE' && (
            <div className="flex-1 flex flex-col gap-4 overflow-y-auto">
              <div className="flex justify-between items-center border-b border-[#00E5FF]/20 pb-2">
                <span className="text-sm font-black tracking-widest text-[#FFD700]">🛠️ FORGE FACTORY & KAHN_DAG</span>
                <span className="text-[10px] text-[#00E5FF]/60">compile cycle: clear</span>
              </div>

              {/* Graph of Thoughts Visualizer */}
              <div className="border border-[#00E5FF]/15 bg-black/40 p-4 rounded flex flex-col gap-2">
                <span className="text-xs font-bold text-[#FFD700]">GRAPH OF THOUGHTS HIERARCHY</span>
                <div className="font-mono text-xs flex flex-col gap-1 pl-2">
                  <div>┌── [Triage Phase] ➔ verified</div>
                  <div>├── [Kahn's DAG Evaluation] ➔ cycle check clear (0 cycles)</div>
                  <div>├── [AST Parsing] ➔ matching inference tags</div>
                  <div>└── [Code Generation] ➔ target bundle: cartridges/system-ui</div>
                </div>
              </div>

              {/* Vercel Deploy Monitor */}
              <div className="border border-[#00E5FF]/15 bg-black/40 p-4 rounded flex flex-col gap-2">
                <span className="text-xs font-bold text-[#FFD700]">VERCEL DEPLOYMENT TELEMETRY</span>
                <div className="flex justify-between text-xs pt-1">
                  <span>PROJECT DIR:</span>
                  <span>/cartridges/system-ui</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>STATUS:</span>
                  <span className="text-[#39FF14] font-bold">READY (PREVIEW AUTO-BUILD)</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>DEPLOY TARGET:</span>
                  <span>Local Node C Fallback</span>
                </div>
              </div>
            </div>
          )}

          {/* ── SHARED TERMINAL INPUT & LOGS ── */}
          <div className="border-t border-[#00E5FF]/20 pt-4 mt-auto flex flex-col gap-4">
            <div className="h-28 overflow-y-auto bg-black/60 p-3 rounded border border-[#00E5FF]/10 font-mono text-xs flex flex-col gap-1 min-h-[7rem]">
              {messages.map((msg, idx) => (
                <div key={idx} className="whitespace-pre-wrap">
                  <span className="text-[#FFD700]">&gt;</span> {msg}
                </div>
              ))}
            </div>
            
            <div className="flex gap-2">
              <input
                type="text"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder="Build section (e.g. 'add pricing list') or run rune..."
                className="flex-1 bg-black border border-[#00E5FF]/30 rounded px-3 py-2 text-xs text-[#00E5FF] focus:outline-none focus:border-[#FFD700] placeholder:text-[#00E5FF]/30"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleCommandSubmit();
                }}
              />
              <button
                onClick={handleCommandSubmit}
                className="px-4 py-2 border border-[#FFD700] text-[#FFD700] bg-black/50 text-xs font-bold hover:bg-[#FFD700]/10 transition-all active:scale-95"
              >
                EXECUTE
              </button>
            </div>
          </div>

        </section>
      </main>

      {/* ── FOOTER ── */}
      <footer className="border-t border-[#00E5FF]/10 px-6 py-2 flex justify-between items-center text-[10px] text-[#00E5FF]/40 bg-[#05050A]">
        <span>EXCALIBUR STANDARD PWA CARTRIDGE</span>
        <span>CONDUIT STATUS: CONNECTED</span>
        <span>SCARCITY MEMORY ENFORCED (VRAM CAP 150MB)</span>
      </footer>

    </div>
  );
}
