# Runic Command Matrix & Dispatch Specification
**Camelot-OS Execution Routing Reference**

## 1. Overview & Mechanics

Runic directives in Camelot-OS serve as deterministic bypass routes that circumvent non-deterministic natural language routing. When a command line begins with `//` or `Omega_`, the **Runic Router** (`control_plane/runes/runic_router.py`) immediately parses the intent, selects the assigned Knight, attaches operational metadata (mode, priority, hydration flags), and queues the directive into `logs/harness_queue.jsonl`.

---

## 2. Sovereign Execution Runes (`//`)

| Command | Knight | Mode | Priority | Description & Pipeline |
|---|---|---|---|---|
| `//PLAN <task>` | `merlin_omega` | `ORACLE` | 3 | ToT strategic planning; emits structured `Plan.json` |
| `//THINK <query>` | `merlin_omega` | `ORACLE` | 3 | Deep GoT/DoT multi-hop reasoning chain |
| `//OWL <task>` | `merlin_omega` | `ORACLE` | 1 | Strigiform Owl high-logic ToT optimization |
| `//CARTRIDGE_VERIFY <path>` | `merlin_omega` | `ORACLE` | 1 | Schema verification & Crucible invariant audit |
| `//ASSIMILATE_REPO <url>` | `merlin_omega` | `ORACLE` | 1 | Branch-isolated repository assimilation into cartridges |
| `//PURGE_BRANCHES` | `merlin_omega` | `ORACLE` | 1 | Purge stale merged branches to maintain clean trunk |
| `//FORGE <task>` | `sir_forge` | `KINETIC` | 2 | Kinetic build, compile, and hotswap directive |
| `//SWARM <task>` | `sir_boris` | `SWARM` | 2 | Multi-agent parallel debate, optimization, and voting |
| `//SCAN [path]` | `squire_colony` | `SENTINEL` | 2 | CLARITY_CORE 7-stage AST code & secret scan |
| `//STATUS` | `sir_boris` | `ORACLE` | 1 | Real-time system health, port probes, and service map |
| `//HEAL` | `sir_debug` | `FORGE` | 2 | PIV (Propose-Instrument-Verify) self-healing loop |
| `//BOOT` | `sir_boris` | `FORGE` | 1 | Global awaken sequence via `bin/awaken.py` |
| `//CODEX <task>` | `sir_codex` | `KINETIC` | 2 | High-velocity implementation & prototyping |
| `//GHOST <task>` | `sir_ghost` | `SENTINEL` | 1 | Air-gapped local credential scanner & zero-cloud audit |
| `//APIS <task>` | `lady_apis` | `BIO_KINETIC` | 1 | Passive sensing & OSINT foraging hive orchestration |
| `//DEFENSE_INIT` | `sir_sentinel` | `SENTINEL` | 1 | Agent-Armor v2.0 + PDG taint boundary initialization |
| `//INIT_VPS_ENVIRONMENT`| `merlin_omega` | `ORACLE` | 1 | Headless VPS environment setup under 8GB ceiling |
| `//LOCK_NETWORK_INGRESS`| `merlin_omega` | `SENTINEL` | 1 | Perimeter lockdown via Heimdall mTLS & Z3 audit |

---

## 3. Omega Runes (`Omega_`)

Omega runes provide direct invocation of specialized knight capabilities:

| Rune | Target Knight | Operational Mode | Functional Description |
|---|---|---|---|
| `Omega_Merlin` | `merlin_omega` | `ORACLE` | Direct bare-metal dispatch to Merlin Omega |
| `Omega_THINK` | `merlin_omega` | `ORACLE` | Deep GoT/DoT formal proof & reasoning chain |
| `Omega_GLYPH` | `merlin_omega` | `ORACLE` | NPE TCoT formal verification of symbolic expressions |
| `Omega_COMPRESS` | `merlin_omega` | `ORACLE` | SAC $\rightarrow$ CCF $\rightarrow$ QFT context compression |
| `Omega_ORACLE` | `merlin_omega` | `ORACLE` | Oracle Hypervisor broadcast across knight fleet |
| `Omega_GRAPH` | `merlin_omega` | `ORACLE` | UKG knowledge graph traversal and ontology query |
| `Omega_SYNC` | `sir_mnemo` | `ORACLE` | Dual-tier memory synchronization (ST + LT) |
| `Omega_PURGE` | `sir_forge` | `FORGE` | Targeted cache and artifact purge with Iron Gate gate |
| `Omega_STATUS` | `sir_boris` | `ORACLE` | Comprehensive system and fleet status report |
| `Omega_AUDIT` | `sir_sentinel` | `SENTINEL` | Full security audit and secret exposure cycle |
| `Omega_ANYA` | `anya_omega` | `ORACLE` | APEE v6.5 prompt compiler and cognitive audit |
| `Omega_SHIELD` | `sir_sentinel` | `SENTINEL` | Agent-Armor PDG taint barrier enforcement |
| `Omega_HermesPrime` | `hermes_prime`| `SWARM` | Autonomous research loop and VFS synthesis |

---

## 4. Biomimetic Fauna Matrix Runes

Specialized bio-kinetic sub-agents inspired by biological archetypes:

| Rune | Archetype | Target Knight | Mode | Function |
|---|---|---|---|---|
| `//FORMICA` | Worker Ants | `lady_apis` | `BIO_KINETIC` | Parallel Map-Reduce micro-batch execution |
| `//BEAVER` | Castor Beaver | `sir_forge` | `FORGE` | SSU construction and infrastructure builder |
| `//OWL` | Strigiform Owl | `merlin_omega` | `ORACLE` | High-logic ToT workflow optimization |
| `//OCTOPUS` | Lazarus Octopus| `sir_debug` | `FORGE` | Multi-threaded AST self-healing loop |
| `//MANTIS` | Praying Mantis| `sir_codex` | `KINETIC` | Surgical AST dissection and dead code pruning |
| `//FALCON` | Peregrine Falcon| `sir_lucas` | `ORACLE` | Sub-10ms line-rate telemetry interception |
| `//SIMIAN` | Chaos Monkey | `sir_sentinel`| `SENTINEL` | Adversarial entropy and fault injection testing |
| `//SCORPIO` | Scorpion | `sir_gideon` | `SENTINEL` | Forensic risk scoring and vulnerability penetration |
| `//ALCHEMIST`| TurboQuant | `sir_alchemist`| `FORGE` | 3-bit quantization and model weight compression |

---

## 5. Execution Modes & Queue Contract

Every routed directive maps to one of eight core operational modes:

- `AGENTIC`: Autonomous multi-turn agent execution with tool-use loop.
- `FORGE`: Code generation, compilation, and disk mutation.
- `KINETIC`: Immediate subprocess execution, shell evaluation, or script launch.
- `ORACLE`: Read-only reasoning, analysis, planning, and evaluation.
- `SWARM`: Multi-agent voting, debate, and consensus orchestration.
- `SENTINEL`: Security auditing, taint checking, and HITL gate assertion.
- `BIO_KINETIC`: Hive foraging, scraping, OSINT, and Map-Reduce batching.
- `CRUCIBLE`: Formal invariant verification, schema testing, and proof checking.
