import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, useGLTF } from '@react-three/drei';
import { Physics, RigidBody } from '@react-three/rapier';
import { EffectComposer, Bloom, Vignette, Noise } from '@react-three/postprocessing';
import { useEngineStore } from '../../features/brain/engineStore';

export default function QuantumScene() {
  const objects = useEngineStore((state) => state.objects);

  return (
    <div className="h-full w-full bg-black">
      <Canvas shadows dpr={[1, 2]} gl={{ antialias: false }}>
        <Suspense fallback={null}>
          <ambientLight intensity={0.5} />
          <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} castShadow />
          <Environment preset="city" />
          <PerspectiveCamera makeDefault position={[0, 2, 10]} />
          <OrbitControls makeDefault />

          <Physics gravity={[0, -9.81, 0]}>
            <RigidBody type="fixed" position={[0, -1, 0]}>
              <mesh receiveShadow>
                <boxGeometry args={[20, 0.5, 20]} />
                <meshStandardMaterial color="#1a1a1a" roughness={0} metalness={0.8} />
              </mesh>
            </RigidBody>

            {/* Dynamic Objects from Brain */}
            {objects.map((obj) => (
              <RigidBody key={obj.id} position={obj.position} colliders="cuboid">
                <mesh castShadow>
                  <boxGeometry />
                  <meshStandardMaterial color={obj.color} emissive={obj.color} emissiveIntensity={1} />
                </mesh>
              </RigidBody>
            ))}
          </Physics>

          <EffectComposer>
            <Bloom luminanceThreshold={1} mipmapBlur intensity={1.5} />
            <Noise opacity={0.02} />
            <Vignette eskil={false} offset={0.1} darkness={1.1} />
          </EffectComposer>
        </Suspense>
      </Canvas>
    </div>
  );
}