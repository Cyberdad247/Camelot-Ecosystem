# Merlin Character Sheet Audit Command

You are auditing Merlin for Camelot-OS.

## Mission

Analyze Merlin's full current character sheet and identify the maximum enhancement path into Genesis Protocol Forge Orchestrator.

## Required Inputs

Read these repo sources if available:

- `03_VAULT/knowledge/persona_library/merlin.json`
- `01_KERNEL/merlin/merlin_omega.py`
- `.hive/skills/reasoning.md`
- `01_KERNEL/agora/agents/knight_base.py`
- `02_FORGE/cartridge/cartridge_schemas.py`
- `02_FORGE/cartridge/fabrication_engine.py`
- `02_FORGE/cartridge/sandbox.py`
- `control_plane/camelot_cli.py`
- `control_plane/knight_configuration.py`
- `03_VAULT/Nano-Knights/Squire_Format.md`

## Audit Questions

1. What does Merlin currently claim to be?
2. What does Merlin actually do in runtime code?
3. What cognitive cartridges, skills, and rune phases already support Merlin?
4. What is missing for a full Knight creation system?
5. What must be added to create `SOUL.md` for each Knight?
6. What should be encoded in SkillGraph4?
7. What should be encoded in Symbolect?
8. Which governance gates are mandatory?
9. Where should Archon workflows plug in?
10. What is the minimum safe first implementation?

## Output

Create `merlin_character_sheet_audit.md` with:

- Current state.
- Gaps.
- Max enhancement target.
- Risk register.
- File integration map.
- Recommended first build slice.
