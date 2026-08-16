import { createHmac, createHash, randomUUID } from 'node:crypto';

/**
 * Bifrost signed message envelope — Camelot-OS trust plane.
 * Header fields per Ω_TITAN_BIFROST spec: ver, msg_id, trace_id, parent_id,
 * type, src, dst, realm, session, node, cartridge, operator, ts, nonce,
 * expires, seq, priority, trust_band, policy_decision, sig_alg, sig,
 * checksum_alg, checksum, provenance_ref.
 */

export type TrustBand = 'allow' | 'warn' | 'review' | 'block' | 'quarantine';
export type QueuePriority = 'critical' | 'high' | 'normal' | 'low';

export interface BifrostHeader {
  ver: string;
  msg_id: string;
  trace_id: string;
  parent_id?: string;
  type: string;
  src: string;
  dst: string;
  realm: string;
  session?: string;
  node: string;
  cartridge?: string;
  operator?: string;
  ts: string;
  nonce: string;
  expires: string;
  seq: number;
  priority: QueuePriority;
  trust_band: TrustBand;
  policy_decision?: string;
  sig_alg: 'hmac-sha256';
  sig?: string;
  checksum_alg: 'sha256';
  checksum?: string;
  provenance_ref?: string;
}

export interface BifrostEnvelope<T = unknown> {
  header: BifrostHeader;
  payload: T;
}

export interface EnvelopeVerification {
  valid: boolean;
  reasons: string[];
  trust_band: TrustBand;
}

const BIFROST_VER = '1.0';

function canonicalPayload(payload: unknown): string {
  return JSON.stringify(payload ?? null);
}

function headerSigningString(h: BifrostHeader): string {
  // Deterministic field order; sig and checksum excluded from their own inputs.
  return [
    h.ver,
    h.msg_id,
    h.trace_id,
    h.parent_id ?? '',
    h.type,
    h.src,
    h.dst,
    h.realm,
    h.session ?? '',
    h.node,
    h.cartridge ?? '',
    h.operator ?? '',
    h.ts,
    h.nonce,
    h.expires,
    String(h.seq),
    h.priority,
    h.trust_band,
    h.policy_decision ?? '',
    h.sig_alg,
    h.checksum_alg,
    h.checksum ?? '',
    h.provenance_ref ?? '',
  ].join('|');
}

export interface SealOptions {
  type: string;
  src: string;
  dst: string;
  realm: string;
  node: string;
  seq: number;
  secret: string;
  ttlMs?: number;
  session?: string;
  cartridge?: string;
  operator?: string;
  parentId?: string;
  traceId?: string;
  priority?: QueuePriority;
  trustBand?: TrustBand;
  policyDecision?: string;
  provenanceRef?: string;
}

export function sealEnvelope<T>(payload: T, opts: SealOptions): BifrostEnvelope<T> {
  const now = Date.now();
  const header: BifrostHeader = {
    ver: BIFROST_VER,
    msg_id: randomUUID(),
    trace_id: opts.traceId ?? randomUUID(),
    parent_id: opts.parentId,
    type: opts.type,
    src: opts.src,
    dst: opts.dst,
    realm: opts.realm,
    session: opts.session,
    node: opts.node,
    cartridge: opts.cartridge,
    operator: opts.operator,
    ts: new Date(now).toISOString(),
    nonce: randomUUID(),
    expires: new Date(now + (opts.ttlMs ?? 30_000)).toISOString(),
    seq: opts.seq,
    priority: opts.priority ?? 'normal',
    trust_band: opts.trustBand ?? 'allow',
    policy_decision: opts.policyDecision,
    sig_alg: 'hmac-sha256',
    checksum_alg: 'sha256',
    provenance_ref: opts.provenanceRef,
  };

  header.checksum = createHash('sha256').update(canonicalPayload(payload)).digest('hex');
  header.sig = createHmac('sha256', opts.secret).update(headerSigningString(header)).digest('hex');

  return { header, payload };
}

export interface VerifyOptions {
  secret: string;
  expectedVer?: string;
  seenNonces?: Set<string>;
  now?: number;
}

export function verifyEnvelope(env: BifrostEnvelope, opts: VerifyOptions): EnvelopeVerification {
  const reasons: string[] = [];
  const h = env.header;
  const now = opts.now ?? Date.now();

  // Version mismatch → fail closed (crystal: ffi.version_mismatch)
  if ((opts.expectedVer ?? BIFROST_VER) !== h.ver) {
    return { valid: false, reasons: ['version_mismatch: fail closed'], trust_band: 'block' };
  }

  // Expiry
  if (now > new Date(h.expires).getTime()) reasons.push('envelope expired');

  // Nonce replay
  if (opts.seenNonces) {
    if (opts.seenNonces.has(h.nonce)) reasons.push('nonce replay detected');
    else opts.seenNonces.add(h.nonce);
  }

  // Checksum (payload integrity)
  const checksum = createHash('sha256').update(canonicalPayload(env.payload)).digest('hex');
  if (checksum !== h.checksum) reasons.push('payload checksum mismatch');

  // Signature (header integrity + provenance)
  const expectedSig = createHmac('sha256', opts.secret)
    .update(headerSigningString(h))
    .digest('hex');
  if (expectedSig !== h.sig) reasons.push('invalid signature');

  const valid = reasons.length === 0;
  return {
    valid,
    reasons: valid ? ['signed envelope verified'] : reasons,
    trust_band: valid ? h.trust_band : 'quarantine',
  };
}
