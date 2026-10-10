// SPDX-License-Identifier: MIT
//
// Spatial Citadel — 3D Rotational Interface Cockpit
// Assimilated from adrianhajdin/3D_portfolio:
// - React Three Fiber (R3F) Canvas scene graph with ambient/directional lighting.
// - Damped rotation mechanics (dampingFactor 0.95) driving 4-quadrant subsystem focus.
// - Complies with PWA law: Luxora Gold (#D4AF37) accents, 'use client', no SSR bleed.

'use client';

import React, { Suspense, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import type * as THREE from 'three';

export interface SpatialCitadelProps {
  onQuadrantChange?: (quadrant: number) => void;
  className?: string;
}

interface CitadelTurntableProps {
  isRotating: boolean;
  setIsRotating: (rotating: boolean) => void;
  setQuadrant: (quadrant: number) => void;
}

function CitadelTurntable({
  isRotating,
  setIsRotating,
  setQuadrant,
}: CitadelTurntableProps) {
  const meshRef = useRef<THREE.Group>(null);
  const lastX = useRef<number>(0);
  const rotationSpeed = useRef<number>(0);
  const dampingFactor = 0.95;

  // Handle pointer down (mouse or touch)
  const handlePointerDown = (e: React.PointerEvent) => {
    e.stopPropagation();
    setIsRotating(true);
    lastX.current = e.clientX;
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    e.stopPropagation();
    setIsRotating(false);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    e.stopPropagation();
    if (isRotating && meshRef.current) {
      const delta = (e.clientX - lastX.current) * 0.005;
      meshRef.current.rotation.y += delta;
      lastX.current = e.clientX;
      rotationSpeed.current = delta;
    }
  };

  useFrame(() => {
    if (!meshRef.current) return;

    if (!isRotating) {
      rotationSpeed.current *= dampingFactor;
      if (Math.abs(rotationSpeed.current) < 0.0001) {
        rotationSpeed.current = 0;
      }
      meshRef.current.rotation.y += rotationSpeed.current;
    }

    // Determine 4-quadrant orientation (0..2PI)
    const normalizedRotation =
      ((meshRef.current.rotation.y % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);

    let stage = 1;
    if (normalizedRotation >= 0 && normalizedRotation < Math.PI / 2) {
      stage = 1; // Core
    } else if (normalizedRotation >= Math.PI / 2 && normalizedRotation < Math.PI) {
      stage = 2; // Pantheon
    } else if (normalizedRotation >= Math.PI && normalizedRotation < (3 * Math.PI) / 2) {
      stage = 3; // CloudBrain
    } else {
      stage = 4; // Excalibur Mobile
    }
    setQuadrant(stage);
  });

  return (
    <group
      ref={meshRef}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerMove={handlePointerMove}
      position={[0, -0.5, 0]}
    >
      {/* Central Cybertronia Spire (Hexagonal Pillar) */}
      <mesh position={[0, 1, 0]}>
        <cylinderGeometry args={[0.8, 1.2, 2.5, 6]} />
        <meshStandardMaterial
          color="#111111"
          metalness={0.9}
          roughness={0.1}
          wireframe={false}
        />
      </mesh>

      {/* Orbiting Luxora Gold Rings */}
      <mesh position={[0, 1.2, 0]} rotation={[0.4, 0, 0]}>
        <torusGeometry args={[1.8, 0.04, 16, 64]} />
        <meshStandardMaterial color="#D4AF37" metalness={1.0} roughness={0.2} />
      </mesh>
      <mesh position={[0, 1.2, 0]} rotation={[-0.4, 0.8, 0]}>
        <torusGeometry args={[2.2, 0.03, 16, 64]} />
        <meshStandardMaterial color="#38bdf8" metalness={0.8} roughness={0.3} />
      </mesh>

      {/* 4 Quadrant Satellite Pylons */}
      {/* Q1: Sovereign Root Node */}
      <mesh position={[2.5, 0.2, 0]}>
        <boxGeometry args={[0.4, 0.8, 0.4]} />
        <meshStandardMaterial color="#10b981" />
      </mesh>
      {/* Q2: Omega Pantheon Node */}
      <mesh position={[0, 0.2, 2.5]}>
        <boxGeometry args={[0.4, 0.8, 0.4]} />
        <meshStandardMaterial color="#D4AF37" />
      </mesh>
      {/* Q3: CloudBrain Node */}
      <mesh position={[-2.5, 0.2, 0]}>
        <boxGeometry args={[0.4, 0.8, 0.4]} />
        <meshStandardMaterial color="#a855f7" />
      </mesh>
      {/* Q4: Excalibur Sentinel Node */}
      <mesh position={[0, 0.2, -2.5]}>
        <boxGeometry args={[0.4, 0.8, 0.4]} />
        <meshStandardMaterial color="#06b6d4" />
      </mesh>
    </group>
  );
}

export function SpatialCitadel({ onQuadrantChange, className }: SpatialCitadelProps) {
  const [isRotating, setIsRotating] = useState(false);
  const [currentQuadrant, setCurrentQuadrant] = useState(1);

  const handleQuadrant = (q: number) => {
    if (q !== currentQuadrant) {
      setCurrentQuadrant(q);
      onQuadrantChange?.(q);
    }
  };

  const quadrantLabels = [
    { title: 'Sovereign Core', desc: 'Cybertronia Root & 4GB Edge Ceiling', color: 'text-emerald' },
    { title: 'Omega Pantheon', desc: 'L7 Modality Hypervisors & Z3 Provers', color: 'text-gold' },
    { title: 'WorldTree CloudBrain', desc: '294 Notebooks & Living Tissues', color: 'text-purple-400' },
    { title: 'Excalibur Mobile', desc: 'Samsung S26 Ultra 120Hz Mesh', color: 'text-cyan' },
  ];

  const activeInfo = quadrantLabels[currentQuadrant - 1] ?? quadrantLabels[0];

  return (
    <div className={`relative h-[360px] w-full overflow-hidden rounded-lg border border-gold/20 bg-black/90 ${className ?? ''}`}>
      {/* Heads-Up Stage Indicator Overlay */}
      <div className="pointer-events-none absolute top-4 left-4 z-10 space-y-1">
        <p className="font-mono text-[10px] text-white/50 uppercase tracking-widest">
          Spatial Citadel // Quadrant {currentQuadrant}
        </p>
        <p className={`font-display text-sm tracking-wider ${activeInfo.color}`}>
          {activeInfo.title}
        </p>
        <p className="font-mono text-xs text-white/40">{activeInfo.desc}</p>
      </div>

      <div className="pointer-events-none absolute bottom-4 right-4 z-10">
        <span className="font-mono text-[10px] text-gold/60 uppercase">
          Drag to Rotate (Damping 0.95)
        </span>
      </div>

      {/* 3D WebGL Canvas */}
      <Canvas
        className={`h-full w-full ${isRotating ? 'cursor-grabbing' : 'cursor-grab'}`}
        camera={{ position: [0, 2.5, 5], fov: 50 }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 10, 5]} intensity={1.5} />
        <pointLight position={[-5, 5, -5]} intensity={0.8} color="#D4AF37" />
        <Suspense fallback={null}>
          <CitadelTurntable
            isRotating={isRotating}
            setIsRotating={setIsRotating}
            setQuadrant={handleQuadrant}
          />
        </Suspense>
      </Canvas>
    </div>
  );
}

export default SpatialCitadel;
