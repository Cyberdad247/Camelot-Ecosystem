# CAMELOT-OS Deployment Guide

**Version**: 6.0.0 | **Target Environments**: Linux, Windows, macOS  
**Prerequisites**: Python 3.11+, Redis 7.0+, Rust 1.70+  
**Estimated Deployment Time**: 15-30 minutes

---

## Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.11 or higher (`python --version`)
- [ ] Pip/Poetry for dependency management
- [ ] Redis server (local or remote)
- [ ] Qdrant vector database (optional, for semantic search)
- [ ] Git (for version control)
- [ ] 8GB RAM minimum (can scale down to 4GB with Tier 3)
- [ ] 2 CPU cores minimum (can scale down with Tier 2)

### Network Requirements
- [ ] Outbound HTTPS access (for cloud services)
- [ ] Port 6379 available (Redis default)
- [ ] Ports 8401-8408 available (agent network)
- [ ] Port 8000 available (web API, optional)

### Security Checklist
- [ ] Environment variables configured (.env file)
- [ ] SSH keys in place (for cloud deployments)
- [ ] API keys secured (Never commit to repo)
- [ ] Firewall rules reviewed
- [ ] TLS certificates prepared (if needed)

---

## Step 1: Environment Setup (5 minutes)

### 1.1 Clone Repository
```bash
git clone https://github.com/cyberdad247/CAMELOT_OS.git
cd CAMELOT_OS
```

### 1.2 Create Virtual Environment
```bash
# Python venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows PowerShell

# OR Poetry
poetry install
```

### 1.3 Install Dependencies
```bash
# Core dependencies
pip install redis qdrant-client pydantic pydantic-ai

# Optional: AI/ML dependencies
pip install anthropic openai qwen-coder

# Optional: Web framework
pip install fastapi uvicorn

# Development dependencies
pip install pytest pytest-asyncio pytest-cov black mypy
```

### 1.4 Configure Environment Variables
Create `.env` file in project root:
```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your_key_here

# Cloud Brain (NotebookLM)
CLOUD_BRAIN_API_KEY=your_key_here
CLOUD_BRAIN_PROJECT_ID=your_project_id

# AI Models (optional)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# System
ENVIRONMENT=production
LOG_LEVEL=INFO
CAMELOT_VERSION=6.0.0
```

### 1.5 Verify Setup
```bash
python -c "import redis, qdrant_client; print('✅ Dependencies OK')"
redis-cli ping  # Should return PONG
```

---

## Step 2: Database & Service Setup (5 minutes)

### 2.1 Start Redis (Required)

**Linux/macOS:**
```bash
redis-server --daemonize yes
# or
brew services start redis
```

**Windows (WSL):**
```bash
wsl redis-server --daemonize yes
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Verify:**
```bash
redis-cli ping
# Expected: PONG
```

### 2.2 Start Qdrant (Optional, for semantic search)

**Docker:**
```bash
docker run -d \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant:v1.7.0
```

**Verify:**
```bash
curl http://localhost:6333/health
# Expected: {"status":"ok"}
```

### 2.3 Initialize Ledger Database

```bash
python -c "
from control_plane.provenance import Provenance
prov = Provenance()
prov.init_database()
print('✅ Ledger database initialized')
"
```

### 2.4 Create Log Directories
```bash
mkdir -p logs/{phase-a,phase-b,phase-c,phase-d,phase-e,phase-f}
mkdir -p cache/{memory,embeddings,state}
mkdir -p vault/{secrets,keys}
chmod 700 vault/  # Restrict permissions
```

---

## Step 3: Agent Network Startup (5 minutes)

### 3.1 Register Agents
```bash
# Start Hermes (dispatch)
python -m control_plane.agent_registry --agent hermes &

# Start RustClaw (orchestration)
python -m control_plane.agent_registry --agent rustclaw &

# Start remaining agents
python -m control_plane.agent_registry --start-all &
```

### 3.2 Verify Agent Health
```bash
python -c "
from control_plane.agent_gateway import AgentGateway
gateway = AgentGateway()
status = gateway.health_check()
print('Agent Status:')
for agent, health in status.items():
    print(f'  {agent}: {health}')
"
```

**Expected Output:**
```
Agent Status:
  hermes: ✅ HEALTHY
  rustclaw: ✅ HEALTHY
  openclaw: ✅ HEALTHY
  nanobot: ✅ HEALTHY
  zeroclaw: ✅ HEALTHY
  apis: ✅ HEALTHY
  galahad: ✅ HEALTHY
  lancelot: ✅ HEALTHY
```

---

## Step 4: Boot Sequence (5 minutes)

### 4.1 Initialize Hive IDE (Phase A)
```bash
python -m control_plane.hive_boot --initialize
# Expected: "Hive IDE booted in 350ms"
```

### 4.2 Initialize Knowledge Pyramid (Phase B)
```bash
python -c "
from control_plane.distributed_memory import DistributedMemory
mem = DistributedMemory()
mem.initialize()
print('✅ Knowledge Pyramid initialized')
"
```

### 4.3 Start Distance Travel (Phase C)
```bash
python -c "
from control_plane.distance_travel import DistanceTravel
dt = DistanceTravel()
dt.startup()
print('✅ Distance Travel network operational')
"
```

### 4.4 Arm Sovereign Gates (Phase D)
```bash
python -c "
from control_plane.soul_oversight import SoulOversight
oversight = SoulOversight()
oversight.arm_gates()
print('✅ Sovereign gates armed and ready')
"
```

### 4.5 Start Bifrost (Phase E)
```bash
python -c "
from control_plane.bifrost import Bifrost
bifrost = Bifrost()
bifrost.start()
print('✅ Bifrost auto-optimization active')
"
```

### 4.6 Initialize Phase F (TOON + Swarm)
```bash
python -c "
from control_plane.toon_encoder import get_toon_encoder
from control_plane.kinetic_swarm import get_kinetic_swarm
encoder = get_toon_encoder()
swarm = get_kinetic_swarm()
print('✅ TOON encoder ready')
print('✅ Kinetic swarm initialized')
"
```

### 4.7 Run Full Boot Test
```bash
python -m control_plane.boot_sequence --full-test
# Expected: "All phases booted successfully ✅"
```

---

## Step 5: System Validation (5 minutes)

### 5.1 Run Integration Tests
```bash
pytest tests/ -v --cov=control_plane
# Expected: "100+ tests passed"
```

### 5.2 Validate Configuration
```bash
python -c "
from control_plane.config_manager import ConfigManager
config = ConfigManager()
config.validate()
print('✅ Configuration validated')
"
```

### 5.3 System Health Check
```bash
python -m control_plane.harness --health-check
# Expected output:
# Harness Status: OPERATIONAL
# Memory: 1.2 GB / 8.0 GB
# Agents: 8/8 healthy
# Ledger: 1700+ entries
# Uptime: Fresh start
```

### 5.4 Run Ledger Sync
```bash
python -c "
from control_plane.ledger_sync import LedgerSync
sync = LedgerSync()
sync.full_sync()
print('✅ Ledger synchronized')
"
```

---

## Step 6: Optional Configuration

### 6.1 Configure Performance Tier
```bash
# Auto-detect (recommended)
python -c "
from control_plane.bifrost_integration import BifrostIntegration
bi = BifrostIntegration()
tier = bi.auto_detect_tier()
print(f'System tier: {tier}')
"

# Manual override
export CAMELOT_TIER=1  # 1=high performance, 2=medium, 3=edge
```

### 6.2 Enable Semantic Search (Optional)
```bash
python -c "
from control_plane.agent_memory import AgentMemory
mem = AgentMemory()
mem.initialize_embeddings()
print('✅ Semantic search enabled')
"
```

### 6.3 Configure Cloud Brain Sync (Optional)
```bash
python -c "
from control_plane.cloudbrain_sync import CloudBrainSync
sync = CloudBrainSync()
sync.configure(api_key='YOUR_KEY')
sync.test_connection()
print('✅ Cloud Brain connected')
"
```

### 6.4 Enable Northstar Gate (Security)
```bash
python -c "
from control_plane.sir_socrates import SirSocrates
socrates = SirSocrates()
socrates.enable_northstar_gate()
print('✅ Northstar sovereignty gate enabled')
"
```

---

## Step 7: Start Services (Production)

### 7.1 Start Harness (Main Process)
```bash
# Foreground (for testing)
python -m control_plane.harness --foreground

# Background (for production)
python -m control_plane.harness --daemon &

# Systemd service (Linux)
sudo systemctl start camelot-os
```

### 7.2 Start Web API (Optional)
```bash
# Development
uvicorn control_plane.orchestrator:app --reload --port 8000

# Production
gunicorn -w 4 -b 0.0.0.0:8000 control_plane.orchestrator:app
```

### 7.3 Start Hive IDE TUI (Optional)
```bash
python -m control_plane.hive_stream_tui --port 8888
# Open browser: http://localhost:8888
```

### 7.4 Monitor System (Optional)
```bash
# In separate terminal
python -c "
from control_plane.harness import SovereignHarness
harness = SovereignHarness()
harness.monitor_continuous()
"
```

---

## Step 8: Verify Production Deployment

### 8.1 Check All Processes
```bash
# List running processes
ps aux | grep python
ps aux | grep redis
ps aux | grep qdrant

# OR on Windows
tasklist | findstr python
```

### 8.2 Validate Network
```bash
# Check agent connectivity
for port in 8401 8402 8403 8404 8405 8406 8407 8408; do
  nc -zv localhost $port
done
```

### 8.3 Test Full Workflow
```bash
python -c "
from control_plane.orchestrator import Orchestrator
orch = Orchestrator()

# Test request through full pipeline
result = orch.process_request({
    'intent': 'system_status',
    'tier': 'auto'
})
print('Full workflow test:')
print(result)
"
```

### 8.4 Generate Deployment Report
```bash
python -m control_plane.harness --deployment-report
# Outputs: deployment_report_TIMESTAMP.json
```

---

## Rollback Procedure (If Needed)

### Rollback Last Deployment
```bash
git log --oneline -n 5
git revert HEAD  # Revert last commit
python -m control_plane.boot_sequence --full-test
```

### Restore from Ledger
```bash
python -c "
from control_plane.provenance import Provenance
prov = Provenance()
prov.restore_from_entry(1699)  # Entry before Phase F
print('✅ System restored to entry 1699')
"
```

### Emergency Restart
```bash
# Kill all processes
pkill -f 'python.*control_plane'
redis-cli SHUTDOWN

# Restart from scratch
./deploy.sh --fresh
```

---

## Post-Deployment

### 1. Create System Snapshot
```bash
python -c "
from control_plane.toon_encoder import get_toon_encoder
encoder = get_toon_encoder()
snapshot = encoder.encode_system_state()
with open('snapshots/deployment.toon', 'w') as f:
    f.write(snapshot)
print('✅ System snapshot created')
"
```

### 2. Enable Monitoring
```bash
python -m control_plane.harness --enable-monitoring
# Sends metrics to observability platform (optional)
```

### 3. Schedule Backups
```bash
# Daily backup (Linux cron)
0 2 * * * /path/to/backup.sh

# Backup script
#!/bin/bash
python -c "from control_plane.memory_sync import MemorySync; MemorySync().backup()"
```

### 4. Configure Alerts
```bash
# Set up alert thresholds
export ALERT_CPU_THRESHOLD=80
export ALERT_MEMORY_THRESHOLD=7.5  # GB
export ALERT_LATENCY_P95=500  # ms
```

### 5. Verify Documentation
- [ ] ARCHITECTURE.md reviewed
- [ ] This DEPLOYMENT_GUIDE.md printed/bookmarked
- [ ] OPERATIONS_MANUAL.md ready
- [ ] Ledger entries accessible
- [ ] Runbooks stored

---

## Troubleshooting

### Issue: Redis Connection Fails
```bash
# Check Redis running
redis-cli ping

# If not running, start it
redis-server --daemonize yes

# Check port
lsof -i :6379
```

### Issue: Agent Network Unreachable
```bash
# Check agent health
python -m control_plane.agent_registry --health-check

# Restart specific agent
python -m control_plane.agent_registry --restart hermes

# Restart all agents
python -m control_plane.agent_registry --restart-all
```

### Issue: High Memory Usage
```bash
# Check memory tier
python -c "from control_plane.bifrost_integration import BifrostIntegration; print(BifrostIntegration().get_current_tier())"

# Force Tier 3 (edge mode)
export CAMELOT_TIER=3

# Clear memory caches
redis-cli FLUSHDB
```

### Issue: Boot Sequence Fails
```bash
# Check logs
tail -f logs/phase-a/boot.log
tail -f logs/system.log

# Run step-by-step
python -m control_plane.hive_boot --step 1
python -m control_plane.hive_boot --step 2
# ... etc
```

---

## Performance Tuning

### For High Throughput (Tier 1)
```bash
export CAMELOT_TIER=1
export REDIS_POOL_SIZE=50
export AGENT_TIMEOUT=10000  # 10 seconds
export SWARM_BATCH_SIZE=100
```

### For Edge Computing (Tier 3)
```bash
export CAMELOT_TIER=3
export REDIS_POOL_SIZE=5
export AGENT_TIMEOUT=2000  # 2 seconds
export MEMORY_LIMIT=2GB
export SWARM_BATCH_SIZE=10
```

### For Development
```bash
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG
export REDIS_CACHE_TTL=300
export FEATURE_FLAGS=experimental,debug
```

---

## Security Hardening

### Enable All Gates
```bash
export HITL_APPROVAL=true
export NORTHSTAR_GATE=true
export IRON_GATE=true
export SOVEREIGNTY_CHECK=true
```

### Rotate Secrets
```bash
python -c "
from control_plane.security import SecretManager
manager = SecretManager()
manager.rotate_all_secrets()
print('✅ Secrets rotated')
"
```

### Enable Audit Logging
```bash
export AUDIT_LOG_ENABLED=true
export AUDIT_LOG_RETENTION=90  # days
```

---

## Support & Escalation

For deployment issues:
1. Check TROUBLESHOOTING section above
2. Review system logs: `logs/system.log`
3. Check agent health: `python -m control_plane.agent_registry --health-check`
4. Create incident entry: Append to PROVENANCE_LEDGER.md
5. Contact: vizion711@gmail.com

---

**Status**: ✅ Ready for Production Deployment
