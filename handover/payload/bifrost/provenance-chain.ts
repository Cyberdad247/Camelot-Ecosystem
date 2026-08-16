import { createHash, createHmac } from 'node:crypto';
import { BifrostEnvelope, TrustBand } from './bifrost-envelope';

/**
 * Provenance ledger append protocol — spec:
 * atomic append, prev_hash chained to latest committed record, never reorder,
 * buffer+retry on failure without claiming commit, quarantine/revocation
 * events appended before ordinary telemetry.
 */

export interface LedgerRecord {
  ledger_version: '1.0';
  event_id: string;
  trace_id: string;
  parent_event_id: string | null;
  msg_id: string;
  msg_type: string;
  src: string;
  dst: string;
  session_id: string | null;
  node_id: string | null;
  cartridge_id: string | null;
  operator_id: string | null;
  timestamp: string;
  trust_band: TrustBand;
  policy_decision: string;
  payload_hash: string;
  prev_hash: string | null;
  current_hash: string;
  signature: string;
  provenance_ref: string;
}

const PRIORITY_TYPES = new Set(['quarantine', 'revoke']);

function sha256(s: string): string {
  return createHash('sha256').update(s).digest('hex');
}

function recordHashInput(
  r: Omit<LedgerRecord, 'current_hash' | 'signature' | 'provenance_ref'>,
): string {
  return [
    r.ledger_version,
    r.event_id,
    r.trace_id,
    r.parent_event_id ?? '',
    r.msg_id,
    r.msg_type,
    r.src,
    r.dst,
    r.session_id ?? '',
    r.node_id ?? '',
    r.cartridge_id ?? '',
    r.operator_id ?? '',
    r.timestamp,
    r.trust_band,
    r.policy_decision,
    r.payload_hash,
    r.prev_hash ?? '',
  ].join('|');
}

export class ProvenanceChain {
  private records: LedgerRecord[] = [];
  private buffer: BifrostEnvelope[] = [];
  private seq = 0;

  constructor(
    private readonly signingSecret: string,
    private failNextAppend = false,
  ) {}

  get head(): LedgerRecord | undefined {
    return this.records[this.records.length - 1];
  }

  get length(): number {
    return this.records.length;
  }

  get bufferedCount(): number {
    return this.buffer.length;
  }

  /** Test hook: simulate a storage failure on the next append. */
  simulateFailure() {
    this.failNextAppend = true;
  }

  /**
   * Atomic append. On failure the envelope is buffered — no commit is claimed.
   * Returns provenance_ref on commit, null when buffered.
   */
  append(envelope: BifrostEnvelope): string | null {
    if (this.failNextAppend) {
      this.failNextAppend = false;
      this.buffer.push(envelope);
      return null;
    }

    const h = envelope.header;
    this.seq += 1;
    const base: Omit<LedgerRecord, 'current_hash' | 'signature' | 'provenance_ref'> = {
      ledger_version: '1.0',
      event_id: `evt_${this.seq.toString().padStart(8, '0')}`,
      trace_id: h.trace_id,
      parent_event_id: this.head?.event_id ?? null,
      msg_id: h.msg_id,
      msg_type: h.type,
      src: h.src,
      dst: h.dst,
      session_id: h.session ?? null,
      node_id: h.node ?? null,
      cartridge_id: h.cartridge ?? null,
      operator_id: h.operator ?? null,
      timestamp: new Date().toISOString(),
      trust_band: h.trust_band,
      policy_decision: h.policy_decision ?? 'none',
      payload_hash: sha256(JSON.stringify(envelope.payload ?? null)),
      prev_hash: this.head?.current_hash ?? null,
    };

    const current_hash = sha256(recordHashInput(base));
    const signature = createHmac('sha256', this.signingSecret)
      .update(current_hash)
      .digest('base64');
    const record: LedgerRecord = {
      ...base,
      current_hash,
      signature,
      provenance_ref: `ledger://camelot/${base.event_id}`,
    };
    this.records.push(record);
    return record.provenance_ref;
  }

  /** Retry buffered appends — quarantine/revocation events first, then FIFO. */
  retryBuffered(): number {
    const pending = [...this.buffer];
    this.buffer = [];
    pending.sort(
      (a, b) =>
        Number(PRIORITY_TYPES.has(b.header.type)) - Number(PRIORITY_TYPES.has(a.header.type)),
    );
    let committed = 0;
    for (const env of pending) {
      if (this.append(env) !== null) committed += 1;
    }
    return committed;
  }

  /** Yggdrasil Merkle root over all committed record hashes (crystal: prove.Yggdrasil_Merkle_root). */
  merkleRoot(): string | null {
    if (this.records.length === 0) return null;
    let level = this.records.map((r) => r.current_hash);
    while (level.length > 1) {
      const next: string[] = [];
      for (let i = 0; i < level.length; i += 2) {
        next.push(sha256(level[i] + (level[i + 1] ?? level[i])));
      }
      level = next;
    }
    return level[0];
  }

  /** provenance_audit spell: recompute every hash and verify the chain + HMACs. */
  verifyChain(): { valid: boolean; brokenAt: string | null } {
    let prev: string | null = null;
    for (const r of this.records) {
      if (r.prev_hash !== prev) return { valid: false, brokenAt: r.event_id };
      const { current_hash, signature, provenance_ref, ...base } = r;
      if (sha256(recordHashInput(base)) !== current_hash)
        return { valid: false, brokenAt: r.event_id };
      const expectedSig = createHmac('sha256', this.signingSecret)
        .update(current_hash)
        .digest('base64');
      if (expectedSig !== signature) return { valid: false, brokenAt: r.event_id };
      prev = current_hash;
    }
    return { valid: true, brokenAt: null };
  }
}
