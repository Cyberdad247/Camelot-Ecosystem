# Instruction Governance Map

## Purpose
Define which instruction files are authoritative at runtime and how conflicts are resolved.

## Source Classification

### Authoritative
- `AGENTS.md`
- `docs/LAWS/TITANIUM_LAWS.md`

### Runtime System Behavior
- `01_KERNEL/config/CAMELOT_APEX_SYSTEM_PROMPT.md`
- `01_KERNEL/config/hitl_gate.json`
- `01_KERNEL/security/iron_gate.py`

### Orchestration Metadata
- `01_KERNEL/config/registry/god_prompt.json`

### Memory Policy
- `01_KERNEL/memory/UKG_CORE.toon`

## Conflict Resolution
Apply this order (highest to lowest):
1. `AGENTS.md`
2. `docs/LAWS/TITANIUM_LAWS.md`
3. `01_KERNEL/config/CAMELOT_APEX_SYSTEM_PROMPT.md`
4. `01_KERNEL/config/registry/god_prompt.json`
5. Other prompt/materialization files

If two layers conflict on safety/governance, the higher layer wins and lower-layer policy must be updated.

## Normalization Checks
- All file paths referenced by instruction docs must exist.
- HITL policy must be consistent across law, system prompt, and UKG memory rules.
- Confirmation secrets must come from environment variables in runtime.
- No instruction may require tools or modules that do not exist in this repo.

## Current Decisions
- HITL is required for high-risk actions.
- Runtime confirmation token source: `CAMELOT_HITL_CONFIRM_TOKEN`.
- Static confirmation token fallback is disabled by default.
