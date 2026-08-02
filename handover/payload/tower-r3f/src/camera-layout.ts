import { FLOORS, FLOOR_GAP, TOWER_TOP_Y, phaseAt, PhaseId } from './tower-data';

/**
 * Camera layout resolution — sealed glyph contract:
 *   s: resolve breakpoint from aspect; merge basePath + floor override +
 *      viewport scale; output path, fov, near, far, framingBias; reuse the
 *      one progress scalar for camera and floor phases.
 *   m: basePath canonical · floorLayouts keyed by floorId · breakpoints map ·
 *      pure resolver · deterministic merge order.
 *   e: no side effects; camera.aspect updated elsewhere; minimize overrides.
 */

export type Breakpoint = 'mobile' | 'tablet' | 'desktop' | 'ultrawide';

/** Canonical camera path — every breakpoint and override is a delta on this. */
export const BASE_PATH = {
  angleStart: -Math.PI / 4,
  sweep: Math.PI * 1.5,
  heightOffset: 1.6,
  near: 0.1,
  far: 80
} as const;

export interface BreakpointLayout {
  fov: number;
  baseRadius: number;
  /** Extra radius added as the tower widens toward the foundation (× progress). */
  radiusGrowth: number;
  /** Vertical look-at bias (world units): positive raises the focus so bottom
   *  chrome never covers the active floor. */
  framingBias: number;
  /** Uniform scale applied to the merged radius — viewport scale. */
  viewportScale: number;
}

export const BREAKPOINTS: Record<Breakpoint, BreakpointLayout> = {
  mobile:    { fov: 62, baseRadius: 8.6, radiusGrowth: 1.4, framingBias: 0.9,  viewportScale: 1.0 },
  tablet:    { fov: 52, baseRadius: 7.8, radiusGrowth: 1.3, framingBias: 0.4,  viewportScale: 1.0 },
  desktop:   { fov: 45, baseRadius: 7.2, radiusGrowth: 1.2, framingBias: 0.0,  viewportScale: 1.0 },
  ultrawide: { fov: 40, baseRadius: 7.2, radiusGrowth: 1.2, framingBias: 0.0,  viewportScale: 1.15 }
};

export function breakpointFor(width: number, height: number): Breakpoint {
  const aspect = width / height;
  if (aspect < 0.8) return 'mobile';
  if (aspect < 1.2) return 'tablet';
  if (aspect < 2.1) return 'desktop';
  return 'ultrawide';
}

/** Per-floor camera deltas, keyed by floorId. Kept minimal by contract. */
export interface FloorLayout {
  radius?: number;
  height?: number;
  angle?: number;
}

export const FLOOR_LAYOUTS: Record<string, FloorLayout> = {
  envelope:  { height: 0.8 },              // arrive slightly above the crown
  yggdrasil: { radius: 1.3, height: -0.7 } // reverence shot: wide and low at the foundation
};

export interface CameraPath {
  angle: number;
  radius: number;
  x: number;
  y: number;
  z: number;
  focusY: number;
}

export interface ResolvedCameraLayout {
  breakpoint: Breakpoint;
  phase: PhaseId;
  activeFloor: number;
  path: CameraPath;
  fov: number;
  near: number;
  far: number;
  framingBias: number;
}

/** Phase modifiers — transition behavior as data, reusing the same progress scalar. */
function applyPhase(phase: PhaseId, working: { radius: number; heightOffset: number; focusY: number }, progress: number) {
  if (phase === 'arrival') {
    const t = progress / 0.06;
    working.radius += (1 - t) * 3.2;
    working.heightOffset += (1 - t) * 1.4;
  } else if (phase === 'foundation') {
    const t = (progress - 0.92) / 0.08;
    working.heightOffset -= t * 1.6;
    working.focusY += t * 0.9;
  }
}

/**
 * Pure resolver. Deterministic merge order:
 *   1. breakpoint base   2. floor override (by floorId)
 *   3. viewport scale    4. phase modifier
 * No side effects; camera.aspect is the renderer's concern.
 */
export function resolveCameraLayout(width: number, height: number, progress: number): ResolvedCameraLayout {
  const p = Math.min(1, Math.max(0, progress));
  const breakpoint = breakpointFor(width, height);
  const bp = BREAKPOINTS[breakpoint];
  const phase = phaseAt(p);

  const lastIndex = FLOORS.length - 1;
  const activeFloor = Math.min(lastIndex, Math.round(p * lastIndex));
  const override = FLOOR_LAYOUTS[FLOORS[activeFloor].id] ?? {};

  const working = {
    radius: (bp.baseRadius + p * bp.radiusGrowth + (override.radius ?? 0)) * bp.viewportScale,
    heightOffset: BASE_PATH.heightOffset + (override.height ?? 0),
    focusY: TOWER_TOP_Y - p * (lastIndex * FLOOR_GAP)
  };
  applyPhase(phase, working, p);

  const angle = BASE_PATH.angleStart + p * BASE_PATH.sweep + (override.angle ?? 0);

  return {
    breakpoint,
    phase,
    activeFloor,
    path: {
      angle,
      radius: working.radius,
      x: Math.cos(angle) * working.radius,
      y: working.focusY + working.heightOffset,
      z: Math.sin(angle) * working.radius,
      focusY: working.focusY
    },
    fov: bp.fov,
    near: BASE_PATH.near,
    far: BASE_PATH.far,
    framingBias: bp.framingBias
  };
}
