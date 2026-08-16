/**
 * Heimdall node-health FSM — Bifrost quarantine/policy guardian.
 * States and guarantees per Ω_TITAN_BIFROST spec:
 *   healthy → observed → suspect → soft_quarantine → hard_quarantine → ragnarok → recovered
 * Ragnarok guarantee: no sessions, no commits, no upgrades, no forwarding — recovery traffic only.
 */

export type HeimdallState =
  | 'healthy'
  | 'observed'
  | 'suspect'
  | 'soft_quarantine'
  | 'hard_quarantine'
  | 'ragnarok'
  | 'recovered';

export type HeimdallEvent =
  | 'anomaly'
  | 'anomaly_confirmed'
  | 'threshold_breach'
  | 'critical_breach'
  | 'clear'
  | 'recovery_verified';

export interface HeimdallCapabilities {
  sessions: boolean;
  commits: boolean;
  upgrades: boolean;
  forward: boolean;
  recoveryOnly: boolean;
}

const TRANSITIONS: Record<HeimdallState, Partial<Record<HeimdallEvent, HeimdallState>>> = {
  healthy: { anomaly: 'observed', critical_breach: 'ragnarok' },
  observed: { anomaly_confirmed: 'suspect', clear: 'healthy', critical_breach: 'ragnarok' },
  suspect: { threshold_breach: 'soft_quarantine', clear: 'observed', critical_breach: 'ragnarok' },
  soft_quarantine: {
    threshold_breach: 'hard_quarantine',
    clear: 'suspect',
    critical_breach: 'ragnarok',
    recovery_verified: 'recovered',
  },
  hard_quarantine: { critical_breach: 'ragnarok', recovery_verified: 'recovered' },
  ragnarok: { recovery_verified: 'recovered' },
  recovered: { clear: 'healthy', anomaly: 'observed' },
};

export function capabilitiesFor(state: HeimdallState): HeimdallCapabilities {
  switch (state) {
    case 'healthy':
    case 'recovered':
      return { sessions: true, commits: true, upgrades: true, forward: true, recoveryOnly: false };
    case 'observed':
      return { sessions: true, commits: true, upgrades: false, forward: true, recoveryOnly: false };
    case 'suspect':
      return {
        sessions: true,
        commits: false,
        upgrades: false,
        forward: true,
        recoveryOnly: false,
      };
    case 'soft_quarantine':
      return {
        sessions: false,
        commits: false,
        upgrades: false,
        forward: true,
        recoveryOnly: false,
      };
    case 'hard_quarantine':
      return {
        sessions: false,
        commits: false,
        upgrades: false,
        forward: false,
        recoveryOnly: false,
      };
    case 'ragnarok':
      // Guarantee: no sessions/commits/upgrades/forward except recovery.
      return {
        sessions: false,
        commits: false,
        upgrades: false,
        forward: false,
        recoveryOnly: true,
      };
  }
}

export interface TransitionRecord {
  from: HeimdallState;
  event: HeimdallEvent;
  to: HeimdallState;
  ts: string;
}

export class HeimdallFsm {
  private _state: HeimdallState;
  readonly history: TransitionRecord[] = [];

  constructor(
    readonly nodeId: string,
    initial: HeimdallState = 'healthy',
  ) {
    this._state = initial;
  }

  get state(): HeimdallState {
    return this._state;
  }

  get capabilities(): HeimdallCapabilities {
    return capabilitiesFor(this._state);
  }

  dispatch(event: HeimdallEvent): HeimdallState {
    const next = TRANSITIONS[this._state][event];
    if (next) {
      this.history.push({ from: this._state, event, to: next, ts: new Date().toISOString() });
      this._state = next;
    }
    return this._state;
  }

  /** Sidecar advisory per crystal: ok→proceed, degraded→review_only, failed→no_grant */
  sidecarAdvisory(): 'proceed' | 'review_only' | 'no_grant' {
    if (this._state === 'healthy' || this._state === 'recovered') return 'proceed';
    if (this._state === 'observed' || this._state === 'suspect') return 'review_only';
    return 'no_grant';
  }
}
