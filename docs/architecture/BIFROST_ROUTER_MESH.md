# Bifrost Router Mesh

## Scope

This is the repo-wide Camelot-Ecosystem contract for the Bifrost Bridge router
mesh. Bifrost is not a single adapter in this repository. It is the bridge
layer that makes these router components part of Camelot-OS:

| Component | Role | Camelot surface |
|---|---|---|
| CLIProxyAPI | OpenAI-compatible provider gateway for Codex, Claude, Gemini, Kimi, and Antigravity lanes | `control_plane/bifrost.py`, default `CLIPROXY_BASE=http://127.0.0.1:8080/v1` |
| OmniRoute | Fast router lane for `SIR_CODEX`, plus repo-local Go router fallback and SSE/status surface | `control_plane/omniroute_policies.py`, `control_plane/go_router/`, default `OMNIROUTE_BASE=http://127.0.0.1:20128/v1` |
| BitRouter | Agentic cost-optimized LLM gateway lane | `control_plane/codex_integration.py`, default `BITROUTER_BASE=http://127.0.0.1:8078/v1` |
| 9Router | Free-provider fallback and token-saving router lane | `control_plane/codex_integration.py`, default `NINE_ROUTER_BASE=http://127.0.0.1:8079/v1` |
| Multivoice Router | Voice and persona ingress switchboard for governed intent routing | `04_KINETIC/multivoice/`, default `http://127.0.0.1:7680` |

## Canonical Integration Points

- `control_plane/bifrost.py` is the dispatch bridge. `sir_codex` resolves to
  `openai_codex` and currently dispatches through the CLIProxy-compatible lane.
- `control_plane/omniroute_policies.py` is the lane selector. Codex/scaffold
  intents resolve to `omni_route_codex`.
- `control_plane/go_router/` is the local Go router surface for rune/SSE
  integration and repo-local OmniRoute behavior.
- `04_KINETIC/multivoice/` is the Cybertronia voice/persona switchboard and
  Bifrost mesh ingress throat.
- `control_plane/codex_integration.py` writes the current bridge status artifact
  at `03_VAULT/runtime_state/codex_integration_latest.json`.
- `apps/bifrost/public/index.html` is the Bifrost bridge UI.
- `02_FORGE/apps/omni-eye-dashboard` exposes the Bridge Matrix in the Camelot
  ecosystem UI.

## Verified Upstreams

These upstream heads were verified live during this integration pass:

| Repo | HEAD | Pushed |
|---|---|---|
| `https://github.com/Cyberdad247/CLIProxyAPI.git` | `f8334be82755113acce3f4a9fb03adc6c1313529` | `2026-07-02T18:32:44Z` |
| `https://github.com/diegosouzapw/OmniRoute.git` | `main` | `2026-08-25` |
| `https://github.com/Cyberdad247/bitrouter.git` | `56b2634a94288ed5b9cfc4840e36877a70e82af4` | `2026-07-02T07:53:20Z` |
| `https://github.com/decolua/9router.git` | `main` | `2026-08-25` |
| `https://github.com/Cyberdad247/Multivoice-router.git` | `57c7c5030628b4630b1e5f0d4cc6ad3358eebe42` | `2026-06-10T20:21:09Z` |

## Verification Gates

```powershell
.venv\Scripts\python.exe -m py_compile control_plane\codex_integration.py control_plane\bifrost.py control_plane\omniroute_policies.py
.venv\Scripts\python.exe -m control_plane.omniroute_policies --test
.venv\Scripts\python.exe -m control_plane.camelot_cli --json codex status
go test ./...
cmd /c npm run build
```

Run `go test ./...` from `04_KINETIC/multivoice` and the dashboard build from
`02_FORGE/apps/omni-eye-dashboard`.
