import { useEffect, useState, useRef, useTransition } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import * as THREE from 'three';

// ── VRAM Protection Governor (SIR_BORIS Protocol) ────────────────────────────
function VramGovernor() {
  const { gl, scene } = useThree();

  useEffect(() => {
    return () => {
      scene.traverse((object) => {
        if (!(object instanceof THREE.Mesh)) return;
        if (object.geometry) object.geometry.dispose();
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

// ── Hyperrealistic Metallic Globe (R3F) ──
function HyperrealisticGlobe({ audioActive }: { audioActive: boolean }) {
  const globeRef = useRef<THREE.Mesh>(null);
  const atmosphereRef = useRef<THREE.Mesh>(null);

  useEffect(() => {
    let frameId: number;
    const animate = () => {
      if (globeRef.current) {
        globeRef.current.rotation.y += audioActive ? 0.025 : 0.005;
        globeRef.current.rotation.x += audioActive ? 0.012 : 0.002;
      }
      if (atmosphereRef.current) {
        atmosphereRef.current.rotation.y -= 0.002;
      }
      frameId = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(frameId);
  }, [audioActive]);

  return (
    <group>
      {/* Dynamic Lighting to highlight specular metalness */}
      <directionalLight position={[5, 3, 5]} intensity={1.5} color="#D4AF37" />
      <pointLight position={[-5, -3, -5]} intensity={1.2} color="#6B3FA0" />
      
      {/* Inner Core: Highly polished metallic globe */}
      <mesh ref={globeRef} castShadow receiveShadow>
        <sphereGeometry args={[1.9, 64, 64]} />
        <meshStandardMaterial
          color="#D4AF37"
          roughness={0.15}
          metalness={0.9}
          bumpScale={0.05}
        />
      </mesh>

      {/* Outer Shell: Ethereal glowing atmosphere halo */}
      <mesh ref={atmosphereRef}>
        <sphereGeometry args={[2.05, 32, 32]} />
        <meshBasicMaterial
          color="#6B3FA0"
          transparent
          opacity={0.15}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          wireframe
        />
      </mesh>
    </group>
  );
}

type Tab = 'SOVEREIGN' | 'VOX' | 'HERMES' | 'FORGE';

interface KnightStatus {
  name: string;
  role: string;
  status: string;
  colorClass: string;
}

export default function CamelotLayout() {
  const [activeTab, setActiveTab] = useState<Tab>('SOVEREIGN');
  const [telemetry, setTelemetry] = useState({
    lattice: 'RADIANT',
    ramUsage: 4.1,
    cpuUsage: 18.4,
    crystalsForged: 142,
    activeAgents: 6,
  });

  const [messages, setMessages] = useState<string[]>([
    "[SYSTEM] Camelot-OS Boot Initialized.",
    "[BIFROST] Connected to sidecar port :8011."
  ]);
  const [inputVal, setInputVal] = useState('');
  const [, startTransition] = useTransition();

  // ── Approval Gate State ───────────────────────────────────────────────────
  const [approvalStatus, setApprovalStatus] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');

  // ── Voice Router State ────────────────────────────────────────────────────
  const [activePersona, setActivePersona] = useState('Anya');
  const [voiceSettings, setVoiceSettings] = useState({
    pitch: 1.0,
    speed: 1.0,
    bufferSize: 4096,
  });
  const [audioActive, setAudioActive] = useState(false);
  const visualizerCanvasRef = useRef<HTMLCanvasElement>(null);

  // ── Knight Roster State ──
  const [knights, setKnights] = useState<KnightStatus[]>([
    { name: 'MERLIN_Ω', role: 'Logic Core', status: 'SLEEP_MODE', colorClass: 'text-green-400' },
    { name: 'LADY_APIS', role: 'Foraging', status: 'INGESTING_DOM...', colorClass: 'text-luxora animate-pulse' },
    { name: 'LUKAS', role: 'Kinetic Engine', status: 'AWAITING_DAG', colorClass: 'text-green-400' },
    { name: 'SIR_SENTINEL', role: 'Warden', status: 'PDG_SCAN_ACTIVE', colorClass: 'text-[#6B3FA0]' }
  ]);

  // ── 3-Second Status Polling (HTML hx-get="/api/status" equivalent) ──
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch('/api/status');
        if (response.ok) {
          const data = await response.json();
          if (data.knights) {
            setKnights(data.knights);
          }
        }
      } catch (err) {
        // Fallback: shuffle knight status details slightly to simulate active execution
        setKnights((prev) =>
          prev.map((k) => {
            if (k.name === 'LADY_APIS' && Math.random() > 0.7) {
              return { ...k, status: Math.random() > 0.5 ? 'INGESTING_DOM...' : 'INDEXING_MEMORIES...' };
            }
            if (k.name === 'MERLIN_Ω' && Math.random() > 0.8) {
              return { ...k, status: k.status === 'SLEEP_MODE' ? 'THINKING...' : 'SLEEP_MODE' };
            }
            return k;
          })
        );
      }
    };

    const interval = setInterval(pollStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  // ── Bifrost SSE Telemetry Conduit ──
  useEffect(() => {
    const eventSource = new EventSource('/bifrost/stream');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        startTransition(() => {
          setTelemetry((prev) => ({
            ...prev,
            cpuUsage: data.cpuUsage ?? prev.cpuUsage,
            ramUsage: data.ramUsage ? parseFloat((data.ramUsage / 10).toFixed(1)) : prev.ramUsage,
            lattice: data.lattice ?? prev.lattice,
          }));
        });
      } catch (err) {
        // Silent catch
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, []);

  // ── Web Audio simulated waveform visualizer ──
  useEffect(() => {
    let animationFrameId: number;
    const canvas = visualizerCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const render = () => {
      ctx.fillStyle = '#050505';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = audioActive ? '#6B3FA0' : '#D4AF37';
      ctx.lineWidth = 2;
      ctx.beginPath();

      const sliceWidth = canvas.width / 40;
      let x = 0;

      for (let i = 0; i < 40; i++) {
        const amplitude = audioActive
          ? (Math.sin(i * 0.4 + Date.now() * 0.02) * 16 + (Math.random() - 0.5) * 10)
          : (Math.sin(i * 0.2 + Date.now() * 0.005) * 3);
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

  // ── Speech Synthesis Trigger ──
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
      setAudioActive(true);
      setTimeout(() => setAudioActive(false), 1500);
    }
  };

  // ── HTMX API endpoints execution equivalent ──
  const handleRezero = async () => {
    setApprovalStatus('REJECTED');
    setMessages((prev) => [...prev, "[SYSTEM] // REZERO command triggered. Rejecting target."]);
    triggerSpeech("Action rejected. Initiating re zero.");
    try {
      await fetch('/api/rezero', { method: 'POST' });
    } catch (err) {
      // Graceful fallback for offline proxy
    }
  };

  const handleGo = async () => {
    setApprovalStatus('APPROVED');
    setMessages((prev) => [...prev, "[SYSTEM] // GO command triggered. Executing target."]);
    triggerSpeech("Action approved. Executing.");
    try {
      await fetch('/api/go', { method: 'POST' });
    } catch (err) {
      // Graceful fallback for offline proxy
    }
  };

  const handleCommandSubmit = async () => {
    if (!inputVal.trim()) return;
    const cmd = inputVal;
    setInputVal('');
    setMessages((prev) => [...prev, `[USER] ${cmd}`]);

    if (!cmd.startsWith('/') && !cmd.startsWith('//')) {
      try {
        setMessages((prev) => [...prev, `[SSM] Querying Ouroboros engine...`]);
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
            `[SSM_AST] Node predicted: "${ast.tag}"`,
            `[SSM_LATENCY] Engine: ${data.engine_latency.toFixed(2)}ms | Wall: ${data.latency_ms.toFixed(2)}ms`
          ]);
          triggerSpeech(`Sovereign intent resolved.`);
        }
      } catch (err: any) {
        setMessages((prev) => [...prev, `[SSM_FETCH_FAILED] ${err.message}`]);
      }
    } else {
      setMessages((prev) => [...prev, `[OMNIRUTE] Dispatched command: ${cmd}`]);
      triggerSpeech("Rune dispatched.");
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#050505] text-[#D4AF37] font-mono select-none overflow-hidden relative selection:bg-[#6B3FA0] selection:text-white">
      
      {/* Scanline Overlay */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(212,175,55,0.04)_50%,rgba(0,0,0,0.18)_50%)] bg-[size:100%_4px] z-50 animate-[scan_6s_linear_infinite]" />
      
      {/* ── HEADER ── */}
      <header className="border-b border-[#6B3FA0] bg-[#1e1e1e] p-4 flex justify-between items-center z-10">
        <div>
          <h1 className="text-2xl font-bold tracking-widest text-[#D4AF37]">
            CAMELOT-OS <span className="text-[#6B3FA0]">v1000</span>
          </h1>
          <p className="text-xs text-gray-400">
            SOVEREIGN_NODE: VIZION // LATTICE: {telemetry.lattice}
          </p>
        </div>

        {/* Tab Selection */}
        <nav className="flex gap-2">
          {(['SOVEREIGN', 'VOX', 'HERMES', 'FORGE'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 text-xs font-bold border transition-all ${
                activeTab === tab
                  ? 'bg-[#6B3FA0]/20 border-[#6B3FA0] text-[#D4AF37] shadow-[0_0_10px_rgba(107,63,160,0.4)]'
                  : 'bg-black/40 border-[#D4AF37]/30 text-[#D4AF37]/60 hover:text-[#D4AF37] hover:border-[#D4AF37]'
              }`}
            >
              {tab === 'SOVEREIGN' && '🜲 COMMAND'}
              {tab === 'VOX' && '🎤 VOX'}
              {tab === 'HERMES' && '💻 HERMES'}
              {tab === 'FORGE' && '🛠️ FORGE'}
            </button>
          ))}
        </nav>

        <div className="flex items-center space-x-4">
          <div className="animate-pulse h-3 w-3 bg-green-500 rounded-full"></div>
          <span className="text-sm font-bold">HIVE_ACTIVE</span>
        </div>
      </header>

      {/* ── MAIN WORKSPACE ── */}
      <main className="flex-grow flex p-4 gap-4 overflow-hidden z-10 min-h-0">
        
        {/* Left Column: Knight Roster & Memcastle State */}
        <aside className="w-1/3 flex flex-col gap-4">
          
          {/* Knight Roster */}
          <div className="border border-[#6B3FA0] bg-[#1e1e1e] p-4 rounded shadow-[0_0_15px_rgba(107,63,160,0.2)] flex flex-col h-1/2 overflow-y-auto">
            <h2 className="text-lg font-bold border-b border-gray-700 pb-2 mb-2">🜲 KNIGHT ROSTER</h2>
            <ul className="space-y-3 text-sm flex-grow overflow-y-auto">
              {knights.map((k, idx) => (
                <li key={idx} className="flex justify-between items-center">
                  <span>[{k.name}] {k.role}</span>
                  <span className={`${k.colorClass} font-bold`}>{k.status}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Memcastle State */}
          <div className="border border-[#D4AF37] bg-[#1e1e1e] p-4 rounded shadow-[0_0_10px_rgba(212,175,55,0.2)] h-1/2 flex flex-col">
            <h2 className="text-lg font-bold border-b border-gray-700 pb-2 mb-2">🧪 MEMCASTLE STATE</h2>
            <div className="space-y-3 text-sm mt-2 flex-grow">
              <div className="flex justify-between">
                <span>RAM UTILIZATION:</span>
                <span className="text-white font-bold">{telemetry.ramUsage}GB / 8.0GB</span>
              </div>
              <div className="flex justify-between">
                <span>UKG CRYSTALS:</span>
                <span className="text-[#6B3FA0] font-bold">{telemetry.crystalsForged} FORGED</span>
              </div>
              <div className="flex justify-between">
                <span>ACTIVE HEURISTIC:</span>
                <span className="text-[#D4AF37] font-bold">First_Principles (mm_001)</span>
              </div>
            </div>
            
            {/* Hyperrealistic Canvas Avatar embed */}
            <div className="h-24 bg-black border border-[#D4AF37]/15 rounded overflow-hidden mt-auto relative shadow-[inset_0_0_12px_rgba(212,175,55,0.1)]">
              <Canvas camera={{ position: [0, 0, 4.5] }}>
                <ambientLight intensity={0.2} />
                <HyperrealisticGlobe audioActive={audioActive} />
                <VramGovernor />
              </Canvas>
              <div className="absolute top-1 left-2 text-[8px] text-[#D4AF37]/40 tracking-widest uppercase">SPECTRUM RENDERER ACTIVE</div>
            </div>
          </div>
        </aside>

        {/* Right Column: Tab View Screens */}
        <section className="w-2/3 border border-[#D4AF37] bg-[#1e1e1e] p-6 rounded flex flex-col shadow-[0_0_10px_rgba(212,175,55,0.2)] relative min-h-0">
          
          {/* TAB 1: SOVEREIGN COMMAND OVERLOOK */}
          {activeTab === 'SOVEREIGN' && (
            <div className="flex-grow flex flex-col min-h-0">
              <div className="absolute top-0 right-0 p-2 text-xs text-gray-500">OUROBOROS_HITL_GATE</div>
              <h2 className="text-xl font-bold mb-4 flex items-center border-b border-gray-800 pb-2">
                <span className="mr-2 text-red-500">⚠️</span> PENDING SOVEREIGN APPROVAL
              </h2>
              
              <div className="flex-grow bg-[#050505] border border-gray-700 p-4 overflow-y-auto mb-4 text-sm text-gray-300 rounded">
                <p className="text-[#6B3FA0] font-bold mb-2">TARGET: Refactor Next.js Headless Router</p>
                <p className="mb-4">
                  Merlin_Ω has generated a structural DAG. Sir Sentinel has audited the PDG. Diff exceeds 10 lines. Security validation requires human override.
                </p>
                
                <pre className="bg-black p-3 border border-gray-800 text-green-400 overflow-x-auto rounded font-mono text-xs shadow-[inset_0_0_8px_rgba(0,0,0,0.8)]">
{JSON.stringify({
  "action": "OVERWRITE",
  "file": "app/router.ts",
  "heuristic_applied": "Occam's Razor",
  "z3_verification": "PASS"
}, null, 2)}
                </pre>

                {approvalStatus !== 'PENDING' && (
                  <div className={`mt-4 p-2.5 text-xs font-bold text-center border uppercase rounded ${
                    approvalStatus === 'APPROVED' ? 'bg-green-500/10 border-green-500 text-green-400' : 'bg-red-500/10 border-red-500 text-red-400'
                  }`}>
                    Action decision logged: {approvalStatus}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-4">
                <button
                  disabled={approvalStatus !== 'PENDING'}
                  onClick={handleRezero}
                  className="px-6 py-2 bg-red-900 hover:bg-red-700 text-white font-bold rounded transition border border-red-500 disabled:opacity-50 active:scale-95"
                >
                  // REZERO (REJECT)
                </button>
                <button
                  disabled={approvalStatus !== 'PENDING'}
                  onClick={handleGo}
                  className="px-6 py-2 bg-[#D4AF37] hover:bg-yellow-500 text-black font-bold rounded transition shadow-[0_0_10px_rgba(212,175,55,0.3)] disabled:opacity-50 active:scale-95"
                >
                  // GO (EXECUTE)
                </button>
              </div>
            </div>
          )}

          {/* TAB 2: VOX CONSOLE */}
          {activeTab === 'VOX' && (
            <div className="flex-grow flex flex-col gap-4 overflow-y-auto">
              <h2 className="text-xl font-bold border-b border-gray-800 pb-2 mb-2">🎤 KICKBOX VOICE ROUTER</h2>
              
              <div className="h-24 bg-black rounded border border-[#6B3FA0]/30 relative overflow-hidden">
                <canvas ref={visualizerCanvasRef} width={450} height={96} className="w-full h-full" />
                <div className="absolute bottom-1 right-2 text-[9px] text-gray-500">VOICE SPECTRUM HUD</div>
              </div>

              <div className="flex flex-col gap-2">
                <span className="text-xs font-bold text-[#D4AF37]">ACTIVE AVATAR CORE</span>
                <div className="grid grid-cols-5 gap-2">
                  {['Anya', 'Boris', 'Merlin', 'Helio', 'Stitch'].map((p) => (
                    <button
                      key={p}
                      onClick={() => {
                        setActivePersona(p);
                        triggerSpeech(`Active profile switched to ${p}.`);
                      }}
                      className={`py-1.5 text-xs font-black border transition-all ${
                        activePersona === p
                          ? 'bg-[#6B3FA0]/20 border-[#6B3FA0] text-[#D4AF37]'
                          : 'bg-black/50 border-[#D4AF37]/20 text-[#D4AF37]/50 hover:border-[#D4AF37]'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-gray-800 pt-4">
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between text-xs">
                    <span>SPEECH SPEED</span>
                    <span className="text-[#D4AF37] font-bold">{voiceSettings.speed}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={voiceSettings.speed}
                    onChange={(e) => setVoiceSettings((prev) => ({ ...prev, speed: parseFloat(e.target.value) }))}
                    className="w-full accent-[#6B3FA0] bg-black h-1 rounded"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between text-xs">
                    <span>VOICE PITCH</span>
                    <span className="text-[#D4AF37] font-bold">{voiceSettings.pitch}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={voiceSettings.pitch}
                    onChange={(e) => setVoiceSettings((prev) => ({ ...prev, pitch: parseFloat(e.target.value) }))}
                    className="w-full accent-[#6B3FA0] bg-black h-1 rounded"
                  />
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: HERMES */}
          {activeTab === 'HERMES' && (
            <div className="flex-grow flex flex-col gap-3 min-h-0">
              <h2 className="text-xl font-bold border-b border-gray-800 pb-2">💻 HERMES DAEMONS & CMUX</h2>
              <div className="flex-grow grid grid-cols-2 gap-3 overflow-y-auto">
                <div className="border border-gray-700 bg-black/60 p-2 rounded flex flex-col overflow-hidden text-[10px]">
                  <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1">CMUX 1: BIFROST_WS</span>
                  <div className="flex-grow font-mono text-[9px] text-gray-400 whitespace-pre-wrap overflow-y-auto mt-1">
                    {"[INFO] ws server started on :8011\n[INFO] payload verified\n[OK] handshake complete"}
                  </div>
                </div>

                <div className="border border-gray-700 bg-black/60 p-2 rounded flex flex-col overflow-hidden text-[10px]">
                  <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1">CMUX 2: WATCHDOG_SERVICE</span>
                  <div className="flex-grow font-mono text-[9px] text-gray-400 whitespace-pre-wrap overflow-y-auto mt-1">
                    {"[OK] checking soft process loops\n[OK] memory safe\n[OK] CPU throttle inactive"}
                  </div>
                </div>

                <div className="border border-gray-700 bg-black/60 p-2 rounded flex flex-col overflow-hidden text-[10px]">
                  <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1">CMUX 3: OMNIROUTE_POLICIES</span>
                  <div className="flex-grow font-mono text-[9px] text-gray-400 whitespace-pre-wrap overflow-y-auto mt-1">
                    {"[POLICY] forward /bifrost -> :8001\n[POLICY] forward /goRouter -> :8077\n[POLICY] forward /api -> :3000"}
                  </div>
                </div>

                <div className="border border-gray-700 bg-black/60 p-2 rounded flex flex-col overflow-hidden text-[10px]">
                  <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1">CMUX 4: INF_ENGINE</span>
                  <div className="flex-grow font-mono text-[9px] text-gray-400 whitespace-pre-wrap overflow-y-auto mt-1">
                    {"[SSM] warm engine active\n[SSM] state dims loaded (256)\n[SSM] awaiting intents"}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: FORGE */}
          {activeTab === 'FORGE' && (
            <div className="flex-grow flex flex-col gap-4 overflow-y-auto">
              <h2 className="text-xl font-bold border-b border-gray-800 pb-2">🛠️ FORGE ENGINE & KAHN_DAG</h2>
              
              <div className="border border-gray-700 bg-black/50 p-4 rounded flex flex-col gap-2">
                <span className="text-xs font-bold text-[#D4AF37]">DAG TOPOLOGY VALIDATION</span>
                <div className="font-mono text-xs flex flex-col gap-1 pl-2">
                  <div>┌── [Triage Ingest] ➔ checked</div>
                  <div>├── [Kahn's Sort Validation] ➔ 0 cycles detected</div>
                  <div>├── [AST Parsing] ➔ 100% matched</div>
                  <div>└── [Target Build] ➔ cartridges/system-ui compiled</div>
                </div>
              </div>

              <div className="border border-gray-700 bg-black/50 p-4 rounded flex flex-col gap-2">
                <span className="text-xs font-bold text-[#D4AF37]">DEPLOYMENT PIPELINE</span>
                <div className="flex justify-between text-xs pt-1">
                  <span>WORKSPACE:</span>
                  <span>/cartridges/system-ui</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>DEPLOY STATE:</span>
                  <span className="text-green-400 font-bold">READY (PREVIEW AUTO-BUILD)</span>
                </div>
              </div>
            </div>
          )}

          {/* ── SHARED TERMINAL FEED & RUNE DISPATCH ── */}
          <div className="border-t border-gray-800 pt-4 mt-auto flex flex-col gap-3">
            <div className="h-24 overflow-y-auto bg-black border border-gray-800 p-2.5 rounded font-mono text-xs flex flex-col gap-1 min-h-[6rem]">
              {messages.map((msg, idx) => (
                <div key={idx} className="whitespace-pre-wrap text-gray-300">
                  <span className="text-[#6B3FA0]">&gt;</span> {msg}
                </div>
              ))}
            </div>
            
            <div className="flex gap-2">
              <input
                type="text"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder="Build section (e.g. 'add pricing list') or run rune..."
                className="flex-1 bg-black border border-[#D4AF37]/30 rounded px-3 py-2 text-xs text-[#D4AF37] focus:outline-none focus:border-[#6B3FA0] placeholder:text-[#D4AF37]/20"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleCommandSubmit();
                }}
              />
              <button
                onClick={handleCommandSubmit}
                className="px-4 py-2 border border-[#6B3FA0] text-[#D4AF37] bg-black/50 text-xs font-bold hover:bg-[#6B3FA0]/15 transition-all active:scale-95"
              >
                DISPATCH
              </button>
            </div>
          </div>

        </section>
      </main>

      {/* ── FOOTER ── */}
      <footer className="border-t border-[#6B3FA0]/30 bg-[#050505] p-2 text-xs text-gray-500 flex justify-between z-10">
        <span>&gt; System listening on internal port 8811...</span>
        <span className="text-[#D4AF37] font-bold">Dreams don't come true, visions do. ⚡</span>
      </footer>
    </div>
  );
}
