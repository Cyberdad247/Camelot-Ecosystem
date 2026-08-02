# Camelot-OS Forge Law Architecture v10000.1

## Objective

Turn a verified R&D upgrade into an immutable, inspectable Bootstrap Prompt
Cartridge without granting an LLM direct write or service-control authority.

## Topology

1. The R&D Command Center produces `blueprint.md`, `tasks.md`,
   `verification.md`, and a structured `forge.json` contract.
2. The verification ledger records `forge_upgrade_verified` with exact source
   hashes after the declared checks pass.
3. The Forge Law compiler validates the contract, resolves its dependency DAG,
   binds the ledger evidence, and creates a content-addressed cartridge.
4. Iron Gate presents the immutable digest, target root, operation list, and
   risk before issuing a short-lived approval grant.
5. LUKAS executes typed operations through the existing harness. File writes
   are atomic, commands use argv allowlists without a shell, and failures roll
   file mutations back.

## Authority Boundaries

- Markdown is documentation and is never parsed as executable code.
- Cloud Brain can propose source bundles but cannot approve or execute them.
- `PROVENANCE_LEDGER.md` and the verification ledger are protected targets.
- Service restarts require a separate approval path and remain disabled in the
  cartridge executor.
- The PWA renders declarative cartridge evidence; it cannot manufacture state.

## Runtime Surfaces

- `control_plane.forge_law`: validation, crystallization, lifecycle, execution.
- `control_plane.runic_router`: `//CRYSTALLIZE` and `//EXECUTE_PROMPT` routing.
- `control_plane.harness`: LUKAS execution and receipt production.
- PWA Forge Queue: inspection, approval requests, status, and rollback evidence.

