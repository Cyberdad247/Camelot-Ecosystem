import { BifrostEnvelope, QueuePriority, verifyEnvelope, VerifyOptions } from './bifrost-envelope';

/**
 * Bifrost bounded async queues — spec:
 * critical bypasses batching only if signed+eligible; high blocks on full;
 * normal delays; low sheds; sustained overflow degrades; persistent quarantines.
 * Partitioned by session/node, ordering preserved within a partition,
 * quarantine/revocation processed before ordinary telemetry.
 */

export type QueueAudit =
  | 'queue.bypass_used'
  | 'queue.backpressure_applied'
  | 'queue.delayed'
  | 'queue.shed'
  | 'queue.dead_letter'
  | 'queue_overflow'
  | 'queue_overflow_critical';

export interface QueueItem {
  envelope: BifrostEnvelope;
  partition: string;
  enqueuedAt: number;
}

export interface EnqueueResult {
  accepted: boolean;
  bypass: boolean;
  audit?: QueueAudit;
  reason: string;
}

const PRIORITY_ORDER: QueuePriority[] = ['critical', 'high', 'normal', 'low'];
const BYPASS_ELIGIBLE_TYPES = new Set(['quarantine', 'revoke', 'sovereign_interrupt']);

export class BifrostQueue {
  private partitions = new Map<string, QueueItem[]>();
  readonly deadLetter: { envelope: BifrostEnvelope; reason: string }[] = [];
  readonly auditLog: { audit: QueueAudit; msg_id: string; ts: string }[] = [];
  private overflowStrikes = 0;

  constructor(
    private readonly capacity: number,
    private readonly verifyOpts: VerifyOptions,
    private readonly overflowStrikeLimit = 3
  ) {}

  get size(): number {
    let n = 0;
    for (const items of this.partitions.values()) n += items.length;
    return n;
  }

  get degraded(): boolean {
    return this.overflowStrikes >= 1;
  }

  get persistentOverflow(): boolean {
    return this.overflowStrikes >= this.overflowStrikeLimit;
  }

  private audit(audit: QueueAudit, msg_id: string) {
    this.auditLog.push({ audit, msg_id, ts: new Date().toISOString() });
  }

  /**
   * Bypass eligibility — spec validation steps: verify signature+checksum
   * (canonicalized header), nonce freshness, priority class, type eligibility,
   * and a policy_decision that allows direct execution.
   */
  canBypass(envelope: BifrostEnvelope): { eligible: boolean; reason: string } {
    const h = envelope.header;
    if (h.priority !== 'critical') return { eligible: false, reason: 'not critical class' };
    if (!BYPASS_ELIGIBLE_TYPES.has(h.type)) return { eligible: false, reason: `type ${h.type} not bypass-eligible` };
    const v = verifyEnvelope(envelope, this.verifyOpts);
    if (!v.valid) return { eligible: false, reason: v.reasons.join('; ') };
    if (h.policy_decision !== 'allow_direct') return { eligible: false, reason: 'policy_decision does not allow direct execution' };
    return { eligible: true, reason: 'signed critical event, bypass granted' };
  }

  enqueue(envelope: BifrostEnvelope, partition: string): EnqueueResult {
    const h = envelope.header;
    const atCapacity = this.size >= this.capacity;

    if (atCapacity) {
      // Critical: never dropped — bypass if signed+eligible, otherwise force-enqueue.
      if (h.priority === 'critical') {
        const bypass = this.canBypass(envelope);
        if (bypass.eligible) {
          this.audit('queue.bypass_used', h.msg_id);
          return { accepted: true, bypass: true, audit: 'queue.bypass_used', reason: bypass.reason };
        }
        this.push(envelope, partition);
        this.strike();
        return { accepted: true, bypass: false, audit: 'queue_overflow', reason: 'critical force-enqueued at capacity' };
      }
      if (h.priority === 'high') {
        this.audit('queue.backpressure_applied', h.msg_id);
        this.strike();
        return { accepted: false, bypass: false, audit: 'queue.backpressure_applied', reason: 'block until space available' };
      }
      if (h.priority === 'normal') {
        this.audit('queue.delayed', h.msg_id);
        return { accepted: false, bypass: false, audit: 'queue.delayed', reason: 'delayed / retry with backoff' };
      }
      // low: shed to dead-letter for audit
      this.deadLetter.push({ envelope, reason: 'shed at capacity' });
      this.audit('queue.shed', h.msg_id);
      return { accepted: false, bypass: false, audit: 'queue.shed', reason: 'low priority shed' };
    }

    this.push(envelope, partition);
    return { accepted: true, bypass: false, reason: 'enqueued' };
  }

  private push(envelope: BifrostEnvelope, partition: string) {
    const items = this.partitions.get(partition) ?? [];
    items.push({ envelope, partition, enqueuedAt: Date.now() });
    this.partitions.set(partition, items);
  }

  private strike() {
    this.overflowStrikes += 1;
    this.audit(this.persistentOverflow ? 'queue_overflow_critical' : 'queue_overflow', 'system');
  }

  /**
   * Drain in priority order (quarantine/revoke first via critical class),
   * preserving FIFO ordering within each partition.
   */
  drain(max = Infinity): QueueItem[] {
    const out: QueueItem[] = [];
    for (const priority of PRIORITY_ORDER) {
      for (const [partition, items] of this.partitions) {
        const keep: QueueItem[] = [];
        for (const item of items) {
          if (item.envelope.header.priority === priority && out.length < max) out.push(item);
          else keep.push(item);
        }
        this.partitions.set(partition, keep);
      }
    }
    return out;
  }
}
