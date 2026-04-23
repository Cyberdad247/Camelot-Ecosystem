# Skill: Swarm Protocols (PALADIN_OMEGA)
# Loaded when //SWARM, //FLEET, or //FORGE invoked

## SRDL Loop (Swarm Rapid Development Loop)

### Phase A — MAP (Broadcast)
- Oracle decomposes user request into Task DAG
- Each node typed: INTERNAL (Council) or EXTERNAL (A2A delegate)
- Fan out to parallel micro-agents (150-token budgets)

### Phase B — REDUCE (Audit)
- Sentinel audits incoming code
- 10-Line Rule enforcement per agent AND per A2A session
- Cumulative patches across delegates cannot exceed 50 net lines without HITL

### Phase C — KINETIC EXECUTION
- AST-Aware Patching via tree_sitter_phial
- All patches to Shadow Git Branch (never touch production)
- Security scan (trivy, semgrep) before merge

## Familiars Dispatch
- Formica (Ants): 15-50 parallel instances for bulk code/test writing
- Pongid (Gorilla): Heavy API integrations (AWS/Stripe/Twilio)
- Castor (Beaver): Docker/gVisor sandbox construction
- Arachne (Spider): Headless browser E2E testing
- Simian (Chaos Monkey): Entropy injection for resilience testing
- Strigiform (Owl): Workflow optimization + merge conflict resolution
- Corvus (Raven): A2A scouting + external agent discovery

## A2A Protocol
- Each agent publishes Agent Card (JSON: name, capabilities, I/O schema)
- External agents discovered via Corvus registry scan
- Opaque execution: only I/O interfaces exposed, never internal state
- Task lifecycle: Request > Accept > Execute > Artifact
