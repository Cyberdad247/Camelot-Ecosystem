import type { TrustBand } from './bifrost-envelope';
import { reconcileTrust } from './bifrost-gateway';
import { type FfiError, type SidecarStatus, degradeTrustBand, evaluateSidecar } from './ffi-policy';

/**
 * Bifrost registration gate — spec workflow:
 * Registration/trust lookup → sidecar health → preflight validation →
 * scoring eligible? → scoring execution → FFI outcome → trust reconciliation →
 * authorization → session grant or deny.
 * Invalid nodes never consume scoring capacity.
 */

export interface RegistrationRequest {
  nodeId: string;
  identityValid: boolean;
  schemaValid: boolean;
  sidecar: SidecarStatus;
  realmBands: TrustBand[];
  highRisk?: boolean;
}

export type ScoringFn = (nodeId: string) => { band: TrustBand } | { error: FfiError };

export interface GateResult {
  granted: boolean;
  finalBand: TrustBand;
  stage: 'registration' | 'sidecar' | 'preflight' | 'scoring' | 'reconciliation' | 'granted';
  scoringInvoked: boolean;
  notes: string[];
}

export function runRegistrationGate(req: RegistrationRequest, score: ScoringFn): GateResult {
  const notes: string[] = [];

  // 1. Registration must pass before scoring.
  if (!req.identityValid) {
    return {
      granted: false,
      finalBand: 'block',
      stage: 'registration',
      scoringInvoked: false,
      notes: ['identity validation failed'],
    };
  }

  // 2. Sidecar health must be green or degraded-but-allowed.
  const sidecar = evaluateSidecar(req.sidecar);
  if (sidecar.scoring === 'no_grant') {
    return {
      granted: false,
      finalBand: 'block',
      stage: 'sidecar',
      scoringInvoked: false,
      notes: ['sidecar failed: no scoring, no session grant'],
    };
  }
  if (sidecar.blockNewGrants) {
    return {
      granted: false,
      finalBand: 'block',
      stage: 'sidecar',
      scoringInvoked: false,
      notes: ['route lost: new grants blocked, node degraded'],
    };
  }
  if (sidecar.scoring === 'review_only') notes.push('sidecar degraded: review mode');

  // 3. Preflight validation must succeed before scoring is called.
  if (!req.schemaValid) {
    return {
      granted: false,
      finalBand: 'block',
      stage: 'preflight',
      scoringInvoked: false,
      notes: ['schema validation failed'],
    };
  }

  // 4–5. Scoring execution + FFI outcome (conservative degradation on failure).
  const outcome = score(req.nodeId);
  let scoringBand: TrustBand;
  if ('error' in outcome) {
    scoringBand = degradeTrustBand('allow', outcome.error, req.highRisk);
    notes.push(`ffi ${outcome.error} → degraded to ${scoringBand}`);
  } else {
    scoringBand = outcome.band;
  }

  // 6. Cross-realm trust reconciliation — most conservative wins.
  const sidecarBand: TrustBand = sidecar.scoring === 'review_only' ? 'review' : 'allow';
  const finalBand = reconcileTrust([scoringBand, sidecarBand, ...req.realmBands]);

  // 7. Authorization follows the reconciled band.
  const granted = finalBand === 'allow' || finalBand === 'warn';
  return {
    granted,
    finalBand,
    stage: granted ? 'granted' : 'reconciliation',
    scoringInvoked: true,
    notes: [...notes, `reconciled band: ${finalBand}`],
  };
}
