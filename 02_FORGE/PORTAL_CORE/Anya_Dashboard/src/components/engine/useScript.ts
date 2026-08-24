// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';

// Feature 9: Scripting Interface
// Allows JSON-defined behavior to drive 3D objects
export const useScript = (scriptName: string, config: any) => {
  const ref = useRef<THREE.Group>(null);

  useFrame((state, delta) => {
    if (!ref.current) return;

    // Example Script: ROTATOR
    if (scriptName === 'ROTATOR') {
      ref.current.rotation.y += delta * (config.speed || 1);
    }

    // Example Script: HOVER
    if (scriptName === 'HOVER') {
      ref.current.position.y = Math.sin(state.clock.elapsedTime) * (config.amplitude || 1);
    }
  });

  return ref;
};