import { HeimdallEvent, HeimdallFsm } from './heimdall-fsm';

/**
 * Microfish — predictive time-series engine (TS reference for the Rust cartridge).
 * Crystal spec: trend / anomaly / capacity. Anomaly signals feed the Heimdall
 * FSM so predictive detection drives containment instead of dashboards.
 */

export interface TrendReport {
  slope: number;          // units per sample
  direction: 'rising' | 'falling' | 'flat';
}

export interface AnomalyReport {
  zScore: number;
  severity: 'none' | 'minor' | 'major' | 'critical';
}

export interface CapacityReport {
  utilization: number;    // 0..1
  samplesToCapacity: number | null; // null when not trending toward limit
}

export class MicrofishSeries {
  private values: number[] = [];

  constructor(private readonly window = 32) {}

  push(value: number) {
    this.values.push(value);
    if (this.values.length > this.window) this.values.shift();
  }

  get size(): number {
    return this.values.length;
  }

  /** Least-squares slope over the window. */
  trend(): TrendReport {
    const n = this.values.length;
    if (n < 2) return { slope: 0, direction: 'flat' };
    const xMean = (n - 1) / 2;
    const yMean = this.values.reduce((a, b) => a + b, 0) / n;
    let num = 0, den = 0;
    for (let i = 0; i < n; i++) {
      num += (i - xMean) * (this.values[i] - yMean);
      den += (i - xMean) ** 2;
    }
    const slope = den === 0 ? 0 : num / den;
    const direction = Math.abs(slope) < 1e-9 ? 'flat' : slope > 0 ? 'rising' : 'falling';
    return { slope, direction };
  }

  /** Z-score of the latest sample against the prior window. */
  anomaly(): AnomalyReport {
    const n = this.values.length;
    if (n < 4) return { zScore: 0, severity: 'none' };
    const prior = this.values.slice(0, n - 1);
    const mean = prior.reduce((a, b) => a + b, 0) / prior.length;
    const variance = prior.reduce((a, b) => a + (b - mean) ** 2, 0) / prior.length;
    const std = Math.sqrt(variance);
    const z = std === 0 ? 0 : Math.abs((this.values[n - 1] - mean) / std);
    const severity = z >= 6 ? 'critical' : z >= 4 ? 'major' : z >= 2.5 ? 'minor' : 'none';
    return { zScore: z, severity };
  }

  /** Samples until `limit` is reached at the current trend, from the latest value. */
  capacity(limit: number): CapacityReport {
    const latest = this.values[this.values.length - 1] ?? 0;
    const utilization = limit === 0 ? 0 : Math.min(1, Math.max(0, latest / limit));
    const { slope } = this.trend();
    if (slope <= 0 || latest >= limit) {
      return { utilization, samplesToCapacity: latest >= limit ? 0 : null };
    }
    return { utilization, samplesToCapacity: Math.ceil((limit - latest) / slope) };
  }
}

const SEVERITY_EVENT: Record<Exclude<AnomalyReport['severity'], 'none'>, HeimdallEvent> = {
  minor: 'anomaly',
  major: 'anomaly_confirmed',
  critical: 'critical_breach'
};

/** Predictive → containment: dispatch the anomaly severity into Heimdall. */
export function feedHeimdall(report: AnomalyReport, fsm: HeimdallFsm): HeimdallEvent | null {
  if (report.severity === 'none') return null;
  const event = SEVERITY_EVENT[report.severity];
  fsm.dispatch(event);
  return event;
}
