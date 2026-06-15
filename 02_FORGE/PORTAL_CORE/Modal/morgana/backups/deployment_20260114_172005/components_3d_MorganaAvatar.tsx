"use client";
import React, { useRef, useMemo, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial, Float, Stars, Html } from "@react-three/drei";
import * as THREE from "three";

interface MorganaAvatarProps {
  mode?: "IDLE" | "RESEARCH" | "DEV" | "MUSIC" | "ANALYSIS";
  onError?: (error: Error) => void;
  requestId?: string;
}

interface ModeColors {
  IDLE: string;
  RESEARCH: string;
  DEV: string;
  MUSIC: string;
  ANALYSIS: string;
}

const MODE_COLORS: ModeColors = {
  IDLE: "#D4AF37",
  RESEARCH: "#00F0FF", 
  DEV: "#10B981",
  MUSIC: "#8B5CF6",
  ANALYSIS: "#F59E0B"
};

interface LivingCoreProps {
  mode: keyof ModeColors;
  onError?: (error: Error) => void;
}

function LivingCore({ mode, onError }: LivingCoreProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [error, setError] = useState<Error | null>(null);
  
  const color = useMemo(() => MODE_COLORS[mode] || MODE_COLORS.IDLE, [mode]);
  
  useFrame((state) => {
    try {
      const t = state.clock.getElapsedTime();
      if(meshRef.current) {
          const material = meshRef.current.material as THREE.MeshStandardMaterial;
          material.distort = 0.4 + Math.sin(t) * 0.2;
          meshRef.current.rotation.x = t * 0.1;
          meshRef.current.rotation.y = t * 0.15;
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      onError?.(error);
    }
  });

  if (error) {
    return (
      <Html center>
        <div className="bg-red-900/80 text-white p-4 rounded">
          <p>3D Rendering Error</p>
          <p className="text-sm">{error.message}</p>
        </div>
      </Html>
    );
  }

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <Sphere args={[1, 64, 64]} ref={meshRef} scale={1.2}>
        <MeshDistortMaterial 
            color={color} 
            envMapIntensity={1} 
            clearcoat={1} 
            clearcoatRoughness={0.1} 
            metalness={0.1} 
            roughness={0.2}
        />
      </Sphere>
    </Float>
  );
}

function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      setHasError(true);
      setError(new Error(event.message));
    };
    
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return (
      <div className="w-full h-64 bg-black/80 flex items-center justify-center border border-red-500">
        <div className="text-red-400 text-center">
          <h3>Rendering Error</h3>
          <p className="text-sm">{error?.message || "Unknown error"}</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export default function MorganaAvatar({ mode = "IDLE", onError, requestId }: MorganaAvatarProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isHealthy, setIsHealthy] = useState(true);
  const [lastCheck, setLastCheck] = useState<string>(new Date().toLocaleTimeString());
  const [dimensions, setDimensions] = useState({ width: 800, height: 256 });

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: Math.max(256, window.innerHeight * 0.3)
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Heartbeat Logic
  useEffect(() => {
    const checkHealth = async () => {
      try {
        // Logic would point to the health endpoint deployed via Modal
        setLastCheck(new Date().toLocaleTimeString());
        setIsHealthy(true);
      } catch (err) {
        setIsHealthy(false);
      }
    };
    
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const handleCanvasError = (error: Error) => {
    console.error("Canvas rendering error:", error);
    onError?.(error);
  };

  return (
    <ErrorBoundary>
      <div className="w-full h-64 relative bg-black/80 border-b border-[#D4AF37]/20 overflow-hidden min-h-[200px]">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
            <div className="text-[#D4AF37] animate-pulse">Loading Morgana...</div>
          </div>
        )}
        
        <Canvas 
          camera={{ position: [0, 0, 3] }}
          gl={{ antialias: true, alpha: true }}
          dpr={[1, 2]}
          onCreated={() => setIsLoading(false)}
          onError={handleCanvasError}
        >
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1.5} color="#fff" />
          <LivingCore mode={mode} onError={handleCanvasError} />
          <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />
        </Canvas>
        
        <div className="absolute bottom-2 right-4 text-[10px] font-mono text-[#D4AF37] tracking-widest opacity-80 bg-black/50 px-2 py-1 rounded">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></span>
            MORGANA_Omega_PROD // STATUS: {mode}
          </div>
          {requestId && <span className="text-[8px]">REQ: {requestId.slice(-8)}</span>}
          <div className="text-[7px] opacity-50">LST_CHK: {lastCheck}</div>
        </div>
      </div>
    </ErrorBoundary>
  );
}