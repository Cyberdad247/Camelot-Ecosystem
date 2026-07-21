# CAMELOT-OS Deployment Quick Start

**Automated 3-node bare-metal cluster deployment using QR Pill orchestrator**

---

## Prerequisites

```bash
# On your workstation/control node:
✓ SSH access to 3 nodes
✓ SSH key configured (default: ~/.ssh/camelot_deploy)
✓ Ubuntu 22.04 LTS on each node
✓ 4+ CPU, 8GB RAM, 100GB SSD per node
✓ Network connectivity between nodes
✓ Root or sudo access on target nodes
```

---

## Quick Start (< 30 minutes)

### 1. Prepare SSH Access

```bash
# Generate SSH key (if not already done)
ssh-keygen -t ed25519 -f ~/.ssh/camelot_deploy -N ""

# Copy key to each node
for node in 192.168.1.{10,11,12}; do
    ssh-copy-id -i ~/.ssh/camelot_deploy root@$node
done

# Verify access
ssh -i ~/.ssh/camelot_deploy root@192.168.1.10 "echo 'SSH OK'"
```

### 2. Run Deployment Script

```bash
# From CAMELOT-OS directory
chmod +x deploy_cluster.sh

# Deploy 3-node cluster (parallel)
./deploy_cluster.sh \
    --nodes 192.168.1.10,192.168.1.11,192.168.1.12 \
    --environment production

# Or sequential deployment (safer for low-resource networks)
./deploy_cluster.sh \
    --nodes 192.168.1.10,192.168.1.11,192.168.1.12 \
    --environment production \
    --no-parallel
```

### 3. Monitor Deployment

```bash
# Watch deployment logs in real-time
tail -f deployment_logs/deployment_*.log

# Or SSH to node and watch services
ssh root@192.168.1.10
journalctl -u camelot-consensus -f
```

### 4. Verify Cluster

```bash
# Check all nodes are healthy
for node in 192.168.1.{10,11,12}; do
    echo "Node: $node"
    ssh root@$node "systemctl status camelot-consensus | grep Active"
done

# Check cluster formation
ssh root@192.168.1.10 "curl -s http://localhost:8443/health | jq ."
```

---

## Deployment Script Usage

```bash
./deploy_cluster.sh [options]

Options:
  --nodes IPS                    Node IPs (comma-separated) [REQUIRED]
  --user USER                    SSH user (default: root)
  --key PATH                     SSH key path (default: ~/.ssh/camelot_deploy)
  --environment ENV              Environment (default: production)
  --no-parallel                  Deploy nodes sequentially
  --skip-validation              Skip pre-deployment checks
  --verbose                      Show detailed output
```

### Examples

**Parallel deployment (fast):**
```bash
./deploy_cluster.sh --nodes 192.168.1.10,192.168.1.11,192.168.1.12
```

**Sequential deployment (safe):**
```bash
./deploy_cluster.sh \
    --nodes 192.168.1.10,192.168.1.11,192.168.1.12 \
    --no-parallel
```

**Staging environment:**
```bash
./deploy_cluster.sh \
    --nodes 10.0.0.10,10.0.0.11,10.0.0.12 \
    --environment staging \
    --no-parallel
```

**Custom SSH key:**
```bash
./deploy_cluster.sh \
    --nodes 192.168.1.10,192.168.1.11,192.168.1.12 \
    --key ~/.ssh/my_camelot_key
```

---

## What the Script Does

### Per Node (8 minutes each)

```
Phase 1: System Preparation
├─ Update apt packages
├─ Install Python 3.10, git, curl, systemd, etc.
└─ Verify system prerequisites

Phase 2: Installing CAMELOT-OS
├─ Clone CAMELOT-OS repository
├─ Install Python dependencies
└─ Setup CAMELOT directory structure

Phase 3: Configuration
├─ Create node configuration (/opt/camelot/config/node.conf)
├─ Generate TLS certificates
└─ Setup directories (data, logs, metrics)

Phase 4: Deploy Services (QR Pill Mode: systemd)
├─ Create camelot-consensus.service
├─ Create camelot-sync.service
├─ Create camelot-agents.service
├─ Create camelot-metrics.service
└─ Reload systemd daemon

Phase 5: Start Services
├─ systemctl start camelot-consensus
├─ systemctl start camelot-sync
├─ systemctl start camelot-agents
└─ systemctl start camelot-metrics

Phase 6: Health Checks
├─ Verify services are running
├─ Check for errors in logs
└─ Report status

Phase 7: Enable on Boot
└─ systemctl enable all services
```

---

## Deployment Timeline

```
Parallel Deployment (3 nodes simultaneously):
├─ T+0min:   Validation & setup
├─ T+1min:   Node 1 deployment starts
├─ T+1min:   Node 2 deployment starts
├─ T+1min:   Node 3 deployment starts
├─ T+9min:   Node 1 deployment complete
├─ T+9min:   Node 2 deployment complete
├─ T+9min:   Node 3 deployment complete
├─ T+10min:  Cluster verification
└─ T+11min:  Deployment complete

Sequential Deployment (nodes one-by-one):
├─ T+0min:   Validation & setup
├─ T+1min:   Node 1 deployment starts
├─ T+9min:   Node 1 complete
├─ T+14min:  Node 2 deployment starts
├─ T+22min:  Node 2 complete
├─ T+27min:  Node 3 deployment starts
├─ T+35min:  Node 3 complete
├─ T+36min:  Cluster verification
└─ T+37min:  Deployment complete
```

---

## Logs and Output

### Deployment Log File

```bash
# Log files stored in ./deployment_logs/
ls -la deployment_logs/

# Example: deployment_20260618_164500.log
tail -f deployment_logs/deployment_*.log
```

### Status Report

```bash
# JSON status file created after deployment
cat deployment_logs/deployment_status.json

# Output:
# {
#   "timestamp": "2026-06-18T16:45:00+00:00",
#   "environment": "production",
#   "nodes": "192.168.1.10,192.168.1.11,192.168.1.12",
#   "deployment_log": "./deployment_logs/deployment_20260618_164500.log",
#   "status": "complete"
# }
```

---

## Post-Deployment Verification

### Check Services on All Nodes

```bash
# Script automatically verifies, but you can verify manually:
for node in 192.168.1.{10,11,12}; do
    echo "=== Node: $node ==="
    ssh root@$node "systemctl status camelot-consensus | grep Active"
    ssh root@$node "systemctl status camelot-agents | grep Active"
done
```

### Check Metrics

```bash
# On node 1
ssh root@192.168.1.10 "curl -s http://localhost:8000/metrics | head -20"

# Expected: Prometheus metrics for consensus, sync, agents, system
```

### Check Cluster Formation

```bash
# Verify leader election
for node in 192.168.1.{10,11,12}; do
    echo "Node: $node"
    ssh root@$node "curl -s http://localhost:8443/health" | jq .
done

# Expected: One leader (role: "leader"), two followers (role: "follower")
```

### Check Network Connectivity

```bash
# Between nodes
ssh root@192.168.1.10 "ping -c 3 192.168.1.11 && ping -c 3 192.168.1.12"

# Should show 0% packet loss
```

---

## Troubleshooting

### Deployment Fails on Node

```bash
# Check SSH access
ssh -i ~/.ssh/camelot_deploy root@192.168.1.10 "echo OK"

# Check disk space
ssh root@192.168.1.10 "df -h /opt"

# Check Python
ssh root@192.168.1.10 "python3 --version"

# Check recent logs
ssh root@192.168.1.10 "journalctl -u camelot-consensus -p err -n 20"
```

### Service Won't Start

```bash
# On the node
ssh root@192.168.1.10

# Check service status
systemctl status camelot-consensus

# View detailed error
journalctl -u camelot-consensus -p err -f

# Try restarting
systemctl restart camelot-consensus
```

### Cluster Not Forming

```bash
# Check all nodes can reach each other
for node in 192.168.1.{10,11,12}; do
    ssh root@$node "ping -c 1 192.168.1.10 && ping -c 1 192.168.1.11 && ping -c 1 192.168.1.12"
done

# Check firewall (if enabled)
ssh root@192.168.1.10 "ufw status"

# If firewall is on, allow consensus port
ssh root@192.168.1.10 "ufw allow 8443/tcp from 192.168.1.0/24"
```

### High Memory Usage

```bash
# Check memory per service
ssh root@192.168.1.10 "ps aux | grep camelot | awk '{print \$6, \$11}'"

# Restart if needed
ssh root@192.168.1.10 "systemctl restart camelot-sync"
```

---

## Next Steps After Deployment

### 1. Setup Observability

```bash
# On your monitoring server/workstation:
cd observability/
docker-compose up -d

# Or install Prometheus + Grafana manually
apt-get install -y prometheus grafana-server

# Access dashboards:
# Prometheus: http://your-monitoring-server:9090
# Grafana: http://your-monitoring-server:3000 (admin/admin123)
```

### 2. Configure Monitoring

```bash
# Update prometheus.yml with your node IPs
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
```

### 3. Test Failover

```bash
# On node 1, stop consensus
ssh root@192.168.1.10 "systemctl stop camelot-consensus"

# Watch node 2 or 3 take over as leader
ssh root@192.168.1.11 "journalctl -u camelot-consensus -f | grep -i leader"

# Restart node 1
ssh root@192.168.1.10 "systemctl start camelot-consensus"

# Verify cluster recovers
ssh root@192.168.1.10 "curl -s http://localhost:8443/health" | jq .
```

---

## Success Criteria

✅ Deployment complete when:
- All 3 nodes report "active (running)" for all services
- Cluster health endpoint shows 1 leader, 2 followers
- Metrics flowing to Prometheus (8000+ metrics on first scrape)
- No error messages in logs
- Network latency between nodes < 100ms

---

## Support

**Deployment issues?**
- Check logs: `tail -f deployment_logs/deployment_*.log`
- Verify SSH: `ssh -i ~/.ssh/camelot_deploy root@<node>`
- Run script with `--verbose` for more detail
- Manually SSH and check systemctl/journalctl

**Script improvement feedback:**
- Update `deploy_cluster.sh` with your adjustments
- Keep logs for post-deployment analysis
- Report any recurring issues

---

**Ready to deploy?**

```bash
./deploy_cluster.sh --nodes 192.168.1.10,192.168.1.11,192.168.1.12
```

**Estimated time: 10-40 minutes** (depending on parallel vs. sequential)
