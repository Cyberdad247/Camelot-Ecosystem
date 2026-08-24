// SPDX-License-Identifier: MIT

import { z } from 'zod';

// Client-side mirrors of the canonical Bifrost contracts
// (apps/bifrost/src/operator/contracts.ts). Drift is caught by the
// schemaVersion literals and the contract test in schemas.test.ts.

export const ActorRoleSchema = z.enum([
  'operator',
  'anya',
  'merlin',
  'hiveide',
  'nano_knight',
  'sentinel',
  'gideon',
  'boris',
  'herald',
  'system',
]);
export type ActorRole = z.infer<typeof ActorRoleSchema>;

export const EvidenceIntegritySchema = z.enum([
  'verified',
  'pending_anchor',
  'unavailable',
  'integrity_failed',
]);
export type EvidenceIntegrity = z.infer<typeof EvidenceIntegritySchema>;

export const ActorSchema = z.object({ id: z.string(), role: ActorRoleSchema });
export type Actor = z.infer<typeof ActorSchema>;

export const EvidenceEnvelopeSchema = z.object({
  schemaVersion: z.literal('operator-evidence/1'),
  eventId: z.string(),
  taskId: z.string(),
  correlationId: z.string(),
  causationId: z.string().optional(),
  timestamp: z.string(),
  actor: ActorSchema,
  kind: z.string(),
  payload: z.record(z.string(), z.unknown()),
  payloadHash: z.string(),
  parentHash: z.string().optional(),
  integrity: EvidenceIntegritySchema,
  receiptRef: z.string().optional(),
  ledgerAnchorRef: z.string().optional(),
});
export type EvidenceEnvelope = z.infer<typeof EvidenceEnvelopeSchema>;

export const DiffEvidenceSchema = z.object({
  baseRevision: z.string(),
  candidateRevision: z.string(),
  diffSha256: z.string(),
  changedPaths: z.array(z.string()),
  addedLines: z.number(),
  removedLines: z.number(),
  generatedAt: z.string(),
  gideonVerdict: z.enum(['pass', 'fail', 'pending', 'unavailable']),
  receiptRef: z.string().optional(),
});
export type DiffEvidence = z.infer<typeof DiffEvidenceSchema>;

export const TestRunResultSchema = z.object({
  schemaVersion: z.literal('test-run-result/1'),
  runId: z.string(),
  taskId: z.string(),
  correlationId: z.string(),
  runner: z.literal('boris-gideon-adapter'),
  status: z.enum(['passed', 'failed', 'cancelled', 'timed_out']),
  startedAt: z.string(),
  completedAt: z.string().optional(),
  suites: z.array(
    z.object({
      name: z.string(),
      status: z.enum(['passed', 'failed', 'skipped']),
      durationMs: z.number(),
      artifactRef: z.string().optional(),
    }),
  ),
  summary: z.object({
    total: z.number(),
    passed: z.number(),
    failed: z.number(),
    skipped: z.number(),
  }),
  outputHash: z.string(),
  receiptRef: z.string().optional(),
});
export type TestRunResult = z.infer<typeof TestRunResultSchema>;

export const ReceiptSummarySchema = z.object({
  receiptId: z.string(),
  eventId: z.string(),
  taskId: z.string(),
  correlationId: z.string(),
  kind: z.string(),
  timestamp: z.string(),
  actor: ActorSchema,
  payloadHash: z.string(),
  parentHash: z.string().optional(),
  integrity: EvidenceIntegritySchema,
});
export type ReceiptSummary = z.infer<typeof ReceiptSummarySchema>;

export const EffectManifestSchema = z.object({
  schemaVersion: z.literal('effect-manifest/1'),
  manifestId: z.string(),
  taskId: z.string(),
  correlationId: z.string(),
  kind: z.string(),
  baseRevision: z.string(),
  candidateRevision: z.string(),
  diffSha256: z.string(),
  allowedPaths: z.array(z.string()),
  requiredEvidence: z.array(z.string()),
  policyClass: z.string(),
  expiresAt: z.string(),
  oneTimeNonce: z.string(),
});
export type EffectManifest = z.infer<typeof EffectManifestSchema>;

export const OperatorTaskSnapshotSchema = z.object({
  schemaVersion: z.literal('operator-task-snapshot/1'),
  taskId: z.string(),
  correlationId: z.string(),
  generatedAt: z.string(),
  integrity: EvidenceIntegritySchema,
  intent: z.record(z.string(), z.unknown()),
  approval: z.record(z.string(), z.unknown()),
  taskGraph: z.array(z.record(z.string(), z.unknown())),
  diffs: z.array(DiffEvidenceSchema),
  tests: z.array(TestRunResultSchema),
  receipts: z.array(ReceiptSummarySchema),
});
export type OperatorTaskSnapshot = z.infer<typeof OperatorTaskSnapshotSchema>;
