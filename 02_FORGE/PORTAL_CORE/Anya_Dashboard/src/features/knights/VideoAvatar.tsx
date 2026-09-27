import { useFrame } from '@react-three/fiber';
import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import type { Mesh } from 'three';
import KnightFigure from './KnightFigure';

interface VideoAvatarProps {
  /** Lowercase knight name from the SSE stream (anya, merlin, ...). */
  knight: string | null;
  /** Accent colour for the procedural fallback. */
  color: string;
}

/**
 * Per-knight idle loop, by convention at public/videos/<knight>_idle.mp4.
 * Keys are the lowercase names broadcast by go_router — NOT display names.
 */
function videoUrlFor(knight: string | null): string {
  return `/videos/${knight ?? 'anya'}_idle.mp4`;
}

/**
 * Projects a per-knight MP4 loop onto a curved screen via THREE.VideoTexture
 * (built into three — no extra dependency). The texture and the underlying
 * HTMLVideoElement are created/disposed in the effect to avoid the known R3F
 * VideoTexture VRAM leak.
 *
 * GRACEFUL FALLBACK: until a real video actually decodes ('loadeddata'), or if
 * the file is missing / autoplay is blocked ('error'), the procedural
 * <KnightFigure> renders instead — so the scene is never blank. Drop a real
 * .mp4 at the path above and the video takes over automatically.
 */
export default function VideoAvatar({ knight, color }: VideoAvatarProps) {
  const meshRef = useRef<Mesh>(null);
  const [texture, setTexture] = useState<THREE.VideoTexture | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(false);

    const video = document.createElement('video');
    video.src = videoUrlFor(knight);
    video.crossOrigin = 'anonymous';
    video.loop = true;
    video.muted = true; // required for autoplay
    video.playsInline = true; // required for iOS Safari

    const onReady = () => {
      setReady(true);
      video.play().catch(() => setReady(false)); // autoplay blocked -> fallback
    };
    const onError = () => setReady(false);

    video.addEventListener('loadeddata', onReady);
    video.addEventListener('error', onError);
    video.load();

    const tex = new THREE.VideoTexture(video);
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.colorSpace = THREE.SRGBColorSpace;
    setTexture(tex);

    return () => {
      video.removeEventListener('loadeddata', onReady);
      video.removeEventListener('error', onError);
      video.pause();
      video.removeAttribute('src');
      video.load(); // force the browser to drop the video buffer
      tex.dispose(); // force WebGL to drop the VRAM
      setTexture(null);
    };
  }, [knight]);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.position.y = Math.sin(clock.getElapsedTime() * 2) * 0.05;
    }
  });

  if (!ready || !texture) {
    return <KnightFigure color={color} />;
  }

  return (
    <mesh ref={meshRef}>
      {/* Curved screen segment gives the 2D loop a 3D presence. */}
      <cylinderGeometry args={[1.4, 1.4, 1.9, 32, 1, true, -Math.PI / 4, Math.PI / 2]} />
      <meshBasicMaterial map={texture} side={THREE.DoubleSide} toneMapped={false} />
    </mesh>
  );
}
