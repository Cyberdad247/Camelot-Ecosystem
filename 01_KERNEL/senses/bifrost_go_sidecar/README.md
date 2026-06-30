# Bifrost Go Sidecar

Lightweight Go bridge that proxies a stable transport surface to the Rust Morgana gateway.

## Endpoints

- `GET /health`
- `GET /v1/bifrost/status` -> `GET /bifrost/status`
- `POST /v1/agent/dispatch` -> `POST /agent/dispatch`

`GET /health` includes a `toon` object when the compiled TOON evidence file is
available. Proxied upstream requests then include these compact envelope
headers:

- `x-camelot-toon-spec`
- `x-camelot-toon-evidence`
- `x-camelot-toon-sha256`
- `x-camelot-toon-bytes`
- `x-camelot-toon-reduction-pct`

## Auth behavior

- Accepts inbound `Authorization`, `x-camelot-token`, or `x-bifrost-token`.
- Normalizes forwarded auth to:
  - `Authorization: Bearer <token>`
  - `x-camelot-token: <token>`
- By default, missing inbound token returns `401`.
- Optional fallback to `CAMELOT_GATEWAY_TOKEN` is available only when `BIFROST_SIDECAR_ALLOW_ENV_TOKEN_FALLBACK=true`.

## Config

- `BIFROST_SIDECAR_BIND_ADDR` (default `127.0.0.1:8011`)
- `BIFROST_SIDECAR_UPSTREAM_URL` (default `http://127.0.0.1:8001`)
- `BIFROST_SIDECAR_TIMEOUT_MS` (default `10000`)
- `CAMELOT_GATEWAY_TOKEN` (optional fallback token for upstream auth)
- `BIFROST_SIDECAR_ALLOW_ENV_TOKEN_FALLBACK` (default `false`)
- `BIFROST_TOON_EVIDENCE_PATH` (default `03_VAULT/runtime_state/camelot_compiled.toon.evidence.json`, resolved from the repo root when possible)

## Run

```powershell
cd C:\Users\vizio\CAMELOT_OS\01_KERNEL\senses\bifrost_go_sidecar
go test ./...
go run .
```

If the default Go build cache is ACL-blocked on Windows, keep the cache inside
the repo for the current shell:

```powershell
$env:GOCACHE='C:\Users\vizio\CAMELOT_OS\data\go-build'
$env:GOTMPDIR='C:\Users\vizio\CAMELOT_OS\data'
go test ./...
```

## Persist on Windows logon

```powershell
cd C:\Users\vizio\CAMELOT_OS\01_KERNEL\senses\bifrost_go_sidecar
go build -o C:\Users\vizio\CAMELOT_OS\bin\bifrost_go_sidecar.exe .
powershell -ExecutionPolicy Bypass -File .\register_sidecar_task.ps1
schtasks /Run /TN "Camelot Bifrost Go Sidecar"
```

If task creation is denied by local policy, `register_sidecar_task.ps1` falls back to a Startup-folder launcher (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\camelot-bifrost-go-sidecar.cmd`).
