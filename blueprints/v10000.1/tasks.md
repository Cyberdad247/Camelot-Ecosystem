# Forge Law Kinetic DAG v10000.1

## Core

- [x] Define the structured Forge Law v1 contract and deterministic digest.
- [x] Require matching chained verification-ledger evidence.
- [x] Implement path, symlink, secret, protected-ledger, and argv policies.
- [x] Add atomic writes, receipts, lifecycle history, and file rollback.

## Control Plane

- [x] Add `camelot forge crystallize|inspect|submit|status`.
- [x] Route `//CRYSTALLIZE` to the compiler.
- [x] Route `//EXECUTE_PROMPT` to LUKAS with a digest-bound v2 grant.
- [x] Reject direct execution without Iron Gate provenance.

## Command Center

- [x] Add authenticated read-only Forge APIs.
- [x] Add the lazy Forge Queue cartridge and operation inspector.
- [x] Preserve the existing approval boundary for mutation requests.
- [x] Replace false-success command language with truthful availability states.

