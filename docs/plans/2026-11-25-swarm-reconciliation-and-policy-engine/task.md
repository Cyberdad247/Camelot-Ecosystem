# Camelot-OS Implementation Task DAG

Generated: 2026-11-25  
Blueprint: `docs/plans/2026-11-25-swarm-reconciliation-and-policy-engine/blueprint.md`  
Verification: `docs/plans/2026-11-25-swarm-reconciliation-and-policy-engine/verification.md`

---

## Phase 0 — Preflight & Resource Guard (Anya)
- [x] **P0.1:** Verify host RAM has >= 1.0 GB headroom before running Node/Rust/Go builds (Global Law 3: 8 GB server ceiling). *(Verified 7.05/7.71 GB; ran strictly sequential checks.)*
- [x] **P0.2:** Check `git status -sb` on `feat/invisioned-marketing-digital-factory` and confirm no unintended changes in `PROVENANCE_LEDGER.md`.

---

## Phase 1 — Swarm Tracker & Placeholder Reconciliation (Sir Alex / Sir Boris)
- [x] **T1.1:** Update `parallel_task_tree.md` Hardware Baseline IP from `100.71.218.75` to `100.110.180.18` (matching `apps/bifrost/main.go`).
- [x] **T1.2:** Update `parallel_task_tree.md` Mermaid diagram and Thread Status Matrix:
  - Thread A (`SIR BORIS`): mark `SUPERSEDED (Hosted in apps/pwa /console)` with actual paths (`apps/pwa/src/components/operator_console/OperatorConsole.tsx`).
  - Thread B (`SIR CODA`): mark `COMPLETE (Verified: go test ./... pass)`.
  - Thread C (`SIR CODEX`): mark `COMPLETE (Verified: cargo check pass)`.
  - Thread D (`LADY ALEXANDRIA`): link both `packages/policy-engine/schemas/approval-states.yaml` and `packages/policy-engine/src/index.ts`.
- [x] **T1.3:** Audit `apps/operations-console/` drift (`.vercel`, `.env.local`, `.env.production`): relocated to `.secrets_backup/operations-console-2026-11-25/`; `apps/operations-console/` now contains only `README.md` and `deployment-notes.md`.

---

## Phase 2 — Complete Thread D: `@camelot/policy-engine` (Lady Alexandria / Sir Forge)
- [x] **T2.1:** Extend TypeScript interfaces in `packages/policy-engine/src/index.ts` to model `transitions_matrix`, `audit_logging`, `TransitionContext`, `TransitionResult`, and `HitlAuditRecord`.
- [x] **T2.2:** Implement fail-closed guard evaluation in `KBAPolicyEngine.evaluateTransition()`:
  - `RiskScoreCheck` (`riskEntropy < 75`; failure returns `REQUIRE_MULTI_SIG`).
  - `MemoryCeilingCheck` (`nodeRamUsageMb < 7168`).
  - `NoSecretExposure` (detects raw secret patterns in `proposedDiff`).
  - `ASTSyntaxValidator` (injectable validator hook with safe default).
- [x] **T2.3:** Enforce `transitions_matrix` rules (matching `from` → `to` RBAC, `requires_2fa: true`, and edge-specific guards), `SUSPENDED` override attestation, and terminal-state immutability (`is_terminal: true`).
- [x] **T2.4:** Add opt-in append-only JSONL audit writer targeting `03_VAULT/runtime_state/hitl_audit_ledger.jsonl` with all fields declared in `approval-states.yaml` (`tenant_id`, `transaction_id`, `from_state`, `to_state`, `operator_id`, `timestamp`, `signature`).
- [x] **T2.5:** Create `packages/policy-engine/src/index.test.ts` (Vitest) with table-driven tests covering:
  - Happy-path lifecycle (`IDLE` → `AWAITING_APPROVAL` → `EDITING_BY_HUMAN` → `EXECUTING` → `COMPLETED`).
  - Direct Sovereign approve blocked when `riskEntropy >= 75` or `nodeRamUsageMb >= 7168`.
  - `EDITING_BY_HUMAN` → `EXECUTING` blocked when `twoFactorVerified` is false or role is not `Sovereign_Executive`.
  - Secret exposure in `proposedDiff` rejected.
  - Terminal states reject all outbound transitions.
  - Audit record schema completeness.
- [x] **T2.6:** Run `npx tsc --noEmit` and `npx vitest run` in `packages/policy-engine/` until 100% green, then update Thread D in `parallel_task_tree.md` to `COMPLETE (Verified)`.

---

## Phase 3 — Sequenced Handoff to `invisioned-marketing` (Cells 1–4)
*(Executed sequentially after Phase 1 & 2 passed Gate 1; mirrored in `docs/superpowers/plans/2026-10-15-invisioned-marketing-production-integration.md`.)*

- [x] **T3.1 (Cell 1 — Sir Sentinel):**
  - Aligned `apps/invisioned-marketing/vercel.json` (`buildCommand`, `.next`, strict CSP/CORS, removed wildcard+credentials conflict).
  - Removed hardcoded Shopify storefront token from `src/app/api/headartworks/bundle-checkout/route.ts`, documented env vars in `.env.example`, and verified `python -m squires.colony ghost apps/invisioned-marketing` reports `0` findings.
- [x] **T3.2 (Cell 2 — Lady Apis):**
  - Added `apps/invisioned-marketing/src/lib/invisionedStore.ts` hybrid persistence (HTTPS cloud DB bridge + air-gapped JSONL fallback) and wired into `lead/route.ts` and `proposal/route.ts`.
  - Hardened Resend webhook notification in `lead/route.ts` with `escapeHtml()` to prevent HTML injection.
- [x] **T3.3 (Cell 3 — Sir Visage):**
  - Verified all 5 public routes (`/`, `/proposal`, `/command`, `/portal`, `/canvas`) and confirmed `npm --prefix apps/invisioned-marketing run typecheck` exits `0`.
- [x] **T3.4 (Cell 4 — Sir Sonus):**
  - Added `GET` duplex WebSocket signaling handshake + ElevenLabs Conversational AI fallback config to `apps/invisioned-marketing/src/app/api/invisioned/oracle/route.ts`.
  - Connected `HolographicClientOracle.tsx` 16-bar frequency visualizer to Web Audio API (`AudioContext` + `AnalyserNode`) with graceful fallback.

---

## Phase 4 — Final Verification & Ledger Alignment
- [x] **T4.1:** Run all checks in `docs/plans/2026-11-25-swarm-reconciliation-and-policy-engine/verification.md`.
- [x] **T4.2:** Verify `camelot --json ledger status` reports `mirrors_aligned: true`.
