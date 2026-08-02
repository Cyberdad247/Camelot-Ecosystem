# CAMELOT-OS v9000.95 Production Task DAG

## Phase 1: Local Pill Fabrication

- [x] Create `kinetic_edge/aaliyah_comms` Rust pill source.
- [x] Register `aaliyah-comms` in the Rust workspace.
- [x] Compile: `cargo build -p aaliyah-comms --target wasm32-wasip1 --release`.
- [x] Hash artifact: `Get-FileHash target/wasm32-wasip1/release/aaliyah_comms.wasm -Algorithm SHA256`.

## Phase 2: Frontend Persona Cartridge

- [x] Add `usePersona.ts` LERP blendshape hook.
- [x] Add `OpenHumanAvatar.tsx` dependency-free preview renderer.
- [x] Wire avatar/status panel into Node_A frontend.
- [x] Build: `npm run build` from `02_FORGE/generated/ukg_omega_glyph_v1000/Node_A_Frontend`.

## Phase 3: KBA Deployment, HITL Required

- [ ] Copy the verified `.wasm` to the KBA node only after operator approval.
- [ ] Restart `camelotd` only from an approved KBA shell.
- [ ] Confirm pill registration from the router status endpoint.

## Phase 4: Vercel Deployment, HITL Required

- [ ] Confirm the intended Vercel project and production URL.
- [ ] Run frontend build in a clean tree.
- [ ] Commit only scoped files.
- [ ] Deploy using authenticated Vercel tooling after operator approval.

## Phase 5: Crucible Acceptance

- [x] Aaliyah host draft command returns `pending_hitl_approval`.
- [x] Aaliyah WASM draft command returns `pending_hitl_approval` under Wasmtime.
- [ ] No MTA dispatch occurs without dashboard approval.
- [ ] Frontend renders on desktop and mobile.
- [ ] Bifrost status probe fails closed when router is unavailable.
