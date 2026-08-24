import { useMemo, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { FLOORS, FLOOR_GAP, TOWER_TOP_Y } from './tower-data';
import { resolveCameraLayout } from './camera-layout';

/** Camelot palette */
const OBSIDIAN = '#050505';
const PLATE = '#0b0b10';
const GOLD = '#D4AF37';
const PURPLE = '#2E0854';
const PURPLE_NEON = '#7A3BD6';

export interface ScrollState {
  progress: number;      // 0 = crown, 1 = foundation
  activeFloor: number;
}

interface SceneProps {
  scroll: React.MutableRefObject<ScrollState>;
  reducedMotion: boolean;
}

/** Taper: crown floors are narrower than the foundation. */
function radiusAt(index: number): number {
  return 1.55 + (index / (FLOORS.length - 1)) * 0.75;
}

function Floor({ index, scroll }: { index: number; scroll: React.MutableRefObject<ScrollState> }) {
  const ringRef = useRef<THREE.MeshStandardMaterial>(null);
  const y = TOWER_TOP_Y - index * FLOOR_GAP;
  const r = radiusAt(index);

  const windows = useMemo(() => {
    const count = 6 + index;
    return Array.from({ length: count }, (_, i) => {
      const a = (i / count) * Math.PI * 2;
      return { position: [Math.cos(a) * (r + 0.02), 0.3, Math.sin(a) * (r + 0.02)] as [number, number, number], rotationY: -a + Math.PI / 2 };
    });
  }, [index, r]);

  return (
    <group position={[0, y, 0]}>
      {/* Stone drum */}
      <mesh>
        <cylinderGeometry args={[r, r + 0.12, 2.1, 24]} />
        <meshStandardMaterial color={PLATE} roughness={0.85} metalness={0.15} />
      </mesh>
      {/* Gold cornice */}
      <mesh position={[0, 1.12, 0]}>
        <cylinderGeometry args={[r + 0.18, r + 0.18, 0.14, 24]} />
        <meshStandardMaterial color={GOLD} roughness={0.35} metalness={0.9} />
      </mesh>
      {/* Active-floor ring: emissive intensity driven per-frame */}
      <mesh position={[0, -0.9, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[r + 0.22, 0.045, 12, 48]} />
        <meshStandardMaterial ref={ringRef} color={PURPLE} emissive={PURPLE_NEON} emissiveIntensity={0} roughness={0.4} />
      </mesh>
      {/* Arrow-slit windows, gold-lit */}
      {windows.map((w, i) => (
        <mesh key={i} position={w.position} rotation={[0, w.rotationY, 0]}>
          <boxGeometry args={[0.1, 0.55, 0.05]} />
          <meshStandardMaterial color={GOLD} emissive={GOLD} emissiveIntensity={0.6} />
        </mesh>
      ))}
      <FloorRingDriver index={index} ringRef={ringRef} scroll={scroll} />
    </group>
  );
}

/** Pulses the purple ring of whichever floor is active. */
function FloorRingDriver({ index, ringRef, scroll }: { index: number; ringRef: React.RefObject<THREE.MeshStandardMaterial>; scroll: React.MutableRefObject<ScrollState> }) {
  useFrame(({ clock }) => {
    const mat = ringRef.current;
    if (!mat) return;
    const active = scroll.current.activeFloor === index;
    const target = active ? 1.6 + Math.sin(clock.elapsedTime * 3) * 0.35 : 0;
    mat.emissiveIntensity = THREE.MathUtils.lerp(mat.emissiveIntensity, target, 0.12);
  });
  return null;
}

function Roof() {
  return (
    <group position={[0, TOWER_TOP_Y + 1.05, 0]}>
      <mesh position={[0, 1.1, 0]}>
        <coneGeometry args={[radiusAt(0) + 0.35, 2.4, 24]} />
        <meshStandardMaterial color={PURPLE} roughness={0.6} metalness={0.3} />
      </mesh>
      {/* Beacon */}
      <mesh position={[0, 2.5, 0]}>
        <sphereGeometry args={[0.14, 16, 16]} />
        <meshStandardMaterial color={GOLD} emissive={GOLD} emissiveIntensity={2.2} />
      </mesh>
      <pointLight position={[0, 2.5, 0]} color={GOLD} intensity={3} distance={9} />
    </group>
  );
}

/** The provenance spine — one gold line, crown to foundation. */
function Spine() {
  const points = useMemo(
    () => [new THREE.Vector3(0, TOWER_TOP_Y + 1.2, 0), new THREE.Vector3(0, -1.4, 0)],
    []
  );
  const geometry = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);
  return (
    <line>
      <primitive object={geometry} attach="geometry" />
      <lineBasicMaterial color={GOLD} transparent opacity={0.55} />
    </line>
  );
}

/**
 * Camera rig: helical descent scrubbed by scroll progress.
 * Responsive: orbit radius and FOV widen on narrow aspects so the tower
 * always fits the frame.
 */
function CameraRig({ scroll, reducedMotion }: SceneProps) {
  const { camera, size } = useThree();
  const smoothed = useRef(0);

  useFrame(() => {
    const target = scroll.current.progress;
    smoothed.current = reducedMotion ? target : THREE.MathUtils.lerp(smoothed.current, target, 0.08);

    const layout = resolveCameraLayout(size.width, size.height, smoothed.current);
    const persp = camera as THREE.PerspectiveCamera;
    if (Math.abs(persp.fov - layout.fov) > 0.1 || persp.near !== layout.near || persp.far !== layout.far) {
      persp.fov = THREE.MathUtils.lerp(persp.fov, layout.fov, 0.1);
      persp.near = layout.near;
      persp.far = layout.far;
      persp.updateProjectionMatrix();
    }
    camera.position.set(layout.path.x, layout.path.y, layout.path.z);
    camera.lookAt(0, layout.path.focusY + layout.framingBias, 0);
  });
  return null;
}

export function TowerScene({ scroll, reducedMotion }: SceneProps) {
  return (
    <Canvas
      dpr={[1, 2]}
      camera={{ position: [5, TOWER_TOP_Y + 2, 5], fov: 45, near: 0.1, far: 80 }}
      gl={{ antialias: true }}
      style={{ position: 'fixed', inset: 0 }}
    >
      <color attach="background" args={[OBSIDIAN]} />
      <fog attach="fog" args={[OBSIDIAN, 10, 34]} />

      <ambientLight intensity={0.25} />
      <directionalLight position={[6, 14, 4]} intensity={0.7} color="#e8e2d0" />
      <pointLight position={[0, -2, 0]} color={PURPLE_NEON} intensity={2} distance={14} />

      {FLOORS.map((_, i) => <Floor key={i} index={i} scroll={scroll} />)}
      <Roof />
      <Spine />

      {/* Ground plane */}
      <mesh position={[0, -1.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[16, 48]} />
        <meshStandardMaterial color="#08080c" roughness={0.95} />
      </mesh>

      <CameraRig scroll={scroll} reducedMotion={reducedMotion} />
    </Canvas>
  );
}
