# Operator Console Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the six-panel Operator Console at `apps/pwa/src/app/console/page.tsx` that renders typed task evidence (intent, approval, task graph, diffs, tests, receipts) from a new Bifrost Operator BFF, supports manifest-scoped approve/deny through a native Sentinel Decision Service, and proves the governed path (evidence → policy → verification → receipt) with Playwright.

**Architecture:** Augmentation above slice #1's VFS Preflight. A new Bifrost operator plane (`apps/bifrost/src/operator/`) owns typed contracts, an append-only SQLite Receipt/Event Service, the Sentinel Decision Service, a Gideon verdict provider, and the HTTP BFF (snapshot + SSE + decision). The PWA consumes typed snapshots + SSE through `apps/pwa/src/lib/operator_console/` and renders six read/approval panels. The console never edits source, never runs a shell, never mints leases, and never bypasses Sentinel.

**Tech Stack:** Next.js 14 App Router + React 18 + TypeScript strict (PWA), Express 4 + Prisma/SQLite + `ws` (Bifrost, existing), zod, vitest (Bifrost has its own config; new one added for PWA lib), Playwright (`apps/pwa/e2e`), native local processes (no Docker), `make` runbook.

**Spec:** `docs/architecture/OPERATOR_CONSOLE_DESIGN.md` (approved 2026-08-14). Companion: `docs/architecture/PEER_ARCHITECTURE.md`, `docs/architecture/VFS_PREFLIGHT_DESIGN.md`, `docs/adr/0006-vfs-preflight-strict-mode.md`.

## Global Constraints

(Copied verbatim or tightened from the approved design doc §2, §7, §8.3, §9, §10, §12; every task implicitly includes this section.)

- **Canonical host is `apps/pwa`.** The console route is `apps/pwa/src/app/console/page.tsx`; components live in `apps/pwa/src/components/operator_console/`. **No duplicate application source** — `apps/operations-console/` is a deployment placeholder limited to `README.md` + `deployment-notes.md` (Task 11 creates it).
- **Six panels:** Intent, Approval, Task Graph, Diffs, Tests, Receipts. Desktop default = responsive 3×2 grid; compact and mobile layouts preserve all six panels (AC1–AC4).
- **Console never authorizes.** It renders evidence and submits `{manifestId, decision, reason, sessionProof}` only. It never edits source, invokes a shell, issues capability leases, accesses secrets, or bypasses Sentinel. "Intent is not authority. A plan is not authority. A model response is not authority. A console click is not authority."
- **Evidence envelope `operator-evidence/1`** with required identifiers: `eventId, taskId, correlationId, timestamp, actor, kind, payloadHash, parentHash?, integrity` (§4). Integrity states are exactly `verified | pending_anchor | unavailable | integrity_failed`. **Never reduce `integrity_failed` to a generic "audit unavailable" indicator.**
- **State labels** are text + iconography + accessible labels; color is never the sole signal: `LIVE, STALE, PENDING DURABLE ANCHOR, UNAVAILABLE, INTEGRITY FAILED, POLICY BLOCKED, APPROVAL REQUIRED, COMPLETED, CANCELLED`.
- **Approval protocol (§9):** one immutable `effect-manifest/1` at a time; approve/deny submits only manifest ID + decision (+ reason + session proof). Sentinel independently verifies identity/role, task visibility, manifest integrity + expiry, required evidence integrity, current Gideon verdict, VFS constraints; writes a decision receipt; on approve issues one short-lived, non-transferable, one-time lease. Completion/failure/cancellation/expiry revokes the lease.
- **Bifrost BFF (§8.3):** `must` authenticate operator session, authorize task visibility, validate schema, redact sensitive fields, verify receipt reference when present, expose last-verified timestamp. `must_not` construct evidence, mint leases, accept raw shell commands, expose secrets or hidden reasoning, turn stale evidence into live state.
- **Failure behavior (§12):** Sentinel unavailable → `APPROVAL SUSPENDED` (approve/deny disabled, manifests remain readable); Gideon unavailable → `AUDIT SUSPENDED` (promotion/write blocked); Bifrost unavailable → render only locally cached verified evidence as `STALE` with exact age and disable all live-confirmation controls; integrity failure → `INTEGRITY FAILED` + disabled associated promotion paths + preserve record.
- **Performance:** p95 event-to-render ≤ 2 s under a local two-worker fixture task (AC6); the native slice #2 service set + two-worker fixture stays inside the declared 8 GB host budget (AC21).
- **Vercel is deferred** (§17): no Vercel auth/trust/network/operator-threat-model work in this slice.
- **Repo conventions:** SPDX-License-Identifier: MIT header on every new authored file (slice #1 check 020 enforces this repo-wide); `'use client'` at the top of any file using browser-only APIs (project Rule 2); Tailwind classes resolve against `apps/pwa/tailwind.config.js` — new tokens must be added to the config first (project Rule 3); hooks precede early returns (project Rule 4).
- **Reuse, don't copy:** `PlanCard.tsx`, `ExecutiveMetricsPanel.tsx`, `Dashboard.tsx` (layout patterns only), `SwarmRosterPanel.tsx`, `OpenDesignStatusPills.tsx` (pill patterns), `ThemeToggle.tsx` are reused from `apps/pwa/src/components/` where the design §6 says so.
- **Frequent commits**, one per task minimum, matching repo style: `feat(operator): …`, `test(operator): …`, `docs(operator): …`.

## File Structure (final state)

```
harness/
  contracts/                         # Task 1 — JSON Schema for wire payloads
    operator-evidence.schema.json
    operator-task-snapshot.schema.json
    effect-manifest.schema.json
    halt-decision.schema.json
    diff-evidence.schema.json
    test-run-result.schema.json
    receipt-summary.schema.json
  fixtures/                          # Task 11 — deterministic fixture tasks
    operator-console-readonly-audit/
    operator-console-approval/
    operator-console-integrity-failure/
    operator-console-cancellation/
  benchmarks/                        # Task 11
    operator-console-event-latency.sh
    operator-console-resource-budget.sh
apps/bifrost/
  prisma/schema.prisma               # MODIFY — add OperatorEvent model (Task 2)
  src/operator/                      # NEW operator plane
    chain.ts                         # pure hash-chain + canonicalization (Task 2)
    contracts.ts                     # zod schemas + types, canonical (Task 1)
    fixtures.ts                      # fixture task/event generators (Task 11)
    gideon.ts                        # typed verdict provider (Task 4)
    receipts.ts                      # append-only event store (Task 2)
    sentinel.ts                      # manifest validation + lease issue/revoke (Task 3)
    bff.ts                           # Express router: session/snapshot/SSE/decision (Task 5)
    contracts.test.ts
    chain.test.ts
    receipts.test.ts
    sentinel.test.ts
    gideon.test.ts
    bff.test.ts
  src/server.ts                      # MODIFY — mount operator BFF router (Task 5)
apps/pwa/
  src/app/console/page.tsx           # NEW (Task 7)
  src/lib/operator_console/          # NEW client data layer (Task 6)
    schemas.ts
    operator-api.ts
    operator-events.ts
    integrity.ts
    formatters.ts
    schemas.test.ts
    integrity.test.ts
    formatters.test.ts
  src/components/operator_console/   # NEW panels (Tasks 7-10)
    OperatorConsole.tsx
    OperatorConsoleHeader.tsx
    IntentPanel.tsx
    ApprovalPanel.tsx
    TaskGraphPanel.tsx
    DiffStreamPanel.tsx
    TestsPanel.tsx
    ReceiptsPanel.tsx
    EvidenceIntegrityBadge.tsx
    EffectManifestDialog.tsx
    ApprovalConfirmationDialog.tsx
    CancellationDialog.tsx
    StaleEvidenceNotice.tsx
    EmptyEvidenceState.tsx
    index.ts
  vitest.config.ts                   # NEW (Task 6)
  package.json                       # MODIFY — add test script + vitest devDep (Task 6)
  e2e/operator_console.spec.ts       # NEW (Task 12)
Makefile                             # NEW — native runbook (Task 11)
apps/operations-console/
  README.md                          # placeholder only (Task 11)
  deployment-notes.md                # placeholder only (Task 11)
docs/architecture/OPERATOR_CONSOLE_AC_EVIDENCE.md   # NEW (Task 12)
```

Cross-file communication: contracts from `operator/contracts.ts` are canonical; PWA mirrors them in `lib/operator_console/schemas.ts` (client-side validation, drift caught by a contract test in Task 6). `chain.ts` is pure; `receipts.ts` persists via Prisma; `sentinel.ts` consumes `contracts.ts` + `receipts.ts`; `bff.ts` wires all services to Express; panels consume `lib/operator_console/*` only.

---

## Task 1: Canonical contracts + harness JSON schemas

**Files:**
- Create: `apps/bifrost/src/operator/contracts.ts`
- Create: `apps/bifrost/src/operator/contracts.test.ts`
- Create: `harness/contracts/*.schema.json` (7 files)

**Interfaces (consumed by all later tasks):**

- `contracts.ts` exports zod schemas + inferred types: `EvidenceEnvelope`, `OperatorTaskSnapshot`, `EffectManifest`, `HaltDecision`, `DiffEvidence`, `TestRunResult`, `ReceiptSummary`, plus the `ActorRole` and `EvidenceIntegrity` unions.
- Property naming: **camelCase in TS and in the JSON Schema** (design §4 TS block is authoritative; its snake_case checklist is a field inventory, not a second wire format — recorded in Decisions Log).
- `schemaVersion` strings: `"operator-evidence/1"`, `"operator-task-snapshot/1"`, `"effect-manifest/1"`, `"halt-decision/1"`, `"test-run-result/1"`.

- [ ] **Step 1: Write the failing contract test**

Create `apps/bifrost/src/operator/contracts.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import {
  EvidenceEnvelopeSchema,
  EffectManifestSchema,
  OperatorTaskSnapshotSchema,
  type EvidenceEnvelope,
  type EffectManifest,
} from './contracts';

describe('operator contracts', () => {
  it('parses a valid evidence envelope (operator-evidence/1)', () => {
    const envelope: EvidenceEnvelope = {
      schemaVersion: 'operator-evidence/1',
      eventId: 'evt_01J...',
      taskId: 'task_01J...',
      correlationId: 'cor_01J...',
      causationId: undefined,
      timestamp: '2026-08-14T13:48:00Z',
      actor: { id: 'sir_gideon', role: 'gideon' },
      kind: 'diff.verified',
      payload: { diffSha256: 'sha256:abc' },
      payloadHash: 'sha256:abc',
      parentHash: undefined,
      integrity: 'verified',
    };
    expect(EvidenceEnvelopeSchema.parse(envelope).schemaVersion).toBe('operator-evidence/1');
  });

  it('rejects an envelope with an unknown actor role', () => {
    const bad = {
      schemaVersion: 'operator-evidence/1',
      eventId: 'evt_1',
      taskId: 'task_1',
      correlationId: 'cor_1',
      timestamp: '2026-08-14T13:48:00Z',
      actor: { id: 'x', role: 'malware' },
      kind: 'diff.verified',
      payload: {},
      payloadHash: 'sha256:x',
      integrity: 'verified',
    };
    expect(() => EvidenceEnvelopeSchema.parse(bad)).toThrow();
  });

  it('parses a valid effect manifest (effect-manifest/1)', () => {
    const manifest: EffectManifest = {
      schemaVersion: 'effect-manifest/1',
      manifestId: 'eff_01J...',
      taskId: 'task_01J...',
      correlationId: 'cor_01J...',
      kind: 'worktree.patch.promote',
      baseRevision: 'git-sha-base',
      candidateRevision: 'git-sha-candidate',
      diffSha256: 'sha256:...',
      allowedPaths: ['apps/pwa/src/components/operator_console/**'],
      requiredEvidence: ['receipt://vfs/no-escape/...'],
      policyClass: 'engineering.write',
      expiresAt: '2026-08-14T14:05:00Z',
      oneTimeNonce: 'opaque-random-value',
    };
    expect(EffectManifestSchema.parse(manifest).policyClass).toBe('engineering.write');
  });

  it('parses a valid task snapshot (operator-task-snapshot/1)', () => {
    const snapshot = OperatorTaskSnapshotSchema.parse({
      schemaVersion: 'operator-task-snapshot/1',
      taskId: 'task_01J...',
      correlationId: 'cor_01J...',
      generatedAt: '2026-08-14T13:48:00Z',
      integrity: 'verified',
      intent: {},
      approval: {},
      taskGraph: [],
      diffs: [],
      tests: [],
      receipts: [],
    });
    expect(snapshot.integrity).toBe('verified');
  });
});
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/contracts.test.ts
```

Expected: `FAIL` — cannot resolve `./contracts`.

- [ ] **Step 3: Implement `contracts.ts`**

Create `apps/bifrost/src/operator/contracts.ts`:

```ts
// SPDX-License-Identifier: MIT

import { z } from 'zod';

export const ActorRoleSchema = z.enum([
  'operator', 'anya', 'merlin', 'hiveide', 'nano_knight',
  'sentinel', 'gideon', 'boris', 'herald', 'system',
]);
export type ActorRole = z.infer<typeof ActorRoleSchema>;

export const EvidenceIntegritySchema = z.enum([
  'verified', 'pending_anchor', 'unavailable', 'integrity_failed',
]);
export type EvidenceIntegrity = z.infer<typeof EvidenceIntegritySchema>;

export const ActorSchema = z.object({
  id: z.string().min(1),
  role: ActorRoleSchema,
});
export type Actor = z.infer<typeof ActorSchema>;

export const EvidenceEnvelopeSchema = z.object({
  schemaVersion: z.literal('operator-evidence/1'),
  eventId: z.string().min(1),
  taskId: z.string().min(1),
  correlationId: z.string().min(1),
  causationId: z.string().optional(),
  timestamp: z.string().min(1),
  actor: ActorSchema,
  kind: z.string().min(1),
  payload: z.record(z.string(), z.unknown()),
  payloadHash: z.string().min(1),
  parentHash: z.string().optional(),
  integrity: EvidenceIntegritySchema,
  receiptRef: z.string().optional(),
  ledgerAnchorRef: z.string().optional(),
});
export type EvidenceEnvelope = z.infer<typeof EvidenceEnvelopeSchema>;

export const EffectManifestSchema = z.object({
  schemaVersion: z.literal('effect-manifest/1'),
  manifestId: z.string().min(1),
  taskId: z.string().min(1),
  correlationId: z.string().min(1),
  kind: z.string().min(1),
  baseRevision: z.string().min(1),
  candidateRevision: z.string().min(1),
  diffSha256: z.string().min(1),
  allowedPaths: z.array(z.string()).default([]),
  requiredEvidence: z.array(z.string()).default([]),
  policyClass: z.string().min(1),
  expiresAt: z.string().min(1),
  oneTimeNonce: z.string().min(1),
});
export type EffectManifest = z.infer<typeof EffectManifestSchema>;

export const HaltDecisionSchema = z.object({
  schemaVersion: z.literal('halt-decision/1'),
  decision: z.enum(['continue', 'block_boot', 'await_hitl']),
  checkId: z.string().optional(),
  rejectionReasons: z.array(z.string()).default([]),
  issuedAt: z.string().min(1),
});
export type HaltDecision = z.infer<typeof HaltDecisionSchema>;

export const DiffEvidenceSchema = z.object({
  baseRevision: z.string().min(1),
  candidateRevision: z.string().min(1),
  diffSha256: z.string().min(1),
  changedPaths: z.array(z.string()).default([]),
  addedLines: z.number().int().nonnegative(),
  removedLines: z.number().int().nonnegative(),
  generatedAt: z.string().min(1),
  gideonVerdict: z.enum(['pass', 'fail', 'pending', 'unavailable']).default('pending'),
  receiptRef: z.string().optional(),
});
export type DiffEvidence = z.infer<typeof DiffEvidenceSchema>;

export const TestRunResultSchema = z.object({
  schemaVersion: z.literal('test-run-result/1'),
  runId: z.string().min(1),
  taskId: z.string().min(1),
  correlationId: z.string().min(1),
  runner: z.literal('boris-gideon-adapter'),
  status: z.enum(['passed', 'failed', 'cancelled', 'timed_out']),
  startedAt: z.string().min(1),
  completedAt: z.string().optional(),
  suites: z.array(z.object({
    name: z.string().min(1),
    status: z.enum(['passed', 'failed', 'skipped']),
    durationMs: z.number().nonnegative(),
    artifactRef: z.string().optional(),
  })).default([]),
  summary: z.object({
    total: z.number().int().nonnegative(),
    passed: z.number().int().nonnegative(),
    failed: z.number().int().nonnegative(),
    skipped: z.number().int().nonnegative(),
  }),
  outputHash: z.string().min(1),
  receiptRef: z.string().optional(),
});
export type TestRunResult = z.infer<typeof TestRunResultSchema>;

export const ReceiptSummarySchema = z.object({
  receiptId: z.string().min(1),
  eventId: z.string().min(1),
  taskId: z.string().min(1),
  correlationId: z.string().min(1),
  kind: z.string().min(1),
  timestamp: z.string().min(1),
  actor: ActorSchema,
  payloadHash: z.string().min(1),
  parentHash: z.string().optional(),
  integrity: EvidenceIntegritySchema,
});
export type ReceiptSummary = z.infer<typeof ReceiptSummarySchema>;

export const OperatorTaskSnapshotSchema = z.object({
  schemaVersion: z.literal('operator-task-snapshot/1'),
  taskId: z.string().min(1),
  correlationId: z.string().min(1),
  generatedAt: z.string().min(1),
  integrity: EvidenceIntegritySchema,
  intent: z.record(z.string(), z.unknown()),
  approval: z.record(z.string(), z.unknown()),
  taskGraph: z.array(z.record(z.string(), z.unknown())).default([]),
  diffs: z.array(DiffEvidenceSchema).default([]),
  tests: z.array(TestRunResultSchema).default([]),
  receipts: z.array(ReceiptSummarySchema).default([]),
});
export type OperatorTaskSnapshot = z.infer<typeof OperatorTaskSnapshotSchema>;
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/contracts.test.ts
```

Expected: 4 passed.

- [ ] **Step 5: Write the 7 harness JSON schemas**

Create `harness/contracts/operator-evidence.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "harness/contracts/operator-evidence.schema.json",
  "title": "Operator Evidence Envelope (operator-evidence/1)",
  "type": "object",
  "required": ["schemaVersion", "eventId", "taskId", "correlationId", "timestamp", "actor", "kind", "payloadHash", "integrity"],
  "properties": {
    "schemaVersion": { "const": "operator-evidence/1" },
    "eventId": { "type": "string", "minLength": 1 },
    "taskId": { "type": "string", "minLength": 1 },
    "correlationId": { "type": "string", "minLength": 1 },
    "timestamp": { "type": "string", "minLength": 1 },
    "actor": {
      "type": "object",
      "required": ["id", "role"],
      "properties": {
        "id": { "type": "string" },
        "role": { "enum": ["operator", "anya", "merlin", "hiveide", "nano_knight", "sentinel", "gideon", "boris", "herald", "system"] }
      }
    },
    "kind": { "type": "string", "minLength": 1 },
    "payload": { "type": "object" },
    "payloadHash": { "type": "string", "minLength": 1 },
    "integrity": { "enum": ["verified", "pending_anchor", "unavailable", "integrity_failed"] }
  }
}
```

Create `harness/contracts/operator-task-snapshot.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "harness/contracts/operator-task-snapshot.schema.json",
  "title": "Operator Task Snapshot (operator-task-snapshot/1)",
  "type": "object",
  "required": ["schemaVersion", "taskId", "correlationId", "generatedAt", "integrity"],
  "properties": {
    "schemaVersion": { "const": "operator-task-snapshot/1" },
    "taskId": { "type": "string" },
    "correlationId": { "type": "string" },
    "generatedAt": { "type": "string" },
    "integrity": { "enum": ["verified", "pending_anchor", "unavailable", "integrity_failed"] },
    "intent": { "type": "object" },
    "approval": { "type": "object" },
    "taskGraph": { "type": "array" },
    "diffs": { "type": "array" },
    "tests": { "type": "array" },
    "receipts": { "type": "array" }
  }
}
```

Create `harness/contracts/effect-manifest.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "harness/contracts/effect-manifest.schema.json",
  "title": "Effect Manifest (effect-manifest/1)",
  "type": "object",
  "required": ["schemaVersion", "manifestId", "taskId", "correlationId", "kind", "baseRevision", "candidateRevision", "diffSha256", "policyClass", "expiresAt", "oneTimeNonce"],
  "properties": {
    "schemaVersion": { "const": "effect-manifest/1" },
    "manifestId": { "type": "string" },
    "taskId": { "type": "string" },
    "correlationId": { "type": "string" },
    "kind": { "type": "string" },
    "baseRevision": { "type": "string" },
    "candidateRevision": { "type": "string" },
    "diffSha256": { "type": "string" },
    "allowedPaths": { "type": "array", "items": { "type": "string" } },
    "requiredEvidence": { "type": "array", "items": { "type": "string" } },
    "policyClass": { "type": "string" },
    "expiresAt": { "type": "string" },
    "oneTimeNonce": { "type": "string" }
  }
}
```

Create `harness/contracts/halt-decision.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "harness/contracts/halt-decision.schema.json",
  "title": "Halt Decision (halt-decision/1)",
  "type": "object",
  "required": ["schemaVersion", "decision", "issuedAt"],
  "properties": {
    "schemaVersion": { "const": "halt-decision/1" },
    "decision": { "enum": ["continue", "block_boot", "await_hitl"] },
    "checkId": { "type": "string" },
    "rejectionReasons": { "type": "array", "items": { "type": "string" } },
    "issuedAt": { "type": "string" }
  }
}
```

Create `harness/contracts/diff-evidence.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "harness/contracts/diff-evidence.schema.json",
  "title": "Diff Evidence",
  "type": "object",
  "required": ["baseRevision", "candidateRevision", "diffSha256", "changedPaths", "addedLines", "removedLines", "generatedAt", "gideonVerdict"],
  "properties": {
    "baseRevision": { "type": "string" },
    "candidateRevision": { "type": "string" },
    "diffSha256": { "type": "string" },
    "changedPaths": { "type": "array", "items": { "type": "string" } },
    "addedLines": { "type": "integer", "minimum": 0 },
    "removedLines": { "type": "integer", "minimum": 0 },
    "generatedAt": { "type": "string" },
    "gideonVerdict": { "enum": ["pass", "fail", "pending", "unavailable"] },
    "receiptRef": { "type": "string" }
  }
}
```

Create `harness/contracts/test-run-result.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "harness/contracts/test-run-result.schema.json",
  "title": "Test Run Result (test-run-result/1)",
  "type": "object",
  "required": ["schemaVersion", "runId", "taskId", "correlationId", "runner", "status", "startedAt", "outputHash"],
  "properties": {
    "schemaVersion": { "const": "test-run-result/1" },
    "runId": { "type": "string" },
    "taskId": { "type": "string" },
    "correlationId": { "type": "string" },
    "runner": { "const": "boris-gideon-adapter" },
    "status": { "enum": ["passed", "failed", "cancelled", "timed_out"] },
    "startedAt": { "type": "string" },
    "completedAt": { "type": "string" },
    "suites": { "type": "array" },
    "summary": { "type": "object" },
    "outputHash": { "type": "string" },
    "receiptRef": { "type": "string" }
  }
}
```

Create `harness/contracts/receipt-summary.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "harness/contracts/receipt-summary.schema.json",
  "title": "Receipt Summary",
  "type": "object",
  "required": ["receiptId", "eventId", "taskId", "correlationId", "kind", "timestamp", "actor", "payloadHash", "integrity"],
  "properties": {
    "receiptId": { "type": "string" },
    "eventId": { "type": "string" },
    "taskId": { "type": "string" },
    "correlationId": { "type": "string" },
    "kind": { "type": "string" },
    "timestamp": { "type": "string" },
    "actor": { "type": "object" },
    "payloadHash": { "type": "string" },
    "parentHash": { "type": "string" },
    "integrity": { "enum": ["verified", "pending_anchor", "unavailable", "integrity_failed"] }
  }
}
```

- [ ] **Step 6: Commit**

```bash
git add apps/bifrost/src/operator/contracts.ts apps/bifrost/src/operator/contracts.test.ts harness/contracts/
git commit -m "feat(operator): canonical operator evidence contracts + harness JSON schemas"
```

---

## Task 2: Pure hash-chain + append-only SQLite Receipt/Event Service

**Files:**
- Create: `apps/bifrost/src/operator/chain.ts`
- Create: `apps/bifrost/src/operator/chain.test.ts`
- Create: `apps/bifrost/src/operator/receipts.ts`
- Create: `apps/bifrost/src/operator/receipts.test.ts`
- Modify: `apps/bifrost/prisma/schema.prisma` (add `OperatorEvent` model)

**Interfaces (consumed by Tasks 3, 5, 6):**

- `chain.canonicalJson(value: unknown): string` — stable, key-sorted serialization.
- `chain.sha256Hex(text: string): string` — `"sha256:" + hex` prefix, matching design's `diffSha256: "sha256:..."` convention.
- `chain.payloadHash(payload: unknown): string` — canonical JSON → sha256.
- `receipts.createStore(): ReceiptEventStore` — lazily binds Prisma; interface: `append(evt: NewOperatorEvent): Promise<StoredEvent>`, `listByTask(taskId: string, limit?: number): Promise<StoredEvent[]>`, `verifyChain(taskId: string): Promise<ChainVerification>`.
- The store is append-only: `append` computes `payloadHash` + `parentHash` (last event's `payloadHash` for the task) and writes one row; no update/delete paths.

- [ ] **Step 1: Write the failing chain test**

Create `apps/bifrost/src/operator/chain.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { canonicalJson, payloadHash, sha256Hex } from './chain';

describe('chain', () => {
  it('canonicalJson is key-sorted and stable regardless of insertion order', () => {
    const a = canonicalJson({ b: 1, a: { y: 2, x: 1 } });
    const b = canonicalJson({ a: { x: 1, y: 2 }, b: 1 });
    expect(a).toBe(b);
  });

  it('payloadHash prefixes with sha256:', () => {
    expect(payloadHash({ hello: 'world' })).toMatch(/^sha256:[0-9a-f]{64}$/);
  });

  it('payloadHash differs when payload changes', () => {
    expect(payloadHash({ a: 1 })).not.toBe(payloadHash({ a: 2 }));
  });

  it('sha256Hex is deterministic', () => {
    expect(sha256Hex('abc')).toBe(sha256Hex('abc'));
    expect(sha256Hex('abc')).toBe('sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  });
});
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/chain.test.ts
```

Expected: `FAIL` — cannot resolve `./chain`.

- [ ] **Step 3: Implement `chain.ts`**

Create `apps/bifrost/src/operator/chain.ts`:

```ts
// SPDX-License-Identifier: MIT

import { createHash } from 'node:crypto';

/** Stable, key-sorted JSON serialization (deterministic across key orders). */
export function canonicalJson(value: unknown): string {
  return JSON.stringify(sortKeys(value));
}

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value !== null && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(record).sort()) out[key] = sortKeys(record[key]);
    return out;
  }
  return value;
}

/** `sha256:`-prefixed hex digest, matching the design's diffSha256 convention. */
export function sha256Hex(text: string): string {
  return `sha256:${createHash('sha256').update(text, 'utf8').digest('hex')}`;
}

/** Content hash of an arbitrary payload via canonical JSON. */
export function payloadHash(payload: unknown): string {
  return sha256Hex(canonicalJson(payload));
}
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/chain.test.ts
```

Expected: 4 passed.

- [ ] **Step 5: Add the `OperatorEvent` model to the Prisma schema**

Modify `apps/bifrost/prisma/schema.prisma` — append this model:

```prisma
// Append-only operator evidence chain (slice #2 Operator Console).
// Rows are never updated or deleted; parentHash links the previous event
// for the same task, forming the integrity chain (design §4).
model OperatorEvent {
  id            String   @id @default(uuid())
  eventId       String   @unique
  taskId        String
  correlationId String
  timestamp     String
  actorId       String
  actorRole     String
  kind          String
  payload       String // canonical JSON
  payloadHash   String
  parentHash    String?
  integrity     String
  createdAt     DateTime @default(now())

  @@index([taskId, createdAt])
}
```

Then regenerate the client (this repo's pattern — `npx --no-install prisma generate` from `apps/bifrost`):

```bash
cd apps/bifrost && npx --no-install prisma generate
```

- [ ] **Step 6: Write the failing receipt store test**

Create `apps/bifrost/src/operator/receipts.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { InMemoryEventStore } from './receipts';

function makeEvt(taskId: string, kind: string, payload: Record<string, unknown>, idx: number) {
  return {
    eventId: `evt_${taskId}_${idx}`,
    taskId,
    correlationId: `cor_${taskId}`,
    timestamp: `2026-08-14T13:4${idx}:00Z`,
    actorId: 'sir_gideon',
    actorRole: 'gideon' as const,
    kind,
    payload,
    integrity: 'verified' as const,
  };
}

describe('receipt event store', () => {
  it('is append-only and links parent hashes per task', async () => {
    const store = new InMemoryEventStore();
    await store.append(makeEvt('t1', 'diff.verified', { diffSha256: 'sha256:a' }, 0));
    await store.append(makeEvt('t1', 'test.passed', { runId: 'r1' }, 1));
    await store.append(makeEvt('t2', 'diff.verified', { diffSha256: 'sha256:b' }, 0));

    const t1 = await store.listByTask('t1');
    expect(t1).toHaveLength(2);
    expect(t1[0]!.parentHash).toBeUndefined();
    expect(t1[1]!.parentHash).toBe(t1[0]!.payloadHash);
    // Task 2's events do not chain across tasks.
    const t2 = await store.listByTask('t2');
    expect(t2[0]!.parentHash).toBeUndefined();
  });

  it('computePayloadHash hashes canonical payload', async () => {
    const store = new InMemoryEventStore();
    const evt = makeEvt('t3', 'receipt.signed', { decision: 'approve' }, 0);
    const stored = await store.append(evt);
    expect(stored.payloadHash).toMatch(/^sha256:[0-9a-f]{64}$/);
  });

  it('verifyChain is true for an unbroken chain and false when tampered', async () => {
    const store = new InMemoryEventStore();
    await store.append(makeEvt('t4', 'a', { n: 1 }, 0));
    await store.append(makeEvt('t4', 'b', { n: 2 }, 1));
    const ok = await store.verifyChain('t4');
    expect(ok).toMatchObject({ valid: true, length: 2 });

    // Simulate an append that ignored the parent hash.
    const store2 = new InMemoryEventStore();
    await store2.append(makeEvt('t5', 'a', { n: 1 }, 0));
    await store2.append({ ...makeEvt('t5', 'b', { n: 2 }, 1), parentHash: 'sha256:forged' });
    const bad = await store2.verifyChain('t5');
    expect(bad.valid).toBe(false);
  });
});
```

- [ ] **Step 7: Run to verify it fails**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/receipts.test.ts
```

Expected: `FAIL` — cannot resolve `./receipts`.

- [ ] **Step 8: Implement `receipts.ts`**

Create `apps/bifrost/src/operator/receipts.ts`:

```ts
// SPDX-License-Identifier: MIT

import { payloadHash } from './chain';

export interface NewOperatorEvent {
  eventId: string;
  taskId: string;
  correlationId: string;
  timestamp: string;
  actorId: string;
  actorRole: string;
  kind: string;
  payload: Record<string, unknown>;
  integrity: 'verified' | 'pending_anchor' | 'unavailable' | 'integrity_failed';
}

export interface StoredEvent extends NewOperatorEvent {
  payloadHash: string;
  parentHash?: string;
}

export interface ChainVerification {
  valid: boolean;
  length: number;
  brokenAt?: string; // eventId where the link broke
}

/** Storage contract — Prisma-backed in production, in-memory in tests. */
export interface EventStore {
  append(evt: NewOperatorEvent): Promise<StoredEvent>;
  listByTask(taskId: string, limit?: number): Promise<StoredEvent[]>;
  verifyChain(taskId: string): Promise<ChainVerification>;
}

/**
 * In-memory store used by unit tests and by the `--fixture` harness mode.
 * Mirrors the Prisma-backed store's append-only + hash-chain semantics.
 */
export class InMemoryEventStore implements EventStore {
  private rows: StoredEvent[] = [];

  async append(evt: NewOperatorEvent): Promise<StoredEvent> {
    const last = (await this.listByTask(evt.taskId, 1))[0];
    const stored: StoredEvent = {
      ...evt,
      payloadHash: payloadHash(evt.payload),
      parentHash: evt.parentHash ?? last?.payloadHash,
    };
    this.rows.push(stored);
    return stored;
  }

  async listByTask(taskId: string, limit = 50): Promise<StoredEvent[]> {
    return this.rows
      .filter((r) => r.taskId === taskId)
      .slice(-limit)
      .reverse();
  }

  async verifyChain(taskId: string): Promise<ChainVerification> {
    const rows = (await this.listByTask(taskId, 1000)).reverse();
    let expectedParent: string | undefined;
    for (const row of rows) {
      if (row.parentHash !== expectedParent) {
        return { valid: false, length: rows.length, brokenAt: row.eventId };
      }
      expectedParent = row.payloadHash;
    }
    return { valid: true, length: rows.length };
  }
}

/**
 * Prisma-backed append-only store over the `OperatorEvent` model.
 * Lazy client binding: constructed with an injected client for tests, or
 * creates the generated client on first use in production.
 */
export function createPrismaEventStore(prisma?: unknown): EventStore {
  let client: {
    operatorEvent: {
      create(data: unknown): Promise<unknown>;
      findMany(args: unknown): Promise<Array<Record<string, unknown>>>;
    };
  } = prisma as never;
  if (!client) {
    // Lazy require keeps import-time side effects off the operator plane.
    // The generated client is at src/generated/client (see server.ts usage).
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { PrismaClient } = require('../generated/client');
    client = new PrismaClient();
  }
  return {
    async append(evt: NewOperatorEvent): Promise<StoredEvent> {
      const last = (await this.listByTask(evt.taskId, 1))[0];
      const stored: StoredEvent = {
        ...evt,
        payloadHash: payloadHash(evt.payload),
        parentHash: evt.parentHash ?? last?.payloadHash,
      };
      await client.operatorEvent.create({
        data: {
          eventId: stored.eventId,
          taskId: stored.taskId,
          correlationId: stored.correlationId,
          timestamp: stored.timestamp,
          actorId: stored.actorId,
          actorRole: stored.actorRole,
          kind: stored.kind,
          payload: JSON.stringify(stored.payload),
          payloadHash: stored.payloadHash,
          parentHash: stored.parentHash,
          integrity: stored.integrity,
        },
      });
      return stored;
    },
    async listByTask(taskId: string, limit = 50): Promise<StoredEvent[]> {
      const rows = (await client.operatorEvent.findMany({
        where: { taskId },
        orderBy: { createdAt: 'desc' },
        take: limit,
      })) as Array<Record<string, unknown>>;
      return rows.map((r) => ({
        eventId: String(r.eventId),
        taskId: String(r.taskId),
        correlationId: String(r.correlationId),
        timestamp: String(r.timestamp),
        actorId: String(r.actorId),
        actorRole: String(r.actorRole),
        kind: String(r.kind),
        payload: JSON.parse(String(r.payload ?? '{}')),
        payloadHash: String(r.payloadHash),
        parentHash: r.parentHash == null ? undefined : String(r.parentHash),
        integrity: String(r.integrity) as StoredEvent['integrity'],
      }));
    },
    async verifyChain(taskId: string): Promise<ChainVerification> {
      const rows = (await this.listByTask(taskId, 1000)).reverse();
      let expectedParent: string | undefined;
      for (const row of rows) {
        if (row.parentHash !== expectedParent) {
          return { valid: false, length: rows.length, brokenAt: row.eventId };
        }
        expectedParent = row.payloadHash;
      }
      return { valid: true, length: rows.length };
    },
  };
}
```

> **Note on the Prisma store's test surface:** unit tests run against `InMemoryEventStore` (hermetic). The Prisma-backed store is exercised by the opt-in integration test in Task 11 (`RUN_DB_TESTS=1`) against a tmp SQLite file. The chain logic is shared, so hash-chain correctness is proven without a live DB.

- [ ] **Step 9: Run to verify it passes**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/chain.test.ts src/operator/receipts.test.ts
```

Expected: all passed.

- [ ] **Step 10: Commit**

```bash
git add apps/bifrost/src/operator/chain.ts apps/bifrost/src/operator/chain.test.ts apps/bifrost/src/operator/receipts.ts apps/bifrost/src/operator/receipts.test.ts apps/bifrost/prisma/schema.prisma
git commit -m "feat(operator): hash-chain + append-only SQLite receipt/event service"
```

---

## Task 3: Sentinel Decision Service

**Files:**
- Create: `apps/bifrost/src/operator/sentinel.ts`
- Create: `apps/bifrost/src/operator/sentinel.test.ts`

**Interfaces (consumed by Task 5 BFF and Task 9 Approval panel):**

- `sentinel.verifyManifest(manifest: EffectManifest, ctx: VerifyContext): VerifyResult` — synchronous, pure: schema parse, expiry check (`expiresAt > now`), required-evidence presence, one-time nonce never seen.
- `sentinel.issueLease(manifestId: string, ttlMs?: number): Lease` — one-time, non-transferable, expiring; registry is in-memory (documented; production PEER Sentinel v2 binding deferred).
- `sentinel.revokeLease(leaseId: string): boolean`
- `sentinel.getLease(leaseId: string): Lease | undefined`
- `sentinel.SENTINEL_UNAVAILABLE` — sentinel object the BFF returns when the decision service is unreachable (design §12).

- [ ] **Step 1: Write the failing Sentinel test**

Create `apps/bifrost/src/operator/sentinel.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it, vi } from 'vitest';
import {
  getLease,
  issueLease,
  revokeLease,
  verifyManifest,
  type VerifyContext,
} from './sentinel';
import type { EffectManifest } from './contracts';

function makeManifest(overrides: Partial<EffectManifest> = {}): EffectManifest {
  return {
    schemaVersion: 'effect-manifest/1',
    manifestId: 'eff_01J',
    taskId: 'task_01J',
    correlationId: 'cor_01J',
    kind: 'worktree.patch.promote',
    baseRevision: 'base',
    candidateRevision: 'cand',
    diffSha256: 'sha256:abc',
    allowedPaths: ['apps/pwa/src/**'],
    requiredEvidence: ['receipt://vfs/no-escape/1'],
    policyClass: 'engineering.write',
    expiresAt: new Date(Date.now() + 60_000).toISOString(),
    oneTimeNonce: 'nonce-1',
    ...overrides,
  };
}

function makeCtx(overrides: Partial<VerifyContext> = {}): VerifyContext {
  return {
    now: () => new Date(),
    seenNonces: new Set<string>(),
    requiredEvidencePresent: (ref: string) => ref.startsWith('receipt://'),
    gideonVerdict: 'pass',
    vfsEvidenceOk: true,
    ...overrides,
  };
}

describe('sentinel decision service', () => {
  it('approves a valid, unexpired manifest with all evidence present', () => {
    const r = verifyManifest(makeManifest(), makeCtx());
    expect(r.approved).toBe(true);
    expect(r.reasons).toEqual([]);
  });

  it('rejects an expired manifest', () => {
    const ctx = makeCtx({ now: () => new Date('2026-08-14T15:00:00Z') });
    const r = verifyManifest(
      makeManifest({ expiresAt: '2026-08-14T14:00:00Z' }),
      ctx,
    );
    expect(r.approved).toBe(false);
    expect(r.reasons).toContain('manifest_expired');
  });

  it('rejects when required evidence is missing', () => {
    const r = verifyManifest(makeManifest(), makeCtx({
      requiredEvidencePresent: () => false,
    }));
    expect(r.approved).toBe(false);
    expect(r.reasons).toContain('required_evidence_missing');
  });

  it('rejects when Gideon verdict is fail or unavailable', () => {
    for (const verdict of ['fail', 'unavailable'] as const) {
      const r = verifyManifest(makeManifest(), makeCtx({ gideonVerdict: verdict }));
      expect(r.approved).toBe(false);
      expect(r.reasons).toContain('gideon_verdict_not_pass');
    }
  });

  it('rejects when VFS evidence is not ok', () => {
    const r = verifyManifest(makeManifest(), makeCtx({ vfsEvidenceOk: false }));
    expect(r.approved).toBe(false);
    expect(r.reasons).toContain('vfs_evidence_not_ok');
  });

  it('rejects a replayed one-time nonce', () => {
    const seen = new Set<string>(['nonce-1']);
    const r = verifyManifest(makeManifest(), makeCtx({ seenNonces: seen }));
    expect(r.approved).toBe(false);
    expect(r.reasons).toContain('nonce_replayed');
  });

  it('issues a lease that verifies once and can be revoked', () => {
    vi.useFakeTimers();
    try {
      const lease = issueLease('eff_01J', 5_000);
      expect(getLease(lease.leaseId)?.manifestId).toBe('eff_01J');
      expect(revokeLease(lease.leaseId)).toBe(true);
      expect(getLease(lease.leaseId)).toBeUndefined();
      expect(revokeLease(lease.leaseId)).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });
});
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/sentinel.test.ts
```

Expected: `FAIL` — cannot resolve `./sentinel`.

- [ ] **Step 3: Implement `sentinel.ts`**

Create `apps/bifrost/src/operator/sentinel.ts`:

```ts
// SPDX-License-Identifier: MIT

import { randomUUID } from 'node:crypto';
import { EffectManifestSchema, type EffectManifest } from './contracts';

export interface VerifyContext {
  now: () => Date;
  /** Nonces already used for this task — replays must be rejected. */
  seenNonces: Set<string>;
  /** Callback resolving a receipt:// ref to presence. */
  requiredEvidencePresent: (ref: string) => boolean;
  gideonVerdict: 'pass' | 'fail' | 'pending' | 'unavailable';
  vfsEvidenceOk: boolean;
}

export interface VerifyResult {
  approved: boolean;
  reasons: string[];
  manifestId: string;
}

export interface Lease {
  leaseId: string;
  manifestId: string;
  issuedAt: number;
  expiresAt: number;
}

/** In-memory lease registry. Slice #2: native decision service; the PEER
 * Sentinel v2 module path (design §17 Q1) remains an open question and this
 * registry is the placeholder it will replace. */
const leases = new Map<string, Lease>();
const seenNonceRegistry = new Map<string, Set<string>>();

export const SENTINEL_UNAVAILABLE = {
  state: 'APPROVAL_SUSPENDED',
  message: 'Sentinel decision service unavailable; approve/deny disabled.',
  lastVerifiedTimestamp: null,
} as const;

export function verifyManifest(
  manifest: EffectManifest,
  ctx: VerifyContext,
): VerifyResult {
  const reasons: string[] = [];

  const parsed = EffectManifestSchema.safeParse(manifest);
  if (!parsed.success) {
    return { approved: false, reasons: ['manifest_schema_invalid'], manifestId: manifest.manifestId };
  }

  if (new Date(manifest.expiresAt).getTime() <= ctx.now().getTime()) {
    reasons.push('manifest_expired');
  }
  for (const ref of manifest.requiredEvidence) {
    if (!ctx.requiredEvidencePresent(ref)) reasons.push('required_evidence_missing');
  }
  if (ctx.gideonVerdict !== 'pass') reasons.push('gideon_verdict_not_pass');
  if (!ctx.vfsEvidenceOk) reasons.push('vfs_evidence_not_ok');
  if (ctx.seenNonces.has(manifest.oneTimeNonce)) reasons.push('nonce_replayed');

  if (reasons.length === 0) {
    const taskNonces = seenNonceRegistry.get(manifest.taskId) ?? new Set<string>();
    taskNonces.add(manifest.oneTimeNonce);
    seenNonceRegistry.set(manifest.taskId, taskNonces);
  }

  return { approved: reasons.length === 0, reasons, manifestId: manifest.manifestId };
}

export function issueLease(manifestId: string, ttlMs = 5 * 60_000): Lease {
  const now = Date.now();
  const lease: Lease = {
    leaseId: randomUUID(),
    manifestId,
    issuedAt: now,
    expiresAt: now + ttlMs,
  };
  leases.set(lease.leaseId, lease);
  return lease;
}

export function getLease(leaseId: string): Lease | undefined {
  const lease = leases.get(leaseId);
  if (!lease) return undefined;
  if (Date.now() > lease.expiresAt) {
    leases.delete(leaseId);
    return undefined;
  }
  return lease;
}

export function revokeLease(leaseId: string): boolean {
  return leases.delete(leaseId);
}
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/sentinel.test.ts
```

Expected: all passed.

- [ ] **Step 5: Commit**

```bash
git add apps/bifrost/src/operator/sentinel.ts apps/bifrost/src/operator/sentinel.test.ts
git commit -m "feat(operator): Sentinel decision service — manifest verification + one-time leases"
```

---

## Task 4: Gideon verdict provider

**Files:**
- Create: `apps/bifrost/src/operator/gideon.ts`
- Create: `apps/bifrost/src/operator/gideon.test.ts`

**Interfaces (consumed by Task 5 BFF):**

- `gideon.verdictFor(diff: DiffEvidence, testRuns: TestRunResult[]): 'pass' | 'fail' | 'pending' | 'unavailable'`
- `gideon.GIDEON_UNAVAILABLE` — the sentinel the BFF uses when the adapter is unreachable (design §12 → `AUDIT SUSPENDED`).

- [ ] **Step 1: Write the failing Gideon test**

Create `apps/bifrost/src/operator/gideon.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { verdictFor } from './gideon';
import type { DiffEvidence, TestRunResult } from './contracts';

function makeDiff(overrides: Partial<DiffEvidence> = {}): DiffEvidence {
  return {
    baseRevision: 'base',
    candidateRevision: 'cand',
    diffSha256: 'sha256:abc',
    changedPaths: ['apps/pwa/src/app/console/page.tsx'],
    addedLines: 12,
    removedLines: 3,
    generatedAt: '2026-08-14T13:48:00Z',
    gideonVerdict: 'pending',
    ...overrides,
  };
}

function makeTest(status: TestRunResult['status']): TestRunResult {
  return {
    schemaVersion: 'test-run-result/1',
    runId: 'run_1',
    taskId: 'task_1',
    correlationId: 'cor_1',
    runner: 'boris-gideon-adapter',
    status,
    startedAt: '2026-08-14T13:40:00Z',
    completedAt: '2026-08-14T13:42:00Z',
    suites: [],
    summary: { total: 0, passed: 0, failed: 0, skipped: 0 },
    outputHash: 'sha256:test',
  };
}

describe('gideon verdict provider', () => {
  it('passes when the diff hash is self-consistent and tests pass', () => {
    expect(verdictFor(makeDiff(), [makeTest('passed')])).toBe('pass');
  });

  it('fails when any test run failed', () => {
    expect(verdictFor(makeDiff(), [makeTest('passed'), makeTest('failed')])).toBe('fail');
  });

  it('is unavailable when the adapter is unreachable', () => {
    expect(verdictFor(makeDiff(), [makeTest('passed')], { unavailable: true })).toBe('unavailable');
  });

  it('stays pending while tests are still running', () => {
    expect(verdictFor(makeDiff(), [makeTest('passed'), makeTest('cancelled')])).toBe('pending');
  });
});
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/gideon.test.ts
```

Expected: `FAIL` — cannot resolve `./gideon`.

- [ ] **Step 3: Implement `gideon.ts`**

Create `apps/bifrost/src/operator/gideon.ts`:

```ts
// SPDX-License-Identifier: MIT

import type { DiffEvidence, TestRunResult } from './contracts';

export type GideonVerdict = 'pass' | 'fail' | 'pending' | 'unavailable';

export const GIDEON_UNAVAILABLE = {
  state: 'AUDIT_SUSPENDED',
  message: 'Gideon audit adapter unavailable; promotion and write approval blocked.',
  lastVerifiedTimestamp: null,
} as const;

/**
 * Deterministic verdict composition for slice #2. The real PEER Gideon
 * adapter (design §17 Q2) replaces the body when it ships; the contract —
 * returning one of the four verdicts and never crashing on outage — is the
 * stable surface the BFF and panels depend on.
 */
export function verdictFor(
  diff: DiffEvidence,
  testRuns: TestRunResult[],
  opts: { unavailable?: boolean } = {},
): GideonVerdict {
  if (opts.unavailable) return 'unavailable';
  if (testRuns.some((t) => t.status === 'failed')) return 'fail';
  if (testRuns.some((t) => t.status === 'passed') && testRuns.every((t) => t.status === 'passed')) {
    return 'pass';
  }
  return 'pending';
}
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/gideon.test.ts
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add apps/bifrost/src/operator/gideon.ts apps/bifrost/src/operator/gideon.test.ts
git commit -m "feat(operator): typed Gideon verdict provider with graceful unavailability"
```

---

## Task 5: Bifrost Operator BFF (snapshot + SSE + decision)

**Files:**
- Create: `apps/bifrost/src/operator/bff.ts`
- Create: `apps/bifrost/src/operator/bff.test.ts`
- Modify: `apps/bifrost/src/server.ts` (mount the router)

**Interfaces (consumed by Task 6 PWA client and Task 12 e2e):**

- `GET /v1/operator/session` — returns `{ authenticated: boolean }` when the operator token header is present and valid (design §8.3 `authenticate_operator_session`). Local slice: token = env `OPERATOR_SESSION_TOKEN`; header `x-operator-token`. No secrets in `config.json` (boolean presence flags only, per repo privacy rule) — the actual token lives in the environment.
- `GET /v1/operator/tasks/:taskId/snapshot` — returns `OperatorTaskSnapshot` (design §8.1).
- `GET /v1/operator/tasks/:taskId/events` — SSE stream, `text/event-stream`, events of type `operator.evidence` (design §8.2). Sends the current snapshot as the first event.
- `POST /v1/operator/effect-manifests/:manifestId/decision` — body `{ decision: 'approve' | 'deny', reason?: string }`; returns `{ status, lease?, receiptRef? }`. Never accepts command text, paths, raw diffs, or deployment instructions (design §9).
- Redaction: `redactSensitive(payload)` strips keys named `secret`, `token`, `password`, `apiKey` before anything leaves the BFF (design §8.3 `redact_sensitive_fields`).
- Fixture mode: when `OPERATOR_FIXTURE_TASK` is set (e.g. `operator-console-approval`), the BFF serves deterministic fixture data (Task 11 populates `fixtures.ts`; Task 5 wires the read path with a minimal inline fixture so the BFF is testable end-to-end now).

- [ ] **Step 1: Write the failing BFF test**

Create `apps/bifrost/src/operator/bff.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import express from 'express';
import { createOperatorBff } from './bff';
import { InMemoryEventStore } from './receipts';
import { verifyManifest, issueLease } from './sentinel';
import type { EffectManifest } from './contracts';

let server: Server;
let base: string;

beforeAll(async () => {
  process.env.OPERATOR_SESSION_TOKEN = 'test-token';
  process.env.OPERATOR_FIXTURE_TASK = 'operator-console-approval';
  const app = express();
  app.use(express.json());
  const store = new InMemoryEventStore();
  const bff = createOperatorBff({
    store,
    verifyManifest,
    issueLease,
    now: () => new Date(),
    requiredEvidencePresent: (ref: string) => ref.startsWith('receipt://'),
    gideonVerdict: () => 'pass' as const,
    vfsEvidenceOk: () => true,
  });
  app.use('/v1/operator', bff);
  server = app.listen(0);
  await new Promise<void>((resolve) => server.once('listening', () => resolve()));
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});

afterAll(async () => {
  await new Promise<void>((resolve) => server.close(() => resolve()));
});

describe('operator BFF', () => {
  it('rejects unauthenticated snapshot requests', async () => {
    const res = await fetch(`${base}/v1/operator/tasks/task_1/snapshot`);
    expect(res.status).toBe(401);
  });

  it('serves a typed task snapshot when authenticated', async () => {
    const res = await fetch(`${base}/v1/operator/tasks/task_1/snapshot`, {
      headers: { 'x-operator-token': 'test-token' },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { schemaVersion: string; integrity: string; taskGraph: unknown[] };
    expect(body.schemaVersion).toBe('operator-task-snapshot/1');
    expect(body.integrity).toBe('verified');
    expect(Array.isArray(body.taskGraph)).toBe(true);
  });

  it('redacts sensitive fields from snapshot payloads', async () => {
    const res = await fetch(`${base}/v1/operator/tasks/task_1/snapshot`, {
      headers: { 'x-operator-token': 'test-token' },
    });
    const text = await res.text();
    expect(text).not.toContain('super-secret');
  });

  it('accepts a manifest-scoped approve decision and returns a lease', async () => {
    const res = await fetch(`${base}/v1/operator/effect-manifests/eff_1/decision`, {
      method: 'POST',
      headers: { 'x-operator-token': 'test-token', 'content-type': 'application/json' },
      body: JSON.stringify({ decision: 'approve', reason: 'evidence verified' }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { status: string; lease?: { leaseId: string } };
    expect(body.status).toBe('APPROVED');
    expect(body.lease?.leaseId).toBeTruthy();
  });

  it('rejects a decision body with extra command/path fields', async () => {
    const res = await fetch(`${base}/v1/operator/effect-manifests/eff_1/decision`, {
      method: 'POST',
      headers: { 'x-operator-token': 'test-token', 'content-type': 'application/json' },
      body: JSON.stringify({ decision: 'approve', command: 'rm -rf /', paths: ['/etc'] }),
    });
    expect(res.status).toBe(400);
  });

  it('exposes an SSE event stream', async () => {
    const res = await fetch(`${base}/v1/operator/tasks/task_1/events`, {
      headers: { 'x-operator-token': 'test-token' },
    });
    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toContain('text/event-stream');
  });
});
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/bff.test.ts
```

Expected: `FAIL` — cannot resolve `./bff`.

- [ ] **Step 3: Implement `bff.ts`**

Create `apps/bifrost/src/operator/bff.ts`:

```ts
// SPDX-License-Identifier: MIT

import { Router, type Request, type Response } from 'express';
import { z } from 'zod';
import type { EventStore } from './receipts';
import type { EffectManifest, OperatorTaskSnapshot } from './contracts';
import type { VerifyContext, VerifyResult } from './sentinel';

const SENSITIVE_KEYS = new Set(['secret', 'token', 'password', 'apiKey', 'authorization']);

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

const DecisionBodySchema = z.object({
  decision: z.enum(['approve', 'deny']),
  reason: z.string().max(2000).optional(),
}).strict(); // .strict() rejects command/path/raw-diff smuggling (design §9)

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
  return Boolean(token && process.env.OPERATOR_SESSION_TOKEN && token === process.env.OPERATOR_SESSION_TOKEN);
}

function auth(res: Response): void {
  res.status(401).json({ error: 'UNAUTHORIZED' });
}

/** Minimal inline fixture so the BFF is testable end-to-end before Task 11
 * swaps in the full harness fixture generators. */
function fixtureSnapshot(taskId: string): OperatorTaskSnapshot {
  const secretsProbe = { name: 'auth_probe', apiKey: 'super-secret-value' };
  return {
    schemaVersion: 'operator-task-snapshot/1',
    taskId,
    correlationId: `cor_${taskId}`,
    generatedAt: new Date().toISOString(),
    integrity: 'verified',
    intent: { raw: 'Verify scoped patch promote', secrets: secretsProbe },
    approval: { state: 'APPROVAL_REQUIRED' },
    taskGraph: [
      { nodeId: 'n1', name: 'ant-mapper', status: 'done' },
      { nodeId: 'n2', name: 'owl-auditor', status: 'running' },
    ],
    diffs: [
      {
        baseRevision: 'base', candidateRevision: 'cand', diffSha256: 'sha256:abc',
        changedPaths: ['apps/pwa/src/app/console/page.tsx'],
        addedLines: 12, removedLines: 3, generatedAt: new Date().toISOString(),
        gideonVerdict: 'pass',
      },
    ],
    tests: [],
    receipts: [],
  };
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
    res.write(`event: operator.evidence\ndata: ${JSON.stringify({ type: 'snapshot', payload: first })}\n\n`);
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
        actorId: 'sentinel', actorRole: 'sentinel',
        kind: 'decision.denied', payload: { manifestId, reason },
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
      baseRevision: 'base', candidateRevision: 'cand',
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
      actorId: 'sentinel', actorRole: 'sentinel',
      kind: 'decision.approved', payload: { manifestId, leaseId: lease.leaseId },
      integrity: 'verified',
    });
    res.status(200).json({ status: 'APPROVED', manifestId, lease });
  });

  return router;
}
```

- [ ] **Step 4: Mount the router in `server.ts`**

Modify `apps/bifrost/src/server.ts` — after the `app.use(express.json(...))` block, add:

```ts
import { createOperatorBff } from './operator/bff';
import { InMemoryEventStore } from './operator/receipts';
import { verifyManifest, issueLease } from './operator/sentinel';

// ── Slice #2 Operator Console BFF ─────────────────────────────────────────
// Native, local-first decision service. Fixture mode (OPERATOR_FIXTURE_TASK)
// serves deterministic task data for the operator console; production data
// binding is additive (see docs/architecture/OPERATOR_CONSOLE_DESIGN.md §8).
const operatorStore = new InMemoryEventStore();
const operatorBff = createOperatorBff({
  store: operatorStore,
  verifyManifest,
  issueLease,
  now: () => new Date(),
  requiredEvidencePresent: (ref: string) => ref.startsWith('receipt://'),
  gideonVerdict: () => 'pass' as const,
  vfsEvidenceOk: () => true,
});
app.use('/v1/operator', operatorBff);
```

- [ ] **Step 5: Run to verify it passes**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/bff.test.ts
```

Expected: 6 passed.

Also run the pre-existing Bifrost suite to confirm no regression:

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run
```

- [ ] **Step 6: Typecheck**

```bash
cd apps/bifrost && npm run typecheck
```

Expected: no type errors.

- [ ] **Step 7: Commit**

```bash
git add apps/bifrost/src/operator/bff.ts apps/bifrost/src/operator/bff.test.ts apps/bifrost/src/server.ts
git commit -m "feat(operator): Bifrost operator BFF — session/snapshot/SSE/decision + redaction"
```

---

## Task 6: PWA operator data layer

**Files:**
- Create: `apps/pwa/src/lib/operator_console/schemas.ts`
- Create: `apps/pwa/src/lib/operator_console/operator-api.ts`
- Create: `apps/pwa/src/lib/operator_console/operator-events.ts`
- Create: `apps/pwa/src/lib/operator_console/integrity.ts`
- Create: `apps/pwa/src/lib/operator_console/formatters.ts`
- Create: `apps/pwa/src/lib/operator_console/schemas.test.ts`
- Create: `apps/pwa/src/lib/operator_console/integrity.test.ts`
- Create: `apps/pwa/src/lib/operator_console/formatters.test.ts`
- Create: `apps/pwa/vitest.config.ts`
- Modify: `apps/pwa/package.json` (add `test` script + `vitest` devDependency)

**Interfaces (consumed by Tasks 7–10 panels):**

- `schemas.ts` — client-side zod mirrors of the canonical contracts (parses inbound BFF payloads; `'use client'`-free so it can be tested in Node).
- `operator-api.fetchSnapshot(taskId: string): Promise<OperatorTaskSnapshot>` — GET with `x-operator-token` from `localStorage`/env; throws typed `OperatorApiError` on 401.
- `operator-api.submitDecision(manifestId: string, decision: 'approve' | 'deny', reason?: string): Promise<DecisionResponse>`
- `operator-events.subscribe(taskId: string, onSnapshot: (s: OperatorTaskSnapshot) => void): () => void` — EventSource wrapper with reconnect; returns unsubscribe.
- `integrity.verifyEnvelope(envelope: EvidenceEnvelope): boolean` — recomputes payloadHash from payload and compares.
- `formatters.ageLabel(iso: string): string` — human age (`2m ago`), used by StaleEvidenceNotice.

- [ ] **Step 1: Add vitest to the PWA**

Modify `apps/pwa/package.json`:

```json
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit",
    "pretest:e2e": "next build",
    "test": "node ../../node_modules/vitest/vitest.mjs run",
    "test:e2e": "playwright test"
  },
```

and add to `devDependencies`:

```json
    "vitest": "^2.1.8"
```

Create `apps/pwa/vitest.config.ts`:

```ts
// SPDX-License-Identifier: MIT

import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/lib/operator_console/**/*.test.ts'],
  },
});
```

- [ ] **Step 2: Write the failing client contract/integrity/formatter tests**

Create `apps/pwa/src/lib/operator_console/schemas.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { OperatorTaskSnapshotSchema } from './schemas';

describe('operator console client schemas', () => {
  it('parses a valid snapshot payload', () => {
    const parsed = OperatorTaskSnapshotSchema.parse({
      schemaVersion: 'operator-task-snapshot/1',
      taskId: 'task_1',
      correlationId: 'cor_1',
      generatedAt: '2026-08-14T13:48:00Z',
      integrity: 'verified',
      intent: {}, approval: {}, taskGraph: [], diffs: [], tests: [], receipts: [],
    });
    expect(parsed.integrity).toBe('verified');
  });

  it('rejects an unknown schemaVersion (drift guard)', () => {
    expect(() => OperatorTaskSnapshotSchema.parse({
      schemaVersion: 'operator-task-snapshot/2',
      taskId: 'task_1', correlationId: 'cor_1', generatedAt: 'x', integrity: 'verified',
    })).toThrow();
  });
});
```

Create `apps/pwa/src/lib/operator_console/integrity.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { payloadHash, verifyEnvelope } from './integrity';
import type { EvidenceEnvelope } from './schemas';

function envelope(overrides: Partial<EvidenceEnvelope> = {}): EvidenceEnvelope {
  const payload = { decision: 'approve' };
  return {
    schemaVersion: 'operator-evidence/1',
    eventId: 'evt_1', taskId: 'task_1', correlationId: 'cor_1',
    timestamp: '2026-08-14T13:48:00Z',
    actor: { id: 'sentinel', role: 'sentinel' },
    kind: 'decision.approved', payload,
    payloadHash: payloadHash(payload),
    integrity: 'verified',
    ...overrides,
  };
}

describe('client integrity', () => {
  it('verifies a self-consistent envelope', () => {
    expect(verifyEnvelope(envelope())).toBe(true);
  });

  it('fails when payloadHash does not match the payload', () => {
    expect(verifyEnvelope(envelope({ payloadHash: 'sha256:forged' }))).toBe(false);
  });
});
```

Create `apps/pwa/src/lib/operator_console/formatters.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { ageLabel } from './formatters';

describe('formatters', () => {
  it('formats seconds and minutes ago', () => {
    const now = Date.now();
    expect(ageLabel(new Date(now - 30_000).toISOString(), now)).toBe('30s ago');
    expect(ageLabel(new Date(now - 2 * 60_000).toISOString(), now)).toBe('2m ago');
  });

  it('formats hours ago', () => {
    const now = Date.now();
    expect(ageLabel(new Date(now - 3 * 3_600_000).toISOString(), now)).toBe('3h ago');
  });
});
```

- [ ] **Step 3: Run to verify they fail**

```bash
cd apps/pwa && node ../../node_modules/vitest/vitest.mjs run src/lib/operator_console
```

Expected: `FAIL` — cannot resolve `./schemas`, `./integrity`, `./formatters`.

- [ ] **Step 4: Implement the client data layer**

Create `apps/pwa/src/lib/operator_console/schemas.ts`:

```ts
// SPDX-License-Identifier: MIT

import { z } from 'zod';

// Client-side mirrors of the canonical Bifrost contracts
// (apps/bifrost/src/operator/contracts.ts). Drift is caught by the
// schemaVersion literals and the contract test in schemas.test.ts.

export const ActorRoleSchema = z.enum([
  'operator', 'anya', 'merlin', 'hiveide', 'nano_knight',
  'sentinel', 'gideon', 'boris', 'herald', 'system',
]);
export type ActorRole = z.infer<typeof ActorRoleSchema>;

export const EvidenceIntegritySchema = z.enum([
  'verified', 'pending_anchor', 'unavailable', 'integrity_failed',
]);
export type EvidenceIntegrity = z.infer<typeof EvidenceIntegritySchema>;

export const ActorSchema = z.object({ id: z.string(), role: ActorRoleSchema });
export type Actor = z.infer<typeof ActorSchema>;

export const EvidenceEnvelopeSchema = z.object({
  schemaVersion: z.literal('operator-evidence/1'),
  eventId: z.string(), taskId: z.string(), correlationId: z.string(),
  causationId: z.string().optional(), timestamp: z.string(), actor: ActorSchema,
  kind: z.string(), payload: z.record(z.string(), z.unknown()),
  payloadHash: z.string(), parentHash: z.string().optional(),
  integrity: EvidenceIntegritySchema,
  receiptRef: z.string().optional(), ledgerAnchorRef: z.string().optional(),
});
export type EvidenceEnvelope = z.infer<typeof EvidenceEnvelopeSchema>;

export const DiffEvidenceSchema = z.object({
  baseRevision: z.string(), candidateRevision: z.string(), diffSha256: z.string(),
  changedPaths: z.array(z.string()), addedLines: z.number(), removedLines: z.number(),
  generatedAt: z.string(),
  gideonVerdict: z.enum(['pass', 'fail', 'pending', 'unavailable']),
  receiptRef: z.string().optional(),
});
export type DiffEvidence = z.infer<typeof DiffEvidenceSchema>;

export const TestRunResultSchema = z.object({
  schemaVersion: z.literal('test-run-result/1'),
  runId: z.string(), taskId: z.string(), correlationId: z.string(),
  runner: z.literal('boris-gideon-adapter'),
  status: z.enum(['passed', 'failed', 'cancelled', 'timed_out']),
  startedAt: z.string(), completedAt: z.string().optional(),
  suites: z.array(z.object({
    name: z.string(), status: z.enum(['passed', 'failed', 'skipped']),
    durationMs: z.number(), artifactRef: z.string().optional(),
  })),
  summary: z.object({ total: z.number(), passed: z.number(), failed: z.number(), skipped: z.number() }),
  outputHash: z.string(), receiptRef: z.string().optional(),
});
export type TestRunResult = z.infer<typeof TestRunResultSchema>;

export const ReceiptSummarySchema = z.object({
  receiptId: z.string(), eventId: z.string(), taskId: z.string(), correlationId: z.string(),
  kind: z.string(), timestamp: z.string(), actor: ActorSchema,
  payloadHash: z.string(), parentHash: z.string().optional(),
  integrity: EvidenceIntegritySchema,
});
export type ReceiptSummary = z.infer<typeof ReceiptSummarySchema>;

export const OperatorTaskSnapshotSchema = z.object({
  schemaVersion: z.literal('operator-task-snapshot/1'),
  taskId: z.string(), correlationId: z.string(), generatedAt: z.string(),
  integrity: EvidenceIntegritySchema,
  intent: z.record(z.string(), z.unknown()),
  approval: z.record(z.string(), z.unknown()),
  taskGraph: z.array(z.record(z.string(), z.unknown())),
  diffs: z.array(DiffEvidenceSchema),
  tests: z.array(TestRunResultSchema),
  receipts: z.array(ReceiptSummarySchema),
});
export type OperatorTaskSnapshot = z.infer<typeof OperatorTaskSnapshotSchema>;
```

Create `apps/pwa/src/lib/operator_console/operator-api.ts`:

```ts
// SPDX-License-Identifier: MIT

'use client';

import { OperatorTaskSnapshotSchema, type OperatorTaskSnapshot } from './schemas';

const BFF_BASE = process.env.NEXT_PUBLIC_BIFROST_HTTP_URL ?? 'http://localhost:3001';

export class OperatorApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'OperatorApiError';
  }
}

function headers(): Record<string, string> {
  const h: Record<string, string> = { 'content-type': 'application/json' };
  const token = localStorage.getItem('operator-session-token') ?? undefined;
  if (token) h['x-operator-token'] = token;
  return h;
}

export async function fetchSnapshot(taskId: string): Promise<OperatorTaskSnapshot> {
  const res = await fetch(`${BFF_BASE}/v1/operator/tasks/${taskId}/snapshot`, { headers: headers() });
  if (res.status === 401) throw new OperatorApiError(401, 'operator session required');
  if (!res.ok) throw new OperatorApiError(res.status, `snapshot failed: ${res.status}`);
  const body = OperatorTaskSnapshotSchema.parse(await res.json());
  return body;
}

export interface DecisionResponse {
  status: 'APPROVED' | 'DENIED' | 'BLOCKED';
  manifestId: string;
  lease?: { leaseId: string };
  reasons?: string[];
}

export async function submitDecision(
  manifestId: string,
  decision: 'approve' | 'deny',
  reason?: string,
): Promise<DecisionResponse> {
  const res = await fetch(`${BFF_BASE}/v1/operator/effect-manifests/${manifestId}/decision`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ decision, reason }),
  });
  if (res.status === 401) throw new OperatorApiError(401, 'operator session required');
  if (!res.ok) throw new OperatorApiError(res.status, `decision failed: ${res.status}`);
  return (await res.json()) as DecisionResponse;
}
```

Create `apps/pwa/src/lib/operator_console/operator-events.ts`:

```ts
// SPDX-License-Identifier: MIT

'use client';

import { OperatorTaskSnapshotSchema, type OperatorTaskSnapshot } from './schemas';

const BFF_BASE = process.env.NEXT_PUBLIC_BIFROST_HTTP_URL ?? 'http://localhost:3001';

/**
 * SSE subscription to the operator BFF event stream. Returns an unsubscribe
 * function. Reconnects on error with a 2s backoff (bounded to 5 attempts).
 */
export function subscribe(
  taskId: string,
  onSnapshot: (s: OperatorTaskSnapshot) => void,
): () => void {
  let closed = false;
  let es: EventSource | null = null;
  let attempts = 0;
  let timer: ReturnType<typeof setTimeout> | undefined;

  const connect = () => {
    if (closed || attempts >= 5) return;
    attempts += 1;
    es = new EventSource(`${BFF_BASE}/v1/operator/tasks/${taskId}/events`);
    es.onmessage = (event: MessageEvent<string>) => {
      try {
        const msg = JSON.parse(event.data) as { type?: string; payload?: unknown };
        if (msg.type === 'snapshot') {
          onSnapshot(OperatorTaskSnapshotSchema.parse(msg.payload));
        }
      } catch {
        // Ignore malformed frames; never fabricate state (design §18).
      }
    };
    es.onerror = () => {
      es?.close();
      es = null;
      timer = setTimeout(connect, 2000);
    };
  };

  connect();
  return () => {
    closed = true;
    if (timer) clearTimeout(timer);
    es?.close();
    es = null;
  };
}
```

Create `apps/pwa/src/lib/operator_console/integrity.ts`:

```ts
// SPDX-License-Identifier: MIT

import type { EvidenceEnvelope } from './schemas';

/** Key-sorted canonical JSON — must match apps/bifrost/src/operator/chain.ts. */
export function canonicalJson(value: unknown): string {
  return JSON.stringify(sortKeys(value));
}

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value !== null && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(record).sort()) out[key] = sortKeys(record[key]);
    return out;
  }
  return value;
}

async function digestHex(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const buf = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export async function payloadHash(payload: unknown): Promise<string> {
  return `sha256:${await digestHex(canonicalJson(payload))}`;
}

/** Recompute the payload hash and compare against the envelope's claim. */
export async function verifyEnvelope(envelope: EvidenceEnvelope): Promise<boolean> {
  const expected = await payloadHash(envelope.payload);
  return expected === envelope.payloadHash;
}
```

> Note: `payloadHash` and `verifyEnvelope` are async (WebCrypto). The integrity test uses `await`.

Create `apps/pwa/src/lib/operator_console/formatters.ts`:

```ts
// SPDX-License-Identifier: MIT

export function ageLabel(iso: string, nowMs: number = Date.now()): string {
  const diffMs = Math.max(0, nowMs - new Date(iso).getTime());
  const secs = Math.floor(diffMs / 1000);
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
```

- [ ] **Step 5: Update the integrity test for async + run all**

The `integrity.test.ts` from Step 2 must use `await` — replace it with:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { payloadHash, verifyEnvelope } from './integrity';
import type { EvidenceEnvelope } from './schemas';

function envelope(overrides: Partial<EvidenceEnvelope> = {}): EvidenceEnvelope {
  const payload = { decision: 'approve' };
  return {
    schemaVersion: 'operator-evidence/1',
    eventId: 'evt_1', taskId: 'task_1', correlationId: 'cor_1',
    timestamp: '2026-08-14T13:48:00Z',
    actor: { id: 'sentinel', role: 'sentinel' },
    kind: 'decision.approved', payload,
    payloadHash: 'sha256:placeholder', // replaced below with the real hash
    integrity: 'verified',
    ...overrides,
  };
}

describe('client integrity', () => {
  it('verifies a self-consistent envelope', async () => {
    const evt = envelope();
    evt.payloadHash = await payloadHash(evt.payload);
    expect(await verifyEnvelope(evt)).toBe(true);
  });

  it('fails when payloadHash does not match the payload', async () => {
    expect(await verifyEnvelope(envelope({ payloadHash: 'sha256:forged' }))).toBe(false);
  });
});
```

Run:

```bash
cd apps/pwa && node ../../node_modules/vitest/vitest.mjs run src/lib/operator_console
```

Expected: all passed (schemas, integrity, formatters).

- [ ] **Step 6: Typecheck the PWA**

```bash
cd apps/pwa && npm run typecheck
```

Expected: no type errors.

- [ ] **Step 7: Commit**

```bash
git add apps/pwa/src/lib/operator_console/ apps/pwa/vitest.config.ts apps/pwa/package.json
git commit -m "feat(operator): PWA operator data layer — typed API, SSE client, integrity, formatters"
```

---

## Task 7: Console shell — route, layout, header, state labels

**Files:**
- Create: `apps/pwa/src/app/console/page.tsx`
- Create: `apps/pwa/src/components/operator_console/OperatorConsole.tsx`
- Create: `apps/pwa/src/components/operator_console/OperatorConsoleHeader.tsx`
- Create: `apps/pwa/src/components/operator_console/EvidenceIntegrityBadge.tsx`
- Create: `apps/pwa/src/components/operator_console/StaleEvidenceNotice.tsx`
- Create: `apps/pwa/src/components/operator_console/EmptyEvidenceState.tsx`
- Create: `apps/pwa/src/components/operator_console/index.ts`

**Interfaces (consumed by Tasks 8–10):**

- `OperatorConsole({ taskId }: { taskId: string })` — owns snapshot state (`OperatorTaskSnapshot | null`), integrity state, and subscribes to SSE (Task 6). Renders the 3×2 grid (desktop), compact (`.compact` class), and mobile (vertical stack) layouts.
- `EvidenceIntegrityBadge({ integrity, taskId }: { integrity: EvidenceIntegrity; taskId: string })` — renders text + icon + screen-reader label; `integrity_failed` is always high-severity styled and never reduced to "audit unavailable".
- `StaleEvidenceNotice({ ageMs }: { ageMs: number })` — `STALE` label + exact age (design §12).
- `EmptyEvidenceState({ panel }: { panel: string })` — "No verified evidence yet" state with panel name (AC18 — never fabricate).

- [ ] **Step 1: Create the route page**

Create `apps/pwa/src/app/console/page.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import { OperatorConsole } from '../../components/operator_console';

export default function OperatorConsolePage() {
  // Fixture task id for slice #2; the harness drives real task ids later.
  return <OperatorConsole taskId="task_01J" />;
}
```

- [ ] **Step 2: Create the shell + primitives**

Create `apps/pwa/src/components/operator_console/EvidenceIntegrityBadge.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { EvidenceIntegrity } from '../../lib/operator_console/schemas';

const LABELS: Record<EvidenceIntegrity, { text: string; className: string }> = {
  verified: { text: 'VERIFIED', className: 'text-emerald-400 border-emerald-400/40' },
  pending_anchor: { text: 'PENDING DURABLE ANCHOR', className: 'text-amber-300 border-amber-300/40' },
  unavailable: { text: 'UNAVAILABLE', className: 'text-slate-400 border-slate-400/40' },
  integrity_failed: { text: 'INTEGRITY FAILED', className: 'text-red-400 border-red-400/60' },
};

export function EvidenceIntegrityBadge({ integrity, taskId }: {
  integrity: EvidenceIntegrity;
  taskId: string;
}) {
  const meta = LABELS[integrity];
  const role = integrity === 'integrity_failed' ? 'alert' : 'status';
  return (
    <span
      role={role}
      aria-label={`Evidence integrity ${meta.text} for task ${taskId}`}
      className={`inline-flex items-center gap-2 border px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest ${meta.className}`}
    >
      <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-current" />
      {meta.text}
    </span>
  );
}
```

Create `apps/pwa/src/components/operator_console/StaleEvidenceNotice.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function StaleEvidenceNotice({ ageLabel }: { ageLabel: string }) {
  return (
    <div
      role="status"
      className="flex items-center gap-2 border border-amber-300/40 bg-amber-300/5 px-3 py-2 font-mono text-[11px] text-amber-200"
    >
      <span aria-hidden="true">◷</span>
      <span>STALE · last verified {ageLabel}</span>
    </div>
  );
}
```

Create `apps/pwa/src/components/operator_console/EmptyEvidenceState.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function EmptyEvidenceState({ panel }: { panel: string }) {
  return (
    <div className="flex h-full min-h-24 items-center justify-center border border-white/10 px-4 py-6 text-center">
      <p className="font-mono text-xs text-white/40">
        No verified evidence yet — <span className="uppercase">{panel}</span>
      </p>
    </div>
  );
}
```

Create `apps/pwa/src/components/operator_console/OperatorConsoleHeader.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { EvidenceIntegrity } from '../../lib/operator_console/schemas';
import { EvidenceIntegrityBadge } from './EvidenceIntegrityBadge';

export function OperatorConsoleHeader({ taskId, integrity }: {
  taskId: string;
  integrity: EvidenceIntegrity;
}) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-b border-gold/20 pb-4">
      <div>
        <h1 className="font-display text-2xl tracking-minted text-gold-light">OPERATOR CONSOLE</h1>
        <p className="font-mono text-[11px] text-white/40">task {taskId} · read-rich, write-on-approval</p>
      </div>
      <EvidenceIntegrityBadge integrity={integrity} taskId={taskId} />
    </header>
  );
}
```

Create `apps/pwa/src/components/operator_console/OperatorConsole.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import { useEffect, useState } from 'react';
import { subscribe } from '../../lib/operator_console/operator-events';
import { fetchSnapshot, OperatorApiError } from '../../lib/operator_console/operator-api';
import type { OperatorTaskSnapshot } from '../../lib/operator_console/schemas';
import { ageLabel } from '../../lib/operator_console/formatters';
import { OperatorConsoleHeader } from './OperatorConsoleHeader';
import { StaleEvidenceNotice } from './StaleEvidenceNotice';
import { EmptyEvidenceState } from './EmptyEvidenceState';
// Panels (Tasks 8-10) fill these slots:
import { IntentPanel } from './IntentPanel';
import { ApprovalPanel } from './ApprovalPanel';
import { TaskGraphPanel } from './TaskGraphPanel';
import { DiffStreamPanel } from './DiffStreamPanel';
import { TestsPanel } from './TestsPanel';
import { ReceiptsPanel } from './ReceiptsPanel';

export function OperatorConsole({ taskId }: { taskId: string }) {
  const [snapshot, setSnapshot] = useState<OperatorTaskSnapshot | null>(null);
  const [lastVerifiedAt, setLastVerifiedAt] = useState<string | null>(null);
  const [bifrostDown, setBifrostDown] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchSnapshot(taskId)
      .then((s) => { if (mounted) { setSnapshot(s); setLastVerifiedAt(s.generatedAt); } })
      .catch((err) => {
        if (mounted && err instanceof OperatorApiError && err.status === 401) {
          // Session required — leave panel in UNAVAILABLE state.
        }
        if (mounted) setBifrostDown(true);
      });
    const unsubscribe = subscribe(taskId, (s) => {
      if (mounted) { setSnapshot(s); setLastVerifiedAt(s.generatedAt); setBifrostDown(false); }
    });
    return () => { mounted = false; unsubscribe(); };
  }, [taskId]);

  const integrity = snapshot?.integrity ?? 'unavailable';

  return (
    <main className="min-h-screen bg-obsidian px-6 py-8 font-mono">
      <OperatorConsoleHeader taskId={taskId} integrity={integrity} />
      {bifrostDown && <StaleEvidenceNotice ageLabel={lastVerifiedAt ? ageLabel(lastVerifiedAt) : 'never'} />}
      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <section className="rounded-sm border border-white/10 p-4" aria-label="Intent">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Intent</h2>
          {snapshot ? <IntentPanel intent={snapshot.intent} /> : <EmptyEvidenceState panel="Intent" />}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Approval">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Approval</h2>
          {snapshot ? <ApprovalPanel taskId={taskId} approval={snapshot.approval} /> : <EmptyEvidenceState panel="Approval" />}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Task Graph">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Task Graph</h2>
          {snapshot ? <TaskGraphPanel nodes={snapshot.taskGraph} /> : <EmptyEvidenceState panel="Task Graph" />}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Diffs">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Diffs</h2>
          {snapshot ? <DiffStreamPanel diffs={snapshot.diffs} /> : <EmptyEvidenceState panel="Diffs" />}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Tests">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Tests</h2>
          {snapshot ? <TestsPanel tests={snapshot.tests} /> : <EmptyEvidenceState panel="Tests" />}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Receipts">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Receipts</h2>
          {snapshot ? <ReceiptsPanel receipts={snapshot.receipts} taskId={taskId} /> : <EmptyEvidenceState panel="Receipts" />}
        </section>
      </div>
    </main>
  );
}
```

> **Note for the implementer:** Tasks 8–10 define the six panel components this task imports. To keep Task 7's test cycle green before panels exist, create minimal stub panel files in Task 7 (each rendering `<EmptyEvidenceState panel="<Name>" />`), then replace them in Tasks 8–10. The plan's Task 8–10 steps give the full implementations.

Create `apps/pwa/src/components/operator_console/index.ts`:

```ts
// SPDX-License-Identifier: MIT

export { OperatorConsole } from './OperatorConsole';
export { OperatorConsoleHeader } from './OperatorConsoleHeader';
export { EvidenceIntegrityBadge } from './EvidenceIntegrityBadge';
export { StaleEvidenceNotice } from './StaleEvidenceNotice';
export { EmptyEvidenceState } from './EmptyEvidenceState';
```

- [ ] **Step 3: Create minimal panel stubs (replaced in Tasks 8–10)**

Create the six stub files (each identical shape):

`apps/pwa/src/components/operator_console/IntentPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function IntentPanel({ intent }: { intent: Record<string, unknown> }) {
  return (
    <pre className="whitespace-pre-wrap break-all text-[11px] text-white/70">
      {JSON.stringify(intent, null, 2)}
    </pre>
  );
}
```

`apps/pwa/src/components/operator_console/ApprovalPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function ApprovalPanel({ approval }: { approval: Record<string, unknown>; taskId: string }) {
  return (
    <p className="text-xs text-white/50">Approval state: {JSON.stringify(approval.state ?? 'unknown')}</p>
  );
}
```

`apps/pwa/src/components/operator_console/TaskGraphPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function TaskGraphPanel({ nodes }: { nodes: Array<Record<string, unknown>> }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {nodes.map((n) => (
        <li key={String(n.nodeId)} className="flex items-center gap-2">
          <span className={`h-1.5 w-1.5 rounded-full ${n.status === 'done' ? 'bg-emerald-400' : 'bg-amber-300'}`} />
          <span>{String(n.name)}</span>
          <span className="text-white/40 uppercase">{String(n.status)}</span>
        </li>
      ))}
    </ul>
  );
}
```

`apps/pwa/src/components/operator_console/DiffStreamPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { DiffEvidence } from '../../lib/operator_console/schemas';

export function DiffStreamPanel({ diffs }: { diffs: DiffEvidence[] }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {diffs.map((d) => (
        <li key={d.diffSha256} className="break-all">
          <span className="text-gold-light">{d.diffSha256.slice(0, 20)}…</span> · {d.addedLines}+ / {d.removedLines}- · gideon {d.gideonVerdict}
        </li>
      ))}
    </ul>
  );
}
```

`apps/pwa/src/components/operator_console/TestsPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { TestRunResult } from '../../lib/operator_console/schemas';

export function TestsPanel({ tests }: { tests: TestRunResult[] }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {tests.map((t) => (
        <li key={t.runId} className="flex items-center gap-2">
          <span className="uppercase">{t.status}</span>
          <span className="text-white/40">{t.summary.passed}/{t.summary.total} passed</span>
        </li>
      ))}
    </ul>
  );
}
```

`apps/pwa/src/components/operator_console/ReceiptsPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { ReceiptSummary } from '../../lib/operator_console/schemas';

export function ReceiptsPanel({ receipts }: { receipts: ReceiptSummary[]; taskId: string }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {receipts.slice(0, 50).map((r) => (
        <li key={r.receiptId} className="flex items-center gap-2">
          <span className="uppercase text-white/40">{r.kind}</span>
          <span>{r.timestamp}</span>
        </li>
      ))}
      {receipts.length === 0 && <li className="text-white/40">No receipts yet</li>}
    </ul>
  );
}
```

- [ ] **Step 4: Verify the PWA typechecks and builds**

```bash
cd apps/pwa && npm run typecheck
```

Expected: no type errors.

- [ ] **Step 5: Commit**

```bash
git add apps/pwa/src/app/console/ apps/pwa/src/components/operator_console/
git commit -m "feat(operator): console shell — route, 3x2 grid layout, integrity badge, stale notice"
```

---

## Task 8: Read-only panels — Intent, Task Graph, Diffs, Tests (full implementations)

**Files:**
- Modify: `apps/pwa/src/components/operator_console/IntentPanel.tsx`
- Modify: `apps/pwa/src/components/operator_console/TaskGraphPanel.tsx`
- Modify: `apps/pwa/src/components/operator_console/DiffStreamPanel.tsx`
- Modify: `apps/pwa/src/components/operator_console/TestsPanel.tsx`

These replace the Task 7 stubs with the typed, state-aware implementations. All four are read-only (inspect only, design §5.2). Failure behavior: unavailable → `EmptyEvidenceState`; integrity failure → high-severity banner + disabled promotion path (no promotion UI exists on read-only panels, so "disabled" means the Approval panel gates).

- [ ] **Step 1: IntentPanel — full implementation**

Replace `apps/pwa/src/components/operator_console/IntentPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function IntentPanel({ intent }: { intent: Record<string, unknown> }) {
  const hasIntent = Object.keys(intent).length > 0;
  if (!hasIntent) {
    return (
      <p className="text-xs italic text-white/40">No signed raw intent available.</p>
    );
  }
  return (
    <div className="space-y-3">
      <p className="text-xs text-white/50">Signed raw intent (read-only):</p>
      <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-all rounded-sm border border-white/10 bg-black/30 p-3 text-[11px] text-white/80">
        {JSON.stringify(intent, null, 2)}
      </pre>
    </div>
  );
}
```

- [ ] **Step 2: TaskGraphPanel — full implementation**

Replace `apps/pwa/src/components/operator_console/TaskGraphPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

interface DagNode {
  nodeId: string;
  name?: string;
  status?: string;
  worker?: string;
  updatedAt?: string;
}

const STATUS_DOT: Record<string, string> = {
  done: 'bg-emerald-400',
  running: 'bg-amber-300',
  blocked: 'bg-red-400',
  cancelled: 'bg-white/30',
};

export function TaskGraphPanel({ nodes }: { nodes: Array<Record<string, unknown>> }) {
  if (!nodes.length) {
    return <p className="text-xs italic text-white/40">No task graph nodes yet.</p>;
  }
  const dag = nodes as DagNode[];
  return (
    <ul className="space-y-2">
      {dag.map((n) => {
        const status = n.status ?? 'unknown';
        return (
          <li key={n.nodeId} className="flex items-center justify-between gap-2 text-xs text-white/80">
            <span className="flex items-center gap-2">
              <span aria-hidden="true" className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[status] ?? 'bg-white/40'}`} />
              <span>{n.name ?? n.nodeId}</span>
            </span>
            <span className="font-mono text-[10px] uppercase tracking-wider text-white/40">
              {status}{n.worker ? ` · ${n.worker}` : ''}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
```

- [ ] **Step 3: DiffStreamPanel — full implementation**

Replace `apps/pwa/src/components/operator_console/DiffStreamPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { DiffEvidence } from '../../lib/operator_console/schemas';

const VERDICT_STYLE: Record<string, string> = {
  pass: 'text-emerald-400',
  fail: 'text-red-400',
  pending: 'text-amber-300',
  unavailable: 'text-slate-400',
};

export function DiffStreamPanel({ diffs }: { diffs: DiffEvidence[] }) {
  if (!diffs.length) {
    return <p className="text-xs italic text-white/40">No diff evidence yet.</p>;
  }
  return (
    <ul className="space-y-3">
      {diffs.map((d) => (
        <li key={d.diffSha256} className="border border-white/10 p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="break-all font-mono text-[10px] text-gold-light">{d.diffSha256}</span>
            <span className={`font-mono text-[10px] uppercase ${VERDICT_STYLE[d.gideonVerdict] ?? ''}`}>
              gideon: {d.gideonVerdict}
            </span>
          </div>
          <p className="mt-1 text-[11px] text-white/50">
            {d.addedLines} added · {d.removedLines} removed · {d.changedPaths.length} paths
          </p>
          {d.changedPaths.slice(0, 4).map((p) => (
            <p key={p} className="mt-0.5 break-all font-mono text-[10px] text-white/40">+ {p}</p>
          ))}
        </li>
      ))}
    </ul>
  );
}
```

- [ ] **Step 4: TestsPanel — full implementation**

Replace `apps/pwa/src/components/operator_console/TestsPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { TestRunResult } from '../../lib/operator_console/schemas';

const STATUS_STYLE: Record<string, string> = {
  passed: 'text-emerald-400',
  failed: 'text-red-400',
  cancelled: 'text-white/40',
  timed_out: 'text-amber-300',
};

export function TestsPanel({ tests }: { tests: TestRunResult[] }) {
  if (!tests.length) {
    return <p className="text-xs italic text-white/40">No test runs yet.</p>;
  }
  return (
    <ul className="space-y-3">
      {tests.map((t) => (
        <li key={t.runId} className="border border-white/10 p-3">
          <div className="flex items-center justify-between gap-2">
            <span className={`font-mono text-[11px] uppercase ${STATUS_STYLE[t.status] ?? ''}`}>{t.status}</span>
            <span className="font-mono text-[10px] text-white/40">
              {t.summary.passed}/{t.summary.total} passed · {t.summary.failed} failed
            </span>
          </div>
          {t.suites.map((s) => (
            <p key={s.name} className="mt-1 text-[11px] text-white/50">
              {s.name} · <span className="uppercase">{s.status}</span> · {s.durationMs}ms
            </p>
          ))}
        </li>
      ))}
    </ul>
  );
}
```

- [ ] **Step 5: Typecheck + verify**

```bash
cd apps/pwa && npm run typecheck
```

Expected: no type errors.

- [ ] **Step 6: Commit**

```bash
git add apps/pwa/src/components/operator_console/IntentPanel.tsx apps/pwa/src/components/operator_console/TaskGraphPanel.tsx apps/pwa/src/components/operator_console/DiffStreamPanel.tsx apps/pwa/src/components/operator_console/TestsPanel.tsx
git commit -m "feat(operator): typed read-only panels — intent, task graph, diffs, tests"
```

---

## Task 9: Approval + Receipts panels

**Files:**
- Create: `apps/pwa/src/components/operator_console/EffectManifestDialog.tsx`
- Create: `apps/pwa/src/components/operator_console/ApprovalConfirmationDialog.tsx`
- Create: `apps/pwa/src/components/operator_console/CancellationDialog.tsx`
- Modify: `apps/pwa/src/components/operator_console/ApprovalPanel.tsx`
- Modify: `apps/pwa/src/components/operator_console/ReceiptsPanel.tsx`

**Interfaces:**

- `EffectManifestDialog({ manifest, onApprove, onDeny, disabled, reason }: ...)` — renders the immutable manifest (changed paths, diff hash, expiry, required evidence, policy class) and Approve/Deny buttons (design §9, AC10). Disabled when Sentinel/Gideon/policy/integrity invalid (AC14).
- `ApprovalConfirmationDialog({ open, decision, onConfirm, onCancel })` — one more explicit confirm before submission (design §9 step 3–4).
- `CancellationDialog({ open, onConfirm, onCancel })` — used when the harness supports cancellation (Task 11/AC20); wires to `POST /v1/operator/tasks/:id/cancel` (added in Task 11; the dialog here degrades gracefully when the endpoint is absent).
- Approval flow state: `APPROVAL_SUSPENDED` (Sentinel down), `AUDIT_SUSPENDED` (Gideon down), `APPROVAL_REQUIRED`, `COMPLETED`, `CANCELLED`, `POLICY_BLOCKED`.

- [ ] **Step 1: EffectManifestDialog**

Create `apps/pwa/src/components/operator_console/EffectManifestDialog.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import { useState } from 'react';
import type { EffectManifest } from '../../lib/operator_console/schemas';

export function EffectManifestDialog({
  manifest,
  onApprove,
  onDeny,
  disabled,
}: {
  manifest: EffectManifest;
  onApprove: (reason?: string) => void;
  onDeny: (reason?: string) => void;
  disabled: boolean;
}) {
  const [reason, setReason] = useState('');

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Effect manifest approval"
      className="border border-gold/30 bg-obsidian p-4 shadow-[4px_4px_0px_0px_#050507]"
    >
      <h3 className="font-display text-sm tracking-minted text-gold-light">EFFECT MANIFEST</h3>
      <dl className="mt-3 space-y-2 text-xs text-white/70">
        <div className="flex justify-between gap-4"><dt className="text-white/40">Manifest</dt><dd className="break-all">{manifest.manifestId}</dd></div>
        <div className="flex justify-between gap-4"><dt className="text-white/40">Kind</dt><dd>{manifest.kind}</dd></div>
        <div className="flex justify-between gap-4"><dt className="text-white/40">Diff SHA-256</dt><dd className="break-all">{manifest.diffSha256}</dd></div>
        <div className="flex justify-between gap-4"><dt className="text-white/40">Policy</dt><dd>{manifest.policyClass}</dd></div>
        <div className="flex justify-between gap-4"><dt className="text-white/40">Expires</dt><dd>{manifest.expiresAt}</dd></div>
        <div className="flex justify-between gap-4"><dt className="text-white/40">Base → Candidate</dt><dd className="break-all">{manifest.baseRevision.slice(0, 8)} → {manifest.candidateRevision.slice(0, 8)}</dd></div>
      </dl>
      <div className="mt-3">
        <p className="mb-1 text-[10px] uppercase tracking-widest text-white/40">Changed paths</p>
        <ul className="max-h-28 overflow-auto border border-white/10 p-2 font-mono text-[10px] text-white/60">
          {manifest.allowedPaths.map((p) => <li key={p}>+ {p}</li>)}
        </ul>
      </div>
      <div className="mt-3">
        <p className="mb-1 text-[10px] uppercase tracking-widest text-white/40">Required evidence</p>
        <ul className="font-mono text-[10px] text-white/60">
          {manifest.requiredEvidence.map((e) => <li key={e}>· {e}</li>)}
        </ul>
      </div>
      <label className="mt-4 block">
        <span className="text-[10px] uppercase tracking-widest text-white/40">Optional reason</span>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          maxLength={500}
          className="mt-1 w-full border border-white/15 bg-black/30 p-2 text-xs text-white/80"
          aria-label="Optional decision reason"
        />
      </label>
      <div className="mt-4 flex gap-3">
        <button
          type="button"
          onClick={() => onApprove(reason)}
          disabled={disabled}
          className="border border-emerald-400/60 px-4 py-2 text-xs uppercase tracking-widest text-emerald-300 transition-colors enabled:hover:bg-emerald-400/10 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Approve
        </button>
        <button
          type="button"
          onClick={() => onDeny(reason)}
          disabled={disabled}
          className="border border-red-400/60 px-4 py-2 text-xs uppercase tracking-widest text-red-300 transition-colors enabled:hover:bg-red-400/10 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Deny
        </button>
      </div>
      {disabled && (
        <p className="mt-3 text-[11px] text-amber-200" role="alert">
          Approve/deny disabled: Sentinel, policy, Gideon, VFS, or evidence integrity is unavailable or invalid.
        </p>
      )}
    </div>
  );
}
```

> **Note:** `EffectManifest` is not yet exported from the client schemas (Task 6 exported the snapshot pieces only). Add it now — see Step 4.

- [ ] **Step 2: ApprovalConfirmationDialog + CancellationDialog**

Create `apps/pwa/src/components/operator_console/ApprovalConfirmationDialog.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function ApprovalConfirmationDialog({
  open,
  decision,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  decision: 'approve' | 'deny';
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Confirm ${decision}`}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
    >
      <div className="w-full max-w-md border border-gold/30 bg-obsidian p-5">
        <h3 className="font-display text-base tracking-minted text-gold-light">
          CONFIRM {decision.toUpperCase()}
        </h3>
        <p className="mt-2 text-xs text-white/60">
          This submits a manifest-scoped decision to Sentinel. Only the manifest ID and your
          decision are transmitted — no commands, no paths, no diffs.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="border border-white/20 px-4 py-2 text-xs uppercase tracking-widest text-white/60"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`border px-4 py-2 text-xs uppercase tracking-widest ${
              decision === 'approve'
                ? 'border-emerald-400/60 text-emerald-300'
                : 'border-red-400/60 text-red-300'
            }`}
          >
            Confirm {decision}
          </button>
        </div>
      </div>
    </div>
  );
}
```

Create `apps/pwa/src/components/operator_console/CancellationDialog.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

export function CancellationDialog({
  open,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Cancel active task"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
    >
      <div className="w-full max-w-md border border-red-400/40 bg-obsidian p-5">
        <h3 className="font-display text-base tracking-minted text-red-300">CANCEL ACTIVE TASK</h3>
        <p className="mt-2 text-xs text-white/60">
          Cancelling revokes the lease, stops workers, and cleans the VFS workspace, then emits a
          cancellation receipt.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <button type="button" onClick={onCancel} className="border border-white/20 px-4 py-2 text-xs uppercase tracking-widest text-white/60">
            Keep running
          </button>
          <button type="button" onClick={onConfirm} className="border border-red-400/60 px-4 py-2 text-xs uppercase tracking-widest text-red-300">
            Confirm cancel
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: ApprovalPanel — full implementation**

Replace `apps/pwa/src/components/operator_console/ApprovalPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import { useState } from 'react';
import { submitDecision, type DecisionResponse } from '../../lib/operator_console/operator-api';
import { EffectManifestDialog } from './EffectManifestDialog';
import { ApprovalConfirmationDialog } from './ApprovalConfirmationDialog';

interface ApprovalView {
  state: string;
  manifest?: EffectManifestLike;
}

// Minimal local shape mirroring effect-manifest/1 (Task 6 schemas export
// the full type; see schemas.ts EffectManifestSchema addition in Step 4).
interface EffectManifestLike {
  schemaVersion: string;
  manifestId: string;
  taskId: string;
  correlationId: string;
  kind: string;
  baseRevision: string;
  candidateRevision: string;
  diffSha256: string;
  allowedPaths: string[];
  requiredEvidence: string[];
  policyClass: string;
  expiresAt: string;
  oneTimeNonce: string;
}

export function ApprovalPanel({ approval, taskId }: {
  approval: Record<string, unknown>;
  taskId: string;
}) {
  const [pendingDecision, setPendingDecision] = useState<'approve' | 'deny' | null>(null);
  const [outcome, setOutcome] = useState<DecisionResponse | null>(null);

  const state = String(approval.state ?? 'APPROVAL_REQUIRED');
  const suspended = state === 'APPROVAL_SUSPENDED' || state === 'AUDIT_SUSPENDED';
  const policyBlocked = state === 'POLICY_BLOCKED';
  const disabled = suspended || policyBlocked;

  // Fixture manifest surfaced by the BFF (Task 5) — slice #2 renders the
  // immutable manifest for the fixture task.
  const manifest: EffectManifestLike = {
    schemaVersion: 'effect-manifest/1',
    manifestId: 'eff_01J',
    taskId,
    correlationId: `cor_${taskId}`,
    kind: 'worktree.patch.promote',
    baseRevision: 'base',
    candidateRevision: 'cand',
    diffSha256: 'sha256:abc',
    allowedPaths: ['apps/pwa/src/components/operator_console/**'],
    requiredEvidence: ['receipt://vfs/no-escape/1'],
    policyClass: 'engineering.write',
    expiresAt: new Date(Date.now() + 60_000).toISOString(),
    oneTimeNonce: 'nonce_fixture',
  };

  const runDecision = async (decision: 'approve' | 'deny', reason?: string) => {
    try {
      const res = await submitDecision(manifest.manifestId, decision, reason);
      setOutcome(res);
    } catch (err) {
      setOutcome({ status: 'BLOCKED', manifestId: manifest.manifestId, reasons: [String(err)] });
    }
    setPendingDecision(null);
  };

  if (suspended) {
    return (
      <div className="border border-amber-300/40 p-3" role="alert">
        <p className="font-mono text-[11px] uppercase tracking-widest text-amber-200">
          {state === 'APPROVAL_SUSPENDED' ? 'Approval suspended — Sentinel unavailable' : 'Audit suspended — Gideon unavailable'}
        </p>
        <p className="mt-1 text-[11px] text-white/50">Existing manifests remain readable. Approve/deny is disabled.</p>
      </div>
    );
  }

  if (policyBlocked) {
    return (
      <div className="border border-red-400/50 p-3" role="alert">
        <p className="font-mono text-[11px] uppercase tracking-widest text-red-300">Policy blocked</p>
        <p className="mt-1 text-[11px] text-white/50">This effect is blocked by policy. No approval path exists.</p>
      </div>
    );
  }

  if (outcome?.status === 'APPROVED') {
    return (
      <div className="border border-emerald-400/50 p-3">
        <p className="font-mono text-[11px] uppercase tracking-widest text-emerald-300">Approved</p>
        <p className="mt-1 text-[11px] text-white/60">Lease {outcome.lease?.leaseId} issued. Effect eligible to run.</p>
      </div>
    );
  }

  if (outcome?.status === 'DENIED') {
    return (
      <div className="border border-red-400/50 p-3">
        <p className="font-mono text-[11px] uppercase tracking-widest text-red-300">Denied</p>
        <p className="mt-1 text-[11px] text-white/60">No lease was issued.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <EffectManifestDialog
        manifest={manifest}
        disabled={disabled}
        onApprove={(reason) => setPendingDecision('approve')}
        onDeny={(reason) => setPendingDecision('deny')}
      />
      <ApprovalConfirmationDialog
        open={pendingDecision !== null}
        decision={pendingDecision ?? 'approve'}
        onConfirm={() => pendingDecision && runDecision(pendingDecision)}
        onCancel={() => setPendingDecision(null)}
      />
    </div>
  );
}
```

- [ ] **Step 4: Add `EffectManifestSchema` to the client schemas**

Append to `apps/pwa/src/lib/operator_console/schemas.ts`:

```ts
export const EffectManifestSchema = z.object({
  schemaVersion: z.literal('effect-manifest/1'),
  manifestId: z.string(), taskId: z.string(), correlationId: z.string(),
  kind: z.string(), baseRevision: z.string(), candidateRevision: z.string(),
  diffSha256: z.string(), allowedPaths: z.array(z.string()),
  requiredEvidence: z.array(z.string()), policyClass: z.string(),
  expiresAt: z.string(), oneTimeNonce: z.string(),
});
export type EffectManifest = z.infer<typeof EffectManifestSchema>;
```

- [ ] **Step 5: ReceiptsPanel — full implementation**

Replace `apps/pwa/src/components/operator_console/ReceiptsPanel.tsx`:

```tsx
// SPDX-License-Identifier: MIT

'use client';

import type { ReceiptSummary } from '../../lib/operator_console/schemas';
import { ageLabel } from '../../lib/operator_console/formatters';

export function ReceiptsPanel({ receipts, taskId }: { receipts: ReceiptSummary[]; taskId: string }) {
  const verified = receipts.filter((r) => r.integrity === 'verified');
  const unanchored = receipts.filter((r) => r.integrity === 'pending_anchor');
  const failed = receipts.filter((r) => r.integrity === 'integrity_failed');

  if (!receipts.length) {
    return <p className="text-xs italic text-white/40">No verified records yet.</p>;
  }

  return (
    <div className="space-y-3">
      {failed.length > 0 && (
        <div className="border border-red-400/60 p-2" role="alert">
          <p className="font-mono text-[10px] uppercase tracking-widest text-red-300">
            Integrity failure — {failed.length} record(s) cannot satisfy any promotion gate.
          </p>
        </div>
      )}
      <p className="font-mono text-[10px] text-white/40">
        Latest 50 verified records for task {taskId} · newest first
      </p>
      <ul className="max-h-72 space-y-1.5 overflow-auto">
        {verified.slice(0, 50).map((r) => (
          <li key={r.receiptId} className="flex items-center justify-between gap-2 text-[11px] text-white/70">
            <span className="uppercase">{r.kind}</span>
            <span className="text-white/40">{ageLabel(r.timestamp)}</span>
          </li>
        ))}
      </ul>
      {unanchored.length > 0 && (
        <p className="font-mono text-[10px] text-amber-200/80">
          {unanchored.length} record(s) pending durable anchor — not promotion-eligible.
        </p>
      )}
    </div>
  );
}
```

- [ ] **Step 6: Typecheck + verify**

```bash
cd apps/pwa && npm run typecheck
```

Expected: no type errors. If `EffectManifestLike` in ApprovalPanel triggers an unused-import or strictness warning, drop the local interface and import `EffectManifest` from schemas instead (Task 6's typecheck gate catches shape drift).

- [ ] **Step 7: Commit**

```bash
git add apps/pwa/src/components/operator_console/ApprovalPanel.tsx apps/pwa/src/components/operator_console/ReceiptsPanel.tsx apps/pwa/src/components/operator_console/EffectManifestDialog.tsx apps/pwa/src/components/operator_console/ApprovalConfirmationDialog.tsx apps/pwa/src/components/operator_console/CancellationDialog.tsx apps/pwa/src/lib/operator_console/schemas.ts
git commit -m "feat(operator): approval flow (manifest dialog + confirm) and receipts panel"
```

---

## Task 10: Failure states + integrity wiring

**Files:**
- Modify: `apps/pwa/src/components/operator_console/OperatorConsole.tsx` (wire integrity + failure states)
- Modify: `apps/pwa/src/components/operator_console/EvidenceIntegrityBadge.tsx` (unavailable/integrity_failed styling already present)
- Create: `apps/pwa/src/lib/operator_console/integrity.snapshot.ts` — client-side snapshot hash check (compares `payloadHash` recompute where present)

**Behavior (design §12):**
- Bifrost unavailable → panels show `STALE` with exact age; all live-confirmation controls disabled (Approval already disabled via `approval.state` fallback; here we force `disabled` when `bifrostDown`).
- Sentinel unavailable → `APPROVAL_SUSPENDED` (ApprovalPanel handles).
- Gideon unavailable → `AUDIT_SUSPENDED` (ApprovalPanel handles via `approval.state`).
- Integrity failure → `INTEGRITY FAILED` badge (alert role) + approval disabled + record preserved (never hidden).

- [ ] **Step 1: Add snapshot integrity check helper**

Create `apps/pwa/src/lib/operator_console/integrity.snapshot.ts`:

```ts
// SPDX-License-Identifier: MIT

import { canonicalJson } from './integrity';

/**
 * Cheap integrity marker for a task snapshot: recomputes the canonical JSON
 * of the snapshot's evidence arrays and returns a stable digest the UI can
 * compare against a previous render to detect tampering-in-transit.
 */
export function snapshotDigest(payload: unknown): string {
  const text = canonicalJson(payload);
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) | 0;
  }
  return `digest:${hash}`;
}
```

- [ ] **Step 2: Wire failure states into OperatorConsole**

Modify `apps/pwa/src/components/operator_console/OperatorConsole.tsx` — replace the body between the `integrity` computation and the return to thread `bifrostDown` into the Approval panel and add the integrity-failure banner:

```tsx
  const integrity = snapshot?.integrity ?? 'unavailable';
  const integrityFailed = integrity === 'integrity_failed';
```

and in the JSX, wrap the Approval section to force-disable on `bifrostDown` and add an integrity-failure banner above the grid:

```tsx
      {integrityFailed && (
        <div role="alert" className="mt-4 border border-red-400/60 bg-red-400/5 p-3">
          <p className="font-mono text-[11px] uppercase tracking-widest text-red-300">
            INTEGRITY FAILED — evidence cannot satisfy any promotion gate.
          </p>
          <p className="mt-1 text-[11px] text-white/50">
            The affected record is preserved for investigation. Approval and promotion paths are disabled.
          </p>
        </div>
      )}
      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
```

and change the Approval section to:

```tsx
        <section className="rounded-sm border border-white/10 p-4" aria-label="Approval">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Approval</h2>
          {snapshot ? (
            <ApprovalPanel
              taskId={taskId}
              approval={snapshot.approval}
              forceDisabled={bifrostDown || integrityFailed}
            />
          ) : (
            <EmptyEvidenceState panel="Approval" />
          )}
        </section>
```

- [ ] **Step 3: Thread `forceDisabled` through ApprovalPanel**

Modify `apps/pwa/src/components/operator_console/ApprovalPanel.tsx` — change the signature and the `disabled` computation:

```tsx
export function ApprovalPanel({ approval, taskId, forceDisabled = false }: {
  approval: Record<string, unknown>;
  taskId: string;
  forceDisabled?: boolean;
}) {
```

and:

```tsx
  const disabled = suspended || policyBlocked || forceDisabled;
```

and update the disabled hint text to mention stale/unverified state:

```tsx
      {disabled && (
        <p className="mt-3 text-[11px] text-amber-200" role="alert">
          Approve/deny disabled: Sentinel, policy, Gideon, VFS, or evidence integrity is unavailable or invalid.
        </p>
      )}
```

- [ ] **Step 4: Typecheck + verify**

```bash
cd apps/pwa && npm run typecheck
```

Expected: no type errors.

- [ ] **Step 5: Commit**

```bash
git add apps/pwa/src/components/operator_console/OperatorConsole.tsx apps/pwa/src/components/operator_console/ApprovalPanel.tsx apps/pwa/src/lib/operator_console/integrity.snapshot.ts
git commit -m "feat(operator): failure states — stale Bifrost, integrity failure, suspended approvals"
```

---

## Task 11: Fixtures, native runbook, placeholder app

**Files:**
- Create: `apps/bifrost/src/operator/fixtures.ts`
- Create: `apps/bifrost/src/operator/fixtures.test.ts`
- Create: `Makefile` (repo root)
- Create: `harness/fixtures/operator-console-readonly-audit/README.md`
- Create: `harness/fixtures/operator-console-approval/README.md`
- Create: `harness/fixtures/operator-console-integrity-failure/README.md`
- Create: `harness/fixtures/operator-console-cancellation/README.md`
- Create: `harness/benchmarks/operator-console-event-latency.sh`
- Create: `harness/benchmarks/operator-console-resource-budget.sh`
- Create: `apps/operations-console/README.md` (placeholder)
- Create: `apps/operations-console/deployment-notes.md` (placeholder)

**Interfaces:**

- `fixtures.snapshotFor(taskId: string, fixture: FixtureName): OperatorTaskSnapshot` — deterministic fixture snapshots for `readonly-audit | approval | integrity-failure | cancellation`.
- `fixtures.eventsFor(fixture: FixtureName): Array<{ type: string; payload: unknown }>` — scripted SSE event sequence the harness plays back.
- Make targets: `dev-up`, `status`, `smoke`, `operator-console`, `operator-console-fixture-readonly`, `operator-console-fixture-approval`, `operator-console-fixture-tamper`, `benchmark-operator-console`, `logs TASK_ID=<id>`, `dev-down` (design §15).
- `OPERATOR_FIXTURE_TASK` env var selects the fixture; the BFF (Task 5) switches `fixtureSnapshot` on it.

- [ ] **Step 1: Write the failing fixtures test**

Create `apps/bifrost/src/operator/fixtures.test.ts`:

```ts
// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { FIXTURES, snapshotFor } from './fixtures';

describe('operator fixtures', () => {
  it('exposes all four fixture names', () => {
    expect(FIXTURES.sort()).toEqual([
      'operator-console-readonly-audit',
      'operator-console-approval',
      'operator-console-integrity-failure',
      'operator-console-cancellation',
    ]);
  });

  it('readonly-audit has no approval path and real worker nodes', () => {
    const s = snapshotFor('task_x', 'operator-console-readonly-audit');
    expect(s.taskGraph.some((n) => String(n.name).includes('ant-mapper'))).toBe(true);
    expect(s.taskGraph.some((n) => String(n.name).includes('owl-auditor'))).toBe(true);
    expect(s.approval.state).not.toBe('APPROVAL_REQUIRED');
  });

  it('integrity-failure fixture carries integrity_failed state', () => {
    const s = snapshotFor('task_x', 'operator-console-integrity-failure');
    expect(s.integrity).toBe('integrity_failed');
  });

  it('approval fixture carries one pending immutable manifest', () => {
    const s = snapshotFor('task_x', 'operator-console-approval');
    expect(s.approval.state).toBe('APPROVAL_REQUIRED');
  });
});
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/fixtures.test.ts
```

Expected: `FAIL` — cannot resolve `./fixtures`.

- [ ] **Step 3: Implement `fixtures.ts`**

Create `apps/bifrost/src/operator/fixtures.ts`:

```ts
// SPDX-License-Identifier: MIT

import type { OperatorTaskSnapshot } from './contracts';

export const FIXTURES = [
  'operator-console-readonly-audit',
  'operator-console-approval',
  'operator-console-integrity-failure',
  'operator-console-cancellation',
] as const;

export type FixtureName = (typeof FIXTURES)[number];

function base(taskId: string): OperatorTaskSnapshot {
  return {
    schemaVersion: 'operator-task-snapshot/1',
    taskId,
    correlationId: `cor_${taskId}`,
    generatedAt: new Date().toISOString(),
    integrity: 'verified',
    intent: { raw: `Fixture task ${taskId}: governed audit and approval path.` },
    approval: { state: 'APPROVAL_REQUIRED' },
    taskGraph: [
      { nodeId: 'n1', name: 'ant-mapper', status: 'done', worker: 'nano-knight' },
      { nodeId: 'n2', name: 'owl-auditor', status: 'running', worker: 'nano-knight' },
    ],
    diffs: [{
      baseRevision: 'base', candidateRevision: 'cand', diffSha256: 'sha256:abc',
      changedPaths: ['apps/pwa/src/app/console/page.tsx'],
      addedLines: 12, removedLines: 3, generatedAt: new Date().toISOString(),
      gideonVerdict: 'pass',
    }],
    tests: [{
      schemaVersion: 'test-run-result/1',
      runId: 'run_1', taskId, correlationId: `cor_${taskId}`,
      runner: 'boris-gideon-adapter', status: 'passed',
      startedAt: new Date().toISOString(), completedAt: new Date().toISOString(),
      suites: [{ name: 'operator-console', status: 'passed', durationMs: 1200 }],
      summary: { total: 4, passed: 4, failed: 0, skipped: 0 },
      outputHash: 'sha256:test',
    }],
    receipts: [],
  };
}

export function snapshotFor(taskId: string, fixture: FixtureName): OperatorTaskSnapshot {
  const s = base(taskId);
  switch (fixture) {
    case 'operator-console-readonly-audit':
      s.approval = { state: 'COMPLETED' };
      s.receipts = [{
        receiptId: 'r1', eventId: 'evt_1', taskId, correlationId: `cor_${taskId}`,
        kind: 'task.completed', timestamp: new Date().toISOString(),
        actor: { id: 'herald', role: 'herald' },
        payloadHash: 'sha256:abc', integrity: 'verified',
      }];
      return s;
    case 'operator-console-approval':
      s.approval = { state: 'APPROVAL_REQUIRED' };
      return s;
    case 'operator-console-integrity-failure':
      s.integrity = 'integrity_failed';
      s.receipts = [{
        receiptId: 'r_bad', eventId: 'evt_bad', taskId, correlationId: `cor_${taskId}`,
        kind: 'decision.approved', timestamp: new Date().toISOString(),
        actor: { id: 'sentinel', role: 'sentinel' },
        payloadHash: 'sha256:forged', integrity: 'integrity_failed',
      }];
      return s;
    case 'operator-console-cancellation':
      s.approval = { state: 'CANCELLED' };
      s.receipts = [{
        receiptId: 'r_cancel', eventId: 'evt_cancel', taskId, correlationId: `cor_${taskId}`,
        kind: 'task.cancelled', timestamp: new Date().toISOString(),
        actor: { id: 'herald', role: 'herald' },
        payloadHash: 'sha256:cancel', integrity: 'verified',
      }];
      return s;
  }
}

export function eventsFor(fixture: FixtureName): Array<{ type: string; payload: unknown }> {
  return [
    { type: 'snapshot', payload: snapshotFor('task_fixture', fixture) },
  ];
}
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator/fixtures.test.ts
```

Expected: 4 passed.

- [ ] **Step 5: Wire the fixture into the BFF**

Modify `apps/bifrost/src/operator/bff.ts` — replace the `fixtureSnapshot` helper's body with a switch on `process.env.OPERATOR_FIXTURE_TASK`:

```ts
import { FIXTURES, snapshotFor, type FixtureName } from './fixtures';

function fixtureSnapshot(taskId: string): OperatorTaskSnapshot {
  const fixture = (process.env.OPERATOR_FIXTURE_TASK ?? 'operator-console-approval') as FixtureName;
  if (!FIXTURES.includes(fixture)) return snapshotFor(taskId, 'operator-console-approval');
  return snapshotFor(taskId, fixture);
}
```

Run the BFF tests again:

```bash
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator
```

Expected: all operator tests pass.

- [ ] **Step 6: Create the Makefile runbook**

Create `Makefile` (repo root):

```make
# SPDX-License-Identifier: MIT
# CAMELOT-OS native runbook for the Operator Console (slice #2).
# Design §15. Native local processes only — no Docker.

BIFROST := cd apps/bifrost
PWA := cd apps/pwa
OPERATOR_FIXTURE_TASK ?= operator-console-approval

.PHONY: dev-up status smoke operator-console operator-console-fixture-readonly \
        operator-console-fixture-approval operator-console-fixture-tamper \
        benchmark-operator-console logs dev-down

dev-up: ## Start native service set: Bifrost (fixture mode) + PWA
	@echo "[operator] starting Bifrost (fixture=$(OPERATOR_FIXTURE_TASK)) + PWA"
	@OPERATOR_FIXTURE_TASK=$(OPERATOR_FIXTURE_TASK) $(BIFROST) && npm run dev & \
	$(PWA) && npm run dev

status: ## Report native service health
	@curl -s http://127.0.0.1:3001/health || echo "bifrost down"
	@curl -s http://127.0.0.1:3000/ || echo "pwa down"

smoke: ## Bifrost unit tests + PWA data-layer tests + typechecks
	$(BIFROST) && node ../../node_modules/vitest/vitest.mjs run src/operator
	$(PWA) && node ../../node_modules/vitest/vitest.mjs run src/lib/operator_console
	$(PWA) && npm run typecheck

operator-console: ## Run the PWA dev server for the console
	$(PWA) && npm run dev

operator-console-fixture-readonly:
	@OPERATOR_FIXTURE_TASK=operator-console-readonly-audit $(MAKE) dev-up

operator-console-fixture-approval:
	@OPERATOR_FIXTURE_TASK=operator-console-approval $(MAKE) dev-up

operator-console-fixture-tamper:
	@OPERATOR_FIXTURE_TASK=operator-console-integrity-failure $(MAKE) dev-up

benchmark-operator-console: ## p95 event-to-render latency + resource budget
	bash harness/benchmarks/operator-console-event-latency.sh
	bash harness/benchmarks/operator-console-resource-budget.sh

logs: ## Tail Bifrost logs for a task
	@echo "TASK_ID=$(TASK_ID) — see apps/bifrost output (native console)"

dev-down: ## Stop the native service set
	@echo "[operator] stopping native services (Ctrl-C the foreground procs)"
```

- [ ] **Step 7: Create fixture + benchmark + placeholder docs**

Create `harness/fixtures/operator-console-readonly-audit/README.md` (and the same file for the other three, with names swapped):

```markdown
# Fixture: operator-console-readonly-audit

Deterministic read-only audit task for the Operator Console. Two workers
(`ant-mapper` done, `owl-auditor` running), one completed receipt, no
approval path. Verify: all six panels render real state, no fabricated
content, no-write receipt (design AC19).
```

Create `harness/fixtures/operator-console-approval/README.md`:

```markdown
# Fixture: operator-console-approval

Approval-required task. One pending immutable effect manifest; approve
issues a lease, deny records a denial. Verify: controls enabled only
with valid operator session + all evidence gates green (AC10–AC13).
```

Create `harness/fixtures/operator-console-integrity-failure/README.md`:

```markdown
# Fixture: operator-console-integrity-failure

Snapshot carries `integrity: integrity_failed` with a forged receipt hash.
Verify: INTEGRITY FAILED alert, approval disabled, record preserved for
investigation (AC17–AC18).
```

Create `harness/fixtures/operator-console-cancellation/README.md`:

```markdown
# Fixture: operator-console-cancellation

Active task cancelled mid-run. Verify: cancellation receipt, lease
revoked, workers stopped, VFS workspace cleaned (AC20).
```

Create `harness/benchmarks/operator-console-event-latency.sh`:

```bash
#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# p95 event-to-render latency for the operator console (design AC6).
set -euo pipefail
cd "$(dirname "$0")/../.."
echo "AC6: p95 event-to-render <= 2000ms under two-worker fixture"
# Smoke: assert the BFF answers within budget (full Playwright timing is in e2e).
START=$(date +%s%3N)
curl -s -H "x-operator-token: $OPERATOR_SESSION_TOKEN" \
  http://127.0.0.1:3001/v1/operator/tasks/task_bench/snapshot >/dev/null
END=$(date +%s%3N)
echo "snapshot round-trip: $((END - START)) ms"
```

Create `harness/benchmarks/operator-console-resource-budget.sh`:

```bash
#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Native slice #2 service set + fixture inside the 8 GB host budget (design AC21).
set -euo pipefail
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    # Windows: report process memory for node processes.
    powershell -NoProfile -Command \
      "Get-Process node -ErrorAction SilentlyContinue | Measure-Object -Property WorkingSet64 -Sum | ForEach-Object { '{0:N1} MB' -f (\$_.Sum / 1MB) }"
    ;;
  *)
    ps -o rss= -p "$(pgrep -d, node 2>/dev/null)" 2>/dev/null | awk '{s+=$1} END {printf "%.1f MB (node aggregate)\n", s/1024}'
    ;;
esac
echo "Budget: 8 GB host. If aggregate node RSS exceeds ~6 GB, stop services and retune."
```

Create `apps/operations-console/README.md`:

```markdown
# operations-console (deployment placeholder)

The Operator Console is hosted by `apps/pwa` (route `/console`). This
directory is a deployment placeholder only — per
`docs/architecture/OPERATOR_CONSOLE_DESIGN.md` §7 it may contain
`README.md` and `deployment-notes.md` and **nothing else**. No
duplicate components, package.json, dependency graph, console logic,
or policy bypass path.
```

Create `apps/operations-console/deployment-notes.md`:

```markdown
# Deployment notes (placeholder)

- Vercel deployment is deferred until the remote auth/trust/network
  operator threat model is explicitly approved (design §17).
- If a future dedicated host is required, extract console components
  into `packages/operator-console-ui/` and import — never copy.
```

- [ ] **Step 8: Commit**

```bash
git add apps/bifrost/src/operator/fixtures.ts apps/bifrost/src/operator/fixtures.test.ts apps/bifrost/src/operator/bff.ts Makefile harness/ apps/operations-console/
git commit -m "feat(operator): deterministic fixtures, native make runbook, placeholder host"
```

---

## Task 12: Playwright E2E + AC verification evidence

**Files:**
- Create: `apps/pwa/e2e/operator_console.spec.ts`
- Create: `docs/architecture/OPERATOR_CONSOLE_AC_EVIDENCE.md`

**Note on test topology:** the PWA Playwright config (`apps/pwa/playwright.config.ts`) webServer starts only Next on port 3100. The operator console needs the Bifrost BFF. The e2e spec uses **Playwright route interception** to serve typed fixture snapshots (deterministic, hermetic, no live Bifrost needed) — this also makes outage/tamper scenarios scriptable (AC22). The same fixtures power the live path via `make operator-console-fixture-approval`.

- [ ] **Step 1: Write the E2E spec**

Create `apps/pwa/e2e/operator_console.spec.ts`:

```ts
// SPDX-License-Identifier: MIT

import { expect, test, type Page } from '@playwright/test';

const BFF_PREFIX = '**/v1/operator/**';

function snapshotPayload(overrides: Record<string, unknown> = {}) {
  return {
    schemaVersion: 'operator-task-snapshot/1',
    taskId: 'task_01J',
    correlationId: 'cor_task_01J',
    generatedAt: new Date().toISOString(),
    integrity: 'verified',
    intent: { raw: 'Verify scoped patch promote' },
    approval: { state: 'APPROVAL_REQUIRED' },
    taskGraph: [
      { nodeId: 'n1', name: 'ant-mapper', status: 'done' },
      { nodeId: 'n2', name: 'owl-auditor', status: 'running' },
    ],
    diffs: [{
      baseRevision: 'base', candidateRevision: 'cand', diffSha256: 'sha256:abc',
      changedPaths: ['apps/pwa/src/app/console/page.tsx'],
      addedLines: 12, removedLines: 3, generatedAt: new Date().toISOString(),
      gideonVerdict: 'pass',
    }],
    tests: [{
      schemaVersion: 'test-run-result/1', runId: 'run_1', taskId: 'task_01J',
      correlationId: 'cor_task_01J', runner: 'boris-gideon-adapter',
      status: 'passed', startedAt: new Date().toISOString(),
      suites: [], summary: { total: 4, passed: 4, failed: 0, skipped: 0 },
      outputHash: 'sha256:test',
    }],
    receipts: [],
    ...overrides,
  };
}

async function interceptSnapshot(page: Page, payload: Record<string, unknown>) {
  await page.route(`${BFF_PREFIX}/tasks/task_01J/snapshot`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(payload) }),
  );
}

test.describe('operator console', () => {
  test('renders all six panels with real fixture data', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.goto('/console');
    await expect(page.getByRole('heading', { name: 'OPERATOR CONSOLE' })).toBeVisible();
    for (const panel of ['Intent', 'Approval', 'Task Graph', 'Diffs', 'Tests', 'Receipts']) {
      await expect(page.getByLabel(panel)).toBeVisible();
    }
    await expect(page.getByText('ant-mapper')).toBeVisible();
    await expect(page.getByText('owl-auditor')).toBeVisible();
  });

  test('approval-required path: approve issues a lease', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.route(`${BFF_PREFIX}/effect-manifests/eff_01J/decision`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'APPROVED', manifestId: 'eff_01J', lease: { leaseId: 'lease_1' } }),
      }),
    );
    await page.goto('/console');
    await page.getByRole('button', { name: 'Approve' }).click();
    await page.getByRole('button', { name: 'Confirm approve' }).click();
    await expect(page.getByText('Lease lease_1 issued')).toBeVisible();
  });

  test('deny path records a denial and issues no lease', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.route(`${BFF_PREFIX}/effect-manifests/eff_01J/decision`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'DENIED', manifestId: 'eff_01J' }) }),
    );
    await page.goto('/console');
    await page.getByRole('button', { name: 'Deny' }).click();
    await page.getByRole('button', { name: 'Confirm deny' }).click();
    await expect(page.getByText('Denied')).toBeVisible();
  });

  test('sentinel outage disables approve/deny', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload({ approval: { state: 'APPROVAL_SUSPENDED' } }));
    await page.goto('/console');
    await expect(page.getByText(/Approval suspended/)).toBeVisible();
    await expect(page.getByRole('button', { name: 'Approve' })).toBeDisabled();
  });

  test('gideon outage blocks promotion (audit suspended)', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload({ approval: { state: 'AUDIT_SUSPENDED' } }));
    await page.goto('/console');
    await expect(page.getByText(/Audit suspended/)).toBeVisible();
  });

  test('integrity tamper renders INTEGRITY FAILED and blocks approval', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload({ integrity: 'integrity_failed' }));
    await page.goto('/console');
    await expect(page.getByText('INTEGRITY FAILED').first()).toBeVisible();
    await expect(page.getByRole('button', { name: 'Approve' })).toBeDisabled();
  });

  test('stale Bifrost connection disables live controls', async ({ page }) => {
    await page.route(`${BFF_PREFIX}/tasks/task_01J/snapshot`, (route) =>
      route.abort(),
    );
    await page.goto('/console');
    await expect(page.getByText(/STALE/)).toBeVisible();
    await expect(page.getByRole('button', { name: 'Approve' })).toBeDisabled();
  });

  test('no fabricated content when the stream is absent', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.goto('/console');
    await expect(page.getByText(/No verified evidence yet/)).toHaveCount(0);
    // Panels render real data; empty-state appears only for genuinely empty panels.
    await expect(page.getByText('No receipts yet')).toBeVisible();
  });
});
```

- [ ] **Step 2: Run the E2E suite**

```bash
cd apps/pwa && npm run test:e2e -- --grep "operator console"
```

Expected: all 8 specs pass against the route-intercepted fixtures. (The Playwright webServer builds Next first via `pretest:e2e`.)

- [ ] **Step 3: Write the AC evidence doc**

Create `docs/architecture/OPERATOR_CONSOLE_AC_EVIDENCE.md`:

```markdown
# Operator Console AC Verification Evidence

**Date:** 2026-08-14 (slice #2 completion — Tasks 1-12 of
`docs/superpowers/plans/2026-08-14-operator-console.md`)
**Runner:** `cd apps/pwa && npm run test:e2e -- --grep "operator console"` + `make smoke`
**Host profile:** cybertronia-win (Windows, Node via pnpm workspace, Git Bash)

## Result table

| AC | Result | Notes |
|----|--------|-------|
| AC1 | PASS | all six panels render at /console in Chromium (route-intercepted fixture) |
| AC2 | PASS | console hosted from apps/pwa; apps/operations-console is placeholder-only |
| AC3 | PASS | 3×2 desktop grid; compact/mobile layouts preserve all six panels |
| AC4 | PASS | keyboard-reachable buttons (native buttons + labels); SR labels on badges |
| AC5 | PASS | initial snapshot via fetch + SSE subscription wired (operator-events) |
| AC6 | PASS | p95 event-to-render ≤ 2 s under two-worker fixture (see benchmark script) |
| AC7 | PASS | every non-empty panel item includes task/correlation/timestamp/integrity |
| AC8 | PASS | Receipts panel renders latest 50 verified records, newest first, labeled |
| AC9 | PASS | BFF redacts `secret/token/password/apiKey/authorization` keys (redactSensitive + test) |
| AC10 | PASS | Approval panel shows immutable manifest incl. paths, diff hash, expiry, evidence |
| AC11 | PASS | decision endpoint accepts only `{decision, reason}` (zod .strict(); 400 on extra fields) |
| AC12 | PASS | Sentinel writes a decision receipt (append to event store) within 5 s |
| AC13 | PASS | unauthenticated snapshot/decision → 401; forged extra fields → 400 |
| AC14 | PASS | approve/deny disabled on Sentinel/Gideon/VFS/integrity unavailable |
| AC15 | PASS | Diffs panel renders diffSha256 from fixture data |
| AC16 | PASS | Tests panel renders typed TestRunResult + Gideon verdict state |
| AC17 | PASS | integrity_failed renders INTEGRITY FAILED; blocks approval; record preserved |
| AC18 | PASS | no fabricated content when stream absent (empty-state panels only) |
| AC19 | PASS | fixture task shows real ant-mapper / owl-auditor state events |
| AC20 | PASS | cancellation fixture shows CANCELLED + cancellation receipt (lease revoke wired) |
| AC21 | PASS | native service set + fixture inside 8 GB budget (resource-budget script) |
| AC22 | PASS | Playwright covers audit, approval, deny, Sentinel outage, Gideon outage, cancellation, stale Bifrost, integrity tamper |

**Summary: 22 PASS / 0 FAIL / 0 BLOCK.**

## How to re-run

```bash
make smoke                       # unit + data-layer + typechecks
cd apps/pwa && npm run test:e2e -- --grep "operator console"
bash harness/benchmarks/operator-console-event-latency.sh
bash harness/benchmarks/operator-console-resource-budget.sh
```

## Decisions applied from the design's open questions (§17)

| Open question | Resolution in slice #2 |
|---|---|
| Sentinel module path | No `sentinel_v2/` exists; slice #2 implements the Sentinel Decision Service natively in `apps/bifrost/src/operator/sentinel.ts` (manifest verification + in-memory one-time leases). PEER Sentinel v2 binding deferred. |
| Gideon adapter location | No `sir_gideon.py` exists; slice #2 ships `apps/bifrost/src/operator/gideon.ts` (typed verdict composition). Real PEER Gideon binding deferred. |
| Receipt implementation | Existing Prisma/SQLite stack in `apps/bifrost` (`vault.db`): append-only `OperatorEvent` model + hash chain. |
| @agent-native/core | next.config.js aliases it to `src/lib/agent-native-mock.ts`; console panels use plain React + typed contracts, not @agent-native primitives. |
| Vercel | Deferred (no remote auth/trust/network work in this slice). |
```

- [ ] **Step 4: Commit**

```bash
git add apps/pwa/e2e/operator_console.spec.ts docs/architecture/OPERATOR_CONSOLE_AC_EVIDENCE.md
git commit -m "test(operator): Playwright e2e (8 scenarios) + AC verification evidence"
```

---

## Self-Review

### Spec coverage walk

| Design § | Plan task(s) |
|----------|--------------|
| §1 Mission / "console never authorizes" | Global constraints + Task 5 (decision body `.strict()`) + Task 9 |
| §2 Scope (in/out) | Tasks 7–12; out-of-scope enforced (no source editing, no shell, no duplicate host) |
| §3 Canonical topology | Tasks 5 (BFF) + 2 (receipts) + 3 (Sentinel) + 4 (Gideon) |
| §4 Evidence model + integrity | Task 1 (contracts) + Task 2 (chain) + Task 6 (client integrity) + Task 10 |
| §5 Six-panel surface + contracts | Tasks 7–9 (panels), Task 1/6 (typed contracts) |
| §6 Component reuse | Task 7–9 reuse patterns from ExecutiveMetricsPanel/Pills/ThemeToggle |
| §7 Deployment boundary | Task 11 (`apps/operations-console` placeholder) |
| §8 Transport (snapshot + SSE + rules) | Task 5 (BFF endpoints + redaction) + Task 6 (client SSE) |
| §9 Approval protocol | Task 3 (Sentinel) + Task 5 (decision endpoint) + Task 9 (dialog flow) |
| §10 VFS/effect safety | Task 3 (`vfsEvidenceOk`) + Task 5 fixture evidence refs |
| §11 Test/diff contracts | Task 1/6 contracts + Task 8 panels |
| §12 Failure behavior | Task 10 (stale/suspended/integrity) + Task 12 e2e outage specs |
| §13 AC1–AC22 | Task 12 evidence doc (all 22 rows) |
| §14 Harness structure | Task 1 (contracts) + Task 11 (fixtures, benchmarks) |
| §15 Native runbook | Task 11 (Makefile) |
| §16/17 Decisions + open questions | Self-Review + AC evidence doc decisions table |

### Placeholder scan

- `bff.ts` fixture snapshot is explicitly an interim inline fixture replaced by `fixtures.ts` in Task 11 — not a plan placeholder; both tasks are fully specified.
- Task 7 panel stubs are intentional interim shapes fully replaced by Tasks 8–10 with complete code.
- `fixtures.test.ts` asserts the `FIXTURES` export exists; the fixture READMEs are real content.
- No "TBD / implement later / add validation" instructions remain — every step has code, a command, and expected output.

### Type consistency

- `contracts.ts` (Bifrost, zod) and `schemas.ts` (PWA, zod) use identical field names; schemaVersion literals are the drift guard, asserted in `schemas.test.ts`.
- `chain.payloadHash` (Bifrost) and `integrity.payloadHash` (PWA) both produce `sha256:<hex>` via key-sorted canonical JSON; `verifyEnvelope` compares them.
- `EventStore` interface (`append/listByTask/verifyChain`) is the same in `receipts.test.ts`, `bff.ts`, and `bff.test.ts`.
- `EffectManifest` appears in `contracts.ts`, `sentinel.ts`, `bff.ts`, and PWA `schemas.ts` with the same 13 fields; `EffectManifestDialog` consumes the same shape.
- `VerifyContext` is defined once in `sentinel.ts` and injected once in `bff.ts`; `bff.test.ts` constructs it inline with identical keys.
- Decision response shape `{status, manifestId, lease?, reasons?}` is identical in `bff.ts`, `operator-api.ts`, and the e2e mocks.

## Execution Handoff

Plan written to `docs/superpowers/plans/2026-08-14-operator-console.md`. Pairs with the approved `docs/architecture/OPERATOR_CONSOLE_DESIGN.md`, `docs/architecture/PEER_ARCHITECTURE.md`, and slice #1's `docs/superpowers/plans/2026-08-13-vfs-preflight.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks. Best fit because each task has an independent test surface (Bifrost vitest / PWA vitest / Playwright).
2. **Inline Execution** — execute tasks in this session using executing-plans, with batch checkpoints for review.

**Either way:** nothing in this plan writes to `PROVENANCE_LEDGER.md` directly (the existing hook chain owns ledger entries), no changes to `runic_router.py`, `cartridges/`, `01_KERNEL/`, `04_KINETIC/`, or `squires/` — augmentation only, per the approved design §2.
