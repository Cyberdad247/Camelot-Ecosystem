"use client";

import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sparkles, Float } from '@react-three/drei';
import { useRef } from 'react';
import * as THREE from 'three';

const GlowingTable = () => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current) {
        meshRef.current.rotation.y += 0.005;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <mesh ref={meshRef}>
        <cylinderGeometry args={[3, 3, 0.2, 32]} />
        <meshStandardMaterial 
            emissive="#00ffcc" 
            emissiveIntensity={2} 
            color="#000000" 
            roughness={0.1}
            metalness={0.8}
        />
      </mesh>
       {/* Holographic Ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
         <ringGeometry args={[3.2, 3.25, 64]} />
         <meshBasicMaterial color="#00ffff" side={THREE.DoubleSide} transparent opacity={0.6} />
      </mesh>
    </Float>
  );
};

export default function RoundTableScene() {
    return (
        <div className="w-full h-full bg-slate-950 rounded-xl overflow-hidden border border-slate-800 shadow-2xl relative">
            <Canvas camera={{ position: [0, 5, 10], fov: 45 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#00ffcc" />
                <GlowingTable />
                <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
                <Sparkles count={50} scale={10} size={4} speed={0.4} opacity={0.5} color="#00ffff" />
                <gridHelper args={[20, 20, 0x1e293b, 0x0f172a]} />
            </Canvas>
            <div className="absolute top-4 left-4 bg-black/50 p-2 rounded text-xs text-cyan-400 font-mono border border-cyan-900/50 backdrop-blur-sm">
                CAMELOT_VISUALIZER::ACTIVE
            </div>
        </div>
    );
}
