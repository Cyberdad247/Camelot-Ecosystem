import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Shield, 
  Terminal, 
  Cpu, 
  Activity, 
  Layers, 
  Zap, 
  Eye, 
  Play, 
  RefreshCw, 
  Sparkles, 
  AlertTriangle, 
  Send, 
  Sliders, 
  Box, 
  Maximize2, 
  Minimize2,
  Compass,
  Flame,
  CheckCircle2,
  Copy,
  Check,
  Radio,
  User,
  Orbit,
  CpuIcon,
  ChevronRight,
  TrendingUp,
  BarChart3
} from 'lucide-react';
import { KNIGHTS_ROSTER } from '../data/knightsData';
import { Knight, ThemeMode } from '../types';

// ==========================================
// A2UI & COPILOTKIT DECLARATIVE TYPES
// ==========================================

export interface A2UIPayload {
  version: string;
  targetComponent: string;
  layout: 'single-card' | 'split-hud' | 'bento-matrix';
  theme: {
    primary: string;
    accent: string;
    surface: string;
  };
  state: {
    systemState: string;
    node: string;
    lattice: string;
    chaosLevel: number;
    fuzzRate: number;
    memoryAllocatedMb: number;
    activeAgents: number;
    verdict: string;
  };
  cards: Array<{
    id: string;
    title: string;
    type: 'metric' | 'log' | 'mutation' | 'directive';
    content: string;
    badge?: string;
  }>;
}

interface SpatialHolographicHUDProps {
  onKineticTrigger: (trigger: string) => void;
  theme?: ThemeMode;
}

export const SpatialHolographicHUD: React.FC<SpatialHolographicHUDProps> = ({
  onKineticTrigger,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  // Container & Canvas Refs
  const canvasContainerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // System & CopilotKit State
  const [systemState, setSystemState] = useState<string>("AWAITING_DIRECTIVE");
  const [chaosLevel, setChaosLevel] = useState<number>(32);
  const [isInjectingFault, setIsInjectingFault] = useState<boolean>(false);
  const [activeAvatarMode, setActiveAvatarMode] = useState<'ANYA_Ω' | 'SIR_BORIS' | 'QUANTUM_CORE'>('ANYA_Ω');
  const [selectedKnight, setSelectedKnight] = useState<Knight | null>(() => {
    return KNIGHTS_ROSTER.find(k => k.id === 'k-anya') || KNIGHTS_ROSTER[0];
  });
  const [cameraMode, setCameraMode] = useState<'perspective' | 'front_avatar' | 'top'>('perspective');
  const [copiedCode, setCopiedCode] = useState(false);
  const [copilotInput, setCopilotInput] = useState('');
  
  const [copilotMessages, setCopilotMessages] = useState<Array<{ sender: 'OPERATOR' | 'ANYA_Ω' | 'SIR_BORIS' | 'COPILOT_AGENT'; text: string; time: string; actionPayload?: any }>>([
    {
      sender: 'ANYA_Ω',
      text: 'Volumetric Emitter Online. Holographic avatar projection synchronized on Cleveland Edge Node.',
      time: '02:24:10',
      actionPayload: { node: 'CYBERTRONIA_MASTER', lattice: 'SECURE', status: 'AWAITING_DIRECTIVE' }
    }
  ]);

  // A2UI Declarative Cartridge Payload
  const [a2uiPayload, setA2uiPayload] = useState<A2UIPayload>({
    version: 'A2UI/v1000.OMEGA',
    targetComponent: 'HolographicCommandCenter',
    layout: 'bento-matrix',
    theme: {
      primary: '#00E5FF',
      accent: '#9D4EDD',
      surface: isDark ? '#050507' : '#ffffff'
    },
    state: {
      systemState: 'AWAITING_DIRECTIVE',
      node: 'CYBERTRONIA_MASTER',
      lattice: 'SECURE',
      chaosLevel: 32,
      fuzzRate: 1420,
      memoryAllocatedMb: 248.6,
      activeAgents: 25,
      verdict: 'CONVERGED'
    },
    cards: [
      {
        id: 'c1',
        title: 'Volumetric Emitter',
        type: 'metric',
        content: 'Concentric Ring Pedestal projection active at 60 FPS WebGPU substrate.',
        badge: 'EMITTER_ACTIVE'
      },
      {
        id: 'c2',
        title: 'Lattice Security',
        type: 'directive',
        content: 'Kyber-768 quantum safe mTLS enclave linked to Cleveland anchor.',
        badge: 'ZERO_DRIFT'
      },
      {
        id: 'c3',
        title: 'Sir Boris Vanguard',
        type: 'mutation',
        content: 'Jitter damping active under 8GB strict scarcity ceiling.',
        badge: 'ACTIVE_GUARD'
      }
    ]
  });

  // State synchronization refs for 60fps WebGL loop
  const chaosLevelRef = useRef(chaosLevel);
  chaosLevelRef.current = chaosLevel;
  const isInjectingFaultRef = useRef(isInjectingFault);
  isInjectingFaultRef.current = isInjectingFault;
  const selectedKnightRef = useRef(selectedKnight);
  selectedKnightRef.current = selectedKnight;
  const avatarModeRef = useRef(activeAvatarMode);
  avatarModeRef.current = activeAvatarMode;

  // Scene references
  const sceneRef = useRef<{
    scene: THREE.Scene;
    renderer: THREE.WebGLRenderer;
    camera: THREE.PerspectiveCamera;
    controls: OrbitControls;
    knightMeshes: Array<{ mesh: THREE.Mesh; knight: Knight }>;
  } | null>(null);

  // Update theme dynamically in Three.js scene
  useEffect(() => {
    if (!sceneRef.current) return;
    const { scene } = sceneRef.current;
    scene.background = new THREE.Color(isDark ? '#050507' : '#f1f5f9');
    scene.fog = new THREE.FogExp2(isDark ? '#050507' : '#f1f5f9', 0.038);
  }, [isDark]);

  // Initialize Three.js Hardware Accelerated Substrate
  useEffect(() => {
    const container = canvasContainerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    let width = container.clientWidth || 1024;
    let height = container.clientHeight || 768;

    // 1. Scene & Atmosphere
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(isDark ? '#050507' : '#f1f5f9');
    scene.fog = new THREE.FogExp2(isDark ? '#050507' : '#f1f5f9', 0.038);

    // 2. Camera Setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 1.8, 6.8);

    // 3. High Performance WebGL Renderer
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // 4. Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxDistance = 14;
    controls.minDistance = 2.5;
    controls.maxPolarAngle = Math.PI / 2 + 0.05;
    controls.target.set(0, 1.2, 0);

    // 5. Holographic Stage Lighting
    const ambientLight = new THREE.AmbientLight('#ffffff', 0.6);
    scene.add(ambientLight);

    const cyanSpot = new THREE.PointLight('#00E5FF', 3, 20);
    cyanSpot.position.set(0, 0.2, 0);
    scene.add(cyanSpot);

    const violetTop = new THREE.PointLight('#9D4EDD', 2.8, 25);
    violetTop.position.set(0, 6, 0);
    scene.add(violetTop);

    const sideRim = new THREE.PointLight('#FF007F', 2, 20);
    sideRim.position.set(4, 2, -3);
    scene.add(sideRim);

    // 6. Perspective Cyberpunk Floor Grid
    const gridGroup = new THREE.Group();
    gridGroup.position.set(0, -0.6, 0);

    const primaryGrid = new THREE.GridHelper(36, 36, '#00E5FF', '#0e1c2a');
    gridGroup.add(primaryGrid);

    const secondaryGrid = new THREE.GridHelper(72, 72, '#9D4EDD', '#080512');
    secondaryGrid.position.set(0, -0.01, 0);
    gridGroup.add(secondaryGrid);

    scene.add(gridGroup);

    // 7. Volumetric Emitter Pedestal (Concentric Rings Base)
    const pedestalGroup = new THREE.Group();
    pedestalGroup.position.set(0, -0.58, 0);

    // Solid pedestal disk
    const discGeo = new THREE.CylinderGeometry(2.2, 2.3, 0.08, 64);
    const discMat = new THREE.MeshStandardMaterial({
      color: '#0A0710',
      metalness: 0.9,
      roughness: 0.2
    });
    const discMesh = new THREE.Mesh(discGeo, discMat);
    pedestalGroup.add(discMesh);

    // Concentric glowing projector rings on floor
    const ringRadii = [0.8, 1.3, 1.8, 2.2];
    const ringColors = ['#00E5FF', '#9D4EDD', '#00E5FF', '#E5B842'];
    const emitterRings: THREE.Mesh[] = [];

    ringRadii.forEach((r, idx) => {
      const ringGeo = new THREE.RingGeometry(r - 0.03, r, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: ringColors[idx],
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85
      });
      const rMesh = new THREE.Mesh(ringGeo, ringMat);
      rMesh.rotation.x = -Math.PI / 2;
      rMesh.position.y = 0.045;
      pedestalGroup.add(rMesh);
      emitterRings.push(rMesh);
    });

    // Holographic Cylinder Light Column
    const cylinderGeo = new THREE.CylinderGeometry(2.1, 2.1, 4.5, 32, 1, true);
    const cylinderMat = new THREE.MeshBasicMaterial({
      color: '#00E5FF',
      transparent: true,
      opacity: 0.07,
      side: THREE.DoubleSide,
      wireframe: true
    });
    const lightColumn = new THREE.Mesh(cylinderGeo, cylinderMat);
    lightColumn.position.y = 2.2;
    pedestalGroup.add(lightColumn);

    scene.add(pedestalGroup);

    // 8. Holographic Avatar Model (Constructed Wireframe Anatomical Mesh)
    const avatarGroup = new THREE.Group();
    avatarGroup.position.set(0, 0, 0);

    // Head
    const headGeo = new THREE.SphereGeometry(0.3, 24, 24);
    const headMat = new THREE.MeshStandardMaterial({
      color: '#00E5FF',
      emissive: '#00E5FF',
      emissiveIntensity: 1.2,
      wireframe: true,
      transparent: true,
      opacity: 0.9
    });
    const headMesh = new THREE.Mesh(headGeo, headMat);
    headMesh.position.set(0, 2.5, 0);
    avatarGroup.add(headMesh);

    // Neck & Torso
    const torsoGeo = new THREE.CylinderGeometry(0.28, 0.22, 0.85, 16);
    const torsoMat = new THREE.MeshStandardMaterial({
      color: '#00E5FF',
      emissive: '#9D4EDD',
      emissiveIntensity: 0.9,
      wireframe: true,
      transparent: true,
      opacity: 0.85
    });
    const torsoMesh = new THREE.Mesh(torsoGeo, torsoMat);
    torsoMesh.position.set(0, 1.8, 0);
    avatarGroup.add(torsoMesh);

    // Chest Core Reactor (Heart Node)
    const coreReactorGeo = new THREE.OctahedronGeometry(0.12, 0);
    const coreReactorMat = new THREE.MeshBasicMaterial({
      color: '#FFFFFF'
    });
    const coreReactor = new THREE.Mesh(coreReactorGeo, coreReactorMat);
    coreReactor.position.set(0, 1.95, 0.15);
    avatarGroup.add(coreReactor);

    // Pelvis
    const pelvisGeo = new THREE.CylinderGeometry(0.23, 0.26, 0.35, 16);
    const pelvisMesh = new THREE.Mesh(pelvisGeo, torsoMat);
    pelvisMesh.position.set(0, 1.25, 0);
    avatarGroup.add(pelvisMesh);

    // Left & Right Arms
    const armGeo = new THREE.CylinderGeometry(0.06, 0.05, 0.9, 8);
    const leftArm = new THREE.Mesh(armGeo, torsoMat);
    leftArm.position.set(-0.45, 1.7, 0);
    leftArm.rotation.z = 0.18;
    avatarGroup.add(leftArm);

    const rightArm = new THREE.Mesh(armGeo, torsoMat);
    rightArm.position.set(0.45, 1.7, 0);
    rightArm.rotation.z = -0.18;
    avatarGroup.add(rightArm);

    // Left & Right Legs
    const legGeo = new THREE.CylinderGeometry(0.09, 0.06, 1.2, 8);
    const leftLeg = new THREE.Mesh(legGeo, torsoMat);
    leftLeg.position.set(-0.2, 0.5, 0);
    avatarGroup.add(leftLeg);

    const rightLeg = new THREE.Mesh(legGeo, torsoMat);
    rightLeg.position.set(0.2, 0.5, 0);
    avatarGroup.add(rightLeg);

    scene.add(avatarGroup);

    // 9. Floating Holographic Concentric Halo Rings (Above and Around Avatar)
    const haloGroup = new THREE.Group();
    haloGroup.position.set(0, 1.8, 0);

    const halo1Geo = new THREE.TorusGeometry(1.6, 0.015, 16, 100);
    const halo1Mat = new THREE.MeshBasicMaterial({ color: '#00E5FF', wireframe: true, opacity: 0.7, transparent: true });
    const halo1 = new THREE.Mesh(halo1Geo, halo1Mat);
    haloGroup.add(halo1);

    const halo2Geo = new THREE.TorusGeometry(2.1, 0.012, 16, 100);
    const halo2Mat = new THREE.MeshBasicMaterial({ color: '#9D4EDD', wireframe: true, opacity: 0.5, transparent: true });
    const halo2 = new THREE.Mesh(halo2Geo, halo2Mat);
    halo2.rotation.x = Math.PI / 2;
    haloGroup.add(halo2);

    const halo3Geo = new THREE.TorusGeometry(2.6, 0.018, 16, 100);
    const halo3Mat = new THREE.MeshBasicMaterial({ color: '#FF007F', wireframe: true, opacity: 0.4, transparent: true });
    const halo3 = new THREE.Mesh(halo3Geo, halo3Mat);
    haloGroup.add(halo3);

    scene.add(haloGroup);

    // 10. Orbiting Knight Data Nodes
    const featuredKnights = KNIGHTS_ROSTER.slice(0, 10);
    const knightsOrbitGroup = new THREE.Group();
    knightsOrbitGroup.position.set(0, 1.8, 0);

    const knightMeshes: Array<{ mesh: THREE.Mesh; knight: Knight }> = [];

    featuredKnights.forEach((k, idx) => {
      const angle = (idx / featuredKnights.length) * Math.PI * 2;
      const radius = 3.6;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = Math.sin(idx * 2) * 0.4;
      const isBoris = k.id === 'k-boris';
      const isAnya = k.id === 'k-anya';

      const octGeo = new THREE.OctahedronGeometry(0.22, 0);
      const octMat = new THREE.MeshStandardMaterial({
        color: isBoris ? '#FF007F' : isAnya ? '#E5B842' : '#00E5FF',
        emissive: isBoris ? '#FF007F' : isAnya ? '#E5B842' : '#9D4EDD',
        emissiveIntensity: 1.8,
        wireframe: false
      });
      const nodeMesh = new THREE.Mesh(octGeo, octMat);
      nodeMesh.position.set(x, y, z);
      nodeMesh.userData = { knightId: k.id };
      knightsOrbitGroup.add(nodeMesh);
      knightMeshes.push({ mesh: nodeMesh, knight: k });

      // Connector beam to avatar core
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(x, y, z)
      ]);
      const lineMat = new THREE.LineBasicMaterial({
        color: isBoris ? '#FF007F' : '#00E5FF',
        transparent: true,
        opacity: 0.2
      });
      const beam = new THREE.Line(lineGeo, lineMat);
      knightsOrbitGroup.add(beam);
    });

    scene.add(knightsOrbitGroup);

    // 11. Particle Atmosphere Matrix
    const particleCount = 200;
    const particleGeo = new THREE.BufferGeometry();
    const particleCoords = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      particleCoords[i] = (Math.random() - 0.5) * 25;
      particleCoords[i + 1] = Math.random() * 12 - 1;
      particleCoords[i + 2] = (Math.random() - 0.5) * 25;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particleCoords, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 0.06,
      color: '#00E5FF',
      transparent: true,
      opacity: 0.75
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    sceneRef.current = { scene, renderer, camera, controls, knightMeshes };

    // 12. Interactive Raycasting on Click
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleClick = (event: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(knightMeshes.map(km => km.mesh));

      if (intersects.length > 0) {
        const hitMesh = intersects[0].object as THREE.Mesh;
        const target = knightMeshes.find(km => km.mesh === hitMesh);
        if (target) {
          setSelectedKnight(target.knight);
          setSystemState(`NODE_ENGAGED: ${target.knight.name.toUpperCase()}`);
        }
      }
    };

    canvas.addEventListener('click', handleClick);

    // 13. Window / Container Resize Observer
    const resizeObserver = new ResizeObserver(() => {
      if (!container || !renderer || !camera) return;
      const newWidth = container.clientWidth || 1024;
      const newHeight = container.clientHeight || 768;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    });
    resizeObserver.observe(container);

    // 14. 60 FPS Render Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();
      const currentChaos = chaosLevelRef.current;
      const isFault = isInjectingFaultRef.current;
      const speed = 1 + (currentChaos / 40);

      // Floor grid motion
      primaryGrid.position.z = (elapsedTime * 0.7) % 2;

      // Halo Rings Rotation (Matching User Style Guide)
      haloGroup.rotation.y += 0.008 * speed;
      haloGroup.rotation.x = Math.sin(elapsedTime * 0.5) * 0.08;

      halo1.rotation.z = elapsedTime * 0.3 * speed;
      halo2.rotation.y = -elapsedTime * 0.4 * speed;
      halo3.rotation.x = elapsedTime * 0.25 * speed;

      // Pedestal rings pulsing
      emitterRings.forEach((r, idx) => {
        const scale = 1 + Math.sin(elapsedTime * 2 + idx) * 0.02;
        r.scale.set(scale, scale, 1);
      });

      // Light column shimmer
      lightColumn.rotation.y = -elapsedTime * 0.15;
      cylinderMat.opacity = 0.05 + Math.sin(elapsedTime * 3) * 0.03;

      // Avatar Breathing & Floating Motion
      avatarGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.06;
      headMesh.rotation.y = Math.sin(elapsedTime * 0.8) * 0.15;
      coreReactor.rotation.y = elapsedTime * 2;
      coreReactor.rotation.z = elapsedTime * 1.5;

      // Orbiting Knights Group
      knightsOrbitGroup.rotation.y = elapsedTime * 0.14;
      particles.rotation.y = elapsedTime * 0.015;

      // Chaos Injection Feedback
      if (isFault) {
        headMat.color.set('#FF007F');
        headMat.emissive.set('#FF007F');
        torsoMat.color.set('#FF007F');
        torsoMat.emissive.set('#FF007F');
      } else {
        headMat.color.set('#00E5FF');
        headMat.emissive.set(currentChaos > 60 ? '#FF007F' : '#00E5FF');
        torsoMat.color.set('#00E5FF');
        torsoMat.emissive.set(currentChaos > 60 ? '#FF007F' : '#9D4EDD');
      }

      // Highlight Selected Knight Mesh
      const curSelected = selectedKnightRef.current;
      knightMeshes.forEach(km => {
        const isSel = curSelected && curSelected.id === km.knight.id;
        const isB = km.knight.id === 'k-boris';
        const isA = km.knight.id === 'k-anya';
        const mat = km.mesh.material as THREE.MeshStandardMaterial;

        if (isSel) {
          km.mesh.scale.set(1.4, 1.4, 1.4);
          mat.color.set('#E5B842');
          mat.emissive.set('#E5B842');
          mat.emissiveIntensity = 3;
        } else if (isB) {
          km.mesh.scale.set(1.1, 1.1, 1.1);
          mat.color.set('#FF007F');
          mat.emissive.set('#FF007F');
          mat.emissiveIntensity = 2;
        } else if (isA) {
          km.mesh.scale.set(1.15, 1.15, 1.15);
          mat.color.set('#00E5FF');
          mat.emissive.set('#00E5FF');
          mat.emissiveIntensity = 2.2;
        } else {
          km.mesh.scale.set(1, 1, 1);
          mat.color.set('#00E5FF');
          mat.emissive.set('#9D4EDD');
          mat.emissiveIntensity = 1.2;
        }
      });

      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      canvas.removeEventListener('click', handleClick);
      renderer.dispose();
    };
  }, []);

  // Camera Switcher
  const switchCameraMode = (mode: 'perspective' | 'front_avatar' | 'top') => {
    setCameraMode(mode);
    if (!sceneRef.current) return;
    const { camera, controls } = sceneRef.current;

    if (mode === 'front_avatar') {
      camera.position.set(0, 1.8, 4.2);
      controls.target.set(0, 1.6, 0);
    } else if (mode === 'top') {
      camera.position.set(0, 9.5, 0.01);
      controls.target.set(0, 0, 0);
    } else {
      camera.position.set(0, 1.8, 6.8);
      controls.target.set(0, 1.2, 0);
    }
  };

  // CopilotKit Action / Update Telemetry Handler
  const handleUpdateTelemetry = (statusText: string) => {
    setSystemState(statusText);
    setA2uiPayload(prev => ({
      ...prev,
      state: {
        ...prev.state,
        systemState: statusText
      }
    }));
  };

  // Trigger Fault Injection
  const handleTriggerChaos = () => {
    setIsInjectingFault(true);
    setChaosLevel(prev => Math.min(prev + 25, 95));
    handleUpdateTelemetry("FAULT_INJECTION_ACTIVE");

    const borisLog = {
      sender: 'SIR_BORIS' as const,
      text: `[CHAOS INJECTION] Synthetic AST divergence + 50ms latency spike injected into node [${selectedKnight?.name || 'ANYA'}]. Asserting self-healing recovery...`,
      time: new Date().toLocaleTimeString(),
      actionPayload: {
        action: 'FAULT_INJECTED',
        target: selectedKnight?.name,
        chaosDelta: '+25%',
        autoRecovery: 'SIR_SYNTAX_ENGAGED'
      }
    };
    setCopilotMessages(prev => [...prev, borisLog]);

    setTimeout(() => {
      setIsInjectingFault(false);
      handleUpdateTelemetry("RESILIENT_CONVERGED");
      setA2uiPayload(prev => ({
        ...prev,
        state: {
          ...prev.state,
          chaosLevel: Math.min(prev.state.chaosLevel + 25, 95),
          fuzzRate: prev.state.fuzzRate + 450,
          verdict: 'SELF_HEALED'
        }
      }));
    }, 1800);
  };

  // Rezero / Reset
  const handleRezero = () => {
    setChaosLevel(20);
    setIsInjectingFault(false);
    handleUpdateTelemetry("SYSTEM_CONVERGED");
    setCopilotMessages(prev => [
      ...prev,
      {
        sender: 'ANYA_Ω',
        text: 'Topological noise rezeroed. Volumetric emitter calibrated at baseline 60 FPS.',
        time: new Date().toLocaleTimeString(),
        actionPayload: { action: 'REZERO_ALL', status: 'CONVERGED' }
      }
    ]);
  };

  // Copilot Agent Prompt Dispatch
  const handleSendCopilot = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!copilotInput.trim()) return;

    const userText = copilotInput.trim();
    setCopilotInput('');

    setCopilotMessages(prev => [
      ...prev,
      {
        sender: 'OPERATOR',
        text: userText,
        time: new Date().toLocaleTimeString()
      }
    ]);

    setTimeout(() => {
      let responseText = `Copilot agent processed directive: "${userText}". Shared state updated across spatial HUD.`;
      if (userText.toLowerCase().includes('boris') || userText.toLowerCase().includes('chaos')) {
        responseText = `Sir Boris executed chaos stress-test across 25 knights. Fuzz rate nominal.`;
        handleTriggerChaos();
      } else if (userText.toLowerCase().includes('boot') || userText.toLowerCase().includes('live')) {
        handleUpdateTelemetry("SOVEREIGN_LIVE");
        onKineticTrigger('//boot');
      } else {
        handleUpdateTelemetry(`EXECUTING: ${userText.toUpperCase().slice(0, 18)}`);
      }

      setCopilotMessages(prev => [
        ...prev,
        {
          sender: 'COPILOT_AGENT',
          text: responseText,
          time: new Date().toLocaleTimeString(),
          actionPayload: {
            directive: userText,
            status: 'EXECUTED',
            agent: 'Anya_Ω & Merlin_Ω'
          }
        }
      ]);
    }, 500);
  };

  const copyA2UIPayload = () => {
    navigator.clipboard.writeText(JSON.stringify(a2uiPayload, null, 2));
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className={`relative w-full h-full min-h-[88vh] ${isDark ? 'bg-[#050507] text-white selection:bg-[#00E5FF] selection:text-black' : 'bg-slate-100 text-slate-900 selection:bg-cyan-500 selection:text-white'} overflow-hidden font-mono flex flex-col transition-colors duration-200`}>
      
      {/* LAYER 1: 3D HARDWARE ACCELERATED WEBGPU / THREE.JS CANVAS */}
      <div 
        ref={canvasContainerRef}
        className="absolute inset-0 z-0 opacity-90 cursor-grab active:cursor-grabbing"
      >
        <canvas
          ref={canvasRef}
          className="w-full h-full block"
        />
      </div>

      {/* LAYER 2: 12-COLUMN GLASSMORPHIC HUD OVERLAY (Matching User Style Guide) */}
      <main className="relative z-10 grid grid-cols-12 gap-4 lg:gap-6 p-4 lg:p-6 flex-1 pointer-events-none overflow-y-auto lg:overflow-hidden">
        
        {/* LEFT TELEMETRY PANEL (Cols: 1-3) */}
        <motion.aside 
          initial={{ x: -40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className={`col-span-12 lg:col-span-3 border ${isDark ? 'border-[#00E5FF]/30 bg-[#050507]/70 text-white shadow-[0_0_15px_rgba(0,229,255,0.1)]' : 'border-cyan-600/40 bg-white/90 text-slate-900 shadow-xl'} backdrop-blur-md p-4 lg:p-5 pointer-events-auto rounded-none flex flex-col justify-between transition-colors`}
        >
          <div>
            {/* Header branding */}
            <div className={`flex items-center justify-between border-b ${isDark ? 'border-[#00E5FF]/20' : 'border-cyan-600/20'} pb-2 mb-4`}>
              <h2 className={`${isDark ? 'text-[#00E5FF]' : 'text-cyan-700'} text-xs uppercase tracking-[0.3em] font-bold flex items-center gap-1.5`}>
                <span className={`w-2 h-2 rounded-full ${isDark ? 'bg-[#00E5FF]' : 'bg-cyan-600'} animate-ping inline-block`} />
                System Telemetry
              </h2>
              <span className={`text-[9px] px-1.5 py-0.5 ${isDark ? 'bg-[#00E5FF]/10 text-[#00E5FF] border-[#00E5FF]/30' : 'bg-cyan-100 text-cyan-800 border-cyan-300'} border font-semibold`}>
                EDGE: CLE
              </span>
            </div>

            {/* Telemetry Metrics List */}
            <div className={`flex flex-col gap-3 text-[11px] tracking-wider ${isDark ? 'text-gray-400' : 'text-slate-600'}`}>
              <div className={`flex justify-between items-center py-1 border-b ${isDark ? 'border-white/5' : 'border-slate-200'}`}>
                <span className={isDark ? 'text-neutral-400' : 'text-slate-500'}>NODE:</span>
                <span className={`${isDark ? 'text-white' : 'text-slate-950'} font-bold tracking-widest`}>CYBERTRONIA_MASTER</span>
              </div>
              <div className={`flex justify-between items-center py-1 border-b ${isDark ? 'border-white/5' : 'border-slate-200'}`}>
                <span className={isDark ? 'text-neutral-400' : 'text-slate-500'}>STATUS:</span>
                <span className={`${isDark ? 'text-[#E5B842] bg-[#E5B842]/10 border-[#E5B842]/30' : 'text-amber-800 bg-amber-100 border-amber-300'} font-bold px-1.5 py-0.5 border text-[10px]`}>
                  {systemState}
                </span>
              </div>
              <div className={`flex justify-between items-center py-1 border-b ${isDark ? 'border-white/5' : 'border-slate-200'}`}>
                <span className={isDark ? 'text-neutral-400' : 'text-slate-500'}>LATTICE:</span>
                <span className={`${isDark ? 'text-[#9D4EDD]' : 'text-purple-700'} font-bold`}>SECURE (24D LEECH)</span>
              </div>
              <div className={`flex justify-between items-center py-1 border-b ${isDark ? 'border-white/5' : 'border-slate-200'}`}>
                <span className={isDark ? 'text-neutral-400' : 'text-slate-500'}>CHAOS STRESS:</span>
                <span className={`font-bold ${chaosLevel > 60 ? (isDark ? 'text-[#FF007F]' : 'text-rose-600') : (isDark ? 'text-[#00E5FF]' : 'text-cyan-700')}`}>
                  {chaosLevel}%
                </span>
              </div>
              <div className={`flex justify-between items-center py-1 border-b ${isDark ? 'border-white/5' : 'border-slate-200'}`}>
                <span className={isDark ? 'text-neutral-400' : 'text-slate-500'}>RECOVERY MTBF:</span>
                <span className={`${isDark ? 'text-emerald-400' : 'text-emerald-700'} font-bold`}>99.999%</span>
              </div>
              <div className={`flex justify-between items-center py-1 border-b ${isDark ? 'border-white/5' : 'border-slate-200'}`}>
                <span className={isDark ? 'text-neutral-400' : 'text-slate-500'}>MEMORY CEILING:</span>
                <span className={`${isDark ? 'text-white' : 'text-slate-950'} font-semibold`}>{a2uiPayload.state.memoryAllocatedMb} MB / 8GB</span>
              </div>
            </div>

            {/* Selected Node Card */}
            {selectedKnight && (
              <div className={`mt-4 p-3 ${isDark ? 'bg-[#0A0710] border-[#00E5FF]/20' : 'bg-slate-50 border-cyan-300'} border text-[10px]`}>
                <div className={`${isDark ? 'text-[#00E5FF]' : 'text-cyan-700'} font-bold uppercase mb-1 flex items-center justify-between`}>
                  <span>Selected Node</span>
                  <span className={isDark ? 'text-amber-400' : 'text-amber-700'}>{selectedKnight.division}</span>
                </div>
                <div className={`${isDark ? 'text-white' : 'text-slate-950'} font-semibold text-xs`}>{selectedKnight.name}</div>
                <div className={`${isDark ? 'text-neutral-400' : 'text-slate-600'} text-[10px] mt-0.5`}>{selectedKnight.role}</div>
                <div className="mt-2 flex items-center justify-between">
                  <span className={isDark ? 'text-neutral-500' : 'text-slate-500'}>Load: {selectedKnight.load}%</span>
                  <button
                    onClick={() => onKineticTrigger(`//dispatch:${selectedKnight.name.toLowerCase().replace(/[^a-z]/g, '')}`)}
                    className={`px-2 py-0.5 ${isDark ? 'bg-[#00E5FF]/20 hover:bg-[#00E5FF]/30 text-[#00E5FF] border-[#00E5FF]/40' : 'bg-cyan-100 hover:bg-cyan-200 text-cyan-800 border-cyan-300'} border text-[10px] transition-all font-semibold`}
                  >
                    //dispatch
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Quick Action Kinetic Buttons */}
          <div className={`mt-4 pt-3 border-t ${isDark ? 'border-[#00E5FF]/20' : 'border-cyan-600/20'} flex flex-col gap-2`}>
            <div className="flex items-center gap-2">
              <button
                onClick={handleTriggerChaos}
                disabled={isInjectingFault}
                className={`flex-1 py-1.5 ${isDark ? 'bg-[#FF007F]/20 hover:bg-[#FF007F]/30 text-[#FF007F] border-[#FF007F]/40' : 'bg-rose-100 hover:bg-rose-200 text-rose-800 border-rose-300'} border text-[10px] font-bold transition-all flex items-center justify-center gap-1 active:scale-95 disabled:opacity-50`}
              >
                <Flame className="w-3 h-3" />
                <span>{isInjectingFault ? 'INJECTING...' : '//chaos:inject'}</span>
              </button>

              <button
                onClick={handleRezero}
                className={`py-1.5 px-3 ${isDark ? 'bg-[#00E5FF]/10 hover:bg-[#00E5FF]/20 text-[#00E5FF] border-[#00E5FF]/30' : 'bg-cyan-100 hover:bg-cyan-200 text-cyan-800 border-cyan-300'} border text-[10px] font-semibold transition-all flex items-center justify-center gap-1 active:scale-95`}
              >
                <RefreshCw className="w-3 h-3" />
                <span>//rezero</span>
              </button>
            </div>

            <button
              onClick={() => onKineticTrigger('//boot')}
              className={`w-full py-1.5 ${isDark ? 'bg-[#E5B842]/20 hover:bg-[#E5B842]/30 text-[#E5B842] border-[#E5B842]/40' : 'bg-amber-100 hover:bg-amber-200 text-amber-900 border-amber-300'} border text-[10px] font-bold transition-all flex items-center justify-center gap-1 active:scale-95`}
            >
              <Zap className="w-3 h-3" />
              <span>//boot (SOVEREIGN REIGNITION)</span>
            </button>
          </div>
        </motion.aside>

        {/* CENTER VOLUMETRIC VIEWPORT (Cols: 4-9) */}
        <section className={`col-span-12 lg:col-span-6 flex flex-col justify-between border ${isDark ? 'border-[#9D4EDD]/20 bg-gradient-to-b from-transparent to-[#9D4EDD]/5' : 'border-purple-600/30 bg-gradient-to-b from-transparent to-purple-100/40'} rounded-none relative p-4 min-h-[360px] lg:min-h-0`}>
          
          {/* Top Viewport Header Chips */}
          <div className="flex items-center justify-between w-full pointer-events-auto">
            <div className={`text-[10px] ${isDark ? 'text-[#9D4EDD] border-[#9D4EDD]/40 bg-[#050507]/70 shadow-[0_0_10px_rgba(157,78,221,0.2)]' : 'text-purple-800 border-purple-400 bg-white/80 shadow-md'} uppercase tracking-widest border backdrop-blur-md px-2.5 py-1 flex items-center gap-1.5 font-bold`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isDark ? 'bg-[#9D4EDD]' : 'bg-purple-600'} animate-pulse`} />
              [AVATAR_VIEWPORT_ACTIVE]
            </div>

            {/* Camera Switcher Buttons */}
            <div className={`flex items-center space-x-1 ${isDark ? 'bg-[#050507]/80 border-[#1D182A]' : 'bg-white/90 border-slate-300 shadow-sm'} backdrop-blur-md p-0.5 border`}>
              <button
                onClick={() => switchCameraMode('perspective')}
                className={`px-2 py-0.5 text-[10px] transition-all ${
                  cameraMode === 'perspective'
                    ? isDark ? 'bg-[#00E5FF]/20 text-[#00E5FF] border border-[#00E5FF]/40 font-bold' : 'bg-cyan-100 text-cyan-800 border border-cyan-300 font-bold'
                    : isDark ? 'text-neutral-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                3D Orbit
              </button>
              <button
                onClick={() => switchCameraMode('front_avatar')}
                className={`px-2 py-0.5 text-[10px] transition-all ${
                  cameraMode === 'front_avatar'
                    ? isDark ? 'bg-[#9D4EDD]/20 text-[#9D4EDD] border border-[#9D4EDD]/40 font-bold' : 'bg-purple-100 text-purple-800 border border-purple-300 font-bold'
                    : isDark ? 'text-neutral-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Avatar Close
              </button>
              <button
                onClick={() => switchCameraMode('top')}
                className={`px-2 py-0.5 text-[10px] transition-all ${
                  cameraMode === 'top'
                    ? isDark ? 'bg-[#E5B842]/20 text-[#E5B842] border border-[#E5B842]/40 font-bold' : 'bg-amber-100 text-amber-900 border border-amber-300 font-bold'
                    : isDark ? 'text-neutral-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Top Grid
              </button>
            </div>
          </div>

          {/* Central Holographic Crosshairs & Watermark */}
          <div className="flex-1 flex items-center justify-center pointer-events-none">
            {/* The 3D Canvas shines through this open volumetric space */}
          </div>

          {/* Bottom Viewport HUD HUD Bar */}
          <div className={`w-full flex items-center justify-between pointer-events-auto ${isDark ? 'bg-[#050507]/70 border-[#9D4EDD]/20' : 'bg-white/85 border-purple-300 shadow-md'} backdrop-blur-md p-2 border text-[10px]`}>
            <div className="flex items-center gap-2">
              <span className={`${isDark ? 'text-[#00E5FF]' : 'text-cyan-700'} font-bold`}>EMITTER:</span>
              <span className={isDark ? 'text-white' : 'text-slate-900 font-medium'}>CONCENTRIC_RINGS_V7</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={isDark ? 'text-neutral-400' : 'text-slate-600'}>SUBSTRATE:</span>
              <span className={`${isDark ? 'text-[#9D4EDD]' : 'text-purple-700'} font-semibold`}>WebGPU / Three.js 60 FPS</span>
            </div>
          </div>
        </section>

        {/* RIGHT TACTICAL MATRIX & AGENTIC CONSOLE (Cols: 10-12) */}
        <motion.aside 
          initial={{ x: 40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
          className={`col-span-12 lg:col-span-3 border ${isDark ? 'border-[#E5B842]/30 bg-[#050507]/70 text-white shadow-[0_0_15px_rgba(229,184,66,0.1)]' : 'border-amber-600/40 bg-white/90 text-slate-900 shadow-xl'} backdrop-blur-md p-4 lg:p-5 pointer-events-auto rounded-none flex flex-col justify-between transition-colors`}
        >
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <div className={`flex items-center justify-between border-b ${isDark ? 'border-[#E5B842]/20' : 'border-amber-600/20'} pb-2 mb-3`}>
              <h2 className={`${isDark ? 'text-[#E5B842]' : 'text-amber-800'} text-xs uppercase tracking-[0.3em] font-bold flex items-center gap-1.5`}>
                <Sparkles className={`w-3.5 h-3.5 ${isDark ? 'text-[#E5B842]' : 'text-amber-600'}`} />
                Agentic Console
              </h2>
              <button
                onClick={copyA2UIPayload}
                className={`flex items-center space-x-1 px-1.5 py-0.5 ${isDark ? 'bg-[#150E24] hover:bg-[#1F1436] text-neutral-300 border-[#2D1F4D]' : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300'} border text-[9px] transition-all`}
                title="Copy Declarative A2UI Payload"
              >
                {copiedCode ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                <span>{copiedCode ? 'Copied' : 'A2UI'}</span>
              </button>
            </div>

            {/* A2UI CARTRIDGE SLOT (Matching User Style Guide) */}
            <div className={`w-full mb-3 border border-dashed ${isDark ? 'border-gray-700 bg-[#0A0710]/80' : 'border-slate-300 bg-slate-50/90'} p-2.5 text-[10px]`}>
              <div className={`flex items-center justify-between text-[9px] ${isDark ? 'text-gray-500' : 'text-slate-500'} uppercase tracking-widest mb-1.5`}>
                <span>A2UI_CARTRIDGE_SLOT</span>
                <span className={`${isDark ? 'text-[#00E5FF]' : 'text-cyan-700'} font-mono font-bold`}>v1000.OMEGA</span>
              </div>
              <div className="grid grid-cols-1 gap-1.5">
                {a2uiPayload.cards.map(card => (
                  <div key={card.id} className={`p-1.5 ${isDark ? 'bg-[#110A1F] border-[#24133F]' : 'bg-white border-slate-200 shadow-sm'} border text-[10px]`}>
                    <div className="flex justify-between items-center">
                      <span className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'} text-[10px]`}>{card.title}</span>
                      {card.badge && (
                        <span className={`text-[8px] px-1 py-0.2 ${isDark ? 'bg-[#00E5FF]/10 text-[#00E5FF] border-[#00E5FF]/20' : 'bg-cyan-100 text-cyan-800 border-cyan-300'} border font-semibold`}>
                          {card.badge}
                        </span>
                      )}
                    </div>
                    <p className={`${isDark ? 'text-neutral-400' : 'text-slate-600'} text-[9px] mt-0.5 line-clamp-1`}>{card.content}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Live Copilot Stream Messages */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1 text-[10px] max-h-[220px] lg:max-h-none">
              <div className={`text-[9px] ${isDark ? 'text-neutral-500' : 'text-slate-500'} uppercase tracking-wider flex items-center justify-between`}>
                <span>CopilotKit Stream</span>
                <span className={`${isDark ? 'text-emerald-400' : 'text-emerald-700'} flex items-center gap-1 font-bold`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${isDark ? 'bg-emerald-400' : 'bg-emerald-600'} animate-pulse`} />
                  SHARED STATE
                </span>
              </div>

              <AnimatePresence initial={false}>
                {copilotMessages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-2 border text-[10px] ${
                      msg.sender === 'OPERATOR'
                        ? isDark ? 'bg-[#00E5FF]/10 border-[#00E5FF]/40 text-[#00E5FF]' : 'bg-cyan-50 border-cyan-300 text-cyan-900 font-medium'
                        : msg.sender === 'SIR_BORIS'
                        ? isDark ? 'bg-[#FF007F]/10 border-[#FF007F]/30 text-neutral-200' : 'bg-rose-50 border-rose-300 text-rose-900 font-medium'
                        : isDark ? 'bg-[#150E24] border-[#2D1F4D] text-neutral-200' : 'bg-purple-50 border-purple-200 text-purple-950 font-medium'
                    }`}
                  >
                    <div className="flex justify-between items-center mb-0.5 text-[8px]">
                      <span className={`font-bold uppercase ${isDark ? 'text-white' : 'text-slate-900'} tracking-wider`}>
                        {msg.sender === 'OPERATOR' ? '👤 OPERATOR' : msg.sender === 'SIR_BORIS' ? '🔨 SIR BORIS' : '🤖 ANYA_Ω / COPILOT'}
                      </span>
                      <span className={isDark ? 'text-neutral-400' : 'text-slate-500'}>{msg.time}</span>
                    </div>
                    <p className="leading-snug">{msg.text}</p>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* Copilot Input Box */}
          <form 
            onSubmit={handleSendCopilot}
            className={`mt-3 pt-2 border-t ${isDark ? 'border-[#E5B842]/20' : 'border-amber-600/20'} flex items-center gap-1.5`}
          >
            <input
              type="text"
              value={copilotInput}
              onChange={(e) => setCopilotInput(e.target.value)}
              placeholder="Direct CopilotKit (//chaos, //boot)..."
              className={`flex-1 ${isDark ? 'bg-[#110A1F] border-[#24133F] text-white placeholder-neutral-500 focus:border-[#00E5FF]' : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 focus:border-cyan-600'} border px-2.5 py-1.5 text-[10px] focus:outline-none`}
            />
            <button
              type="submit"
              className="px-2.5 py-1.5 bg-[#E5B842] hover:bg-[#E5B842]/80 text-[#050507] font-bold text-[10px] transition-all flex items-center gap-1 active:scale-95"
            >
              <Send className="w-3 h-3" />
            </button>
          </form>
        </motion.aside>

      </main>

      {/* SCANLINE & LUXURY BRUTALIST OVERLAY (From Style Guide) */}
      <div className="absolute inset-0 pointer-events-none opacity-5 mix-blend-overlay z-50 bg-[radial-gradient(#00E5FF_1px,transparent_1px)] [background-size:16px_16px]" />
    </div>
  );
};
