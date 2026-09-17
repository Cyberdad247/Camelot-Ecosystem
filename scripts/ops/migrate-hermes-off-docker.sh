#!/usr/bin/env bash
# scripts/ops/migrate-hermes-off-docker.sh
#
# One-way migration of the Hermes agent on the VPS hub from a container to the
# native hermes-agent.service unit.
#
# HUMAN_GATE: this mutates hub unit state. It refuses to run without an explicit
# confirmation flag AND an operator token, and it never removes the previous
# container deployment — that stays available for rollback and is a separate,
# explicit operator decision.
#
# Usage:
#   CAMELOT_DASHBOARD_OPERATOR_TOKEN=... ./scripts/ops/migrate-hermes-off-docker.sh --confirm
#
# Rollback:
#   systemctl disable --now hermes-agent.service

set -euo pipefail

CONFIRM="${1:-}"
TOKEN="${CAMELOT_DASHBOARD_OPERATOR_TOKEN:-}"

HUB="${CAMELOT_HUB_HOST:-162.35.107.134}"
HUB_USER="${CAMELOT_HUB_USER:-root}"

SERVICE_SRC="infra/systemd/hermes-agent.service"
SLICE_SRC="infra/systemd/camelot-workers.slice"
SERVICE_DEST="/etc/systemd/system/hermes-agent.service"
SLICE_DEST="/etc/systemd/system/camelot-workers.slice"

HERMES_BIN="/usr/local/bin/hermes"
HERMES_HOME="/srv/camelot/hermes"

SSH=(ssh -o BatchMode=yes -o ConnectTimeout=8 "${HUB_USER}@${HUB}")

fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
ok()   { printf 'ok: %s\n' "$*"; }

# --- Gate -------------------------------------------------------------------

[[ "$CONFIRM" == "--confirm" ]] || \
    fail "refusing to mutate hub unit state without --confirm"
[[ -n "$TOKEN" ]] || \
    fail "CAMELOT_DASHBOARD_OPERATOR_TOKEN is not set; HUMAN_GATE not satisfied"

[[ -f "$SERVICE_SRC" ]] || fail "missing $SERVICE_SRC"
[[ -f "$SLICE_SRC" ]]   || fail "missing $SLICE_SRC"

printf '=> target hub: %s@%s\n' "$HUB_USER" "$HUB"

# --- Local pre-flight: the unit itself must be container-free ---------------
#
# Only non-comment lines are inspected. A comment cannot execute anything, and
# matching comments produces false positives on innocuous text (this script's
# own filename contains "docker"). What matters is an executable directive that
# names a runtime.

container_directive() {
    grep -vE '^[[:space:]]*#' "$1" \
        | grep -inE '^[[:space:]]*(Exec[A-Za-z]*|Command)=.*\b(docker|podman|containerd)\b' \
        || true
}

for f in "$SERVICE_SRC" "$SLICE_SRC"; do
    hit="$(container_directive "$f")"
    if [[ -n "$hit" ]]; then
        fail "$f invokes a container runtime: $hit"
    fi
done
ok "unit files are container-free"

# --- Remote pre-flight: never remove a working service to install a broken one

"${SSH[@]}" bash -s -- "$HERMES_BIN" "$HERMES_HOME" <<'REMOTE'
set -euo pipefail
HERMES_BIN="$1"
HERMES_HOME="$2"

if [[ ! -x "$HERMES_BIN" ]]; then
    printf 'FAIL: %s is not executable.\n' "$HERMES_BIN" >&2
    printf '\n' >&2
    printf 'The hub has no native Hermes install yet. Install it root-mode so the\n' >&2
    printf 'launcher lands where this unit expects it:\n' >&2
    printf '\n' >&2
    printf '    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sudo bash -s -- --skip-browser\n' >&2
    printf '\n' >&2
    printf -- '--skip-browser omits the Playwright/Chromium step. That step is the only\n' >&2
    printf 'part of the install that needs root-provided shared libraries, and a\n' >&2
    printf 'headless hub does not need browser automation.\n' >&2
    exit 1
fi
printf 'ok: %s present\n' "$HERMES_BIN"

# Upstream auto-detects whether Hermes came from the git installer, Docker, or
# Nix, and reports it. If it reports a container install, this migration would
# produce a unit that shells back into one, so stop here.
if "$HERMES_BIN" doctor 2>&1 | grep -qiE 'install method.*(docker|container)'; then
    printf 'FAIL: hermes doctor reports a container install method; reinstall natively\n' >&2
    exit 1
fi
printf 'ok: hermes doctor reports a non-container install method\n'

if ! getent passwd camelot >/dev/null 2>&1; then
    printf 'FAIL: user camelot does not exist\n' >&2
    exit 1
fi
printf 'ok: user camelot present\n'

# The service has ProtectSystem=strict with only HERMES_HOME writable, and a
# WorkingDirectory of the same path. It must exist before the unit starts, and
# HERMES_HOME must be set because ProtectHome=yes hides ~/.hermes.
install -d -o camelot -g camelot -m 0750 "$HERMES_HOME"
printf 'ok: %s ready\n' "$HERMES_HOME"
REMOTE

# --- Install ----------------------------------------------------------------

scp -o BatchMode=yes "$SLICE_SRC" "${HUB_USER}@${HUB}:${SLICE_DEST}"
scp -o BatchMode=yes "$SERVICE_SRC" "${HUB_USER}@${HUB}:${SERVICE_DEST}"
ok "units transferred"

"${SSH[@]}" bash -s <<'REMOTE'
set -euo pipefail

# The slice must exist before the service binds to it, otherwise systemd cannot
# place the unit in the cgroup hierarchy and the start fails.
systemctl daemon-reload
systemctl enable --now camelot-workers.slice

systemctl enable --now hermes-agent.service
systemctl is-active --quiet hermes-agent.service
printf 'ok: hermes-agent.service active\n'

systemctl show -p Slice --value hermes-agent.service

# hermes doctor is the upstream-supported health check and also reports the
# detected install method. Prefer it over probing the port directly.
if /usr/local/bin/hermes doctor >/dev/null 2>&1; then
    printf 'ok: hermes doctor clean\n'
else
    printf 'warn: hermes doctor reported problems; inspect with: hermes doctor\n'
fi
REMOTE

# --- Report surviving container deployment (do not remove) ------------------

"${SSH[@]}" bash -s <<'REMOTE'
set -uo pipefail
if command -v docker >/dev/null 2>&1 \
   && docker ps --format '{{.Names}}' 2>/dev/null | grep -qx hermes; then
    printf 'note: the previous hermes container is still running.\n'
    printf '      It is retained for rollback. Remove it explicitly once the\n'
    printf '      native unit has proven stable:\n'
    printf '          docker stop hermes && docker rm hermes\n'
else
    printf 'note: no hermes container currently running\n'
fi
REMOTE

printf '=> migration complete\n'
printf '=> rollback: systemctl disable --now hermes-agent.service\n'
