# EXCALIBUR v1000 — Deployment Guide

HTMX-driven dashboard + FastAPI control plane for the CAMELOT-OS sovereign
runtime. Targets local Edge (laptop / Termux / mini-PC) deployments against the
8 GB RAM ceiling — no cloud, no telemetry, no third-party networked services
unless explicitly listed in "Optional Add-ons" below.

---

## 1. What ships

| File | Purpose |
|---|---|
| `excalibur_controller.py` | FastAPI control plane: `/api/status`, `/api/go`, `/api/rezero`, `/api/stream`, `/health`, `/version`, `/favicon.ico`, debug-only `/api/_test/reset` |
| `excalibur_dashboard.html` | Single-file UI (Tailwind v4 + htmx 2.0.3 + htmx-ext-sse 2.2.2 + Web Audio) |
| `excalibur_state.json` | Auto-generated on first boot; persists gate status across restarts |
| `tests/test_excalibur_controller.py` | 19+ tests covering regression, palette contract, auth, CORS, persistence, audio SSE shape |
| `DEPLOYMENT_EXCALIBUR.md` | This file |

---

## 2. Pre-requisites

- **Python 3.11+** with `venv` (3.13 verified).
- **uvicorn**, **fastapi**, **pytest**, **httpx** — all installable from PyPI.
- *(optional, real TTS)* **`pyttsx3`** plus the platform speech engine:
  - Windows: SAPI 5 ships with the OS — no extra step.
  - macOS: `NSSpeechSynthesizer` ships with the OS — no extra step.
  - Linux / Termux: `apt install espeak espeak-ng` (or `pkg install espeak` on Termux).
  - Without `pyttsx3` available, the controller falls back to a pure-stdlib
    procedural sine synth so the audio channel still works.
- *(optional, chromium screenshots)* `chrome` for `browser-use` verification.

---

## 3. Install (desktop)

```powershell
cd C:\Users\vizio\CAMELOT_OS
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install fastapi uvicorn[standard] pytest httpx pyttsx3
```

## 3.1 Install (Termux)

```bash
pkg update && pkg install python espeak espeak-ng
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install fastapi "uvicorn[standard]" pytest httpx pyttsx3
```

---

## 4. Run

```bash
EXCALIBUR_AUTH_TOKEN=$(python -c 'import secrets;print(secrets.token_urlsafe(24))') \
  .venv/bin/python -m uvicorn excalibur_controller:app \
    --host 127.0.0.1 --port 8811 --reload
```

Open `http://127.0.0.1:8811/` in any modern browser.

> **Operator note:** the boot log emits either `EXCALIBUR auth: using
> EXCALIBUR_AUTH_TOKEN from environment.` or a warning that a one-shot token
> was auto-generated. **Copy the token from the first line of the boot log
> into the dashboard's "Operator Auth Token" panel and press SAVE.** Operators
> who set `EXCALIBUR_AUTH_TOKEN` get a stable token across restarts.

### Run on a port other than 8811

```bash
.venv/bin/python -m uvicorn excalibur_controller:app --host 127.0.0.1 --port 9001
```

### Run behind nginx / a tunnel

Add `EXCALIBUR_ALLOW_ORIGIN_REGEX='https://.*\.example\.com$'` so the CORS
allow-list matches your public origin (or pin to a comma-separated literal list
via `EXCALIBUR_ALLOW_ORIGINS=https://app.example.com,https://ops.example.com`).
Then run uvicorn behind nginx; terminate TLS upstream and let nginx forward
plaintext HTTP to `127.0.0.1:8811`.

---

## 5. Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `EXCALIBUR_AUTH_TOKEN` | auto-generated | Required on `POST /api/go` and `POST /api/rezero`. Compared with `secrets.compare_digest`. |
| `EXCALIBUR_STATE_FILE` | `excalibur_state.json` next to the controller (dev) / under `_DATA_ROOT` (frozen) | Atomic JSON file persisting gate status across restarts. |
| `EXCALIBUR_EVENT_LOG` | `logs/excalibur_events.jsonl` under the same root | JSONL audit log of every `/api/go`, `/api/rezero`, `/api/_test/reset`. Setting this overrides the inferred location. |
| `EXCALIBUR_DATA_DIR` | See [Data Directory Routing](#data-directory-routing) below | Operator override for the mutable-state root (state.json + logs/). |
| `EXCALIBUR_ALLOW_ORIGINS` | empty (regex-only) | Comma-separated literal CORS origins (skip regex entirely). |
| `EXCALIBUR_ALLOW_ORIGIN_REGEX` | `https?://(localhost\|127\.0\.0\.1\|\[::1\])(:\d+)?$` | Browser-friendly regex for local Edge / Termux. Override for prod. |
| `EXCALIBUR_DEBUG` | unset | When `=1`, mounts `POST /api/_test/reset` for ops. Otherwise 404. |

Credentials of any kind are never logged.

---

## 5.1 Data Directory Routing

The controller distinguishes between two filesystem roots so the frozen
binary never accidentally writes state into the bundle's `_internal/`
folder (which would be read-only when installed under `C:\Program Files\`
and would pollute the bundle with runtime data on reinstall).

### `_BUNDLE_ROOT` — read-only assets

Where the bundled **read-only** assets live (just `excalibur_dashboard.html`
today; pyttsx3 driver DLLs / espeak binaries on POSIX).

| Build mode | Path |
|---|---|
| Local dev (`python excalibur_controller.py` or `uvicorn excalibur_controller:app`) | `Path(excalibur_controller.py).parent` (the checkout root) |
| Frozen (`dist/excalibur/excalibur.exe`) | `sys._MEIPASS` → `<bundle>/_internal/` |

### `_DATA_ROOT` — mutable state

Where the controller writes `excalibur_state.json` and `logs/excalibur_events.jsonl`.

| Source | Windows | POSIX (Linux / Termux / macOS) |
|---|---|---|
| `EXCALIBUR_DATA_DIR` env var (always wins) | wherever you point it | wherever you point it |
| Frozen default (e.g. desktop shortcut, `Win+R → excalibur`) | `%APPDATA%\EXCALIBUR\` | `$XDG_DATA_HOME/excalibur/` (fallback `~/.excalibur/`) |
| Local dev default | `<controller file>/excalibur_state.json` (next to the source) | same |

A boot-time breadcrumb is logged so operators can verify the resolved
paths before triggering any state mutation:

```text
EXCALIBUR bundle=C:\Program Files\Excalibur\_internal data=C:\Users\vizio\AppData\Roaming\EXCALIBUR
```

### Operator overrides

```powershell
# Pin state to a stable OS location forever.
$env:EXCALIBUR_DATA_DIR = "E:\camelot\excalibur-state"
C:\Apps\Excalibur\excalibur.exe
```

```bash
# Mac/Linux/Termux: pin to an explicit runtime dir.
EXCALIBUR_DATA_DIR=/var/lib/excalibur /opt/excalibur/excalibur
```

### Verification on first boot

```text
# Windows
dir "%APPDATA%\EXCALIBUR"
# → excalibur_state.json, logs\excalibur_events.jsonl

# Windows SYSTEM context (NT AUTHORITY\SYSTEM, Windows services, scheduled
# tasks). `%APPDATA%` resolves to the SYSTEM profile, so state lands at:
dir "C:\Windows\System32\config\systemprofile\AppData\Roaming\EXCALIBUR"

# POSIX (XDG)
ls "${XDG_DATA_HOME:-$HOME/.local/share}/excalibur"
# → excalibur_state.json, logs/excalibur_events.jsonl

# POSIX (fallback)
ls "$HOME/.excalibur"
```

### Network-share deployments (UNC paths)

The frozen binary can run with `_DATA_ROOT` mapped to a UNC path for multi-host
deployments:

```text
# Windows
set EXCALIBUR_DATA_DIR=\\fileserver\camelot\excalibur-state

# POSIX
export EXCALIBUR_DATA_DIR=/mnt/nfs/excalibur-state
```

Caveats:
- The running user account MUST have write+create permissions on the target
  share. On Windows SMB, run the binary under a service account that owns
  the share; POSIX NFS often needs `no_root_squash` if you launch under root.
- Latency on the share becomes the bootstrap floor — expect the first `/api/go`
  to take 200-1000 ms instead of the usual ~5 ms. For latency-sensitive
  operators, run locally and replicate state out-of-band.

### Migration from a controller-sibling layout

If you're upgrading an existing install that put `excalibur_state.json` next
to the controller (the legacy fallback before this routing layer), do a
two-step migration:

1. **One-shot copy.** Move/rename the old file to the new path:
   ```text
   :: Windows user install
   move excalibur_state.json "%APPDATA%\EXCALIBUR\excalibur_state.json"

   # POSIX user install
   mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/excalibur"
   mv excalibur_state.json "${XDG_DATA_HOME:-$HOME/.local/share}/excalibur/"
   ```
2. **Pin the controller.** Set `EXCALIBUR_STATE_FILE` to the new absolute
   path so future boots don't accidentally re-create a sibling file in cwd:
   ```text
   set EXCALIBUR_STATE_FILE=%APPDATA%\EXCALIBUR\excalibur_state.json
   ```

The controller doesn't auto-migrate because doing so silently would mask
operator confusion about where state lives.

---

## 6. Production checklist

- [ ] **Set `EXCALIBUR_AUTH_TOKEN`**. The token is never logged; without it, a
      fresh one is auto-generated each boot.
- [ ] **Override `EXCALIBUR_ALLOW_ORIGIN_REGEX`** to your real origin
      (e.g. `https://app\.example\.com$`). The default only matches localhost /
      127.0.0.1 / `[::1]`.
- [ ] **Always run uvicorn behind a TLS-terminating proxy** in production. The
      control plane itself speaks plaintext HTTP.
- [ ] **Disable `EXCALIBUR_DEBUG`** (do not set it) in production to keep the
      no-auth `/api/_test/reset` endpoint off the route table.
- [ ] **Persist `excalibur_state.json`** somewhere durable. The path is
      operator-configurable via `EXCALIBUR_STATE_FILE`.
- [ ] **Single-process deployment.** The control plane holds the state in
      memory + the atomic JSON file; horizontally-scaling would require
      swapping `_save_state()` for MemCastle / MemPalace L2 (see
      `_commit_state()` comments).
- [ ] **For Termux**: keep the device awake with `termux-wake-lock` if running
      continuously. Caddy / nginx reverse-proxy recommended.
- [ ] **For containers**: ship `python:3.13-slim` + `apt-get install -y espeak`
      (Linux) OR `python:3.13-windowsservercore` with SAPI pre-installed.

---

## 7. Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET`  | `/`                      | open | Serves `excalibur_dashboard.html`. |
| `GET`  | `/favicon.ico`           | open | 1x1 transparent ICO. Defeats implicit browser request. |
| `GET`  | `/health`                | open | Returns `ok`. |
| `GET`  | `/version`               | open | Returns `{name, version}`. |
| `GET`  | `/api/status`            | open | Pre-rendered HTML fragment for htmx polling. |
| `GET`  | `/api/stream`            | open | SSE channel: multi-modal text + amplitude + base64 PCM audio. |
| `POST` | `/api/go`                | `X-Camelot-Auth` | Resumes the iron gate. Persists state. |
| `POST` | `/api/rezero`            | `X-Camelot-Auth` | Rolls the gate back to PAUSED. Persists state. |
| `POST` | `/api/_test/reset`       | `EXCALIBUR_DEBUG=1` only | Reset state to canonical defaults. 404 in prod. |

---

## 8. Smoke test

```bash
# Health
curl -sS http://127.0.0.1:8811/health

# Status (royal-paused initially)
curl -sS http://127.0.0.1:8811/api/status | head -3

# /api/go without auth (expect 401)
curl -sS -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:8811/api/go

# /api/go with auth (expect 200 + HTML, state.json now LIVE/SLEEP_MODE)
curl -sS -X POST -H "X-Camelot-Auth: $EXCALIBUR_AUTH_TOKEN" http://127.0.0.1:8811/api/go

# Restart uvicorn and re-check — state survives
cat excalibur_state.json
curl -sS http://127.0.0.1:8811/api/status | grep -E 'LIVE|PAUSED'
```

---

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Dashboard loads but background is white / unstyled | Tailwind v4 standalone CDN unreachable from your network | Wire a proxy or fall back to a local Tailwind CLI build that emits one CSS file. |
| Browser console 404 on `/favicon.ico` | (was) Old dashboard lacked a favicon | Now the dashboard declares an inline `<link rel="icon" href="data:image/svg+xml,utf8,<svg ...>">E</svg>">`; modern browsers consume the data URI and skip the implicit `/favicon.ico` request entirely. Verify with `curl -sS http://.../ | grep 'rel="icon"'`. |
| `/api/go` returns 401 | Missing or stale auth token | Re-copy the token from the boot log into the dashboard's auth input. |
| State does not persist | `EXCALIBUR_STATE_FILE` points to a path Uvicorn can't write | Confirm `ls -la $EXCALIBUR_STATE_FILE` after a successful `/api/go`. |
| No audio playback in browser | User never pressed `▶ ENABLE AUDIO` (browsers require a gesture) | Click the button once. |
| TTS engine logs `procedural` despite `pyttsx3` installed | pyttsx3 driver failed init (no espeak binary, missing SAPI, etc.) | Install the platform speech engine. Boot log will say "falling back to procedural". |
| Port already in use (`Errno 10048` / `98`) | A previous uvicorn process is still holding the port | `taskkill /F /PID <pid>` (Windows) or `kill -9 <pid>` (Linux/Termux). |

---

## 10. Optional add-ons

- **Real TTS** — install `pyttsx3` + the platform engine. The control plane
  auto-detects at import time and logs which engine won the election.
- **MemCastle / MemPalace L2** — replace `_save_state` / `_load_state` with a
  call into `control_plane/memcastle.py` (sqlite-vec) or
  `01_KERNEL/memory/mempalace_l2.py`. The persistence write boundaries are
  documented on `_commit_state()` so a future maintainer can swap the backend
  without changing call-site usage.
- **NotebookLM telemetry** — `control_plane/cognitive_service.py` ships the
  Graphify + MemCastle + Bridge pipeline; can be wired into a side process to
  push the gate-state deltas.
- **Camelot Mesh event log** — every `/api/go`, `/api/rezero`, and
  `/api/_test/reset` appends a JSONL record to
  `$EXCALIBUR_EVENT_LOG` (default `logs/excalibur_events.jsonl`) carrying
  `ts`, `kind`, `knight`, `before`, `after`, `client`, `metadata`. The schema
  mirrors `01_KERNEL/EXCALIBUR/excalibur_autopilot.py` so a single grain
  reaper can consume both files. Override with `EXCALIBUR_EVENT_LOG`.
- **Portable single-file binary** — `excalibur.spec` builds a self-contained
  `dist/excalibur.exe` (≈25 MB with the procedural audio engine; larger with
  pyttsx3). Build with:

  ```bash
  .venv/Scripts/python.exe -m pip install pyinstaller
  .venv/Scripts/python.exe -m PyInstaller --clean excalibur.spec
  ./dist/excalibur.exe                   # default port 8811
  EXCALIBUR_PORT=9001 ./dist/excalibur.exe
  ```

  The Python interpreter is bundled; no venv is required on the target host.
  Cross-publish to Termux via `[Termux-API](file:///C:/Users/vizio/CAMELOT_OS)`'s
  `termux-share` after running `./dist/excalibur.exe` once to confirm boot.
