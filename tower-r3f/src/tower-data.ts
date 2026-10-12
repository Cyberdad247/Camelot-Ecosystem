/** Single edit point for tower content and scroll phases. Camera concerns live in camera-layout.ts. */

export interface FloorSpec {
  /** Stable id — floorLayouts in camera-layout.ts key on this. */
  id: string;
  numeral: string;
  name: string;
  role: string;
  data: string;
}

/** Crown (index 0) to foundation — the real traversal order of the Bifrost trust plane. */
export const FLOORS: FloorSpec[] = [
  {
    id: 'envelope',
    numeral: 'VII',
    name: 'ENVELOPE SEAL',
    role: 'Every intent enters the tower wrapped in a canonical header — signed, checksummed, nonce-fresh.',
    data: 'hmac-sha256 · 24 fields · ver-mismatch fails closed',
  },
  {
    id: 'queue',
    numeral: 'VI',
    name: 'BOUNDED PASSAGE',
    role: 'Priority queues partitioned by session. Critical writs may bypass — only under a valid seal.',
    data: 'critical > high > normal > low · shed → dead-letter',
  },
  {
    id: 'gateway',
    numeral: 'V',
    name: 'THE GATEWAY',
    role: 'Three verdicts fuse into one: envelope truth, node health, sovereign policy.',
    data: 'quarantine > block > review > warn > allow',
  },
  {
    id: 'registration',
    numeral: 'IV',
    name: 'REGISTRATION GATE',
    role: 'No unproven node consumes scoring. Identity, sidecar, and preflight stand before the oracle is asked.',
    data: 'invalid nodes never score · x-realm reconciled',
  },
  {
    id: 'heimdall',
    numeral: 'III',
    name: 'HEIMDALL WATCH',
    role: 'Seven states of containment. Ragnarok isolates absolutely — recovery traffic alone may pass.',
    data: 'healthy → observed → suspect → quarantine → ragnarok',
  },
  {
    id: 'microfish',
    numeral: 'II',
    name: 'MICROFISH ORACLE',
    role: 'The tower watches its own pulse. Anomalies climb the sigma ladder and summon the Watch.',
    data: '2.5σ minor · 4σ major · 6σ critical → containment',
  },
  {
    id: 'ffi',
    numeral: 'I',
    name: 'FFI TRIBUNAL',
    role: 'Failure is judged conservatively. Timeouts earn review; broken contracts earn silence.',
    data: 'timeout → 1 retry → review · compute-fail → no retry',
  },
  {
    id: 'yggdrasil',
    numeral: 'Ω',
    name: 'YGGDRASIL LEDGER',
    role: 'The foundation. Every event chained to the last, rooted in one Merkle truth. Nothing reorders. Nothing is unwritten.',
    data: 'prev_hash chain · merkle root · quarantine appends first',
  },
];

export const FLOOR_GAP = 3.2;
export const TOWER_TOP_Y = (FLOORS.length - 1) * FLOOR_GAP;

/** Scroll phases in progress space [0..1]. */
export type PhaseId = 'arrival' | 'descent' | 'foundation';

export interface PhaseSpec {
  id: PhaseId;
  from: number;
  to: number;
}

export const PHASES: PhaseSpec[] = [
  { id: 'arrival', from: 0.0, to: 0.06 },
  { id: 'descent', from: 0.06, to: 0.92 },
  { id: 'foundation', from: 0.92, to: 1.0 },
];

export function phaseAt(progress: number): PhaseId {
  const p = Math.min(1, Math.max(0, progress));
  for (const phase of PHASES) {
    if (p >= phase.from && p <= phase.to) return phase.id;
  }
  return 'descent';
}
