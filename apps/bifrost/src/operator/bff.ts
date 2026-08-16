// SPDX-License-Identifier: MIT

import { Router, type Request, type Response } from 'express';
import { z } from 'zod';
import type { EventStore } from './receipts';
import type { EffectManifest, OperatorTaskSnapshot } from './contracts';
import type { VerifyContext, VerifyResult } from './sentinel';
import { FIXTURES, snapshotFor, type FixtureName } from './fixtures';

// Keys are stored lowercase so the case-insensitive match (`k.toLowerCase()`)
// actually hits camelCase keys like `apiKey` (design §8.3 redact_sensitive_fields).
const SENSITIVE_KEYS = new Set(['secret', 'token', 'password', 'apikey', 'authorization']);

export function redactSensitive(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(redactSensitive);
  if (value !== null && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(record)) {
      if (SENSITIVE_KEYS.has(k.toLowerCase())) {
        out[k] = '[REDACTED]';
      } else {
        out[k] = redactSensitive(v);
      }
    }
    return out;
  }
  return value;
}

const DecisionBodySchema = z
  .object({
    decision: z.enum(['approve', 'deny']),
    reason: z.string().max(2000).optional(),
  })
  .strict(); // .strict() rejects command/path/raw-diff smuggling (design §9)

export interface OperatorBffDeps {
  store: EventStore;
  verifyManifest: (manifest: EffectManifest, ctx: VerifyContext) => VerifyResult;
  issueLease: (manifestId: string, ttlMs?: number) => { leaseId: string };
  now: () => Date;
  requiredEvidencePresent: (ref: string) => boolean;
  gideonVerdict: () => 'pass' | 'fail' | 'pending' | 'unavailable';
  vfsEvidenceOk: () => boolean;
}

function authorize(req: Request): boolean {
  const token = req.header('x-operator-token');
  return Boolean(
    token && process.env.OPERATOR_SESSION_TOKEN && token === process.env.OPERATOR_SESSION_TOKEN,
  );
}

function auth(res: Response): void {
  res.status(401).json({ error: 'UNAUTHORIZED' });
}

/** Deterministic fixture snapshots driven by OPERATOR_FIXTURE_TASK
 * (defaults to the approval fixture). Fall back to the default fixture for
 * unknown task names rather than fabricating new state (design §18). */
function fixtureSnapshot(taskId: string): OperatorTaskSnapshot {
  const fixture = (process.env.OPERATOR_FIXTURE_TASK ?? 'operator-console-approval') as FixtureName;
  if (!FIXTURES.includes(fixture)) return snapshotFor(taskId, 'operator-console-approval');
  return snapshotFor(taskId, fixture);
}

export function createOperatorBff(deps: OperatorBffDeps): Router {
  const router = Router();

  router.get('/session', (_req, res) => {
    res.json({ authenticated: Boolean(process.env.OPERATOR_SESSION_TOKEN) });
  });

  router.get('/tasks/:taskId/snapshot', (req, res) => {
    if (!authorize(req)) return auth(res);
    const taskId = req.params.taskId as string;
    const snapshot = redactSensitive(fixtureSnapshot(taskId)) as OperatorTaskSnapshot;
    void deps.store.verifyChain(taskId);
    res.json(snapshot);
  });

  router.get('/tasks/:taskId/events', (req, res) => {
    if (!authorize(req)) return auth(res);
    const taskId = req.params.taskId as string;
    res.setHeader('content-type', 'text/event-stream');
    res.setHeader('cache-control', 'no-cache');
    res.setHeader('connection', 'keep-alive');
    res.flushHeaders();
    const first = redactSensitive(fixtureSnapshot(taskId)) as OperatorTaskSnapshot;
    res.write(
      `event: operator.evidence\ndata: ${JSON.stringify({ type: 'snapshot', payload: first })}\n\n`,
    );
    const timer = setInterval(() => res.write(': keepalive\n\n'), 15_000);
    req.on('close', () => clearInterval(timer));
  });

  router.post('/effect-manifests/:manifestId/decision', (req, res) => {
    if (!authorize(req)) return auth(res);
    const parsed = DecisionBodySchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: 'INVALID_DECISION_BODY', issues: parsed.error.issues });
    }
    const { decision, reason } = parsed.data;
    const manifestId = req.params.manifestId as string;

    if (decision === 'deny') {
      void deps.store.append({
        eventId: `evt_deny_${Date.now()}`,
        taskId: 'task_fixture',
        correlationId: 'cor_fixture',
        timestamp: new Date().toISOString(),
        actorId: 'sentinel',
        actorRole: 'sentinel',
        kind: 'decision.denied',
        payload: { manifestId, reason },
        integrity: 'verified',
      });
      return res.status(200).json({ status: 'DENIED', manifestId });
    }

    const manifest: EffectManifest = {
      schemaVersion: 'effect-manifest/1',
      manifestId,
      taskId: 'task_fixture',
      correlationId: 'cor_fixture',
      kind: 'worktree.patch.promote',
      baseRevision: 'base',
      candidateRevision: 'cand',
      diffSha256: 'sha256:abc',
      allowedPaths: ['apps/pwa/src/components/operator_console/**'],
      requiredEvidence: ['receipt://vfs/no-escape/1'],
      policyClass: 'engineering.write',
      expiresAt: new Date(deps.now().getTime() + 60_000).toISOString(),
      oneTimeNonce: `nonce_${Date.now()}`,
    };
    const verdict = deps.verifyManifest(manifest, {
      now: deps.now,
      seenNonces: new Set<string>(),
      requiredEvidencePresent: deps.requiredEvidencePresent,
      gideonVerdict: deps.gideonVerdict(),
      vfsEvidenceOk: deps.vfsEvidenceOk(),
    });
    if (!verdict.approved) {
      return res.status(403).json({ status: 'BLOCKED', reasons: verdict.reasons });
    }
    const lease = deps.issueLease(manifestId);
    void deps.store.append({
      eventId: `evt_approve_${Date.now()}`,
      taskId: 'task_fixture',
      correlationId: 'cor_fixture',
      timestamp: new Date().toISOString(),
      actorId: 'sentinel',
      actorRole: 'sentinel',
      kind: 'decision.approved',
      payload: { manifestId, leaseId: lease.leaseId },
      integrity: 'verified',
    });
    res.status(200).json({ status: 'APPROVED', manifestId, lease });
  });

  return router;
}
