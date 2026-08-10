# QERE — Cybertronia Extraction Pipeline (Chrome MV3 extension)

A Chrome extension: highlight text on any page, right-click → "Extract to
QERE", and the side panel formats it into a QERE-structured intent and
dispatches it to the real **Cybertronia Multivoice-Router**
(`04_KINETIC/multivoice`) over HTTP.

## Files
| File | Role |
|---|---|
| `manifest.json` | MV3 manifest — `contextMenus`, `storage`, `sidePanel` permissions + `host_permissions` for the local router (required to bypass CORS; the router doesn't set `Access-Control-Allow-Origin`, and plain `fetch` from a `chrome-extension://` origin is otherwise blocked) |
| `background.js` | Service worker — creates the context-menu item, writes the selection to `chrome.storage.local`, opens the side panel |
| `sidepanel.html` / `sidepanel.js` | The panel UI — picks up the pending extraction (on load and live via `chrome.storage.onChanged`), applies the QERE formatting wrapper, POSTs it to the router, renders the response |

## The real router contract (04_KINETIC/multivoice/orchestration/router.go)
Confirmed by running the router locally and curling both endpoints — this is
**not** the `https://api.cybertronia.internal/v1/router/evaluate` JSON/HTMX
endpoint referenced in early drafts of this feature; that endpoint doesn't
exist anywhere in this codebase.

- `POST /intent` — **raw text body** (not JSON, not form-encoded) = the intent.
  - Success: `200`, body is a single SSE-formatted event —
    `event: response\ndata: <response text>\n\n`.
  - Failure: non-200 (e.g. `502`), body is the plain-text error.
- `GET /healthz` — plain text `MULTIVOICE OK`.

HTMX was in the original draft of this feature but its default form-encoded
POST doesn't match this raw-text-body contract — `sidepanel.js` uses plain
`fetch()` instead of vendoring a library only to bypass its core AJAX layer.

## Running it
```bash
# 1. Start the router (see 04_KINETIC/multivoice/README.md)
cd 04_KINETIC/multivoice
go run ./cmd/multivoice   # binds :7680 by default

# 2. Load the extension
#    chrome://extensions -> Developer mode -> Load unpacked -> 04_KINETIC/qere_extension
```
If `:7680` is already in use on your machine (confirmed to collide with an
unrelated Windows service during development — check via `netstat -ano |
findstr :7680`), start the router with `CAMELOT_MV_SSE=:<port>` and update
`ROUTER_URL` in `sidepanel.js` to match.

## Verified
Loaded as a real unpacked extension in Chromium (Playwright), against a real
running `multivoice` instance:
- Context menu → storage write → side panel live-picks-up flow: confirmed.
- QERE formatting wrapper output: confirmed exact.
- `fetch()` POST + CORS via `host_permissions`: confirmed (failed with a CORS
  error before `host_permissions` was added; fixed).
- Error-path rendering: confirmed against a real `502` from the router (an
  unrelated pre-existing Anthropic API billing issue on this machine).
- SSE success-response parsing: unit-tested against the router's exact
  real format (`event: response\ndata: ...\n\n`) — not exercised end-to-end
  live, since the router's upstream LLM call is currently blocked by that
  same billing issue, not anything in this extension.
