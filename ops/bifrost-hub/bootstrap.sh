#!/usr/bin/env bash
#
# Camelot Bifrost Hub — bootstrap for the OCI control plane.
#
# Target: Ubuntu 24.04 LTS ARM64 (VM.Standard.A1.Flex, 2 OCPU / 8 GB, 50 GB boot)
#
# Implements the control-plane plan:
#   Bifrost, Sentinel, task scheduler, cartridge/node registry, receipt service,
#   SQLite WAL, encrypted backups, Tailscale, PWA/API backend.
#
# Explicitly NOT installed (per plan): Docker/Kubernetes, Ollama/vLLM or any local
# LLM inference, Neo4j, Weaviate, engineering build workers.
#
# Usage:
#   sudo TS_AUTHKEY=tskey-auth-XXXX ./bootstrap.sh
#
# Env overrides:
#   TS_AUTHKEY   required  Tailscale auth key (https://login.tailscale.com/admin/settings/keys)
#   TS_HOSTNAME  optional  Tailscale machine name      (default: bifrost-hub)
#   ADMIN_USER   optional  non-root admin account      (default: ubuntu)
#   APP_DIR      optional  control-plane root          (default: /opt/camelot/bifrost-hub)
#   BACKUP_DIR   optional  encrypted backup root       (default: /opt/camelot/backups)
#
set -euo pipefail

TS_AUTHKEY="${TS_AUTHKEY:-}"
TS_HOSTNAME="${TS_HOSTNAME:-bifrost-hub}"
ADMIN_USER="${ADMIN_USER:-ubuntu}"
APP_DIR="${APP_DIR:-/opt/camelot/bifrost-hub}"
BACKUP_DIR="${BACKUP_DIR:-/opt/camelot/backups}"

log() { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }

[ "$(id -u)" -eq 0 ] || { echo "error: run as root (sudo)"; exit 1; }
[ -n "$TS_AUTHKEY" ] || { echo "error: TS_AUTHKEY is required (Tailscale auth key)"; exit 1; }
id "$ADMIN_USER" >/dev/null 2>&1 || { echo "error: user '$ADMIN_USER' does not exist"; exit 1; }

export DEBIAN_FRONTEND=noninteractive

log "Phase 1/5 — base packages (minimal, per plan)"
apt-get update -qq
apt-get install -y -qq \
  curl ca-certificates gnupg \
  sqlite3 age ufw fail2ban unattended-upgrades

log "Phase 2/5 — Tailscale (private admin plane)"
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --authkey "$TS_AUTHKEY" --hostname "$TS_HOSTNAME"
TS_IP="$(tailscale ip -4 | head -n1)"

log "Phase 3/5 — control-plane layout + SQLite"
mkdir -p "$APP_DIR"/{bin,bifrost,sentinel,scheduler,registry,receipts,data} \
         "$BACKUP_DIR"
chown -R "$ADMIN_USER":"$ADMIN_USER" "$APP_DIR" "$BACKUP_DIR"

# SQLite WAL for the receipt service (set per-database at service init):
#   PRAGMA journal_mode=WAL;  PRAGMA synchronous=NORMAL;
cat > "$APP_DIR/data/README.md" <<'MD'
# Control-plane data
- receipts.db   — receipt chain (WAL mode, see bootstrap notes)
- registry.db   — cartridge/node registry
- scheduler.db  — task scheduler state
Encrypted nightly snapshots: /opt/camelot/backups (age-encrypted).
MD
chown "$ADMIN_USER":"$ADMIN_USER" "$APP_DIR/data/README.md"

log "Phase 4/5 — firewall: no public ingress after bootstrap"
ufw default deny incoming
ufw default allow outgoing
# SSH only from the Tailscale CGNAT range (100.64.0.0/10); drop public SSH.
ufw allow from 100.64.0.0/10 to any port 22 proto tcp
ufw --force enable

log "Phase 5/6 — encrypted backups (age)"
AGE_KEY="/root/.config/age/bifrost-key.txt"
AGE_RECIPIENT="/root/.config/age/bifrost-recipient.txt"
if [ ! -f "$AGE_RECIPIENT" ]; then
  mkdir -p "$(dirname "$AGE_KEY")"
  age-keygen -o "$AGE_KEY"
  age-keygen -y "$AGE_KEY" > "$AGE_RECIPIENT"
  chmod 600 "$AGE_KEY"
fi

cat > /usr/local/bin/camelot-backup <<'SH'
#!/usr/bin/env bash
# Nightly age-encrypted snapshot of the control-plane data + receipts.
set -euo pipefail
APP_DIR="${APP_DIR:-/opt/camelot/bifrost-hub}"
BACKUP_DIR="${BACKUP_DIR:-/opt/camelot/backups}"
RECIPIENT="/root/.config/age/bifrost-recipient.txt"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"
# WAL databases must be checkpointed before a file-level copy, or the snapshot
# can mix WAL frames with a stale main DB file.
if [ -f "$APP_DIR/data/receipts.db" ]; then
  sqlite3 "$APP_DIR/data/receipts.db" "PRAGMA wal_checkpoint(TRUNCATE);" >/dev/null
fi
tar -C "$APP_DIR" -czf - data receipts \
  | age -R "$RECIPIENT" \
  > "$BACKUP_DIR/bifrost-$STAMP.tgz.age"
find "$BACKUP_DIR" -name 'bifrost-*.tgz.age' -mtime +30 -delete
SH
chmod +x /usr/local/bin/camelot-backup

# systemd timer: nightly backup at 03:17 UTC
cat > /etc/systemd/system/camelot-backup.service <<'UNIT'
[Unit]
Description=Camelot Bifrost Hub encrypted backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/camelot-backup
UNIT
cat > /etc/systemd/system/camelot-backup.timer <<'UNIT'
[Unit]
Description=Nightly Camelot Bifrost Hub backup

[Timer]
OnCalendar=*-*-* 03:17:00
Persistent=true

[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now camelot-backup.timer

log "Phase 6/6 — receipt service (systemd unit + SQLite WAL init)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/init-receipt-db.sh" ]; then
  install -m 0755 "$SCRIPT_DIR/init-receipt-db.sh" /usr/local/bin/camelot-init-receipt-db
  APP_DIR="$APP_DIR" ANCHOR_INTERVAL="${ANCHOR_INTERVAL:-1000}" \
    /usr/local/bin/camelot-init-receipt-db
else
  echo "  ⚠ init-receipt-db.sh not next to bootstrap.sh — skipping DB init"
fi
if [ -f "$SCRIPT_DIR/receipt-service.service" ]; then
  install -m 0644 "$SCRIPT_DIR/receipt-service.service" /etc/systemd/system/receipt-service.service
  systemctl daemon-reload
  systemctl enable receipt-service.service
  echo "  unit installed + enabled — stays inactive until the binary exists"
  echo "  (ConditionPathExists=/opt/camelot/bifrost-hub/bin/receipt-service)"
else
  echo "  ⚠ receipt-service.service not next to bootstrap.sh — skipping unit install"
fi

log "Bootstrap complete."
echo "  Tailscale IP : $TS_IP  (set ssh HostName of 'oci-admin-ts' to this)"
echo "  Public IP    : for bootstrap only; public SSH is now blocked"
echo "  Backup key   : $AGE_KEY  (recipient: $AGE_RECIPIENT) — back this key up offline!"
echo "  Test backup  : sudo /usr/local/bin/camelot-backup"
echo "  Restore      : age -d backup.tgz.age | tar -xzf - -C /tmp/restore"
echo "  Receipt svc  : deploy the binary to /opt/camelot/bifrost-hub/bin/receipt-service,"
echo "                 then: sudo systemctl restart receipt-service"
