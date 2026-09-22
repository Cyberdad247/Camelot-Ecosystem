import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import * as THREE from 'three';
import { 
  Search, 
  Zap, 
  Mic, 
  Volume2, 
  VolumeX, 
  Compass, 
  Sparkles, 
  ArrowRight,
  Layers,
  LayoutGrid,
  Cpu,
  Shield,
  Radio,
  Box,
  FileCode,
  Terminal as TerminalIcon,
  Globe,
  Network,
  Users,
  Scale,
  ChevronRight,
  Filter,
  CheckCircle2,
  LucideIcon,
  Headphones,
  ShieldCheck
} from 'lucide-react';
import { ActiveTab, ThemeMode } from '../types';
import { multiVoiceRouter } from '../services/multiVoiceRouter';

interface ArthurianVSPGatewayProps {
  onNavigate: (tab: ActiveTab) => void;
  onKineticTrigger: (trigger: string) => void;
  theme?: ThemeMode;
}

interface CartridgeItem {
  id: ActiveTab;
  name: string;
  code: string;
  tagline: string;
  leadKnight: string;
  division: string;
  color: string;
  borderHover: string;
  bgGlow: string;
  icon: LucideIcon;
  category: 'core' | 'intelligence' | 'governance' | 'dev';
  latency: string;
  status: 'ACTIVE' | 'ENGAGED' | 'STANDBY';
  voiceLine: string;
  speaker: 'anya' | 'arthur' | 'merlin' | 'boris' | 'gideon';
}

const CARTRIDGE_DIRECTORY: CartridgeItem[] = [
  {
    id: 'round-table',
    name: 'Round Table 12-Col Grid',
    code: 'ROUND_TABLE_12COL_GRID',
    tagline: '12-Column Sovereign Grid Cockpit (Boris, Codex, Helio, Octavian, Merlin & Anya)',
    leadKnight: 'SIR_BORIS',
    division: 'Core Engineering & Vanguard',
    color: 'text-cyan-300',
    borderHover: 'hover:border-cyan-400/80 hover:shadow-[0_0_25px_rgba(0,229,255,0.35)]',
    bgGlow: 'bg-cyan-950/20',
    icon: Users,
    category: 'core',
    latency: '0.12ms',
    status: 'ACTIVE',
    voiceLine: 'Round Table Cockpit initialized. 12-column A2UI grid and agent telemetry bridge active.',
    speaker: 'boris'
  },
  {
    id: 'audio-workbench',
    name: 'Kickbox Audio Workbench',
    code: 'KICKBOX_AUDIO_DSP',
    tagline: 'Kickbox 3D-to-2D Spatial DSP Canvas & Zero-GC Ring Buffers',
    leadKnight: 'ANYA_Ω',
    division: 'Intelligence',
    color: 'text-purple-400',
    borderHover: 'hover:border-purple-500/80 hover:shadow-[0_0_25px_rgba(157,78,221,0.35)]',
    bgGlow: 'bg-purple-950/20',
    icon: Headphones,
    category: 'intelligence',
    latency: '0.08ms',
    status: 'ACTIVE',
    voiceLine: 'Kickbox Audio Workbench engaged. 3D spatial soundfield and WASM DSP active.',
    speaker: 'anya'
  },
  {
    id: 'shadow-gauntlet',
    name: 'Gideon Shadow Gauntlet',
    code: 'SHADOW_MICROVM_GAUNTLET',
    tagline: 'Shadow Micro-VM TDD Gauntlet & Z3 Neurosymbolic SAT Invariants',
    leadKnight: 'SIR_GIDEON',
    division: 'Executive & Governance',
    color: 'text-emerald-400',
    borderHover: 'hover:border-emerald-500/80 hover:shadow-[0_0_25px_rgba(16,185,129,0.35)]',
    bgGlow: 'bg-emerald-950/20',
    icon: ShieldCheck,
    category: 'governance',
    latency: '0.04ms',
    status: 'ACTIVE',
    voiceLine: 'Sir Gideon Shadow MicroVM gauntlet online. Formal Z3 proofs verified.',
    speaker: 'merlin'
  },
  {
    id: 'cartridge-matrix',
    name: 'Cartridge Matrix Vanguard',
    code: 'CARTRIDGE_MATRIX_V4',
    tagline: 'Hot-Swappable Dioxus/WASM Micro-Frontends & Live Sandboxes',
    leadKnight: 'MERLIN_Ω',
    division: 'Core Engineering & Vanguard',
    color: 'text-pink-400',
    borderHover: 'hover:border-pink-500/80 hover:shadow-[0_0_25px_rgba(244,114,182,0.35)]',
    bgGlow: 'bg-pink-950/20',
    icon: Box,
    category: 'core',
    latency: '0.4ms',
    status: 'ACTIVE',
    voiceLine: 'Cartridge Matrix Vanguard online. Engaging hot-swappable micro-frontend cartridges.',
    speaker: 'merlin'
  },
  {
    id: 'digital-factory',
    name: 'Sovereign Digital Factory',
    code: 'FACTORY_BLAST_ENGINE',
    tagline: 'Autonomous Product Pipeline, 7-Gate Grill & Kinetic Injection',
    leadKnight: 'SIR_ARCHITECT',
    division: 'Core Engineering & Vanguard',
    color: 'text-amber-400',
    borderHover: 'hover:border-amber-500/80 hover:shadow-[0_0_25px_rgba(245,158,11,0.35)]',
    bgGlow: 'bg-amber-950/20',
    icon: Cpu,
    category: 'core',
    latency: '1.2ms',
    status: 'ENGAGED',
    voiceLine: 'Digital Factory BLAST engine activated. Autonomous generation pipeline standing by.',
    speaker: 'arthur'
  },
  {
    id: 'multivoice',
    name: 'Multi-Voice Router Deck',
    code: 'VOCODER_MULTIPLEX_V7',
    tagline: '8 Sovereign Knight Neural Vocoders & Speech Synthesis Multiplex',
    leadKnight: 'ANYA_Ω',
    division: 'Executive',
    color: 'text-purple-400',
    borderHover: 'hover:border-purple-500/80 hover:shadow-[0_0_25px_rgba(168,85,247,0.35)]',
    bgGlow: 'bg-purple-950/20',
    icon: Radio,
    category: 'intelligence',
    latency: '0.2ms',
    status: 'ACTIVE',
    voiceLine: 'Multi-Voice Router synchronized. Neural vocoder lattice calibrated.',
    speaker: 'anya'
  },
  {
    id: 'spatial-hud',
    name: 'Holographic 3D Spatial HUD',
    code: 'WEBGPU_SPATIAL_HUD',
    tagline: '3D Knight Avatars, WebGL Substrate & Spatial Audio Lattice',
    leadKnight: 'SIR_ANIMATOR',
    division: 'Streaming & Customer Ops',
    color: 'text-cyan-400',
    borderHover: 'hover:border-cyan-500/80 hover:shadow-[0_0_25px_rgba(0,229,255,0.35)]',
    bgGlow: 'bg-cyan-950/20',
    icon: Compass,
    category: 'intelligence',
    latency: '0.8ms',
    status: 'ACTIVE',
    voiceLine: 'Holographic Spatial HUD rendered. 3D avatar nodes online.',
    speaker: 'anya'
  },
  {
    id: 'contracts',
    name: 'Contract Schemas & Gideon Vault',
    code: 'GIDEON_Z3_PROOF_VAULT',
    tagline: 'MsgPack Schemas, AST Integrity & Formal Mathematical Proofs',
    leadKnight: 'SIR_WARDEN',
    division: 'Core Engineering & Vanguard',
    color: 'text-emerald-400',
    borderHover: 'hover:border-emerald-500/80 hover:shadow-[0_0_25px_rgba(16,185,129,0.35)]',
    bgGlow: 'bg-emerald-950/20',
    icon: Shield,
    category: 'governance',
    latency: '0.1ms',
    status: 'ACTIVE',
    voiceLine: 'Contract Vault accessed. Gideon Z3 verification gates armed.',
    speaker: 'merlin'
  },
  {
    id: 'htmx',
    name: 'HTMX Sovereign Command Center',
    code: 'HTMX_GO_SSE_BROADCAST',
    tagline: 'Go Backend SSE Streams, Real-Time DOM Fragments & Live Audit',
    leadKnight: 'ANYA_Ω',
    division: 'Executive',
    color: 'text-amber-300',
    borderHover: 'hover:border-amber-400/80 hover:shadow-[0_0_25px_rgba(251,191,36,0.35)]',
    bgGlow: 'bg-amber-950/20',
    icon: Globe,
    category: 'dev',
    latency: '0.5ms',
    status: 'ENGAGED',
    voiceLine: 'HTMX Command Center engaged. Live SSE fragments streaming.',
    speaker: 'anya'
  },
  {
    id: 'lattice',
    name: 'Swarm Lattice Visualizer',
    code: 'DAG_TOPOLOGY_MONITOR',
    tagline: 'Real-time DAG State Graph, Bottleneck Triaging & Flow Vectors',
    leadKnight: 'MERLIN_Ω',
    division: 'Core Engineering & Vanguard',
    color: 'text-sky-400',
    borderHover: 'hover:border-sky-500/80 hover:shadow-[0_0_25px_rgba(56,189,248,0.35)]',
    bgGlow: 'bg-sky-950/20',
    icon: Network,
    category: 'intelligence',
    latency: '0.3ms',
    status: 'ACTIVE',
    voiceLine: 'Swarm Lattice topology mapped. Real-time agent nodes monitored.',
    speaker: 'merlin'
  },
  {
    id: 'knights',
    name: 'Round Table Knight Roster',
    code: 'KNIGHT_ROSTER_TELEMETRY',
    tagline: '8 Sovereign Knights, Memory Quota & Real-time Division Load',
    leadKnight: 'KING_ARTHUR',
    division: 'Executive',
    color: 'text-blue-400',
    borderHover: 'hover:border-blue-500/80 hover:shadow-[0_0_25px_rgba(96,165,250,0.35)]',
    bgGlow: 'bg-blue-950/20',
    icon: Users,
    category: 'governance',
    latency: '0.2ms',
    status: 'ACTIVE',
    voiceLine: 'Round Table Knights summoned. Division telemetry physicalized.',
    speaker: 'arthur'
  },
  {
    id: 'constitution',
    name: 'Constitutional Governance',
    code: 'ANYA_FIRST_LAW_APE',
    tagline: 'Anya First Law, Human-In-The-Loop Authorizations & Sandboxes',
    leadKnight: 'ANYA_Ω',
    division: 'Executive',
    color: 'text-rose-400',
    borderHover: 'hover:border-rose-500/80 hover:shadow-[0_0_25px_rgba(251,113,133,0.35)]',
    bgGlow: 'bg-rose-950/20',
    icon: Scale,
    category: 'governance',
    latency: '0.05ms',
    status: 'ACTIVE',
    voiceLine: 'Constitutional Laws verified. Anya First Law and APEE triage asserted.',
    speaker: 'anya'
  },
  {
    id: 'terminal',
    name: 'Interactive Sovereign Terminal',
    code: 'WASMTIME_IPC_TERMINAL',
    tagline: 'Direct DAG Execution, SQLite WAL2 Stream & Wasmtime Host CLI',
    leadKnight: 'BORIS',
    division: 'Core Engineering & Vanguard',
    color: 'text-cyan-300',
    borderHover: 'hover:border-cyan-400/80 hover:shadow-[0_0_25px_rgba(103,232,249,0.35)]',
    bgGlow: 'bg-cyan-950/20',
    icon: TerminalIcon,
    category: 'dev',
    latency: '0.1ms',
    status: 'ACTIVE',
    voiceLine: 'Terminal active. Direct DAG execution stream opened.',
    speaker: 'boris'
  },
  {
    id: 'vfs',
    name: 'VFS Sovereign Explorer',
    code: 'ISOMORPHIC_VFS_CORE',
    tagline: 'Master Scaffold Files, Dioxus Components, Contracts & Rust Specs',
    leadKnight: 'SIR_SCRIBE',
    division: 'Core Engineering & Vanguard',
    color: 'text-teal-400',
    borderHover: 'hover:border-teal-500/80 hover:shadow-[0_0_25px_rgba(45,212,191,0.35)]',
    bgGlow: 'bg-teal-950/20',
    icon: FileCode,
    category: 'dev',
    latency: '0.2ms',
    status: 'ACTIVE',
    voiceLine: 'VFS Master Scaffold opened. Isomorphic file tree synchronized.',
    speaker: 'merlin'
  },
  {
    id: 'command-center',
    name: 'Unified Command Center',
    code: 'UNIFIED_DEV_DECK',
    tagline: 'Central Multi-Split Switchboard, Live Telemetry & System HUD',
    leadKnight: 'ANYA_Ω',
    division: 'Executive',
    color: 'text-amber-400',
    borderHover: 'hover:border-amber-500/80 hover:shadow-[0_0_25px_rgba(245,158,11,0.35)]',
    bgGlow: 'bg-amber-950/20',
    icon: Layers,
    category: 'core',
    latency: '0.3ms',
    status: 'ACTIVE',
    voiceLine: 'Command Center overview engaged. All operational subsystems active.',
    speaker: 'anya'
  }
];

// =========================================================================
// 3D Arthurian Cyber Citadel Substrate (Native High-Performance Three.js)
// =========================================================================

function Arthurian3DCanvas() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    let animationFrameId: number;
    let width = container.clientWidth || window.innerWidth;
    let height = container.clientHeight || window.innerHeight;

    // 1. Scene & Atmosphere
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020407);
    scene.fog = new THREE.FogExp2(0x03060d, 0.032);

    // 2. Camera Setup
    const camera = new THREE.PerspectiveCamera(46, width / height, 0.1, 100);
    camera.position.set(0, 1.2, 11);

    // 3. High Performance WebGL Renderer
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: 'high-performance',
      alpha: false
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;

    // 4. Lighting Rig
    const ambientLight = new THREE.AmbientLight(0x182030, 0.65);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 2.0);
    dirLight.position.set(0, 16, 8);
    scene.add(dirLight);

    const cyanPoint = new THREE.PointLight(0x00e5ff, 5.5, 28);
    cyanPoint.position.set(0, 4, -4);
    scene.add(cyanPoint);

    const purplePoint = new THREE.PointLight(0x9d4edd, 4.0, 22);
    purplePoint.position.set(-10, 2, -6);
    scene.add(purplePoint);

    const goldPoint = new THREE.PointLight(0xe5b842, 4.0, 22);
    goldPoint.position.set(10, 2, -6);
    scene.add(goldPoint);

    // 5. Celestial Outer Dome & Rings
    const domeGroup = new THREE.Group();
    domeGroup.position.set(0, 0, -15);

    const domeGeo = new THREE.SphereGeometry(28, 48, 48, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMat = new THREE.MeshStandardMaterial({
      color: 0x051020,
      roughness: 0.15,
      metalness: 0.85,
      side: THREE.DoubleSide
    });
    const domeMesh = new THREE.Mesh(domeGeo, domeMat);
    domeMesh.position.set(0, 4, 0);
    domeGroup.add(domeMesh);

    const domeWireGeo = new THREE.SphereGeometry(28.05, 32, 24, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeWireMat = new THREE.MeshBasicMaterial({
      color: 0x00e5ff,
      wireframe: true,
      transparent: true,
      opacity: 0.09
    });
    const domeWireMesh = new THREE.Mesh(domeWireGeo, domeWireMat);
    domeWireMesh.position.set(0, 4, 0);
    domeGroup.add(domeWireMesh);

    // Celestial Radian Rings
    const ringGroup = new THREE.Group();
    ringGroup.position.set(0, 6, 0);
    ringGroup.rotation.x = Math.PI / 2.2;

    const ring1Geo = new THREE.RingGeometry(26, 26.5, 64);
    const ring1Mat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, side: THREE.DoubleSide, transparent: true, opacity: 0.45 });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ringGroup.add(ring1);

    const ring2Geo = new THREE.RingGeometry(23, 23.3, 48);
    const ring2Mat = new THREE.MeshBasicMaterial({ color: 0x9d4edd, side: THREE.DoubleSide, transparent: true, opacity: 0.35 });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ringGroup.add(ring2);

    domeGroup.add(ringGroup);
    scene.add(domeGroup);

    // 6. Cyber Citadel Fortress
    const fortressGroup = new THREE.Group();
    fortressGroup.position.set(0, -2.5, -8);

    const darkMetalMat = new THREE.MeshStandardMaterial({ color: 0x0b101a, metalness: 0.92, roughness: 0.12 });
    const cyanNeonMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff });

    // Spire
    const spireGeo = new THREE.BoxGeometry(4.5, 7.5, 3.5);
    const spireMesh = new THREE.Mesh(spireGeo, darkMetalMat);
    spireMesh.position.set(0, 3.75, 0);
    fortressGroup.add(spireMesh);

    // Arch
    const archGeo = new THREE.CylinderGeometry(1.6, 2.6, 2.2, 8);
    const archMesh = new THREE.Mesh(archGeo, darkMetalMat);
    archMesh.position.set(0, 8, 0);
    fortressGroup.add(archMesh);

    // Glowing Portal Gate
    const portalGeo = new THREE.BoxGeometry(1.5, 3.0, 0.2);
    const portalMesh = new THREE.Mesh(portalGeo, cyanNeonMat);
    portalMesh.position.set(0, 1.3, 1.8);
    fortressGroup.add(portalMesh);

    // Ramparts
    const rampartGeo = new THREE.BoxGeometry(5.5, 4.2, 2.5);
    const leftRampart = new THREE.Mesh(rampartGeo, darkMetalMat);
    leftRampart.position.set(-5, 2.1, -0.5);
    fortressGroup.add(leftRampart);

    const rightRampart = new THREE.Mesh(rampartGeo, darkMetalMat);
    rightRampart.position.set(5, 2.1, -0.5);
    fortressGroup.add(rightRampart);

    // Battlement Pillars & Slits
    const pillarGeo = new THREE.BoxGeometry(1.4, 3.8, 2);
    const slitGeo = new THREE.BoxGeometry(0.08, 2.6, 0.05);

    [-9.5, -7.5, 7.5, 9.5].forEach((x) => {
      const pillar = new THREE.Mesh(pillarGeo, darkMetalMat);
      pillar.position.set(x, 1.7, -1);
      fortressGroup.add(pillar);
    });

    [-8, -5, -3, 3, 5, 8].forEach((x) => {
      const slit = new THREE.Mesh(slitGeo, cyanNeonMat);
      slit.position.set(x, 2.3, 0.4);
      fortressGroup.add(slit);
    });

    // Converging Laser Beams
    const laserGroup = new THREE.Group();
    const createLaser = (start: [number, number, number], end: [number, number, number], color = 0x00e5ff, opacity = 0.7) => {
      const pts = [new THREE.Vector3(...start), new THREE.Vector3(...end)];
      const geo = new THREE.BufferGeometry().setFromPoints(pts);
      const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity });
      return new THREE.Line(geo, mat);
    };

    laserGroup.add(createLaser([-14, -1, 4], [0, 9.5, 0], 0x00e5ff, 0.75));
    laserGroup.add(createLaser([-8, 3, 0], [0, 9.5, 0], 0x00e5ff, 0.55));
    laserGroup.add(createLaser([14, -1, 4], [0, 9.5, 0], 0x00e5ff, 0.75));
    laserGroup.add(createLaser([8, 3, 0], [0, 9.5, 0], 0x00e5ff, 0.55));
    fortressGroup.add(laserGroup);

    scene.add(fortressGroup);

    // 7. Colossal Sentinels (Mechanical Knights)
    const sentinelGroup = new THREE.Group();

    const buildSentinel = (x: number, z: number, rotY: number) => {
      const sent = new THREE.Group();
      sent.position.set(x, -1.8, z);
      sent.rotation.y = rotY;

      // Pedestal
      const pedGeo = new THREE.CylinderGeometry(1.2, 1.4, 0.8, 8);
      const pedMesh = new THREE.Mesh(pedGeo, darkMetalMat);
      pedMesh.position.set(0, -0.8, 0);
      sent.add(pedMesh);

      // Torso
      const torsoGeo = new THREE.CylinderGeometry(0.7, 0.5, 2.2, 6);
      const torsoMesh = new THREE.Mesh(torsoGeo, darkMetalMat);
      torsoMesh.position.set(0, 1.8, 0);
      sent.add(torsoMesh);

      // Reactor Chest Core
      const chestGeo = new THREE.BoxGeometry(0.35, 0.45, 0.1);
      const chestMesh = new THREE.Mesh(chestGeo, cyanNeonMat);
      chestMesh.position.set(0, 2.1, 0.5);
      sent.add(chestMesh);

      // Helm & Optic Visor
      const helmGeo = new THREE.SphereGeometry(0.45, 12, 12);
      const helmMesh = new THREE.Mesh(helmGeo, darkMetalMat);
      helmMesh.position.set(0, 3.2, 0);
      sent.add(helmMesh);

      const visorGeo = new THREE.BoxGeometry(0.4, 0.1, 0.1);
      const visorMesh = new THREE.Mesh(visorGeo, cyanNeonMat);
      visorMesh.position.set(0, 3.2, 0.35);
      sent.add(visorMesh);

      // Pauldrons
      const pauldronGeo = new THREE.BoxGeometry(0.65, 0.8, 0.7);
      const leftPaul = new THREE.Mesh(pauldronGeo, darkMetalMat);
      leftPaul.position.set(-0.9, 2.4, 0);
      sent.add(leftPaul);

      const rightPaul = new THREE.Mesh(pauldronGeo, darkMetalMat);
      rightPaul.position.set(0.9, 2.4, 0);
      sent.add(rightPaul);

      // Greatsword
      const swordGeo = new THREE.CylinderGeometry(0.05, 0.05, 3.4, 8);
      const swordMat = new THREE.MeshStandardMaterial({ color: 0x1a233a, metalness: 0.9 });
      const sword = new THREE.Mesh(swordGeo, swordMat);
      sword.position.set(0.65, 0.8, 0.5);
      sword.rotation.x = 0.1;
      sword.rotation.z = -0.05;
      sent.add(sword);

      return sent;
    };

    sentinelGroup.add(buildSentinel(-11.5, -4, 0.3));
    sentinelGroup.add(buildSentinel(-6.8, -3.2, 0.2));
    sentinelGroup.add(buildSentinel(6.8, -3.2, -0.2));
    sentinelGroup.add(buildSentinel(11.5, -4, -0.3));

    scene.add(sentinelGroup);

    // 8. Ground Floor & Reflective Cyber Tracks
    const floorGroup = new THREE.Group();
    floorGroup.position.set(0, -2.5, 0);

    const floorGeo = new THREE.PlaneGeometry(60, 60);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x030509,
      roughness: 0.08,
      metalness: 0.96
    });
    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    floorMesh.rotation.x = -Math.PI / 2;
    floorGroup.add(floorMesh);

    // Center Runway Track
    const runwayGeo = new THREE.PlaneGeometry(3.4, 30);
    const runwayMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.14 });
    const runwayMesh = new THREE.Mesh(runwayGeo, runwayMat);
    runwayMesh.rotation.x = -Math.PI / 2;
    runwayMesh.position.set(0, 0.01, 5);
    floorGroup.add(runwayMesh);

    // Neon Highway Edge Tracks
    const trackGeo = new THREE.PlaneGeometry(0.06, 30);
    const track1 = new THREE.Mesh(trackGeo, cyanNeonMat);
    track1.rotation.x = -Math.PI / 2;
    track1.position.set(-1.7, 0.02, 5);
    floorGroup.add(track1);

    const track2 = new THREE.Mesh(trackGeo, cyanNeonMat);
    track2.rotation.x = -Math.PI / 2;
    track2.position.set(1.7, 0.02, 5);
    floorGroup.add(track2);

    scene.add(floorGroup);

    // 9. Particle Star Field
    const starCount = 350;
    const starGeo = new THREE.BufferGeometry();
    const starPositions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
      starPositions[i] = (Math.random() - 0.5) * 50;
      starPositions[i + 1] = Math.random() * 25 - 2;
      starPositions[i + 2] = -15 - Math.random() * 20;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    const starMat = new THREE.PointsMaterial({ size: 0.08, color: 0x00e5ff, transparent: true, opacity: 0.65 });
    const stars = new THREE.Points(starGeo, starMat);
    scene.add(stars);

    // 10. Mouse Parallax Motion
    let mouseX = 0;
    let mouseY = 0;
    const handleMouseMove = (e: MouseEvent) => {
      const normX = (e.clientX / window.innerWidth) * 2 - 1;
      const normY = -(e.clientY / window.innerHeight) * 2 + 1;
      mouseX = normX * 0.4;
      mouseY = normY * 0.2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // 11. Render / Animation Loop
    const clock = new THREE.Clock();

    const animate = () => {
      const t = clock.getElapsedTime();

      // Rotate dome & rings
      domeMesh.rotation.y = t * 0.015;
      ringGroup.rotation.z = -t * 0.01;

      // Pulse Laser Group
      laserGroup.rotation.y = Math.sin(t * 0.2) * 0.03;

      // Gentle Sentinel Float
      sentinelGroup.position.y = Math.sin(t * 0.8) * 0.04;

      // Camera parallax lerp
      camera.position.x += (mouseX - camera.position.x) * 0.03;
      camera.position.y += (1.2 + mouseY - camera.position.y) * 0.03;
      camera.lookAt(0, 2.5, -6);

      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    // Resize Handler
    const handleResize = () => {
      if (!container) return;
      width = container.clientWidth || window.innerWidth;
      height = container.clientHeight || window.innerHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      scene.clear();
    };
  }, []);

  return (
    <div ref={containerRef} className="absolute inset-0 w-full h-full pointer-events-auto">
      <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
}

// ==========================================
// Main Arthurian VSP Gateway Component
// ==========================================

export function ArthurianVSPGateway({
  onNavigate,
  onKineticTrigger,
  theme = 'dark'
}: ArthurianVSPGatewayProps) {
  const [intent, setIntent] = useState('');
  const [isRouting, setIsRouting] = useState(false);
  const [routedTarget, setRoutedTarget] = useState<string | null>(null);
  const [voiceActive, setVoiceActive] = useState(false);
  const [ambientAudioOn, setAmbientAudioOn] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'core' | 'intelligence' | 'governance' | 'dev'>('all');
  const [searchFilter, setSearchFilter] = useState('');

  const inputRef = useRef<HTMLInputElement>(null);
  const speechRecognitionRef = useRef<any>(null);

  // Quick preset shortcuts for immediate injection
  const PRESET_DIRECTIVES = [
    { label: '⚡ //matrix:hot-swap', query: 'Open Cartridge Matrix for hot-swapping', tab: 'cartridge-matrix' as ActiveTab, color: 'text-pink-400 border-pink-500/30' },
    { label: '⚙️ //factory:blast', query: 'Launch Sovereign Digital Factory BLAST engine', tab: 'digital-factory' as ActiveTab, color: 'text-amber-400 border-amber-500/30' },
    { label: '🎙️ //voice:multiplex', query: 'Initialize Multi-Voice Router audio deck', tab: 'multivoice' as ActiveTab, color: 'text-purple-400 border-purple-500/30' },
    { label: '🛡️ //audit:gideon', query: 'Audit AST schemas in Contract Vault', tab: 'contracts' as ActiveTab, color: 'text-emerald-400 border-emerald-500/30' },
    { label: '🌀 //spatial:hud', query: 'Engage Holographic 3D Spatial HUD', tab: 'spatial-hud' as ActiveTab, color: 'text-cyan-400 border-cyan-500/30' },
    { label: '🌐 //htmx:sse', query: 'Launch HTMX Command Center and Live SSE', tab: 'htmx' as ActiveTab, color: 'text-amber-300 border-amber-400/30' },
    { label: '👥 //knights:roster', query: 'Inspect Round Table Knight Roster and telemetry', tab: 'knights' as ActiveTab, color: 'text-blue-400 border-blue-500/30' }
  ];

  // Initialize Speech Recognition if supported
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((r: any) => r[0].transcript)
          .join('');
        setIntent(transcript);
      };

      recognition.onend = () => {
        setVoiceActive(false);
      };

      recognition.onerror = () => {
        setVoiceActive(false);
      };

      speechRecognitionRef.current = recognition;
    }
  }, []);

  const toggleVoiceRecording = () => {
    if (!speechRecognitionRef.current) {
      setVoiceActive(true);
      multiVoiceRouter.playCyberSfx('lock');
      setTimeout(() => {
        setIntent('Deploy UI/UX Cartridge with high-fidelity WebGPU preview');
        setVoiceActive(false);
      }, 1500);
      return;
    }

    if (voiceActive) {
      speechRecognitionRef.current.stop();
      setVoiceActive(false);
    } else {
      try {
        speechRecognitionRef.current.start();
        setVoiceActive(true);
        multiVoiceRouter.playCyberSfx('lock');
      } catch {
        setVoiceActive(false);
      }
    }
  };

  const toggleAmbientAudio = () => {
    const newState = !ambientAudioOn;
    setAmbientAudioOn(newState);
    if (newState) {
      multiVoiceRouter.playCyberSfx('boot');
      multiVoiceRouter.speakAsKnight('anya', 'Spatial audio lattice energized. All sensors calibrated.');
    }
  };

  // Launch Cartridge directly with Voice Confirmation & Transition
  const launchCartridgeDirect = (cartridge: CartridgeItem) => {
    setIsRouting(true);
    setRoutedTarget(cartridge.code);
    multiVoiceRouter.playCyberSfx('lock');

    setTimeout(() => {
      multiVoiceRouter.speakAsKnight(cartridge.speaker, cartridge.voiceLine);
    }, 200);

    setTimeout(() => {
      setIsRouting(false);
      setMenuOpen(false);
      onNavigate(cartridge.id);
      onKineticTrigger(`//route:${cartridge.id}`);
    }, 900);
  };

  // Neurosymbolic Intent Evaluation & Polyglot Matrix Routing
  const executeRouting = (rawQuery: string) => {
    const query = (rawQuery || intent).trim();
    if (!query) return;

    setIsRouting(true);
    multiVoiceRouter.playCyberSfx('lock');

    const lower = query.toLowerCase();
    let targetTab: ActiveTab = 'command-center';
    let targetName = 'COMMAND_CENTER_OVERVIEW';
    let speakerKnight: 'anya' | 'arthur' | 'merlin' | 'boris' | 'gideon' = 'anya';
    let voiceConfirmation = 'Routing directive through the Sovereign Polyglot Matrix.';

    // Check direct matching cartridge in directory
    const matched = CARTRIDGE_DIRECTORY.find(c => 
      lower.includes(c.id) || 
      lower.includes(c.name.toLowerCase()) || 
      lower.includes(c.code.toLowerCase())
    );

    if (matched) {
      targetTab = matched.id;
      targetName = matched.code;
      speakerKnight = matched.speaker;
      voiceConfirmation = matched.voiceLine;
    } else if (lower.includes('table') || lower.includes('captain') || lower.includes('boris') || lower.includes('helio') || lower.includes('octavian') || lower.includes('12-col') || lower.includes('grid') || lower.includes('cockpit')) {
      targetTab = 'round-table';
      targetName = 'ROUND_TABLE_12COL_GRID';
      speakerKnight = 'boris';
      voiceConfirmation = 'Round Table Agent Cockpit online. 12-column spatial grid and state bridge engaged.';
    } else if (lower.includes('kickbox') || lower.includes('dsp') || lower.includes('spatial audio') || lower.includes('fft') || lower.includes('frequency') || lower.includes('resonance')) {
      targetTab = 'audio-workbench';
      targetName = 'KICKBOX_AUDIO_DSP';
      speakerKnight = 'anya';
      voiceConfirmation = 'Kickbox Audio Workbench active. Zero-GC ring buffers and 3D spatial DSP online.';
    } else if (lower.includes('gauntlet') || lower.includes('tdd') || lower.includes('shadow') || lower.includes('microvm') || lower.includes('formal proof')) {
      targetTab = 'shadow-gauntlet';
      targetName = 'SHADOW_MICROVM_GAUNTLET';
      speakerKnight = 'gideon';
      voiceConfirmation = 'Sir Gideon Shadow MicroVM gauntlet engaged. 5/5 Z3 SAT proofs physicalized.';
    } else if (lower.includes('vps') || lower.includes('twin') || lower.includes('telemetry') || lower.includes('server') || lower.includes('nginx') || lower.includes('prometheus') || lower.includes('cartridge') || lower.includes('matrix') || lower.includes('hot-swap') || lower.includes('module') || lower.includes('ux') || lower.includes('ui') || lower.includes('vanguard')) {
      targetTab = 'cartridge-matrix';
      targetName = lower.includes('vps') || lower.includes('twin') ? 'VPS_DYNAMIC_TWIN_vMAX' : 'CARTRIDGE_MATRIX_V4';
      speakerKnight = 'anya';
      voiceConfirmation = lower.includes('vps') || lower.includes('twin')
        ? 'VPS Dynamic Twin engaged. Spatial WebGPU telemetry and Nginx proxy online.'
        : 'Cartridge Matrix online. Engaging hot-swappable micro-frontend cartridges.';
    } else if (lower.includes('factory') || lower.includes('blast') || lower.includes('build') || lower.includes('pipeline') || lower.includes('generate') || lower.includes('scaffold') || lower.includes('saas')) {
      targetTab = 'digital-factory';
      targetName = 'FACTORY_BLAST_ENGINE';
      speakerKnight = 'arthur';
      voiceConfirmation = 'Digital Factory BLAST engine activated. Autonomous generation pipeline standing by.';
    } else if (lower.includes('voice') || lower.includes('speech') || lower.includes('audio') || lower.includes('router') || lower.includes('multiplex') || lower.includes('tts') || lower.includes('stt')) {
      targetTab = 'multivoice';
      targetName = 'VOCODER_MULTIPLEX_V7';
      speakerKnight = 'anya';
      voiceConfirmation = 'Multi-Voice Router initialized. Sovereign Knight vocoders synchronized.';
    } else if (lower.includes('contract') || lower.includes('schema') || lower.includes('receipt') || lower.includes('vault') || lower.includes('proof') || lower.includes('gideon') || lower.includes('z3') || lower.includes('audit')) {
      targetTab = 'contracts';
      targetName = 'GIDEON_Z3_PROOF_VAULT';
      speakerKnight = 'merlin';
      voiceConfirmation = 'Contract Vault accessed. Gideon Z3 verification gates armed.';
    } else if (lower.includes('htmx') || lower.includes('go') || lower.includes('sse') || lower.includes('ledger') || lower.includes('stream') || lower.includes('fragment')) {
      targetTab = 'htmx';
      targetName = 'HTMX_GO_SSE_BROADCAST';
      speakerKnight = 'anya';
      voiceConfirmation = 'HTMX Sovereign Command Center engaged. Live SSE fragments streaming.';
    } else if (lower.includes('spatial') || lower.includes('3d') || lower.includes('hologram') || lower.includes('hud') || lower.includes('webgpu') || lower.includes('avatar')) {
      targetTab = 'spatial-hud';
      targetName = 'WEBGPU_SPATIAL_HUD';
      speakerKnight = 'anya';
      voiceConfirmation = 'Holographic Spatial HUD rendered. 3D Knight avatar lattice engaged.';
    } else if (lower.includes('lattice') || lower.includes('swarm') || lower.includes('topology') || lower.includes('graph') || lower.includes('network')) {
      targetTab = 'lattice';
      targetName = 'DAG_TOPOLOGY_MONITOR';
      speakerKnight = 'merlin';
      voiceConfirmation = 'Swarm Lattice topology mapped. Real-time agent nodes monitored.';
    } else if (lower.includes('knight') || lower.includes('roster') || lower.includes('agent') || lower.includes('division') || lower.includes('warden') || lower.includes('scout') || lower.includes('scribe')) {
      targetTab = 'knights';
      targetName = 'KNIGHT_ROSTER_TELEMETRY';
      speakerKnight = 'arthur';
      voiceConfirmation = 'Round Table Knights summoned. Telemetry and division load physicalized.';
    } else if (lower.includes('terminal') || lower.includes('log') || lower.includes('bash') || lower.includes('cli') || lower.includes('exec') || lower.includes('command')) {
      targetTab = 'terminal';
      targetName = 'WASMTIME_IPC_TERMINAL';
      speakerKnight = 'boris';
      voiceConfirmation = 'Terminal active. Direct DAG execution stream opened.';
    } else if (lower.includes('vfs') || lower.includes('file') || lower.includes('explorer') || lower.includes('code') || lower.includes('notebook') || lower.includes('scaffold')) {
      targetTab = 'vfs';
      targetName = 'ISOMORPHIC_VFS_CORE';
      speakerKnight = 'merlin';
      voiceConfirmation = 'VFS Master Scaffold opened. Isomorphic file tree synchronized.';
    } else if (lower.includes('constitution') || lower.includes('rule') || lower.includes('law') || lower.includes('gate') || lower.includes('hitl')) {
      targetTab = 'constitution';
      targetName = 'ANYA_FIRST_LAW_APE';
      speakerKnight = 'anya';
      voiceConfirmation = 'Constitutional Laws verified. Anya First Law and APEE triage asserted.';
    }

    setRoutedTarget(targetName);

    // Audio & Voice Feedback
    setTimeout(() => {
      multiVoiceRouter.speakAsKnight(speakerKnight, voiceConfirmation);
    }, 300);

    // Dynamic Navigation Delay for Cinematic Transition
    setTimeout(() => {
      setIsRouting(false);
      onNavigate(targetTab);
      onKineticTrigger(`//route:${targetTab}`);
    }, 1100);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeRouting(intent);
  };

  const filteredCartridges = CARTRIDGE_DIRECTORY.filter(c => {
    const matchesCategory = selectedCategory === 'all' || c.category === selectedCategory;
    const matchesSearch = searchFilter.trim() === '' || 
      c.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      c.tagline.toLowerCase().includes(searchFilter.toLowerCase()) ||
      c.code.toLowerCase().includes(searchFilter.toLowerCase()) ||
      c.leadKnight.toLowerCase().includes(searchFilter.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div id="arthurian-vsp-gateway" className="relative h-full w-full bg-[#020407] overflow-hidden flex flex-col items-center justify-between font-sans select-none text-neutral-100">
      
      {/* 3D WebGL Canvas Layer: Arthurian Cyber Citadel */}
      <Arthurian3DCanvas />

      {/* Top Telemetry Overlay (Anya Gate Status & Controls) */}
      <header className="relative z-20 w-full px-4 sm:px-6 py-3.5 flex items-center justify-between bg-gradient-to-b from-[#020407]/95 via-[#020407]/60 to-transparent pointer-events-auto">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-[#00E5FF]/10 border border-[#00E5FF]/40 flex items-center justify-center shadow-[0_0_15px_rgba(0,229,255,0.3)]">
            <Compass className="w-5 h-5 text-[#00E5FF] animate-spin" style={{ animationDuration: '24s' }} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold tracking-widest text-[#00E5FF] uppercase">
                VSP GATEWAY vMAX
              </span>
              <span className="px-1.5 py-0.2 bg-[#E5B842]/20 border border-[#E5B842]/50 text-[#E5B842] text-[9px] font-mono font-bold rounded">
                NEUROSYMBOLIC
              </span>
            </div>
            <p className="text-[11px] text-neutral-400 font-mono hidden sm:block">
              Virtual Simulation Protocol // Sovereign Arthurian Matrix
            </p>
          </div>
        </div>

        {/* Action Toggles & Direct Cartridge Navigator Launch */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          <button
            onClick={() => setMenuOpen(true)}
            className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-[#00E5FF]/20 to-[#9D4EDD]/20 hover:from-[#00E5FF]/30 hover:to-[#9D4EDD]/30 border border-[#00E5FF]/60 hover:border-[#00E5FF] text-[#00E5FF] text-xs font-mono font-bold transition-all flex items-center space-x-2 shadow-[0_0_15px_rgba(0,229,255,0.3)] active:scale-95 group"
            title="Open Sovereign Cartridge Navigation Portal"
          >
            <LayoutGrid className="w-4 h-4 text-[#00E5FF] group-hover:scale-110 transition-transform" />
            <span>CARTRIDGE DIRECTORY</span>
            <span className="px-1.5 py-0.2 bg-[#00E5FF] text-black font-extrabold text-[9px] rounded font-mono">
              12
            </span>
          </button>

          <button
            onClick={toggleAmbientAudio}
            className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold transition-all flex items-center space-x-1.5 active:scale-95 ${
              ambientAudioOn
                ? 'bg-[#00E5FF]/20 border-[#00E5FF] text-[#00E5FF] shadow-[0_0_12px_rgba(0,229,255,0.3)]'
                : 'bg-neutral-900/80 border-neutral-800 text-neutral-400 hover:text-neutral-200'
            }`}
            title="Toggle Cybernetic Atmospheric Audio"
          >
            {ambientAudioOn ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
            <span className="hidden md:inline">Audio Lattice</span>
          </button>

          <button
            onClick={() => onNavigate('command-center')}
            className="px-3.5 py-1.5 bg-neutral-900/90 hover:bg-neutral-800 border border-neutral-700/80 hover:border-[#00E5FF]/50 text-neutral-200 rounded-lg text-xs font-mono font-semibold transition-all flex items-center space-x-1.5 active:scale-95 shadow-sm"
            title="Switch to full developer HUD"
          >
            <Layers className="w-3.5 h-3.5 text-[#00E5FF]" />
            <span className="hidden sm:inline">Developer Deck</span>
            <ArrowRight className="w-3 h-3 text-neutral-400" />
          </button>
        </div>
      </header>

      {/* Central Celestial Heraldry Title: KNIGHTS OF THE ROUND */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center mt-1 pointer-events-none px-4 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          className="relative flex flex-col items-center justify-center py-2"
        >
          {/* Top Arc Coordinates & Star Compass */}
          <div className="flex items-center space-x-3 mb-1">
            <div className="h-[1px] w-12 sm:w-28 bg-gradient-to-r from-transparent via-[#00E5FF]/60 to-[#00E5FF]"></div>
            <div className="flex items-center space-x-1.5 text-[10px] sm:text-xs font-mono tracking-[0.3em] text-[#00E5FF]/90 uppercase">
              <Sparkles className="w-3 h-3 text-[#E5B842] animate-pulse" />
              <span>SOVEREIGN WASM MATRIX</span>
              <Sparkles className="w-3 h-3 text-[#E5B842] animate-pulse" />
            </div>
            <div className="h-[1px] w-12 sm:w-28 bg-gradient-to-l from-transparent via-[#00E5FF]/60 to-[#00E5FF]"></div>
          </div>

          {/* Majestic Metallic Serif Typography: KNIGHTS OF THE ROUND */}
          <div className="relative my-0.5">
            {/* Celestial Compass SVG Circular Overlay */}
            <svg
              className="absolute -top-10 left-1/2 -translate-x-1/2 w-[340px] sm:w-[520px] md:w-[680px] h-[210px] pointer-events-none opacity-40"
              viewBox="0 0 700 240"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <ellipse cx="350" cy="120" rx="320" ry="90" stroke="#00E5FF" strokeWidth="1" strokeDasharray="4 6" />
              <ellipse cx="350" cy="120" rx="280" ry="75" stroke="#E5B842" strokeWidth="0.8" />
              <ellipse cx="350" cy="120" rx="240" ry="60" stroke="#9D4EDD" strokeWidth="0.6" strokeDasharray="2 4" />
              <line x1="350" y1="20" x2="350" y2="40" stroke="#00E5FF" strokeWidth="2" />
              <line x1="350" y1="200" x2="350" y2="220" stroke="#00E5FF" strokeWidth="2" />
              <line x1="20" y1="120" x2="40" y2="120" stroke="#00E5FF" strokeWidth="2" />
              <line x1="660" y1="120" x2="680" y2="120" stroke="#00E5FF" strokeWidth="2" />
            </svg>

            {/* Typography Line 1: KNIGHTS */}
            <h1 className="text-4xl sm:text-6xl md:text-8xl lg:text-9xl font-serif font-extrabold tracking-[0.18em] uppercase text-transparent bg-clip-text bg-gradient-to-b from-[#ffffff] via-[#e2e8f0] to-[#64748b] drop-shadow-[0_4px_25px_rgba(0,229,255,0.45)] leading-tight m-0">
              KNIGHTS
            </h1>

            {/* Typography Line 2: OF */}
            <div className="flex items-center justify-center gap-4 my-0.5">
              <div className="h-[1px] w-16 sm:w-28 bg-gradient-to-r from-transparent via-[#00E5FF] to-white"></div>
              <span className="text-base sm:text-2xl md:text-3xl font-serif font-bold tracking-[0.4em] text-[#00E5FF] drop-shadow-[0_0_12px_rgba(0,229,255,0.8)]">
                OF
              </span>
              <div className="h-[1px] w-16 sm:w-28 bg-gradient-to-l from-transparent via-[#00E5FF] to-white"></div>
            </div>

            {/* Typography Line 3: THE ROUND */}
            <h1 className="text-4xl sm:text-6xl md:text-8xl lg:text-9xl font-serif font-extrabold tracking-[0.18em] uppercase text-transparent bg-clip-text bg-gradient-to-b from-[#ffffff] via-[#e2e8f0] to-[#64748b] drop-shadow-[0_4px_25px_rgba(0,229,255,0.45)] leading-tight m-0">
              THE ROUND
            </h1>
          </div>

          {/* Subtitle Badge */}
          <div className="mt-1 flex items-center space-x-2 text-[10px] sm:text-xs font-mono text-neutral-300">
            <span className="text-[#00E5FF] font-bold">ANYA_Ω APEE v7.0</span>
            <span className="text-neutral-600">•</span>
            <span className="text-neutral-400">Zero-UI Neurosymbolic Gateway</span>
            <span className="text-neutral-600">•</span>
            <span className="text-[#E5B842]">LATTICE: V1000 ASCENDED</span>
          </div>
        </motion.div>
      </div>

      {/* Floating Direct Cartridge Launch Dock (Visible on Main Screen) */}
      <div className="relative z-20 w-full max-w-4xl px-4 pointer-events-auto flex flex-col items-center">
        
        {/* Quick Launch Dock Bar with Instant Jump Cartridges */}
        <div className="w-full bg-[#080710]/80 backdrop-blur-xl border border-[#00E5FF]/30 rounded-2xl p-2 sm:p-3 shadow-[0_0_30px_rgba(0,0,0,0.8)] flex flex-col gap-2">
          
          <div className="flex items-center justify-between px-2 pb-1 border-b border-neutral-800/80">
            <div className="flex items-center space-x-2 text-[11px] font-mono text-neutral-300">
              <span className="w-2 h-2 rounded-full bg-[#00E5FF] animate-ping" />
              <span className="font-bold text-[#00E5FF]">ACTIVE CARTRIDGE DOCK</span>
              <span className="text-neutral-500">// Direct Jump Nexus</span>
            </div>
            <button
              onClick={() => setMenuOpen(true)}
              className="text-[11px] font-mono text-[#E5B842] hover:text-white flex items-center space-x-1 transition-colors cursor-pointer"
            >
              <span>View All 12 Cartridges</span>
              <ChevronRight className="w-3 h-3" />
            </button>
          </div>

          {/* Rapid Cartridge Buttons Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-1.5 sm:gap-2">
            {CARTRIDGE_DIRECTORY.slice(0, 6).map((cartridge) => {
              const Icon = cartridge.icon;
              return (
                <button
                  key={cartridge.id}
                  onClick={() => launchCartridgeDirect(cartridge)}
                  disabled={isRouting}
                  className={`p-2 rounded-xl bg-neutral-950/80 hover:bg-neutral-900 border border-neutral-800 ${cartridge.borderHover} transition-all duration-200 flex flex-col items-center text-center group cursor-pointer active:scale-95`}
                  title={`${cartridge.name} (${cartridge.leadKnight})`}
                >
                  <div className={`p-1.5 rounded-lg ${cartridge.bgGlow} mb-1 group-hover:scale-110 transition-transform`}>
                    <Icon className={`w-4 h-4 ${cartridge.color}`} />
                  </div>
                  <span className="text-[11px] font-semibold text-neutral-200 group-hover:text-white truncate w-full">
                    {cartridge.name.split(' ')[0]}
                  </span>
                  <span className="text-[9px] font-mono text-neutral-400 truncate w-full">
                    {cartridge.leadKnight.replace('SIR_', '').replace('_Ω', '')}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Zero-UI Omnibox Search Router (Floating Glassmorphic Pill) */}
      <div className="relative z-20 w-full max-w-3xl px-4 sm:px-6 pb-5 pointer-events-auto flex flex-col items-center">
        
        {/* Dynamic Neurosymbolic Routing Pulse Banner */}
        <AnimatePresence>
          {isRouting && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-2.5 px-5 py-1.5 rounded-full bg-[#00E5FF]/15 border border-[#00E5FF]/50 backdrop-blur-xl flex items-center space-x-3 shadow-[0_0_25px_rgba(0,229,255,0.4)]"
            >
              <Zap className="w-4 h-4 text-[#00E5FF] animate-bounce" />
              <span className="text-xs font-mono font-bold tracking-wider text-[#00E5FF] uppercase">
                POLYGLOT MATRIX ROUTING ➔ {routedTarget || 'DISPATCHING...'}
              </span>
              <div className="w-2.5 h-2.5 rounded-full bg-[#00E5FF] animate-ping" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* The Omnibox Search Pill Form */}
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
          className="w-full"
        >
          <form
            onSubmit={handleFormSubmit}
            className={`relative flex items-center w-full bg-[#0B0914]/90 backdrop-blur-2xl border ${
              isRouting
                ? 'border-[#00E5FF] shadow-[0_0_40px_rgba(0,229,255,0.5)]'
                : 'border-[rgba(0,229,255,0.4)] hover:border-[#00E5FF] shadow-[0_0_30px_rgba(0,229,255,0.2)]'
            } rounded-full p-2 sm:p-2.5 transition-all duration-300`}
          >
            {/* Sovereign Operator Avatar Node (VaShawn / Vizion / Arthurian Crest) */}
            <div
              className="flex-shrink-0 h-11 w-11 sm:h-12 sm:w-12 rounded-full bg-gradient-to-tr from-[#120B24] via-[#2A174E] to-[#45227B] border-2 border-[#E5B842] shadow-[0_0_12px_rgba(229,184,66,0.6)] flex items-center justify-center overflow-hidden cursor-pointer group"
              title="Sovereign Operator Node: VaShawn O. Head (Vizion) - Click to Open Directory"
              onClick={() => setMenuOpen(true)}
            >
              <div className="text-[#E5B842] font-serif font-black text-lg group-hover:scale-110 transition-transform">
                👑
              </div>
            </div>

            {/* Natural Language Prompt Input */}
            <input
              ref={inputRef}
              type="text"
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              disabled={isRouting}
              placeholder={voiceActive ? 'Listening to voice intent...' : "Command the Swarm... (e.g., 'Deploy UI/UX Cartridge', 'Launch Digital Factory')"}
              className="flex-1 bg-transparent border-none outline-none text-white text-sm sm:text-base md:text-lg px-4 sm:px-5 placeholder-neutral-400 font-mono tracking-wide selection:bg-[#00E5FF]/40 selection:text-white"
            />

            {/* Voice Input Trigger */}
            <button
              type="button"
              onClick={toggleVoiceRecording}
              disabled={isRouting}
              className={`flex-shrink-0 h-10 w-10 sm:h-11 sm:w-11 rounded-full flex items-center justify-center transition-all mr-1.5 ${
                voiceActive
                  ? 'bg-rose-500 text-white shadow-[0_0_15px_rgba(244,63,94,0.6)] animate-pulse'
                  : 'bg-neutral-900/80 hover:bg-neutral-800 text-neutral-400 hover:text-[#00E5FF] border border-neutral-700/60'
              }`}
              title="Voice Intent Speech-to-Text"
            >
              <Mic className="w-4 h-4" />
            </button>

            {/* Execute / Neurosymbolic Search Button */}
            <button
              type="submit"
              disabled={isRouting || (!intent.trim() && !voiceActive)}
              className="flex-shrink-0 h-11 w-11 sm:h-12 sm:w-12 rounded-full bg-gradient-to-r from-[#00E5FF] to-[#00B4D8] text-black hover:brightness-110 flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(0,229,255,0.4)] active:scale-95"
              title="Execute Directive via Polyglot Matrix"
            >
              {isRouting ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
                >
                  <Zap className="w-5 h-5 text-black fill-black" />
                </motion.div>
              ) : (
                <Search className="w-5 h-5 text-black stroke-[2.5]" />
              )}
            </button>
          </form>
        </motion.div>

        {/* Quick Action Kinetic Directives */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-2.5 w-full flex items-center justify-center flex-wrap gap-1.5 px-2"
        >
          {PRESET_DIRECTIVES.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => {
                setIntent(preset.query);
                executeRouting(preset.query);
              }}
              disabled={isRouting}
              className={`px-2.5 py-1 rounded-full bg-[#0D0B14]/80 hover:bg-[#1A162B] border ${preset.color} text-[11px] font-mono transition-all hover:scale-105 active:scale-95 shadow-sm whitespace-nowrap`}
            >
              <span>{preset.label}</span>
            </button>
          ))}
        </motion.div>

        {/* System Sovereign Footer Status */}
        <div className="mt-2 flex items-center space-x-3 text-[10px] font-mono text-neutral-500">
          <span className="flex items-center gap-1 text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Edge Node: 8GB Strict [Cleveland, OH]</span>
          </span>
          <span>•</span>
          <span>Zero-UI No-Code Gateway</span>
          <span>•</span>
          <span className="text-[#00E5FF]">Gideon Gate: Active</span>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* Comprehensive Cartridge Navigation Modal / Nexus Flyout Drawer */}
      {/* ========================================================================= */}
      <AnimatePresence>
        {menuOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-8 bg-black/80 backdrop-blur-xl pointer-events-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.94, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.94, y: 20 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="relative w-full max-w-5xl max-h-[90vh] bg-[#070912] border border-[#00E5FF]/40 rounded-3xl shadow-[0_0_60px_rgba(0,229,255,0.25)] flex flex-col overflow-hidden text-neutral-100"
            >
              {/* Modal Header */}
              <div className="px-6 py-5 border-b border-neutral-800 bg-[#0c0f1d] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-[#00E5FF]/10 border border-[#00E5FF]/50 flex items-center justify-center">
                    <LayoutGrid className="w-5 h-5 text-[#00E5FF]" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-lg font-bold font-serif tracking-wider text-white uppercase">
                        Sovereign Cartridge Directory
                      </h2>
                      <span className="px-2 py-0.5 rounded bg-[#00E5FF]/20 border border-[#00E5FF]/40 text-[#00E5FF] text-[10px] font-mono font-bold">
                        12 MODULAR WASM CARTRIDGES
                      </span>
                    </div>
                    <p className="text-xs font-mono text-neutral-400">
                      Direct single-click dispatch to any Camelot-OS subsystem
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {/* Search Bar in Modal */}
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder="Filter cartridges..."
                      value={searchFilter}
                      onChange={(e) => setSearchFilter(e.target.value)}
                      className="bg-neutral-900/90 border border-neutral-700/80 focus:border-[#00E5FF] rounded-xl pl-8 pr-3 py-1.5 text-xs font-mono text-white outline-none w-48 sm:w-60"
                    />
                  </div>

                  <button
                    onClick={() => setMenuOpen(false)}
                    className="p-2 rounded-xl bg-neutral-800/80 hover:bg-neutral-700 text-neutral-400 hover:text-white transition-colors cursor-pointer"
                  >
                    ✕
                  </button>
                </div>
              </div>

              {/* Category Filter Pills */}
              <div className="px-6 py-3 bg-[#0a0d18] border-b border-neutral-800/80 flex items-center space-x-2 overflow-x-auto">
                <Filter className="w-3.5 h-3.5 text-neutral-500 flex-shrink-0" />
                {[
                  { id: 'all', label: 'All Cartridges (12)' },
                  { id: 'core', label: 'Core Engines & Pipelines (3)' },
                  { id: 'intelligence', label: 'Intelligence & Spatial (3)' },
                  { id: 'governance', label: 'Governance & Security (3)' },
                  { id: 'dev', label: 'Developer Subsystems (3)' }
                ].map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id as any)}
                    className={`px-3 py-1 rounded-lg text-xs font-mono font-medium transition-all whitespace-nowrap cursor-pointer ${
                      selectedCategory === cat.id
                        ? 'bg-[#00E5FF] text-black font-bold shadow-[0_0_12px_rgba(0,229,255,0.4)]'
                        : 'bg-neutral-900/80 text-neutral-400 hover:text-white hover:bg-neutral-800 border border-neutral-800'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              {/* Cartridge Grid */}
              <div className="p-6 overflow-y-auto max-h-[60vh] grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredCartridges.map((cartridge) => {
                  const Icon = cartridge.icon;
                  return (
                    <div
                      key={cartridge.id}
                      onClick={() => launchCartridgeDirect(cartridge)}
                      className={`p-4 rounded-2xl bg-[#0d1020]/90 border border-neutral-800 ${cartridge.borderHover} transition-all duration-300 flex flex-col justify-between cursor-pointer group hover:-translate-y-1 shadow-lg`}
                    >
                      <div>
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className={`w-10 h-10 rounded-xl ${cartridge.bgGlow} border border-neutral-700/60 flex items-center justify-center group-hover:scale-110 transition-transform`}>
                              <Icon className={`w-5 h-5 ${cartridge.color}`} />
                            </div>
                            <div>
                              <h3 className="text-sm font-bold text-white group-hover:text-[#00E5FF] transition-colors">
                                {cartridge.name}
                              </h3>
                              <span className="text-[10px] font-mono text-neutral-400 block">
                                Lead: <span className="text-neutral-200">{cartridge.leadKnight}</span>
                              </span>
                            </div>
                          </div>

                          <span className="px-1.5 py-0.5 rounded bg-neutral-900 border border-neutral-700 text-[9px] font-mono text-neutral-300">
                            {cartridge.latency}
                          </span>
                        </div>

                        <p className="text-xs text-neutral-300 font-sans line-clamp-2 mb-3">
                          {cartridge.tagline}
                        </p>
                      </div>

                      <div className="pt-3 border-t border-neutral-800/80 flex items-center justify-between text-[10px] font-mono">
                        <span className="text-neutral-500 uppercase tracking-wider">
                          {cartridge.division.split('&')[0]}
                        </span>
                        <div className="flex items-center space-x-1 text-[#00E5FF] font-semibold group-hover:translate-x-1 transition-transform">
                          <span>LAUNCH</span>
                          <ArrowRight className="w-3 h-3" />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Modal Footer */}
              <div className="px-6 py-4 bg-[#090b14] border-t border-neutral-800 flex items-center justify-between text-xs font-mono text-neutral-400">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Sovereign Wasmtime Runtime • Multi-Tenant RLS • Zero External Calls</span>
                </div>
                <button
                  onClick={() => setMenuOpen(false)}
                  className="px-4 py-1.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-semibold transition-colors cursor-pointer"
                >
                  Close Portal
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
