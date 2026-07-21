# OpenClaude Assimilation Report

## Source

- Upstream: `https://github.com/Gitlawb/openclaude`
- Staged path: `.camelot/vault/staging/openclaude`
- Staged HEAD: `64d164d2`
- Package: `@gitlawb/openclaude`
- Version observed: `0.23.0`
- Runtime: Node.js `>=22.0.0`
- Build/test manager: Bun
- License: `SEE LICENSE FILE`

## Assimilation Pass

- Protocol: Camelot Understand-Anything adapter
- Command: `.venv/Scripts/python.exe bin/understand_anything_assimilate.py --root .camelot/vault/staging/openclaude --output-root .understand-anything/openclaude --max-files 800`
- Graph nodes: `804`
- Graph edges: `803`
- Graph artifact: `.camelot/vault/staging/openclaude/.understand-anything/openclaude/knowledge-graph.json`
- Report artifact: `.camelot/vault/staging/openclaude/.understand-anything/openclaude/CAMELOT_ASSIMILATION_REPORT.md`

## System Overview

OpenClaude is a TypeScript/Bun coding-agent CLI that overlaps with Camelot's prompt, routing, provider, local-model, MCP, and terminal-UI layers.

Primary surfaces:

- `src/commands`: slash and CLI command implementations.
- `src/components`: React/Ink terminal UI components.
- `src/services`: API, MCP, OAuth, wiki, voice, and provider service integrations.
- `src/tools`: agent tool implementations.
- `src/integrations`: provider and model metadata.
- `src/entrypoints`: CLI, MCP, SDK, and public type entrypoints.
- `src/tasks`: local, remote, workflow, and monitor task handling.
- `web`: documentation website.
- `vscode-extension`: editor extension package.

## Camelot Fit

High-value patterns to assimilate without wholesale runtime replacement:

- Provider profile bootstrap and recommendation flow.
- OpenAI-compatible provider metadata and route detection.
- Local Ollama profile ergonomics.
- MCP server/client integration patterns.
- React/Ink prompt UI conventions.
- Runtime doctor and privacy verification scripts.
- VS Code extension packaging as a secondary operator surface.

## Integration Recommendation

Use OpenClaude as a reference cartridge, not as Camelot's primary runtime.

Recommended integration path:

1. Create a read-only `openclaude` reference cartridge under Camelot docs/runtime metadata.
2. Compare OpenClaude provider/profile abstractions against Camelot `Switchboard`, `OmniRoute`, `Bifrost`, and `knight_session`.
3. Extract only stable patterns into Camelot:
   - provider-profile schema
   - runtime doctor checklist
   - model metadata normalization
   - MCP integration checklist
   - React/Ink prompt UX improvements
4. Keep secrets out of graph artifacts. `.env.example` contains placeholder secret names only; do not ingest real `.env` files.
5. Validate any imported pattern with Camelot's prompt-first local Cloudbrain route before using frontier/provider calls.

## Risk Register

- OpenClaude is a large active TypeScript/Bun project; direct vendoring would increase maintenance entropy.
- It expects Node `>=22` and Bun, while Camelot core remains Python/PowerShell-heavy.
- Provider-routing behavior overlaps with Camelot and could conflict with `Switchboard`/`OmniRoute` if installed blindly.
- The repository contains extensive provider/env documentation; treat all env values as schema examples, not credentials.
- Some workflows launch agents that can read/write files and execute commands. Keep integration behind HITL.

## Next Engineering Tasks

- Build a Camelot provider-profile comparison table: OpenClaude profile fields vs Camelot `omniroute.json` and `switchboard.py`.
- Add an optional `openclaude` reference node to future Understand-Anything graph runs.
- Evaluate whether OpenClaude's `doctor:runtime` concepts should map into `camelot doctor`.
- Prototype a non-executing `camelot openclaude plan` command before any runtime launch command.
- Do not install dependencies or execute OpenClaude agent loops until the above comparison is reviewed.

