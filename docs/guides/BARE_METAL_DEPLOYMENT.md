# CAMELOT-OS Bare-Metal Deployment Guide

**Corrected Approach**: Private, On-Premise, QR Pill Orchestration  
**Date**: 2026-06-18  
**Target**: 3-node bare-metal cluster (self-hosted infrastructure)  
**Philosophy**: Enterprise-grade, low-resource, zero cloud dependency

---

## Overview

CAMELOT-OS deploys to **your private infrastructure** using **QR Pill orchestrator** (Docker-free, systemd-native).

```
Your Private Servers (3 nodes)
         ↓
QR Pill Deployment Script
         ↓
Systemd Units (native OS)
         ↓
CAMELOT-OS Services
         ↓
Enterprise System (fully independent)
```

**No AWS. No cloud costs. No vendor lock-in.**

---

## Prerequisites

### Hardware Requirements

Per node:
- **CPU**: 4+ cores
- **RAM**: 8GB minimum
- **Storage**: 100GB SSD
- **Network**: Gigabit Ethernet

Example configurations:
- **Option 1**: Physical servers (Dell, HP, Lenovo)
- **Option 2**: Virtual machines (KVM, Proxmox, vSphere)
- **Option 3**: Colocation facility
- **Option 4**: On-premise Kubernetes cluster

### Network Requirements

- **Private network**: 10.0.0.0/8 or 192.168.0.0/16
- **3 static IPs**: One per node
- **Firewall rules**:
  - Port 8443 (Consensus) — between nodes
  - Port 6379 (Redis) — between nodes
  - Port 8400-8410 (Agents) — between nodes
  - Port 8000 (Metrics) — for monitoring
  - Port 22 (SSH) — for admin

### Software Requirements

- **OS**: Ubuntu 22.04 LTS or equivalent
- **Python**: 3.10+
- **systemd**: Latest
- **Git**: Latest
- **curl, wget, net-tools**: Standard utilities

---

## Step 1: Prepare Nodes

### Setup Each Node

```bash
# Login to node 1
ssh root@192.168.1.10

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \
    python3.10 python3-pip \
    git curl wget \
    net-tools jq htop \
    systemd build-essential

# Verify Python
python3 --version
# Should be 3.10+
```

### Clone CAMELOT-OS

```bash
# On node 1 (repeat for nodes 2 & 3)
mkdir -p /opt/camelot
cd /opt/camelot

git clone https://github.com/camelot/camelot-os.git
cd camelot-os

# Install Python dependencies
pip3 install -r requirements.txt
pip3 install prometheus-client jaeger-client
```

---

## Step 2: Deploy QR Pill

### Create Deployment Configuration

On node 1:

```bash
cat > /tmp/deploy.env <<'EOF'
NODE_ID="node_1"
CLUSTER_NODES="192.168.1.10,192.168.1.11,192.168.1.12"
ENVIRONMENT="production"
QR_PILL_MODE="systemd"
METRICS_ENABLED="true"
EOF

chmod 600 /tmp/deploy.env
```

### Run QR Pill Deployment

```bash
# On node 1
bash /opt/camelot/camelot-os/terraform/scripts/qr_pill_deploy.sh

# This will:
# ├─ Phase 1-2: Install system + CAMELOT-OS
# ├─ Phase 3-4: Configure + deploy services
# ├─ Phase 5-6: Start services + health checks
# ├─ Phase 7-9: Setup observability + backup
# └─ Time: ~8 minutes
```

### Repeat for Nodes 2 & 3

```bash
# On node 2
ssh root@192.168.1.11
cat > /tmp/deploy.env <<'EOF'
NODE_ID="node_2"
CLUSTER_NODES="192.168.1.10,192.168.1.11,192.168.1.12"
ENVIRONMENT="production"
QR_PILL_MODE="systemd"
METRICS_ENABLED="true"
EOF

bash /opt/camelot/camelot-os/terraform/scripts/qr_pill_deploy.sh

# Repeat on node 3 (192.168.1.12, NODE_ID="node_3")
```

---

## Step 3: Verify Cluster Formation

### Check Services on Each Node

```bash
# SSH to node 1
ssh root@192.168.1.10

# Verify all services are running
systemctl status camelot-consensus
systemctl status camelot-sync
systemctl status camelot-agents
systemctl status camelot-metrics

# Expected: all "active (running)"
```

### Check Logs

```bash
# View consensus logs
journalctl -u camelot-consensus -f

# Should show:
# [14:32:15] Consensus initialized (node_1)
# [14:32:16] Joining cluster: node_1, node_2, node_3
# [14:32:18] Leader elected: node_1
```

### Verify Cluster Health

```bash
# Check consensus
curl http://localhost:8443/health

# Expected output:
# {"status": "healthy", "role": "leader"}

# Check metrics
curl http://localhost:8000/metrics | grep camelot_consensus_proposals_total

# Check redis connectivity
redis-cli -h 127.0.0.1 -p 6379 ping
# Should return: PONG
```

---

## Step 4: Setup Observability (Local)

### Option A: On Your Workstation

If you have Docker available on your admin workstation:

```bash
# On your local machine
cd observability/
docker-compose up -d

# Access dashboards:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin123)
# Jaeger: http://localhost:16686
```

### Option B: On a Dedicated Monitoring Node

```bash
# On a 4th node or workstation:
ssh root@192.168.1.20

# Install Docker
apt-get install -y docker.io docker-compose

# Clone CAMELOT-OS
git clone https://github.com/camelot/camelot-os.git

# Start observability stack
cd camelot-os/observability
docker-compose up -d

# Configure Prometheus to scrape your 3 nodes
# Edit prometheus.yml:
# - Update targets to 192.168.1.10:8000, 192.168.1.11:8000, 192.168.1.12:8000
# - Restart: docker-compose restart prometheus
```

### Option C: Pure Prometheus (No Docker)

```bash
# On your monitoring server
apt-get install -y prometheus grafana-server

# Configure Prometheus
cat > /etc/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'camelot-node-1'
    static_configs:
      - targets: ['192.168.1.10:8000']
  
  - job_name: 'camelot-node-2'
    static_configs:
      - targets: ['192.168.1.11:8000']
  
  - job_name: 'camelot-node-3'
    static_configs:
      - targets: ['192.168.1.12:8000']
EOF

systemctl restart prometheus
systemctl restart grafana-server
```

---

## Step 5: Configure High Availability

### Setup Redis Cluster (Local Network)

Each node already includes local Redis. To cluster them:

```bash
# On node 1
redis-cli --cluster create \
  192.168.1.10:6379 \
  192.168.1.11:6379 \
  192.168.1.12:6379 \
  --cluster-replicas 1
```

### Setup Qdrant Cluster (Optional L1.5)

```bash
# Deploy Qdrant on a separate server or use cloud instance
# Configure knowledge sync to connect:
# Edit /opt/camelot/config/node.conf:
# [knowledge_sync]
# qdrant_url = http://192.168.1.30:6333
```

---

## Day-2 Operations

### Restart All Services

```bash
# On each node
systemctl restart camelot-consensus
systemctl restart camelot-sync
systemctl restart camelot-agents

# Wait 10 seconds for cluster to stabilize
sleep 10

# Verify
systemctl status camelot-consensus
```

### View Service Logs

```bash
# Real-time consensus logs
journalctl -u camelot-consensus -f

# Last 50 lines of sync
journalctl -u camelot-sync -n 50

# All errors
journalctl -p err -u camelot-agents
```

### Backup Data

```bash
# Manual backup (runs daily via cron)
/opt/camelot/bin/backup.sh

# Verify
ls -la /opt/camelot/backups/
```

### Monitoring

```bash
# Check resource usage
systemd-cgtop

# Monitor CPU/memory per service
ps aux | grep camelot

# Network connectivity
netstat -tlnp | grep camelot

# Disk usage
df -h /opt/camelot
```

---

## Scaling Operations

### Add a 4th Node

```bash
# Prepare new server (192.168.1.13)
ssh root@192.168.1.13
apt-get install -y python3.10 python3-pip git curl net-tools

# Clone and deploy
git clone https://github.com/camelot/camelot-os.git /opt/camelot/camelot-os

# Update cluster nodes list
cat > /tmp/deploy.env <<'EOF'
NODE_ID="node_4"
CLUSTER_NODES="192.168.1.10,192.168.1.11,192.168.1.12,192.168.1.13"
ENVIRONMENT="production"
EOF

# Deploy
bash /opt/camelot/camelot-os/terraform/scripts/qr_pill_deploy.sh

# Consensus automatically handles new node joining
```

### Remove a Node

```bash
# Graceful shutdown on node 4
ssh root@192.168.1.13
systemctl stop camelot-consensus
systemctl stop camelot-sync
systemctl stop camelot-agents

# Cluster rebalances automatically
# Node 4 can now be powered down
```

---

## Disaster Recovery

### Daily Backups (Automatic)

```bash
# Cron job created by QR Pill deployment
0 3 * * * /opt/camelot/bin/backup.sh

# Backups stored in: /opt/camelot/backups/
```

### Manual Full Backup

```bash
# On each node
tar czf /opt/camelot/backups/manual-backup-$(date +%Y%m%d).tar.gz \
  /opt/camelot/data \
  /opt/camelot/config
```

### Restore from Backup

```bash
# Stop services
systemctl stop camelot-consensus camelot-sync camelot-agents

# Restore
tar xzf /opt/camelot/backups/backup_20260618_030000/data.tar.gz -C /

# Restart
systemctl start camelot-consensus
systemctl start camelot-sync
systemctl start camelot-agents
```

### Node Recovery

If a node fails:

```bash
# On the failed node
ssh root@192.168.1.11

# Check if still accessible
systemctl status camelot-consensus

# If services are down, restart
systemctl restart camelot-consensus
systemctl restart camelot-sync
systemctl restart camelot-agents

# If hardware is dead, provision new server with same IP
# Run deployment script
bash /opt/camelot/camelot-os/terraform/scripts/qr_pill_deploy.sh
```

---

## Resource Usage

### Typical Per-Node Footprint

```
CPU:     20-30% (idle), 50-70% (under load)
RAM:     2.5-3.5 GB
Disk:    100 GB (50% system, 50% data)
Network: 10-50 Mbps (depends on load)
```

### Cost Comparison

```
AWS (3x t3.2xlarge):        $1,025/month
Your Hardware (CAPEX):      ~$5,000 (one-time)
                            + ~$300/month (power, cooling, space)

Break-even point: ~5 months
Then: 60-80% cost savings vs. cloud
```

---

## Security Hardening

### Enable TLS Between Nodes

Already configured by QR Pill:

```bash
# TLS certificates in /etc/camelot/tls/
ls -la /etc/camelot/tls/

# Verify TLS is enabled
curl -k https://192.168.1.10:8443/health
```

### Firewall Rules

```bash
# On each node
ufw enable
ufw allow ssh
ufw allow 8443/tcp from 192.168.1.0/24  # Consensus
ufw allow 6379/tcp from 192.168.1.0/24  # Redis
ufw allow 8400:8410/tcp from 192.168.1.0/24  # Agents
ufw allow 8000/tcp from 192.168.1.0/24  # Metrics
```

### Secrets Management

```bash
# Never store secrets in code
# Use environment variables:
export CAMELOT_SECRET_KEY=$(openssl rand -base64 32)

# Or use a secrets manager:
apt-get install vault
# Configure Vault to distribute secrets
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check status
systemctl status camelot-consensus

# View detailed error
journalctl -u camelot-consensus -p err -n 20

# Common issues:
# - Port already in use: netstat -tlnp | grep 8443
# - Missing dependencies: pip3 install -r requirements.txt
# - File permissions: chown camelot:camelot /opt/camelot/data
```

### Cluster Not Forming

```bash
# Check network connectivity
ping 192.168.1.11
ping 192.168.1.12

# Verify consensus on all nodes
for node in 192.168.1.{10,11,12}; do
  echo "Node: $node"
  curl -s http://$node:8443/health | jq .
done

# Check logs for errors
journalctl -u camelot-consensus -p err -f
```

### High Memory Usage

```bash
# Check memory per service
ps aux | grep camelot | awk '{print $6, $11}'

# If one service is leaking:
systemctl restart camelot-sync  # Example: restart sync

# Check for large data files
du -sh /opt/camelot/data/*

# Clean old backups if needed
rm /opt/camelot/backups/backup_2026-05-* -rf
```

---

## Deployment Checklist

- [ ] 3 physical/virtual servers ready
- [ ] Network configured (static IPs, firewall rules)
- [ ] Ubuntu 22.04 installed on all nodes
- [ ] SSH keys configured (passwordless login)
- [ ] Python 3.10+ installed
- [ ] QR Pill deployment script run on all 3 nodes
- [ ] All services healthy (systemctl status)
- [ ] Cluster formation verified (curl health endpoints)
- [ ] Observability running (Prometheus scraping)
- [ ] Backup cron job active
- [ ] Firewall rules applied
- [ ] Team trained on systemctl commands
- [ ] Runbooks documented
- [ ] Disaster recovery procedures tested

---

## Production Deployment Command

```bash
# SSH to node 1
ssh root@192.168.1.10

# Verify prerequisites
python3 --version  # Must be 3.10+
systemctl --version

# Run deployment
bash /opt/camelot/camelot-os/terraform/scripts/qr_pill_deploy.sh

# Monitor progress
tail -f /var/log/camelot-deployment.log

# Wait ~8 minutes, then verify
systemctl status camelot-consensus
curl http://localhost:8000/metrics
```

---

## Support & Resources

- **Logs**: `journalctl -u camelot-*`
- **Documentation**: `/opt/camelot/camelot-os/OPERATIONS_MANUAL.md`
- **Runbooks**: `/opt/camelot/camelot-os/terraform/INFRASTRUCTURE_GUIDE.md`
- **Monitoring**: Prometheus/Grafana on your monitoring server

---

## Summary

CAMELOT-OS on bare-metal is:

✅ **Independent** — No cloud vendor, full control  
✅ **Low-resource** — Runs on commodity hardware  
✅ **Enterprise-grade** — Byzantine consensus, distributed sync  
✅ **Fully automated** — QR Pill handles all setup  
✅ **Self-healing** — systemd auto-restart, fault tolerance  
✅ **Observable** — Prometheus, Grafana, Jaeger integration  

**Deployment time**: ~24 minutes (3 nodes × 8 minutes)  
**Cost**: ~$300/month (operating) vs. $1,025/month (cloud)  
**Vendor lock-in**: Zero  

---

**🚀 Ready for bare-metal deployment to your private infrastructure.**
