# Package Ownership Map - 2026-07-01

Scope: `C:\Users\vizio\CAMELOT_OS`

Purpose: classify package and crate surfaces before any lockfile consolidation. This is analysis-only. No lockfiles should be deleted or moved until every owner and verification command is confirmed.

## Summary

Tracked package surfaces found:

| Ecosystem | Primary manifests | Lockfiles / sums | Initial risk |
|---|---:|---:|---|
| Rust | 27 `Cargo.toml` | 19 `Cargo.lock` | High fragmentation; many independent crates and generated nodes. |
| Node | 22 `package.json` | 11 `package-lock.json` | High fragmentation; multiple apps and possible duplicate prototypes. |
| Go | 12 `go.mod` | 7 `go.sum` | Medium fragmentation; mostly sidecars/runners. |
| Python | 3 `pyproject.toml` | varies | Low/medium; root project plus embedded references. |

## Active Runtime Candidates

| Surface | Evidence | Proposed verification |
|---|---|---|
| `.` | Root `Cargo.toml`, `Cargo.lock`, `package.json`, `package-lock.json`, `pyproject.toml`. | Root tests plus targeted Camelot triage. |
| `control_plane/rtk` | Rust Token Killer crate. | `cargo check` from crate/workspace. |
| `control_plane/go_router` | Go router module. | `go test ./...` from module. |
| `control_plane/runners/go` | Go runner module. | `go test ./...` from module. |
| `control_plane/runners/rust` | Rust runner crate. | `cargo check` from crate. |
| `01_KERNEL/core/aegis_shield` | Required rapid triage compile target. | Already covered by `rust-kernel-compile`. |
| `01_KERNEL/reasoning/ouroboros_engine` | Required rapid triage compile target. | Already covered by `rust-kernel-compile`. |
| `01_KERNEL/senses/morgana_bridge` | Kernel bridge crate. | `cargo check` from crate. |
| `04_KINETIC/squires_rs` | Native Squire scanner path. | `cargo build --release` from crate. |
| `kinetic_edge/swarm_spawner` | Bio-Swarm binary source. | `cargo test` / `cargo build --release` from crate. |

## Forge/App Candidates

| Surface | Package files | Initial classification |
|---|---|---|
| `02_FORGE` | `package.json`, `package-lock.json` | Active forge workspace candidate. |
| `02_FORGE/apps/anya-lyte` | `package.json` | App package; needs workspace map. |
| `02_FORGE/apps/omni-eye-dashboard` | `package.json` | Dashboard app; likely active. |
| `02_FORGE/KINETIC_ARMORY/edge-router` | `package.json` | Router package; likely active. |
| `02_FORGE/KINETIC_ARMORY/omnivoice-router` | `package.json`, `package-lock.json` | Router package; likely active but lockfile ownership needed. |
| `02_FORGE/packages/anya-domain` | `package.json` | Library package. |
| `02_FORGE/packages/anya-lyte` | `package.json` | Potential duplicate of app naming; needs owner check. |
| `02_FORGE/packages/pocket-squire` | `package.json`, `package-lock.json` | Package candidate. |
| `02_FORGE/pocket_squire` | `package.json`, `package-lock.json` | Possible duplicate/prototype of `packages/pocket-squire`; do not merge without import check. |
| `02_FORGE/PORTAL_CORE` | `package.json`, `package-lock.json` | Portal workspace candidate. |
| `02_FORGE/PORTAL_CORE/Anya_Dashboard` | `package.json`, `package-lock.json` | Dashboard package; likely active. |
| `02_FORGE/PORTAL_CORE/web` | `package.json`, `package-lock.json` | Web package; needs owner check. |
| `02_FORGE/holotable` | `package.json`, `package-lock.json` | App/prototype candidate. |
| `apps/bifrost` | `package.json`, `package-lock.json` | Active app candidate. |

## Generated Or Prototype Candidates

| Surface | Package files | Rule |
|---|---|---|
| `02_FORGE/generated/ukg_omega_glyph_v1000/Node_A_Frontend` | `package.json`, `package-lock.json` | Generated lane; exclude from default scans. |
| `02_FORGE/generated/ukg_omega_glyph_v1000/Node_B_Bifrost` | `Cargo.toml`, `Cargo.lock` | Generated lane; exclude from default scans. |
| `02_FORGE/generated/ukg_omega_glyph_v1000/Node_C_Omni_Router` | `go.mod`, `go.sum` | Generated lane; exclude from default scans. |
| `02_FORGE/generated/ukg_omega_glyph_v1000/Node_D_MicroVM` | `Cargo.toml`, `Cargo.lock` | Generated lane; exclude from default scans. |
| `camelot-v1000-test/cosmic_core` | `Cargo.toml`, `Cargo.lock` | Test/prototype lane. |

## Vendored Or Reference Candidates

| Surface | Package files | Rule |
|---|---|---|
| `03_VAULT/LLM-Apps-Ref/Advanced-Agents/agent_teams/ai_travel_planner_agent_team/backend` | `pyproject.toml` | Reference; exclude from default runtime scans. |
| `03_VAULT/LLM-Apps-Ref/Advanced-Agents/agent_teams/ai_travel_planner_agent_team/client` | `package.json` | Reference; exclude from default runtime scans. |
| `03_VAULT/LLM-Apps-Ref/Advanced-Agents/ai_news_and_podcast_agents/web` | `package.json` | Reference; exclude from default runtime scans. |
| `03_VAULT/training/configs/kinetic_edge/mcp_server` | `Cargo.toml`, `Cargo.lock` | Training/config reference; exclude unless target task names it. |

## Kernel And Edge Supporting Modules

| Surface | Package files | Initial classification |
|---|---|---|
| `01_KERNEL/agora/fleet` | `go.mod`, `go.sum` | Kernel support; verify before cleanup. |
| `01_KERNEL/agora/swarms/hivemind` | `go.mod` | Kernel support; missing `go.sum` may be valid if no external deps. |
| `01_KERNEL/EXCALIBUR/BRIDGE/GENKIT` | `package.json` | Bridge package. |
| `01_KERNEL/EXCALIBUR/config/registry` | `package.json` | Config package. |
| `01_KERNEL/EXCALIBUR/kernel_api_bridge` | `Cargo.toml`, `Cargo.lock` | Kernel bridge. |
| `01_KERNEL/forge/nano_forge/extension` | `package.json` | Extension package. |
| `01_KERNEL/mesh/node_c` | `go.mod`, `go.sum` | Mesh node module. |
| `01_KERNEL/opensre` | `Cargo.toml` | OpenSRE crate candidate. |
| `01_KERNEL/senses/bifrost_go_sidecar` | `go.mod` | Sidecar module. |
| `01_KERNEL/senses/vizion-telemetry` | `go.mod`, `go.sum` | Telemetry module. |
| `02_FORGE/cartridge/rustclaw` | `Cargo.toml`, `Cargo.lock` | Cartridge crate. |
| `02_FORGE/excalibur-dev` | `Cargo.toml`, `Cargo.lock`, nested crate manifests, orchestrator `pyproject.toml` | Workspace candidate; do not split without Cargo workspace check. |
| `02_FORGE/kinetic/cribo` | `Cargo.toml`, `Cargo.lock` | Kinetic crate. |
| `02_FORGE/kinetic/hephaestus` | `Cargo.toml`, `Cargo.lock` | Kinetic crate. |
| `02_FORGE/kinetic/rotel` | `Cargo.toml`, `Cargo.lock` | Kinetic crate. |
| `02_FORGE/kinetic_sovereign` | `go.mod`, `go.sum` | Kinetic Go module. |
| `03_VAULT/Nano-Knights` | `package.json` | Vault package; needs active/runtime check. |
| `04_KINETIC/cmd/runic_router` | `go.mod`, `go.sum` | Runic router module. |
| `04_KINETIC/multivoice` | `go.mod` | Voice module. |
| `kinetic_edge/camelot_edge` | `Cargo.toml` | Edge crate. |
| `kinetic_edge/pqcrypto` | `Cargo.toml`, `Cargo.lock` | Edge crypto crate. |
| `kinetic_edge/rotel` | `Cargo.toml`, `Cargo.lock` | Edge crate. |
| `kinetic_edge/saltare` | `go.mod`, `go.sum` | Edge Go module. |

## Cleanup Rule

- A lockfile is not duplicate merely because its basename repeats.
- A lockfile becomes a cleanup candidate only when its parent package is classified as generated, vendored reference, or archived prototype and no live command imports it.
- Package cleanup must be verified by targeted tests before and after each move/delete proposal.
