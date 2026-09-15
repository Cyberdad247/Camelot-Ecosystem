# 🎭 FORGED MULTI-KNIGHT AUDIT PROMPTS
## Cyberdad247/Kickbox-audio — Reproducible Dispatch

**Forged via:** ANYA_Omega APEE v6.5 Triple-QFT Compiler
**Date:** 2026-08-22 | **Gate:** ColMAD 3/3 APPROVED

---

## 🔥 Prompt 1: SIR_FORGE — Architecture Audit + Implementation Plan

```
//FORGE AUDIT: Cyberdad247/Kickbox-audio — 4 branches: main (v1.0.0 baseline),
feat/knight-console (Bifrost server rewrite + CMS + streaming + SMTP + WASM +
AaliyahComposer), feat/microcubic-routing (MicrocubicMatrix worker_threads
radical simplification), feat/pwa-lakisha-audit-applied. Evaluate Bifrost server
patterns, identify best routing/state/broadcast approach, security architecture,
UI/PWA patterns, DB/Tests, and produce integration plan for unified branch.
```

**Dispatch:** `python -m control_plane.runic_router route --rune FORGE --task "<above>"`
**Knight:** sir_forge | **Mode:** KINETIC

---

## 🛡️ Prompt 2: SIR_SENTINEL — Security Audit

```
//SCAN SECURITY AUDIT: Cyberdad247/Kickbox-audio — HMAC signing, proxy auth,
SMTP relay, rate limiting, HITL gates, secrets hygiene across 4 branches
(main, feat/knight-console, feat/microcubic-routing, feat/pwa-lakisha-audit-applied).
Evaluate each security control, identify gaps, recommend hardening.
```

**Dispatch:** `python -m control_plane.runic_router route --rune SCAN --task "<above>"`
**Knight:** sir_ghost (privacy scan mode) | **Mode:** SENTINEL

---

## 🧠 Prompt 3: MERLIN_OMEGA — Deep Integration Reasoning

```
//THINK INTEGRATION ANALYSIS: Cyberdad247/Kickbox-audio — Compare
feat/knight-console server rewrite (CMS, SMTP, streaming telemetry, WASM pills)
vs feat/microcubic-routing (MicrocubicMatrix worker_threads radical
simplification). Determine optimal merge strategy that preserves
knight-console features while adopting microcubic routing efficiency.
Identify conflict zones and resolution strategy.
```

**Dispatch:** `python -m control_plane.runic_router route --rune THINK --task "<above>"`
**Knight:** merlin_omega | **Mode:** ORACLE

---

## 🏗️ Prompt 4: SIR_BORIS — Architecture Review

```
Omega_BORIS ARCHITECTURE REVIEW: Cyberdad247/Kickbox-audio — 4 branches to
unify into one efficient branch. Compare server patterns (Express routing vs
MicrocubicMatrix worker_threads), state management (applyCommand + snapshot vs
cube_collapsed events), broadcast patterns (WebSocket STATE_UPDATE + STREAMING_TELEMETRY),
and recommend the optimal hybrid architecture.
```

**Dispatch:** `python -m control_plane.runic_router route --rune "Omega_BORIS" --task "<above>"`
**Knight:** sir_boris | **Mode:** FORGE

---

## 🔒 Prompt 5: SIR_SENTINEL — Security Hardening

```
Omega_SENTINEL SECURITY AUDIT: Cyberdad247/Kickbox-audio — Evaluate HMAC webhook
signing, mTLS proxy authentication, SMTP relay DKIM, rate limiting (3 tiers:
streaming 600/min, CMS 30/min, proxy 120/min), HITL gates for CMS content,
RBAC matrix, WASM memory safety, and Tailscale serve network exposure.
```

**Dispatch:** `python -m control_plane.runic_router route --rune "Omega_SENTINEL" --task "<above>"`
**Knight:** sir_ghost (privacy override) | **Mode:** SENTINEL

---

## 🔮 Prompt 6: MERLIN_OMEGA — Strategic Deep Reasoning

```
Omega_MERLIN DEEP REASONING: Cyberdad247/Kickbox-audio branch integration
strategy. Analyze the architectural divergence between feat/knight-console
(feature-rich, 8450+ lines added) and feat/microcubic-routing (radical
simplification, 25976 lines removed). Produce a decision tree for merge
resolution: which files to keep, which to port, which to delete. Consider
backward compatibility, test coverage, and production deployment risk.
```

**Dispatch:** `python -m control_plane.runic_router route --rune "Omega_MERLIN" --task "<above>"`
**Knight:** sir_boris (Merlin fallback) | **Mode:** FORGE

---

## ⚡ Prompt 7: SIR_CODEX — Implementation Plan

```
Omega_CODEX IMPLAN: Cyberdad247/Kickbox-audio — create feat/unified-v1000
branch merging best of all 4 branches. Step 1: checkout feat/knight-console
as base. Step 2: port MicrocubicMatrix from feat/microcubic-routing. Step 3:
restore LakishaHUD from main if voice pipeline needed. Step 4: resolve
conflicts (server.ts, BifrostContext.tsx, package.json, tailwind.config).
Step 5: verify (typecheck, test, build, lint). Step 6: update CHANGELOG.
```

**Dispatch:** `python -m control_plane.runic_router route --rune "Omega_CODEX" --task "<above>"`
**Knight:** sir_codex | **Mode:** ORACLE

---

## 🔮 Prompt 8: ANYA_Omega — Sovereign Gate Validation

```
Omega_ANYA GATE VALIDATION: After feat/unified-v1000 is created, run full
APEE v6.5 pipeline on the unified branch to validate:
(1) Architecture integrity — all imports resolve, no orphaned modules
(2) Security posture — HMAC, mTLS, rate limiting, HITL all functional
(3) Test coverage — all suites pass (Vitest + Playwright)
(4) Build verification — production build succeeds
(5) Deployment readiness — Vercel config valid, environment variables set
```

**Dispatch:** `python -m control_plane.runic_router route --rune "Omega_ANYA" --task "<above>"`
**Knight:** anya_omega | **Mode:** ORACLE

---

## 📋 Quick Dispatch Script

```python
#!/usr/bin/env python3
"""Dispatch all 8 knight audit prompts for KBA branch unification."""
from control_plane.runes.runic_router import route_rune
import json

PROMPTS = [
    ("//FORGE", "AUDIT: Cyberdad247/Kickbox-audio — 4 branches to unify. Evaluate Bifrost server patterns, security, UI/PWA, DB/Tests, produce integration plan."),
    ("//SCAN", "SECURITY AUDIT: Cyberdad247/Kickbox-audio — HMAC, proxy auth, SMTP, rate limits, HITL, secrets across 4 branches."),
    ("//THINK", "INTEGRATION ANALYSIS: Cyberdad247/Kickbox-audio — knight-console vs microcubic-routing merge strategy."),
    ("Omega_BORIS", "ARCHITECTURE REVIEW: Cyberdad247/Kickbox-audio — server patterns, state management, broadcast."),
    ("Omega_SENTINEL", "SECURITY: Cyberdad247/Kickbox-audio — HMAC, mTLS, SMTP, rate limits, HITL, WASM safety."),
    ("Omega_MERLIN", "DEEP REASONING: Cyberdad247/Kickbox-audio — branch integration decision tree."),
    ("Omega_CODEX", "IMPLAN: Cyberdad247/Kickbox-audio — feat/unified-v1000 creation steps."),
    ("Omega_ANYA", "GATE VALIDATION: Cyberdad247/Kickbox-audio unified branch — architecture, security, tests, build."),
]

for rune, task in PROMPTS:
    r = route_rune(rune, task)
    print(f"{rune:20s} → {r.knight:20s} | {r.mode:10s} | queued={r.queued}")
```
