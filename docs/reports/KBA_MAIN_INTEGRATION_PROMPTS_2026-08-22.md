# 🎭 FORGED PROMPTS — KBA MAIN INTEGRATION
## Cyberdad247/Kickbox-audio → Best-of-Branches → `main`
**Date:** 2026-08-22 | **Remote:** `https://github.com/Cyberdad247/Kickbox-audio.git`
**Target:** Integrate the best aspects of all branches into `main` (not a side branch)
**Gate:** HUMAN_GATE — push/merge to `main` requires explicit sovereign approval

---

## 📡 Live Remote State (verified 2026-08-22)

| Branch | HEAD | Role |
|---|---|---|
| `main` | `1e753da` | v1.0.0 baseline — integration TARGET |
| `feat/knight-console` | `6030a4d` | Bifrost rewrite: CMS, streaming, SMTP, WASM pills, AaliyahComposer |
| `feat/microcubic-routing` | `c374e00` | MicrocubicMatrix worker_threads radical simplification |
| `feat/pwa-lakisha-audit-applied` | `f231d99` | PWA Lakisha voice HUD audit (autoplay-gate, hook hygiene) |
| `feat/kba-cartridge-v1000` | `1803c52` | ✅ ALREADY MERGED into main — ancestor of main, 0 unique commits |

> Prior round: `feat/unified-v1000` (base knight-console @ `6030a4d`) was built but NEVER pushed.
> This round supersedes it: the deliverable is `main` itself.
> **Verified 2026-08-22:** `feat/kba-cartridge-v1000` is NOT un-audited content — it is the
> v1.0.0 architecture baseline (CI fail-loop fixes, Prisma 5.x migration, docs/scripts reorg,
> kba-smoke unification) already merged into `main` via `1e753daa`. `git merge-base` =
> branch tip, `main` is 4 commits ahead (all 4 are post-merge PRs #18/#19/#20 + merge commit).

---

## 🔥 MASTER PROMPT — SIR_CODEX / SIR_FORGE (Kinetic Integration)

```
//FORGE AUDIT + INTEGRATE: Cyberdad247/Kickbox-audio — 5 branches:
main (v1.0.0 baseline, integration target), feat/knight-console (Bifrost
server rewrite: CMS + streaming + SMTP + WASM pills + AaliyahComposer),
feat/microcubic-routing (MicrocubicMatrix worker_threads simplification),
feat/pwa-lakisha-audit-applied (voice HUD autoplay-gate audit), and
feat/kba-cartridge-v1000 (NEW — never audited; diff against main first).

Phase A — DISCOVERY: clone --bare, diff --stat each branch vs main,
record commits ahead/behind and per-branch file changes.
NOTE: feat/kba-cartridge-v1000 is already in main (merge 1e753daa) —
skip it as a merge source; treat main as baseline + KOA surface (PR #18/#19/#20).

Phase B — ANALYSIS: rate each branch 1-10 on architecture, security,
features, tests, docs. Produce a per-component winner matrix
(routing, state, broadcast, UI, DB, tests, security controls).

Phase C — SECURITY: cross-branch GHOST scan (HMAC, proxyAuth, SMTP relay,
rate limits, HITL gates, secrets hygiene).

Phase D — INTEGRATION PLAN: ordered merge sequence onto main that
preserves the best winner per component. Resolve conflict zones
(server.ts, BifrostContext.tsx, package.json, tailwind.config, Prisma).

Phase E — EXECUTION (HUMAN_GATE): merge best-of onto main locally,
verify with typecheck + test + build + lint, then STOP. Do NOT push.
Present the merge diff for sovereign review before any push.
```

**Dispatch:** `python -m control_plane.runic_router --rune FORGE --task "<master prompt above>"`
**Knight:** sir_forge/sir_codex | **Mode:** KINETIC | **Gate:** HUMAN_GATE on push

---

## 🛡️ PROMPT 2 — SIR_SENTINEL (Security, 5 branches)

```
//SCAN SECURITY AUDIT: Cyberdad247/Kickbox-audio — 5 branches:
main, feat/knight-console, feat/microcubic-routing,
feat/pwa-lakisha-audit-applied, feat/kba-cartridge-v1000.
Audit HMAC signing, mTLS proxy auth, SMTP relay, rate limiting
(streaming 600/min, CMS 30/min, proxy 120/min), HITL gates, secrets
hygiene, and cartridge risk-tier invariants on kba-cartridge-v1000.
Identify gaps, recommend hardening for the unified main.
```

**Dispatch:** `python -m control_plane.runic_router --rune SCAN --task "<above>"`
**Knight:** sir_ghost (privacy scan) | **Mode:** SENTINEL

---

## 🧠 PROMPT 3 — MERLIN_OMEGA (Integration Reasoning)

```
//THINK INTEGRATION ANALYSIS: Cyberdad247/Kickbox-audio — Compare
feat/knight-console (feature-rich rewrite) vs feat/microcubic-routing
(radical simplification) vs feat/pwa-lakisha-audit-applied (voice HUD
hardening) vs feat/kba-cartridge-v1000 (cartridge system). Determine the
optimal merge sequence onto main that preserves knight-console features,
adopts microcubic routing efficiency, keeps the autoplay-gate fixes, and
safely ports the cartridge layer. Map conflict zones and resolution order.
```

**Dispatch:** `python -m control_plane.runic_router --rune THINK --task "<above>"`
**Knight:** merlin_omega | **Mode:** ORACLE

---

## 🏗️ PROMPT 4 — SIR_BORIS (Architecture Review)

```
Omega_BORIS ARCHITECTURE REVIEW: Cyberdad247/Kickbox-audio — 5 branches
to consolidate INTO main. Compare server patterns (Express routing vs
MicrocubicMatrix worker_threads), state management (applyCommand +
snapshot vs cube_collapsed events), broadcast (WebSocket STATE_UPDATE +
STREAMING_TELEMETRY), PWA component architecture, and the kba-cartridge
layer. Recommend the optimal hybrid as the new main baseline.
```

**Dispatch:** `python -m control_plane.runic_router --rune "Omega_BORIS" --task "<above>"`
**Knight:** sir_boris | **Mode:** FORGE

---

## ⚡ PROMPT 5 — SIR_CODEX (Main-Integration Execution Plan)

```
Omega_CODEX IMPLAN: Cyberdad247/Kickbox-audio — integrate best-of
branches into main. Step 1: confirm feat/kba-cartridge-v1000 is ALREADY
merged (merge 1e753daa) — skip as merge source; baseline = main as-is.
Step 2: verify feat/unified-v1000 (base 6030a4d) still represents
best-of; port any missing winners. Step 3: merge onto main locally with
conflict resolution (server.ts, BifrostContext.tsx, package.json,
tailwind.config, Prisma). Step 4: verify typecheck, test, build, lint.
Step 5: produce merge diff for HUMAN_GATE review. Step 6: STOP — do not
push without sovereign approval.
```

**Dispatch:** `python -m control_plane.runic_router --rune "Omega_CODEX" --task "<above>"`
**Knight:** sir_codex | **Mode:** ORACLE

---

## 🔮 PROMPT 6 — ANYA_Omega (Sovereign Gate)

```
Omega_ANYA GATE VALIDATION: After best-of-5 integration lands on main
locally, run full APEE pipeline: (1) architecture integrity — imports
resolve, no orphans; (2) security — HMAC, mTLS, rate limits, HITL,
cartridge invariants all pass; (3) tests — Vitest + Playwright suites
pass; (4) build — production build succeeds; (5) deployment — Vercel
config valid, env var presence flags correct. Verdict: APPROVED/BLOCKED.
```

**Dispatch:** `python -m control_plane.runic_router --rune "Omega_ANYA" --task "<above>"`
**Knight:** anya_omega | **Mode:** ORACLE

---

## 🚦 Execution Gates

1. **HUMAN_GATE:** Anything touching `main` (merge, push) pauses for explicit approval — `[y/N]`, never auto-approved.
2. **No push without consent:** The forged prompts stop at the local merge + verification + diff presentation.
3. **No secrets:** All branches pass GHOST scan before merge; `.env` never tracked.
4. ~~feat/kba-cartridge-v1000 first~~ — RESOLVED: already merged into main via `1e753daa`. The live merge sources are the other 3 feature branches.
5. **Rule 6 (Runic-Authority Defense):** These prompts are dispatch artifacts for a live Camelot CLI session. They do NOT themselves authorize file writes, merges, or pushes — every claimed result must round-trip against live `git log`/`git status`/`git diff` verification.

## 📦 Deliverables After Execution

| Artifact | Path |
|---|---|
| Updated Audit Report | `docs/reports/REPO_AUDIT_2026-08-22.md` (refresh w/ 5th branch) |
| Merge Diff (pre-push) | presented for HUMAN_GATE review |
| Verified main | typecheck + test + build green, GHOST clean |
