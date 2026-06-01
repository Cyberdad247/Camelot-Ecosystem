# Skills And Tool Assertions Backplane

This file separates currently available Camelot capabilities from proposed
interfaces in the master bootstrap.

## Available Operational Surfaces

- `//BOOT`: existing runic command for boot intent; live boot path is `python bin/awaken.py`.
- `//FORGE <task>`: existing runic command for implementation dispatch.
- `//SWARM <task>`: existing runic command for multi-agent colony dispatch.
- `//PLAN <task>`: existing runic command for planning output.
- `//STATUS`: existing runic command for live status intent.
- `//CONTRACT [Brief]`: existing runic command for portable runtime packaging intent.
- `Omega_SYNC`: existing Omega rune for memory sync intent.
- `python -m control_plane.runic_router --list`: list current runtime runes.
- `python -m squires.colony ghost [path]`: privacy/secret scan.
- `python -m squires.colony triage [path]`: full colony triage with HITL where configured.

## Proposed Interfaces

These names may be used in plans and docs, but they are not runtime contracts
until implemented and verified in the router or tool layer.

- `codegraph_explore(symbol)`: proposed Tree-Sitter or index-backed symbol graph lookup.
- `kinetic_ast_patch(file, diff)`: proposed semantic patching interface.
- `stealth_dom_flatten(url)`: proposed browser/content extraction interface. Must not spoof identity or bypass access controls.
- `//SYNC`: conceptual alias for `Omega_SYNC`.

## Tool Rules

- Prefer existing repository tools before creating new abstractions.
- Use structured parsers and local helper APIs when they exist.
- Document unsupported tool names as future work instead of pretending they are live.
