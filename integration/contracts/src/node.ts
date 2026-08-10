// Mesh node contracts (Phase 4A) — mirrors integration/gateway/nodes.go.
//
// THE RULE: Tailscale makes a node reachable; it does not make it trusted or
// authorized. Trust is a band the gateway assigns; authorization is a
// short-lived node/tenant/capability-scoped lease the gateway mints and the
// node re-validates. Nothing in this file is ever asserted by a node about
// itself — these are the gateway's answers.

/** Assigned by the gateway. A node never claims its own band. */
export type NodeTrustBand = 'pending' | 'limited' | 'trusted' | 'degraded' | 'revoked';

export type NodeHealthState = 'healthy' | 'degraded' | 'offline';

export interface NodeCapability {
  name: string;
  /** Read-only capabilities may be served by limited-trust nodes. */
  readOnly: boolean;
}

export interface NodeIdentity {
  nodeId: string;
  tenantId: string;
  displayName: string;
  /** SHA-256 of the node's enrolment secret; the secret never leaves the node. */
  keyFingerprint: string;
}

export interface NodeRegistration {
  identity: NodeIdentity;
  capabilities: NodeCapability[];
  agentVersion: string;
  /** Where the gateway dispatches jobs. Never surfaced to the UI or audit. */
  dispatchUrl: string;
}

export interface NodeHealth {
  nodeId: string;
  status: NodeHealthState;
  backend?: string;
  meshReachable: boolean;
  meshBackend?: string;
  activeJobs: number;
  reportedAt: string;
}

/** What GET /v1/nodes returns: no address, no key, no secret — by design. */
export interface NodeView {
  nodeId: string;
  tenantId: string;
  displayName: string;
  trust: NodeTrustBand;
  health: NodeHealthState;
  local: boolean;
  capabilities: NodeCapability[];
  agentVersion: string;
  meshBackend?: string;
  lastSeen: string;
  /** Truncated hash of the dispatch address: distinguishes nodes, reaches none. */
  addressHash: string;
  revocationReason?: string;
}

export interface NodeJobRequest {
  sessionId?: string;
  turnId?: string;
  tenantId: string;
  capability: string;
  payload?: unknown;
  /** Ask for the mesh explicitly. Absent, routing stays local-first. */
  preferRemote?: boolean;
  nodeId?: string;
  /** Effectful jobs are never retried and never re-run locally after a
   *  remote attempt — the remote side may already have applied them. */
  effectful?: boolean;
}

export interface NodeRouteDecision {
  requestId: string;
  target: 'local' | 'remote' | 'none';
  nodeId?: string;
  capability: string;
  reason: string;
  fallback: boolean;
}

export interface NodeJobOutcome {
  decision: NodeRouteDecision;
  result?: unknown;
  auditId: string;
  failure?: string;
}

export interface NodeRevocation {
  nodeId: string;
  reason: string;
  at: string;
}

/** True when a node may currently be offered work at all. */
export function nodeIsServiceable(node: NodeView): boolean {
  return (node.trust === 'trusted' || node.trust === 'limited') && node.health === 'healthy';
}

/** Plain-language explanation of a node's current standing, for the panel. */
export function nodeStandingLabel(node: NodeView): string {
  switch (node.trust) {
    case 'trusted':
      return node.health === 'healthy' ? 'trusted · ready' : `trusted · ${node.health}`;
    case 'limited':
      return node.health === 'healthy' ? 'limited · read-only work' : `limited · ${node.health}`;
    case 'pending':
      return 'pending · awaiting your approval';
    case 'degraded':
      return 'degraded · heartbeat stale, no new jobs';
    case 'revoked':
      return `revoked${node.revocationReason ? ` · ${node.revocationReason}` : ''}`;
  }
}

/** One-line explanation of where a job ran and why. */
export function routeExplanation(decision: NodeRouteDecision): string {
  if (decision.target === 'none') return `no route · ${decision.reason}`;
  const where = decision.target === 'local' ? 'local node' : `remote node ${decision.nodeId}`;
  return decision.fallback
    ? `${where} (fallback) · ${decision.reason}`
    : `${where} · ${decision.reason}`;
}
