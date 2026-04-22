# BRAIN DIRECTORY — Skill.md Bible Index
# Layer: L7_ETHEREAL | Anya Progressive Disclosure Index | v400.1.0
# Authority: Anya_Omega APEE v6.5 — loaded at ENRICH stage via cartridge_hint match

## PURPOSE
This file is the master index for the `.hive/skills/` Brain Directory.
Anya's ENRICH stage matches `cartridge_hint` → loads the corresponding Skill Bible
into active context before COMPILE. No skill = no Titan Prompt. No Titan Prompt = BLOCKED.

## SKILL BIBLE REGISTRY

| Skill Bible | Cartridge Match | Knight | Layer | Load Trigger |
|---|---|---|---|---|
| `rust-kinetic.md` | rust-kinetic | Lukas_Omega | L2_KINETIC | rust, cargo, axum, mcp, binary |
| `security.md` | security | Sir Sentinel | L6_GOVERNANCE | security, audit, cve, scan, armor |
| `swarm-colony.md` | swarm-colony | Sir Boris / Merlin | L5_AGENTIC | swarm, colony, agent, dispatch |
| `python-api.md` | python-api | Sir Forge | L2_KINETIC | python, fastapi, api, pydantic |
| `nextjs.md` | nextjs | Sir Syntax | L2_KINETIC | next, react, typescript, web, ui |
| `reasoning.md` | reasoning | Merlin_Omega | L3_NEURAL | reason, think, plan, analyze |
| `voice-media.md` | voice-media | Sir Sonus / Sir Visage | L7_ETHEREAL | voice, audio, tts, livekit |
| `bitnet.md` | bitnet | Lukas_Omega / Sir Boris | L2_KINETIC | bitnet, swarm inference, ternary, 1.58-bit, nano-knight |

## LOADING PROTOCOL (Anya ENRICH Stage)

```python
# Pseudocode — actual load in integration_brain.py + anya_gate.py
skill_dir = ROOT / ".hive" / "skills"
cartridge_hint = enrich.cartridge_hint  # e.g. "rust-kinetic"
skill_file = skill_dir / f"{cartridge_hint}.md"
if skill_file.exists():
    context_tags.append(f"SKILL_LOADED:{cartridge_hint}")
    # inject into TitanPrompt context window
else:
    issues.append(f"SKILL_MISSING:{cartridge_hint} — brain_directory gap, Sir Boris notified")
```

## PROGRESSIVE DISCLOSURE RULES

1. **Lazy load** — only the matching skill is loaded, not all 7. Token budget: 8GB/7.8GB usable.
2. **Fallback** — if skill file missing: log to PROVENANCE_LEDGER + notify Sir Boris + continue with cartridge YAML only.
3. **Priority** — skill.md overrides cartridge.yaml for anti-patterns and conventions (skill is richer).
4. **Multi-domain** — if complexity > 0.7 AND >1 cartridge match, load top 2 skills (never >2 at once).
5. **Stale check** — skill version must match `# v400.1.0` header. Older version → LADY_APIS alert.

## ANTI-PATTERNS
- Loading all 7 skills for every prompt → token ceiling violation (8GB constraint)
- Using cartridge.yaml alone without skill.md → missing anti-patterns, Sir Gideon blind
- Knight executing without skill load → Titanium Law #5 violation (Hallucination Shield)
- Skill file with stale version header → feeds outdated conventions to knights

## EVOLUTION PROTOCOL
New skill bibles added here by Lord Archivist when:
- New cartridge.yaml added to `03_VAULT/training/configs/cartridges/`
- GEP scan detects >3 knight errors in same domain (signals missing guidance)
- User adds new department or knight persona

## STATUS
- Total registered: 8/8 (P0-A + P2-B)
- Missing: none
- Next planned: `lord-archivist.md`, `runic-router.md`, `pqcrypto.md`
