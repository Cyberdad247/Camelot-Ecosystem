"use client";

import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { motion } from 'motion/react';
import { Sparkles, Terminal, Activity, Shield } from 'lucide-react';

// --- 3D WEBGPU SUBSTRATE (Sir Stitch & Sir Visage) ---
// Renders the holographic spinning rings from your visual anchor
const HolographicRings = () => {
  const groupRef = useRef<THREE.Group>(null);
  
  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.2;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Outer Cyan Wireframe Halo */}
      <mesh>
        <torusGeometry args={[2.5, 0.02, 16, 100]} />
        <meshBasicMaterial color="#00E5FF" wireframe opacity={0.6} transparent />
      </mesh>
      {/* Radiant Violet Perpendicular Ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[3, 0.01, 16, 100]} />
        <meshBasicMaterial color="#9D4EDD" wireframe opacity={0.3} transparent />
      </mesh>
      {/* Inner Neon Core */}
      <mesh rotation={[0, Math.PI / 4, 0]}>
        <torusGeometry args={[1.8, 0.015, 16, 80]} />
        <meshBasicMaterial color="#FF007F" wireframe opacity={0.4} transparent />
      </mesh>
    </group>
  );
};

// --- A2UI DECLARATIVE OVERLAY (Sir Hydron) ---
export default function HolographicCommandCenter({
  onDirectiveChange,
}: {
  onDirectiveChange?: (status: string) => void;
}) {
  const [systemState, setSystemState] = useState("AWAITING_DIRECTIVE");

  const updateTelemetry = (newStatus: string) => {
    setSystemState(newStatus);
    if (onDirectiveChange) {
      onDirectiveChange(newStatus);
    }
  };

  return (
    <div className="relative w-full h-full min-h-[85vh] bg-[#050507] overflow-hidden font-mono text-white selection:bg-[#00E5FF] selection:text-black">
      
      {/* LAYER 1: 3D HARDWARE ACCELERATED CANVAS */}
      <div className="absolute inset-0 z-0 opacity-80 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
          <ambientLight intensity={0.5} />
          <HolographicRings />
        </Canvas>
      </div>

      {/* LAYER 2: 12-COLUMN GLASSMORPHIC HUD OVERLAY */}
      <main className="relative z-10 grid grid-cols-12 gap-6 p-8 h-full pointer-events-none">
        
        {/* Left Telemetry Panel */}
        <motion.aside 
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="col-span-12 lg:col-span-3 border border-[#00E5FF]/30 bg-[#050507]/40 backdrop-blur-md p-6 pointer-events-auto rounded-none shadow-[0_0_15px_rgba(0,229,255,0.1)] flex flex-col justify-between"
        >
          <div>
            <h2 className="text-[#00E5FF] text-xs uppercase tracking-[0.3em] mb-4 border-b border-[#00E5FF]/20 pb-2 flex items-center justify-between">
              <span>System Telemetry</span>
              <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] animate-ping" />
            </h2>
            <div className="flex flex-col gap-4 text-[10px] tracking-wider text-gray-400">
              <div className="flex justify-between">
                <span>NODE:</span> <span className="text-white font-bold">CYBERTRONIA_MASTER</span>
              </div>
              <div className="flex justify-between">
                <span>STATUS:</span> <span className="text-[#E5B842] font-semibold">{systemState}</span>
              </div>
              <div className="flex justify-between">
                <span>LATTICE:</span> <span className="text-[#9D4EDD] font-semibold">SECURE</span>
              </div>
              <div className="flex justify-between">
                <span>PROFILE:</span> <span className="text-emerald-400">8GB_EDGE_STRICT</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#00E5FF]/20 flex gap-2">
            <button
              onClick={() => updateTelemetry("SYSTEM_STRESSED: CHAOS_INJECTED")}
              className="flex-1 py-1.5 bg-[#FF007F]/20 hover:bg-[#FF007F]/30 text-[#FF007F] border border-[#FF007F]/40 text-[10px] font-bold transition-all active:scale-95"
            >
              //inject
            </button>
            <button
              onClick={() => updateTelemetry("AWAITING_DIRECTIVE")}
              className="px-3 py-1.5 bg-[#00E5FF]/20 hover:bg-[#00E5FF]/30 text-[#00E5FF] border border-[#00E5FF]/40 text-[10px] transition-all active:scale-95"
            >
              //rezero
            </button>
          </div>
        </motion.aside>

        {/* Center Volumetric Viewport */}
        <section className="col-span-12 lg:col-span-6 flex items-center justify-center border border-[#9D4EDD]/20 bg-gradient-to-b from-transparent to-[#9D4EDD]/5 rounded-none relative min-h-[300px]">
          <div className="absolute top-4 left-4 text-[10px] text-[#9D4EDD] uppercase tracking-widest border border-[#9D4EDD]/30 px-2 py-1 bg-[#050507]/60 backdrop-blur-md">
            [AVATAR_VIEWPORT_ACTIVE]
          </div>
          {/* The 3D Canvas shines through this empty space */}
          <div className="text-center pointer-events-none opacity-40">
            <div className="text-[10px] text-[#00E5FF] tracking-[0.4em] uppercase mb-1">
              VOLUMETRIC_SUBSTRATE
            </div>
            <div className="text-[8px] text-gray-500 font-mono">
              WEBGPU_SPATIAL_HUD // WASM_SANDBOXED
            </div>
          </div>
        </section>

        {/* Right Tactical Matrix */}
        <motion.aside 
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
          className="col-span-12 lg:col-span-3 border border-[#E5B842]/30 bg-[#050507]/40 backdrop-blur-md p-6 pointer-events-auto rounded-none flex flex-col justify-between"
        >
          <div>
            <h2 className="text-[#E5B842] text-xs uppercase tracking-[0.3em] mb-4 border-b border-[#E5B842]/20 pb-2">
              Agentic Console
            </h2>
            {/* A2UI Component Slot for Agent-Rendered Forms */}
            <div className="w-full h-32 border border-dashed border-gray-700 bg-[#0A0710]/60 p-3 flex flex-col justify-between text-[10px] text-gray-400">
              <div className="flex justify-between items-center text-[9px] text-[#00E5FF]">
                <span>A2UI_CARTRIDGE_SLOT</span>
                <span>v1000.OMEGA</span>
              </div>
              <p className="text-neutral-300 text-[10px]">
                Declarative UI payload mounted. CopilotKit state synchronized.
              </p>
              <div className="text-[8px] text-gray-500 flex justify-between">
                <span>TARGET: CYBERTRONIA</span>
                <span className="text-emerald-400">ACTIVE</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#E5B842]/20 text-[9px] text-gray-500">
            [RUNTIME_PROFILE]: 8GB_EDGE_NODE_STRICT
          </div>
        </motion.aside>

      </main>
      
      {/* Scanline Overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-10 mix-blend-overlay z-50 bg-[radial-gradient(#00E5FF_1px,transparent_1px)] [background-size:16px_16px]" />
    </div>
  );
}
