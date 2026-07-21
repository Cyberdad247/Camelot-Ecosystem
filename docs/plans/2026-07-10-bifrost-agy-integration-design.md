# Camelot-OS ↔ AGY CLI Integration Design

**Date**: 2026-07-10
**Status**: Validated via Thinktank Protocol (5 rounds)

## Objective
Provide the optimal infrastructure for merging Camelot-OS CLI with AGY CLI, with a specific focus on resolving the `/model` visibility gap and Bifrost governance mesh integration.

## Constraints & Context
- AGY's `/model` is a built-in platform command showing only the active model selected in `settings.json`. It cannot be natively modified to pull from Camelot's Bifrost.
- Bifrost has 20+ terminals across 7 routing strategies (cliproxy, sovereign, cloudbrain, etc.) that the user needs visibility into.
- Heimdall Governance currently reports `ATTENTION_REQUIRED` due to a missing/empty mesh manifest.
- AGY currently uses `~/.gemini/extensions/camelot-os/GEMINI.md` to inject context, but it is missing 17 runic commands and 30 Omega runes.

## Three-Tier Integration Architecture

After debating Extension-First, Bridge-Layer, and Native MCP approaches, the Thinktank concluded that the optimal infrastructure requires a phased three-tier implementation:

### 1. The Context Tier (Immediate Fix)
We will expand the AGY extension context injection so the agent is immediately aware of all missing runic commands and the static state of the Bifrost registry.
- **Action**: Update `GEMINI.md` to document the 24 runic commands, the top 10 Omega runes, and the static Bifrost knight-to-model roster.
- **Benefit**: Zero-code immediate visibility.

### 2. The Bridge Tier (Live CLI Integration)
We will create a lightweight bridge within the Camelot CLI to allow AGY to query live Bifrost status.
- **Action**: Fix the Heimdall mesh manifest by creating `03_VAULT/runtime_state/bifrost_router_mesh_manifest.json` with the 5 required components.
- **Action**: Add a `models` subcommand to `control_plane.camelot_cli.py`.
- **Action**: Add a `//MODELS` runic command to `runic_router.py` that invokes the subcommand.
- **Benefit**: Provides live, probeable terminal status without a massive refactor.

### 3. The Native MCP Tier (Long-Term Architecture)
To truly merge Camelot-OS and AGY without violating the LATTICE_SIGNAL sovereignty model, we will formalize Bifrost as a capability of AGY via the Model Context Protocol (MCP).
- **Action**: Build or extend an MCP server (e.g., `cognitive_mcp.py`) exposing `bifrost_list_models`, `bifrost_dispatch`, and `bifrost_status` tools.
- **Benefit**: Natively solves the `/model` visibility gap, as AGY can natively query MCP tools for models and dispatch tasks directly to specific knights.

## Implementation Plan

1. **Manifest Fix**: Generate `bifrost_router_mesh_manifest.json` to clear Heimdall governance warnings.
2. **Context Update**: Overhaul the `GEMINI.md` extension.
3. **Bridge CLI**: Implement `camelot_cli models` and the `//MODELS` rune.
4. **MCP Sidecar**: Scaffold the Bifrost MCP tool interface.
