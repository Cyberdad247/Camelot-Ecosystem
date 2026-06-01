# OMNI-ROUTER AUDIT — Task DAG
## LATTICE_SIGNAL | SIR_BORIS Lead | 2026-05-14

---

## PHASE 0 — Pre-Flight (no writes, verify live state)

| ID | Task | Knight | Output |
|---|---|---|---|
| T-01 | Query CLIProxy /v1/models — capture full model list | SIR_HELIO | 38 models confirmed ✅ |
| T-02 | Read omniroute.json — audit current engine bindings | SIR_ALEX | Bindings mapped ✅ |
| T-03 | Read knight_session.py KNIGHT_MODEL_MAP | SIR_ALEX | 10 entries, Anthropic-biased ✅ |
| T-04 | Merlin GoT — 3-branch capability/cost/latency analysis | MERLIN_Ω | Matrix resolved ✅ |
| T-05 | Alex Cognitive Cartridge — finalize knight→model assignment | SIR_ALEX | 13 knights mapped ✅ |

---

## PHASE 1 — OmniRoute Config Rewrite

| ID | Task | Knight | Dep | Status |
|---|---|---|---|---|
| T-10 | Rewrite `omniroute.json` engines section — add Google-priority bindings for all 11 non-harness knights | SIR_FORGE | T-05 | PENDING |
| T-11 | Rewrite `omniroute.json` tier structure — add G0/G1/G2/G3/C1/C2/X1/L0 tiers | SIR_FORGE | T-10 | PENDING |
| T-12 | Update `routing_matrix.fallback_chain` → `["gemini", "cliproxy_claude", "codex", "open_coder"]` | SIR_FORGE | T-11 | PENDING |
| T-13 | Update `routing_matrix.complexity_routing` — low→G1, medium→G3, high→G3+C2 | SIR_FORGE | T-12 | PENDING |
| T-14 | Add `knight_model_map` block to omniroute.json — single source of truth | SIR_FORGE | T-13 | PENDING |
| T-15 | Validate JSON: `python -c "import json; json.load(open('omniroute.json'))"` | SIR_SENTINEL | T-14 | PENDING |

---

## PHASE 2 — knight_session.py Update

| ID | Task | Knight | Dep | Status |
|---|---|---|---|---|
| T-20 | Update `KNIGHT_MODEL_MAP` — 11 knights → Google-priority models | SIR_FORGE | T-14 | PENDING |
| T-21 | Add `KNIGHT_FALLBACK_MAP` — secondary model per knight | SIR_FORGE | T-20 | PENDING |
| T-22 | Update `_resolve()` — pull model from omniroute.json `knight_model_map` if present, else KNIGHT_MODEL_MAP | SIR_FORGE | T-21 | PENDING |
| T-23 | Update `_classify_tier()` — G0/G1/G2/G3 tier logic replacing T0/T1/T2/T3 labels | SIR_FORGE | T-22 | PENDING |
| T-24 | Update `/models` table — add Fallback column | SIR_FORGE | T-23 | PENDING |

---

## PHASE 3 — Portable Binary Update

| ID | Task | Knight | Dep | Status |
|---|---|---|---|---|
| T-30 | Update `camelot_portable.py` — _KEYWORD_MAP model references to new Gemini models | SIR_FORGE | T-20 | PENDING |
| T-31 | Update `camelot_portable.py` — _KNIGHT_MODEL_MAP inline dict | SIR_FORGE | T-30 | PENDING |
| T-32 | Rebuild portable binary: `python scripts/build_portable.py --clean --test` | SIR_FORGE | T-31 | PENDING |

---

## PHASE 4 — Verification & Ledger

| ID | Task | Knight | Dep | Status |
|---|---|---|---|---|
| T-40 | Run V-0: `camelot status` — confirm CLIProxy sees Gemini models | SIR_SENTINEL | T-15 | PENDING |
| T-41 | Run V-1: `ks --list` — confirm updated model map | SIR_SENTINEL | T-24 | PENDING |
| T-42 | Run V-2: `ks` live prompt → verify SIR_BORIS routes to gemini-3-pro-preview | SIR_SENTINEL | T-24 | PENDING |
| T-43 | Run V-3: `ks --knight sir_ghost` → verify Ollama harness unchanged | SIR_SENTINEL | T-24 | PENDING |
| T-44 | Run V-4: privacy keyword test → confirm SIR_GHOST still triggers | SIR_SENTINEL | T-42 | PENDING |
| T-45 | Run V-5: portable binary smoke test 4/4 | SIR_SENTINEL | T-32 | PENDING |
| T-46 | Update PROVENANCE_LEDGER.md + sync all 3 copies | SIR_BORIS | T-45 | PENDING |

---

## DEPENDENCY GRAPH

```
T-01 ─┐
T-02 ─┤
T-03 ─┤→ T-04 → T-05 ─→ T-10 → T-11 → T-12 → T-13 → T-14 → T-15
T-04 ─┘                                                        │
                                                               ↓
                                                T-20 → T-21 → T-22 → T-23 → T-24
                                                 │
                                                 └→ T-30 → T-31 → T-32
                                                                        │
                                             T-40 ← T-15              │
                                             T-41 ← T-24              ↓
                                             T-42 ← T-24        T-45 ← T-32
                                             T-43 ← T-24              │
                                             T-44 ← T-42        T-46 ←┘
```

---

## KNIGHT DISPATCH

| Phase | Knight | Role |
|---|---|---|
| 0 | MERLIN_Ω | GoT decomposition, capability analysis |
| 0 | SIR_ALEX | Cognitive cartridge, binding matrix |
| 1-3 | SIR_FORGE | Implementation — JSON rewrite + Python edits |
| 1,4 | SIR_SENTINEL | JSON validation, live verification |
| All | SIR_BORIS | Lead, Harmony Gate, ledger entry |

---

## ESTIMATED EFFORT

| Phase | Tasks | LOC Changed | Risk Score |
|---|---|---|---|
| Phase 0 | 5 | 0 | 0 |
| Phase 1 | 6 | ~120 (JSON) | Low (12) |
| Phase 2 | 5 | ~30 (Python) | Low (15) |
| Phase 3 | 3 | ~20 (Python) | Low (10) |
| Phase 4 | 7 | 0 | 0 |

Total risk score: **37** → auto-apply (below HITL threshold of 50)
