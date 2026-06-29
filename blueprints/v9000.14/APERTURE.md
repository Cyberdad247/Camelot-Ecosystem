# Aperture — Centralized LLM Access & Spend on the Bifrost Board

[Aperture by Tailscale](https://aperture.tailscale.com) (beta) is a centralized
gateway that fronts upstream LLM providers. Keys live in **one place**, model
access is granted **per user/team**, and every request is attributed to a
**Tailscale identity** — so you get per-user token/cost tracking, session logs,
and an audit trail of the tool calls agents make, without each knight handling
provider credentials.

The Bifrost Intelligence Board now surfaces this directly: an **"LLM ACCESS &
SPEND (Aperture)"** panel (`control_plane/aperture_bridge.py` →
`/bifrost/aperture`) shows total spend, tokens, requests, sessions, and the
top-cost models, with a link to the full Aperture dashboard. It degrades
gracefully — if the tailnet/`ai` device is unreachable it shows "not connected"
rather than erroring.

## 1. Stand up Aperture
1. Sign up at <https://aperture.tailscale.com>; after setup it appears as a
   tailnet device named **`ai`** (dashboard at `http://ai/ui`).
2. Dashboard → **Administration → Providers** → add your provider keys, e.g.:
   ```json
   {
     "providers": {
       "anthropic": {
         "baseurl": "https://api.anthropic.com",
         "apikey": "YOUR_ANTHROPIC_KEY",
         "authorization": "x-api-key",
         "models": ["claude-sonnet-4-5", "claude-opus-4-5"],
         "compatibility": { "anthropic_messages": true }
       }
     }
   }
   ```
3. Grant model access (deny-by-default) — see `tag:aperture` grant in
   `01_KERNEL/mesh/node_c/tailnet-policy.example.hujson` style, e.g. give
   `group:knights` the `user` role on `anthropic/claude-*`.

## 2. Point the knights at Aperture
Clients use a **placeholder** key — Aperture injects real credentials by tailnet
identity. Use `http://` (WireGuard still encrypts).

**Claude Code** (`~/.claude/settings.json`):
```json
{
  "apiKeyHelper": "echo '-'",
  "env": { "ANTHROPIC_BASE_URL": "http://ai" }
}
```

**CI/CD** (e.g. GitHub Actions — runner must be on the tailnet via the Tailscale
GitHub Action as an ephemeral node):
```yaml
env:
  ANTHROPIC_BASE_URL: http://ai
  ANTHROPIC_API_KEY: "-"
```

## 3. Wire the Bifrost panel
The panel reads these (all optional — defaults shown):

| env var | default | purpose |
|---|---|---|
| `APERTURE_URL` | `http://ai` | base URL of the Aperture device |
| `APERTURE_USAGE_PATH` | `/api/usage` | usage endpoint (configurable — Aperture's API is beta) |
| `APERTURE_DASHBOARD_URL` | `http://ai/ui` | link target for "open dashboard →" |

Then run the board (`python -m control_plane.bifrost_server --serve`) and open
`http://127.0.0.1:8080/bifrost`. The panel polls every 10s.

> The usage-endpoint **parser** (`aperture_bridge.parse_usage`) is intentionally
> tolerant (accepts `models`/`usage` rows with `tokens`/`cost`/`requests`
> aliases). If Aperture's GA usage API differs, only `parse_usage` needs
> updating — the panel, endpoint, and graceful-degradation path stay the same.

## Verify
```bash
python -m control_plane.aperture_bridge --test     # 9 checks incl. live mock fetch
python -m pytest tests/test_phase3_brain.py -k aperture -q
```
