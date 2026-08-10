# BriefingScript — Deadline Integration Audit

**Branch:** `claude/camelot-mvp-velocity` @ `fbc784c` · **Date:** 2026-08-09
**Verdict:** ⚠️ **CONDITIONAL GO** — shippable, with one deadline-day blocker that is
**not in our code** and two defects worth fixing first.

---

## 0. Audit integrity — read this before trusting anything below

Two of three commissioned agents (forensic sweep, ingestion-point security) **died
mid-run on an API session limit** and delivered no findings. One got as far as "no
Zod in any of those package.json files"; the other said "found a hard blocker"
without naming it.

**Their findings are NOT reproduced here, invented, or guessed at.** Everything
below was executed or read directly. The audit is therefore **partial**: the
static security sweep of ingestion points and the full forensic bloat/logic-smell
pass did not happen. Section 6 states exactly what remains unaudited.

Two roster corrections: **Sir Gideon and Sir Sentinel do not exist** in
`01_KERNEL/agora/agents/roster.json` (43 agents). Sir Codex, Sir Dagonet, Lady
Veritas and Sir Socrates do. Dagonet (The Breaker) was cast for the edge-case work.
There is no MicroVM in this repo — Firecracker is aspirational prose in
`docs/agentforge.md`. The five edge cases below ran against a **real native stack**
on this host, and that is stated rather than dressed up.

---

## 1. The deadline blocker — and it is not ours

**CI has never executed against this code.** Every `pull_request` run since
2026-08-07 aborted in 3–15 seconds with no logs. The cause is already documented
in your own repo, at `.github/workflows/deploy-vercel.yml:11-14`:

> `dorny/paths-filter` calls the PR Files API, and the deploy jobs comment the
> preview URL on the PR. The default `GITHUB_TOKEN` here lacks those scopes, which
> is why "Detect changes" failed with **"Resource not accessible by integration"**.

`deploy-vercel.yml` has since had `permissions: {contents: read, pull-requests: write}`
added. **`verify_os.yml` — "Camelot OS Verification", the one that actually gates —
has no `permissions:` block at all.** That is the fix, and it is one stanza.

**Impact at the deadline:** PR #200 and #201 will show red checks that have nothing
to do with the diff. Plan for admin merge, or land the `permissions:` fix first and
get a real signal.

**Second CI fact:** no workflow exercises `integration/`. `forge-ci.yml` is
path-filtered to `02_FORGE/**`; `verify_os.yml` and `deploy-vercel.yml` have no path
filter but test other things. The slice's 89 vitest / 70 Go / 19 Rust tests run
**only on a developer machine**. Nothing catches a regression on push.

---

## 2. Shadow validation — 5 edge cases, executed live

Native stack, loopback, real processes. Not simulated.

| # | Case | Result | Evidence |
|---|---|---|---|
| **EC1** | 10 MB request body | 🔴 **FAIL** | HTTP **200** in 320 ms. No body size limit anywhere. |
| **EC2** | 30 concurrent durable writes | ✅ PASS | 30 artifacts, 30 distinct contents, zero collisions. Lease-derived naming holds under contention. |
| **EC3** | Hostile JSON (50 k nesting, type confusion, non-JSON) | ✅ PASS | All **400**. `{"error":"...exceeded max depth"}`. Gateway alive. |
| **EC4a** | SIGKILL mid-write, restart on same DB | ✅ PASS | 1687 audit rows survived; clean boot; **zero** orphaned `.note-*` temp files. |
| **EC4b** | Tampered audit row, restart | ✅ PASS | **Refused to boot**, exit 1: `hash chain broken at index 842 (tampering?)` |
| **EC5** | 400 sustained mixed-tier turns | ✅ PASS | 3133 ms (**7 ms/turn**); RSS 17→20 MB (**+3 MB, no leak**); audit 1.1 MB; 100 artifacts / 408 KB. |

**EC1 is the one real defect.** A 10 MB transcript is accepted, buffered entirely in
memory, hashed, and stored in the session context window. On the documented **8 GB
single-host ceiling** (`.agent/local_env.md`) this is a trivial memory-pressure
lever. Fix is one line per handler:

```go
r.Body = http.MaxBytesReader(w, r.Body, maxRequestBytes)  // 1 MiB is generous
```

EC4b deserves emphasis: the tamper-evidence claim is **not** marketing. A single
mid-chain row edit stops the process booting.

---

## 3. Latency and resource profile

| Metric | Measured | Assessment |
|---|---|---|
| Turn latency (tier-1) | p95 **2.3 ms**, avg 2.1 ms | No bottleneck |
| Sustained turn cost | **7 ms/turn** over 400 | Linear, no degradation |
| Gateway cold start | **327 ms** | Fine |
| Gateway RSS idle → loaded | 17 → **20 MB** | +3 MB over 400 turns; no leak |
| Node agent RSS | **3.4 MB** | Negligible |
| Console RSS | 19 MB | `python http.server` dev stand-in |
| **Control stack total** | **~42 MB** | Against 8 GB: **0.5%**. Ample headroom. |
| Compute p95 (1024-sample batch) | 10.1 ms (max 40.3) | Variance is CPU scheduling, not a defect |

**No latency spikes found.** The performance story is genuinely strong; the risk on
this box is memory-by-abuse (EC1), not throughput.

---

## 4. Integration topology

**Blast radius outside `integration/` and `docs/`: two files.**
`Cargo.toml` (one workspace member) and `Cargo.lock` (11 lines). Verified by
`git diff --stat 98543e0..HEAD`. The slice is genuinely self-contained.

**Clean-clone build: ✅ PASSES.** A fresh clone of the branch runs `npm install` and
`./scripts/build.sh` successfully. `contracts/dist/` and `kickbox/dev-token.txt` are
absent as expected and are generated by the build/startup path — **no hidden
prerequisite**, no broken teammate machine. This was the highest-risk unknown and it
is clean.

**Generated-file discipline:** `gateway/skills_gen.go` and `contracts/src/skills.gen.ts`
are committed (present in the clean clone) and drift-checked by `make test`. Correct
call — no codegen in the startup path.

---

## 5. Security claims — verified, refuted, unknown

| Claim | Status |
|---|---|
| "Zod validation schemas fully operational across all data ingestion points" | 🔴 **REFUTED.** **Zero** Zod references in `integration/`. What actually validates: Go `encoding/json` with typed structs plus explicit field checks — which EC3 proves is effective (every hostile input 400s). The claim is false; the underlying posture is nonetheless sound. Do not "fix" this by adding Zod to a zero-dependency contracts package. |
| "AgentArmor security hooks operational" | 🔴 **REFUTED (prior finding).** `control_plane/main.py:504` `_pdg_check` is five substrings matched against the user's own intent string. Not a PDG; cannot catch injection, which arrives in tool *outputs*. Nothing equivalent exists in `integration/` at all. |
| Tier-3 Iron Gate authenticated | ✅ **HOLDS** (fixed today). 401 without a token; 403 on foreign-origin preflight; loopback-only bind verified refused from `192.0.2.2`. |
| Audit tamper-evidence | ✅ **HOLDS** — EC4b, empirically. |
| No LLM in the tool-selection path | ✅ **HOLDS.** `hermes.go` is deterministic phrase matching over a fixed registry. Tool-choice prompt injection is structurally impossible. **The strongest security property in the system and the least advertised.** |
| Z3 "50 ms crucible", `<0.7%` error rate | 🔴 **REFUTED (prior).** Fluents are regex-grounded, so the solver decides nothing; fails open on missing import; no timeout exists. |

---

## 6. NOT AUDITED — do not read absence as clearance

- Static security sweep of every ingestion point (agent died). Specifically unreviewed: `hermes` subprocess boundary, `store.go` SQL construction, WebSocket frame parsing, model-provider SSE parsing.
- Forensic bloat / dead-code / logic-smell pass over `integration/` (agent died).
- Anything outside `integration/`, `.github/workflows/`, and root build files. The other ~30 top-level directories were **not** examined.
- Browser-path verification: the `quick-note` button and the console's `dev-token.txt` fetch are typechecked and covered by construction, **never clicked in a real browser**.
- Acer hardware gate (owner: Sovereign) — still outstanding, still blocking PR #200.

---

## 7. Scores

| Dimension | Score | Basis |
|---|---|---|
| **Safety** | **8 / 10** | Lease→broker→audit chain verified end to end under crash and concurrency; tamper-refusal empirical; auth closed today. −2: EC1 unbounded body, and a partial security audit. |
| **Stability** | **9 / 10** | No leak over 400 turns, survives SIGKILL with zero orphans, 30-way concurrency clean, clean-clone build passes. −1: single-process in-memory lease store is the known scaling wall. |
| **ROI** | **7 / 10** | Governance substrate is reusable far beyond voice — it is a blackboard already. −3: the product surface is still four skills, one of which does real work. |
| **Deadline readiness** | **6 / 10** | Code is ready. CI cannot prove it, and that is the gap the team will feel. |

---

## 8. Required before deployment

**Blocking**
1. Add `permissions: {contents: read, pull-requests: write}` to `verify_os.yml` — one stanza, fixes "Resource not accessible by integration", turns CI from noise into signal.
2. `http.MaxBytesReader` on gateway request bodies (EC1).

**Strongly recommended**
3. A workflow that actually runs `cd integration && make test` on PRs touching `integration/**`. Today nothing does.
4. Complete the two aborted audits (ingestion points, forensic sweep) after the session limit resets.
5. Click through the console once in a real browser with auth on.

**Known, accepted, documented**
6. Acer hardware record still gates PR #200.
7. P2–P5 from the agency blueprint (Z3 fail-open, PDG, docs IMPLEMENTED/PROPOSED split) remain open.

---

## 9. Iron Gate

**HALTED.** No code was changed by this audit — it is read-and-measure only. The
working tree is clean at `fbc784c`, the release gate is intact (`4a68aa0`, no tags),
and PRs #200/#201 remain drafts.

Await `//GO` before crystallising the build. Recommended first scope: **items 1 and
2** — both are small, both are verifiable, and item 1 is the difference between a
deadline review with evidence and one without.
