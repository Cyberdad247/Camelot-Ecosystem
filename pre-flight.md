---
context: "Camelot-OS Bio-Kinetic Swarm Ignition"
version: "v4.0-FABLE_CORE"
status: "GROUNDED — every item below maps to a real file, tool, or command in this repo"
---
# 🚀 PRE-FLIGHT SWARM IGNITION CHECKLIST

**[PRIME DIRECTIVE]**: Do not dispatch `//SWARM` or `//FORGE` until the MCP pipelines and Skill Matrices below are verified. Every checkbox names something that actually exists — if a check fails, fix the real system, don't skip the box.

### 1. MCP Gateway Validation
- [ ] **mcp_conductor**: wired in `.claude/settings.json` (`python -m control_plane.mcp_conductor`). Verify the module imports cleanly before trusting dispatch.
- [ ] **Filesystem / Shell**: Claude Code native Read/Write/Edit/Bash tools active (no separate MCP needed — these are built in).
- [ ] **Web grounding**: Claude Code native WebFetch/WebSearch + Context7 docs MCP available for zero-day documentation pulls.
- [ ] **Runic Router**: `python -m control_plane.runic_router --rune FORGE|SWARM` responds (kinetic + colony dispatch paths).

### 2. Skill Matrix Synchronization
> The skill registry is `.claude/skills/` (38+ skills). Fictional names from earlier drafts map to these real skills:
- [ ] **`source-driven-development`** — replaces "last30days-skill". Grounds every new library/dependency in current official docs (pair with Context7). Protects against stale-knowledge hallucination.
- [ ] **`using-git-worktrees`** — replaces "shadow-workspace-skill". All kinetic coding happens in isolated worktrees / shadow branches (already a Titanium Law in the SIR_BORIS agent definition).
- [ ] **`doubt-driven-development` + `verification-before-completion`** — adversarial review and evidence-before-claims gates loaded.
- [ ] **`dispatching-parallel-agents` + `subagent-driven-development`** — swarm fan-out patterns loaded.

### 3. Bio-Kinetic Swarm Readiness
- [ ] **SIR_BORIS (Orchestrator)**: `.claude/agents/sir-boris.md` synced to v4.0-FABLE (source of truth: `docs/protocols/boris-fable-bootstrap.md`). DAG/Crucible conductor ready.
- [ ] **SIR_SENTINEL (Iron Gate)**: `.claude/agents/sir-sentinel.md` + `sentinel_asm.py` scanner ready. Zero-trust diff audit before merge.
- [ ] **Cartridge sandbox**: signed-manifest enforcement in STRICT mode (sig→deny→HITL→allow→budget). Unsigned cartridges do not execute.
- [ ] **Boot state**: `//boot` (15-phase `bin/awaken.py`) green. Known intentional WARNs: Local LT Memory :8200 (needs `MODAL_ENDPOINT`); watch for CIM outage / Octavian WARN gotchas.

**[IGNITION_COMMAND]** (the real one — there is no `//TRANSCEND`):
```powershell
cd C:\Users\vizio\CAMELOT_OS
$env:PYTHONIOENCODING="utf-8"; .venv\Scripts\python.exe -X utf8 bin\awaken.py
```
Then dispatch via `/swarm` or `/forge` with SIR_BORIS as conductor.
