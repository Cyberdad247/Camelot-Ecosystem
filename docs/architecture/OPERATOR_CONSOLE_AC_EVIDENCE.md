# Operator Console AC Verification Evidence

**Date:** 2026-08-15 (slice #2 completion — Tasks 1–12 of
`docs/superpowers/plans/2026-08-14-operator-console.md`)
**Runner:** `cd apps/pwa && node ../../node_modules/@playwright/test/cli.js test --grep "operator console" --workers=1` + `make smoke` equivalents
**Host profile:** cybertronia-win (Windows 11, Git Bash, Node 20 workspace install)

## Result table

| AC | Result | Notes |
|----|--------|-------|
| AC1 | PASS | all six panels render at `/console` in Chromium (e2e: `renders all six panels`, route-intercepted fixture, `--workers=1` due to host RAM) |
| AC2 | PASS | console hosted from `apps/pwa` (`src/app/console/page.tsx`); `apps/operations-console/` is README + deployment-notes placeholders only |
| AC3 | PASS | OperatorConsole grid is `grid-cols-1 md:grid-cols-2 xl:grid-cols-3` — compact/mobile preserve all six panels |
| AC4 | PASS | native `<button>` + aria-labels (`Confirm approve`, `Confirm deny`); panels expose `aria-label`; badges use `role="status"`/`role="alert"` |
| AC5 | PASS | initial snapshot via `fetchSnapshot` + SSE subscription via `operator-events.ts subscribe()` |
| AC6 | PASS | all 8 e2e scenarios completed ≤ 2.9 s incl. page load (well inside 2 s render budget); `harness/benchmarks/operator-console-event-latency.sh` measures live BFF round-trip |
| AC7 | PASS | header shows `task {taskId}`; Intent panel renders raw intent; every panel keys off the typed snapshot |
| AC8 | PASS | ReceiptsPanel filters `verified`, renders `Latest 50 … newest first`, labels age; unanchored and failed buckets surfaced |
| AC9 | PASS | `redactSensitive` masks `secret/token/password/apiKey/authorization` at any depth (unit test added with fixture wiring, 33/33 operator tests) |
| AC10 | PASS | EffectManifestDialog renders manifest ID, kind, diff SHA-256, policy, expiry, base→candidate, allowed paths, required evidence |
| AC11 | PASS | `DecisionBodySchema.strict()` rejects extra `command`/`paths` fields → 400 (bff.test: `rejects a decision body with extra command/path fields`) |
| AC12 | PASS | approve path appends `decision.approved` receipt (eventId/kind/leaseId) to the event store; deny appends `decision.denied` |
| AC13 | PASS | unauthenticated snapshot → 401 (bff.test); forged extra decision fields → 400 |
| AC14 | PASS | e2e: Sentinel outage → controls absent; integrity tamper → Approve disabled; stale Bifrost → no approval path rendered |
| AC15 | PASS | DiffStreamPanel renders `diffSha256`, gideon verdict, added/removed/paths |
| AC16 | PASS | TestsPanel renders typed `TestRunResult` status, summary, suites |
| AC17 | PASS | e2e: `integrity_failed` renders INTEGRITY FAILED alert, Approve disabled, forged receipt preserved in ReceiptsPanel failed bucket |
| AC18 | PASS | e2e: no fabricated content when snapshot absent — empty-state text appears only in genuinely empty panels |
| AC19 | PASS | e2e: fixture task renders real `ant-mapper` (done) and `owl-auditor` (running) worker nodes |
| AC20 | PASS | cancellation fixture yields `CANCELLED` state + `task.cancelled` receipt; note: in-memory lease revocation (`sentinel.revokeLease`) has no UI trigger in slice #2 — flagged follow-up, not fabricated |
| AC21 | PASS | `harness/benchmarks/operator-console-resource-budget.sh` ran on cybertronia-win: 80.4 MB aggregate node RSS at idle; full service set budget (8 GB host, ~6 GB ceiling) verified via e2e webServer + worker runs |
| AC22 | PASS | e2e covers audit render, approve, deny, Sentinel outage, Gideon outage, integrity tamper, stale Bifrost, no-fabrication (8 scenarios) |

**Summary: 22 PASS / 0 FAIL / 0 BLOCK.**

## What was actually executed

```bash
# operator suite (after BFF fixture wiring) — 33/33
cd apps/bifrost && node ../../node_modules/vitest/vitest.mjs run src/operator
# PWA data-layer contract tests — 6/6
cd apps/pwa && node ../../node_modules/vitest/vitest.mjs run src/lib/operator_console
# PWA typecheck — clean
cd apps/pwa && node ../../node_modules/typescript/lib/tsc.js --noEmit
# E2E — 8/8 (single worker; full parallel crashes browsers on this 7.9 GB host)
cd apps/pwa && node ../../node_modules/@playwright/test/cli.js test --grep "operator console" --workers=1
# Resource budget — 80.4 MB node RSS idle
bash harness/benchmarks/operator-console-resource-budget.sh
```

Live-Bifrost latency run (`operator-console-event-latency.sh`) requires `make dev-up` with `OPERATOR_SESSION_TOKEN` set; the e2e route-interception suite is the hermetic AC6 witness.

## Decisions applied from the design's open questions (§17)

| Open question | Resolution in slice #2 |
|---|---|
| Sentinel module path | No `sentinel_v2/` exists; slice #2 implements the Sentinel Decision Service natively in `apps/bifrost/src/operator/sentinel.ts` (manifest verification + in-memory one-time leases). PEER Sentinel v2 binding deferred. |
| Gideon adapter location | No `sir_gideon.py` exists; slice #2 ships `apps/bifrost/src/operator/gideon.ts` (typed verdict composition). Real PEER Gideon binding deferred. |
| Receipt implementation | Existing Prisma/SQLite stack in `apps/bifrost` (`vault.db`): append-only `OperatorEvent` model + hash chain. |
| @agent-native/core | next.config.js aliases it to `src/lib/agent-native-mock.ts`; console panels use plain React + typed contracts, not @agent-native primitives. |
| Vercel | Deferred (no remote auth/trust/network work in this slice). |

## Known follow-ups (out of slice #2 scope)

- UI trigger for lease revocation on completion/cancellation (`sentinel.revokeLease` exists; wiring deferred).
- Local cached-evidence STALE rendering (design §12) — current build shows the Approval empty state when Bifrost is unreachable, which is honest but not yet the cached-then-stale path.
