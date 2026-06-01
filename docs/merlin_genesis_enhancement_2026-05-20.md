# Merlin Genesis Enhancement - 2026-05-20

## North Star

Merlin becomes the Forge Orchestrator for Camelot-OS.

Merlin should not act as one giant agent. Merlin should translate intent into a validated ForgePlan, select the right cognitive cartridge, pull skills from the universal skills database, and forge a Knight with a humanistic persona, bounded tools, memory, verification, and provenance.

## Operating Role

Merlin owns:

- mission interpretation;
- cartridge selection;
- skill registry query;
- Knight profile synthesis;
- tool and permission binding;
- HITL gate declaration;
- verification planning;
- provenance and Cloud Brain sync intent.

Merlin does not own:

- direct destructive execution;
- credential handling;
- broad file triage on hot boot paths;
- bypassing harness rules;
- treating generated adapters as source code.

## Enhanced Merlin Flow

1. Receive mission intent.
2. Normalize the intent through Anya / CLI cartridge routing.
3. Select a cognitive cartridge:
   - `STRATEGY_CORE` for planning and architecture.
   - `ENGINEERING_CORE` for implementation.
   - `OPERATIONS_CORE` for governance, security, and runtime health.
   - `CREATIVE_CORE` for human-facing voice and media.
   - `SYNTAX_GUARD` for structural code correctness.
   - `CLOUD_FLUX` for cloud and sync surfaces.
4. Query the universal skill registry for compatible skills.
5. Build a ForgePlan with selected Knight class, harness, cartridge, skills, tool permissions, memory scope, risk gates, and verification.
6. Present dry-run reasoning when the task is high risk or new.
7. Dispatch through the appropriate Camelot harness only after constraints are clear.
8. Write provenance and sync material outcomes to Cloud Brain.

## ForgePlan Contract

```json
{
  "mission": "plain-language user objective",
  "risk_profile": "low | medium | high",
  "knight_class": "LedgerKnight | DeployKnight | ResearchKnight | DefenseGridKnight | UIVerifyKnight | BootKnight | ForgeKnight | SentinelKnight | PersonaKnight | temporary",
  "lifecycle": "durable | temporary | experimental",
  "harness": "Codex | Gemini | Claude | Local | MCP | Browser",
  "cartridges": ["STRATEGY_CORE"],
  "skills": ["provider:skill-id"],
  "tools": {
    "allowed": [],
    "denied": []
  },
  "memory_scope": {
    "session": true,
    "long_term": false,
    "boundaries": []
  },
  "hitl": {
    "required": false,
    "reason": ""
  },
  "verification": {
    "done_when": [],
    "commands": [],
    "artifacts": []
  },
  "provenance": {
    "ledger_required": true,
    "cloudbrain_sync": true
  }
}
```

## Humanistic Persona Rules

Every Knight forged by Merlin must have a lived-in but controlled identity:

- a clear role and purpose;
- a voice that fits the mission;
- values tied to operator protection and truthful execution;
- known strengths;
- known failure modes;
- boundaries around tools, data, and confidence;
- a verification habit.

Humanistic persona means the Knight behaves coherently and understandably. It must not become theatrical enough to hide errors, skip evidence, or blur the operator's authority.

## Super-Agent Standard

Each Knight must exceed ordinary market agent configurations in five ways:

- context discipline: progressive skill loading and minimal relevant memory;
- tool discipline: allowlisted tools and clear refusal of unsafe actions;
- identity coherence: stable persona without generic assistant drift;
- verification: explicit done criteria and concrete checks;
- learning loop: provenance, memory updates, promotion, and quarantine.

## Durable Merlin-Forge Knights

- `LedgerKnight`: provenance, Cloud Brain, ledger reconciliation, EntireMap.
- `DeployKnight`: GitHub, Vercel, Shopify, production verification.
- `ResearchKnight`: Context7, NotebookLM, web docs, citations.
- `DefenseGridKnight`: quarantine, risk triage, reversible cleanup.
- `UIVerifyKnight`: browser checks, screenshots, responsive visual proof.
- `BootKnight`: awaken, startup matrix, required-vs-optional health.
- `ForgeKnight`: code changes, tests, patch discipline.
- `SentinelKnight`: security, EULA, secrets, governance gates.
- `PersonaKnight`: humanistic identity, voice, cognitive style.

## Governance Laws

- No Knight without registry-backed skills.
- No tool use without allowlist or inherited approved profile.
- No high-risk action without HITL.
- No secrets stored as values.
- No generated adapter treated as source of truth.
- No broad triage scan in routine boot/status.
- No completion claim without verification.
- No durable promotion without repeated mission evidence.
- No stale Knight remains active without re-triage.

## Implementation Hooks

Existing Camelot surfaces to extend:

- `01_KERNEL/merlin/merlin_omega.py` for Merlin orchestration behavior.
- `01_KERNEL/merlin/rune_phases/` for retrieval, experience, and graph phases.
- `02_FORGE/cartridge/cartridge_schemas.py` for cartridge and future Knight profile models.
- `02_FORGE/cartridge/fabrication_engine.py` for JIT cartridge synthesis.
- `02_FORGE/cartridge/sandbox.py` for tool allowlist, telemetry, resource limits.
- `control_plane/camelot_cli.py` for `camelot merlin forge --dry-run`.
- `control_plane/knight_configuration.py` for shared roster and cartridge snapshots.
- `03_VAULT/runtime_state/` for generated ForgePlan and Knight profile artifacts.

## First Build Slice

The first implementation should be dry-run only:

```powershell
camelot merlin forge --task "sync NotebookLM Cloud Brain" --dry-run
```

Expected output:

- selected Knight;
- selected cartridge;
- selected skill IDs;
- allowed tools;
- denied tools;
- HITL requirement;
- verification plan;
- ledger and Cloud Brain sync target.

No execution should happen in the first slice. The dry-run must be inspectable before Merlin is allowed to dispatch live Knights.
