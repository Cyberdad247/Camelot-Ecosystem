#!/bin/bash

# CAMELOT-OS Emergency Diagnostic
# Run this immediately to capture system state

echo "🚨 EMERGENCY DIAGNOSTIC - Capturing System State"
echo "=================================================="
echo ""

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
DIAG_DIR="emergency_diagnostics_$TIMESTAMP"
mkdir -p "$DIAG_DIR"

echo "Diagnostic directory: $DIAG_DIR"
echo ""

# ========== CONSENSUS STATUS ==========
echo "[1/8] Consensus Status..."
for ip in 192.168.1.{10,11,12}; do
    echo "Node $ip:" | tee -a "$DIAG_DIR/consensus.txt"
    curl -s -m 5 "http://$ip:8443/health" | jq . 2>/dev/null | tee -a "$DIAG_DIR/consensus.txt"
    echo "" | tee -a "$DIAG_DIR/consensus.txt"
done

# ========== AGENT STATUS ==========
echo "[2/8] Agent Status..."
curl -s -m 5 "http://192.168.1.10:8400/agents/status" | jq . 2>/dev/null > "$DIAG_DIR/agents.json" || echo "Failed to get agent status"
cat "$DIAG_DIR/agents.json" | jq "{total: (.agents | length), healthy: (.agents | map(select(.healthy==true)) | length)}"

# ========== SYNC STATUS ==========
echo "[3/8] Knowledge Sync Status..."
curl -s -m 5 "http://192.168.1.10:6379/knight/sync-status" | jq . 2>/dev/null > "$DIAG_DIR/sync.json" || echo "Failed to get sync status"
cat "$DIAG_DIR/sync.json"

# ========== SERVICE LOGS ==========
echo "[4/8] Service Logs (Last 50 lines each)..."
for node in 192.168.1.{10,11,12}; do
    echo "Node $node services:" | tee -a "$DIAG_DIR/service_logs.txt"
    for service in camelot-{consensus,sync,agents,metrics}; do
        echo "  $service:" | tee -a "$DIAG_DIR/service_logs.txt"
        ssh -o ConnectTimeout=5 root@"$node" "systemctl status $service" 2>/dev/null | head -20 | tee -a "$DIAG_DIR/service_logs.txt"
        echo "" | tee -a "$DIAG_DIR/service_logs.txt"
    done
    echo "" | tee -a "$DIAG_DIR/service_logs.txt"
done

# ========== RECENT ERRORS ==========
echo "[5/8] Recent Errors (journalctl)..."
for node in 192.168.1.{10,11,12}; do
    echo "Node $node errors:" | tee -a "$DIAG_DIR/errors.txt"
    ssh -o ConnectTimeout=5 root@"$node" "journalctl PRIORITY=err -u camelot-* -n 30" 2>/dev/null | tee -a "$DIAG_DIR/errors.txt"
    echo "" | tee -a "$DIAG_DIR/errors.txt"
done

# ========== SYSTEM RESOURCES ==========
echo "[6/8] System Resources..."
for node in 192.168.1.{10,11,12}; do
    echo "Node $node:" | tee -a "$DIAG_DIR/resources.txt"
    ssh -o ConnectTimeout=5 root@"$node" "free -h && echo && top -bn1 | head -15" 2>/dev/null | tee -a "$DIAG_DIR/resources.txt"
    echo "" | tee -a "$DIAG_DIR/resources.txt"
done

# ========== NETWORK CONNECTIVITY ==========
echo "[7/8] Network Connectivity..."
for ip in 192.168.1.{10,11,12}; do
    echo "Ping $ip:" | tee -a "$DIAG_DIR/network.txt"
    ping -c 3 "$ip" 2>&1 | tee -a "$DIAG_DIR/network.txt"
    echo "" | tee -a "$DIAG_DIR/network.txt"
done

# ========== TEST OUTPUT ==========
echo "[8/8] Test Output..."
if [ -d "test_results_"* ]; then
    ls -la test_results_*/ | tee -a "$DIAG_DIR/test_files.txt"
    tail -100 test_results_*/output.log 2>/dev/null | tee -a "$DIAG_DIR/test_output.txt"
    tail -100 test_results_*/load_test.log 2>/dev/null | tee -a "$DIAG_DIR/load_test_output.txt"
    tail -100 test_results_*/chaos_test.log 2>/dev/null | tee -a "$DIAG_DIR/chaos_test_output.txt"
fi

echo ""
echo "=================================================="
echo "✅ Diagnostics Complete"
echo "📁 Files saved to: $DIAG_DIR/"
echo ""
echo "Key files:"
echo "  - consensus.txt: Consensus health from all 3 nodes"
echo "  - agents.json: Agent status"
echo "  - sync.json: Knowledge sync status"
echo "  - service_logs.txt: Service status from all nodes"
echo "  - errors.txt: Recent errors from journals"
echo "  - resources.txt: CPU/Memory usage"
echo "  - network.txt: Ping connectivity"
echo "  - test_output.txt: Test log output"
echo ""
