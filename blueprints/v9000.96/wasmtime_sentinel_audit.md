# CAMELOT-OS v9000.96 Wasmtime Sentinel Audit

Date: 2026-07-07
Scope: Local Wasmtime runtime used to execute `aaliyah_comms.wasm`

## Primary-Source Findings

| Claim | Verdict | Evidence |
|---|---|---|
| Wasmtime `v46.0.1` is the latest GitHub release checked in this audit | confirmed | GitHub release page marks `v46.0.1` latest, released 2026-06-24 |
| `v46.0.1` fixes a WASI permissions advisory | confirmed | `GHSA-4ch3-9j33-3pmj`, `CVE-2026-58494` |
| Payload CVE `CVE-2026-54786` was verified against Wasmtime primary sources | rejected | No matching primary-source Wasmtime advisory found during this audit |
| Payload CVE `CVE-2026-24116` was verified against Wasmtime primary sources | rejected | No matching primary-source Wasmtime advisory found during this audit |
| Payload CVE `CVE-2025-64345` was verified against Wasmtime primary sources | rejected | No matching primary-source Wasmtime advisory found during this audit |

## Local Runtime Evidence

- Runtime: `.cache\tools\wasmtime-v46.0.1\wasmtime-v46.0.1-x86_64-windows\wasmtime.exe`
- Version output: `wasmtime 46.0.1 (823d1b8f2 2026-06-24)`
- Release zip SHA-256: `99F038066B16CB3AAF63C1D282A9D7BA7BEFAFBADF7AA8827CC4C712D96BC31A`
- Aaliyah WASM SHA-256: `9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095`
- Execution command: `.cache\tools\wasmtime-v46.0.1\wasmtime-v46.0.1-x86_64-windows\wasmtime.exe -C cache=n target\wasm32-wasip1\release\aaliyah_comms.wasm "draft welcome campaign for new contacts"`
- Execution result: `pending_hitl_approval`

## Deployment Gate

Remote KBA deployment remains blocked until the KBA node reports Wasmtime `46.0.1` or newer and the deployed `aaliyah_comms.wasm` hash matches the local SHA-256 above.
