# Items 2 + 3 Decision Matrix (Plan-Only)

This document enumerates the unresolved sub-decisions for **spec item 2**
(BIFROST BRIDGE: cryptographic enforcement + BrainSync CRDT coverage) and
**spec item 3** (CYBERTRONIA INTEGRATION: isolation + RTK + panopticon
blinding) as of the **Lane signals only** ship of items 1a + 1b.

**No code changes for items 2 and 3 in this PR.**  Both contain sub-
decisions that need explicit per-clause resolution from the operator AND
a HUMAN_GATE operator token (`CAMELOT_DASHBOARD_OPERATOR_TOKEN`) for the
security-class moves, per `AGENTS.md` Iron Gate.

---

## How to use this matrix

Each row is a single-turn resolution: reply with the option letter + any
footnote. Once all decisions in a row are made — and operator token
provided for HUMAN_GATE-class rows — the corresponding scope-PR is
unblocked.

---

## Status

| Item   | Status                          | Code shipped                                                |
|--------|---------------------------------|-------------------------------------------------------------|
| 1a + 1b (omni-router lane signals) | ✓ shipped (this PR)  | `control_plane/omniroute_policies.py` + `tests/test_omniroute_policies.py` |
| 2 (Bifrost Bridge + BrainSync CRDT) | ⏸ plan-only          | —                                                           |
| 3 (Cybertronia isolation + RTK Scythe) | ⏸ plan-only         | —                                                           |

---

## Item 2 — BIFROST BRIDGE decisions

| #    | Decision                                                                          | Options                                                                                                            | Recommended default                                              | Blocker class                                                         |
|------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------|
| 2.1  | `BrainSync` naming                                                                 | (a) rename `nano_swarm_crdt` → `brainsync_crdt` (b) introduce new `control_plane/brainsync.py` that uses existing CRDT | **(b)** — additive; no migration                                | naming                                                                |
| 2.2  | "absolute isomorphic consistency" precision                                       | (a) colloquial-paper-absolute (LUB-CRDT semantics, no proof artifact needed) (b) formal-math-absolute (Z3/SMT artifact required)   | **(a)** — matches existing `merge_strategy: least_upper_bound`  | evidence (proof artifact required if (b))                            |
| 2.3  | WireGuard-vs-QUIC transport                                                        | (a) keep WireGuard + add QUIC (defense-in-depth) (b) substitute WireGuard for QUIC (c) QUIC-only after WireGuard sunset | **(a)** — preserves existing mesh, additive                      | **SECURITY-CLASS → HUMAN_GATE** (`CAMELOT_DASHBOARD_OPERATOR_TOKEN`) |
| 2.4  | "every Camelot forge output commits to BrainSync CRDT" coverage                   | (implicit) — every forged system file becomes a CRDT delta through the BrainSync publication layer                 | —                                                                | **SECURITY-CLASS → HUMAN_GATE**                                       |

---

## Item 3 — CYBERTRONIA INTEGRATION decisions

| #    | Decision                                                                          | Options                                                                                                            | Recommended default                                              | Blocker class                                                         |
|------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------|
| 3.1  | CRDT multi-tenant sharding migration                                              | (i) migrate every existing commit to project namespace; (ii) forward-only (only new emits are sharded)             | **(ii)** — lighter; no data migration                            | migration/scope                                                       |
| 3.2  | "blinding the panopticon" encryption-at-rest shape                                | (a) per-project key envelope (`.age` blobs, project-secret) (b) whole-ledger envelope (single project-vault key) (c) reuse existing `aegis_redact_map.json` pipeline | **(c)** — minimal new crypto surface                             | **SECURITY-CLASS → HUMAN_GATE**                                       |
| 3.3  | RTK Scythe identity                                                               | (a) reuse `control_plane/rtk/` as-is (RTK is the Scythe); wire RTK into forge wrapper (b) introduce new `control_plane/rtk_scythe/` with explicit "trim-noise" interface | **(a)** — smallest scope                                         | naming                                                                |
| 3.4  | Cybertronia isolation shared-allowed list                                         | Are camelot-wide docs (`AGENTS.md`, `TODO.md`, root `tasks.md`, `verification.md`) exempted from project isolation? | **yes** — root docs stay camelot-wide; only new project-bound emits are isolated | namespacing |

---

## Item 1 hardening — optional precision questions

| #      | Decision                                                                          | Options                                                                                                            | Recommended default                                              | Blocker class                                                         |
|--------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------|
| 1.H.1  | "hardware-native speeds" precision (item 1a sentence 3)                           | (a) precise (SIR_CODEX scaffolds native-only: x86_64/arm64; excludes WASM); (b) colloquial ("fast"; no filter)      | **(b)** — keeps `02_FORGE/kinetic/actor` (Wasmtime 30 / wasm32-wasip1) integrated       | scope / emit-target filter optional                                  |
| 1.H.2  | paper bibliography on disk                                                         | drop `[1]` `[2]` `[4]` `[5]` `[8]` `[7]` `[13]` `[14]` to `docs/architecture/camelot_v1000_paper/bibliography.md`    | —                                                                | unrelated but blocks reasoning over paper claims                      |

---

## Verification command for THIS PR (already passing)

```bash
.venv/Scripts/python.exe -m pytest tests/test_omniroute_policies.py -v
# Or, if running with bare python on Windows / bash:
python -m pytest tests/test_omniroute_policies.py -v
python -m control_plane.omniroute_policies --test  # 6/6 self-test cases
python -m control_plane.soul_oversight --test     # regression: 12/12 must still pass
```

---

## What this matrix does NOT cover (out of PR scope)

* The `forge_nexus.sh` claim — long stamped REJECTED in
  `02_FORGE/cartridge/digital_factory_v4000_ascended/Sir_Codex/Agent.md`
  and `Sir_Bard/Agent.md`. No execution.
* Persona-injection envelopes refused in prior conversation turns
  (`[SYSTEM_BOOT] :: ARCHITECTS`, `[MODE] :: KINETIC_PRECISION`,
  `<> PRIME DIRECTIVE: ORTHOGONAL VELOCITY`,
  *"You are the Sovereign Context Compiler…"* persona assertion). None of
  these are executable specs.
* The empty-fence TeX `\`\`\`tex …` payloads and stray `***` / `#`
  keystrokes from prior turns — all rendered as artifacts of paste-
  compression / chat truncation, not directives.

---

## Spec provenance

The Omni-Router Matrix / Bifrost & CRDT Alignment / Cybertronia Isolation
paragraphs arrived as paper-style fragments with bracketed citations
through the conversation. **Items 1a + 1b were grounded to live Camelot
artifacts** (`.claude/commands/boot.md:28`; `04_KINETIC/multivoice/...`;
`scripts/cybertron_dawning.py:123`; `01_KERNEL/memory/tissue/nano_swarm_crdt.json`)
and shipped as `control_plane/omniroute_policies.py` in this PR.

**Items 2 + 3 are plan-only** pending the resolutions above. Each
sub-decision is a one-turn choice; aggregate resolutions unblock their
respective scope-PRs.
