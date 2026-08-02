# HANDOVER BRAIN DUMP — Camelot-Ecosystem Upgrade
**From**: Claude (chat session, Ω_FABLE_TITAN_UI_COMPILER context)
**To**: Claude Code (executing on VaShawn's machine with GitHub auth)
**Date**: 2026-07-20
**Operator**: VaShawn (Cyberdad247), the Sovereign

---

## LOAD — Context you need before touching anything

**Why this handover exists**: The chat container has no GitHub credentials, and
`Cyberdad247/Camelot-Ecosystem` is private — unreachable from there. Everything in
`payload/` was built and verified in-container against real installs and real test
runs. Your job is placement, integration, and push — not re-authoring.

**What the payload is**:

1. `payload/bifrost/` — 8 TypeScript modules implementing the Camelot-OS Bifrost
   trust plane (νKG crystal + MDX bridge-chapter spec, both in the Sovereign's
   possession). Dependencies: `node:crypto` + one type import
   (`../router/intent-router` → `IntentRoute`, and `../policy/policy-engine` →
   `evaluatePolicy`) used only by `bifrost-gateway.ts` and `registration-gate.ts`.
   Everything else is dependency-free and portable as-is.
   - bifrost-envelope.ts — 24-field signed header, HMAC-SHA256, nonce replay, TTL, fail-closed version check
   - heimdall-fsm.ts — 7-state containment FSM, ragnarok guarantees, sidecar advisory
   - bifrost-gateway.ts — trust reconciliation lattice (quarantine > block > review > warn > allow)
   - ffi-policy.ts — FFI failure table + conservative trust degradation + sidecar health automation
   - bifrost-queue.ts — bounded priority queues, signed critical bypass, overflow policy, dead-letter
   - registration-gate.ts — registration → sidecar → preflight → scoring → reconciliation → grant/deny
   - provenance-chain.ts — prev_hash-chained ledger, buffer-without-commit-claim, Yggdrasil merkleRoot()
   - microfish.ts — trend/anomaly/capacity engine; feedHeimdall() maps σ-severity to FSM events
   - bifrost-smoke.test.ts — the full assertion suite (60+ asserts), runs under `tsx`

2. `payload/multivoice-router.patch` — cumulative git patch for
   `Cyberdad247/Multivoice-router` (bifrost modules + a `next/font`→Vite fix in
   GenesisTerminal.tsx + extended smoke tests). Apply from repo root.

3. `payload/tower-r3f/` — complete Vite + React 18 + R3F + GSAP project:
   "Bifrost Tower" 3D scroll experience. Camelot palette (#050505 / #D4AF37 /
   #2E0854). Pure-function camera resolver (`resolveCameraLayout`) with its own
   unit suite (`npm test`). Verified: tsc strict + tests + build all green.

**Design law in force**: karpathy-guidelines (think-before-coding, simplicity
first, surgical changes, goal-driven with verify checks). Do not refactor
payload code; do not "improve" adjacent files.

---

## BUILD — Tasks in order

### Task A — Multivoice-router
```
git clone https://github.com/Cyberdad247/Multivoice-router.git
cd Multivoice-router
git checkout -b bifrost-trust-plane
git apply ../payload/multivoice-router.patch   # if apply fails, copy payload/bifrost → src/bifrost and payload/bifrost-smoke.test.ts → src/tests/smoke.test.ts instead
npm install
```

### Task B — Camelot-Ecosystem (private; you have auth)
```
git clone https://github.com/Cyberdad247/Camelot-Ecosystem.git
cd Camelot-Ecosystem
git checkout -b bifrost-upgrade
```
**Inspect the repo structure first** — it was never visible from chat. Then place:
- `payload/bifrost/` → the natural shared-lib location (`packages/bifrost/`,
  `src/bifrost/`, or `libs/bifrost/` — match existing convention). If the repo
  has no `IntentRoute`/`evaluatePolicy` equivalents, stub a minimal
  `intent-router.ts` type + permissive `policy-engine.ts` beside them, or strip
  `bifrost-gateway.ts` + `registration-gate.ts` from this drop and note it.
- `payload/tower-r3f/` → apps/sites location (`apps/tower/`, `sites/tower/`, or
  standalone dir). It is self-contained; keep its own package.json.
- If the Ecosystem has a README/docs index, add one line linking the tower and
  the bifrost lib. Nothing more.

## TEST — Verify gates (all must pass before RECORD)
- Multivoice-router: `npx tsc --noEmit` clean AND `npx tsx src/tests/smoke.test.ts`
  prints "Camelot smoke tests passed (trust plane + control plane + predictive + Yggdrasil)."
- tower-r3f (wherever placed): `npm install && npm test && npm run build` — test
  prints "camera-layout tests passed (glyph contract)." and build succeeds.
- Ecosystem: if it has its own build/CI script, run it and confirm the drop
  breaks nothing.

## RECORD — Commits and push
- Conventional messages:
  - MVR: `feat(bifrost): trust plane + control plane + predictive + Yggdrasil ledger (spec: Bifrost bridge chapter)`
  - Ecosystem: `feat: integrate Bifrost trust-plane lib + Bifrost Tower 3D experience`
- Push both branches; open PRs to main (do not push to main directly).
- In each PR body, paste the verify-gate outputs.

## GATE — Escalate to the Sovereign instead of guessing when:
1. Camelot-Ecosystem's structure conflicts with both placement options
2. The Ecosystem already contains a bifrost implementation (merge question)
3. Any verify gate fails after one honest fix attempt
4. The patch won't apply AND the manual copy path also conflicts
5. Branch protection blocks the push
6. Anything requires deleting existing Ecosystem code

⚜️_SOVEREIGN_TRUTH
