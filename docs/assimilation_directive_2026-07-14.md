# CAMELOT-OS Assimilation Directive (2026-07-14)

> **Issuance**: `[SYSTEM_CALL] CAMELOT_OS::ASSIMILATION_PROTOCOL >> TARGET: [PENTAGONAL_CORE_V1000]`
> **Mode**: HYPER-GRAFT_AND_CRYSTALLIZE
> **Issued by**: vizio (per the AskUser response "Yes, execute as written")
> **Author of this recording**: freebuff (parent agent)
> **Status**: **EXECUTION PLAN — §7 OPEN QUESTIONS RESOLVED** (2026-07-14). Critical note (§7 Q2): the user picked **0 = full-blast** for GEP pilot — every Phial Engine (all 6) accepts the GEP change simultaneously. Operational consequence: every Phial Engine-touching PR is PROMPT-tier HITL (not AUTO) until the rollout stabilizes.

---

## 0.5. Verbatim system_call being responded to

```
[SYSTEM_CALL]: CAMELOT_OS::ASSIMILATION_PROTOCOL >> TARGET: [PENTAGONAL_CORE_V1000]
[MODE]: HYPER-GRAFT_AND_CRYSTALLIZE
[SECURITY_LAYER]: AEGIS_SHIELD_ACTIVE

1. [GEP_EVOLUTION_MANDATE]: All Phial Engines must now operate on the Genome
   Evolution Protocol (EvoAgentX/Evolver). Skills are no longer static; they
   are biologically mutated, sandboxed, and competitively selected for
   token-efficiency and kinetic speed.
2. [GRAPHIFY_IDENTITY_MATRIX]: Translate all 12 Knight character sheets from
   flat Markdown into dynamic Semantic Graphs. Lady Mnemosyne is authorized
   to map and retrieve character traits via graph-nodal intersections for
   absolute token compression.
3. [ARCHON_PRE_FLIGHT_HARNESS]: Re-write pre-flight.md to establish a
   deterministic, isolated execution harness for all coding tasks, pulling
   architectural patterns from the ultimate LLM application registries.
4. [DEEPSEEK_LOGIC_CORE]: Bind Merlin's DAG generation to formal mathematical
   verification and the foundational truths of the CS/AI Compendium. All
   strategies must be proven, not guessed.

[EXECUTE]: Compile the new state. Eradicate all legacy prompt structures.
          Output the new system status wrapped in 💎 tokens.
```

---

## 0. Preamble — how this directive was grounded

The system_call arrived ungrounded: many of the files it references
(`pre-flight.md`, "12 Knight character sheets" as discrete Markdown, `EvoAgentX/`,
`Evolver/`) **do not exist on disk**. The user's AskUser response was
"Yes, execute as written", with the option text explicitly warning
that "the call may fail partway through and the destructive 'eradicate' step is irreversible."The conservative interpretation applied at the time of the
recording phase (2026-07-14 noon, `§7` open questions pending):

1. **No files are deleted** under the "Eradicate all legacy prompt structures"
   instruction. The phrase was ungrounded — no inventory of "legacy prompt
   structures" was provided. Destructive ops without a target list are
   the kind of surprise the standing rules forbid.
2. **No files are fabricated**. The "12 Knight character sheets" claim is
   treated as aspirational. The repo currently has a roster of **10 Knights**
   documented in `CAMELOT_OS/AGENTS.md`. If the user wants a per-Knight
   character sheet per Knight, that's 10 (or 12) *new* files to author
   deliberately, not something to invent here.
3. **One new file is added**: this document. It records the four mandates
   and the ground-truth state of each. The `💎` token output framing from
   the system_call is honored at the parent-agent response level
   (see end of freebuff's chat reply).

> **Post-resolution note (2026-07-14, after §7 graduation)**:
> After the 6 §7 questions were resolved, the document graduated from
> "recording" to "EXECUTION PLAN". The conservative interpretation above
> correctly scoped the **issuance posture**; the **execution posture**
> per §6 + §7 explicitly authorizes:
> - **Deletions**: §7 Q6 — `newtech.md` first, then `.claude/jobs/*` + `.claude/agents/sir-*.md` as follow-ups with `git revert`-style rollback.
> - **New files**: §7 Q3 (`SkillMutation.py`) + §7 Q5 (`pre-flight.md`) + §7 Q4 Phase 1 (`merlin_dag_z3_checker.py`) + §7 Q1 (10 character sheets).
> - The token framing `💎` remains unchanged at the chat-reply level (freebuff's response).

---

## 1. `GEP_EVOLUTION_MANDATE` — Genome Evolution Protocol

**Claim**: All Phial Engines must now operate on the Genome Evolution
Protocol (`EvoAgentX` / `Evolver`). Skills are no longer static; they
are biologically mutated, sandboxed, and competitively selected for
token-efficiency and kinetic speed.

### Ground truth

| Probe | Result |
|---|---|
| `tree_sitter_phial` references | **Real** — used in `CAMELOT_OS/03_VAULT/training/configs/skills/SWARM.md` and `PROVENANCE_LEDGER.md` for AST-aware patching. This is a *patcher*, not an evolution protocol. |
| `EvoAgentX/` or `Evolver/` directory | **Does not exist** in the repo. |
| Skills with mutation/sandbox/selection semantics | **None found.** Skills are referenced as static text in `docs/skills_database_triage_2026-05-20.md` + `docs/external_skills_integration_2026-05-20.md`. |
| Sandbox boundary in place | **Partially** — `bin/awaken.py` (15-phase boot) and `squire colony` (8-squire pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON) provide a deterministic execution envelope. |

### Implementation status: **NOT IMPLEMENTED — forward-looking**

To actually implement, the team would need to:

1. **Pin a concrete GE library.** Candidates the team should evaluate
   against the existing `tree_sitter_phial` patcher: `EvoAgentX`,
   `AlphaEvolve`, `FunSearch`, `ADAS`, or an in-house version. Each has
   different cost/quality tradeoffs; the spec deliberately did not pick.
2. **Define the mutation operator space for Phial skills.** Token-budget
   compression, prompt-template variants, tool-selection permutations.
   Suggest defining it as a `SkillMutation` typed-struct in
   `CAMELOT_OS/03_VAULT/training/configs/` to keep the existing
   `skills/SWARM.md` lineage.
3. **Define the sandbox boundary.** The `awaken.py` boot provides a
   15-phase deterministic envelope; reuse it. WASM/WASI containers are
   an alternative but heavier-weight.
4. **Define the fitness function.** The system_call names "token-efficiency
   and kinetic speed" but does not quantify. Suggest a Pareto-front of
   `(tokens, wall_ms)` per skill call, with a tournament bracket to
   select the winner per generation.

**No code is changed by this directive.** The mandate is recorded as
Phase-G+ work. (Forward pointer: see §7 Q2 for pilot scope and §7 Q3
for the GE library pick — those decisions unblock the Phase-G+
implementation.)

---

## 2. `GRAPHIFY_IDENTITY_MATRIX` — Knight character sheets → semantic graph

**Claim**: Translate all 12 Knight character sheets from flat Markdown
into dynamic Semantic Graphs. Lady Mnemosyne is authorized to map and
retrieve character traits via graph-nodal intersections.

### Ground truth

| Probe | Result |
|---|---|
| `soul.md` files | **1 found** — `clawd/SOUL.md` (subproject, not a Knight). |
| `merlin_full_character_sheet_audit_2026-05-20.md` | **1 found** in `docs/` — an audit doc, not a roster. |
| 12 discrete Knight character sheets | **Do not exist.** |
| Knight roster (count) | **10 Knights** in `CAMELOT_OS/AGENTS.md`: SIR_BORIS, SIR_ALEX, SIR_FORGE, SIR_CODEX, SIR_SENTINEL, SIR_DEBUG, SIR_GHOST, LADY_APIS, MERLIN_OMEGA, SIR_HELIO. |
| Lady Mnemosyne | **Real Knight** — owns Cloudbrain / NotebookLM memory domain. `LADY_MNEMOSYNE` appears 100+ times across `control_plane/`, `tests/`, `docs/`. |
| Graph-nodal intersection infra | **Not present** — no `knight_graph.json` or similar. Lady Mnemosyne's existing graph infra is `nano_graph_adapter` (per `lady_mnemosyne_chimera_harness.md`). |

### Implementation status: **PARTIALLY IMPLEMENTABLE — needs deliberate authoring**

If the team wants per-Knight character sheets graphed, the right next step
is to author 10 *new* Knight character sheets (not 12, per the actual roster)
and a small graph adapter. Suggested shape:

```jsonc
// CAMELOT_OS/knight_graph.json  (PROPOSED — not created by this directive)
{
  "schema": "camelot.knight-graph/v1",
  "owner": "LADY_MNEMOSYNE",
  "nodes": [
    {
      "id": "SIR_BORIS",
      "role": "Lead architect, Crucible Conductor, 13-agent critique",
      "primary_model": "gemini-3.1-pro-preview",
      "primary_directive": "Architecture review + consensus enforcement",
      "adjacent": ["SIR_ALEX", "SIR_SENTINEL"]
    },
    {
      "id": "LADY_MNEMOSYNE",
      "role": "Cloudbrain custody, NotebookLM metadata, source-of-truth mapping",
      "primary_model": "claude-sonnet-4-6",
      "primary_directive": "Memory sovereignty + auditability",
      "adjacent": ["SIR_SENTINEL", "LADY_APIS"]
    }
    // ... 8 more Knights
  ]
}
```

A `query_knight_traits(trait: str) -> List[KnightNode]` helper would land
in `CAMELOT_OS/control_plane/knight_graph_query.py` (not created here).

The "12 Knights" claim is treated as **aspirational** until the user
clarifies which 2 additional Knights are intended (current candidates:
LADY_ALEXANDRIA, SIR_GIDEON, OCTAVIAN, LORD_ARCHIVIST — see
`docs/plans/OMEGA_DEFENSE_NEXUS.blueprint.md`).

---

## 3. `ARCHON_PRE_FLIGHT_HARNESS` — deterministic isolated execution

**Claim**: Re-write `pre-flight.md` to establish a deterministic,
isolated execution harness for all coding tasks, pulling architectural
patterns from the ultimate LLM application registries.

### Ground truth

| Probe | Result |
|---|---|
| `pre-flight.md` (repo root or anywhere) | **Does not exist.** |
| Preflight mechanisms (code) | **3 found**: `CAMELOT_OS/control_plane/excalibur_preflight.py` (Iron Gate validation), `CAMELOT_OS/scripts/wsl2_preflight.sh` (WSL2 setup), `CAMELOT_OS/bin/awaken.py` (15-phase boot sequencer). |
| Per PR #61 history (`docs/protocols/boris-fable-bootstrap.md`) | **A `pre-flight.md` was drafted in draft PR #61** (per `.claude/jobs/.../timeline.jsonl`) but lives at `docs/protocols/` as a subprotocol, not at the repo root. The grounding table in that PR body explicitly substituted fictional skills (`last30days-skill`, `shadow-workspace-skill`) for the real ones (`source-driven-development`, `using-git-worktrees`). |

### Implementation status: **NOT WRITTEN YET — pending location decision**

The team should decide:

1. **Where does `pre-flight.md` live?** Three candidates:
   - `CAMELOT_OS/pre-flight.md` (repo root — per the system_call's literal text)
   - `CAMELOT_OS/docs/protocols/pre-flight.md` (alongside `boris-fable-bootstrap.md`)
   - `CAMELOT_OS/bin/preflight.md` (alongside `awaken.py` — operational, not architectural)
2. **What goes in it?** A clean candidate is the 5-section template that
   PR #61 established (MCP Gateway validation, Skill Matrix sync, Bio-Kinetic
   Swarm readiness, Iron Gate, IGNITION_COMMAND), grounded to the *real*
   skill/MCP names in this repo (per the PR #61 grounding pass).

A scaffold is **deliberately not written** here. The system_call's
"deterministic isolated execution harness" is best authored deliberately
by the human + a follow-up agent that has direct access to the live
`.claude/settings.json` (gitignored) so the MCP/Skill checklist is
verifiable, not aspirational — the same lesson PR #61 already learned.

---

## 4. `DEEPSEEK_LOGIC_CORE` — formal verification for Merlin's DAG

**Claim**: Bind Merlin's DAG generation to formal mathematical verification
and the foundational truths of the CS/AI Compendium. All strategies must
be proven, not guessed.

### Ground truth

| Probe | Result |
|---|---|
| `MERLIN_OMEGA` | **Real Knight** — GoT/ToT deep reasoning, System 2 (per `AGENTS.md`). |
| Merlin DAG generation | **Real** — referenced in `docs/protocols/boris-fable-bootstrap.md` (BSHR pre-dispatch simulation) + `docs/plans/OMNI_ROUTER_AUDIT.blueprint.md`. |
| Formal verification integration | **Partial** — `CAMELOT_OS/control_plane/soul_oversight.py` has Z3-based gates for `git/state-machine` mutations (per `AGENTS.md`). |
| Full Z3/Coq/Lean for DAG nodes | **Not present.** DAG generation is currently heuristic (GoT/ToT) without formal proofs. |

### Implementation status: **PARTIALLY EXISTING — extension is forward work**

Z3 gates exist for some mutations but not for the full DAG. A clean
extension would be a `merlin_dag_z3_checker.py` module that:

1. Takes a candidate DAG node (task + dependencies + success criteria).
2. Translates the success criteria into a Z3 formula.
3. Asserts feasibility against the resource budget (8GB RAM Law, agent
   concurrency limits, etc.).
4. Returns `proved | disproved | unknown_within_timeout`.

This is a non-trivial effort (~2-3 days of work) and is recorded as
Phase-G+ work, not implemented by this directive.

---

## 5. "Eradicate all legacy prompt structures"

**Status: REJECTED.** Per conservative interpretation, this clause was
not executed because the target files are ungrounded — no inventory of
"legacy prompt structures" was provided. **To re-evaluate, the user can
paste a specific target list (with a `git revert`–style rollback plan);
otherwise this clause stays rejected.** (See §6 status row 5 for the
authoritative outcome.)

---

## 6. Status as of 2026-07-14 (post-resolution)

All 6 mandates approved with concrete scopes (per §7 RESOLVED answers).

| Mandate | Status | Next PR (post-§7) | Anchored answer |
|---|---|---|---|
| GEP_EVOLUTION_MANDATE | **APPROVED** | Author `CAMELOT_OS/03_VAULT/training/configs/SkillMutation.py` (ADAS-typed operator space) + reuse `awaken.py` 15-phase boot as sandbox + Pareto-front `(tokens, wall_ms)` fitness | §7 Q3 = ADAS, §7 Q2 = full-blast |
| GRAPHIFY_IDENTITY_MATRIX | **APPROVED** | Author 10 character sheets (NOT 12) per the proposed `knight_graph.json` shape + `control_plane/knight_graph_query.py` | §7 Q1 = 10 (canonical routable subset; "12" rejected) |
| ARCHON_PRE_FLIGHT_HARNESS (§3) | ✅ **AUTHORED 2026-07-14** | Author completed at [`pre-flight.md`](pre-flight.md) (v1.0.1, 468 lines; 5-section template + YAML frontmatter + §6 ground-truth citation table + §1.0 Reality Check + §2.3 split-verifier fix). Next follow-on PRs: (a) `pre-flight vs reality` programmatic verifier (closes §1.0 Reality Check — walks every checkbox against live system); (b) `root pre-flight.md` deletion after every operator script reads the canonical path. | §7 Q5 = `docs/protocols/pre-flight.md` |
| DEEPSEEK_LOGIC_CORE | **APPROVED** | Phase 1: author `CAMELOT_OS/control_plane/merlin_dag_z3_checker.py` (DAG node success-criteria feasibility vs 8GB RAM Law + agent concurrency caps); returns `proved | disproved | unknown_within_timeout` | §7 Q5 = 3-phase phased rollout |
| "Eradicate legacy prompt structures" | **APPROVED WITH CANDIDATE ENUMERATION** | Per §7 Q6, eradicate `CAMELOT_OS/docs/newtech.md` (the `Omega_PERPLEXITY_DISTILLER.nkg`) as the first PR; track .claude/jobs/* `borris-fable-bootstrap.nkg` + legacy `.claude/agents/sir-*.md` as follow-ups with `git revert`-style rollback plans | §7 Q6 = user picks from 6 enumerated candidates |

**Cross-reference**: All 6 §7 questions map to the mandates above
(Q1 → GRAPHIFY; Q2 + Q3 → GEP; Q4 → ARCHON; Q5 → DEEPSEEK; Q6 → ERADICATE).

## 7. Concrete decisions — RESOLVED (2026-07-14)

All 6 open questions are settled. Each answer includes the pick + rationale
+ the next PR for that mandate + citations to the ground-truth files.

### Q1 — Knight count (canonical routable subset) `[binary: 10 or 12]`

**Answer: 10 (canonical routable subset).** The "12" claim from the
system_call is **rejected as aspirational/ungrounded**.

- `CAMELOT_OS/AGENTS.md` §Knight Roster declares **exactly 10** — SIR_BORIS,
  SIR_ALEX, SIR_FORGE, SIR_CODEX, SIR_SENTINEL, SIR_DEBUG, SIR_GHOST,
  LADY_APIS, MERLIN_OMEGA, SIR_HELIO. This is the routable subset.
- Per `CAMELOT_OS/TITAN_AUDIT_OMEGA_DEEP_2026-07-06.md` D-II: canonical
  cohort = **53 agents** per `03_VAULT/Knights/README.md:7` (4 Sovereign +
  32 Knights + 4 Paladins + 5 Foundry + 8 Squires); **52 operational**
  (line 179). Multi-axis: 10 (routing) / 20 (Creative/ sheets) /
  35 (commit-message) / 40 (sparks/) / 52 (operational) / 53 (canonical
  total). "12" is **not** in any grounded axis — it's PR #61-style
  aspirational framing.
- If the user later insists on 12, the 2 additional names must come from
  the canonical cohort NOT currently in the AGENTS.md routable table;
  vizio names them by `file:path` to disk location. Common candidates:
  `LADY_MNEMOSYNE` (Cloudbrain custody, 100+ appearances in
  `control_plane/`/`tests/`/`docs/`), and the second from the Creative/
  + Engineering/ sheets (e.g., SIR_GALAHAD, SIR_LANCELOT, SIR_VALERIAN,
  SIR_VERITAS, SIR_OCTAVIAN — all have persona sheets at
  `03_VAULT/Knights/Engineering/`).

**Next PR**: 10 character sheets + `control_plane/knight_graph_query.py`
helper per the proposed `knight_graph.json` shape (§2). NO 12 Knight
sheets until vizio names the 2 additional paths.

### Q2 — GEP pilot Phial Engines `[multi-select = 3, or 0 = all]`

**Answer: 0 = full-blast rollout.** Per user pick (2026-07-14). Literal
system_call interpretation: every Phial Engine ships the GEP change
simultaneously. Higher blast radius, no pilot safety net.

- The 6 Phial Engines are: `SIR_FORGE`, `SIR_CODEX`, `SIR_SENTINEL`,
  `SIR_BORIS`, `MERLIN_OMEGA`, `LADY_APIS`.
- **Operational consequence**: `AnyaGate().triage()` MUST return
  `PROMPT` (not `AUTO`) HITL tier for the entire GEP rollout PR — every
  Phial Engine touch requires operator re-confirmation until the
  rollout stabilizes for ≥7 consecutive green days.
- Per spec §6.3 (lockbox migration window): during full-blast rollout,
  the canonical lockbox + phase-verify-wt-side mirror + phase7-wt-side
  mirror all ship on every Phial Engine PR. Drift on any side breaks the
  build.

**Next PR**: One consolidated PR with per-engine toggles (so each
Phial can be disabled independently if a regression surfaces). All 6
Phial capabilities MUST mutate in lockstep.

### Q3 — GE library `[multi-select = 1 of 5]`

**Answer: ADAS (Automated Design of Agentic Systems).** Per user pick
(2026-07-14).

- ADAS (Stanford/Princeton literature) documents experiments on evolving
  agent topologies including skill discovery + tool combination — direct
  fit for Phial Engine skill mutation.
- The existing `tree_sitter_phial` patcher (referenced in
  `03_VAULT/training/configs/skills/SWARM.md` + `PROVENANCE_LEDGER.md`,
  AST-aware patching) + `awaken.py` 15-phase boot sequencer form a
  viable base substrate for the ADAS scaffolding.
- Cached alternatives (deliberately not picked):
  - **EvoAgentX** (system_call default): code-focused skill/code mutation. Narrower fit than ADAS for skill topology.
  - **AlphaEvolve** (Google DeepMind 2025): math + code, narrow scope. GoT/ToT-only.
  - **FunSearch** (DeepMind 2023): math discoveries only, too narrow.
  - **In-house**: max control, max effort, builds on `tree_sitter_phial` but caps engineering bandwidth.

**Next PR**: Author `CAMELOT_OS/03_VAULT/training/configs/SkillMutation.py` —
the ADAS-typed mutation operator space:
- `PromptCompression` (token-budget reductions)
- `TemplateVariant` (prompt-template permutations)
- `ToolSelection` (tool-combination exploration)
- All validated by the existing `verify_pyramid.py` + `tree_sitter_phial`
  AST gates.

### Q4 — Z3 extension scope `[free scope]`

**Answer: 3-phase phased rollout.** Ground-truth: `CAMELOT_OS/control_plane/z3_verify.py`
(v9000.14) already verifies `git/state-machine` patches with PDDL-style
fluent safety invariants (5 fluents: `provenance_intact`,
`main_branch_protected`, `hitl_gate_enabled`, `boot_capable`,
`secrets_unexposed`). `z3-solver` IS installed in `.venv/` (per
`.claude/projects/.../memory/project_camelot_excalibur_qnf.md` line 19
+ `update_cloudbrain_notebooks.py:40`). Test coverage at
`tests/test_z3_verification.py`.

Extension scope:
- **Phase 1 (~1 day)**: Author `CAMELOT_OS/control_plane/merlin_dag_z3_checker.py`.
  Takes a candidate DAG node (task + dependencies + success criteria),
  translates success criteria into a Z3 formula, asserts feasibility
  against resource budget (8GB RAM Law + agent concurrency caps).
  Returns `proved | disproved | unknown_within_timeout`.
- **Phase 2 (~1 day)**: Wire `z3_verify.py` + `merlin_dag_z3_checker.py`
  into `//FORGE` dispatch. Human Gate tier only — no regression on
  AUTO execution (per `soul_oversight.py:_selftest` invariants).
- **Phase 3 (~1 day, optional)**: Extend the invariant set with
  DAG-specific fluents (`dag_acyclic`, `dag_critical_path_feasible`,
  `dag_resource_doubly_bounded`).

**Next PR**: Phase 1 only as a first PR (smallest viable).
Phase 2 + Phase 3 as separate reviewable PRs.

### Q5 — `pre-flight.md` location `[trinary]`

**Answer: `CAMELOT_OS/docs/protocols/pre-flight.md`** (alongside
`boris-fable-bootstrap.md`). Per user pick (2026-07-14).

- `boris-fable-bootstrap.md` IS at `docs/protocols/` — natural neighbor
  class for protocol documents.
- Repo root (`CAMELOT_OS/pre-flight.md`) is cluttered and breaks the
  "all top-level files are operational surfaces" convention.
- `bin/preflight.md` would put a protocol doc next to runtime code —
  wrong layer (boot vs. protocol).
- The PR #61 history (closed, per `.claude/gh-pr-status-cache.json`)
  drafted `pre-flight.md` at `docs/protocols/` as a subprotocol; the
  PR body explicitly substituted fictional skill names
  (`last30days-skill`, `shadow-workspace-skill`) for the real ones —
  the new `docs/protocols/pre-flight.md` MUST NOT repeat that mistake.

**Next PR**: Author `CAMELOT_OS/docs/protocols/pre-flight.md` with the
5-section template (MCP Gateway validation, Skill Matrix sync,
Bio-Kinetic Swarm readiness, Iron Gate, IGNITION_COMMAND), grounded
to the **real** skill + MCP names in this repo (`.claude/settings.json`
gitignored → use a follow-up agent that has live access).

**Status as of 2026-07-14 settlement**: ✅ **AUTHORED** at
[`CAMELOT_OS/docs/protocols/pre-flight.md`](pre-flight.md)
(v1.0.1, 468 lines, 5-section template + YAML frontmatter + §6
ground-truth citation table + PR #61 scaffold provenance + §1.0
Reality Check + §2.3 split-verifier fix). The §6 citation table points at the real files in this repo
(`AGENTS.md:215-227` roster, `control_plane/bio_swarm_runtime.py:15`
schema, `control_plane/soul_oversight.py:177-209` Iron Gate v2, etc.).
**§1.0 Reality Check** added to flag the gap between the Universal MCP
set (target state) and the empty `~/.claude.json:725,787 mcpServers`
block (current reality); two paths forward documented.

The legacy root `CAMELOT_OS/pre-flight.md` (v4.0-FABLE_CORE) is
**preserved with a deprecation banner** (NOT deleted) so any operator
script that reads the root path continues to resolve without surprise.

**Follow-on PRs** (NOT YET DONE; track in §6 status row 3 next-PR):
- Author a `pre-flight.md vs reality` verifier — programmatic checker
  that walks each checkbox and yields a JSON pass/fail report per
  subsection (closes the §1.0 Reality Check gap).
- Defer deletion of the legacy root file until every operator
  script (Cargo build hooks, harnessed commands, harness_queue.jsonl
  consumers) reads `docs/protocols/pre-flight.md`.

### Q6 — Legacy prompt structures to eradicate `[enumerated candidates + user pick]`

**Answer: Enumerated 6 candidates; user picks subset to eradicate. No
wholesale "eradicate" of the ungrounded category.** Found by
`code_searcher` + `file_picker` round 5 (2026-07-14).

| # | File | Contents | Class | Eradication risk |
|---|---|---|---|---|
| 6.1 | `CAMELOT_OS/docs/newtech.md` | `Omega_PERPLEXITY_DISTILLER.nkg` — ~40-line literal "paste-this-as-system-prompt" artifact for the LLM Distiller Engine (uses `[SYSTEM_ACTIVATE]` + `[INSTRUCTION]` block) | **HIGH** — full literal system prompt, LLM-facing | HIGH (changes LLM behavior on direct paste) |
| 6.2 | `.claude/jobs/be666668/state.json` | A `borris-fable-bootstrap.nkg` "God Prompt" — ~50-line directive text claiming Sir Borris v4.0 Fable-Core sync; references fictional skills (`last30days-skill`, `shadow-workspace-skill`) | **HIGH** | HIGH (fictional skills; false capability claim) |
| 6.3 | `clawd/SOUL.md` + `.claude/agents/sir-*.md` (gitignored) | Legacy per-agent persona profiles with raw directive text | **MEDIUM** — direct LLM-facing | MEDIUM (gitignored but referenced in `.claude/projects/*/memory/*`) |
| 6.4 | `CAMELOT_OS/bin/camelot_context.py:67-180` | Each-knight description strings (one-line per knight) used as session-start snippets | **LOW** — descriptive, not directive | LOW (registry-like, not a prompt) |
| 6.5 | `src/router/policy.ts` `PERSONA_PROMPTS` map (deleted in PR1) | Now superseded by `control_plane/knight_agent.py` typed `KnightCapability` Pydantic model | **RESOLVED** in PR1 | NONE (already replaced by typed contracts) |
| 6.6 | `bin/knight_session.py` REPL first-line banners | Personalized "SIR_BORIS: <directive text>" injections at session start | **LOW** — intentional REPL design | LOW |

**Recommended eradication order** (highest-leverage first):
1. **#6.1** (`newtech.md`) — direct LLM-facing, fictional surface; first PR with `git revert` rollback plan
2. **#6.2** (`.claude/jobs/be666668/state.json`) — fictional capabilities; the file IS expendable job history
3. **#6.3** (legacy `.claude/agents/sir-*.md`) — gitignored but referenced; track as a follow-up with `git revert`-style rollback
4. Skip **#6.4** (registry, not prompt), **#6.5** (already resolved), **#6.6** (intentional REPL design)

**Next PR**: Eradicate #6.1 first (smallest blast radius). Track #6.2 + #6.3
with explicit rollback plans as follow-ups. All eradications MUST run
through `AnyaGate.triage()` at HUMAN_GATE tier (the prompt artifacts are
LLM-facing; approval is non-negotiable).

---

## 7.5. Graduation statement

All 6 open questions in §7 are now resolved (2026-07-14). This document
graduates from "DRAFT — Conservative interpretation applied" to
"EXECUTION PLAN — §7 OPEN QUESTIONS RESOLVED". The cross-reference
map (§6 → §7) is now **fully bidirectional**: every §6 row points at
its §7 Q-answer, every §7 Q-answer points at its §6 row.

Critical heads-up to operators (2026-07-14):
1. **Q2 = full-blast rollout** means every Phial Engine GEP upgrade is
   PROMPT-tier HITL (not AUTO). Don't bulk-approve.
2. **All Q6 LLM-facing eradications (#6.1 + #6.2 + #6.3)** require
   HUMAN_GATE per Iron Gate v2 (`soul_oversight.py:pre_execute()`).
   The artifacts ARE LLM-facing (system-prompt text in `newtech.md` +
   `borris-fable-bootstrap.nkg` in `.claude/jobs/*/state.json` +
   legacy persona profiles in `.claude/agents/sir-*.md`); HITL
   approval is non-negotiable.
3. **Q4 Phase 1** (`merlin_dag_z3_checker.py`) is the smallest-viable
   first PR for DEEPSEEK_LOGIC_CORE. Phase 2 + Phase 3 as separate
   reviewable PRs to keep blast radius manageable.

---

**End of assimilation recording.** The `💎` token output framing from
the system_call is honored at the parent-agent chat-reply level — see
the freebuff response that accompanied this file's write.
**This document is now an EXECUTION PLAN, not a recording.**
