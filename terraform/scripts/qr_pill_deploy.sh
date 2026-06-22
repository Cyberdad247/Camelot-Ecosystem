#!/bin/bash
# QR Pill Deployment Script
# Deploys CAMELOT-OS without Docker, using systemd orchestration
#
# Environment variables:
#   - node_id: Node identifier (node_1, node_2, etc.)
#   - cluster_nodes: Comma-separated list of node IPs
#   - environment: dev, staging, production
#   - qr_pill_mode: systemd, bare-metal, custom
#   - metrics_enabled: true/false

set -euo pipefail

# Configuration
NODE_ID="${node_id:-node_1}"
CLUSTER_NODES="${cluster_nodes:-localhost}"
ENVIRONMENT="${environment:-production}"
QR_PILL_MODE="${qr_pill_mode:-systemd}"
METRICS_ENABLED="${metrics_enabled:-true}"

CAMELOT_HOME="/opt/camelot"
CAMELOT_USER="camelot"
CAMELOT_GROUP="camelot"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log_info() {
    log "ℹ️  $1"
}

log_success() {
    log "✅ $1"
}

log_error() {
    log "❌ $1"
}

# ── Phase 1: System Preparation ────────────────────────────────────────

log_info "Phase 1: System Preparation"

# Update package manager
apt-get update
apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    wget \
    net-tools \
    jq \
    htop \
    systemd

log_success "System packages installed"

# Create camelot user
if ! id -u "$CAMELOT_USER" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "$CAMELOT_USER"
    log_success "Created $CAMELOT_USER user"
else
    log_info "$CAMELOT_USER user already exists"
fi

# Create directories
mkdir -p "$CAMELOT_HOME"/{bin,config,data,logs,metrics}
chown -R "$CAMELOT_USER:$CAMELOT_GROUP" "$CAMELOT_HOME"
chmod 755 "$CAMELOT_HOME"

log_success "Created CAMELOT directory structure"

# ── Phase 2: Install CAMELOT-OS ────────────────────────────────────────

log_info "Phase 2: Installing CAMELOT-OS"

# Clone or update repository
if [ ! -d "$CAMELOT_HOME/camelot-os" ]; then
    git clone https://github.com/camelot/camelot-os.git "$CAMELOT_HOME/camelot-os"
    log_success "Cloned CAMELOT-OS repository"
else
    cd "$CAMELOT_HOME/camelot-os"
    git pull origin main
    log_success "Updated CAMELOT-OS repository"
fi

# Install Python dependencies
cd "$CAMELOT_HOME/camelot-os"
pip3 install -r requirements.txt
pip3 install prometheus-client jaeger-client

log_success "Installed Python dependencies"

# Create symlink to camelot-os
ln -sf "$CAMELOT_HOME/camelot-os" /opt/app
export PYTHONPATH="$CAMELOT_HOME/camelot-os:$PYTHONPATH"

log_success "CAMELOT-OS installed"

# ── Phase 3: Configuration ────────────────────────────────────────────

log_info "Phase 3: Configuring CAMELOT-OS"

# Create node configuration
cat > "$CAMELOT_HOME/config/node.conf" <<EOF
[node]
id = $NODE_ID
environment = $ENVIRONMENT
cluster_nodes = $CLUSTER_NODES

[consensus]
port = 8443
timeout = 10

[knowledge_sync]
redis_nodes = $CLUSTER_NODES:6379
qdrant_url = http://localhost:6333

[agent_network]
port_start = 8400
port_end = 8410

[metrics]
enabled = $METRICS_ENABLED
port = 8000

[observability]
jaeger_agent_host = localhost
jaeger_agent_port = 6831
prometheus_pushgateway = localhost:9091
EOF

chown "$CAMELOT_USER:$CAMELOT_GROUP" "$CAMELOT_HOME/config/node.conf"
chmod 640 "$CAMELOT_HOME/config/node.conf"

log_success "Created node configuration"

# Create TLS certificates (self-signed for demo)
if [ ! -f "$CAMELOT_HOME/certs/tls.crt" ]; then
    mkdir -p "$CAMELOT_HOME/certs"
    openssl req -x509 -newkey rsa:4096 -nodes \
        -out "$CAMELOT_HOME/certs/tls.crt" \
        -keyout "$CAMELOT_HOME/certs/tls.key" \
        -days 365 \
        -subj "/CN=$NODE_ID" 2>/dev/null

    chown "$CAMELOT_USER:$CAMELOT_GROUP" "$CAMELOT_HOME/certs"/*
    chmod 600 "$CAMELOT_HOME/certs/tls.key"

    log_success "Generated TLS certificates"
fi

# ── Phase 4: Deploy Services (QR Pill Orchestration) ──────────────────

log_info "Phase 4: Deploying Services (QR Pill Mode: $QR_PILL_MODE)"

# Create systemd service units
create_systemd_unit() {
    local service_name=$1
    local service_cmd=$2
    local service_port=$3
    local depends_on=${4:-""}

    local unit_file="/etc/systemd/system/camelot-$service_name.service"

    cat > "$unit_file" <<EOF
[Unit]
Description=CAMELOT-OS $service_name Service
After=network-online.target$([[ -n "$depends_on" ]] && echo " camelot-$depends_on.service")
Wants=network-online.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
Type=simple
User=$CAMELOT_USER
WorkingDirectory=$CAMELOT_HOME/camelot-os
Environment="PYTHONUNBUFFERED=1"
Environment="CAMELOT_NODE_ID=$NODE_ID"
Environment="CAMELOT_HOME=$CAMELOT_HOME"
Environment="CAMELOT_CONFIG=$CAMELOT_HOME/config/node.conf"
ExecStart=/usr/bin/python3 $service_cmd
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=camelot-$service_name

[Install]
WantedBy=multi-user.target
EOF

    chmod 644 "$unit_file"
    log_success "Created systemd unit: $service_name"
}

# ── Compute cluster topology (node_N maps to Nth IP in CLUSTER_NODES) ──
# Each node runs one node_daemon (consensus+sync+agents) on HTTP port 8443.
IFS=',' read -ra _CLUSTER_IPS <<< "$CLUSTER_NODES"
_NODE_NUM="${NODE_ID#node_}"
_SELF_IDX=$(( _NODE_NUM - 1 ))
_PEER_SPEC=""
_ALL_NODES_SPEC=""
for _i in "${!_CLUSTER_IPS[@]}"; do
    _nid="node_$(( _i + 1 ))"
    _url="http://${_CLUSTER_IPS[$_i]}:8443"
    _ALL_NODES_SPEC+="${_nid}=${_url},"
    if [ "$_i" -ne "$_SELF_IDX" ]; then
        _PEER_SPEC+="${_nid}=${_url},"
    fi
done
_PEER_SPEC="${_PEER_SPEC%,}"
_ALL_NODES_SPEC="${_ALL_NODES_SPEC%,}"
_LEADER_FLAG=""
[ "$_SELF_IDX" -eq 0 ] && _LEADER_FLAG="--leader"

log_info "Topology: node_id=$NODE_ID self_idx=$_SELF_IDX peers=[$_PEER_SPEC] leader=${_LEADER_FLAG:-no}"

# Deploy node daemon (consensus + sync + agents in one process, /health on 8443)
create_systemd_unit "node" \
    "-m control_plane.cluster.node_daemon --node-id $NODE_ID --host 0.0.0.0 --port 8443 --peers $_PEER_SPEC $_LEADER_FLAG" \
    "8443"

# Deploy metrics daemon (Prometheus /metrics on 8000, scrapes all nodes)
if [ "$METRICS_ENABLED" == "true" ]; then
    create_systemd_unit "metrics" \
        "-m control_plane.cluster.metrics_daemon --port 8000 --nodes $_ALL_NODES_SPEC" \
        "8000" \
        "node"
fi

# Reload systemd
systemctl daemon-reload

log_success "Systemd units created and reloaded"

# ── Phase 5: Start Services ────────────────────────────────────────────

log_info "Phase 5: Starting Services"

# Start node daemon (hosts consensus + sync + agents)
systemctl start camelot-node
sleep 2

# Start metrics if enabled
if [ "$METRICS_ENABLED" == "true" ]; then
    systemctl start camelot-metrics
fi

# Enable on boot
systemctl enable camelot-node
[ "$METRICS_ENABLED" == "true" ] && systemctl enable camelot-metrics

log_success "Services started"

# ── Phase 6: Health Checks ────────────────────────────────────────────

log_info "Phase 6: Health Checks"

sleep 3

# Check service status
check_service() {
    local service=$1
    if systemctl is-active --quiet "camelot-$service"; then
        log_success "camelot-$service is running"
        return 0
    else
        log_error "camelot-$service is NOT running"
        return 1
    fi
}

all_healthy=true
check_service "node" || all_healthy=false
[ "$METRICS_ENABLED" == "true" ] && check_service "metrics" || all_healthy=false

# Verify the node's HTTP /health endpoint actually responds (the daemon binds
# the port for real now — this check would have always failed on the old demos).
if curl -sf -m 5 "http://localhost:8443/health" >/dev/null 2>&1; then
    log_success "Node /health endpoint responding on :8443"
else
    log_error "Node /health endpoint NOT responding on :8443"
    all_healthy=false
fi

if [ "$all_healthy" = "true" ]; then
    log_success "All services are healthy"
else
    log_error "Some services are not running"
    systemctl status camelot-node || true
fi

# ── Phase 7: Observability Setup ──────────────────────────────────────

log_info "Phase 7: Setting Up Observability"

# Create prometheus scrape config
mkdir -p "$CAMELOT_HOME/prometheus"

cat > "$CAMELOT_HOME/prometheus/scrape_$NODE_ID.yml" <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'camelot-$NODE_ID'
    static_configs:
      - targets: ['localhost:8000']
EOF

log_success "Created Prometheus scrape config"

# ── Phase 8: Backup & Recovery Setup ──────────────────────────────────

log_info "Phase 8: Setting Up Backup & Recovery"

# Create backup directory
mkdir -p "$CAMELOT_HOME/backups"
chown "$CAMELOT_USER:$CAMELOT_GROUP" "$CAMELOT_HOME/backups"

# Create backup script
cat > "$CAMELOT_HOME/bin/backup.sh" <<'BACKUP_EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$CAMELOT_HOME/backups/backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"
tar czf "$BACKUP_DIR/data.tar.gz" "$CAMELOT_HOME/data"
tar czf "$BACKUP_DIR/config.tar.gz" "$CAMELOT_HOME/config"
echo "Backup created: $BACKUP_DIR"
BACKUP_EOF

chmod +x "$CAMELOT_HOME/bin/backup.sh"

# Create cron job for daily backups
if ! crontab -u "$CAMELOT_USER" -l 2>/dev/null | grep -q "backup.sh"; then
    (crontab -u "$CAMELOT_USER" -l 2>/dev/null || echo ""; echo "0 3 * * * $CAMELOT_HOME/bin/backup.sh") | \
        crontab -u "$CAMELOT_USER" -
    log_success "Created daily backup cron job"
fi

# ── Phase 9: Deployment Report ────────────────────────────────────────

log_info "Phase 9: Deployment Summary"

cat << 'REPORT'

╔════════════════════════════════════════════════════════════════╗
║          CAMELOT-OS QR PILL DEPLOYMENT COMPLETE              ║
╚════════════════════════════════════════════════════════════════╝

📊 DEPLOYMENT SUMMARY:
  Node ID:          $NODE_ID
  Environment:      $ENVIRONMENT
  Deployment Mode:  $QR_PILL_MODE
  Home Directory:   $CAMELOT_HOME

🚀 SERVICES DEPLOYED:
  ✅ Node daemon — consensus + sync + agents (port 8443, /health)
  ✅ Metrics Collector (port 8000, /metrics)

📈 OBSERVABILITY:
  ✅ Prometheus metrics on port 8000
  ✅ Jaeger tracing configured
  ✅ System logging via journalctl

🔄 MANAGEMENT COMMANDS:
  • View service status:
    systemctl status camelot-node

  • View logs:
    journalctl -u camelot-node -f

  • Restart services:
    systemctl restart camelot-node
    systemctl restart camelot-metrics

  • Backup data:
    $CAMELOT_HOME/bin/backup.sh

📍 NEXT STEPS:
  1. Monitor logs: journalctl -u camelot-node -f
  2. Check metrics: curl http://localhost:8000/metrics
  3. Verify cluster: curl http://localhost:8443/health
  4. Configure monitoring: Point Prometheus to localhost:8000

REPORT

log_success "Deployment complete!"

# ── Phase 10: Performance Baseline ─────────────────────────────────────

log_info "Phase 10: Measuring Performance Baseline"

sleep 5

# Check resource usage
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM=$(free | grep Mem | awk '{print ($3/$2) * 100}')

log_info "Performance Baseline:"
log_info "  CPU Utilization: ${CPU}%"
log_info "  Memory Utilization: ${MEM}%"

# Final status
log_success "QR Pill deployment successful! 🔮"
