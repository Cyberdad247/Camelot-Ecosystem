#!/usr/bin/env bash
# ========================================================================================
# [SYSTEM ACTIVATION]: CAMELOT-OS vMAX OMEGA TITAN
# [TARGET HOST]: 8GB InterServer VPS (162.35.107.134) // "Cybertronia Hub"
# [BOOTSTRAP CLASS]: FULLSTACK_BAREMETAL_CUBE
# [SECURITY LEVEL]: EXCALIBUR_ZERO_TRUST
# [DO NOT]: Use Docker. Use Kubernetes. Use Node.js or Python in hot-path.
# ========================================================================================
#
# CONTRACT: Post-conditions, not attempts.
#
# Every phase in this file ends by asserting an OUTCOME. Nothing is allowed to fail
# quietly. The previous revision was almost entirely `|| true` — including PHASE 5,
# which enables the always-on daemons:
#
#     sudo systemctl enable --now camelot-heimdall-bifrost \
#                              camelot-hermes-prime \
#                              camelot-vps-mesh \
#                              caddy || true
#
# That line meant "try four things and report nothing", and it is why the hub ran
# for weeks with `caddy` absent, three camelot units `disabled`, and a
# `camelot-hermes-prime.service` that was switched off with a `--loop` flag the
# engine rejects outright. The banner still said "FORGED & SOVEREIGN", because the
# banner was a print statement, not a result.
#
# Post-conditions here describe OUTCOMES, not implementations:
#   * "something serves :80" instead of "caddy is running" — nginx serves the hub,
#     and asserting caddy would have failed a host that is actually fine.
#   * "the unit is enabled AND active" instead of "enable --now returned".
#
# Usage:
#   bash scripts/vps_hub_bootstrap.sh               # apply, then verify (mutates)
#   bash scripts/vps_hub_bootstrap.sh --apply       # same, explicit
#   bash scripts/vps_hub_bootstrap.sh --self-check  # verify only, NO mutation
#
# `--self-check` audits an existing host read-only. Exit code is 0 only if every
# REQUIRED post-condition holds. Use it to catch drift after the fact, which is the
# thing the old `|| true` made impossible.
# ========================================================================================

set -euo pipefail

MODE="apply"
case "${1:-}" in
  --self-check) MODE="self-check" ;;
  --apply|"")   MODE="apply" ;;
  -h|--help)
    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  *) echo "unknown argument: $1 (try --self-check)" >&2; exit 2 ;;
esac

CUBE_REPO="${CUBE_REPO:-https://github.com/Cyberdad247/Camelot-Ecosystem.git}"
CUBE_DIR="${CUBE_DIR:-/opt/Camelot-Ecosystem}"
HUB_PUBLIC_IP="${HUB_PUBLIC_IP:-162.35.107.134}"

# --- Post-condition contract ------------------------------------------------------------
# Required units are ENABLED (survive reboot) and ACTIVE. The Hermes Prime cadence is a
# timer, so the timer is the unit that must be active — its service is a Type=oneshot and
# is *correctly* inactive between runs.
REQUIRED_UNITS=(
  camelot-bifrost.service
  camelot-vps-mesh.service
  camelot-edge-bus.service
  camelot-hermes-prime.timer
  # The monitoring layer is part of the contract, not a convenience on top of it: a
  # reality check that is installed but not running is documentation. Asserting the
  # timers here means any human or script that runs this audit notices a monitor that
  # has been switched off. (The watchdog is what notices it unattended.)
  camelot-selfcheck.timer
  camelot-selfcheck-watchdog.timer
)

# Units that must NOT be running, because a named replacement owns their job. Keeping this
# explicit stops a well-meaning operator from "fixing" a disabled unit back into service
# and recreating a two-supervisor split.
FORBIDDEN_UNITS=(
  pm2-root.service   # :3001 is owned by camelot-bifrost.service since the PM2 retirement
)

# Required listeners, by outcome.
REQUIRED_PORTS=(80 3001 8095)

PASS_COUNT=0
FAILURES=()
WARNINGS=()

ok()  { printf '  \033[32mPASS\033[0m %s\n' "$1"; PASS_COUNT=$((PASS_COUNT + 1)); }
bad() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAILURES+=("$1"); }
warn(){ printf '  \033[33mWARN\033[0m %s\n' "$1"; WARNINGS+=("$1"); }
phase() { printf '\n\033[1m%s\033[0m\n' "$1"; }

# check <label> <command...> — pass/fail on a read-only predicate.
check() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then ok "$label"; else bad "$label"; fi
}

# attempt <label> <command...> — runs a mutation. Failure is RECORDED, never swallowed.
# The old `|| true` made these indistinguishable from success; here they fail the run.
attempt() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    ok "$label"
  else
    bad "$label (command failed)"
  fi
}

require_user() {
  local u="$1"
  if id "$u" >/dev/null 2>&1; then ok "user $u exists"; else bad "user $u missing"; fi
}

require_unit() {
  local u="$1" en ac
  en=$(systemctl is-enabled "$u" 2>/dev/null || true)
  ac=$(systemctl is-active  "$u" 2>/dev/null || true)
  case "$en" in
    enabled|enabled-runtime|static|indirect) ;;
    *) bad "unit $u not enabled (got: ${en:-unknown}) — it will not survive a reboot"; return 0 ;;
  esac
  if [[ "$ac" == "active" ]]; then
    ok "unit $u enabled + active"
  else
    bad "unit $u enabled but ${ac:-unknown}"
  fi
}

require_port() {
  local p="$1"
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -qE "[:.]${p}\$"; then
    ok "something serves :$p"
  else
    bad "nothing serves :$p"
  fi
}

# Token-aware endpoint probe. Once MESH_BRIDGE_TOKEN is provisioned, the mesh bridge
# requires it; probing without it would report a healthy host as broken.
mesh_http_code() {
  local url="$1"
  if [[ -n "${MESH_BRIDGE_TOKEN:-}" ]]; then
    curl -s -o /dev/null -w '%{http_code}' --max-time 8 \
      -H "x-camelot-token: ${MESH_BRIDGE_TOKEN}" "$url"
  else
    curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$url"
  fi
}

# Require 2xx specifically. `curl -f` treats 3xx as success, so a redirect to a login
# page used to count as a passing endpoint check — the same species of false green this
# rewrite exists to remove.
check_endpoint() {
  local label="$1" url="$2" code
  code=$(mesh_http_code "$url" 2>/dev/null || echo 000)
  if [[ "$code" =~ ^2 ]]; then
    ok "$label"
  else
    bad "$label ($url -> HTTP ${code:-000})"
  fi
}

echo "========================================================================"
echo "🏰 CAMELOT-OS VPS HUB — ${MODE^^} (${HUB_PUBLIC_IP} / KVM563)"
echo "   Sovereign Co-Governors: HERMES_PRIME & SIR_HEIMDALL"
echo "========================================================================"
# NB: `[[ ... ]] && cmd` would abort the script here under `set -e` when the test is
# false, because the compound returns non-zero. Always use an explicit if.
if [[ "$MODE" == "self-check" ]]; then
  echo "   read-only audit: no changes will be made"
fi

# ========================================================================================
# PHASE 1 — OS PREREQUISITES & CGROUPS v2
# ========================================================================================
phase "[PHASE 1] OS Prerequisites & Cgroups v2"

if [[ "$MODE" == "apply" ]]; then
  attempt "apt update"        sudo apt-get update -qq
  attempt "apt upgrade"       sudo apt-get upgrade -y -qq
  attempt "apt prerequisites" sudo apt-get install -y -qq \
    curl wget git build-essential openssl ca-certificates unzip tar jq gnupg lsb-release
fi

if [[ ! -e /sys/fs/cgroup/cgroup.controllers ]]; then
  if [[ "$MODE" == "apply" ]]; then
    echo "  enabling cgroups v2 (reboot required)"
    sudo sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"/' /etc/default/grub
    sudo update-grub
  fi
  bad "cgroups v2 active (reboot required, then re-run)"
else
  ok "cgroups v2 active"
fi

# ========================================================================================
# PHASE 2 — NATIVE TOOLCHAINS & DATASTORES
# ========================================================================================
phase "[PHASE 2] Native Toolchains & Datastores"

if [[ "$MODE" == "apply" ]]; then
  if ! command -v cargo >/dev/null 2>&1; then
    attempt "install Rust toolchain" \
      bash -c 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
    # shellcheck disable=SC1090
    if [[ -f "$HOME/.cargo/env" ]]; then
      source "$HOME/.cargo/env"
    fi
  fi
  if ! command -v go >/dev/null 2>&1; then
    attempt "install Go 1.22.4" bash -c \
      'wget -q https://go.dev/dl/go1.22.4.linux-amd64.tar.gz && sudo tar -C /usr/local -xzf go1.22.4.linux-amd64.tar.gz && rm -f go1.22.4.linux-amd64.tar.gz'
    export PATH="$PATH:/usr/local/go/bin"
  fi
  attempt "postgresql + caddy packages" \
    sudo apt-get install -y -qq openjdk-17-jre-headless postgresql postgresql-contrib caddy
  attempt "enable postgresql" sudo systemctl enable --now postgresql

  if ! command -v minio >/dev/null 2>&1; then
    attempt "install minio" bash -c \
      'wget -q https://dl.min.io/server/minio/release/linux-amd64/minio && sudo install minio /usr/local/bin/ && rm -f minio && sudo mkdir -p /var/lib/minio'
  fi
  # Idempotent by design: `useradd` on an existing user is a no-op, and the previous
  # `|| true` hid genuine failures too. Verify the user, don't trust the exit code.
  getent passwd minio-user >/dev/null 2>&1 || \
    sudo useradd -r -s /sbin/nologin minio-user >/dev/null 2>&1 || true
  attempt "minio state dir owned by minio-user" \
    sudo chown -R minio-user:minio-user /var/lib/minio

  if ! command -v qdrant >/dev/null 2>&1; then
    attempt "install qdrant" bash -c \
      'curl -L https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz | tar -xz && sudo install qdrant /usr/local/bin/ && rm -f qdrant && sudo mkdir -p /var/lib/qdrant/storage'
  fi
  if ! command -v tailscale >/dev/null 2>&1; then
    attempt "install tailscale" bash -c 'curl -fsSL https://tailscale.com/install.sh | sh'
  fi
fi

for tool in cargo go qdrant tailscale; do
  check "$tool installed" command -v "$tool"
done
check "postgresql active" systemctl is-active --quiet postgresql
check "minio-user exists" id minio-user

# ========================================================================================
# PHASE 3 — CAMELOT ECOSYSTEM & SYSTEMD UNITS
# ========================================================================================
phase "[PHASE 3] Camelot Ecosystem & Systemd Units"

if [[ "$MODE" == "apply" ]]; then
  sudo mkdir -p "$CUBE_DIR"
  if [[ ! -d "$CUBE_DIR/.git" ]]; then
    attempt "clone $CUBE_REPO" sudo git clone "$CUBE_REPO" "$CUBE_DIR"
  else
    # A failed pull is not fatal, but it is not silent either: a stale clone is exactly
    # how the hub came to carry a `--loop 60` unit that upstream had already replaced.
    if sudo git -C "$CUBE_DIR" pull --ff-only origin main >/dev/null 2>&1; then
      ok "clone fast-forwarded"
    else
      warn "$CUBE_DIR could not be fast-forwarded — unit files may be stale"
    fi
  fi
  shopt -s nullglob
  units=("$CUBE_DIR"/infra/systemd/*.service)
  shopt -u nullglob
  if (( ${#units[@]} == 0 )); then
    bad "no .service files found under $CUBE_DIR/infra/systemd"
  else
    attempt "install ${#units[@]} unit file(s)" sudo cp "${units[@]}" /etc/systemd/system/
  fi
  attempt "systemctl daemon-reload" sudo systemctl daemon-reload
fi

check "$CUBE_DIR is a git checkout" test -d "$CUBE_DIR/.git"
if compgen -G "/etc/systemd/system/camelot-*.service" >/dev/null; then
  ok "camelot units present in /etc/systemd/system"
else
  bad "no camelot-*.service units installed"
fi

# ========================================================================================
# PHASE 4 — DATASTORE INITIALIZATION
# ========================================================================================
phase "[PHASE 4] Data & Vector Memory"

if [[ "$MODE" == "apply" ]]; then
  if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='camelot_vmax'" 2>/dev/null | grep -q 1; then
    ok "database camelot_vmax already present"
  else
    attempt "create database camelot_vmax" sudo -u postgres createdb camelot_vmax
  fi
  attempt "ensure qdrant collection world_tree" bash -c \
    "curl -s -X PUT http://localhost:6333/collections/world_tree -H 'Content-Type: application/json' -d '{\"vectors\":{\"size\":24,\"distance\":\"Cosine\"}}' >/dev/null"
fi

check "database camelot_vmax exists" bash -c \
  "sudo -u postgres psql -tAc \"SELECT 1 FROM pg_database WHERE datname='camelot_vmax'\" 2>/dev/null | grep -q 1"
check "qdrant collection world_tree reachable" curl -sf http://localhost:6333/collections/world_tree

# ========================================================================================
# PHASE 5 — ALWAYS-ON DAEMONS (the phase whose failures used to be invisible)
# ========================================================================================
phase "[PHASE 5] Always-On Sovereign Hub Daemons"

if [[ "$MODE" == "apply" ]]; then
  for unit in "${REQUIRED_UNITS[@]}"; do
    if [[ -f "/etc/systemd/system/$unit" ]]; then
      attempt "enable --now $unit" sudo systemctl enable --now "$unit"
    else
      bad "$unit not installed (cannot be enabled)"
    fi
  done
fi

for unit in "${REQUIRED_UNITS[@]}"; do
  require_unit "$unit"
done

# --- Engine liveness, not just unit liveness --------------------------------------------
# `require_unit camelot-hermes-prime.timer` above proves the SCHEDULE is on. It does not
# prove the engine is PRODUCING: a timer that is active while its cycles stopped passing
# satisfies every check above, and the hub goes on serving a status that is false. That is
# the exact defect this audit was written to catch (`HERMES_PRIME: ALWAYS_ON_HUB` beside a
# disabled unit), one level down.
#
# The freshness rule itself lives in the bridge (`hermes_prime_status`), so this asserts
# the SERVED verdict instead of restating the window here. A second copy of the threshold
# would be a second source of truth, which is what let the original claim rot.
hp_served="$(curl -fsS -m 10 "http://127.0.0.1:8095/api/hermes" 2>/dev/null \
  | python3 -c 'import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    print("unreachable"); raise SystemExit
# Only the fields /api/hermes actually carries. Printing a field this endpoint does
# not expose would render `cycles=None` as though data were missing.
print("%s age=%ss" % (d.get("status"), d.get("last_cycle_age_s")))' 2>/dev/null)"
if [[ "$hp_served" == ALWAYS_ON_HUB* ]]; then
  ok "hermes prime engine producing fresh cycles (${hp_served})"
else
  bad "hermes prime engine not producing fresh cycles (served: ${hp_served:-unreachable})"
fi

for unit in "${FORBIDDEN_UNITS[@]}"; do
  if systemctl is-active --quiet "$unit" 2>/dev/null; then
    bad "$unit is running — it has been retired in favour of a systemd unit"
  else
    ok "retired supervisor inactive: $unit"
  fi
done

for port in "${REQUIRED_PORTS[@]}"; do
  require_port "$port"
done

# Outcome, not implementation: nginx serves the hub today, so requiring `caddy` would
# fail a correctly-working host. What matters is that the daemons above are enabled and
# the ports answer. Anything else is reported as drift for a human to judge.
if systemctl is-active --quiet caddy 2>/dev/null; then
  ok "caddy active"
elif ss -ltn 2>/dev/null | awk '{print $4}' | grep -qE '[:.]443$'; then
  ok "TLS listener on :443 present"
else
  warn "no listener on :443 — public surface is plaintext HTTP on :80"
fi

# :3001 used to be served by PM2 while camelot-bifrost.service sat inactive/disabled, so
# systemd reported the gateway as dead while it was handling traffic. It is now owned by
# the unit, and this asserts the ownership rather than just the port.
if systemctl is-active --quiet camelot-bifrost 2>/dev/null; then
  ok ":3001 owned by camelot-bifrost.service"
elif ss -ltn 2>/dev/null | awk '{print $4}' | grep -qE '[:.]3001$'; then
  bad ":3001 is served, but NOT by camelot-bifrost.service — a second supervisor owns it"
else
  bad ":3001 is not served by anything"
fi

# ========================================================================================
# PHASE 6 — LUXORA NEXUS LAB PWA
# ========================================================================================
phase "[PHASE 6] Luxora Nexus Lab PWA"

if [[ "$MODE" == "apply" ]]; then
  if [[ -x "$CUBE_DIR/scripts/deploy_luxora_nexus_lab.sh" ]]; then
    attempt "run deploy_luxora_nexus_lab.sh" \
      bash -c "cd '$CUBE_DIR' && ./scripts/deploy_luxora_nexus_lab.sh"
  else
    warn "$CUBE_DIR/scripts/deploy_luxora_nexus_lab.sh not present or not executable"
  fi
fi

# The full client contract, not half of it. `deploy_luxora_nexus_lab.sh` verifies these
# same four paths with its own `check_endpoint` calls; checking only two here let the
# other two answer 302 from the Hermes dashboard while this audit reported the contract
# satisfied. The routes live in infra/nginx/camelot-mesh-bridge.conf and are installed by
# scripts/ops/install-mesh-bridge-routes.sh — this file does not restate them.
check_endpoint "mesh telemetry through nginx"      "http://localhost/mesh/status"
check_endpoint "bifrost knights through nginx"     "http://localhost/bifrost/knights"
check_endpoint "hermes telemetry through nginx"    "http://localhost/hermes/telemetry"
check_endpoint "heimdall governance through nginx" "http://localhost/heimdall/governance"

# ========================================================================================
# RESULT — the banner is a result, not a print statement
# ========================================================================================
echo
echo "========================================================================"
if (( ${#FAILURES[@]} == 0 )); then
  echo "🛡️  VPS HUB VERIFIED — ${PASS_COUNT} post-conditions passed"
  if (( ${#WARNINGS[@]} )); then
    printf '   %d warning(s) — review, not blocking\n' "${#WARNINGS[@]}"
  fi
  echo "========================================================================"
  exit 0
fi

echo "🔴 VPS HUB NOT PRODUCTION-READY — ${#FAILURES[@]} post-condition(s) failed"
echo "========================================================================"
for f in "${FAILURES[@]}"; do printf '   ❌ %s\n' "$f"; done
if (( ${#WARNINGS[@]} )); then
  echo
  for w in "${WARNINGS[@]}"; do printf '   ⚠️  %s\n' "$w"; done
fi
echo "========================================================================"
exit 1
