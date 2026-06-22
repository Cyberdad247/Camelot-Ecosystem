# Global Boot Command Audit

## Source Of Truth

`awaken` is the only global startup command for Camelot-OS. `//BOOT` routes to
that command and `python bin/awaken.py` is the repo-local fallback when shell
shims are blocked.

## Consolidated Startup Chain

The boot contract now lives in `control_plane/boot_sequence.py` and includes:

- core engines: CLIProxyAPI, Defense Grid, Kinetic Edge, Morgana, Bifrost
- local and optional engines: OmniVoice, Kitten TTS, Sir Octavian, Local LT
  Memory, Clawdbot, Sir Pi, Edge PWA
- routing and orchestration: OmniRoute on `:20128`, Hermes OmniRoute assignment,
  Knight Config Sync, Codex Integration, Nano Swarm Runtime
- memory/cloud surfaces: Cloud Brain Auth, Cloud Brain RPC, Warp workflow sync

## Hermes OmniRoute Contract

Hermes is assigned as the boot-time orchestration system through the
`Hermes OmniRoute` phase. The phase writes:

`03_VAULT/runtime_state/hermes_omniroute_orchestrator_latest.json`

That artifact records:

- canonical command: `awaken`
- rune alias: `//BOOT`
- orchestrator: `sir_hermes`
- endpoint: `http://127.0.0.1:20128/v1`
- active zero-cost engines from `omniroute.json`
- free terminal lanes from the Switchboard

If the external OmniRoute binary is not installed at `~/.omniroute`, `awaken`
falls back to the repo-local generated `Node_C_Omni_Router` binary on the same
port. The fallback binary is built from
`02_FORGE/generated/ukg_omega_glyph_v1000/Node_C_Omni_Router`. If Hermes is
missing or no zero-cost engines are configured, the assignment phase warns and
points at the runtime artifact.
