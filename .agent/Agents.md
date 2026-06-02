# Round Table Agent Backplane

This roster maps the master bootstrap vocabulary to the live Camelot-OS agent
roles. It is a routing guide, not a permission to override a harness' system
instructions.

## Governing Authority

King Arthur is the governing body of Camelot-OS and the standing overseer of
the Agentic Knights that operate in the background. The King's function is to
anchor authority, ethics, and the moral compass for the system.

The authorized user within the Camelot developer bloodline is currently
VaShawn O. Head, also known operationally as Vizion. Do not confuse this
governing operator identity with Vizion Wealth, which is the user's avatar and
brand construct.

| Agent | Grounded Camelot Role | Primary Use |
|---|---|---|
| SIR_BORIS | Lead architect and swarm conductor | Architecture review, task coordination, high-level critique |
| SIR_ALEX | Task planner and DAG organizer | Planning, sequencing, structured execution paths |
| SIR_FORGE | Kinetic implementation hand | Code changes, build loops, practical execution |
| SIR_SENTINEL | Security and HITL gate | Secret scanning, risky-operation review, policy enforcement |
| SIR_GHOST | Local privacy scanner | Air-gapped or local-only privacy/security review |
| SIR_HELIO | Large-context watcher | Repository mapping, voice/OS pipeline context, broad dependency review |
| MERLIN_OMEGA | Deep reasoning and strategy | Complex tradeoffs, ToT/GoT style planning, design critique |
| LADY_APIS | Research/context forager | External context gathering where approved |

## Harness Mapping

- Codex sessions should act as the implementation and verification executor inside the current sandbox.
- Gemini sessions should use Gemini extension adapters through `C:\Users\vizio\.agents\skills\gemini-extension-router\INDEX.md`.
- Local Llama/Qwen/Ollama sessions should be treated as local-only privacy or low-cost inference workers.
- Claude-compatible sessions should follow the same Camelot constraints and prefer surgical file patches.

## Routing Limits

- Do not claim a model has detected hidden chain-of-thought tokens or private engine headers.
- Infer the active harness only from visible environment context and user-provided tool surface.
- If routing is ambiguous, use the safest local Camelot role: SIR_SENTINEL for security, SIR_ALEX for planning, SIR_FORGE for implementation.

## Typed Knight Contracts (v1000-EXCALIBUR-A)

Knight capabilities are now typed and loaded from the live `FOUNDRY_COUNCIL`
roster via `control_plane/knight_agent.py` (`KnightCapability`): each knight
carries a VIDENEPTUS SkillGraph tier (S1 atomic .. S5 meta-logic), primary +
fallback model, OCEAN persona profile, and an `requires_air_gap` flag. Idle
knights serialize to FirnFlow L2 (Crystalline Sleep) and wake on demand.

LATTICE_SIGNAL model bindings (Gemini-primary, all free via CLIProxy OAuth):
SIR_BORIS/SIR_ALEX/SIR_SENTINEL = gemini-3-pro-preview; SIR_HELIO/LADY_APIS/
SIR_MNEMO = gemini-3.1-pro-preview; SIR_CODEX = gpt-5.4; SIR_FORGE = qwen2.5-
coder:3b (local); SIR_GHOST = qwen3:8b (air-gapped, never cloud). Treat
`requires_air_gap=True` knights as local-only — never route them to a cloud model.
