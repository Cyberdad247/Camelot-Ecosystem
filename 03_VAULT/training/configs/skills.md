# Camelot Shared Skills Registry

Approved evolution rules are appended here after governance review.
---
## 2026-05-23T18:28:39.551699+00:00 :: SIR_HELIO
- Objective: Synchronize local state to Cloud Brain via //sync
- Learning: The local python CLI auth token can expire silently, but the MCP ethereal surface retains a separate, radiant auth heartbeat.
- Approved Rule: When cloudbrain sync commands fail due to auth expiration, fallback to manual ethereal synchronization using MCP notebook tools instead of halting the ascension.
- Verification:
  - `Verify mcp_notebooklm_note list succeeds when local CLI fails.`
- Scope:
  - control_plane/cloudbrain_sync.py
---
## 2026-08-22T00:00:00Z :: SIR_CODEX
- Objective: Create a reusable multi-repo branch audit skill that orchestrates Camelot knights for comprehensive repo analysis.
- Learning: Branch audit prompts forged for KBA (Cyberdad247/Kickbox-audio) can be generalized into a 7-phase pipeline (Discovery, Analysis, AnyaGate, Knight Dispatch, Secret Scan, Synthesis, Execution) that works on any multi-branch repo.
- Approved Rule: When auditing a Git repository with divergent branches, ALWAYS use the 7-phase multi-repo-branch-audit pipeline: clone bare, diff all branches against main, compile intent through AnyaGate, dispatch SIR_BORIS (architecture) + SIR_SENTINEL (security) + MERLIN_OMEGA (reasoning) + SIR_CODEX (implementation), run Squire Colony GHOST scan across all branches, and produce audit report + knight prompts + secret audit + integration plan.
- Verification:
  - `python .agents/skills/multi-repo-branch-audit/run_audit.py <repo_url>` exits 0
  - `skill('multi-repo-branch-audit')` loads successfully
  - `.agents/skills/multi-repo-branch-audit/SKILL.md` YAML frontmatter has name and description
- Scope:
  - .agents/skills/multi-repo-branch-audit/SKILL.md
  - .agents/skills/multi-repo-branch-audit/run_audit.py
