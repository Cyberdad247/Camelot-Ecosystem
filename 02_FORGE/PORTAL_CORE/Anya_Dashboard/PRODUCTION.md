# Anya Dashboard Production Notes

## Required runtime services

The dashboard is a Vite static app. Live behavior comes from external services configured with `VITE_*` environment variables at build time.

- `VITE_BIFROST_HTTP_URL`: Morgana/Bifrost HTTP origin, for example `http://127.0.0.1:8001` locally or a public HTTPS bridge in cloud production.
- `VITE_BIFROST_WS_URL`: Morgana/Bifrost websocket URL, for example `ws://127.0.0.1:8001/ws` locally or `wss://.../ws` in cloud production.
- `VITE_BIFROST_TOKEN`: Optional gateway token for local/private deployments. This is browser-visible and should be replaced by backend-issued session auth for public deployments.
- `VITE_GRADIO_URL`: Gradio sandbox URL embedded by OpenViking.
- `VITE_CLOUD_BRAIN_URL`: Cloud brain endpoint. By default this routes through Bifrost at `/modal/cloud-brain`.
- `VITE_SALTARE_ROUTE_URL`: Saltare semantic gateway route endpoint.
- `VITE_ROTEL_STREAM_URL`: Rotel telemetry event stream endpoint.
- `VITE_KINETIC_TOKEN`: Shared local kinetic token. For public production, do not expose long-lived secrets in the browser.
- `VITE_APP_HOME_ROUTE`: Default route. Use `/openviking` for the command bridge.

## Deployment posture

- Build command: `npm run build`
- Output directory: `dist`
- SPA rewrites are configured in `vercel.json`.
- Browser hardening headers are configured in `vercel.json`.
- The app uses lazy routes so the OpenViking command bridge does not load the legacy Three/Rapier 3D stack on startup.

## Production caveats

- Vite environment variables are public client-side values. Do not place private API keys in `VITE_*`.
- Set `CAMELOT_GATEWAY_TOKEN` on the Rust Bifrost Gateway to require auth for protected HTTP routes and websocket access.
- Set `MODAL_CLOUD_BRAIN_URL` on the Rust Bifrost Gateway to proxy cloud brain calls through `/modal/cloud-brain`.
- If Vercel hosts the UI while Bifrost runs on a local machine, the browser will call the viewer's local `127.0.0.1`, not the Vercel server. This is correct for a local command deck, but cloud production needs a public HTTPS/WSS Bifrost bridge.
- Some embedded sites can block iframing with their own `X-Frame-Options` or CSP. Gradio should be hosted with iframe-friendly headers if it is embedded.
