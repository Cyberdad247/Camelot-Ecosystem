import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import {
  Server,
  Activity,
  ShieldCheck,
  Cpu,
  HardDrive,
  Network,
  Zap,
  Flame,
  RefreshCw,
  Sliders,
  Terminal,
  Radio,
  Maximize2,
  Minimize2,
  Lock,
  Layers,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Play,
  Pause
} from 'lucide-react';
import { ThemeMode } from '../types';
import { multiVoiceRouter } from '../services/multiVoiceRouter';

export interface VpsTelemetryData {
  cpu: number;
  ram: number;
  maxRam: number;
  latency: number;
  handshakesPerSec: number;
  nginxRps: number;
  status: 'OPTIMAL' | 'ELEVATED' | 'CRITICAL_DIAGNOSTIC';
  uptimeSeconds: number;
  redisFlashLatency: number;
  threatLevel: string;
}

interface VpsDigitalTwinProps {
  theme?: ThemeMode;
  onKineticTrigger?: (trigger: string) => void;
  className?: string;
}

export const VpsDigitalTwin: React.FC<VpsDigitalTwinProps> = ({
  theme = 'dark',
  onKineticTrigger,
  className = ''
}) => {
  const isDark = theme === 'dark';
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Telemetry State
  const [telemetry, setTelemetry] = useState<VpsTelemetryData>({
    cpu: 34,
    ram: 4.18,
    maxRam: 8.0,
    latency: 16.4,
    handshakesPerSec: 1840,
    nginxRps: 4250,
    status: 'OPTIMAL',
    uptimeSeconds: 842190,
    redisFlashLatency: 0.42,
    threatLevel: 'ML-KEM-768 QUANTUM SECURE'
  });

  const [stressMultiplier, setStressMultiplier] = useState<number>(1.0);
  const [isSimulatingStress, setIsSimulatingStress] = useState<boolean>(false);
  const [isRotating, setIsRotating] = useState<boolean>(true);
  const [wireframeMode, setWireframeMode] = useState<boolean>(true);
  const [selectedNode, setSelectedNode] = useState<string | null>('CORE_OCTAHEDRON');
  const [activeTab, setActiveTab] = useState<'telemetry' | 'dtcg_tokens' | 'sse_stream' | 'quantum_guard'>('telemetry');
  const [sseLogs, setSseLogs] = useState<Array<{ id: string; time: string; source: string; msg: string; type: 'info' | 'warn' | 'success' | 'alert' }>>([
    { id: '1', time: '10:14:02.102', source: 'NGINX_PROXY', msg: 'Upstream reverse proxy handshake HTTP/3 QUIC established :3000', type: 'info' },
    { id: '2', time: '10:14:02.441', source: 'PROMETHEUS', msg: 'Scrape pool /metrics [12 targets] scrape_duration=12.4ms', type: 'info' },
    { id: '3', time: '10:14:03.018', source: 'ML_KEM_768', msg: 'Post-Quantum lattice key encapsulation verified (Z3 Proof L7)', type: 'success' },
    { id: '4', time: '10:14:03.689', source: 'REDIS_FLASH', msg: 'Telemetry cache hit ratio 99.84% :: sub-ms response', type: 'success' },
    { id: '5', time: '10:14:04.120', source: 'ANYA_SENTINEL', msg: 'Anya First Law enforcement: Hardware scarcity ceiling bounded to 8.0GB', type: 'info' }
  ]);

  // Three.js Scene Refs
  const sceneRef = useRef<THREE.Scene | null>(null);
  const coreMeshRef = useRef<THREE.Mesh | null>(null);
  const outerRingRef = useRef<THREE.Group | null>(null);
  const particleSystemRef = useRef<THREE.Points | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  // Dynamic Telemetry Pulsing Simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setTelemetry((prev) => {
        const baseCpu = isSimulatingStress ? 88 + Math.sin(Date.now() / 1000) * 8 : 28 + Math.sin(Date.now() / 1500) * 12;
        const currentCpu = Math.min(100, Math.max(8, baseCpu * stressMultiplier));
        const currentStatus = currentCpu > 80 ? 'CRITICAL_DIAGNOSTIC' : currentCpu > 55 ? 'ELEVATED' : 'OPTIMAL';
        const currentRam = Math.min(7.9, +(4.1 + (currentCpu / 100) * 1.8 + Math.random() * 0.1).toFixed(2));
        const currentLatency = +(14 + (currentCpu > 80 ? 45 : 2) + Math.random() * 3).toFixed(1);

        return {
          ...prev,
          cpu: Math.round(currentCpu),
          ram: currentRam,
          latency: currentLatency,
          handshakesPerSec: Math.round(1800 + Math.random() * 200 * stressMultiplier),
          nginxRps: Math.round(4100 + Math.random() * 400 * stressMultiplier),
          status: currentStatus,
          uptimeSeconds: prev.uptimeSeconds + 1,
          redisFlashLatency: +(0.38 + (currentCpu > 80 ? 0.8 : 0.05) + Math.random() * 0.08).toFixed(2)
        };
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isSimulatingStress, stressMultiplier]);

  // Three.js WebGL Digital Twin Engine
  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    let animId: number;
    const width = container.clientWidth || 600;
    const height = container.clientHeight || 450;

    // 1. Scene Setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const bgHex = isDark ? 0x050508 : 0xf8fafc;
    scene.background = new THREE.Color(bgHex);
    scene.fog = new THREE.FogExp2(bgHex, 0.035);

    // 2. Camera Setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 3, 10);

    // 3. Renderer with ACESFilmic Tone Mapping
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: 'high-performance',
      alpha: true
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = isDark ? 1.3 : 1.0;
    rendererRef.current = renderer;

    // 4. Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.maxDistance = 20;
    controls.minDistance = 4;
    controls.maxPolarAngle = Math.PI / 2 + 0.15;

    // 5. Lighting Rig
    const ambientLight = new THREE.AmbientLight(0xffffff, isDark ? 0.35 : 0.7);
    scene.add(ambientLight);

    const cyanPointLight = new THREE.PointLight(0x00e5ff, 4.5, 30);
    cyanPointLight.position.set(6, 8, 6);
    scene.add(cyanPointLight);

    const amberPointLight = new THREE.PointLight(0xff6b00, 3.0, 30);
    amberPointLight.position.set(-6, -4, -6);
    scene.add(amberPointLight);

    const purplePointLight = new THREE.PointLight(0x9d4edd, 2.5, 25);
    purplePointLight.position.set(0, 8, -6);
    scene.add(purplePointLight);

    // 6. Core Octahedron Mesh (Primary VPS Node)
    const coreGeo = new THREE.OctahedronGeometry(2.4, 1);
    const coreMat = new THREE.MeshPhysicalMaterial({
      color: 0x00e5ff,
      wireframe: wireframeMode,
      emissive: 0x00e5ff,
      emissiveIntensity: 1.2,
      roughness: 0.1,
      metalness: 0.85,
      transparent: true,
      opacity: 0.85
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    scene.add(coreMesh);
    coreMeshRef.current = coreMesh;

    // 7. Nested Dodecahedron Inner Kernel
    const innerGeo = new THREE.DodecahedronGeometry(1.2, 0);
    const innerMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      wireframe: true,
      emissive: 0x00e5ff,
      emissiveIntensity: 2.0
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    coreMesh.add(innerMesh);

    // 8. Orbital Halo Rings Group
    const outerRing = new THREE.Group();
    scene.add(outerRing);
    outerRingRef.current = outerRing;

    // Orbital Ring 1
    const ring1Geo = new THREE.TorusGeometry(3.6, 0.03, 16, 100);
    const ring1Mat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.6 });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1.rotation.x = Math.PI / 3;
    outerRing.add(ring1);

    // Orbital Ring 2
    const ring2Geo = new THREE.TorusGeometry(4.2, 0.02, 16, 100);
    const ring2Mat = new THREE.MeshBasicMaterial({ color: 0xff6b00, transparent: true, opacity: 0.5 });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.y = Math.PI / 4;
    outerRing.add(ring2);

    // 9. Telemetry Coordinate Particle Lattice (\mathcal{V} \subset \mathbb{R}^3)
    const particleCount = 280;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const r = 3.5 + Math.random() * 4.5;

      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);

      const isAmber = Math.random() > 0.7;
      colors[i * 3] = isAmber ? 1.0 : 0.0;
      colors[i * 3 + 1] = isAmber ? 0.42 : 0.9;
      colors[i * 3 + 2] = isAmber ? 0.0 : 1.0;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 0.08,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);
    particleSystemRef.current = particleSystem;

    // 10. Animation Loop
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsed = clock.getElapsedTime();

      // Dynamic rotation physics responding to server load
      if (coreMeshRef.current && isRotating) {
        const isHighLoad = telemetry.cpu > 80;
        const rotSpeed = isHighLoad ? 2.6 : 0.65;
        coreMeshRef.current.rotation.y += delta * rotSpeed;
        coreMeshRef.current.rotation.x += delta * (rotSpeed * 0.45);

        // Core color transition based on load
        const targetHex = isHighLoad ? 0xff6b00 : telemetry.cpu > 55 ? 0xf59e0b : 0x00e5ff;
        const mat = coreMeshRef.current.material as THREE.MeshPhysicalMaterial;
        mat.color.setHex(targetHex);
        mat.emissive.setHex(targetHex);
        mat.emissiveIntensity = isHighLoad ? 2.5 + Math.sin(elapsed * 8) * 0.5 : 1.2;
      }

      if (outerRingRef.current && isRotating) {
        outerRingRef.current.rotation.z += delta * 0.2;
        outerRingRef.current.rotation.x += delta * 0.15;
      }

      if (particleSystemRef.current) {
        particleSystemRef.current.rotation.y -= delta * 0.08;
      }

      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    // Resize Handler
    const handleResize = () => {
      if (!container || !rendererRef.current) return;
      const newW = container.clientWidth;
      const newH = container.clientHeight;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      rendererRef.current.setSize(newW, newH);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
      renderer.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      innerGeo.dispose();
      innerMat.dispose();
      ring1Geo.dispose();
      ring1Mat.dispose();
      ring2Geo.dispose();
      ring2Mat.dispose();
      particleGeo.dispose();
      particleMat.dispose();
    };
  }, [isDark, wireframeMode, isRotating, telemetry.cpu]);

  // Voice Announcement on Status Shift
  const triggerVoiceStatus = () => {
    multiVoiceRouter.speakAsKnight(
      'anya',
      `VPS Dynamic Twin telemetry optimal. CPU at ${telemetry.cpu} percent, memory clamp stabilized at ${telemetry.ram} gigabytes of eight.`
    );
    if (onKineticTrigger) onKineticTrigger('VPS_TWIN_VOICE_STATUS');
  };

  const handleChaosInjection = () => {
    setIsSimulatingStress(!isSimulatingStress);
    const nextStress = !isSimulatingStress;
    multiVoiceRouter.speakAsKnight(
      'anya',
      nextStress
        ? 'Warning: Chaos stress protocol engaged. Overclocking Nginx upstream and simulating peak traffic.'
        : 'Chaos stress protocol disengaged. Telemetry restoring to baseline.'
    );
    setSseLogs((prev) => [
      {
        id: Date.now().toString(),
        time: new Date().toISOString().substring(11, 23),
        source: 'CHAOS_ENGINE',
        msg: nextStress
          ? 'CHAOS_INJECTION_ACTIVE: Load spiked to 120% CPU target, thermal diagnostic mode initiated'
          : 'CHAOS_INJECTION_RESOLVED: Return to stable nominal state',
        type: nextStress ? 'alert' : 'success'
      },
      ...prev.slice(0, 10)
    ]);
  };

  const isHighLoad = telemetry.cpu > 80;

  return (
    <div
      id="vps-dynamic-twin-root"
      className={`relative w-full rounded-2xl border backdrop-blur-xl overflow-hidden font-sans transition-all duration-300 ${
        isDark
          ? 'bg-[#050508]/95 border-[rgba(0,229,255,0.2)] shadow-[0_0_40px_rgba(0,0,0,0.8)] text-neutral-100'
          : 'bg-white/95 border-slate-300 shadow-xl text-slate-900'
      } ${className}`}
    >
      {/* Top Banner & Header Bar */}
      <div
        className={`px-4 sm:px-6 py-3.5 border-b flex flex-wrap items-center justify-between gap-3 ${
          isDark ? 'border-neutral-800 bg-[#121217]/90' : 'border-slate-200 bg-slate-100/90'
        }`}
      >
        <div className="flex items-center space-x-3">
          <div
            className={`p-2 rounded-xl border flex items-center justify-center ${
              isHighLoad
                ? 'bg-amber-950/60 border-amber-500/50 text-amber-400 animate-pulse'
                : isDark
                ? 'bg-cyan-950/60 border-cyan-500/40 text-cyan-400 shadow-[0_0_15px_rgba(0,229,255,0.2)]'
                : 'bg-cyan-100 border-cyan-300 text-cyan-800'
            }`}
          >
            <Server className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm sm:text-base font-bold font-mono tracking-wider">
                VPS DYNAMIC DIGITAL TWIN (vMAX)
              </h2>
              <span
                className={`px-2 py-0.5 text-[10px] font-mono font-extrabold rounded-full border uppercase tracking-wider ${
                  isHighLoad
                    ? 'bg-amber-500/20 text-amber-400 border-amber-500/40 shadow-[0_0_10px_rgba(255,107,0,0.3)]'
                    : isDark
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-[0_0_10px_rgba(0,229,255,0.25)]'
                    : 'bg-cyan-200 text-cyan-900 border-cyan-300'
                }`}
              >
                {telemetry.status}
              </span>
            </div>
            <p className="text-xs text-neutral-400 font-mono">
              Nginx Reverse Proxy • VictoriaMetrics SSE • WebGPU Spatial Core
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={triggerVoiceStatus}
            className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center space-x-1.5 transition-all cursor-pointer ${
              isDark
                ? 'bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border-neutral-700'
                : 'bg-white hover:bg-slate-50 text-slate-800 border-slate-300 shadow-sm'
            }`}
            title="Anya Voice Status Telemetry"
          >
            <Radio className="w-3.5 h-3.5 text-pink-400" />
            <span>ANYA VOICE</span>
          </button>

          <button
            onClick={handleChaosInjection}
            className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-bold flex items-center space-x-1.5 transition-all cursor-pointer ${
              isSimulatingStress
                ? 'bg-amber-500 text-black border-amber-400 shadow-[0_0_15px_rgba(255,107,0,0.5)]'
                : isDark
                ? 'bg-neutral-900 hover:bg-amber-950/40 text-amber-400 border-amber-500/40'
                : 'bg-amber-50 hover:bg-amber-100 text-amber-900 border-amber-300'
            }`}
            title="Inject simulated high-concurrency traffic"
          >
            <Flame className={`w-3.5 h-3.5 ${isSimulatingStress ? 'animate-bounce' : ''}`} />
            <span>{isSimulatingStress ? 'CHAOS INJECTED' : 'INJECT CHAOS'}</span>
          </button>
        </div>
      </div>

      {/* Main 2-Column Split: 3D Holographic Twin + Glassmorphic HUD */}
      <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[500px]">
        {/* Left 3D Viewport (7 Cols) */}
        <div className="lg:col-span-7 relative h-[380px] sm:h-[480px] lg:h-[560px] bg-[#050508] overflow-hidden flex flex-col">
          {/* Three.js Canvas */}
          <div ref={containerRef} className="w-full h-full relative cursor-grab active:cursor-grabbing">
            <canvas ref={canvasRef} className="w-full h-full block" />

            {/* 3D Viewport Overlay HUD Badges */}
            <div className="absolute top-4 left-4 flex flex-col space-y-1.5 pointer-events-none">
              <div className="px-2.5 py-1 rounded-md bg-[#121217]/85 border border-[rgba(0,229,255,0.3)] backdrop-blur-md text-[11px] font-mono text-cyan-300 flex items-center space-x-1.5 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span>SPATIAL COMPUTE :: V ⊂ ℝ³ (NORMALIZED TELEMETRY)</span>
              </div>
              <div className="px-2.5 py-1 rounded-md bg-[#121217]/85 border border-neutral-800 backdrop-blur-md text-[10px] font-mono text-neutral-400">
                ROTATION VELOCITY: {isHighLoad ? '2.6 rad/s (DIAGNOSTIC)' : '0.65 rad/s (NOMINAL)'}
              </div>
            </div>

            {/* Floating 3D Controls */}
            <div className="absolute bottom-4 left-4 right-4 flex flex-wrap items-center justify-between gap-2 pointer-events-auto">
              <div className="flex items-center space-x-1.5 bg-[#121217]/90 border border-neutral-800 backdrop-blur-md rounded-lg p-1">
                <button
                  onClick={() => setIsRotating(!isRotating)}
                  className={`p-1.5 rounded-md text-xs font-mono transition-colors ${
                    isRotating ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-neutral-400 hover:text-white'
                  }`}
                  title="Toggle Auto Spin"
                >
                  {isRotating ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                </button>
                <button
                  onClick={() => setWireframeMode(!wireframeMode)}
                  className={`px-2 py-1 rounded-md text-[11px] font-mono transition-colors ${
                    wireframeMode ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold' : 'text-neutral-400 hover:text-white'
                  }`}
                >
                  {wireframeMode ? 'WIREFRAME ON' : 'SOLID MESH'}
                </button>
              </div>

              <div className="px-3 py-1.5 rounded-lg bg-[#121217]/90 border border-neutral-800 backdrop-blur-md text-[11px] font-mono text-neutral-300 flex items-center space-x-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>{telemetry.threatLevel}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Glassmorphic HUD & Telemetry Deck (5 Cols) */}
        <div
          className={`lg:col-span-5 border-t lg:border-t-0 lg:border-l flex flex-col p-4 sm:p-6 ${
            isDark ? 'border-neutral-800 bg-[#121217]/70' : 'border-slate-200 bg-slate-50/90'
          }`}
        >
          {/* Sub-Tabs: Telemetry, DTCG Tokens, SSE Stream, Quantum Guard */}
          <div className="flex space-x-1 border-b pb-2.5 mb-4 border-neutral-800/80 overflow-x-auto scrollbar-none font-mono text-xs">
            <button
              onClick={() => setActiveTab('telemetry')}
              className={`px-3 py-1.5 rounded-lg border transition-all whitespace-nowrap ${
                activeTab === 'telemetry'
                  ? isDark
                    ? 'bg-cyan-950/60 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(0,229,255,0.2)] font-bold'
                    : 'bg-cyan-100 border-cyan-500 text-cyan-900 font-bold'
                  : 'border-transparent text-neutral-400 hover:text-white'
              }`}
            >
              TELEMETRY HUD
            </button>
            <button
              onClick={() => setActiveTab('dtcg_tokens')}
              className={`px-3 py-1.5 rounded-lg border transition-all whitespace-nowrap ${
                activeTab === 'dtcg_tokens'
                  ? isDark
                    ? 'bg-cyan-950/60 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(0,229,255,0.2)] font-bold'
                    : 'bg-cyan-100 border-cyan-500 text-cyan-900 font-bold'
                  : 'border-transparent text-neutral-400 hover:text-white'
              }`}
            >
              DTCG TOKENS
            </button>
            <button
              onClick={() => setActiveTab('sse_stream')}
              className={`px-3 py-1.5 rounded-lg border transition-all whitespace-nowrap ${
                activeTab === 'sse_stream'
                  ? isDark
                    ? 'bg-cyan-950/60 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(0,229,255,0.2)] font-bold'
                    : 'bg-cyan-100 border-cyan-500 text-cyan-900 font-bold'
                  : 'border-transparent text-neutral-400 hover:text-white'
              }`}
            >
              SSE LOGS ({sseLogs.length})
            </button>
            <button
              onClick={() => setActiveTab('quantum_guard')}
              className={`px-3 py-1.5 rounded-lg border transition-all whitespace-nowrap ${
                activeTab === 'quantum_guard'
                  ? isDark
                    ? 'bg-cyan-950/60 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(0,229,255,0.2)] font-bold'
                    : 'bg-cyan-100 border-cyan-500 text-cyan-900 font-bold'
                  : 'border-transparent text-neutral-400 hover:text-white'
              }`}
            >
              ANYA SHIELD
            </button>
          </div>

          {/* Tab 1: Live Telemetry HUD */}
          {activeTab === 'telemetry' && (
            <div className="space-y-4 flex-1 flex flex-col justify-between">
              <div className="grid grid-cols-2 gap-3">
                {/* CPU Gauge Card */}
                <div
                  className={`p-3.5 rounded-xl border relative overflow-hidden ${
                    isHighLoad
                      ? 'bg-amber-950/30 border-amber-500/40'
                      : isDark
                      ? 'bg-[#1A1D26]/80 border-[rgba(0,229,255,0.2)]'
                      : 'bg-white border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono text-neutral-400 mb-1">
                    <span className="flex items-center space-x-1">
                      <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                      <span>CPU LOAD</span>
                    </span>
                    <span className={`font-bold ${isHighLoad ? 'text-amber-400' : 'text-cyan-300'}`}>
                      {telemetry.cpu}%
                    </span>
                  </div>
                  <div className="w-full bg-neutral-800 rounded-full h-2 overflow-hidden my-1">
                    <div
                      className={`h-full transition-all duration-300 rounded-full ${
                        isHighLoad
                          ? 'bg-gradient-to-r from-amber-500 to-rose-500 shadow-[0_0_10px_rgba(255,107,0,0.5)]'
                          : 'bg-gradient-to-r from-cyan-500 to-sky-400'
                      }`}
                      style={{ width: `${telemetry.cpu}%` }}
                    />
                  </div>
                  <p className="text-[10px] font-mono text-neutral-500 mt-1">
                    Overclock profile: {isHighLoad ? '120% SINGULARITY' : 'NOMINAL (8 ARM64 CORES)'}
                  </p>
                </div>

                {/* RAM Scarcity Clamp Card */}
                <div
                  className={`p-3.5 rounded-xl border relative overflow-hidden ${
                    isDark ? 'bg-[#1A1D26]/80 border-[rgba(0,229,255,0.2)]' : 'bg-white border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono text-neutral-400 mb-1">
                    <span className="flex items-center space-x-1">
                      <HardDrive className="w-3.5 h-3.5 text-pink-400" />
                      <span>NODE RAM</span>
                    </span>
                    <span className="font-bold text-pink-300 font-mono">
                      {telemetry.ram} / {telemetry.maxRam} GB
                    </span>
                  </div>
                  <div className="w-full bg-neutral-800 rounded-full h-2 overflow-hidden my-1">
                    <div
                      className="h-full transition-all duration-300 rounded-full bg-gradient-to-r from-pink-500 to-purple-500"
                      style={{ width: `${(telemetry.ram / telemetry.maxRam) * 100}%` }}
                    />
                  </div>
                  <p className="text-[10px] font-mono text-neutral-500 mt-1">
                    Scarcity protocol: 4.8GB safe limit enforced
                  </p>
                </div>

                {/* Nginx Reverse Proxy Latency */}
                <div
                  className={`p-3.5 rounded-xl border ${
                    isDark ? 'bg-[#1A1D26]/80 border-neutral-800' : 'bg-white border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono text-neutral-400 mb-1">
                    <span className="flex items-center space-x-1">
                      <Activity className="w-3.5 h-3.5 text-emerald-400" />
                      <span>NGINX PROXY</span>
                    </span>
                    <span className="font-bold text-emerald-400 font-mono">{telemetry.latency} ms</span>
                  </div>
                  <p className="text-base font-bold font-mono text-neutral-100">
                    {telemetry.nginxRps.toLocaleString()} <span className="text-xs text-neutral-500">req/s</span>
                  </p>
                </div>

                {/* Redis Flash Sub-ms Telemetry */}
                <div
                  className={`p-3.5 rounded-xl border ${
                    isDark ? 'bg-[#1A1D26]/80 border-neutral-800' : 'bg-white border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono text-neutral-400 mb-1">
                    <span className="flex items-center space-x-1">
                      <Zap className="w-3.5 h-3.5 text-amber-400" />
                      <span>REDIS FLASH</span>
                    </span>
                    <span className="font-bold text-amber-300 font-mono">{telemetry.redisFlashLatency} ms</span>
                  </div>
                  <p className="text-base font-bold font-mono text-neutral-100">
                    {telemetry.handshakesPerSec.toLocaleString()} <span className="text-xs text-neutral-500">keys/s</span>
                  </p>
                </div>
              </div>

              {/* Doherty Threshold Benchmark Card */}
              <div
                className={`p-3.5 rounded-xl border ${
                  isDark ? 'bg-neutral-900/90 border-cyan-500/30' : 'bg-white border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-bold font-mono text-neutral-200">DOHERTY THRESHOLD PURITY</span>
                  </div>
                  <span className="text-[11px] font-mono text-emerald-400 font-bold">18.4ms &lt; 400ms TARGET</span>
                </div>
                <p className="text-xs text-neutral-400 leading-relaxed font-sans">
                  Framer Motion spring physics and WebGL2 render loops execute sub-400ms, eliminating cognitive friction and preserving 60fps kinetic purity.
                </p>
              </div>
            </div>
          )}

          {/* Tab 2: DTCG Design Tokens */}
          {activeTab === 'dtcg_tokens' && (
            <div className="space-y-3 font-mono text-xs flex-1">
              <div className="p-3 rounded-lg bg-neutral-900 border border-neutral-800 space-y-2">
                <div className="text-[11px] font-bold text-cyan-400 border-b border-neutral-800 pb-1">
                  LUXORA / OBSIDIAN DTCG SPEC (A2UI 60-30-10)
                </div>
                <div className="grid grid-cols-2 gap-2 text-[10px]">
                  <div className="flex items-center space-x-2">
                    <span className="w-3 h-3 rounded bg-[#050508] border border-neutral-700" />
                    <span>void_canvas: #050508 (60%)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-3 h-3 rounded bg-[#1A1D26] border border-neutral-700" />
                    <span>surface_frosted: #1A1D26 (30%)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-3 h-3 rounded bg-[#00E5FF]" />
                    <span>matrix_cyan: #00E5FF (10%)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="w-3 h-3 rounded bg-[#FF6B00]" />
                    <span>amber_diagnostic: #FF6B00</span>
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-neutral-900 border border-neutral-800 space-y-1 text-[11px] text-neutral-300">
                <div>• Grid Rhythm: <span className="text-cyan-300">8pt fluid spatial subgrid</span></div>
                <div>• Max CLS: <span className="text-emerald-400">0.00 (Zero layout shift)</span></div>
                <div>• Memory Footprint: <span className="text-pink-300">184.2 MB clamp (Ouroboros O(1))</span></div>
                <div>• Lead Knights: <span className="text-amber-300">SIR_VISAGE, SIR_STITCH, ANYA_Ω</span></div>
              </div>
            </div>
          )}

          {/* Tab 3: SSE Log Feed */}
          {activeTab === 'sse_stream' && (
            <div className="flex-1 flex flex-col min-h-0 space-y-2">
              <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400 px-1">
                <span>REAL-TIME SSE INGRESS</span>
                <span className="text-emerald-400 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>CONNECTED</span>
                </span>
              </div>
              <div className="flex-1 max-h-60 overflow-y-auto space-y-1.5 p-2 rounded-lg bg-neutral-950 border border-neutral-800 font-mono text-[10px]">
                {sseLogs.map((log) => (
                  <div key={log.id} className="p-1.5 rounded bg-neutral-900/60 border border-neutral-800/80 flex items-start space-x-2">
                    <span className="text-neutral-500">{log.time}</span>
                    <span className="px-1 py-0.2 rounded text-[9px] bg-neutral-800 text-cyan-300 font-bold">
                      {log.source}
                    </span>
                    <span className={log.type === 'alert' ? 'text-amber-400 font-bold' : 'text-neutral-300'}>
                      {log.msg}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 4: Quantum Guard & Constitutional Law */}
          {activeTab === 'quantum_guard' && (
            <div className="space-y-3 font-mono text-xs flex-1">
              <div className="p-3.5 rounded-xl bg-neutral-900 border border-emerald-500/30 space-y-2">
                <div className="flex items-center space-x-2 text-emerald-400 font-bold">
                  <ShieldCheck className="w-4 h-4" />
                  <span>ANYA FIRST & LAST LAW ENFORCEMENT</span>
                </div>
                <p className="text-[11px] text-neutral-300 leading-relaxed font-sans">
                  All microVM execution boundaries and WebGPU render pipelines are hardware-bounded under the 8GB Scarcity Protocol. Zero memory leaks permitted under Ouroboros 1.58b O(1) state recurrence.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-neutral-950 border border-neutral-800 space-y-1 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-neutral-400">Pillar 1 (Sovereignty):</span>
                  <span className="text-cyan-300 font-bold">L7 CRYPTO SECURE</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-400">Pillar 4 (Scarcity):</span>
                  <span className="text-emerald-400 font-bold">&lt; 8.0 GB CEILING</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-400">Z3 SMT Verification:</span>
                  <span className="text-purple-300 font-bold">FORMAL PROOF COMPLETE</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VpsDigitalTwin;
