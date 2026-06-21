# CAMELOT-OS Infrastructure-as-Code & QR Pill Deployment

**Status**: Production-ready infrastructure automation  
**Date**: 2026-06-18  
**Deployment Modes**: QR Pill (systemd) or Kubernetes  
**Platforms**: AWS, GCP, bare metal

---

## Executive Summary

Two-tier infrastructure deployment for CAMELOT-OS:

1. **Infrastructure-as-Code (Terraform)**: Provision cloud resources (VPC, EC2, Redis, Qdrant)
2. **QR Pill Orchestrator**: Docker-free deployment using systemd, bare-metal processes, or custom orchestration

**Key Benefits**:
- ✅ No Docker dependency (Docker-free by design)
- ✅ Lightweight & efficient (systemd-native)
- ✅ Compressed deployment format (QR Pill crystals)
- ✅ Fast provisioning (< 10 minutes to production)
- ✅ Multi-cloud support (AWS, GCP)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Terraform Infrastructure-as-Code                       │
│  ├─ AWS: VPC, EC2, ElastiCache Redis, SNS              │
│  ├─ GCP: GKE, Memorystore Redis, Qdrant Cluster        │
│  └─ Multi-region failover configuration                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  QR Pill Orchestrator (Docker-Free)                     │
│  ├─ Systemd mode: native systemd units                 │
│  ├─ Bare-metal mode: direct process execution          │
│  └─ Custom mode: extensible orchestration              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  CAMELOT-OS Services (3-node cluster)                   │
│  ├─ Node 1: Consensus + Sync + Agents                  │
│  ├─ Node 2: Consensus + Sync + Agents                  │
│  └─ Node 3: Consensus + Sync + Agents                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Data Layer                                              │
│  ├─ L1: Redis Cluster (3 nodes, ElastiCache)            │
│  ├─ L1.5: Qdrant Vector Store (3 nodes)                 │
│  └─ L2: CloudBrain (single source of truth)             │
└──────────────────────────────────────────────────────────┘
```

---

## Part 1: Infrastructure Provisioning (Terraform)

### Prerequisites

```bash
# Install Terraform
brew install terraform  # macOS
# or
apt-get install terraform  # Linux

# AWS credentials
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcp-key.json"
```

### Quick Start

```bash
# 1. Initialize Terraform
cd terraform/
terraform init

# 2. Validate configuration
terraform validate

# 3. Plan deployment
terraform plan -out=tfplan

# 4. Apply (provision infrastructure)
terraform apply tfplan
```

### Terraform Variables

Create `terraform/terraform.tfvars`:

```hcl
# Environment
environment = "production"

# AWS Configuration
aws_region     = "us-east-1"
instance_type  = "t3.2xlarge"  # 8 CPU, 32 GB memory
cluster_size   = 3

# GCP Configuration (optional)
gcp_project = "camelot-os-prod"
gcp_region  = "us-central1"

# Deployment mode
enable_kubernetes = false  # Use QR Pill (true for K8s)
qr_pill_mode      = "systemd"  # systemd, bare-metal, or custom
```

### What Gets Provisioned

| Component | AWS | GCP | Description |
|-----------|-----|-----|-------------|
| **Compute** | 3x EC2 (t3.2xlarge) | GKE cluster | CAMELOT-OS instances |
| **Networking** | VPC, subnets, IGW | VPC, routes | Multi-AZ networking |
| **Storage** | ElastiCache Redis | Memorystore | L1 data layer |
| **Vectors** | — | Qdrant cluster | L1.5 consolidation |
| **Monitoring** | SNS topics | Cloud Monitoring | Alerts & logging |
| **IAM** | Instance roles | Service accounts | Least privilege access |

### Example Output

```bash
$ terraform apply tfplan

Outputs:

instance_ips = [
  "10.0.1.42",
  "10.0.2.53",
  "10.0.3.61",
]

instance_public_ips = [
  "54.123.45.67",
  "54.123.45.68",
  "54.123.45.69",
]

redis_endpoint = "camelot-redis-cluster.xxxxx.ng.0001.use1.cache.amazonaws.com:6379"

deployment_mode = "QR Pill (systemd)"
```

---

## Part 2: QR Pill Orchestration (Docker-Free)

### What is QR Pill?

A compressed deployment format inspired by TOON crystals:

```
QRP1:node_1:a3f2b1c9:eyJub2RlX2lkIjogIm5vZGVfMSIsICJzZXJ2aWNlcyI6IHt...
```

**Encodes**:
- Node configuration (ID, cluster topology)
- Service definitions (processes, ports, health checks)
- Recovery procedures (restart policies, backups)
- Observability (metrics, tracing endpoints)

### QR Pill Deployment Modes

#### Mode 1: Systemd (Recommended for Production)

**Advantages**:
- ✅ Native OS integration
- ✅ Automatic restart on failure
- ✅ System-wide resource limits
- ✅ Journal logging integration
- ✅ No additional runtime needed

**How it works**:
```bash
# Deployment creates:
/etc/systemd/system/camelot-consensus.service
/etc/systemd/system/camelot-sync.service
/etc/systemd/system/camelot-agents.service
/etc/systemd/system/camelot-metrics.service

# Manage services:
systemctl start camelot-consensus
systemctl restart camelot-sync
systemctl status camelot-agents
journalctl -u camelot-consensus -f
```

#### Mode 2: Bare-Metal (High Performance)

**Advantages**:
- ✅ Direct process execution (no systemd overhead)
- ✅ Custom resource management
- ✅ Fine-grained process control

**How it works**:
```python
orchestrator = QRPillOrchestrator(crystal, DeploymentMode.BARE_METAL)
await orchestrator.deploy()
# Processes run directly, managed by orchestrator
```

#### Mode 3: Custom (Extensible)

**Advantages**:
- ✅ Custom orchestration logic
- ✅ Integration with existing systems
- ✅ Advanced routing/load balancing

---

## Part 3: Using QR Pill

### Generate QR Pill Crystal

```python
from control_plane.qr_pill_orchestrator import QRPillCrystal, ServiceDef, HealthCheck

# Define services
consensus = ServiceDef(
    name="consensus",
    command="python -m control_plane.distributed_ledger_consensus",
    port=8443,
    health_check=HealthCheck(endpoint="http://localhost:8443/health"),
)

# Create crystal
crystal = QRPillCrystal(
    node_id="node_1",
    cluster_id="camelot-prod",
    peers=["node_2", "node_3"],
    services={"consensus": consensus},
    metrics_enabled=True,
)

# Export as QR code data
qr_data = crystal.to_qr_code_data()
print(qr_data)
# Output: QRP1:node_1:a3f2b1c9:eyJub2RlX2lkIjogIm5vZGVfMSIsICJzZXJ2aWNlcyI6IHt...
```

### Deploy Using Terraform + QR Pill

The `qr_pill_deploy.sh` script (included in Terraform configuration):

1. **Provisions infrastructure** (VPC, EC2, Redis, Qdrant)
2. **Installs CAMELOT-OS** (Python dependencies, codebase)
3. **Deploys QR Pill** (generates systemd units, starts services)
4. **Validates health** (checks all services are running)
5. **Sets up observability** (Prometheus, backups, logging)

**Execution timeline**:
- Phase 1-2 (System prep + install): 3 minutes
- Phase 3-4 (Config + deploy): 2 minutes
- Phase 5-6 (Start services + health check): 1 minute
- Phase 7-9 (Observability + backup + report): 2 minutes
- **Total: ~8 minutes**

### Manual Deployment Example

```bash
# 1. SSH to EC2 instance
ssh -i ~/.ssh/camelot_deploy.pem ec2-user@54.123.45.67

# 2. Run deployment script
bash qr_pill_deploy.sh \
    --node-id node_1 \
    --cluster-nodes "10.0.1.42,10.0.2.53,10.0.3.61" \
    --environment production \
    --qr-pill-mode systemd

# 3. Verify deployment
systemctl status camelot-consensus
journalctl -u camelot-consensus -f

# 4. Check metrics
curl http://localhost:8000/metrics
```

---

## Part 4: Day-2 Operations

### Service Management

```bash
# View all CAMELOT services
systemctl list-units camelot-*

# Restart all services
for svc in consensus sync agents metrics; do
    systemctl restart camelot-$svc
done

# View logs for specific service
journalctl -u camelot-consensus -f --lines 100

# Check resource usage
systemd-cgtop
# or
ps aux | grep camelot
```

### Health Monitoring

```bash
# Check if all services are healthy
curl http://localhost:8443/health   # Consensus
curl http://localhost:6379/health   # Sync
curl http://localhost:8400/health   # Agents
curl http://localhost:8000/metrics  # Metrics

# View service failures
journalctl -p err -u camelot-consensus
journalctl -p err -u camelot-sync
journalctl -u camelot-agents -n 100
```

### Scaling Operations

**Add a node (horizontal scaling)**:

```bash
# Update Terraform variables
vim terraform/terraform.tfvars
# Change: cluster_size = 3 → cluster_size = 4

# Apply changes
terraform plan -out=tfplan
terraform apply tfplan

# New EC2 instance will be created and automatically deployed
```

**Restart a service**:

```bash
systemctl restart camelot-consensus
# Service will restart and rejoin cluster automatically
```

**Perform a rolling update**:

```bash
# Update code
cd /opt/camelot/camelot-os
git pull origin main

# Restart one node at a time
for svc in agents sync consensus; do
    systemctl restart camelot-$svc
    sleep 10  # Wait for service to stabilize
done
```

---

## Part 5: Disaster Recovery

### Backup Procedure

```bash
# Manual backup
/opt/camelot/bin/backup.sh
# Creates: /opt/camelot/backups/backup_20260618_030000/

# Restore from backup
tar xzf /opt/camelot/backups/backup_20260618_030000/data.tar.gz -C /
```

### Quick Recovery (< 15 min)

```bash
# 1. Identify failed node
# From Prometheus alerts or monitoring dashboard

# 2. Terminate failed instance
aws ec2 terminate-instances --instance-ids i-xxxxx

# 3. Terraform automatically creates replacement
terraform apply  # Auto-scales back to 3 nodes

# 4. New instance auto-deploys via user_data script
# Consensus handles node rejoining automatically
```

### Full Cluster Recovery (< 1 hour)

```bash
# 1. Backup current state
/opt/camelot/bin/backup.sh

# 2. Destroy all infrastructure
terraform destroy

# 3. Re-provision from backup
terraform apply
# user_data script redeploys and restores from S3 backup
```

---

## Part 6: Cost Optimization

### Resource Sizing

| Component | Current | Cost/Month | Optimization |
|-----------|---------|-----------|--------------|
| EC2 (3x t3.2xlarge) | 8 vCPU, 32GB | $450 | Downsize to t3.xlarge ($225) |
| ElastiCache Redis | cache.r6g.xlarge (3x) | $300 | Reduce to cache.r6g.large ($150) |
| Qdrant (GCP) | n1-standard-4 (3x) | $200 | Use preemptible VMs ($80) |
| **Total** | | **$950/month** | **~$455/month** |

### Cost Reduction Strategies

```hcl
# In terraform.tfvars

# 1. Use smaller instance types for staging
instance_type = "t3.large"  # $0.08/hour vs $0.33/hour for xlarge

# 2. Enable auto-shutdown for dev environments
enable_auto_shutdown = true

# 3. Use spot instances (70% discount)
resource "aws_instance" "camelot_node" {
  instance_type = "t3.2xlarge"
  spot_price    = "0.10"  # vs $0.33 on-demand
  # ...
}

# 4. Reduce backup retention
backup_retention_days = 7  # vs 30
```

---

## Part 7: Multi-Region Failover

### Setup Active-Active Across Regions

```bash
# Provision in us-east-1
terraform apply -var="aws_region=us-east-1"

# Provision in us-west-2
terraform apply -var="aws_region=us-west-2"

# Both clusters sync via distributed consensus
# Automatic failover if primary region fails
```

### Failover Testing

```bash
# Simulate region failure
aws ec2 modify-instance-attribute \
    --instance-id i-xxxxx \
    --no-source-dest-check

# Traffic automatically routes to secondary region
# Consensus handles cross-region coordination
```

---

## Part 8: Troubleshooting

### Service Won't Start

```bash
# Check status
systemctl status camelot-consensus

# View detailed logs
journalctl -u camelot-consensus -p err -n 50

# Check ports are available
netstat -tlnp | grep 8443

# Restart
systemctl restart camelot-consensus
```

### High CPU Usage

```bash
# Identify which service
top -p $(systemctl show -p MainPID camelot-consensus | cut -d= -f2)

# Check resource limits
systemctl show camelot-consensus | grep Limit

# Adjust if needed
systemctl set-property camelot-consensus CPUQuota=100%
```

### Network Issues

```bash
# Check connectivity to peers
for peer in node_2 node_3; do
    ping -c 1 $peer
    curl http://$peer:8443/health
done

# Verify security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Check DNS
nslookup camelot-node-1
```

---

## Summary

| Component | Technology | Status |
|-----------|-----------|--------|
| **Infrastructure-as-Code** | Terraform | ✅ Ready |
| **QR Pill Orchestrator** | Python + Systemd | ✅ Ready |
| **Deployment Automation** | Bash scripts | ✅ Ready |
| **Multi-cloud** | AWS + GCP | ✅ Ready |
| **Disaster Recovery** | S3 backups + Terraform | ✅ Ready |
| **Cost Optimization** | Instance sizing | ✅ Documented |

---

## Next Steps

1. **Deploy to AWS**:
   ```bash
   terraform apply -var="aws_region=us-east-1" -var="cluster_size=3"
   ```

2. **Monitor**:
   ```bash
   curl http://54.123.45.67:8000/metrics  # Prometheus
   curl http://54.123.45.67:8443/health   # Consensus health
   ```

3. **Scale**:
   ```bash
   terraform apply -var="cluster_size=5"  # Increase to 5 nodes
   ```

4. **Failover**:
   ```bash
   terraform apply -var="aws_region=us-west-2"  # Multi-region
   ```

---

**Production Deployment Checklist**:
- [ ] AWS credentials configured
- [ ] SSH key pair created
- [ ] Terraform variables customized
- [ ] terraform plan reviewed
- [ ] terraform apply executed
- [ ] Health checks passing
- [ ] Metrics flowing to Prometheus
- [ ] Backup S3 bucket created
- [ ] SNS alerts configured
- [ ] Team trained on day-2 ops

