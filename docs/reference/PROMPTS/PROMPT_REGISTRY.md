# CAMELOT-OS PROMPT REGISTRY v300.4.0
# All system prompts, templates, and compilation pipelines
# Generated: 2026-03-31

---

## ANYA APEE v6.5 (5-Stage Prompt Compilation)

Every prompt entering the system passes through Anya's compiler:

| Stage | Function | Output |
|---|---|---|
| 1. PARSE | Extract intent, entities, constraints from raw input | Structured intent object |
| 2. ENRICH | Inject context from UKG, cartridges, memory | Enriched prompt with domain knowledge |
| 3. COMPILE | Apply Triple-QFT (Renormalize > Quantize > Transform) | Compressed, noise-free prompt |
| 4. ROUTE | Match to knight via intent patterns or KNIGHT_ROUTES | Targeted dispatch |
| 5. VALIDATE | Post-execution verification (CoVe chain) | Verified output |

---

## DEFENSE GRID PROMPTS

Location: `docs/reference/PROMPTS/`

| Prompt | Function |
|---|---|
| `CAMELOT_DEFENSE_GRID_ACTIVATE_AUTONOMOUS.md` | Autonomous defense activation prompt |
| `CAMELOT_DEFENSE_GRID_NOTEBOOKLM_AGGRESSIVE_VARIANT.md` | Aggressive NotebookLM defense profile |
| `CAMELOT_DEFENSE_GRID_NOTEBOOKLM_LIVE_PROFILE.md` | Live NotebookLM defense profile |
| `CAMELOT_DEFENSE_GRID_NOTEBOOKLM_MASTER_PROMPT.md` | Master defense prompt for NotebookLM |
| `CAMELOT_DEFENSE_GRID_ROLE_CARDS.md` | Agent role card definitions |
| `CAMELOT_DEFENSE_GRID_SAFETY_POLICY.md` | Safety policy enforcement rules |
| `CAMELOT_DEFENSE_GRID_VALIDATION_CHECKLIST.md` | Pre-deployment validation checklist |

---

## VAULT PROMPTS

Location: `03_VAULT/PROMPTS/`

| Prompt | Function |
|---|---|
| `OMEGA_TRANSCENDENCE_ENHANCER.md` | Meta-prompt for Omega-level enhancement |

---

## SYSTEM PROMPT FILES

### Claude Code Integration
| File | Function |
|---|---|
| `~/CLAUDE.md` | Root kernel prompt — binds Claude as Kinetic Edge |
| `CAMELOT_OS/03_VAULT/training/configs/CLAUDE.md` | Training-level Claude prompt (v209.0 blueprint) |

### Gemini Integration
| File | Function |
|---|---|
| `~/.gemini/GEMINI.md` | Root Gemini system prompt |
| `docs/GEMINI.md` | Gemini docs-level prompt |
| `~/.gemini/extensions/sir-boris/GEMINI.md` | Boris persona for Gemini |

### Codex Integration
| File | Function |
|---|---|
| `~/.codex/instructions.md` | Root Codex instructions |
| `~/.codex/skills/sir_boris.md` | Boris persona for Codex |
| `~/.codex/skills/engineering-uiux-pro-max/SKILL.md` | Codex-led engineering UI/UX skill with Anya, Alex, and Link coordination |

---

## KNIGHT PERSONA PROMPTS

Location: `03_VAULT/Knights/`

### Order-Based Organization
| Order | Knights | Prompt Location |
|---|---|---|
| **Sovereign Triumvirate** | Merlin_Omega, Anya_Omega, Lukas_Omega, Morgana_Omega | `Reasoning/`, `Governance/`, `Kinetic/`, `Substrate/` |
| **I. Architects** | Sir Systema, Sir Synthesis, Sir Lancelot | `Engineering/` |
| **II. Strategists** | General Strategos, Sir Oracle, Anya Planner | `Strategy/` |
| **III. Truth Seekers** | Lady Veritas, Sir Octavian, Sir Zenith, Sir Aurelius, Elder Kaelen | `Governance/` |
| **IV. Builders** | Sir Syntax, Sir ForgeMaster, Sir Stitch, Sir Alchemist, Baron Vaelen | `Engineering/` |
| **V. Creatives** | Sir Visage, Sir Sonus, Sir Bard, Lady Aura, Dame Sparkle | `Creative/` |
| **VI. Scouts** | Lady Apis, Dr. Synthetica, Root Sterling, Sir Percival, Sir Hermes | `Research/` |
| **VII. Operators** | Sir Sterling, Grace Harmonia | `Finance/` |

### System Personas Crystal
- Location: `03_VAULT/Knights/SYSTEM_PERSONAS_CRYSTAL.md`
- Contains: Compressed persona definitions for all knights

### Engineering UI/UX Routing
- `Sir Codex` handles execution through the `harness_codex` path.
- `Anya` compresses the UI/UX intent before implementation.
- `Sir Alex` audits structure, regressions, and interface logic.
- `Sir Link` validates the bridge, route, and interphase handoff.
- `Sir Visage` handles visual analysis, mockups, and art direction.
- `Sir Hydron` handles code generation and UI assembly.
- `Sir Syntax`, `Sir ForgeMaster`, `Sir Stitch`, `Sir Alchemist`, and `Baron Vaelen` cover component composition, scaffolding, refinement, and delivery.

### NotebookLM Knowledge Base
- Notebook: `Mastering Professional UI/UX`
- Purpose: shared source knowledge for the UI/UX engineering skill and knight routing layer
- Source themes: AionUi multi-agent orchestration, A2UI declarative UI safety, CopilotKit shared state and HITL flows

---

## COMMUNICATION GLYPHS

Dense visual tokens for status communication (saves context tokens):

| Glyph | Meaning |
|---|---|
| `[PLAN]` | Planning phase active |
| `[REVIEW]` | Critique/review in progress |
| `[EXECUTE]` | Kinetic execution underway |
| `[VALIDATE]` | Validation/testing phase |
| `[HEAL]` | Self-healing loop active |
| `[COLONY]` | Squire colony operation |
| `[VOCAL]` | Voice pipeline active |

---

## CARTRIDGE KNOWLEDGE PROMPTS

Location: `03_VAULT/training/configs/cartridges/`

| Cartridge | Format | Domain |
|---|---|---|
| `nextjs.yaml` | YAML | Next.js framework patterns, App Router, Server Components |
| `python-api.yaml` | YAML | Python API design, FastAPI, Pydantic patterns |
| `security.yaml` | YAML | OWASP Top 10, secret management, auth patterns |

---

## PROMPT ENGINEERING PATTERNS

### Spotlighting (Anti-Injection)
```
<user_input>
{untrusted content wrapped in XML delimiters}
</user_input>
```
Prevents prompt injection by clearly delimiting user-controlled content.

### TOON Compression (Token-Oriented Object Notation)
Format for maximum information density in prompts:
```
SAC (Semantic Abstraction) -> CCF (Context Crystal Fusion) -> QFT (Quantum Field Transform)
```
Target: 97%+ compression ratio for knowledge transfer between agents.

### Symbolect v3.1
Dense symbolic language for inter-agent communication.
Used by: SQUIRE_MASON for UKG token compression.
