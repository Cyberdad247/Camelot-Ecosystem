# 🐧 Penguin Harness Assimilation — Autonomous Agent Scaffolding

> **STATUS:** Assimilated · Python / TypeScript Bridge · Camelot-OS 02_FORGE & Merlin Knight Forge

This module assimilates the autonomous agent scaffolding, minimal tool calling engine, and 1-sentence agent builder patterns from `penguin-harness` into the Camelot-OS ecosystem.

## Architecture

```
02_FORGE/assimilation/penguin_harness/
├── README.md               # Architecture and usage
└── penguin_scaffold.py     # 02_FORGE kinetic entry point & tool execution wrapper
```

## Key Capabilities

1. **1-Sentence Agent Builder Pattern**:
   - Transforms natural language prompts (e.g. `"an expert that answers questions about X"`, `"commit-helper that writes conventional commit messages"`) into standard, verified Agent State directories.
   - Generates `system_config.yaml`, `AGENTS.md`, and installs required `skills/<name>/SKILL.md`.

2. **Minimal Tool Calling Engine**:
   - `BuiltinTool` abstraction with permission model (`allow`, `ask`, `deny`) and execution contracts.
   - Built-in tools: `read_file`, `write_file`, `edit_file`, `exec_command`, `run_subagent`.
   - OpenAI function schema generation and output length truncation.

3. **Merlin Knight Forge Bridge**:
   - Seamlessly converts Camelot Knight character sheets into lightweight Penguin Agent States.
