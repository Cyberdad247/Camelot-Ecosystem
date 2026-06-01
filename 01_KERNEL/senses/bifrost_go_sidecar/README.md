# Bifrost Go Sidecar

Lightweight Go bridge that proxies a stable transport surface to the Rust Morgana gateway.

## Endpoints

- `GET /health`
- `GET /v1/bifrost/status` -> `GET /bifrost/status`
- `POST /v1/agent/dispatch` -> `POST /agent/dispatch`

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

## Run

```powershell
cd C:\Users\vizio\CAMELOT_OS\01_KERNEL\senses\bifrost_go_sidecar
go test ./...
go run .
```

## Persist on Windows logon

```powershell
cd C:\Users\vizio\CAMELOT_OS\01_KERNEL\senses\bifrost_go_sidecar
go build -o C:\Users\vizio\CAMELOT_OS\bin\bifrost_go_sidecar.exe .
powershell -ExecutionPolicy Bypass -File .\register_sidecar_task.ps1
schtasks /Run /TN "Camelot Bifrost Go Sidecar"
```

If task creation is denied by local policy, `register_sidecar_task.ps1` falls back to a Startup-folder launcher (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\camelot-bifrost-go-sidecar.cmd`).
