'use client';

import React, { useRef } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Billboard, Image as DreiImage } from '@react-three/drei';
import * as THREE from 'three';

const KNIGHTS_META = [
  { name: 'Merlin', pos: [0, 1.5, -4], sprite: '/assets/knights/merlin.png', color: '#FFD700' },
  { name: 'Zenith', pos: [3.5, 1.5, -3], sprite: '/assets/knights/zenith.png', color: '#ff4444' },
  { name: 'Anya', pos: [-3.5, 1.5, -3], sprite: '/assets/knights/anya.png', color: '#44ffaa' },
  { name: 'Syntax', pos: [4.5, 1.5, 0.5], sprite: '/assets/knights/merlin.png', color: '#44aaff' }, // Sync temp
  { name: 'Nova', pos: [-4.5, 1.5, 0.5], sprite: '/assets/knights/merlin.png', color: '#ff8844' }, // Nova temp
];

function RoundTable() {
  return (
    <group>
      {/* The Table Top */}
      <mesh position={[0, 0, 0]} receiveShadow>
        <cylinderGeometry args={[5, 5, 0.2, 32]} />
        <meshStandardMaterial color="#0c0c0c" roughness={0.05} metalness={0.9} />
      </mesh>

      {/* Gold Rim / Energy Ring */}
      <mesh position={[0, 0.11, 0]}>
        <cylinderGeometry args={[5.05, 5.05, 0.02, 64]} />
        <meshStandardMaterial color="#FFD700" emissive="#FFD700" emissiveIntensity={2} />
      </mesh>

      {/* Center Hologram Core */}
      <mesh position={[0, 0.3, 0]}>
        <cylinderGeometry args={[1, 1, 0.5, 32]} />
        <meshStandardMaterial
          color="#44aaff"
          transparent
          opacity={0.3}
          emissive="#44aaff"
          emissiveIntensity={1}
        />
      </mesh>
    </group>
  );
}

function KnightBillboard({
  position,
  sprite,
  color,
}: { position: number[]; sprite: string; color: string }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.position.y =
        position[1] + Math.sin(state.clock.elapsedTime + position[0]) * 0.1;
    }
  });

  return (
    <group ref={groupRef} position={new THREE.Vector3(position[0], position[1], position[2])}>
      <Billboard follow={true}>
        <DreiImage url={sprite} scale={[2.5, 3.5]} transparent alphaTest={0.5} />
        {/* Glow behind the sprite */}
        <mesh position={[0, 0, -0.1]}>
          <planeGeometry args={[3, 4]} />
          <meshBasicMaterial color={color} transparent opacity={0.1} />
        </mesh>
      </Billboard>

      {/* Foot Light */}
      <pointLight position={[0, -1.5, 0]} distance={4} intensity={2} color={color} />
    </group>
  );
}

function Environment() {
  const texture = useLoader(THREE.TextureLoader, '/assets/throne_bg.webp');
  texture.mapping = THREE.EquirectangularReflectionMapping;

  return (
    <mesh orientation-y={Math.PI}>
      <sphereGeometry args={[50, 64, 64]} />
      <meshBasicMaterial map={texture} side={THREE.BackSide} />
    </mesh>
  );
}

export function ThroneRoom() {
  return (
    <Canvas shadows className="w-full h-full">
      <PerspectiveCamera makeDefault position={[0, 6, 12]} fov={50} />
      <OrbitControls
        enableZoom={false}
        maxPolarAngle={Math.PI / 2.1}
        minPolarAngle={Math.PI / 4}
        rotateSpeed={0.5}
      />

      <ambientLight intensity={0.5} />
      <pointLight position={[0, 15, 0]} intensity={3} color="#FFD700" />

      {/* The Immersive Background */}
      <React.Suspense fallback={null}>
        <Environment />
      </React.Suspense>

      {/* The Stage */}
      <RoundTable />

      {/* The Knights */}
      {KNIGHTS_META.map((knight, idx) => (
        <KnightBillboard
          key={idx}
          position={knight.pos}
          sprite={knight.sprite}
          color={knight.color}
        />
      ))}

      {/* Floor reflection effect */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]} receiveShadow>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial
          color="#000"
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.8}
        />
      </mesh>
    </Canvas>
  );
}
