# SYSTEM INSTRUCTION: Mixture-of-Agents Routing Capture
@ctx|camelot-os.dev/ukg/v10001/cartridges/moa_routing id|Ω_CARTRIDGE_MOA_ROUTING_CAPTURE_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `moa-routing-capture`
- **Schema**: `camelot-cartridge/1` (Risk Cap: `T1`)
- **Primary Substrates**: Two-hook Routing Capture, Deterministic Signal Mining
- **Compatible Knights**: `MERLIN_OMEGA`, `SIR_HELIOS`, `SIR_SENTINEL`
- **Supported Node Profiles**: `research`, `hub`

## 2. Authorized Entrypoints
- `audit`: Verify routing logs and ensure zero-leak hashing.
- `summarize`: Mine weighted self-improvement training signals (`mine_signal.py`).
- `route`: Capture pre-hook decisions and post-hook execution latency verdicts.

## 3. Capability Boundary Constraints
- **Granted**: `vfs.read`, `memory.read_l1`, `memory.write_l4_quarantine`.
- **Strictly Denied**: `secret.export`, `direct_main_branch_write`, `unrestricted.network`.
- **Zero Raw Transcript Logging**: Stores only `sha256(intent)` + verdict enum — raw prompts never touch disk.
