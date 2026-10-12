import type { TrustBand } from './bifrost-envelope';

/**
 * FFI timeout/failure policy — Bifrost spec.
 * Timeouts are transient (1 retry, degrade to review); compute failures are
 * contract-level (no retry, review/block by risk); version mismatch fails closed.
 */

export type FfiError =
  | 'ffi_timeout'
  | 'ffi_compute_failed'
  | 'ffi_transport_failed'
  | 'ffi_invalid_input'
  | 'ffi_version_mismatch'
  | 'ffi_batch_too_large';

export interface FfiPolicyOutcome {
  retry: 'once' | 'none' | 'split_and_requeue';
  fallback: 'review' | 'review_or_block' | 'reject' | 'fail_closed' | 'requeue';
}

export const FFI_POLICY: Record<FfiError, FfiPolicyOutcome> = {
  ffi_timeout: { retry: 'once', fallback: 'review' },
  ffi_compute_failed: { retry: 'none', fallback: 'review_or_block' },
  ffi_transport_failed: { retry: 'once', fallback: 'review' },
  ffi_invalid_input: { retry: 'none', fallback: 'reject' },
  ffi_version_mismatch: { retry: 'none', fallback: 'fail_closed' },
  ffi_batch_too_large: { retry: 'split_and_requeue', fallback: 'requeue' },
};

/**
 * Conservative trust degradation on FFI failure:
 * allow/warn + timeout → review; review stays review; block/quarantine unchanged.
 */
export function degradeTrustBand(current: TrustBand, error: FfiError, highRisk = false): TrustBand {
  if (current === 'block' || current === 'quarantine') return current;
  if (error === 'ffi_version_mismatch') return 'block'; // fail closed
  if (error === 'ffi_invalid_input') return current; // batch rejected, band untouched
  if (error === 'ffi_compute_failed') return highRisk ? 'block' : 'review';
  // timeout / transport / oversize after retry exhaustion
  return 'review';
}

/**
 * Tailscale sidecar health automation — spec:
 * health_ok→proceed, health_degraded→review_only, health_failed→no_grant,
 * route_ready→advertise, route_lost→block new grants + mark degraded.
 */
export type SidecarHealth = 'ok' | 'degraded' | 'failed';

export interface SidecarStatus {
  health: SidecarHealth;
  routeReady: boolean;
}

export interface SidecarAdvisory {
  scoring: 'proceed' | 'review_only' | 'no_grant';
  advertise: boolean;
  blockNewGrants: boolean;
}

export function evaluateSidecar(status: SidecarStatus): SidecarAdvisory {
  const scoring =
    status.health === 'ok' ? 'proceed' : status.health === 'degraded' ? 'review_only' : 'no_grant';
  return {
    scoring,
    advertise: status.routeReady && status.health !== 'failed',
    blockNewGrants: !status.routeReady || status.health === 'failed',
  };
}
