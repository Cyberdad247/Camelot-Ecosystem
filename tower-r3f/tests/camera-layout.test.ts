import assert from 'node:assert/strict';
import { breakpointFor, resolveCameraLayout, BREAKPOINTS, BASE_PATH, FLOOR_LAYOUTS } from '../src/camera-layout';
import { FLOORS, phaseAt, TOWER_TOP_Y } from '../src/tower-data';

// ── Breakpoints (incl. ultrawide) ──────────────────────────────
assert.equal(breakpointFor(390, 844), 'mobile');
assert.equal(breakpointFor(820, 820), 'tablet');
assert.equal(breakpointFor(1920, 1080), 'desktop');
assert.equal(breakpointFor(3440, 1440), 'ultrawide');

// ── Phases: one progress scalar drives camera and floors ───────
assert.equal(phaseAt(0), 'arrival');
assert.equal(phaseAt(0.5), 'descent');
assert.equal(phaseAt(0.95), 'foundation');
assert.equal(phaseAt(-1), 'arrival');
assert.equal(phaseAt(2), 'foundation');
assert.equal(resolveCameraLayout(1920, 1080, 0.5).phase, phaseAt(0.5));

// ── Output contract: path, fov, near, far, framingBias ─────────
const mid = resolveCameraLayout(1920, 1080, 0.5);
assert.equal(mid.near, BASE_PATH.near);
assert.equal(mid.far, BASE_PATH.far);
assert.equal(mid.fov, BREAKPOINTS.desktop.fov);
assert.equal(typeof mid.framingBias, 'number');
assert.ok(Math.abs(mid.path.x - Math.cos(mid.path.angle) * mid.path.radius) < 1e-9);
assert.ok(Math.abs(mid.path.z - Math.sin(mid.path.angle) * mid.path.radius) < 1e-9);

// focusY descends monotonically with progress
let prevY = Infinity;
for (let p = 0; p <= 1.0001; p += 0.1) {
  const r = resolveCameraLayout(1920, 1080, p);
  assert.ok(r.path.focusY <= prevY + 1e-9, `focusY not descending at p=${p}`);
  prevY = r.path.focusY;
}

// ── Deterministic merge order: base → override → viewport scale ─
// Foundation (yggdrasil) override widens radius beyond plain base+growth
const foundationIdx = FLOORS.length - 1;
assert.equal(FLOORS[foundationIdx].id, 'yggdrasil');
assert.ok(FLOOR_LAYOUTS.yggdrasil.radius === 1.3);
const atFoundation = resolveCameraLayout(1920, 1080, 1);
const plainRadius = BREAKPOINTS.desktop.baseRadius + 1 * BREAKPOINTS.desktop.radiusGrowth;
assert.ok(atFoundation.path.radius > plainRadius, 'floor override not merged');

// Viewport scale applies AFTER override: ultrawide radius = (base+growth+override)×1.15
const uwFoundation = resolveCameraLayout(3440, 1440, 1);
// remove foundation-phase modifier influence by comparing pre-phase math directly:
const expectedUw = (BREAKPOINTS.ultrawide.baseRadius + 1 * BREAKPOINTS.ultrawide.radiusGrowth + 1.3) * BREAKPOINTS.ultrawide.viewportScale;
assert.ok(Math.abs(uwFoundation.path.radius - expectedUw) < 1e-9, 'merge order violated');

// ── Phase modifiers ────────────────────────────────────────────
const arrivalStart = resolveCameraLayout(1920, 1080, 0);
const arrivalEnd = resolveCameraLayout(1920, 1080, 0.06);
assert.ok(arrivalStart.path.radius > arrivalEnd.path.radius, 'arrival should ease inward');
const preFoundation = resolveCameraLayout(1920, 1080, 0.92);
assert.ok(atFoundation.path.y - atFoundation.path.focusY < preFoundation.path.y - preFoundation.path.focusY,
  'foundation phase should lower the camera relative to focus');

// ── Responsive framing ─────────────────────────────────────────
const mobile = resolveCameraLayout(390, 844, 0.5);
assert.ok(mobile.path.radius > mid.path.radius);
assert.ok(mobile.fov > mid.fov);
assert.ok(mobile.framingBias > mid.framingBias, 'portrait should bias focus upward');

// Purity: same inputs, same output (no side effects)
assert.deepEqual(resolveCameraLayout(1234, 777, 0.42), resolveCameraLayout(1234, 777, 0.42));

// Crown sanity
assert.equal(resolveCameraLayout(1920, 1080, 0).activeFloor, 0);
assert.ok(Math.abs(resolveCameraLayout(1920, 1080, 0).path.focusY - TOWER_TOP_Y) < 1e-9);

console.log('camera-layout tests passed (glyph contract).');
