# Symbolact Dictionary for Camelot-OS v701

Generated: 2026-08-12T17:36:02.237472+00:00

`Symbolact` is the v701 operator-facing name for an action-bearing Symbolect token. In plain terms: a Symbolact is a short symbol, word, or command that carries both meaning and an expected action.

| Token | Meaning | Source |
| --- | --- | --- |
| Symbolact | Action-bearing symbolic command: a compact token that tells Camelot what to do and why. | v701 alias for Symbolect action dictionary |
| Symbolect | Camelot symbolic compression layer for logic, prompts, routing, and A2A packets. | 01_KERNEL/merlin/Engines/symbolect_transpiler/symbolect.py |
| UKG | Universal Knowledge Glyph; structured compressed memory that can survive context limits. | 01_KERNEL/merlin/Engines/ukg_runtime.py |
| TOON_v2 | Token-oriented object notation for dense agent output and persona manifests. | 01_KERNEL/protocols/knight_evolution_protocol.md |
| S_omega | Soul Router score used to select the best Knight engine for an intent. | control_plane/soul_router.py |
| V | Velocity: urgency or time pressure component in S_omega. | control_plane/soul_router.py |
| M | Magnitude: scope and complexity component in S_omega. | control_plane/soul_router.py |
| P | Privacy: sensitivity component that can force local or air-gapped routing. | control_plane/soul_router.py |
| E | Environment: engine-fit component based on the active routing matrix. | control_plane/soul_router.py |
| DKS | Dynamic Knight Swapping; keeps only a small hot pool of Knight context in RAM. | control_plane/dks_manager.py |
| Iron Gate | Human-in-the-loop and policy boundary for risky kinetic operations. | 01_KERNEL/iron_gate |
| Watchtower | Resource, process, kingdom-status, and governor monitoring surface. | 01_KERNEL/iron_gate/watchtower.py |
| Cloud Brain | NotebookLM-backed long-term memory and canonical sync surface. | control_plane/cloudbrain_sync.py |
| Ledger is Law | Every meaningful Camelot mutation must be recorded and reconcilable. | PROVENANCE_LEDGER.md |
| ASSIMILATE | Classify an external project or file into keep, compress, stage, or purge lanes. | docs/reference/LEGAL/MASTER_GLOSSARY.md |
| Nano-Knight | Small local utility worker for fast scanning, patching, compression, or verification. | 03_VAULT/Nano-Knights |
| Bio-Swarm | Domain-cartridge team mode for research, coding, security, voice, or interface work. | 01_KERNEL/agora/swarms |
| Lukas Verify | Local evidence pass: file existence, ledger status, queue status, and command output. | current v701 protocol |

## Canonical Symbolect Operators

| Operator | Meaning |
| --- | --- |
| -> | implies |
| <- | derived_from |
| == | equivalent_to |
| != | not_equivalent_to |
| && | and |
| // | or |
| >> | process_flow_to |
| << | process_flow_from |
| [?] | query |
| [!] | alert |
| [*] | insight |
| [@] | reference |
| {...} | context_block |
| <...> | variable |
| # | entity_tag |

## v701 Authoring Rule

Use Symbolacts for repeatable command meaning, not decorative language. A valid Symbolact should answer three questions: what action happens, which surface owns it, and what evidence proves it happened.
