┌─────────────────────────────────────────────────────────────────┐
│ Anya PWA / Operator Console                                     │
│ Intent · approval · task graph · diffs · tests · receipts       │
└─────────────────────────────────────────────────────────────────┘
Status: Approved — forged for implementation
Date: 2026-08-14
Tier: APEX — Surface Architecture
Vertical Slice: #2 of 5 — follows VFS Preflight / Cartridge Load Gate
Substrate: PEER-aligned
Canonical host: apps/pwa
Console route: apps/pwa/src/app/console/page.tsx
Component home: apps/pwa/src/components/operator_console/
Runtime: Native, local-first, policy-governed; no Docker or Kubernetes.

Co-equal architecture documents

docs/architecture/PEER_ARCHITECTURE.md

docs/architecture/VFS_PREFLIGHT_DESIGN.md

docs/adr/0006-vfs-preflight-strict-mode.md

PROVENANCE_LEDGER.md

.hive/TITANIUM_LAWS.md

1. Mission
The Operator Console is Camelot’s human-facing read-rich, write-on-approval surface for governed engineering work.

It allows an authenticated operator to:

Inspect the active intent, plan, task graph, diffs, tests, resource state, and receipts.

Review an immutable effect manifest before approval.

Approve or deny only that exact effect manifest.

Observe verification, lease issuance, execution outcome, revocation, cleanup, and final receipt.

The console never directly edits source code, invokes an unrestricted shell, issues its own capability leases, accesses secrets, or bypasses Sentinel.

text
Intent is not authority.
A plan is not authority.
A model response is not authority.
A console click is not authority.

Only Sentinel-issued, scoped, expiring capability leases
permit a host-verified effect.
The PEER substrate remains authoritative:

text
Anya       -> Plan and expression policy
Merlin     -> Orchestration and runtime selection
HiVeiDe    -> Repository map, task DAG, lock coordination
Nano-Knights -> Bounded execution
Sentinel   -> Policy, halt decision, lease issuance, revocation
Gideon     -> Independent diff, test, security, and lifecycle verification
Herald     -> Receipt and operator-facing evidence expression
The project’s existing architecture defines distinct Planner, Executor, Verifier, and Generator roles. The Operator Console must preserve this separation in both UI and backend contracts.

2. Scope
In scope
A six-panel operator console in the Anya PWA.

Typed snapshots and Server-Sent Event streams from Bifrost.

Immutable, correlation-scoped evidence records.

Read-only rendering of intent, task graph, diff evidence, test results, and receipts.

Manifest-scoped approve/deny flow through Sentinel.

Explicit unavailable, unverified, stale, and integrity-failure UI states.

Playwright end-to-end coverage for the governed audit and approval fixture.

Native local-process operation under the 8 GB resource budget.

Out of scope
Editing source code in the console.

Automatic merge, deployment, deletion, migration, messaging, or external action.

General-purpose terminal access.

Arbitrary agent thought-stream display or hidden reasoning storage.

Cloud routing, VPS hosting, remote multi-tenant operation, or external browser automation.

Replacing Dashboard.tsx, AGNO Studio, or existing kernel components.

Duplicating the PWA source tree into apps/operations-console/.

Docker, Kubernetes, or container-dependent local execution.

3. Canonical topology
text
┌──────────────────────────────────────────────────────────┐
│ Operator                                                  │
│ Anya PWA: /console                                        │
└───────────────────────┬──────────────────────────────────┘
                        │ snapshots + SSE
┌───────────────────────▼──────────────────────────────────┐
│ Bifrost Operator BFF                                      │
│ authenticated · redacted · schema validated               │
└───────────────┬─────────────────────────────┬────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│ Receipt/Event Service      │   │ Sentinel Decision Service │
│ append-only local records  │   │ policy · lease · revoke   │
│ hash chain · manifests     │   │ effect-manifest validation│
└───────────────┬───────────┘   └──────────────┬───────────┘
                │                              │
                ▼                              ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│ Ledger Anchor Writer       │   │ PEER / Engineering Plane  │
│ selected signed summaries  │   │ Anya · Merlin · HiVeiDe   │
│ -> PROVENANCE_LEDGER.md    │   │ Knights · Gideon · Boris  │
└───────────────────────────┘   └──────────────────────────┘
Truth hierarchy
Layer	Responsibility	Canonical status
Receipt/Event Service	Immutable runtime event record and evidence chain	Canonical operational truth
Sentinel	Policy decision, lease issuance, revocation	Canonical effect authority
Gideon	Independent verification verdict	Canonical quality gate
PROVENANCE_LEDGER.md	Human-readable signed/hashed evidence anchor	Canonical durable projection
Bifrost	Validated, redacted read/stream transport	Transport only
Operator Console	Human-facing rendering and approval request	Never authoritative
PROVENANCE_LEDGER.md remains a critical evidence anchor, but it is not the live event bus. Runtime control flow must not depend on Git commits, filesystem polling, or Markdown parsing.

4. Evidence model
All panel data uses a common evidence envelope.

ts
export type EvidenceIntegrity =
  | "verified"
  | "pending_anchor"
  | "integrity_failed"
  | "unavailable";

export type EvidenceEnvelope<TPayload> = {
  schemaVersion: "operator-evidence/1";
  eventId: string;
  taskId: string;
  correlationId: string;
  causationId?: string;

  timestamp: string;

  actor: {
    id: string;
    role:
      | "operator"
      | "anya"
      | "merlin"
      | "hiveide"
      | "nano_knight"
      | "sentinel"
      | "gideon"
      | "boris"
      | "herald"
      | "system";
  };

  kind: string;
  payload: TPayload;

  payloadHash: string;
  parentHash?: string;
  signatureOrMac?: string;

  integrity: EvidenceIntegrity;
  receiptRef?: string;
  ledgerAnchorRef?: string;
};
Required identifiers
Every operator-relevant event must include:

text
required:
  - event_id
  - task_id
  - correlation_id
  - timestamp
  - actor
  - kind
  - payload_hash
  - integrity
Integrity behavior
Integrity state	Meaning	UI behavior	Approval behavior
verified	Hash chain and receipt are valid	Normal evidence display	Eligible if all gates pass
pending_anchor	Event is valid but ledger anchoring is pending	Show “Pending durable anchor”	Not eligible for promotion
unavailable	Source cannot be reached	Show last verified state and age	Disabled
integrity_failed	Hash, signature, parent chain, or receipt verification failed	High-severity alert; show affected evidence reference	Disabled and blocking
The console must never reduce integrity_failed to a generic “audit unavailable” indicator.

5. Surface design
5.1 Six-panel architecture
text
┌──────────┬────────────┬──────────────┬───────┬───────┬───────────┐
│ Intent   │ Approval   │ Task Graph   │ Diffs │ Tests │ Receipts  │
└──────────┴────────────┴──────────────┴───────┴───────┴───────────┘
Default layout: responsive 3×2 desktop grid.
Compact mode: operator-selectable dense six-column data layout.
Mobile layout: ordered vertical panels with a persistent approval/cancel control bar.

5.2 Panel contracts
Panel	PEER binding	Read model	Operator action	Failure behavior
Intent	Anya / Plan	IntentRecord	None	Render signed raw intent and show advisory_unavailable if Anya formatting is absent
Approval	Sentinel / Review Gate	EffectManifest, HaltDecision	Approve or deny one immutable manifest	Disable all effects if Sentinel, policy, Gideon, or integrity state is invalid
Task Graph	HiVeiDe / Execute	DagNodeStatus[], path locks, worktree state	Cancel active task if policy permits	Show last verified state, stale timestamp, and worker/service condition
Diffs	Sentinel + Gideon / Review	DiffEvidence	Inspect only	Show unavailable or integrity-failed state; no promotion possible
Tests	Gideon + Boris / Review	TestRunResult, verifier result	Inspect only	Show audit suspension and block approval/promotion
Receipts	Herald + Anya / Express	ReceiptSummary[]	Inspect/export only	Display verified records only; label unanchored records separately
5.3 State hierarchy
Every panel uses one of the following visible state labels:

text
LIVE
STALE
PENDING DURABLE ANCHOR
UNAVAILABLE
INTEGRITY FAILED
POLICY BLOCKED
APPROVAL REQUIRED
COMPLETED
CANCELLED
Color cannot be the sole signal. Each state includes text, iconography, and accessible screen-reader labels.

6. Existing component reuse
Existing component	Path	Reuse in console
PlanCard.tsx	apps/pwa/src/components/PlanCard.tsx	Intent summary and structured plan presentation
ExecutiveMetricsPanel.tsx	apps/pwa/src/components/ExecutiveMetricsPanel.tsx	Approval counts, risk tier, and active lease metrics
Dashboard.tsx	apps/pwa/src/components/Dashboard.tsx	Layout and responsive panel composition patterns only
SwarmRosterPanel.tsx	apps/pwa/src/components/SwarmRosterPanel.tsx	Nano-Knight and task-worker status representation
OpenDesignStatusPills.tsx	apps/pwa/src/components/OpenDesignStatusPills.tsx	Verified, blocked, pending, and integrity-state pill patterns
ThemeToggle.tsx	apps/pwa/src/components/ThemeToggle.tsx	Theme control; console must remain usable in both themes
New component tree
text
apps/pwa/src/
  app/
    console/
      page.tsx
  components/
    operator_console/
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
  lib/
    operator_console/
      schemas.ts
      operator-api.ts
      operator-events.ts
      integrity.ts
      formatters.ts
Route
tsx
// apps/pwa/src/app/console/page.tsx

import { OperatorConsole } from "@/components/operator_console";

export default function OperatorConsolePage() {
  return <OperatorConsole />;
}
The PWA remains the canonical source and host for Slice #2.

7. Deployment boundary
apps/operations-console/ is not a second console application in this slice.

text
apps_operations_console:
  status: "deployment placeholder"
  source_of_truth: "apps/pwa"
  permitted_contents:
    - README.md
    - deployment-notes.md
  prohibited_in_slice_2:
    - duplicate_components
    - copied_package_json
    - divergent_dependency_graph
    - separate_console_logic
    - alternate_policy_bypass_path
If a future dedicated host is required, extract common console components into a versioned package:

text
packages/operator-console-ui/
Both hosts must then import that package rather than copy source files.

8. Data transport
8.1 Snapshot endpoint
text
GET /v1/operator/tasks/{taskId}/snapshot
Accept: application/json
Returns the current verified task projection.

json
{
  "schemaVersion": "operator-task-snapshot/1",
  "taskId": "task_01J...",
  "correlationId": "cor_01J...",
  "generatedAt": "2026-08-14T13:48:00Z",
  "integrity": "verified",
  "intent": {},
  "approval": {},
  "taskGraph": [],
  "diffs": [],
  "tests": [],
  "receipts": []
}
8.2 Event stream
text
GET /v1/operator/tasks/{taskId}/events
Accept: text/event-stream
Bifrost provides Server-Sent Events for Slice #2. The PWA uses React Query or SWR for initial snapshots and reconciliation; SSE provides incremental updates.

text
event: operator.evidence
id: evt_01J...
data: {"schemaVersion":"operator-evidence/1", "...":"..."}
8.3 Transport rules
text
bifrost_operator_bff:
  must:
    - authenticate_operator_session
    - authorize_task_visibility
    - validate_schema
    - redact_sensitive_fields
    - verify_receipt_reference_when_present
    - expose_last_verified_timestamp
  must_not:
    - construct_evidence
    - mint_leases
    - accept_raw_shell_commands
    - expose_secrets
    - expose_hidden_reasoning
    - turn_stale_evidence_into_live_state
9. Approval protocol
The Approval panel handles one exact effect manifest at a time.

text
effect_manifest:
  schema_version: "effect-manifest/1"
  manifest_id: "eff_01J..."
  task_id: "task_01J..."
  correlation_id: "cor_01J..."

  kind: "worktree.patch.promote"

  base_revision: "git-sha-base"
  candidate_revision: "git-sha-candidate"
  diff_sha256: "sha256:..."

  allowed_paths:
    - "apps/pwa/src/components/operator_console/**"

  required_evidence:
    - "receipt://vfs/no-escape/..."
    - "receipt://tests/operator-console/..."
    - "receipt://gideon/verdict/..."

  policy_class: "engineering.write"
  expires_at: "2026-08-14T14:05:00Z"
  one_time_nonce: "opaque-random-value"
Approval sequence
text
1. Operator opens the immutable effect manifest.
2. Console displays:
   - target action
   - task and correlation ID
   - changed paths
   - base/candidate revision
   - diff SHA-256
   - required VFS, test, and Gideon evidence
   - expiry time
3. Operator chooses Approve or Deny.
4. Console submits only:
   - manifest ID
   - decision
   - optional reason
   - authenticated operator session proof
5. Sentinel independently verifies:
   - operator identity and role
   - task visibility and policy
   - manifest integrity and expiry
   - required evidence integrity
   - current Gideon verdict
   - VFS constraints
6. Sentinel writes a decision receipt.
7. If approved, Sentinel issues one short-lived, non-transferable lease.
8. Host verifies lease before performing the exact manifest-bound effect.
9. Completion, failure, cancellation, or expiry revokes the lease.
Approval endpoint
text
POST /v1/operator/effect-manifests/{manifestId}/decision
Content-Type: application/json
json
{
  "decision": "approve",
  "reason": "Verified scoped patch and test evidence."
}
The endpoint never accepts direct command text, filesystem paths not already inside the manifest, raw diffs, shell instructions, or deployment instructions.

10. VFS and effect safety
The Operator Console relies on Slice #1 VFS Preflight evidence before it can render an effect as promotion-eligible.

text
required_vfs_evidence:
  - repository_revision_pinned
  - task_workspace_is_ephemeral
  - allowed_paths_normalized
  - no_path_escape_detected
  - protected_paths_denied
  - secrets_not_mounted_or_explicitly_scoped
  - network_mode_matches_lease
  - resource_budget_granted
  - workspace_cleanup_completed
The console may show VFS evidence but cannot generate, alter, or override it.

11. Test and diff contracts
Diff evidence
ts
export type DiffEvidence = {
  baseRevision: string;
  candidateRevision: string;
  diffSha256: string;
  changedPaths: string[];
  addedLines: number;
  removedLines: number;
  generatedAt: string;
  gideonVerdict?: "pass" | "fail" | "pending" | "unavailable";
  receiptRef: string;
};
Test result
ts
export type TestRunResult = {
  schemaVersion: "test-run-result/1";
  runId: string;
  taskId: string;
  correlationId: string;

  runner: "boris-gideon-adapter";
  status: "passed" | "failed" | "cancelled" | "timed_out";

  startedAt: string;
  completedAt?: string;

  suites: Array<{
    name: string;
    status: "passed" | "failed" | "skipped";
    durationMs: number;
    artifactRef?: string;
  }>;

  summary: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
  };

  outputHash: string;
  receiptRef: string;
};
The UI must consume these typed contracts, not raw output from test_runner_agent.py.

12. Failure behavior
Sentinel unavailable
text
Approval panel:
- State: APPROVAL SUSPENDED
- Existing manifests remain readable.
- Approve and Deny controls are disabled.
- Console states last verified policy timestamp.
- No lease can be issued.
Gideon unavailable
text
Diffs and Tests panels:
- State: AUDIT SUSPENDED
- Existing evidence remains readable if verified.
- Any promotion or write approval is blocked.
Bifrost unavailable
text
All panels:
- Render only locally cached verified evidence.
- Mark evidence as STALE with exact age.
- Disable all controls requiring live backend confirmation.
- Offer reconnect status; never fabricate active state.
Integrity failure
text
Affected panel:
- State: INTEGRITY FAILED
- Display event/receipt reference and failure class.
- Disable associated approval and promotion paths.
- Emit local operator-visible error telemetry.
- Preserve the record for investigation; never hide it.
13. Acceptance criteria
Surface
AC1: All six panels render at /console in Chromium using the Anya PWA development server.

AC2: The console is hosted from apps/pwa; no duplicate application source is created in apps/operations-console.

AC3: Desktop defaults to a responsive 3×2 grid; compact and mobile layouts preserve all six panels.

AC4: Keyboard-only navigation reaches every panel, disclosure, approve/deny button, and cancellation control.

Evidence and transport
AC5: The console receives an initial task snapshot from Bifrost and updates from SSE.

AC6: Under a local two-worker fixture task, p95 event-to-render latency is at most 2 seconds.

AC7: Every displayed non-empty panel item includes task ID, correlation ID, timestamp, integrity state, and receipt reference where applicable.

AC8: The Receipts panel renders the last 50 verified records matching the current task/correlation scope and explicitly labels sort order.

AC9: Bifrost redacts sensitive fields before evidence reaches the browser.

Policy and approval
AC10: The Approval panel displays the immutable effect manifest, including changed paths, diff hash, expiry, and required verification evidence.

AC11: Approve/deny submits only a manifest-scoped decision to Sentinel.

AC12: Sentinel writes a signed decision receipt within 5 seconds of a valid fixture decision.

AC13: A browser-forged request lacking valid operator authentication, manifest scope, or required evidence is denied.

AC14: Approval controls are disabled whenever Sentinel, policy, Gideon, VFS, or evidence integrity is unavailable or invalid.

Verification
AC15: The Diffs panel verifies that its displayed diff_sha256 matches the fixture diff artifact.

AC16: The Tests panel renders typed TestRunResult data and a Gideon verifier state.

AC17: A tampered ledger anchor or receipt hash renders INTEGRITY FAILED; it cannot satisfy a promotion gate.

AC18: No panel renders fabricated content when its stream is absent.

Lifecycle and resources
AC19: A fixture read-only task displays real Ant Mapper and Owl Auditor state events, not placeholder values.

AC20: Cancelling an active fixture task revokes the lease, stops workers, cleans the VFS workspace, and produces a cancellation receipt.

AC21: The native Slice #2 service set and two-worker fixture remain inside the declared 8 GB host budget.

AC22: Playwright covers the normal audit path, approval-required path, deny path, Sentinel outage, Gideon outage, cancellation, stale Bifrost connection, and integrity tamper path.

14. Harness structure
text
harness/
  contracts/
    operator-evidence.schema.json
    operator-task-snapshot.schema.json
    effect-manifest.schema.json
    halt-decision.schema.json
    diff-evidence.schema.json
    test-run-result.schema.json
    receipt-summary.schema.json

  fixtures/
    operator-console-readonly-audit/
    operator-console-approval/
    operator-console-integrity-failure/
    operator-console-cancellation/

  integration/
    operator-bff-sse.spec.ts
    sentinel-manifest-decision.spec.ts
    vfs-evidence-gate.spec.ts
    receipt-chain-integrity.spec.ts

  e2e/
    operator_console.spec.ts

  benchmarks/
    operator-console-event-latency.sh
    operator-console-resource-budget.sh

  golden/
    receipts/
    manifests/
    evidence-chains/
Required test matrix
Scenario	Expected result
Read-only audit	Real task graph, findings, no-write receipt
Approval required	Controls remain disabled until valid operator approval
Valid approval	Sentinel emits decision receipt and scoped lease
Denial	Sentinel records denial; no lease issued
Expired manifest	Approval rejected
Gideon failure	Promotion blocked
Sentinel outage	Approval suspended
Bifrost outage	Cached evidence is stale; controls disabled
Diff hash mismatch	Integrity failed; promotion blocked
Ledger anchor tamper	Integrity failed; evidence cannot satisfy a gate
Cancellation	Worker stop, lease revoke, cleanup receipt
Resource breach	Worker terminates safely with budget-failure receipt
15. Native runbook
bash
make dev-up
make status
make smoke
make operator-console
make operator-console-fixture-readonly
make operator-console-fixture-approval
make operator-console-fixture-tamper
make benchmark-operator-console
make logs TASK_ID=<task-id>
make dev-down
Suggested native process order:

text
1. Local state and SQLite validation
2. Receipt/Event Service
3. Sentinel Decision Service
4. VFS Guardian
5. HiVeiDe coordinator
6. Gideon/Boris adapter
7. Bifrost Operator BFF
8. Anya PWA
A missing service must produce a visible degraded state and block affected controls. No service may silently fall back to direct filesystem, network, or shell access.

Camelot’s target environment is native and resource-constrained; bare processes and explicit lifecycle scripts are the supported path.

16. Decisions log
#	Topic	Final decision
1	Slice placement	Slice #2 of 5, after VFS Preflight
2	Canonical host	apps/pwa is the only console application host in Slice #2
3	operations-console	Deployment placeholder only; no duplicate app or dependency graph
4	Data truth	Receipt/Event Service is operational truth; PROVENANCE_LEDGER.md is durable signed/hashed projection
5	Live updates	Bifrost SSE for events; React Query/SWR for snapshots and reconciliation
6	Approval	Sentinel-only, manifest-scoped, immutable, expiring, one-time approval
7	Integrity	verified, pending_anchor, unavailable, and integrity_failed are distinct states
8	Anya dependency	Anya governs presentation; deterministic raw-evidence fallback renders if Anya is unavailable
9	Git hooks	Hooks may anchor evidence but cannot be required for runtime control flow
10	Promotion	Gideon, VFS, policy, integrity, and human approval must all pass
11	Performance	No mandatory R3F/3D rendering in this slice; prioritize readable live evidence under budget
12	Authority	UI, Anya, Merlin, and Knights cannot mint leases or bypass Sentinel
17. Open questions
Sentinel module path: confirm whether control_plane/core/sentinel_v2/ or control_plane/security/sentinel_v2/ is canonical.

Gideon adapter location: confirm whether control_plane/core/sir_gideon.py is the intended adapter boundary.

Receipt implementation: determine whether SQLite-backed append-only event storage, an existing local ledger service, or another native receipt runtime is already preferred.

@agent-native/core: inspect exported primitives before writing panel-level interaction primitives.

Vercel deployment: defer until the remote auth, trust, network, and operator threat model is explicitly approved.

18. Operational law
text
Camelot governs.
Anya clarifies and expresses.
Merlin coordinates.
HiVeiDe maps and dispatches.
Nano-Knights execute bounded work.
Sentinel authorizes and revokes.
Gideon verifies independently.
The VFS contains writes.
The harness proves behavior.
The receipt records evidence.
The human approves consequential effects.
This vertical slice is complete only when the console proves the full governed path—from task evidence through policy and verification to a machine-checkable receipt—without needing an unbounded agent, duplicate UI host, direct filesystem access, or fabricated state.

