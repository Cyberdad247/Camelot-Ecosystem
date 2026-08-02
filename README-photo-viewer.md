# Secret Photo Viewer

A small, privacy-first web app for viewing photos in a PIN-protected vault.
It ships as a standalone HTML page (`secret-photo-viewer.html`) and a Gradio
headless wrapper (`gradio_photo_viewer.py`) so you can interact with it from a
browser even when no display is attached to the host.

## Features

- PIN-protected IndexedDB vault (PBKDF2-SHA256 + random salt)
- First-run PIN setup
- Drag/drop or click-to-upload photos
- Headless upload through the Gradio UI or directly via `POST /api/staged`
- Automatic import of staged photos on unlock
- Photo validation and stale/invalid cleanup
- Security headers and CSP
- Per-IP rate limiting on uploads
- Pillow-based image validation (not just extension checks)
- Health endpoint (`/health`)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python gradio_photo_viewer.py
```

Open the printed local URL in a browser and set a PIN on first run.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SPV_HOST` | `0.0.0.0` | Host to bind |
| `SPV_PORT` | `7860` | Port to bind |
| `SPV_STAGING_DIR` | `staged_uploads` | Where headless uploads are staged |
| `SPV_MAX_UPLOAD_SIZE` | `10485760` | Max upload size in bytes (10 MB) |
| `SPV_IFRAME_HEIGHT` | `700px` | Gradio iframe height |
| `SPV_LOG_LEVEL` | `INFO` | Python log level |
| `SPV_STAGING_MAX_AGE_SECONDS` | `3600` | Stale staged file age before cleanup |
| `SPV_RATE_LIMIT_REQUESTS` | `20` | Max upload requests per window per IP |
| `SPV_RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate-limit window in seconds |
| `SPV_API_KEY` | - | Optional API key to protect `/api/staged` endpoints |
| `SPV_PASSWORD_HASH` | - | Optional bcrypt hash of the app password; enables HTTP Basic Auth on all endpoints except `/health` |
| `SPV_STORAGE_BACKEND` | `local` | Staging backend: `local` or `s3` |
| `SPV_REDIS_URL` | - | Redis URL for distributed rate limiting |
| `SPV_S3_ENDPOINT` | - | S3/MinIO endpoint (e.g. `http://minio:9000`) |
| `SPV_S3_BUCKET` | - | S3/MinIO bucket name |
| `SPV_S3_ACCESS_KEY` | - | S3/MinIO access key |
| `SPV_S3_SECRET_KEY` | - | S3/MinIO secret key |
| `SPV_GOOGLE_CLIENT_ID` | - | Google OAuth 2.0 Web Client ID for Google Sign-In / Google Photos |

## Running tests

The project includes both FastAPI backend unit tests and a Playwright end-to-end
browser test.

```bash
# Backend unit tests
python -m pytest tests/test_secret_photo_viewer.py -v

# End-to-end browser test (requires Playwright browsers)
python scripts/verify_photo_viewer.py

# Watch the browser during e2e verification (slower, but useful for debugging)
python scripts/verify_photo_viewer.py --no-headless
```

The backend tests cover the `/api/staged` endpoints (list, upload, download,
delete) and the Gradio `_stage_uploads` helper. The e2e test starts the server on
an ephemeral port, creates a PIN, uploads a generated PNG through both the hidden
headless input and the visible Gradio File component, unlocks the vault, and
asserts that both photos appear in the gallery.

## Headless upload mechanism

The Gradio wrapper exposes a normal `gr.File` component for manual uploads, but
Gradio's File component does not reliably fire its backend event when a headless
browser manipulates its hidden `<input type="file">` directly. To support
programmatic and automated uploads without breaking the visible component:

1. A hidden native `<input id="headless-upload" type="file">` is injected into
   the page via `gr.HTML`.
2. After the Gradio app loads, a small client-side script (registered with
   `blocks.load()`) attaches a `change` listener to that input and posts the
   chosen files to `POST /api/staged`.
3. On success, the same script sends a `SYNC_STAGED` message to the embedded
   vault iframe, which imports the staged files into IndexedDB.

Because the Gradio `File` event itself is wired to `.change()` instead of
`.upload()`, both the visible drag-and-drop component and the hidden headless
input trigger the same `_stage_uploads` handler. This keeps the headless test
path and the manual user path consistent.

## Google Sign-In / Google Photos integration

The Secret Photo Viewer can optionally import photos from a user's Google Photos
library after verifying their Google identity.

### Setup

1. Create a Google Cloud project and OAuth 2.0 Web Client ID.
2. Enable the Google Photos Library API.
3. Set the public Web Client ID:

```bash
export SPV_GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
```

No client secret is stored in the repository. The Client ID is delivered to the
frontend at runtime via `GET /api/google/config`.

### User flow

1. In the vault UI, click **Google Photos**.
2. Sign in with Google. The frontend receives a Google ID token, which it sends
   to `POST /api/google/verify`. The backend validates the token with Google's
   public keys and returns the user's profile.
3. Click **List Photos** to request an access token for the read-only Google
   Photos scope. The frontend sends the access token to `POST /api/google/photos`,
   and the backend proxies the request to `https://photoslibrary.googleapis.com`.
4. Select thumbnails and click **Import Selected**. The backend fetches each
   chosen image, validates it with Pillow, stages it under `/api/staged`, and the
   vault iframe imports it.

### Security notes

- The backend never stores the user's Google access token.
- The Content-Security-Policy is updated to allow scripts/frames from
  `https://accounts.google.com` and image/connect requests to Google Photos APIs.
- The Google Sign-In endpoints return `503` if `SPV_GOOGLE_CLIENT_ID` is unset or if
  the `google-auth` library is not installed.


```bash
# Unit tests
python -m pytest tests/test_photo_viewer_api.py -v

# End-to-end browser test (requires Playwright browsers)
python tests/test_browser_upload.py
```

## Docker

```bash
docker build -t secret-photo-viewer .
docker run -p 7860:7860 secret-photo-viewer
```

Or with Docker Compose:

```bash
docker compose up -d
```

## systemd (Linux VM)

1. Copy files to `/opt/secret-photo-viewer`.
2. Create a virtual environment and install requirements.
3. Adjust `secret-photo-viewer.service` if needed.
4. Install and start:

```bash
sudo cp secret-photo-viewer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now secret-photo-viewer
```

## Password authentication

You can protect the entire app with a single app-level password using HTTP Basic Auth.

1. Generate a bcrypt hash of your password (interactive):

```bash
python gradio_photo_viewer.py --generate-password-hash
```

Copy the printed hash, update `SPV_PASSWORD_HASH` with it, and restart the app to rotate the password.

You can also generate the hash inline without prompts:

```bash
python -c 'import bcrypt; print(bcrypt.hashpw(input("Password: ").encode(), bcrypt.gensalt()).decode())'
```

2. Set the hash in the environment and start the app:

```bash
export SPV_PASSWORD_HASH='$2b$12$...'
python gradio_photo_viewer.py
```

When `SPV_PASSWORD_HASH` is set, every endpoint except `/health` and `/metrics` requires a valid `Authorization: Basic ...` header. The `/api/staged` endpoints can still be accessed with the `X-API-Key` header when `SPV_API_KEY` is also configured, so headless scripts do not need to send a Basic Auth password. `/metrics` remains unauthenticated so Prometheus can scrape it.

The Gradio file-upload handler also re-checks these credentials as defense-in-depth, so even WebSocket-triggered event handlers cannot stage files without the password or API key.

## Reverse proxy (nginx example)

```nginx
server {
    listen 80;
    server_name photos.example.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

The app exposes a Prometheus `/metrics` endpoint with the following metrics:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `spv_upload_requests_total` | Counter | `status` | Upload requests by outcome (`success`, `invalid_type`, `invalid_content`, `oversized`, `error`) |
| `spv_upload_bytes_total` | Counter | - | Total bytes of successfully staged images |
| `spv_upload_duration_seconds` | Histogram | - | Upload processing latency |
| `spv_staged_files_count` | Gauge | - | Current number of files in staging |
| `spv_staged_files_bytes` | Gauge | - | Total bytes used by staged files |
| `spv_health_checks_total` | Counter | - | `/health` endpoint hits |
| `spv_cleanup_removed_total` | Counter | - | Files removed by periodic cleanup |

### Local Prometheus + Grafana (Docker Compose)

```bash
docker compose up -d
```

- App: http://localhost:7860
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (login `admin` / password `admin`)

A pre-built dashboard is provisioned automatically under **Dashboards > Secret Photo Viewer**.

Set a strong Grafana admin password via the `GF_ADMIN_PASSWORD` environment variable before starting the stack; the example compose file enforces this.

## Security notes

- The vault is client-side. Photos are stored in the browser's IndexedDB and are never sent to the server unless uploaded through the headless staging endpoints.
- Staged files are temporary. They are imported into the vault on unlock and deleted automatically. With the `local` backend, a per-process background task removes files older than `SPV_STAGING_MAX_AGE_SECONDS`. With the `s3` backend, rely on bucket lifecycle/expiration policies instead.
- The app is designed for trusted/local network use. When `SPV_API_KEY` is set, the `/api/staged` endpoints require the `X-API-Key` header for upload/list/delete operations. Keep the key out of source control and pass it via the environment.
- The `/metrics` endpoint is unauthenticated so that Prometheus can scrape it. Keep it internal (it is not exposed by the reverse-proxy example below).
- The Docker image runs as a non-root user (`spv`, UID 1000). The staging directory is created with the sticky bit (`1777`) so that named volumes remain writable for the runtime user. If you use a **host bind mount** for `/app/staged_uploads`, ensure the host path is writable by UID 1000; otherwise the bind mount will override the image's permissions.

**Do not expose the unauthenticated endpoints directly to the public internet.** Always place this service behind a reverse proxy, VPN, or firewall. PIN hashing also requires a secure browser context (HTTPS or `localhost`), otherwise first-run setup will fail.
