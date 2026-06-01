# Local Environment Backplane

This file records operational facts and defaults for Camelot-OS agent sessions.
It is a shared context contract, not a claim that every harness can enforce the
same sandbox, network, or timing behavior.

## Runtime Boundary

- Workspace root: `C:\Users\vizio\CAMELOT_OS`
- Host profile: Windows workstation with strict resource pressure awareness.
- Memory posture: assume an 8 GB RAM ceiling unless a live probe proves more is available.
- Shell posture: prefer PowerShell-native commands on Windows.
- Python posture: prefer the repository virtual environment when present.

## Workspace Paths

- Primary repo: `C:\Users\vizio\CAMELOT_OS`
- Proposed shadow worktree path: `.shadow_forge_worktree/`
- Runtime state path: `03_VAULT/runtime_state/`
- Training/config path: `03_VAULT/training/configs/`
- Router entrypoint: `control_plane/runic_router.py`

## Network And Sandboxing

- Follow the active harness approval and sandbox rules before network access.
- Do not assume general outbound egress is available.
- Use approved local tools and documented Camelot commands before inventing a new path.
- Do not bypass security prompts, HITL gates, or credential handling rules.

## Timing Defaults

- Use short first probes for boot/debug work.
- Treat long-running tasks as suspect until their process, port, and log evidence is clear.
- Prefer fail-fast diagnostics before broad source inspection when the user names a live command.
