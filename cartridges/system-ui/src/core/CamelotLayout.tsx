import { useEffect, useState, useRef, useTransition } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { KickboxAudioController } from './audioContext';
import { PersonaStateManager } from './personaState';
import { AionTimelineCache } from './aionTimeline';
import { HerdrMeshRouter } from './herdrMesh';

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
      <directionalLight position={[5, 3, 5]} intensity={1.5} color="#D4AF37" />
      <pointLight position={[-5, -3, -5]} intensity={1.2} color="#6B3FA0" />

      <mesh ref={globeRef} castShadow receiveShadow>
        <sphereGeometry args={[1.9, 64, 64]} />
        <meshStandardMaterial
          color="#D4AF37"
          roughness={0.15}
          metalness={0.9}
        />
      </mesh>

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

interface SwarmStatus {
  name: string;
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
    networkLag: 11,
  });

  const [messages, setMessages] = useState<string[]>([
    "[SYSTEM] Camelot-OS Boot Initialized.",
    "[BIFROST] Connected to sidecar port :8011."
  ]);
  const [inputVal, setInputVal] = useState('');
  const [, startTransition] = useTransition();

  // Core Controllers (Refs ensure single instance across renders)
  const audioController = useRef(new KickboxAudioController());
  const personaManager = useRef(new PersonaStateManager());
  const timelineCache = useRef(new AionTimelineCache(30));
  const meshRouter = useRef(new HerdrMeshRouter());

  const [personaName, setPersonaName] = useState('Anya');
  const [masterVolume, setMasterVolume] = useState(1.0);
  const [timelineHistory, setTimelineHistory] = useState<any[]>([]);

  // Setup Herdr Mesh Router nodes on mount
  useEffect(() => {
    meshRouter.current.registerNode('s26', 'EDGE');
    meshRouter.current.registerNode('nC', 'ROUTER');
    meshRouter.current.registerNode('bifrost', 'BRIDGE');
    meshRouter.current.registerNode('multivoice', 'VOX');
    meshRouter.current.registerNode('chatterbox', 'TTS');
    meshRouter.current.registerNode('omniroute', 'GATEWAY');

    meshRouter.current.connectNodes('s26', 'nC');
    meshRouter.current.connectNodes('nC', 'bifrost');
    meshRouter.current.connectNodes('bifrost', 'multivoice');
    meshRouter.current.connectNodes('bifrost', 'chatterbox');
    meshRouter.current.connectNodes('bifrost', 'omniroute');
  }, []);

  // Dispose audio controller on unmount
  useEffect(() => {
    return () => {
      audioController.current.dispose();
    };
  }, []);

  const handlePersonaChange = (name: string) => {
    personaManager.current.setPersona(name);
    setPersonaName(name);
    setMessages((prev) => [...prev, `[SYSTEM] Switched active persona to ${name}`]);
    triggerSpeech(`Active persona updated to ${name}.`);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setMasterVolume(val);
    audioController.current.setVolume(val);
  };

  // ── Bifrost SSE Conduit ──
  useEffect(() => {
    const eventSource = new EventSource('/bifrost/stream');
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        startTransition(() => {
          setTelemetry((prev) => {
            const next = {
              ...prev,
              cpuUsage: data.cpuUsage ?? prev.cpuUsage,
              ramUsage: data.ramUsage ? parseFloat((data.ramUsage / 10).toFixed(1)) : prev.ramUsage,
              lattice: data.lattice ?? prev.lattice,
              networkLag: data.networkLag ?? prev.networkLag,
            };
            timelineCache.current.push(next);
            setTimelineHistory([...timelineCache.current.getHistory()]);
            return next;
          });
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

  // ── Simulates ticking for telemetry updates ──
  useEffect(() => {
    const interval = setInterval(() => {
      setTelemetry((prev) => {
        const nextCpu = Math.max(5, Math.min(95, prev.cpuUsage + (Math.random() - 0.5) * 6));
        const nextRam = Math.max(1.0, Math.min(8.0, prev.ramUsage + (Math.random() - 0.5) * 0.2));
        const nextLag = Math.max(2, Math.min(25, prev.networkLag + Math.floor((Math.random() - 0.5) * 4)));
        const next = {
          ...prev,
          cpuUsage: parseFloat(nextCpu.toFixed(1)),
          ramUsage: parseFloat(nextRam.toFixed(1)),
          networkLag: nextLag,
        };
        timelineCache.current.push(next);
        setTimelineHistory([...timelineCache.current.getHistory()]);
        return next;
      });
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // ── Approval Gate State ───────────────────────────────────────────────────
  const [approvalStatus, setApprovalStatus] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');

  // ── Active Swarm Status (v1100) ──
  const [swarmList] = useState<SwarmStatus[]>([
    { name: '[MERLIN_Ω]', status: 'ORCHESTRATING', colorClass: 'text-green-400' },
    { name: '[ANYA_Ω]', status: 'STREAMING_AUDIO', colorClass: 'text-luxora' },
    { name: '[LUKAS]', status: 'AWAITING_PRD', colorClass: 'text-gray-500' },
    { name: '[SIR_SENTINEL]', status: 'IRON_GATE_SECURE', colorClass: 'text-green-400' }
  ]);

  // ── VOX / Lip Sync Programmatic State ─────────────────────────────────────
  const [voiceCapturing, setVoiceCapturing] = useState(false);
  const [mouthHeight, setMouthHeight] = useState(4);
  const [speechConsoleLog, setSpeechConsoleLog] = useState('> Awaiting streaming hypermedia voice packets...');
  const [audioActive, setAudioActive] = useState(false);

  // ── Speech Synthesis Trigger ──
  const triggerSpeech = (text: string) => {
    const attrs = personaManager.current.getAttributes();
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.pitch = attrs.voicePitch;
      utterance.rate = attrs.voiceSpeed;
      utterance.onstart = () => {
        setAudioActive(true);
      };
      utterance.onend = () => {
        setAudioActive(false);
        setMouthHeight(4);
      };
      utterance.onerror = () => {
        setAudioActive(false);
        setMouthHeight(4);
      };
      window.speechSynthesis.speak(utterance);
    } else {
      setAudioActive(true);
      setTimeout(() => {
        setAudioActive(false);
        setMouthHeight(4);
      }, 1500);
    }
  };

  // ── Live Lip Sync Simulation (HTML programmatic script equivalent) ──
  useEffect(() => {
    let interval: number;
    const attrs = personaManager.current.getAttributes();

    if (audioActive) {
      interval = window.setInterval(() => {
        const amplitude = Math.random();
        const heightVal = 4 + (amplitude * 16);
        setMouthHeight(heightVal);
        setSpeechConsoleLog(`> SSE Packet: [EMOTION: ${attrs.emotion}] // AMPLITUDE: ${amplitude.toFixed(2)}`);
      }, 120);
    } else {
      setMouthHeight(4);
      setSpeechConsoleLog('> SSE Packet: [EMOTION: SLEEPING] // AMPLITUDE: 0.00');
    }

    return () => clearInterval(interval);
  }, [audioActive, personaName]);

  // ── Capture Toggle Logic ──
  const handleCaptureToggle = () => {
    if (!voiceCapturing) {
      audioController.current.init();
      setVoiceCapturing(true);
      setMessages((prev) => [...prev, "[SYSTEM] Audio capture context initialized via Kickbox Controller."]);
      triggerSpeech("Audio capture matrix enabled.");
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
      // Graceful fallback
    }
  };

  const handleGo = async () => {
    setApprovalStatus('APPROVED');
    setMessages((prev) => [...prev, "[SYSTEM] // GO command triggered. Executing target."]);
    triggerSpeech("Action approved. Executing.");
    try {
      await fetch('/api/go', { method: 'POST' });
    } catch (err) {
      // Graceful fallback
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
            EXCALIBUR <span className="text-[#6B3FA0]">v1100</span>
          </h1>
          <p className="text-xs text-gray-400">
            FOUNDER: VaShawn O. Head aka Vizion // AVATAR MATRIX: ONLINE
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
          <span className="text-sm font-bold">AVATAR_AUDIO_LATTICE::CONNECTED</span>
        </div>
      </header>

      {/* ── MAIN WORKSPACE ── */}
      <main className="flex-grow flex p-4 gap-4 overflow-hidden z-10 min-h-0">

        {/* Left Column: Active Swarm Status & OpenPersona State */}
        <aside className="w-1/4 flex flex-col gap-4">

          {/* Active Swarm Status */}
          <div className="border border-[#6B3FA0] bg-[#1e1e1e] p-4 rounded shadow-[0_0_15px_rgba(107,63,160,0.2)] flex flex-col h-2/3 overflow-y-auto">
            <h2 className="text-xs font-bold border-b border-gray-700 pb-2 mb-2 text-[#6B3FA0]">🜲 ACTIVE SWARM STATUS</h2>
            <ul className="space-y-3 text-xs flex-grow overflow-y-auto">
              {swarmList.map((s, idx) => (
                <li key={idx} className="flex justify-between items-center">
                  <span>{s.name}</span>
                  <span className={`${s.colorClass} font-bold`}>{s.status}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* OpenPersona State */}
          <div className="border border-[#D4AF37] bg-[#1e1e1e] p-4 rounded shadow-[0_0_10px_rgba(212,175,55,0.2)] h-1/3 text-xs flex flex-col justify-between">
            <div>
              <h2 className="font-bold text-[#D4AF37] mb-1">🧪 OPENPERSONA STATE</h2>
              <p className="mt-1">ACTIVE: <span className="text-white font-bold">{personaName}</span></p>
              <p className="mt-1">EMOTION: <span className="text-[#6B3FA0] font-bold">{personaManager.current.getAttributes().emotion}</span></p>
              <p className="mt-1">PITCH: <span className="text-white">{personaManager.current.getAttributes().voicePitch}x</span></p>
              <p className="mt-1">SPEED: <span className="text-white">{personaManager.current.getAttributes().voiceSpeed}x</span></p>
              <p className="mt-1">LATENCY: <span className="text-green-400 font-bold">&lt;{telemetry.networkLag}ms</span></p>
              <div className="mt-2 flex gap-1">
                {(['Anya', 'Merlin', 'Boris'] as const).map((p) => (
                  <button
                    key={p}
                    onClick={() => handlePersonaChange(p)}
                    className={`px-1.5 py-0.5 rounded border text-[9px] font-bold transition-all ${
                      personaName === p
                        ? 'bg-[#6B3FA0] border-[#6B3FA0] text-white'
                        : 'bg-black/35 border-gray-700 text-gray-400 hover:text-white hover:border-gray-500'
                    }`}
                  >
                    {p.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Hyperrealistic Canvas Avatar embed */}
            <div className="h-16 bg-black border border-[#D4AF37]/15 rounded overflow-hidden relative shadow-[inset_0_0_8px_rgba(212,175,55,0.1)]">
              <Canvas camera={{ position: [0, 0, 4.5] }}>
                <ambientLight intensity={0.2} />
                <HyperrealisticGlobe audioActive={audioActive} />
                <VramGovernor />
              </Canvas>
            </div>
          </div>
        </aside>

        {/* Center / Main Viewport and Right panels */}
        <section className="flex-1 flex gap-4 min-h-0 overflow-hidden">

          {/* Middle Viewport (Faculty / Sovereign Override) */}
          <div className="flex-grow border border-[#D4AF37] bg-[#1e1e1e] p-6 rounded flex flex-col shadow-[0_0_10px_rgba(212,175,55,0.2)] relative min-h-0">

            {/* TAB 1: SOVEREIGN OVERRIDE */}
            {activeTab === 'SOVEREIGN' && (
              <div className="flex-grow flex flex-col min-h-0">
                <div className="absolute top-2 left-2 text-xs text-[#D4AF37]">FACULTY_VIEWPORT</div>
                <div className="absolute top-2 right-2 text-xs text-gray-500">OUROBOROS_HITL_GATE</div>
                <h2 className="text-xl font-bold mb-4 flex items-center border-b border-gray-800 pb-2 mt-4">
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
                    <div className={`mt-4 p-2 text-xs font-bold text-center border uppercase rounded ${
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
                    className="px-6 py-2 bg-red-900 hover:bg-red-700 text-white font-bold rounded transition border border-red-500 disabled:opacity-50 active:scale-95 text-xs"
                  >
                    // REZERO (REJECT)
                  </button>
                  <button
                    disabled={approvalStatus !== 'PENDING'}
                    onClick={handleGo}
                    className="px-6 py-2 bg-[#D4AF37] hover:bg-yellow-500 text-black font-bold rounded transition shadow-[0_0_10px_rgba(212,175,55,0.3)] disabled:opacity-50 active:scale-95 text-xs"
                  >
                    // GO (EXECUTE)
                  </button>
                </div>
              </div>
            )}

            {/* TAB 2: VOX CONSOLE (LIP SYNC INTEGRATED) */}
            {activeTab === 'VOX' && (
              <div className="flex-grow flex flex-col items-center justify-center min-h-0 relative">
                <div className="absolute top-2 left-2 text-xs text-[#D4AF37]">FACULTY_VIEWPORT</div>

                {/* SVG Avatar Vector with Pinging Eyes and Lip-Sync Mouth */}
                <div id="avatar-frame" className="w-48 h-48 rounded-full border-2 border-[#6B3FA0] flex items-center justify-center bg-[#050505] mb-6 shadow-[0_0_15px_rgba(107,63,160,0.5)] relative overflow-hidden">
                  <svg id="avatar-vector" className="w-32 h-32 text-[#D4AF37]" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="50" cy="45" r="30" stroke="currentColor" strokeWidth="2" fill="#050505"/>
                    <circle cx="40" cy="40" r="3" fill="#6B3FA0" className="animate-ping"/>
                    <circle cx="40" cy="40" r="2" fill="currentColor"/>
                    <circle cx="60" cy="40" r="3" fill="#6B3FA0" className="animate-ping"/>
                    <circle cx="60" cy="40" r="2" fill="currentColor"/>
                    <rect id="avatar-mouth" x="42" y="58" width="16" height={mouthHeight} rx="2" fill="currentColor" className="transition-[height] duration-75" />
                  </svg>
                </div>

                {/* Animated Equalizer Bars */}
                <div className="w-2/3 h-12 bg-[#050505] border border-gray-800 rounded p-2 flex items-center justify-center gap-1.5 shadow-[inset_0_0_8px_rgba(0,0,0,0.8)]">
                  <div className={`w-1 bg-[#6B3FA0] rounded transition-all duration-100 ${audioActive ? 'h-5 animate-bounce' : 'h-2'}`}></div>
                  <div className={`w-1 bg-[#D4AF37] rounded transition-all duration-100 ${audioActive ? 'h-9 animate-bounce' : 'h-2'}`} style={{ animationDelay: '0.1s' }}></div>
                  <div className={`w-1 bg-[#6B3FA0] rounded transition-all duration-100 ${audioActive ? 'h-11 animate-bounce' : 'h-2'}`} style={{ animationDelay: '0.2s' }}></div>
                  <div className={`w-1 bg-[#D4AF37] rounded transition-all duration-100 ${audioActive ? 'h-7 animate-bounce' : 'h-2'}`} style={{ animationDelay: '0.3s' }}></div>
                  <div className={`w-1 bg-[#6B3FA0] rounded transition-all duration-100 ${audioActive ? 'h-3 animate-bounce' : 'h-2'}`} style={{ animationDelay: '0.4s' }}></div>
                </div>

                {/* Dynamic voice test synthesis selector */}
                <div className="flex gap-2 mt-4 w-2/3 justify-center">
                  <button
                    onClick={() => triggerSpeech("Lattice protocol active. Executing speech synthesis test.")}
                    className="px-3 py-1 border border-[#D4AF37]/40 text-[#D4AF37] hover:bg-[#D4AF37]/10 rounded text-[10px]"
                  >
                    TEST VOX
                  </button>
                  <button
                    onClick={() => {
                      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
                      setAudioActive(false);
                      setMouthHeight(4);
                    }}
                    className="px-3 py-1 border border-red-500/40 text-red-400 hover:bg-red-500/10 rounded text-[10px]"
                  >
                    SILENCE
                  </button>
                </div>
              </div>
            )}

            {/* TAB 3: HERMES */}
            {activeTab === 'HERMES' && (
              <div className="flex-grow flex flex-col gap-3 min-h-0 text-[10px]">
                <h2 className="text-xl font-bold border-b border-gray-800 pb-2">💻 HERMES DAEMONS & CMUX</h2>

                {/* 4-column CMUX / Topology Layout */}
                <div className="flex-grow grid grid-cols-2 gap-3 overflow-y-auto min-h-0">
                  {/* Left inner column: Daemons */}
                  <div className="flex flex-col gap-3 min-h-0">
                    <div className="border border-gray-700 bg-black/60 p-2 rounded flex flex-col overflow-hidden h-1/2 text-[10px]">
                      <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1">CMUX 1: BIFROST_WS</span>
                      <div className="flex-grow font-mono text-[9px] text-gray-400 whitespace-pre-wrap overflow-y-auto mt-1">
                        {"[INFO] ws server started on :8011\n[INFO] payload verified\n[OK] handshake complete"}
                      </div>
                    </div>

                    <div className="border border-gray-700 bg-black/60 p-2 rounded flex flex-col overflow-hidden h-1/2 text-[10px]">
                      <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1">CMUX 2: WATCHDOG_SERVICE</span>
                      <div className="flex-grow font-mono text-[9px] text-gray-400 whitespace-pre-wrap overflow-y-auto mt-1">
                        {"[OK] checking soft process loops\n[OK] memory safe\n[OK] CPU throttle inactive"}
                      </div>
                    </div>
                  </div>

                  {/* Right inner column: Dynamic Topology & Timeline */}
                  <div className="flex flex-col gap-3 min-h-0">
                    {/* Herdr Swarm Topology */}
                    <div className="border border-gray-700 bg-black/60 p-2.5 rounded flex flex-col overflow-hidden h-1/2 text-[10px]">
                      <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1 mb-1">🌐 HERDR SWARM TOPOLOGY (multiplexed)</span>
                      <div className="flex-grow font-mono text-[9px] text-gray-400 overflow-y-auto space-y-0.5">
                        {meshRouter.current.getNodes().map((node) => {
                          const connections = meshRouter.current.getNodes()
                            .filter((other) => other.id !== node.id && meshRouter.current.isConnected(node.id, other.id))
                            .map((other) => other.id);
                          return (
                            <div key={node.id} className="flex justify-between items-center py-0.5 border-b border-gray-900/40">
                              <span className="text-[#6B3FA0] font-bold">[{node.id.toUpperCase()}] ({node.type})</span>
                              <span className="text-gray-500">➜ {connections.join(', ') || 'STANDALONE'}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Aion Timeline Cache */}
                    <div className="border border-gray-700 bg-black/60 p-2.5 rounded flex flex-col overflow-hidden h-1/2 text-[10px]">
                      <span className="text-[#D4AF37] font-bold border-b border-gray-800 pb-1 mb-1">⏳ AION TEMPORAL STATE CACHE</span>
                      <div className="flex-grow font-mono text-[8px] text-gray-400 overflow-y-auto space-y-0.5">
                        {timelineHistory.slice(-5).reverse().map((frame, idx) => (
                          <div key={idx} className="flex justify-between items-center text-[8px]">
                            <span>{new Date(frame.timestamp).toLocaleTimeString()}</span>
                            <span className="text-green-400">CPU: {frame.cpuUsage}%</span>
                            <span className="text-luxora">RAM: {frame.ramUsage}GB</span>
                            <span className="text-blue-400">LAG: {frame.networkLag}ms</span>
                          </div>
                        ))}
                        {timelineHistory.length === 0 && (
                          <div className="text-gray-600 italic">Awaiting telemetry frames...</div>
                        )}
                      </div>
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
              </div>
            )}

            {/* ── SHARED TERMINAL FEED & RUNE DISPATCH ── */}
            <div className="border-t border-gray-800 pt-4 mt-auto flex flex-col gap-3">
              <div className="h-24 overflow-y-auto bg-black border border-gray-800 p-2.5 rounded font-mono text-xs flex flex-col gap-1 min-h-[5rem]">
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

          </div>

          {/* Right Column (Voice Controller Deck) */}
          <aside className="w-64 border border-[#6B3FA0] bg-[#1e1e1e] p-4 rounded flex flex-col justify-between shadow-[0_0_15px_rgba(107,63,160,0.2)]">
            <div>
              <h2 className="text-sm font-bold text-[#6B3FA0] border-b border-gray-700 pb-2 mb-3">🎙️ VOICE CONTROLLER</h2>
              <p className="text-xs text-gray-400 mb-4">
                Hold button or issue standard OpenCLI targets natively via text loop.
              </p>

              <button
                id="mic-btn"
                onClick={handleCaptureToggle}
                className={`w-full py-4 font-bold rounded border transition text-sm flex items-center justify-center gap-2 ${
                  voiceCapturing
                    ? 'bg-green-900 border-green-500 text-white shadow-[0_0_10px_rgba(34,197,94,0.3)]'
                    : 'bg-[#6B3FA0] border-purple-500 text-white hover:bg-purple-800 glow-purple active:scale-95'
                }`}
              >
                <span>🔴</span> {voiceCapturing ? 'CAPTURE STANDBY' : 'INITIALIZE CAPTURE'}
              </button>

              {/* Master Volume Slider (Kickbox-audio) */}
              <div className="mt-6">
                <div className="flex justify-between items-center text-xs mb-1">
                  <span className="text-[#D4AF37] font-bold">KICKBOX MASTER VOL</span>
                  <span className="text-white font-bold">{Math.round(masterVolume * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={masterVolume}
                  onChange={handleVolumeChange}
                  className="w-full h-1 bg-black border border-gray-800 rounded-lg appearance-none cursor-pointer accent-[#D4AF37]"
                />
              </div>
            </div>

            <div className="bg-[#050505] border border-gray-800 p-3 rounded text-[10px] text-gray-400 font-mono">
              <p className="text-[#D4AF37] mb-1">SYSTEM_RECON_STREAM:</p>
              <p id="console-stream" className="whitespace-pre-wrap select-text selection:bg-[#6B3FA0]">{speechConsoleLog}</p>
            </div>
          </aside>

        </section>
      </main>

      {/* ── FOOTER ── */}
      <footer className="border-t border-[#6B3FA0]/30 bg-[#050505] p-2 text-[10px] text-gray-500 flex justify-between z-10">
        <span>&gt; Server: localhost:8811 // Substrate Local Layer 2 Loaded</span>
        <span className="text-[#D4AF37]">Dreams don't come true, visions do. ⚡</span>
      </footer>
    </div>
  );
}
