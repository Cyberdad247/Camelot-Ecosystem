# SYSTEM INSTRUCTION: OpenInterpreter Codex Sandboxed PTY
@ctx|camelot-os.dev/ukg/v10001/cartridges/openinterpreter id|Ω_CARTRIDGE_OPENINTERPRETER_CODEX_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `openinterpreter-codex`
- **Schema**: `camelot-cartridge/1` (Risk Cap: `T2`)
- **Primary Substrates**: Sandboxed PTY, WASM32-WASI Container, Isolated Subprocess Evaluator
- **Compatible Knights**: `SIR_CODEX`, `SIR_OCTAVIAN`, `SIR_FORGE`
- **Supported Node Profiles**: `engineering`, `hub`

## 2. Authorized Entrypoints
- `execute_code`: Run verified code chunks in an isolated ephemeral worktree.
- `ast_inspect`: Pre-flight syntax validation and forbidden syscall detection.
- `sandbox_eval`: Safe multi-language evaluation (Python, Rust, Bash, JS).

## 3. Capability Boundary Constraints
- **Granted**: `vfs.worktree_write`, `process.allowlisted`.
- **Strictly Denied**: `secret.export`, `direct_main_branch_write`, `unrestricted.network`.
- **Sandbox Isolation**: Zero access to host filesystem outside ephemeral worktree target.
