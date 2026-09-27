import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { multiVoiceRouter } from '../services/multiVoiceRouter';
import { ThemeMode } from '../types';

interface ThreeUIEngineProps {
  theme: ThemeMode;
  activeMode?: 'command' | 'factory' | 'multivoice' | 'heraldry';
  onSelectNode?: (nodeId: string) => void;
}

export const ThreeUIEngine: React.FC<ThreeUIEngineProps> = ({
  theme,
  activeMode = 'command',
  onSelectNode
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDark = theme === 'dark';

  const [hoveredObject, setHoveredObject] = useState<string | null>(null);
  const [fps, setFps] = useState(60);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    let animationFrameId: number;
    let width = container.clientWidth || 800;
    let height = container.clientHeight || 500;

    // 1. Scene & Atmosphere
    const scene = new THREE.Scene();
    const bgCol = isDark ? 0x050507 : 0xf1f5f9;
    scene.background = new THREE.Color(bgCol);
    scene.fog = new THREE.FogExp2(bgCol, 0.035);

    // 2. Camera Setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 5, 12);

    // 3. Renderer with High Dynamic Range Tone Mapping
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: 'high-performance',
      alpha: true
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = isDark ? 1.2 : 1.0;

    // 4. Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 + 0.1;
    controls.minDistance = 3;
    controls.maxDistance = 25;

    // 5. Lighting Matrix
    const ambientLight = new THREE.AmbientLight(isDark ? 0x221a36 : 0xffffff, isDark ? 1.8 : 2.5);
    scene.add(ambientLight);

    const cyanSpot = new THREE.SpotLight(0x00e5ff, 4, 30, Math.PI / 4, 0.3);
    cyanSpot.position.set(8, 12, 6);
    scene.add(cyanSpot);

    const purpleSpot = new THREE.SpotLight(0x9d4edd, 4, 30, Math.PI / 4, 0.3);
    purpleSpot.position.set(-8, 12, -6);
    scene.add(purpleSpot);

    const goldPoint = new THREE.PointLight(0xe5b842, 3, 15);
    goldPoint.position.set(0, 2, 0);
    scene.add(goldPoint);

    // 6. THREEUI SPATIAL FLOOR GRID
    const gridHelper = new THREE.GridHelper(
      28,
      28,
      isDark ? 0x00e5ff : 0x0284c7,
      isDark ? 0x1f1635 : 0xcbd5e1
    );
    gridHelper.position.y = -2;
    scene.add(gridHelper);

    // 7. THREEUI 3D HOLOGRAPHIC SHIELD & CROWN (HOME OF CAMELOT-OS)
    const heraldryGroup = new THREE.Group();
    heraldryGroup.position.set(0, 1.5, 0);

    // Outer Shield Frame (Extruded Shape)
    const shieldShape = new THREE.Shape();
    shieldShape.moveTo(0, 2.2);
    shieldShape.lineTo(1.8, 1.8);
    shieldShape.lineTo(1.5, -0.5);
    shieldShape.lineTo(0, -2.2);
    shieldShape.lineTo(-1.5, -0.5);
    shieldShape.lineTo(-1.8, 1.8);
    shieldShape.closePath();

    const extrudeSettings = { depth: 0.2, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: 0.05, bevelThickness: 0.05 };
    const shieldGeo = new THREE.ExtrudeGeometry(shieldShape, extrudeSettings);
    const shieldMat = new THREE.MeshPhysicalMaterial({
      color: isDark ? 0x24123d : 0xede9fe,
      emissive: isDark ? 0x3b1569 : 0xc4b5fd,
      emissiveIntensity: 0.4,
      roughness: 0.2,
      metalness: 0.8,
      wireframe: false,
      transparent: true,
      opacity: 0.88
    });
    const shieldMesh = new THREE.Mesh(shieldGeo, shieldMat);
    shieldMesh.name = 'HERALDRY_SHIELD';
    heraldryGroup.add(shieldMesh);

    // Wireframe Shield Overlay
    const shieldWireGeo = new THREE.WireframeGeometry(shieldGeo);
    const shieldWireMat = new THREE.LineBasicMaterial({
      color: isDark ? 0x00e5ff : 0x0891b2,
      transparent: true,
      opacity: 0.7
    });
    const shieldWire = new THREE.LineSegments(shieldWireGeo, shieldWireMat);
    heraldryGroup.add(shieldWire);

    // Crown on Top of Shield
    const crownGeo = new THREE.ConeGeometry(1.2, 0.9, 5, 1, true);
    const crownMat = new THREE.MeshStandardMaterial({
      color: 0xe5b842,
      metalness: 0.9,
      roughness: 0.2,
      emissive: 0x854d0e,
      emissiveIntensity: 0.5
    });
    const crownMesh = new THREE.Mesh(crownGeo, crownMat);
    crownMesh.position.set(0, 2.7, 0.1);
    crownMesh.rotation.y = Math.PI / 5;
    crownMesh.name = 'SOVEREIGN_CROWN';
    heraldryGroup.add(crownMesh);

    // Central Glowing Crystal Core (AI_KERNEL / DGT_STRUC)
    const coreGeo = new THREE.OctahedronGeometry(0.7, 0);
    const coreMat = new THREE.MeshPhysicalMaterial({
      color: 0xe5b842,
      emissive: 0xe5b842,
      emissiveIntensity: 1.2,
      roughness: 0.1,
      metalness: 0.9,
      transmission: 0.6,
      transparent: true,
      opacity: 0.95
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    coreMesh.position.set(0, 0.4, 0.35);
    coreMesh.name = 'AI_KERNEL_CORE';
    heraldryGroup.add(coreMesh);

    // Concentric Energy Halos
    const haloGeos = [1.8, 2.4, 3.1];
    const haloMeshes: THREE.Mesh[] = [];
    haloGeos.forEach((r, idx) => {
      const ringGeo = new THREE.TorusGeometry(r, 0.025, 12, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: idx === 0 ? 0x00e5ff : idx === 1 ? 0x9d4edd : 0xe5b842,
        transparent: true,
        opacity: 0.8
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2 + idx * 0.15;
      ring.name = `HALO_RING_${idx}`;
      heraldryGroup.add(ring);
      haloMeshes.push(ring);
    });

    scene.add(heraldryGroup);

    // 8. THREEUI 3D REAL-TIME AUDIO FREQUENCY BARS
    const audioBarsGroup = new THREE.Group();
    audioBarsGroup.position.set(0, -1.8, 3.5);
    const numBars = 24;
    const barMeshes: THREE.Mesh[] = [];
    const barWidth = 0.22;
    const spacing = 0.32;
    const startX = -((numBars - 1) * spacing) / 2;

    for (let i = 0; i < numBars; i++) {
      const barGeo = new THREE.BoxGeometry(barWidth, 1, 0.15);
      // Translate pivot to bottom
      barGeo.translate(0, 0.5, 0);

      const t = i / (numBars - 1);
      const barColor = new THREE.Color().lerpColors(
        new THREE.Color(0x00e5ff),
        new THREE.Color(0xff007f),
        t
      );

      const barMat = new THREE.MeshStandardMaterial({
        color: barColor,
        emissive: barColor,
        emissiveIntensity: 0.6,
        roughness: 0.3,
        metalness: 0.8
      });

      const barMesh = new THREE.Mesh(barGeo, barMat);
      barMesh.position.set(startX + i * spacing, 0, 0);
      barMesh.scale.y = 0.1;
      barMesh.name = `AUDIO_BAR_${i}`;
      audioBarsGroup.add(barMesh);
      barMeshes.push(barMesh);
    }
    scene.add(audioBarsGroup);

    // 9. THREEUI 3D DIGITAL FACTORY CONVEYOR PODS (BLAST PIPELINE)
    const factoryGroup = new THREE.Group();
    factoryGroup.position.set(0, -1.2, -4);

    const blastStages = [
      { name: 'BLUEPRINT', color: 0x00e5ff, pos: -4.5 },
      { name: 'LINK', color: 0x38bdf8, pos: -2.25 },
      { name: 'ARCHITECT', color: 0x9d4edd, pos: 0 },
      { name: 'STYLIZE', color: 0xf472b6, pos: 2.25 },
      { name: 'TRIGGER', color: 0xe5b842, pos: 4.5 }
    ];

    const podMeshes: THREE.Group[] = [];

    blastStages.forEach((stage) => {
      const pod = new THREE.Group();
      pod.position.set(stage.pos, 0, 0);

      // Base pedestal
      const pedGeo = new THREE.CylinderGeometry(0.8, 0.9, 0.3, 6);
      const pedMat = new THREE.MeshStandardMaterial({
        color: 0x150e24,
        roughness: 0.4,
        metalness: 0.8,
        emissive: stage.color,
        emissiveIntensity: 0.2
      });
      const ped = new THREE.Mesh(pedGeo, pedMat);
      pod.add(ped);

      // Floating crystal icon
      const cryGeo = new THREE.OctahedronGeometry(0.4, 0);
      const cryMat = new THREE.MeshPhysicalMaterial({
        color: stage.color,
        emissive: stage.color,
        emissiveIntensity: 0.8,
        roughness: 0.1,
        metalness: 0.9
      });
      const cry = new THREE.Mesh(cryGeo, cryMat);
      cry.position.y = 0.8;
      cry.name = `FACTORY_POD_${stage.name}`;
      pod.add(cry);

      // Ring around crystal
      const podRingGeo = new THREE.TorusGeometry(0.65, 0.02, 8, 32);
      const podRingMat = new THREE.MeshBasicMaterial({ color: stage.color });
      const podRing = new THREE.Mesh(podRingGeo, podRingMat);
      podRing.rotation.x = Math.PI / 2;
      podRing.position.y = 0.8;
      pod.add(podRing);

      factoryGroup.add(pod);
      podMeshes.push(pod);
    });

    scene.add(factoryGroup);

    // 10. THREEUI 3D RADIAL TACHOMETER / DIAL GAUGES
    const dialGroup = new THREE.Group();
    dialGroup.position.set(6, 2.5, 0);
    dialGroup.rotation.y = -Math.PI / 4;

    const dialRingGeo = new THREE.TorusGeometry(1.2, 0.04, 16, 48, Math.PI * 1.5);
    const dialRingMat = new THREE.MeshStandardMaterial({
      color: 0x00e5ff,
      emissive: 0x00e5ff,
      emissiveIntensity: 0.8
    });
    const dialRing = new THREE.Mesh(dialRingGeo, dialRingMat);
    dialRing.rotation.z = Math.PI * 0.75;
    dialGroup.add(dialRing);

    const needleGeo = new THREE.BoxGeometry(0.04, 1.0, 0.02);
    needleGeo.translate(0, 0.5, 0);
    const needleMat = new THREE.MeshBasicMaterial({ color: 0xff007f });
    const dialNeedle = new THREE.Mesh(needleGeo, needleMat);
    dialNeedle.position.z = 0.05;
    dialGroup.add(dialNeedle);

    scene.add(dialGroup);

    // 11. Raycasting Interactivity
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handlePointerMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children, true);

      if (intersects.length > 0) {
        const topHit = intersects[0].object;
        if (topHit.name) {
          setHoveredObject(topHit.name);
          canvas.style.cursor = 'pointer';
          return;
        }
      }
      setHoveredObject(null);
      canvas.style.cursor = 'grab';
    };

    const handleClick = () => {
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children, true);

      if (intersects.length > 0) {
        const hit = intersects[0].object;
        multiVoiceRouter.playCyberSfx('lock');
        if (hit.name && onSelectNode) {
          onSelectNode(hit.name);
        }
      }
    };

    canvas.addEventListener('mousemove', handlePointerMove);
    canvas.addEventListener('click', handleClick);

    // 12. Resize Observer
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width: w, height: h } = entry.contentRect;
        if (w > 0 && h > 0) {
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          renderer.setSize(w, h);
        }
      }
    });
    resizeObserver.observe(container);

    // 13. High-Performance Render Loop
    let clock = new THREE.Clock();
    let frameCount = 0;
    let lastTime = performance.now();
    const freqData = new Uint8Array(32);

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsed = clock.getElapsedTime();

      // FPS tracking
      frameCount++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(Math.round((frameCount * 1000) / (now - lastTime)));
        frameCount = 0;
        lastTime = now;
      }

      // Rotate Heraldry Group & Halos
      heraldryGroup.rotation.y = Math.sin(elapsed * 0.4) * 0.25;
      coreMesh.rotation.y = elapsed * 1.2;
      coreMesh.rotation.x = Math.sin(elapsed * 0.8) * 0.3;
      coreMesh.position.y = 0.4 + Math.sin(elapsed * 2) * 0.08;

      haloMeshes.forEach((halo, i) => {
        halo.rotation.z += (i % 2 === 0 ? 1 : -1) * delta * (0.6 + i * 0.2);
        halo.rotation.x += delta * 0.2;
      });

      // Animate Dial Needle with pseudo-telemetry
      dialNeedle.rotation.z = -Math.PI * 0.5 + (Math.sin(elapsed * 1.5) * 0.5 + 0.5) * Math.PI * 1.2;

      // Animate Factory Pods
      podMeshes.forEach((pod, idx) => {
        const crystal = pod.children[1] as THREE.Mesh;
        if (crystal) {
          crystal.rotation.y += delta * (1.2 + idx * 0.2);
          crystal.position.y = 0.8 + Math.sin(elapsed * 2.5 + idx) * 0.12;
        }
      });

      // Update Audio Spectrum Frequency Bars from MultiVoice Analyser
      const analyser = multiVoiceRouter.getAnalyser();
      if (analyser) {
        analyser.getByteFrequencyData(freqData);
        for (let i = 0; i < numBars; i++) {
          const val = (freqData[i] || 0) / 255;
          const targetScale = Math.max(0.1, val * 3.5);
          barMeshes[i].scale.y += (targetScale - barMeshes[i].scale.y) * 0.3;
        }
      } else {
        // Ambient fallback wave
        for (let i = 0; i < numBars; i++) {
          const synthVal = Math.sin(elapsed * 4 + i * 0.4) * 0.5 + 0.5;
          barMeshes[i].scale.y = 0.2 + synthVal * 0.8;
        }
      }

      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      canvas.removeEventListener('mousemove', handlePointerMove);
      canvas.removeEventListener('click', handleClick);
      renderer.dispose();
    };
  }, [isDark, activeMode]);

  return (
    <div ref={containerRef} className="relative w-full h-full min-h-[380px] overflow-hidden select-none">
      <canvas ref={canvasRef} className="w-full h-full block" />

      {/* Floating ThreeUI Diagnostics Overlay */}
      <div className="absolute top-3 left-3 pointer-events-none flex items-center gap-2">
        <div className={`px-2 py-0.5 text-[10px] font-mono border backdrop-blur-md ${
          isDark ? 'bg-black/60 border-cyan-500/40 text-cyan-400' : 'bg-white/80 border-cyan-600/30 text-cyan-800'
        }`}>
          <span>THREEUI_ENGINE: </span>
          <span className="font-bold">{fps} FPS</span>
        </div>

        {hoveredObject && (
          <div className={`px-2 py-0.5 text-[10px] font-mono border backdrop-blur-md animate-pulse ${
            isDark ? 'bg-purple-950/80 border-purple-400 text-purple-200' : 'bg-purple-100 border-purple-500 text-purple-900'
          }`}>
            TARGET: {hoveredObject}
          </div>
        )}
      </div>
    </div>
  );
};
