# HERMES_PRIME_NEXUS Harness

## Prime-Agent API Hooks
- `POST /prime/nexus/spawn`: Allocate new multi-node scaling instance.
- `GET /prime/nexus/telemetry`: Ingest distributed node state.
- `PUT /prime/nexus/phial`: Update Phial Engine weights dynamically.

## CLI Interfaces & Tool Bindings
- **PhialEngine (executable)**: `python 01_KERNEL/titan/phials/hermes_prime_phial.py --cycle "<seed>"` — MGV loop + Ouroboros memory + Phial weight re-weighting. State persists to `03_VAULT/runtime_state/hermes_prime_phial.json`. Self-test: `--test`.
- **Cross-Agent Communication**: Bind to `runic_router.py` for direct Omega dispatch (`Omega_HermesPrime`).
- **Distributed Compute Allocation**: Connect to underlying infrastructure (Docker/Kubernetes/Bifrost) to assign task-specific hardware constraints.
- **VFS Scaffold Commands**: Tools for writing directly to Virtual File System.

## Harmony Runes
- `⚡//SYNC_VFS_WORKSPACE`
- `⚡//FORGE_HERMES_PRIME_FILES`
- `⚡//IGNITE_SELF_EVOLUTION_LOOP`
