# PEER_ARCHITECTURE.md

**Status:** Draft for sovereign review
**Date:** 2026-08-13
**Tier:** APEX (Substrate-Reframe Architecture)
**Authority:** Sovereign (VaShawn O. Head / Vizion)
**Co-equal:** Companion to `docs/architecture/VFS_PREFLIGHT_DESIGN.md`, `docs/adr/0006-vfs-preflight-strict-mode.md`, `docs/superpowers/plans/2026-08-13-vfs-preflight.md`

---

## 1. Thesis

The engineering substrate follows the **PEER pattern** already declared in
`01_KERNEL/protocols/agno_orchestrator.md:27` (Plan, Execute, Express,
Review), extended with three infrastructure layers that have been implicit
in earlier CAMELOT-OS writes but never formalized:

- **Camelot** (top-level gate, above PEER): authorizes effects
- **HiVeiDe** = **Hive IDE** (multi-agent coordinator, between Plan and
  Execute; substrate = `docs/architecture/HIVE_BRIDGE_FINAL.md`)
- **Merlin** (runtime-adapter selector): bridges Plan and Execute, picks
  bounded runtime adapters per Plan's intent (per AGNO's Fountain phase)

This binds the existing concrete roster (Anya · SIR_SENTINEL ·
SIR_GIDEON · MERLIN_OMEGA · Nano-Knights · Hive IDE) to the abstract PEER
seam so that any future engineering task can name its place in the
discipline without re-deriving the architecture.

---

## 2. Role Map (7 named entities, 4 PEER roles, 3 infrastructure)

| # | Entity | Role | PEER-4 mapping | Primary substrate | Slice #1 alignment |
|---|--------|------|----------------|-------------------|-------------------|
| 1 | **Camelot** | Authorize effects (above PEER) | (above PEER) | OS-level gate; symbolic, not a code module | Slice #1 falls under Camelot's authority to authorize the gate |
| 2 | **Anya** | Scope intent; wrap user-visible output | **Plan** + **Express** | `control_plane/core/anya_gate.py::{AnyaGate,AnyaCompiler}`, Symbolect Gateway, TITANIUM_LAW #05 (`ANYA FIRST, ANYA LAST`) | Slice #1 uses AnyaGate.triage() as advisory (advisory only; preflight owns CONFIRMED/REJECTED) |
| 3 | **HiVeiDe** (Hive IDE) | Map + coordinate repository work / prompt routing / multi-agent switching | (Coordinator; between Plan and Execute) | `docs/architecture/HIVE_BRIDGE_FINAL.md`, `Bifrost`, `Switchboard`, `.hive/agents/`, `.hive/skills/`, `.hive/TITANIUM_LAWS.md` | (slice #1 does not invoke Hive IDE; reserved for slices #2-3) |
| 4 | **Merlin** | Select bounded runtime adapters per Plan; instantiate domain experts with TAL (per AGNO Fountain) | (Adapter-selector; Plan→Execute bridge) | `MERLIN_OMEGA` deep reasoning, AGNO Fountain phase | (reserved for slices #2-3) |
| 5 | **Nano-Knights** | Perform discrete tasks in isolated worktrees | **Execute** | AGENTS.md Codex v5.5 (mini-agents, `🧠.memory=store:false` semantics) | Slices #2-3 will spin up Nano-Knights for gate verification |
| 6 | **Sentinel** | Gate every effect (HITL) | **Review (gate)** | `SIR_SENTINEL` (AgentArmor); v1000 incarnation = `soul_oversight.IronGateV2` (legacy fallback) | Slice #1's HALT authorizer; Iron Gate is legacy fallback when Sentinel-v2 not yet built |
| 7 | **Gideon** | Audit every effect against 10 Shatterpoints | **Review (audit)** | `SIR_GIDEON` (Forensic Sting); GIDEON_RISK_MATRIX; Boris-Gideon TDD Lock pattern | Slice #1 advisory; full enforcement at slices #2-3 |

**Why 7 entities but only 4 PEER roles:** Anya covers both Plan and
Express per TITANIUM_LAW #05 (Anya wraps all Knight→User communication).
Camelot, HiVeiDe, and Merlin are *infrastructure layers outside PEER's
4 roles* — they shape and route but don't consume Plan/Execute/Express/
Review roles themselves.

---

## 3. PEER Seam Discipline (for engineering tasks)

Any new engineering task — file write, refactor, gate, slice, plan,
schema — names itself in three coordinates:

1. **PEER role(s)** it primarily exercises (Plan / Execute / Express /
   Review).
2. **Authorizer**: which top-level gate has jurisdiction? (Slice #1
   pretends this is "Camelot" symbolically; future slices #2-3 likely
   model it as SIR_SENTINEL with Iron Gate as fallback.)
3. **Coordinator**: do Hive IDE / Bifrost get involved? (Slice #1 does
   not invoke them; slices #2-3 do.)

The discipline: a task does not run if any of the three coordinates is
undefined. Defining them is the AGNO **Deliberation** phase done by
**Lukas** in the 5-Panel Debate workflow, then handed off to slice-level
specs (like the VFS_PREFLIGHT_DESIGN.md this document companions).

---

## 4. Slice #1 (VFS Preflight) re-thread

Slice #1 was originally drafted as **augmentation above v1000-EXCALIBUR-A**
with `soul_oversight.IronGateV2` as the HITL authorizer. The sovereign
2026-08-13 directive retargets it to **PEER substrate** with
**Sentinel+Gideon** as canonical Review pair:

| Slice #1 authorizer | Previous: v1000 Iron Gate | New: PEER Sentinel+Gideon pair |
|---|---|---|
| Halt decision | Iron Gate `pre_execute(...)` | Sentinel v2 (when built) → for now: Iron Gate falls back to Sentinel's v1000 incarnation (`soul_oversight.IronGateV2(GateKeys.PREFLIGHT).pre_execute(...)`) |
| Forensic audit | (none — slice was silent) | Gideon v2 (when built) → for now: Scorpion Sting adapter that runs GIDEON_RISK_MATRIX against each REJECTED check before promotion |
| Substrate availability | Required | Optional; graceful-degradation sentinel `advisory_unavailable` if substrate missing |

The Iron Gate reference is **not deleted**; it is **demoted to legacy
fallback** for v1000-EXCALIBUR-A hosts where Sentinel-v2 hasn't been
built yet. The substrate-vs-spec patch in slice #1's spec §3.3 +
decisions log row 9 already establishes this graceful-degradation
discipline.

**Concrete spec changes (governance patch on slice #1, this commit):**
1. Spec header "Substrate" line updated to reference PEER substrate.
2. Spec §3.3 "Reuse, not replacement" rewritten: Sentinel+Gideon canonical,
   Iron Gate legacy fallback.
3. Spec §3.4 (new) "PEER substrate mapping" — short table.
4. Spec §10 cross-references list adds this document.
5. Spec §8 Decisions Log adds a row recording the substrate swap.
6. Plan Task 6 / Task 8 / Task 9 surface Sentinel+Gideon implementation
   stubs the implementer must build before Sentinel-v2 ships.

---

## 5. AGNO Intersection

The AGNO 5-Panel Debate in `01_KERNEL/protocols/agno_orchestrator.md`
is a different stack (Agno / Merlin / Lukas / LightAgent / LangGraph)
than PEER. AGNO is **studio-side**: voice / podcast / multimodal
choreography. PEER is **engineering-side**: code / gates / worktrees.

**They intersect at Plan + Express roles:**

- AGNO's **Merlin** (Persona Generator in Fountain) is a *flavor* of the
  PEER-substrate Merlin's "runtime-adapter selection." When work in
  PEER-land touches AGNO (e.g., voice feedback for a SIC pingback or a
  Vivisect audio aftermath), the call is delegated from PEER's
  Express role to AGNO's Synthesis/LangGraph role.
- AGNO's **Lukas** (Architect/Deliberation) is the *prompter* who feeds
  the PEER Plan role. Lukas runs ToT/Bewertungsmatrix; PEER's Plan role
  receives scope from Lukas.

For slice #1 (VFS preflight, no studio work) AGNO is **not invoked**.
For slice #4 (Bio-Kinetic Swarm Harness) AGNO may be invoked for voice
announcements; for slice #5 (Cartridge↔Knight Reforge) AGNO may be
invoked for sentinel-cardinality warnings. Each slice's spec will say.

---

## 6. Slice Forecast (per PEER seam)

| Slice | PEER roles exercised | Authorizer | Coordinator | Gates from Sentinel | Audit by Gideon |
|-------|----------------------|------------|-------------|---------------------|-----------------|
| #1 VFS Preflight | mostly Review (Sentinel emits halt decision; Gideon advective); touches Express for operator summary | Camelot | not invoked | boots up; Iron Gate fallback OK | Scorpion Sting on each REJECTED (advisory in slice #1) |
| #2 Cartridge Load Gate | Plan (Anya scopes cartridge load) + Review (Sentinel denies malformed load) + Express (Anya summary) | Sentinel | Hive IDE | gates cartridge binding on MISSING_TOOL/MISSING_CARTRIDGE | Scorpion Sting on every new cartridge |
| #3 Nano-Knight Promotion Gate | Plan (Merlin selects bounded adapter) + Execute (Nano-Knights in worktree) + Review (Gideon forensically) | Sentinel | Hive IDE | denies promotion unless EVP/UKG-crystal evidence class is CONFIRMED | Boris-Gideon TDD Lock + Scorpion Sting on every promotion |
| #4 Bio-Kinetic Swarm Harness | Plan + Execute + Express (full PEER sweep) | Sentinel | Hive IDE + AGNO LangGraph | every swarm-event REJECT requires Sentinel sign-off | Gideon GIDEON_RISK_MATRIX full + Anya cybernetics guard |
| #5 Cartridge ↔ Knight Reforge | Plan + Express primarily | Camelot | Hive IDE | (read-only reforge; no Sentinel gate beyond MISSING_CARTRIDGE on rollback) | (read-only; advisory only) |

---

## 7. Open Questions for Sovereign

1. **Sentinel-v2 module path:** When Sentinel-v2 is built, where should
   it live? Likely `control_plane/core/sentinel_v2/` (parallel to
   `anya_gate.py`, `soul_oversight.py`); alternative: `control_plane/security/sentinel_v2/`.
   Slice #1 does not require a decision but slices #2-3 do.

2. **Gideon forensic-adapter:**
   `SIR_GIDEON` is currently a forensic auditor via `//SCORPION` rune
   and `GIDEON_RISK_MATRIX.md`. Is the "audit every effect" pattern an
   inline call to `//SCORPION`, or a Python adapter?
   `control_plane/core/sir_socrates.py` exists as a dialectical warden;
   a `control_plane/core/sir_gideon.py` parallel would be cleanest.

3. **Express role ownership** — is it OK that Anya covers both
   Plan and Express (per LAW #05)? Or should a separate Express-layer
   entity take the user-facing comms (e.g., `ME`, bodyguards, layer
   6)? Given the user's roster didn't list an Express-only entity, the
   LAW #05 double-coverage is the conservative read. Sovereign may
   overrule.

4. **HiVeiDe profile lifecycle:** `.hive/agents/` has 2 files
   (`KICKBOX_GENESIS_KNIGHTS_MANIFEST.md`, `OMEGA_SIR_CODEX_BLUEPRINT_v1.0.nkg.md`).
   Is HiVeiDe a surfacing IDE-only (read-only), or does it also gate
   agent profile writes via Bifrost/SDJ? Slice #2 will need a write
   path; sovereign DNA on this affects how slice #2 plans.

5. **Slice #1's pre-existing `203c11f0`** commit.
   This PEER_ARCHITECTURE document is a NEW governing document.
   Patch to `VFS_PREFLIGHT_DESIGN.md` is a follow-up commit that
   RETARGETS slice #1's substrate from "augmentation above v1000" to
   "PEER-aligned native" with Iron Gate as legacy fallback. Sodality
   decides whether to squash or layer as separate commits.

---

## 8. Decisions Log

| # | Topic | Original | Final |
|---|-------|----------|-------|
| 1 | Architecture venue | v1000 augmentation | PEER-aligned native |
| 2 | Roster | (single Anya/Sentinel/etc.) | 7 entities, 4 PEER-roles, 3 infra layers |
| 3 | Sentinel role | SIR_SENTINEL = security only | = **Review (gate)** of PEER; canonical authorizer |
| 4 | Gideon role | SIR_GIDEON = forensic auditor | = **Review (audit)** of PEER; partner to Sentinel |
| 5 | HiVeiDe role | (not documented) | = **Hive IDE**, i.e. `.hive/agents/`, `.hive/skills/`, Bifrost, Switchboard (substrate-verified: `docs/architecture/HIVE_BRIDGE_FINAL.md`) |
| 6 | Anya role | (single "intent" role) | Plan + Express (per TITANIUM_LAW #05 every Knight-to-User is wrapped by Anya) |
| 7 | Merlin role | (unclear) | Runtime adapter selector (per AGNO Fountain); bridges Plan→Execute |
| 8 | Camelot role | OS name | Top-level authorizer (above PEER); symbolic in slice #1 |
| 9 | AGNO relationship | (none/orthogonal) | AGNO intersects PEER at Plan+Express; AGNO is studio-side, PEER is engineering-side |
| 10 | Slice #1 patch | Iron Gate is canonical verifier | Sentinel+Gideon canonical; Iron Gate = legacy fallback until Sentinel-v2 built |

---

## 9. Cross-References

- **AGNO/PROTOCOL substrate:** `01_KERNEL/protocols/agno_orchestrator.md`
- **Hive IDE reference:** `docs/architecture/HIVE_BRIDGE_FINAL.md`
- **Hive governance:** `.hive/TITANIUM_LAWS.md`
- **Slice #1 (companion):** `docs/architecture/VFS_PREFLIGHT_DESIGN.md`
- **Slice #1 ADR:** `docs/adr/0006-vfs-preflight-strict-mode.md`
- **Slice #1 plan:** `docs/superpowers/plans/2026-08-13-vfs-preflight.md`
- **v1000 Iron Gate legacy fallback:** `control_plane/core/soul_oversight.py::IronGateV2`
- **VFS_REPOSTIORY:** `vfs/{preflight,systeminstructions,skills,rosters,protocols}.md`
- **Knight roster:** `AGENTS.md` (Canonical Knight Roster, sovereign reference)
- **Substrate verification:** 2026-08-13 against `control_plane/core/anya_gate.py`, `control_plane/core/soul_oversight.py`, `control_plane/core/factory_lane.py`, `01_KERNEL/protocols/agno_orchestrator.md`, `.hive/TITANIUM_LAWS.md`, `docs/architecture/HIVE_BRIDGE_FINAL.md`.
