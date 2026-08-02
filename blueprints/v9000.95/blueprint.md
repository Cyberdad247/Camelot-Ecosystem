# CAMELOT-OS v9000.95 Production Ascension Blueprint

Date: 2026-07-06
Evidence posture: grounded preflight, not remote go-live

## Evidence Classification

| Claim | Status | Evidence |
|---|---|---|
| Aaliyah WASM pill source exists locally | confirmed | `kinetic_edge/aaliyah_comms/` |
| Aaliyah pill compiles to WASI Preview 1 | confirmed | `cargo build -p aaliyah-comms --target wasm32-wasip1 --release` |
| OpenHuman/persona frontend surface exists | confirmed | `02_FORGE/generated/ukg_omega_glyph_v1000/Node_A_Frontend/src/OpenHumanAvatar.tsx`, `usePersona.ts` |
| PWA can build locally | confirmed | `npm run build` in Node_A frontend |
| KBA `/opt/camelot` install completed | blocked | Requires real Linux/KBA shell access and HITL approval |
| Vercel production deploy completed | blocked | Requires explicit deploy approval and authenticated Vercel/GitHub surface |

## Architecture

Layer 1, Glass: Vite React Node_A frontend renders the OpenHuman persona bridge, local status probes, and Aaliyah intent preview state. The current implementation is dependency-free and avoids claiming Three.js/VRM runtime until those packages are audited and installed.

Layer 2, Bifrost: `nativeBridge.ts` targets `http://127.0.0.1:4180/v1/nano-swarm/status` for local router status. Future kinematic frames should travel over the same Bifrost/SSE boundary before a VRM renderer consumes them.

Layer 3, Pill Runtime: `aaliyah-comms` is a Rust WASI Preview 1 pill. It emits a JSON draft envelope with `pending_hitl_approval` and performs no network or MTA dispatch.

Layer 4, KBA Node: Linux installation to `/opt/camelot/cartridges/pills/` remains a deployment action, not a confirmed local fact. The safe push path is compile locally, hash the `.wasm`, copy via an approved channel, then restart the target service under operator control.

## Non-Negotiable Gates

Email dispatch must remain host-mediated and HITL-gated. The WASM pill may draft, classify, and prepare intent envelopes, but it must not send mail directly.

Remote install, service restart, git push, and Vercel production deploy are destructive/external actions. They require explicit operator approval and live credentials.

## Local Build Evidence

- WASM artifact: `target/wasm32-wasip1/release/aaliyah_comms.wasm`
- SHA-256: `9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095`
- Host behavior probe: `cargo run -p aaliyah-comms -- "draft welcome campaign for new contacts"` emits `pending_hitl_approval`
- Frontend build: `npm run build` completed under `Node_A_Frontend`
- Wasmtime runtime execution: pass via `.cache\tools\wasmtime-v46.0.1\wasmtime-v46.0.1-x86_64-windows\wasmtime.exe -C cache=n`
