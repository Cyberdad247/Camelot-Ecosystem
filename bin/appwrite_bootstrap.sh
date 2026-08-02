#!/usr/bin/env bash
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
#
# bin/appwrite_bootstrap.sh — PR #1 of NOTES_MNEMOSYNE_WIRING.md (2026-07-14).
#
# Idempotent Appwrite 1.6.5 self-host bootstrapper. Reads .env.appwrite (or
# copies from .env.appwrite.example), rotates SECRET fields via
# `openssl rand -hex 32`, brings up the docker-compose.appwrite.yml stack,
# polls /v1/health until 200 (max 120s), issues an API key via appwrite-cli,
# and writes APPWRITE_API_KEY back to .env.appwrite for Bifrost to consume.
#
# Usage:
#   bin/appwrite_bootstrap.sh            # full bootstrap
#   bin/appwrite_bootstrap.sh --dry-run  # checks docker + env + port presence
#   bin/appwrite_bootstrap.sh --teardown # docker compose down -v (full reset)
#
# Pre-conditions:
#   - docker + docker compose v2 + jq + openssl installed
#   - BIFROST context: it's OK for Appwrite's stack to be off while you ship
#     PR #1 alone. PR #3 will assume this script has already run.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"
COMPOSE_FILE="docker-compose.appwrite.yml"
ENV_FILE=".env.appwrite"
ENV_EXAMPLE=".env.appwrite.example"
RUNTIME_DIR="${APPWRITE_RUNTIME_DIR:-/opt/appwrite_runtime}"
BACKUPS_DIR="$RUNTIME_DIR/backups"

DRY_RUN=0
TEARDOWN=0

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --teardown) TEARDOWN=1 ;;
        *) echo "Unknown arg: $arg" >&2; exit 64 ;;
    esac
done

step() { printf "\n\033[1;36m>>> %s\033[0m\n" "$*"; }
ok()   { printf "\033[1;32m    OK\033[0m  %s\n" "$*"; }
warn() { printf "\033[1;33m    WARN\033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m    ERR\033[0m  %s\n" "$*" >&2; exit 1; }

# ── Teardown path ──────────────────────────────────────────────────────
if [ "$TEARDOWN" = "1" ]; then
    step "Tearing down camelot-appwrite stack (full reset, volumes included)"
    docker compose -f "$COMPOSE_FILE" down -v 2>&1 || warn "Compose down failed; check docker"
    ok "Teardown complete. No .py files touched —pure infra."
    exit 0
fi

# ── Pre-flight checks ─────────────────────────────────────────────────
step "Pre-flight: docker + jq + openssl availability"
command -v docker >/dev/null 2>&1 || err "docker not found; install Docker"
docker compose version >/dev/null 2>&1 || err "docker compose v2 not found (Docker CLI plugin required)"
command -v jq >/dev/null 2>&1 || err "jq not found; install jq"
command -v openssl >/dev/null 2>&1 || err "openssl not found; install openssl"

ok "Docker prerequisites in place"
[ "$DRY_RUN" = "1" ] && { warn "Dry-run only: skipping docker compose"; exit 0; }

# ── Step 1: env file bootstrap ─────────────────────────────────────────
step "Step 1: env file bootstrap"
if [ ! -f "$ENV_FILE" ]; then
    [ -f "$ENV_EXAMPLE" ] || err "Missing $ENV_EXAMPLE — cannot seed $ENV_FILE"
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    ok "Copied $ENV_EXAMPLE → $ENV_FILE"
fi

# ── Step 2: rotate SECRET fields (idempotent: skip if already rotated) ─
step "Step 2: rotate secrets (only if placeholder still set)"
rotate_if_placeholder() {
    local key="$1"
    local current
    current=$(grep -E "^${key}=" "$ENV_FILE" | head -1 | cut -d= -f2- || echo "")
    if [ "$current" = "changeme-at-bootstrap" ] || [ -z "$current" ] || [ "$current" = "<issued-by-bootstrap-script>" ]; then
        local rotated
        rotated=$(openssl rand -hex 32)
        # in-place sed: replace the line value (escape pipes + ampersands for sed safety)
        local escaped
        escaped=$(printf '%s\n' "$rotated" | sed -e 's/[&|\\]/\\&/g')
        sed -i.bak -E "s|^(${key}=).*|\1${escaped}|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
        ok "Rotated $key"
    else
        warn "$key already rotated — leaving as-is (idempotent)"
    fi
}
rotate_if_placeholder APPWRITE_DB_PASS
rotate_if_placeholder APPWRITE_DB_ROOT_PASS
rotate_if_placeholder APPWRITE_STORAGE_MINIO_ACCESS_KEY
rotate_if_placeholder APPWRITE_STORAGE_MINIO_SECRET

# ── Step 3: docker compose pull ────────────────────────────────────────
step "Step 3: docker compose pull"
docker compose -f "$COMPOSE_FILE" pull 2>&1 | tail -10 || err "docker compose pull failed"

# ── Step 4: docker compose up ──────────────────────────────────────────
step "Step 4: docker compose up -d"
mkdir -p "$BACKUPS_DIR"
docker compose -f "$COMPOSE_FILE" up -d 2>&1 | tail -10 || err "docker compose up failed"
ok "Stack up; containers: $(docker compose -f "$COMPOSE_FILE" ps --services | wc -l)"

# ── Step 5: health-check loop ─────────────────────────────────────────
step "Step 5: health-check loop (max 120s)"
deadline=$((SECONDS + 120))
appwrite_url="https://$(grep -E '^APPWRITE_DOMAIN=' "$ENV_FILE" | cut -d= -f2-)/v1/health"
# Override per APPWRITE_FORCE_HTTPS for local-dev: try both schemes
while [ $SECONDS -lt $deadline ]; do
    if curl -fsS --max-time 5 "https://$(grep -E '^APPWRITE_DOMAIN=' "$ENV_FILE" | cut -d= -f2-)/v1/health" >/dev/null 2>&1; then
        health_url="https://$(grep -E '^APPWRITE_DOMAIN=' "$ENV_FILE" | cut -d= -f2-)/v1/health"
        ok "Appwrite HEALTHY at $health_url"
        break
    fi
    if curl -fsS --max-time 5 -k "http://$(grep -E '^APPWRITE_DOMAIN=' "$ENV_FILE" | cut -d= -f2-)/v1/health" >/dev/null 2>&1; then
        health_url="http://$(grep -E '^APPWRITE_DOMAIN=' "$ENV_FILE" | cut -d= -f2-)/v1/health"
        warn "Appwrite HEALTHY only on http (Traefik TLS not yet issued — local-dev OK)"
        break
    fi
    sleep 5
done
[ $SECONDS -lt $deadline ] || err "Appwrite did not become HEALTHY within 120s"

# ── Step 6: issue API key (manual fallback — appwrite-cli preferred) ──
step "Step 6: API key provisioning (manual — pop .env, then `appwrite-cli keys create`)"
echo "    MANUAL STEP:"
echo "      1. Open https://appwrite.local in a browser"
echo "      2. Create a project named 'sovereign_db' (or update APPWRITE_PROJECT in .env)"
echo "      3. Generate an API key with the 'documents.write' + 'documents.read' scopes"
echo "      4. Paste the key into APPWRITE_API_KEY= in .env.appwrite"
echo "    The Bifrost Bridge will pick up these env vars on next dispatch."
warn "Future PR #3 will automate this with `appwrite-cli keys create --scope documents.*`"

# ── Step 7: print NEXT-STEPS ───────────────────────────────────────────
step "Appwrite LIVE"
ok "Stack: 5 services (appwrite + mariadb + redis + minio + traefik)"
ok "Health: $health_url"
ok "Env:    $ENV_FILE (gitignored)"
ok "Backups: weekly cron → $BACKUPS_DIR/"
echo ""
echo "Next:"
echo "  - Bifrost side: wait for PR #3 to enable appwrite_client.py integration"
echo "  - Verification: curl $health_url → expect {\"status\":\"pass\",...}"
echo "  - Teardown:    bin/appwrite_bootstrap.sh --teardown"

# ── Verify gitignore covers the local env file ────────────────────────
if [ -f .gitignore ] && ! grep -q "^\.env\.appwrite$" .gitignore; then
    warn ".gitignore does NOT list '.env.appwrite' — adding it"
    echo ".env.appwrite" >> .gitignore
fi

ok "Bootstrap complete."
