# 🤖 Assimilation Engine — Camelot-OS 02_FORGE

> **STATUS:** Active · Python

The Assimilation module integrates external frameworks, autonomous agent architectures, and specialized runtimes into CAMELOT-OS.

## Modules

### 1. Voice Assistant Omega
A Python-based voice interaction system with gVisor sandboxing for secure execution. Integrated with the CAMELOT-OS voice pipeline.

- Directory: `02_FORGE/assimilation/voice_assistant_omega/`
- Entry Point: `main.py`

### 2. Penguin Harness Scaffolding
Assimilated autonomous agent patterns from `penguin-harness`:
- **1-Sentence Agent Builder Pattern**: Rapid agent generation (`system_config.yaml`, `AGENTS.md`, `skills/`).
- **Minimal Tool Calling Engine**: Standard `BuiltinTool` execution contract and safe file/command tools.
- **Merlin Knight Adapter**: Conversion between Merlin character sheets and Penguin Agent States.

- Directory: `02_FORGE/assimilation/penguin_harness/`
- Entry Point: `penguin_scaffold.py`
- Core Engine: `.agents/skills/merlin-knight-forge/penguin_builder.py`
