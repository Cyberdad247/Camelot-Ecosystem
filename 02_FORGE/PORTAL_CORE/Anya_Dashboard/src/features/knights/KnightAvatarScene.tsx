import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { useKnightStream } from './useKnightStream';
import VideoAvatar from './VideoAvatar';

/**
 * Knight -> accent colour. Keys are the EXACT lowercase names broadcast by
 * go_router's knightRoster in main.go: anya, merlin, codex, hashimoto, boris,
 * helios. Do not use display names like "SIR_CODEX" here — the SSE payload is
 * lowercase and would never match.
 */
const KNIGHT_COLORS: Record<string, string> = {
  anya: '#e879f9',
  merlin: '#818cf8',
  codex: '#34d399',
  hashimoto: '#fbbf24',
  boris: '#f87171',
  helios: '#fde047',
};
const IDLE_COLOR = '#475569';

/*
 * AVATAR ASSET PATHS (both optional — the scene works with neither present):
 *   - Video:  public/videos/<knight>_idle.mp4   (handled by VideoAvatar)
 *   - VRM:    public/avatars/<knight>.vrm        (future; needs @pixiv/three-vrm
 *             + VRMUtils.deepDispose on cleanup to free textures, not just geo)
 * Use the SAME lowercase keys as KNIGHT_COLORS. With no asset present,
 * VideoAvatar renders the procedural KnightFigure fallback.
 */

interface KnightAvatarSceneProps {
  /** Override the active knight; defaults to the live SSE stream. */
  activeKnight?: string | null;
}

export default function KnightAvatarScene({ activeKnight }: KnightAvatarSceneProps) {
  const stream = useKnightStream();
  const knight = activeKnight ?? stream.activeKnight?.knight ?? null;
  const color = useMemo(
    () => (knight ? (KNIGHT_COLORS[knight] ?? IDLE_COLOR) : IDLE_COLOR),
    [knight],
  );

  return (
    <div className="relative h-full w-full overflow-hidden rounded-xl border border-slate-800/60 bg-[#05060c]">
      <div className="absolute left-3 top-3 z-10 font-mono text-[11px] text-slate-400">
        <span className="uppercase tracking-widest text-slate-600">active</span>{' '}
        <span style={{ color }} className="capitalize">
          {knight ?? 'idle'}
        </span>
      </div>
      <Canvas camera={{ position: [0, 0.6, 3.2], fov: 42 }} dpr={[1, 2]}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[3, 4, 3]} intensity={1.1} />
        <pointLight position={[-3, 1, 2]} intensity={0.4} color={color} />
        <VideoAvatar knight={knight} color={color} />
      </Canvas>
    </div>
  );
}
