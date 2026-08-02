#!/usr/bin/env bash
# camelotd.sh — Camelot-OS Bare-Metal Client Node Orchestrator
# Written on a Windows dev host as a TEMPLATE. Operator runs this NATIVELY on
# the Linux client node. Do NOT invoke from PowerShell or WSL cwd != /opt/camelot
# paths will silently misbehave because the runtime tree lives on the host only.
#
# Responsibilities:
#   1. Ensure /var/run/camelot + /var/log/camelot exist.
#   2. Idempotently start camelot-kickbox + camelot-openmontage via systemctl.
#   3. Launch the Node bus + cartridge gateway with PID files + log redirection.
#   4. Symlink the KBA cartridge into /var/www/camelot/active.
#   5. Trap EXIT/INT/TERM so child Node processes are stopped cleanly.
#
# This script is intentionally a thin supervisor: it does NOT loop-restart
# long-running services (systemd's Restart=on-failure owns that policy) and
# does NOT install or migrate the unit files (operator-driven, see the
# companion BARE-METAL-DEPLOY.md).

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — runtime paths match the production layout on the Linux node.
# ---------------------------------------------------------------------------
CART_DIR="/opt/camelot/cartridges"
GATEWAY_PORT=8443

LOG_DIR="/var/log/camelot"
RUN_DIR="/var/run/camelot"

mkdir -p "$LOG_DIR" "$RUN_DIR" /var/www/camelot

# ---------------------------------------------------------------------------
# Logging helper — single line, UTC, prefix-tag so journalctl correlation works.
# ---------------------------------------------------------------------------
log() {
    printf '%s [camelotd] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"
}

# ---------------------------------------------------------------------------
# Cleanup trap — best-effort kill of background Node children we own.
# systemd already supervises camelot-kickbox / camelot-openmontage so we do
# not touch them here; touching their cgroups from a sibling script would
# race with systemd's own controller.
# ---------------------------------------------------------------------------
cleanup() {
    log "Trap fired — stopping Node children we own."
    for pidfile in "$RUN_DIR/bus.pid" "$RUN_DIR/gateway.pid"; do
        if [ -f "$pidfile" ]; then
            pid="$(cat "$pidfile" 2>/dev/null || true)"
            if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
                log "Killing PID $pid (from $pidfile)"
                kill "$pid" 2>/dev/null || true
            fi
            rm -f "$pidfile"
        fi
    done
    log "camelotd exit."
}
trap cleanup EXIT INT TERM

# ---------------------------------------------------------------------------
# 1. Ensure native systemd services (kickbox + openmontage) are active.
# is-active || start is the canonical idempotency form: if systemd already
# started them at boot this is a no-op.
# ---------------------------------------------------------------------------
log "Verifying camelot-kickbox systemd unit..."
systemctl is-active --quiet camelot-kickbox \
    || sudo systemctl start camelot-kickbox

log "Verifying camelot-openmontage systemd unit..."
systemctl is-active --quiet camelot-openmontage \
    || sudo systemctl start camelot-openmontage

# ---------------------------------------------------------------------------
# 2. Mount the default cartridge (KBA) by symlink. Symlink, not copy, so
# operator updates to /opt/camelot/cartridges/kba-executive-assistant/www
# propagate without a redeploy.
# ---------------------------------------------------------------------------
log "Mounting KBA cartridge into /var/www/camelot/active"
ln -sfn "$CART_DIR/kba-executive-assistant/www" /var/www/camelot/active

# ---------------------------------------------------------------------------
# 3. Launch Node bus + cartridge gateway with PID tracking + log redirection.
# nohup defeats SIGHUP if the operator's terminal disappears; appending to
# LOG_DIR/*.log lets journalctl/syslog ingest them via rsyslog forwarding.
# ---------------------------------------------------------------------------
log "Starting Node bus (/opt/camelot/os/lib/bus.js)"
nohup node /opt/camelot/os/lib/bus.js \
    > "$LOG_DIR/bus.log" 2>&1 &
bus_pid=$!
if [ -z "$bus_pid" ] || ! kill -0 "$bus_pid" 2>/dev/null; then
    log "ERROR: bus.js launch produced no live PID; aborting before partial-start state."
    exit 1
fi
echo "$bus_pid" > "$RUN_DIR/bus.pid"

log "Starting cartridge gateway on port $GATEWAY_PORT"
nohup node /opt/camelot/system/gateway/server.js --port "$GATEWAY_PORT" \
    > "$LOG_DIR/gateway.log" 2>&1 &
gateway_pid=$!
if [ -z "$gateway_pid" ] || ! kill -0 "$gateway_pid" 2>/dev/null; then
    log "ERROR: gateway launch produced no live PID; aborting before partial-start state."
    # Also clean up the already-running bus so we don't leave it orphaned.
    [ -f "$RUN_DIR/bus.pid" ] && kill "$(cat "$RUN_DIR/bus.pid")" 2>/dev/null || true
    exit 1
fi
echo "$gateway_pid" > "$RUN_DIR/gateway.pid"

log "camelotd orchestrator running. PIDs: bus=$(cat "$RUN_DIR/bus.pid") gateway=$(cat "$RUN_DIR/gateway.pid"). Awaiting SIGTERM..."

# Block forever — cleanup trap fires on any exit signal.
wait
