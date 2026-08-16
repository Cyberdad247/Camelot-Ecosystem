import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import type { Group } from 'three';

/**
 * Procedural placeholder avatar (head + capsule body, slow auto-rotate).
 * Dependency-free and always renderable — used as the fallback whenever a real
 * video/VRM asset is missing. Colour is driven by the active knight.
 */
export default function KnightFigure({ color }: { color: string }) {
  const group = useRef<Group>(null);
  useFrame((_, delta) => {
    if (group.current) group.current.rotation.y += delta * 0.4;
  });

  return (
    <group ref={group} position={[0, -0.6, 0]}>
      <mesh position={[0, 1.12, 0]}>
        <sphereGeometry args={[0.32, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          roughness={0.3}
        />
      </mesh>
      <mesh position={[0, 0.35, 0]}>
        <capsuleGeometry args={[0.32, 0.7, 8, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.22}
          roughness={0.4}
          metalness={0.3}
        />
      </mesh>
    </group>
  );
}
