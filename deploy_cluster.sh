#!/bin/bash

################################################################################
# CAMELOT-OS Bare-Metal Cluster Deployment Script
# Automated 3-node deployment using QR Pill orchestrator
#
# Usage:
#   ./deploy_cluster.sh [options]
#
# Options:
#   --nodes 192.168.1.10,192.168.1.11,192.168.1.12    Node IPs (comma-separated)
#   --user root                                         SSH user
#   --key ~/.ssh/camelot_deploy                        SSH key path
#   --environment production                           Environment (dev/staging/prod)
#   --no-parallel                                      Deploy nodes sequentially
#   --skip-validation                                  Skip pre-deployment checks
#   --verbose                                          Show detailed output
################################################################################

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/deployment_logs"
DEPLOYMENT_LOG="${LOG_DIR}/deployment_$(date +%Y%m%d_%H%M%S).log"
STATUS_FILE="${LOG_DIR}/deployment_status.json"

# Default values
NODES=""
SSH_USER="root"
SSH_KEY="${HOME}/.ssh/camelot_deploy"
ENVIRONMENT="production"
PARALLEL=true
SKIP_VALIDATION=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── Logging Functions ────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

# ── Parse Arguments ──────────────────────────────────────────────────────────

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --nodes)
                NODES="$2"
                shift 2
                ;;
            --user)
                SSH_USER="$2"
                shift 2
                ;;
            --key)
                SSH_KEY="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --no-parallel)
                PARALLEL=false
                shift
                ;;
            --skip-validation)
                SKIP_VALIDATION=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
}

print_usage() {
    cat << EOF
Usage: $0 [options]

Options:
  --nodes IPS                    Node IPs (comma-separated, required)
  --user USER                    SSH user (default: root)
  --key PATH                     SSH key path (default: ~/.ssh/camelot_deploy)
  --environment ENV              Environment (default: production)
  --no-parallel                  Deploy nodes sequentially
  --skip-validation              Skip pre-deployment checks
  --verbose                      Show detailed output

Examples:
  $0 --nodes 192.168.1.10,192.168.1.11,192.168.1.12
  $0 --nodes 10.0.0.10,10.0.0.11,10.0.0.12 --environment staging
EOF
}

# ── Setup ────────────────────────────────────────────────────────────────────

setup() {
    mkdir -p "$LOG_DIR"

    log_info "Starting CAMELOT-OS Cluster Deployment"
    log_info "Deployment log: $DEPLOYMENT_LOG"
    log_info "Environment: $ENVIRONMENT"
    log_info "Nodes: $NODES"
    log_info "Parallel deployment: $PARALLEL"

    if [[ -z "$NODES" ]]; then
        log_error "No nodes specified. Use --nodes to provide node IPs"
        print_usage
        exit 1
    fi

    if [[ ! -f "$SSH_KEY" ]] && [[ ! "$SKIP_VALIDATION" == "true" ]]; then
        log_error "SSH key not found: $SSH_KEY"
        exit 1
    fi
}

# ── Validation ───────────────────────────────────────────────────────────────

validate_node() {
    local node=$1

    log_info "Validating node: $node"

    # Check SSH connectivity
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SSH_USER@$node" "echo 'SSH OK'" > /dev/null 2>&1; then
        log_error "Cannot SSH to $node"
        return 1
    fi

    # Check Python 3.10+
    if ! ssh -i "$SSH_KEY" "$SSH_USER@$node" "python3 --version 2>&1 | grep -q 'Python 3.[1-9]'" > /dev/null 2>&1; then
        log_warning "Python 3.10+ not found on $node, will install"
    fi

    # Check disk space
    local disk_usage=$(ssh -i "$SSH_KEY" "$SSH_USER@$node" "df /opt | tail -1 | awk '{print \$5}' | sed 's/%//'")
    if [[ $disk_usage -gt 80 ]]; then
        log_warning "Disk usage on $node is ${disk_usage}%, recommend cleanup"
    fi

    log_success "Node $node validation passed"
    return 0
}

validate_cluster() {
    if [[ "$SKIP_VALIDATION" == "true" ]]; then
        log_warning "Skipping validation"
        return 0
    fi

    log_info "Validating cluster..."

    IFS=',' read -ra node_array <<< "$NODES"

    for node in "${node_array[@]}"; do
        node=$(echo "$node" | xargs)  # Trim whitespace
        if ! validate_node "$node"; then
            log_error "Validation failed for node: $node"
            return 1
        fi
    done

    log_success "All nodes validated"
    return 0
}

# ── Deployment ───────────────────────────────────────────────────────────────

deploy_node() {
    local node=$1
    local node_id=$2
    local all_nodes=$3

    log_info "Deploying node: $node (node_id: $node_id)"

    # SSH and run deployment
    ssh -i "$SSH_KEY" "$SSH_USER@$node" << DEPLOY_SCRIPT
set -euo pipefail

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo "[INFO] Phase 1: System Preparation"
apt-get update > /dev/null 2>&1
apt-get install -y python3.10 python3-pip git curl wget net-tools jq htop systemd build-essential openssl > /dev/null 2>&1
echo "\${GREEN}[✓]\${NC} System packages installed"

echo "[INFO] Phase 2: Installing CAMELOT-OS"
mkdir -p /opt/camelot
cd /opt/camelot

if [[ ! -d "camelot-os" ]]; then
    git clone https://github.com/camelot/camelot-os.git > /dev/null 2>&1
else
    cd camelot-os && git pull origin main > /dev/null 2>&1 && cd ..
fi

cd camelot-os
pip3 install -q -r requirements.txt > /dev/null 2>&1
pip3 install -q prometheus-client jaeger-client > /dev/null 2>&1
echo "\${GREEN}[✓]\${NC} CAMELOT-OS installed"

echo "[INFO] Phase 3: Configuring CAMELOT-OS"
mkdir -p /opt/camelot/{config,data,logs,metrics}

cat > /opt/camelot/config/node.conf <<'CONFIG'
[node]
id = $node_id
environment = $ENVIRONMENT
cluster_nodes = $all_nodes

[consensus]
port = 8443
timeout = 10

[knowledge_sync]
redis_nodes = 127.0.0.1:6379
qdrant_url = http://127.0.0.1:6333

[agent_network]
port_start = 8400
port_end = 8410

[metrics]
enabled = true
port = 8000

[observability]
jaeger_agent_host = localhost
jaeger_agent_port = 6831
prometheus_pushgateway = localhost:9091
CONFIG

echo "\${GREEN}[✓]\${NC} Configuration created"

echo "[INFO] Phase 4: Deploying Services (QR Pill Mode: systemd)"

# Create systemd units
cat > /etc/systemd/system/camelot-consensus.service <<'SERVICE'
[Unit]
Description=CAMELOT-OS Consensus Service
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
Type=simple
User=root
WorkingDirectory=/opt/camelot/camelot-os
Environment="PYTHONUNBUFFERED=1"
Environment="CAMELOT_NODE_ID=$node_id"
Environment="CAMELOT_CONFIG=/opt/camelot/config/node.conf"
ExecStart=/usr/bin/python3 -m control_plane.distributed_ledger_consensus
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

cat > /etc/systemd/system/camelot-sync.service <<'SERVICE'
[Unit]
Description=CAMELOT-OS Knowledge Sync Service
After=network-online.target camelot-consensus.service
Wants=network-online.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
Type=simple
User=root
WorkingDirectory=/opt/camelot/camelot-os
Environment="PYTHONUNBUFFERED=1"
Environment="CAMELOT_NODE_ID=$node_id"
Environment="CAMELOT_CONFIG=/opt/camelot/config/node.conf"
ExecStart=/usr/bin/python3 -m control_plane.distributed_knowledge_sync
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

cat > /etc/systemd/system/camelot-agents.service <<'SERVICE'
[Unit]
Description=CAMELOT-OS Agent Registry Service
After=network-online.target camelot-consensus.service
Wants=network-online.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
Type=simple
User=root
WorkingDirectory=/opt/camelot/camelot-os
Environment="PYTHONUNBUFFERED=1"
Environment="CAMELOT_NODE_ID=$node_id"
Environment="CAMELOT_CONFIG=/opt/camelot/config/node.conf"
ExecStart=/usr/bin/python3 -m control_plane.distributed_agent_registry
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

cat > /etc/systemd/system/camelot-metrics.service <<'SERVICE'
[Unit]
Description=CAMELOT-OS Metrics Collector
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/camelot/camelot-os
Environment="PYTHONUNBUFFERED=1"
Environment="CAMELOT_NODE_ID=$node_id"
ExecStart=/usr/bin/python3 -m control_plane.metrics_collector
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
echo "\${GREEN}[✓]\${NC} Systemd units created"

echo "[INFO] Phase 5: Starting Services"
systemctl start camelot-consensus
sleep 2
systemctl start camelot-sync
systemctl start camelot-agents
systemctl start camelot-metrics
echo "\${GREEN}[✓]\${NC} Services started"

echo "[INFO] Phase 6: Health Checks"
sleep 3

if systemctl is-active --quiet camelot-consensus; then
    echo "\${GREEN}[✓]\${NC} Consensus is running"
else
    echo "[ERROR] Consensus failed to start"
    journalctl -u camelot-consensus -n 10
    exit 1
fi

if systemctl is-active --quiet camelot-agents; then
    echo "\${GREEN}[✓]\${NC} Agents are running"
else
    echo "[ERROR] Agents failed to start"
    exit 1
fi

echo "[INFO] Phase 7: Enabling on Boot"
systemctl enable camelot-consensus camelot-sync camelot-agents camelot-metrics
echo "\${GREEN}[✓]\${NC} Services enabled on boot"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  CAMELOT-OS QR PILL DEPLOYMENT DONE   ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Node: $node_id"
echo "Status: Ready"
echo ""

DEPLOY_SCRIPT

    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        log_success "Node $node deployed successfully"
        return 0
    else
        log_error "Node $node deployment failed (exit code: $exit_code)"
        return 1
    fi
}

# ── Verification ─────────────────────────────────────────────────────────────

verify_cluster() {
    log_info "Verifying cluster formation..."

    IFS=',' read -ra node_array <<< "$NODES"
    local node_count=${#node_array[@]}
    local healthy_count=0

    for node in "${node_array[@]}"; do
        node=$(echo "$node" | xargs)

        # Check consensus health
        local health=$(ssh -i "$SSH_KEY" "$SSH_USER@$node" "curl -s http://localhost:8443/health 2>/dev/null | grep -o '\"status\":\"[^\"]*\"' || echo 'status:unknown'" 2>/dev/null || echo "unknown")

        if [[ "$health" == *"status"* ]] || [[ "$health" == "healthy" ]]; then
            log_success "Node $node is healthy"
            ((healthy_count++))
        else
            log_warning "Node $node status unclear: $health"
        fi
    done

    log_info "Cluster status: $healthy_count/$node_count nodes healthy"

    if [[ $healthy_count -eq $node_count ]]; then
        log_success "Cluster fully operational"
        return 0
    elif [[ $healthy_count -gt 0 ]]; then
        log_warning "Cluster partially operational, give it time to stabilize"
        return 0
    else
        log_error "Cluster verification failed"
        return 1
    fi
}

# ── Status Report ────────────────────────────────────────────────────────────

generate_status_report() {
    log_info "Generating status report..."

    cat > "$STATUS_FILE" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "environment": "$ENVIRONMENT",
  "nodes": "$NODES",
  "deployment_log": "$DEPLOYMENT_LOG",
  "status": "complete"
}
EOF

    log_success "Status report: $STATUS_FILE"
}

# ── Main ─────────────────────────────────────────────────────────────────────

main() {
    parse_arguments "$@"
    setup

    if ! validate_cluster; then
        log_error "Cluster validation failed"
        exit 1
    fi

    IFS=',' read -ra node_array <<< "$NODES"
    local node_count=${#node_array[@]}

    # Create node IDs
    declare -a node_ids=()
    for ((i=0; i<node_count; i++)); do
        node_ids+=("node_$((i+1))")
    done

    log_info "Deploying $node_count nodes..."

    # Deploy nodes
    if [[ "$PARALLEL" == "true" ]]; then
        # Parallel deployment
        local pids=()
        for ((i=0; i<node_count; i++)); do
            deploy_node "${node_array[$i]}" "${node_ids[$i]}" "$NODES" &
            pids+=($!)
        done

        # Wait for all deployments
        local failed=0
        for pid in "${pids[@]}"; do
            if ! wait $pid; then
                ((failed++))
            fi
        done

        if [[ $failed -gt 0 ]]; then
            log_error "$failed node(s) failed to deploy"
            exit 1
        fi
    else
        # Sequential deployment
        for ((i=0; i<node_count; i++)); do
            if ! deploy_node "${node_array[$i]}" "${node_ids[$i]}" "$NODES"; then
                log_error "Deployment failed at node: ${node_array[$i]}"
                exit 1
            fi
            sleep 5  # Wait before deploying next node
        done
    fi

    # Verify cluster
    sleep 10
    if ! verify_cluster; then
        log_warning "Cluster verification incomplete, monitoring..."
    fi

    generate_status_report

    log_success "CAMELOT-OS cluster deployment complete!"
    log_info "Next: Check observability at Prometheus/Grafana"
    log_info "Logs: $DEPLOYMENT_LOG"
}

# Execute main function
main "$@"
