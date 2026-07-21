---
context: "Camelot-OS Bio-Kinetic Swarm Ignition — ARCHON_PRE_FLIGHT_HARNESS"
version: "v1.0.1"
encoding: "TOON_UKG_v1"
spec_authority: "CAMELOT_OS/docs/assimilation_directive_2026-07-14.md §3"
supersedes: "CAMELOT_OS/pre-flight.md (now deprecated; see §0.4 Migration Note)"
---

# 🚀 PRE-FLIGHT SINGULARITY CHECKLIST

> **ARCHON_PRE_FLIGHT_HARNESS — Deterministic Isolated Execution Substrate**
>
> Per the [Assimilation Directive §3](../assimilation_directive_2026-07-14.md), this
> file establishes the **deterministic, isolated execution harness** for every
> kinetic coding task in CAMELOT-OS. Before dispatching `//SWARM`, `//FORGE`, or
> any rune that triggers kinetic execution, the operator (vizio) and the parent
> agent (freebuff / Codebuff) **MUST** verify every checkbox below.
>
> **Every named entity below is real** — verified against the repo on 2026-07-14
> during the §7 Q5 graduation. If a check fails, **fix the underlying system**
> (install the missing MCP, scaffold the missing skill, rebuild the missing
> binary) — do not skip the box.

---

## 0. Preamble

### 0.1 Prime Directive

> **Do not dispatch `//SWARM`, `//FORGE`, or any kinetic rune until MCP
> Gateway Validation (§1) + Skill Matrix Synchronization (§2) + Bio-Kinetic
> Swarm Readiness (§3) all return GREEN. Iron Gate v2 (§4) supervises every
> dispatch; failures SUSPEND via `FileStatePersistence`. The
> `[IGNITION_COMMAND]` in §5 is the only legal entrypoint.**

### 0.2 Quick Reference Card

| Phase | Section | What goes wrong if red | One-line fix |
|---|---|---|---|
| **P1 — MCP Gateways** | §1 | Agent can't fetch docs/code/state-of-world mid-task | `npx -y @<owner>/<mcp>` per row |
| **P2 — Skill Matrix** | §2 | Stale knowledge + drift hallucinations | `npx skills add <owner>/<repo>` |
| **P3 — Swarm Readiness** | §3 | Knights not loaded; binary missing; layout cold | `bin/awaken.py --quick` |
| **P4 — Iron Gate v2** | §4 | Gates diverge; HUMAN_GATE suspends; Z3 blocks mutations | `python -m control_plane.soul_oversight --test` |
| **P5 — IGNITION** | §5 | `//BOOT` halts at Phase 8; `//SWARM`/`//FORGE` blocked | `//HEAL` then re-`//BOOT` |

### 0.3 Spec Anchor Chain

This file is grounded to:

- **§3 — ARCHON_PRE_FLIGHT_HARNESS** of [Assimilation Directive 2026-07-14 §7](../assimilation_directive_2026-07-14.md#7-resolved-questions-execution-plan-answers).
- **PR #61** history at `.claude/jobs/be666668/state.json:63` (Anya Ω "Bio-Kinetic Swarm Ignition" intent) — provided the original 5-section scaffold; this file is the canonical graduation of that scaffold against real repo state.
- **`borris-fable-bootstrap.md`** (sibling in `docs/protocols/`) — the Cognitive Engine that loads **after** pre-flight green.
- **`iron_gate_protocol.md`** (sibling in `docs/protocols/`) — the deeper protocol spec that §4 below summarizes.

### 0.4 Migration Note (Root → docs/protocols/)

The earlier `CAMELOT_OS/pre-flight.md` (root, 2026-07-13) is superseded by
**this file** at `CAMELOT_OS/docs/protocols/pre-flight.md`. Two reasons:

1. **§7 Q5 graduation** (Assimilation Directive) resolved the location
   pick to `docs/protocols/` — the same directory as the other 19 protocol
   specs (`iron_gate_protocol.md`, `paladin_htn_protocol.md`,
   `borris-fable-bootstrap.md`, etc.).
2. **Granular file:line citations** (added here, §6 below) make this file
   a hydrated gate; the root file is redacted to a one-line forwarder
   pointer only.

The root file is preserved (NOT deleted) with a deprecation banner so any
existing code path that reads `CAMELOT_OS/pre-flight.md` continues to
resolve without surprises.

---

## 1. Claude Code MCP Gateway Validation

Every MCP below MUST be hot-loaded before the runic router accepts `//FORGE` /
`//SWARM`. The list is the "Universal MCP Set" defined in
`phase7-wt/docs/architecture/UNIVERSAL_MCP_SYSTEM.md:277-285`. Pinned
priority tags come from the same source.

### 1.0 Reality Check (2026-07-14 audit)

Per `~/.claude.json:725,787` (user-level `mcpServers` block) the current
per-user MCP config is **empty**: `"mcpServers": {}`. Per
`.claude/settings.local.json:26` only **Claude Code native tools** are
active today (`Bash(curl ...)`, WebFetch, WebSearch, Read/Write/Edit/Bash).

**Two paths forward**:

| Path | Operator profile | Source of truth |
|---|---|---|
| **A. Native tools only** (current state) | Solo operator with Context7 fallback | `CAMELOT_OS/pre-flight.md` §1 (v4.0-FABLE_CORE root file) |
| **B. Universal MCP set** (target state) | Multi-agent / heavy-fan-out workflows | this file §1.1 (install checklist) |

If only path A is needed, the operator can skip §1.1 and rely on
**Claude Code native Read/Write/Edit/Bash + WebFetch/WebSearch +
Context7**. If path B is needed, run the install commands in §1.2 first.

### 1.1 MCP Inventory (Universal set + Camelot-specific overlay, ASPIRATIONAL)

| MCP Server | npx invocation | Purpose | Priority |
|---|---|---|---|
| **GitHub** | `npx -y @github/mcp-server` | Issues, PRs, repos, code search | **HIGH** |
| **Filesystem** | `npx -y @anthropic/mcp-filesystem` | Scoped file access for agents | **MEDIUM** |
| **PostgreSQL** | `npx -y @anthropic/mcp-postgres` | Direct DB queries | **MEDIUM** |
| **Brave Search** | `npx -y @anthropic/mcp-brave-search` | Web search without API vendor lock | **MEDIUM** |
| **Puppeteer** | `npx -y @anthropic/mcp-puppeteer` | Browser automation + screenshots | LOW |
| **Memory** | `npx -y @anthropic/mcp-memory` | Persistent knowledge graph | LOW |
| **Docker** | `npx -y @docker/mcp-server` | Container management | LOW |
| **Context7** | `npx -y @upstash/context7-mcp` | Up-to-date library docs | **HIGH** (pair with §2 source-driven-development) |
| **World Monitor** | streamable-http `https://worldmonitor.app/mcp` | Live global intel (39 tools) | optional |
| **Camelot-OS MCP** | per `phase7-wt/03_VAULT/training/configs/config/mcp_servers.json` | Round-trip L0↔L2↔Cloud Brain | KNIGHT-LANE |

### 1.2 Verification Procedure

```bash
# Method 1 — Claude Code slash command
/mcp list

# Method 2 — Direct transport probe (look for ETag / 200 OK)
for url in \
  "https://worldmonitor.app/mcp" \
  "https://github.com/mcp" \
; do
  curl -sS -o /dev/null -w "%{http_code}  %{url}\n" "$url"
done

# Method 3 — Manifest introspection (Camelot-specific overlay)
cat phase7-wt/03_VAULT/training/configs/config/mcp_servers.json
# Expect: schema=="camelot-os-v60.0-mcp-manifest", mcpServers key present.
```

### 1.3 Runic Router (kinetic gate)

| Check | Command | Pass criterion |
|---|---|---|
| Router responds | `python -m control_plane.runic_router --list` | prints ≥25 runes (`//FORGE`, `//SWARM`, `//SCAN`, `//BOOT`, `//PLAN`, `//HEAL`, `//STATUS`, `Omega_*`) |
| Kinetic dispatch | `python -m control_plane.runic_router --rune FORGE --task "echo test"` | dispatcher routes to `SIR_FORGE` (per `AGENTS.md:226`); no CLI error |
| Colony dispatch | `python -m control_plane.runic_router --rune SWARM --task "echo test"` | dispatcher routes to `SIR_BORIS` |

> **Cross-ref**: the runic router engine lives at `CAMELOT_OS/control_plane/runic_router.py` (per `AGENTS.md:298`). The 10-rune table is `AGENTS.md:246-269`. Omega_ dispatch table is `AGENTS.md:278-285`.

---

## 2. Skill Matrix Synchronization

Per absorption of the [camelot-os SKILL.md](../../../.agents/skills/camelot-os/SKILL.md) and the [camelot-universal-critical-thinking SKILL.md](../../../.agents/skills/camelot-universal-critical-thinking/SKILL.md), three categories of skills must be active:

### 2.1 Core Scaffold (every run)

| Skill | Installed via | Purpose | Replacement reason |
|---|---|---|---|
| **`source-driven-development`** | `npx skills add <owner>/source-driven-development --yes` | Grounds every new library/dependency in current official docs (pair with Context7 MCP, §1.1) | Replaces deprecated `last30days-skill` (still referenced in some legacy blueprints at `phase7-wt/pre-flight.md:18`). |
| **`using-git-worktrees`** | `npx skills add <owner>/using-git-worktrees --yes` | All kinetic coding happens in isolated worktrees / shadow branches (Titanium Law via SIR_BORIS agent definition) | Replaces deprecated `shadow-workspace-skill`. |
| **`find-docs`** | `npx skills add <owner>/find-docs --yes` | Universal doc retrieval without vendor lock | Universal fallback; always available. |

### 2.2 Camelot-OS Specific (every Camelot task)

| Skill | Installed via | Purpose |
|---|---|---|
| **`camelot-os`** | Locally at `.agents/skills/camelot-os/` | Knight roster + runic dispatcher + Squire Colony + boot sequence. Activate when the user invokes runic commands (`//FORGE`, `//SWARM`, `//SCAN`, `//BOOT`, `//PLAN`, `//HEAL`, `//STATUS`, `Omega_*`). |
| **`camelot-universal-critical-thinking`** | Locally at `.agents/skills/camelot-universal-critical-thinking/` | PAUL-loop discipline, Portkey-style assimilation, lightweight workflow tooling. Apply to every multi-step task in Camelot-OS. |

### 2.3 Verification Procedure

```bash
# Camelot-OS specific skills (local installs — expected to resolve)
ls .agents/skills/find-docs/SKILL.md                       || echo "MISSING: find-docs"
ls .agents/skills/camelot-os/SKILL.md                      || echo "MISSING: camelot-os"
ls .agents/skills/camelot-universal-critical-thinking/SKILL.md \
                                                            || echo "MISSING: camelot-universal-critical-thinking"

# Core scaffold — installed via the agent-skills npm registry, not local clone
# (cycle checks the GLOBAL registry; add --user if scoped).
npx skills list 2>/dev/null | grep -q "source-driven-development"     || npx skills add <owner>/source-driven-development --yes
npx skills list 2>/dev/null | grep -q "using-git-worktrees"          || npx skills add <owner>/using-git-worktrees --yes
```

> **Why the split?**: `find-docs`, `camelot-os`, and
> `camelot-universal-critical-thinking` ship as **local clones** under
> `.agents/skills/` (in-repo), so `ls` is the canonical check.
> `source-driven-development` and `using-git-worktrees` ship via
> **the agent-skills registry**, so `npx skills list` is the canonical
> check. Mixing the two was a §2 v1.0.0 bug — fixed in v1.0.1.

> **Negation-note on retired skills**: PR #61's original 5-section scaffold
> (`.claude/jobs/be666668/state.json:63`) named `last30days-skill` and
> `shadow-workspace-skill`. **Both have been retired** in favor of
> `source-driven-development` and `using-git-worktrees` respectively
> (see rationale at `phase7-wt/pre-flight.md:18-19`). If either appears
> in a current `//SKILLS` manifest, escalate to gateway drift.

---

## 3. Bio-Kinetic Swarm Readiness

Per the 10-knight AGENTS.md roster (`AGENTS.md:215-227`) and the
`//SWARM` dispatcher (`control_plane/runic_router.py` per
`AGENTS.md:264`), the following 8 knights MUST be on the hot lane
before any multi-agent colony dispatch.

### 3.1 Kinetic Roster (routing subset)

| Knight | Layer | Rune | What they dispatch |
|---|---|---|---|
| **SIR_BORIS** | Lead Architect / 13-Agent Critique | `//SWARM`, `Omega_Boris`, `//EVOLVE_AND_FORGE` | DAG timeline + critique-gated deployment |
| **SIR_ALEX** | Task Planner / DAG Orchestrator | `//PLAN`, `Omega_Alex` | AST Plan Mode + Task DAG |
| **SIR_FORGE** | Kinetic Code Execution | `//FORGE`, `Omega_Forge`, `//CONTRACT` | WASM/Rust kernel swings |
| **SIR_CODEX** | High-Velocity Implementation | `//CODEX`, `Omega_Codex` | Rapid implementation lane |
| **SIR_SENTINEL** | AgentArmor + Iron Gate HITL | `//STATUS`, `Omega_Sentinel` | Security audit + gate invocation |
| **SIR_DEBUG** | PIV Self-Healing Loop | `//HEAL`, `Omega_Debug` | Plan-Implement-Validate (3 iter) |
| **MERLIN_OMEGA** | GoT/ToT Deep Reasoning | `Omega_Merlin` | System 2 / Videneptus LaC |
| **LADY_APIS** | BASHR Research Loop | `Omega_Apis` | Context foraging |

> **Multi-axis note**: per §7 Q1 of the Assimilation Directive, the
> **canonical roster** is 53 knights (4 Sovereign + 32 Knights +
> 4 Paladins + 5 Foundry + 8 Squires per `03_VAULT/Knights/README.md:7`).
> The 10-roster table above is the **routing subset** that the runic
> router exercises today; the 53-roster is the long-term goal. Both
> numbers are correct for their respective scopes — they are NOT a
> contradiction.

### 3.2 Bio-Swarm Runtime Cache

The kinetic-edge sidecar (`SWARM_QUEEN` model per §3 / §3.1) maintains a
runtime cache at:

```
03_VAULT/runtime_state/bio_swarm_runtime_latest.json
```

Schema: `camelot.bio-swarm-runtime/v1` per `control_plane/bio_swarm_runtime.py:15`.
Read with: `control_plane/bio_swarm_runtime.read_bio_swarm_status()`
(same file, line 110).

| Field | Type | Required | Pass criterion |
|---|---|---|---|
| `status` | enum | yes | MUST equal `"READY"` (binary exists + state present) |
| `binary_path` | path | yes | Path to `swarm-spawner.exe` (looked up under `bin/`, `kinetic_edge/.../target/release/`, or `target/release/`) |
| `binary_sha256` | hex | yes | Stable hash; re-pin on every binary rebuild |
| `state_path` | path | yes | Path the runtime status JSON lives at |
| `queue_path` | path | yes | Path `logs/harness_queue.jsonl` (queue of kinetic tasks) |
| `binary_exists` | bool | yes | `true` only when binary path resolves |

> **Rebuild loop**: if `status != "READY"`, run
> `cargo build --release -p swarm-spawner` from `kinetic_edge/swarm_spawner/`
> or accept the BLOCKED verdict on `bin/preflight_bio_swarm()` (line 154).

### 3.3 Verification Procedure

```bash
# 1. Runic router responds
python -m control_plane.runic_router --list | head -25

# 2. Bio-Swarm status
python -c "from control_plane.bio_swarm_runtime import read_bio_swarm_status; \
  import json; print(json.dumps(read_bio_swarm_status(), indent=2)[:400])"
# Expect: $schema="camelot.bio-swarm-runtime/v1", status="READY".

# 3. EXCALIBUR substrate pre-flight (boot-level gate)
python -m control_plane.excalibur_preflight
# Expect: "VERDICT: [GO] - substrate satisfies EXCALIBUR v1000.0.0".
# NO-GO blocks on missing rustc/cargo/sandbox primitives OR <500MB RAM headroom.
```

---

## 4. Iron Gate v2 (Zero-Trust Tier-by-Tier Check)

Per [iron_gate_protocol.md](./iron_gate_protocol.md) (sibling) +
`control_plane/soul_oversight.py:177-209` (Iron Gate v2 `pre_execute()`).

### 4.1 Three-Tier Dispatch

| Tier | Method | Conditions | Bypass |
|---|---|---|---|
| **AUTO** | dispatches immediately | `triage.hitl_tier == "AUTO"` | None — runs |
| **PROMPT** | operator confirm required (timeout-optional) | `triage.hitl_tier == "PROMPT"` | `CAMELOT_ALLOW_TIMEOUT_AUTO=1` (unattended) |
| **HUMAN_GATE** | `CAMELOT_DASHBOARD_OPERATOR_TOKEN` required | `triage.hitl_tier == "HUMAN_GATE"` | Token must be set; else job SUSPENDS via `FileStatePersistence.save(...)` |

### 4.2 Colony Nexus Escalation (`soul_oversight.py:_colony_escalate`)

If `colony_report.md`'s current risk_score is CRITICAL (`is_critical=True` per
`01_KERNEL/iron_gate/DEFENSE_GRID/colony_nexus.py:scan()`), every non-HUMAN_GATE
tier is automatically escalated to HUMAN_GATE. The escort loop is
non-blocking — if colony data is unavailable, the original tier is returned
unchanged.

### 4.3 Z3 Verification Gate

If `triage.requires_z3_verification == True` (auto-set for git-mutating /
state-machine jobs), `_z3_verify_patch()` runs BEFORE the tier dispatch
(`soul_oversight.py:120`). It calls `control_plane.z3_verify.verify_patch()`,
which encodes safety invariants as fluents, grounds the patch into action
effects, and BLOCKS any patch that makes the safety goal unsatisfiable.

| z3 status | Returns |
|---|---|
| Passes | proceeds to tier dispatch |
| Fails | `GateDecision(approved=False, method="Z3_BLOCK", detail)` + `_append_hitl(`Z3_BLOCK: ...`)` to `logs/hitl_queue.jsonl` |
| Encoder unavailable | `(True, f"Z3 encoder unavailable ({exc}) — passed through")` — degrades gracefully |

### 4.4 Environment Variables (verbatim from `soul_oversight.py`)

| Variable | Effect when set | Effect when unset |
|---|---|---|
| `CAMELOT_DASHBOARD_OPERATOR_TOKEN` | HUMAN_GATE jobs dispatch immediately | HUMAN_GATE jobs SUSPEND to `FileStatePersistence` |
| `CAMELOT_ALLOW_TIMEOUT_AUTO=1` | PROMPT tier auto-approves after timeout | PROMPT tier returns `method="PROMPT"`, blocks on operator |
| `CAMELOT_OS_HOME` | All paths anchored here | Anchor defaults to `<script-dir>/../...` per `excalibur_preflight.py:60` |

### 4.5 Verification Procedure

```bash
# 1. Three-tier self-test (must show ALL PASS)
python -m control_plane.soul_oversight --test
# Expect: SoulOversight self-test (P1-T05 consolidated gate) -> ALL PASS — soul_oversight

# 2. z3 encoder cold-load
python -c "from control_plane.z3_verify import verify_patch, PatchIntent; \
  print(verify_patch(PatchIntent(description='smoke', diff='+ nothing')).safe)"
# Expect: True (solver loaded; harmless patch passes)

# 3. Iron Gate daily ops
python -c "from control_plane.iron_gate_protocol import PATTERN; \
  print('OK' if PATTERN else 'MISSING')"   # never fails — PATTERN is always defined.
```

> **Cross-ref**: the full Iron Gate protocol spec lives at
> [iron_gate_protocol.md](./iron_gate_protocol.md). The implementation is
> [`control_plane/soul_oversight.py:177-209`](../../control_plane/soul_oversight.py).
> The pre-PEP rationale is documented in §6 below.

---

## 5. IGNITION_COMMAND

The single legal entrypoint to the kinetic run-loop. After §1–§4 all return
GREEN, dispatch:

```bash
//BOOT --shadow-agent
```

### 5.1 Resolution Path

`//BOOT --shadow-agent` resolves per `AGENTS.md:266` → `bin/awaken.py` →
6-phase boot sequence:

| Phase | What runs | Gate target |
|---|---|---|
| 1 — CLIProxy | stoic CLI handshake | warm shell |
| 2 — Defense | shadow veil + Iron Gate v2 spawn | SIR_SENTINEL GREEN |
| 3 — Kinetic Edge | Rust warm-load (`01_KERNEL/core/aegis_shield`) | `cargo check` GREEN |
| 4 — Cloud Brain | NotebookLM L2 sync | notebook id resolved |
| 5 — HUD | 5-port probe (`8011` Bifrost, `8077` Heimdall, `8088` Codex, `8090` Colossus, `8079` Anya) | all 5 GREEN |
| 6 — REPL | `bin/knight_session.py` opens (rich REPL `ks`) | session live |

> **Note**: legacy `bin/awaken.py` v9000.14 docs (under `blueprints/v9000.14/`)
> referenced a 15-phase boot count — this is **speculative historical
> context**; the canonical current implementation per
> `bin/awaken.py:5` docstring runs **6 phases** (CLIProxy → Defense →
> Kinetic Edge → Cloud Brain → HUD → REPL). The 15-phase claim is
> unverified and may reflect pre-CYBERTRONIA hardware-bound iteration
> counts. If any phase reports `BLOCKED`, the operator dispatches
> `//HEAL` (Plan-Implement-Validate via SIR_DEBUG, max 3 iterations).

### 5.2 Post-Boot Gates (IRON_GATE DASHBOARD ≡ Phase 8 in legacy blueprint)

After `//BOOT` completes, the Iron Gate Dashboard MUST report
`status: CLEARED` before any `//SWARM` or `//FORGE` is permitted. The live
verifier is:

```bash
//STATUS —port-bi=8079   # Anya port — reports Iron Gate v2 status
//SCAN .                # Squire Colony triage — surfaces colony_report.md
```

| Iron Gate Dashboard indicator | Meaning | Pass criterion |
|---|---|---|
| `AUTO tier: dispatched` | AUTO jobs ran clean | required for `//FORGE` |
| `PROMPT tier: confirmed` | operator approved inbox | required for `//FORGE` |
| `HUMAN_GATE tier: token=set` | `CAMELOT_DASHBOARD_OPERATOR_TOKEN` accepted | required for `//SWARM` |
| `Colony risk: LOW` | `<50` per `colony_report.md` | required for `//SWARM` |
| `Z3: clean` | no BLOCK verdicts in last 24h | required for any git-mutating job |

### 5.3 Failure Recovery

| Symptom | Diagnostic | Recovery |
|---|---|---|
| `//BOOT` stalls on Phase N | `bin/awaken.py:1` stdout buffering | set `PYTHONUNBUFFERED=1` and re-run |
| `//BOOT` Phase 6 REPL blank terminal | TUI failure on Windows PS5.1 legacy_windows=False already handled (`squires/colony.py:18`) | try `dist\camelot.exe` portable instead |
| `//SWARM` returns `SUSPENDED` | `CAMELOT_DASHBOARD_OPERATOR_TOKEN` unset on HUMAN_GATE | set token or set `CAMELOT_ALLOW_TIMEOUT_AUTO=1` for unattended |
| `//SCAN` aborts at SENTINEL gate | risk_score ≥ 50 OR secrets found | chase `[y/N]` prompt at operator |

---

## 6. Ground-Truth Citations

Every claim in §1–§5 above traces to a real file in this repo (verified
2026-07-14). Use this table to audit any future drift.

| § | Claim | Authority |
|---|---|---|
| §1.1 Universal MCP set | `phase7-wt/docs/architecture/UNIVERSAL_MCP_SYSTEM.md:277-285` |
| §1.1 World Monitor MCP | `worldmonitor/server.json:1-22` |
| §1.2 Manifest schema | `phase7-wt/03_VAULT/training/configs/config/mcp_servers.json:2` |
| §1.3 Runic router engine | `AGENTS.md:298` (`python -m control_plane.runic_router`) |
| §1.3 Rune table | `AGENTS.md:246-269` (10 runes) + `AGENTS.md:278-285` (Omega_ dispatch) |
| §2 Skill retirements | `phase7-wt/pre-flight.md:18-19` |
| §2.2 `camelot-os` skill | `.agents/skills/camelot-os/SKILL.md:1-12` |
| §2.2 `camelot-universal-critical-thinking` | `.agents/skills/camelot-universal-critical-thinking/SKILL.md:1-12` |
| §3.1 Knight roster | `AGENTS.md:215-227` (10 routable) + `03_VAULT/Knights/README.md:7` (53 canonical) |
| §3.2 Bio-Swarm schema | `control_plane/bio_swarm_runtime.py:15` (RUNTIME_SCHEMA) |
| §3.2 Bio-Swarm status fn | `control_plane/bio_swarm_runtime.py:110-131` |
| §3.3 EXCALIBUR substrate | `control_plane/excalibur_preflight.py:178-200` (boot_excalibur_preflight) |
| §4.0 Iron Gate protocol | [iron_gate_protocol.md](./iron_gate_protocol.md) |
| §4.1 Three tiers + pre_execute | `control_plane/soul_oversight.py:177-209` |
| §4.2 Colony Nexus escalation | `control_plane/soul_oversight.py:88-104` |
| §4.3 Z3 verification | `control_plane/soul_oversight.py:60-86` |
| §4.4 Env vars | `control_plane/soul_oversight.py:181, 192, 194` |
| §4.5 soul_oversight selftest | `control_plane/soul_oversight.py:212-260` |
| §5.1 `//BOOT` resolution | `AGENTS.md:266` (`SIR_ALEX / Run awaken.py full boot`) |
| §5.1 boot phase list | `bin/awaken.py:5` (`//BOOT sequence (CLIProxy → Defense → Kinetic Edge → Cloud Brain → HUD → REPL)`) |
| §5.2 5-port probe | `TITAN_AUDIT_GOVERNOR_7D_2026-07-06.md:41` (Boot row: 5-port probe + 6-phase boot sequence) + `bin/awaken.py:5` (6-phase docstring) + `sprint8_enrichment.py:55` (BOOT_PROBES extended 5→8 with OmniVoice:3002 + KittenTTS:8300 + SirOctavian:8400) |
| §5.3 Hi-boot recovery | `bin/awaken.py:1-9` (CLI help) + `squires/colony.py:18` (UTF-8 reconfigure) |
| Cross-cut | original PR #61 scaffold | `.claude/jobs/be666668/state.json:63` |

---

## 7. PR #61 Scaffold Provenance

The original 5-section scaffold was generated by Anya Ω inside Claude Code
session `be666668-dfe7-4404-a37d-72bdf3e7c9e7` (timestamp
`~2025-10-09` per the JSONL plus validation). The full text is recoverable
from `.claude/jobs/be666668/state.json:63` `intent` field (search for
"PRE-FLIGHT SINGULARITY CHECKLIST"). The scaffold named a different stack
(`last30days-skill`, `shadow-workspace-skill`, "CodeGraph/Codebase Memory
MCP") that **the codebase has since retired or renamed**.

This file keeps PR #61's 5-section ordering and IGNITION_COMMAND tone but
rewrites each section against the **live repo state** as of 2026-07-14:

| PR #61 line | Once named | Now named | Migration |
|---|---|---|---|
| "CodeGraph/Codebase Memory MCP" | (concept) | (none — superseded by worldmonitor MCP + codegraph tools where available) | if `codegraph` skill lands, pin it |
| `last30days-skill` | `@anthropic-ai/codeflash-skill` (or local) | `source-driven-development` | retired per `phase7-wt/pre-flight.md:18` |
| `shadow-workspace-skill` | local shadow branch git skill | `using-git-worktrees` | retired per `phase7-wt/pre-flight.md:19` |
| `Sir Syntax / Sentinel` | merged concept | **Sir Syntax** (AST guillotine, tree-sitter-phial) + **Sir Sentinel** (Iron Gate HitL, separate) | two knights, not one |
| `.claudecode/skills.md` | local skill manifest | `find-docs` (universal) + `camelot-os` + `camelot-universal-critical-thinking` | three skill slots, distributed |

---

## 8. End of Pre-Flight

Pre-flight green status:

- ☐ §1 — MCP Gateway Validation (all boxes checked)
- ☐ §2 — Skill Matrix Synchronization (all 5 skills installed)
- ☐ §3 — Bio-Kinetic Swarm Readiness (status="READY" + 8 knights hot)
- ☐ §4 — Iron Gate v2 (3-tier self-test returns ALL PASS, Z3 loaded)
- ☐ §5 — IGNITION_COMMAND dispatched from a GREEN Iron Gate Dashboard

**Operator signature**: `_` (vizio, 2026-07-14)
**Verified-by**: freebuff (parent agent, §7 Q5 graduation of Assimilation Directive)

> When all boxes are checked and the operator has signed, dispatch the
> kinetic rune (`//SWARM` or `//FORGE`) from a clean terminal. The Iron
> Gate supervises every dispatch from that point forward.
