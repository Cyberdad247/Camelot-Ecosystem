import { IntentRoute } from '../router/intent-router';
import { evaluatePolicy } from '../policy/policy-engine';
import { BifrostEnvelope, TrustBand, verifyEnvelope, VerifyOptions } from './bifrost-envelope';
import { HeimdallFsm } from './heimdall-fsm';

/**
 * Bifrost gateway — reconciles envelope verification, Heimdall node health,
 * and the intent policy engine into a single trust decision.
 * Reconciliation lattice per spec: quarantine > block > review > warn > allow;
 * unanimous allow → allow.
 */

const SEVERITY: Record<TrustBand, number> = {
  quarantine: 4,
  block: 3,
  review: 2,
  warn: 1,
  allow: 0
};

export function reconcileTrust(verdicts: TrustBand[]): TrustBand {
  if (verdicts.length === 0) return 'review';
  return verdicts.reduce((worst, v) => (SEVERITY[v] > SEVERITY[worst] ? v : worst), 'allow' as TrustBand);
}

export interface GatewayDecision {
  trust_band: TrustBand;
  proceed: boolean;
  requiresApproval: boolean;
  verdicts: { source: string; band: TrustBand; reason: string }[];
  route: IntentRoute;
}

export function gateIntent(
  route: IntentRoute,
  envelope: BifrostEnvelope,
  verifyOpts: VerifyOptions,
  heimdall: HeimdallFsm
): GatewayDecision {
  const verdicts: GatewayDecision['verdicts'] = [];

  // 1. Signed envelope verification
  const env = verifyEnvelope(envelope, verifyOpts);
  verdicts.push({ source: 'bifrost_envelope', band: env.valid ? env.trust_band : 'quarantine', reason: env.reasons.join('; ') });

  // 2. Heimdall node health
  const advisory = heimdall.sidecarAdvisory();
  const heimdallBand: TrustBand = advisory === 'proceed' ? 'allow' : advisory === 'review_only' ? 'review' : 'block';
  verdicts.push({ source: 'heimdall_fsm', band: heimdallBand, reason: `node=${heimdall.nodeId} state=${heimdall.state} advisory=${advisory}` });

  // 3. Intent policy engine
  const policy = evaluatePolicy(route);
  const policyBand: TrustBand = !policy.allowed ? 'block' : policy.route.requiresApproval ? 'review' : 'allow';
  verdicts.push({ source: 'policy_engine', band: policyBand, reason: policy.reason });

  const trust_band = reconcileTrust(verdicts.map(v => v.band));

  return {
    trust_band,
    proceed: trust_band === 'allow' || trust_band === 'warn',
    requiresApproval: trust_band === 'review',
    verdicts,
    route: policy.route
  };
}
