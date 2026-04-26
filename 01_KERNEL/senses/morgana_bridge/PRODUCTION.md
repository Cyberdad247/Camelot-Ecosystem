# Morgana Bifrost Gateway Production Notes

The Morgana bridge is now the production Bifrost Gateway for the Anya Dashboard. It exposes public health endpoints and protects control endpoints when `CAMELOT_GATEWAY_TOKEN` is set.

## Public endpoints

- `GET /health`: liveness and redacted gateway configuration.
- `GET /ping`: lightweight compatibility ping.

## Protected endpoints

These require auth when `CAMELOT_GATEWAY_TOKEN` is configured:

- `GET /bifrost/status`
- `GET /openviking/map`
- `POST /pulse`
- `POST /agent/dispatch`
- `POST /modal/cloud-brain`
- `GET /ws`

HTTP auth accepts either `Authorization: Bearer <token>` or `x-camelot-token: <token>`.
Websocket auth accepts `?token=<token>`.

## Environment variables

- `BIFROST_BIND_ADDR`: bind address, default `0.0.0.0:8001`.
- `BIFROST_PUBLIC_HTTP_URL`: public HTTP origin sent to clients, default `http://127.0.0.1:8001`.
- `BIFROST_PUBLIC_WS_URL`: public websocket URL, default `ws://127.0.0.1:8001/ws`.
- `BIFROST_CORS_ORIGIN`: optional exact allowed dashboard origin. If omitted, local/dev permissive CORS is used.
- `CAMELOT_GATEWAY_TOKEN`: optional auth token. Set this for production.
- `CAMELOT_OWNER`: expected owner username, default `vizio`.
- `CAMELOT_ROOT`: Camelot repo root, default `C:\Users\vizio\CAMELOT_OS`.
- `OPENVIKING_MAP_PATH`: map file path, default `<CAMELOT_ROOT>\entiremap.md`.
- `SALTARE_GATEWAY_URL`: kinetic gateway origin, default `http://localhost:8085`.
- `MODAL_CLOUD_BRAIN_URL`: Modal cloud brain target proxied through `/modal/cloud-brain`.
- `GRADIO_URL`: optional Gradio URL reported by health.

## Local run

```powershell
cd C:\Users\vizio\CAMELOT_OS\01_KERNEL\senses\morgana_bridge
& C:\Users\vizio\.cargo\bin\cargo.exe run
```

## Production posture

For a public Vercel dashboard, deploy this gateway behind HTTPS/WSS and set `BIFROST_CORS_ORIGIN` to the Vercel domain. Do not expose local filesystem map or dispatch routes without `CAMELOT_GATEWAY_TOKEN`.
