# CAMELOT-OS v9000.95 Verification Gates

## Commands

```powershell
cargo build -p aaliyah-comms --target wasm32-wasip1 --release
Get-FileHash target\wasm32-wasip1\release\aaliyah_comms.wasm -Algorithm SHA256
cd 02_FORGE\generated\ukg_omega_glyph_v1000\Node_A_Frontend
npm run build
```

## Gate Matrix

| Gate | Command | Passing Evidence |
|---|---|---|
| WASM compile | `cargo build -p aaliyah-comms --target wasm32-wasip1 --release` | `target/wasm32-wasip1/release/aaliyah_comms.wasm` exists |
| Host behavior | `cargo run -p aaliyah-comms -- "draft welcome campaign for new contacts"` | JSON includes `pending_hitl_approval` |
| WASM behavior | `.cache\tools\wasmtime-v46.0.1\wasmtime-v46.0.1-x86_64-windows\wasmtime.exe -C cache=n target\wasm32-wasip1\release\aaliyah_comms.wasm "draft welcome campaign for new contacts"` | JSON includes `pending_hitl_approval` |
| Frontend type/build | `npm run build` | Vite build exits 0 |
| Router fail-closed | click status probe with router offline | UI records fallback message, no crash |
| KBA install | remote shell verification | `.wasm` hash matches local artifact |
| Vercel deploy | Vercel deployment URL | production build is reachable and matches commit |

## Blockers

- Native Windows may not have `wasm32-wasip1` installed. Use `rustup target add wasm32-wasip1` if the compile fails with missing `core` or `std`.
- Wasmtime v46.0.1 is installed locally under `.cache\tools`; use `-C cache=n` in this sandbox to avoid denied writes to the default AppData cache.
- KBA and Vercel actions are intentionally blocked until explicit operator approval is given for remote mutation.

## Current Evidence

- WASM compile: pass.
- Artifact hash: `9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095`.
- Host behavior: pass; output status is `pending_hitl_approval`.
- Frontend build: pass; generated Vite bundle under `dist/`.
- Wasmtime version: `wasmtime 46.0.1 (823d1b8f2 2026-06-24)`.
- WASM runtime behavior: pass; output status is `pending_hitl_approval`.
