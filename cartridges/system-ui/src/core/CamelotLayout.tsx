import React, { useEffect, useState, useRef, useTransition } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

// ── VRAM Protection Hook (SIR_BORIS Protocol) ────────────────────────────────
function VramGovernor() {
  const { gl, scene } = useThree();

  useEffect(() => {
    return () => {
      // Deep traversal to dispose geometries, materials, and textures on unmount
      scene.traverse((object) => {
        if (!(object instanceof THREE.Mesh)) return;

        if (object.geometry) {
          object.geometry.dispose();
        }

        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((mat) => mat.dispose());
          } else {
            object.material.dispose();
          }
        }
      });

      // Dispose of the WebGL renderer context and force context loss
      gl.dispose();
      gl.forceContextLoss();
      console.log('[SIR_BORIS] VRAM Governor: Cleaned WebGL context & disposed geometries/materials.');
    };
  }, [gl, scene]);

  return null;
}

// ── 3D Earth Globe Component (R3F) ───────────────────────────────────────────
function EmpireGlobe() {
  return (
    <mesh castShadow receiveShadow>
      <sphereGeometry args={[2.5, 32, 32]} />
      <meshStandardMaterial
        color="#00E5FF"
        wireframe
        emissive="#00E5FF"
        emissiveIntensity={0.2}
      />
    </mesh>
  );
}

// ── Master Bento Box Layout ──────────────────────────────────────────────────
export default function CamelotLayout() {
  const [telemetry, setTelemetry] = useState({
    lattice: 'RADIANT',
    ramUsage: 42.5,
    networkLag: 5,
    activeAgents: 10,
  });
  const [show3D, setShow3D] = useState(true);
  const [messages, setMessages] = useState<string[]>([]);
  const [, startTransition] = useTransition();

  // ── Bifrost Bridge Stream Connection (SSE) ──────────────────────────────────
  useEffect(() => {
    // Connect to the Go Omni-Router's Bifrost Bridge SSE endpoint
    const eventSource = new EventSource('/bifrost/stream');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        startTransition(() => {
          setTelemetry((prev) => ({
            ...prev,
            ...data,
          }));
        });
      } catch (err) {
        console.error('[BIFROST] Error parsing SSE payload:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.warn('[BIFROST] SSE connection disconnected, attempting retry:', err);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-[#05050A] font-mono text-[#00E5FF] selection:bg-[#FFD700] selection:text-black">
      {/* Top Identity bar */}
      <header className="flex items-center justify-between border-b border-[#00E5FF]/20 px-6 py-4 bg-[#12121A]">
        <div className="flex items-center gap-4">
          <span className="text-xl font-bold tracking-widest text-[#FFD700]">EXCALIBUR // PWA</span>
          <span className="text-xs bg-[#00E5FF]/10 px-2 py-0.5 rounded border border-[#00E5FF]/30">v9000.101</span>
        </div>
        <div className="flex gap-6 text-xs">
          <div>LATTICE: <span className="text-[#FFD700]">{telemetry.lattice}</span></div>
          <div>RAM: <span className="text-[#FFD700]">{telemetry.ramUsage.toFixed(1)}%</span></div>
          <div>LAG: <span className="text-[#FFD700]">{telemetry.networkLag}ms</span></div>
        </div>
      </header>

      {/* Main Grid: Bento Box Architecture */}
      <main className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4 p-4 overflow-hidden">
        
        {/* Left Column: Telemetry & Agent Registry */}
        <section className="flex flex-col gap-4 border border-[#00E5FF]/20 bg-[#12121A]/50 p-4 rounded-lg">
          <h2 className="text-sm font-bold tracking-widest border-b border-[#00E5FF]/20 pb-2 text-[#FFD700]">
            🤖 TELEMETRY BENTO
          </h2>
          <div className="flex-1 flex flex-col gap-2 justify-center">
            <div className="bg-black/40 p-3 rounded border border-[#00E5FF]/10">
              <div className="text-xs text-[#00E5FF]/50">ACTIVE AGENTS</div>
              <div className="text-2xl font-bold">{telemetry.activeAgents} / 43</div>
            </div>
            <div className="bg-black/40 p-3 rounded border border-[#00E5FF]/10">
              <div className="text-xs text-[#00E5FF]/50">RAM CONSUMPTION</div>
              <div className="text-2xl font-bold">{telemetry.ramUsage.toFixed(1)}%</div>
            </div>
            <button
              onClick={() => setShow3D(!show3D)}
              className="mt-4 px-4 py-2 border border-[#FFD700] text-[#FFD700] bg-transparent hover:bg-[#FFD700]/10 transition-colors text-xs font-bold rounded cursor-pointer"
            >
              {show3D ? 'DISMOUNT 3D CANVAS (VRAM SAVE)' : 'MOUNT 3D CANVAS'}
            </button>
          </div>
        </section>

        {/* Center Column: 3D Visualization Spatial Canvas */}
        <section className="relative flex flex-col border border-[#00E5FF]/20 bg-black rounded-lg overflow-hidden min-h-[300px]">
          <h2 className="absolute top-4 left-4 z-10 text-xs font-bold tracking-widest bg-black/80 px-2 py-1 rounded border border-[#00E5FF]/30">
            🌌 SPATIAL PREVIEW (L0)
          </h2>
          {show3D ? (
            <div className="w-full h-full">
              <Canvas camera={{ position: [0, 0, 8] }}>
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 5, 5]} />
                <EmpireGlobe />
                <OrbitControls enableZoom={true} />
                <VramGovernor />
              </Canvas>
            </div>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-xs text-[#FFD700] bg-[#12121A]/20">
              [ 3D SPATIAL CANVAS DEALLOCATED VIA SIR_BORIS PROTOCOL ]
            </div>
          )}
        </section>

        {/* Right Column: OmniTerminal Log Output */}
        <section className="flex flex-col gap-4 border border-[#00E5FF]/20 bg-[#12121A]/50 p-4 rounded-lg">
          <h2 className="text-sm font-bold tracking-widest border-b border-[#00E5FF]/20 pb-2 text-[#FFD700]">
            ⚡ KINETIC FEED
          </h2>
          <div className="flex-1 overflow-y-auto bg-black/60 p-3 rounded border border-[#00E5FF]/10 font-mono text-xs flex flex-col gap-1">
            {messages.length === 0 ? (
              <div className="text-[#00E5FF]/40">[ Listening to Bifrost conduit... ]</div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className="whitespace-pre-wrap">
                  <span className="text-[#FFD700]">&gt;</span> {msg}
                </div>
              ))
            )}
          </div>
          <input
            type="text"
            placeholder="Execute system rune..."
            className="w-full bg-black border border-[#00E5FF]/30 rounded px-3 py-2 text-xs text-[#00E5FF] focus:outline-none focus:border-[#FFD700] placeholder:text-[#00E5FF]/30"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.currentTarget.value) {
                const val = e.currentTarget.value;
                setMessages((prev) => [...prev, val]);
                e.currentTarget.value = '';
              }
            }}
          />
        </section>
      </main>

      {/* Footer bar */}
      <footer className="border-t border-[#00E5FF]/10 px-6 py-2 text-center text-[10px] text-[#00E5FF]/40 bg-[#05050A]">
        EXCALIBUR STANDARD PWA • OFFLINE CONDUIT ACTIVE • SCARCITY RUNTIME ENFORCED
      </footer>
    </div>
  );
}
