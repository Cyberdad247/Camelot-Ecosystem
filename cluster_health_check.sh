#!/bin/bash

# CAMELOT-OS Comprehensive Cluster Health Check
# Verifies all 3 nodes and all 4 services are operational

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

NODES=("192.168.1.10" "192.168.1.11" "192.168.1.12")
RESULTS=()

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        CAMELOT-OS CLUSTER HEALTH CHECK                     ║"
echo "║        $(date '+%Y-%m-%d %H:%M:%S')                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ========== CONNECTIVITY CHECKS ==========

echo -e "${BLUE}[1/5] NETWORK CONNECTIVITY${NC}"
echo "────────────────────────────────────────────────────────────"

for node in "${NODES[@]}"; do
    echo -n "  Ping $node: "
    if ping -c 1 -W 2 "$node" &> /dev/null; then
        echo -e "${GREEN}✓ Reachable${NC}"
        RESULTS+=("ping_$node:PASS")
    else
        echo -e "${RED}✗ Unreachable${NC}"
        RESULTS+=("ping_$node:FAIL")
    fi
done

echo ""

# ========== SSH CONNECTIVITY ==========

echo -e "${BLUE}[2/5] SSH ACCESS${NC}"
echo "────────────────────────────────────────────────────────────"

for node in "${NODES[@]}"; do
    echo -n "  SSH to $node: "
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@"$node" "echo 'OK'" &> /dev/null; then
        echo -e "${GREEN}✓ Connected${NC}"
        RESULTS+=("ssh_$node:PASS")
    else
        echo -e "${RED}✗ Failed${NC}"
        RESULTS+=("ssh_$node:FAIL")
    fi
done

echo ""

# ========== SERVICE STATUS ==========

echo -e "${BLUE}[3/5] SERVICE STATUS${NC}"
echo "────────────────────────────────────────────────────────────"

services=("camelot-consensus" "camelot-sync" "camelot-agents" "camelot-metrics")

for node in "${NODES[@]}"; do
    echo "  Node $node:"

    for service in "${services[@]}"; do
        echo -n "    $service: "

        status=$(ssh -o ConnectTimeout=5 root@"$node" "systemctl is-active $service" 2>/dev/null || echo "unknown")

        if [ "$status" = "active" ]; then
            echo -e "${GREEN}✓ Running${NC}"
            RESULTS+=("${node}_${service}:PASS")
        else
            echo -e "${RED}✗ $status${NC}"
            RESULTS+=("${node}_${service}:FAIL")
        fi
    done
    echo ""
done

# ========== CONSENSUS HEALTH ==========

echo -e "${BLUE}[4/5] CONSENSUS HEALTH${NC}"
echo "────────────────────────────────────────────────────────────"

for node in "${NODES[@]}"; do
    echo -n "  Node $node health: "

    response=$(curl -s -m 5 "http://$node:8443/health" 2>/dev/null || echo "{}")

    if [ -z "$response" ] || [ "$response" = "{}" ]; then
        echo -e "${RED}✗ No response${NC}"
        RESULTS+=("consensus_health_$node:FAIL")
    else
        status=$(echo "$response" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
        agreement=$(echo "$response" | jq -r '.nodes_in_agreement // 0' 2>/dev/null || echo "0")
        latency=$(echo "$response" | jq -r '.latency_ms // 0' 2>/dev/null || echo "0")

        if [ "$status" = "healthy" ]; then
            echo -e "${GREEN}✓ Healthy${NC} (agreement: $agreement/3, latency: ${latency}ms)"
            RESULTS+=("consensus_health_$node:PASS")
        else
            echo -e "${RED}✗ $status${NC} (agreement: $agreement/3)"
            RESULTS+=("consensus_health_$node:FAIL")
        fi
    fi
done

echo ""

# ========== AGENT NETWORK ==========

echo -e "${BLUE}[5/5] AGENT NETWORK${NC}"
echo "────────────────────────────────────────────────────────────"

echo -n "  Agent count: "
response=$(curl -s -m 5 "http://192.168.1.10:8400/agents/status" 2>/dev/null || echo "{}")

if [ -z "$response" ] || [ "$response" = "{}" ]; then
    echo -e "${RED}✗ No response${NC}"
    RESULTS+=("agents:FAIL")
else
    total=$(echo "$response" | jq '.agents | length' 2>/dev/null || echo "0")
    healthy=$(echo "$response" | jq '.agents | map(select(.healthy==true)) | length' 2>/dev/null || echo "0")

    if [ "$total" = "24" ] && [ "$healthy" = "24" ]; then
        echo -e "${GREEN}✓ $healthy/$total healthy${NC}"
        RESULTS+=("agents:PASS")
    else
        echo -e "${YELLOW}⚠ $healthy/$total healthy${NC}"
        RESULTS+=("agents:WARN")
    fi
fi

echo -n "  Agent confidence: "
avg_confidence=$(echo "$response" | jq '.agents[].confidence | add / length' 2>/dev/null || echo "0")
if (( $(echo "$avg_confidence >= 0.85" | bc -l) )); then
    echo -e "${GREEN}✓ $avg_confidence${NC}"
else
    echo -e "${YELLOW}⚠ $avg_confidence (target: 0.85+)${NC}"
fi

echo ""

# ========== KNOWLEDGE SYNC ==========

echo -e "${BLUE}[BONUS] KNOWLEDGE SYNC${NC}"
echo "────────────────────────────────────────────────────────────"

echo -n "  Sync status: "
sync_response=$(curl -s -m 5 "http://192.168.1.10:6379/knight/sync-status" 2>/dev/null || echo "{}")

if [ -z "$sync_response" ] || [ "$sync_response" = "{}" ]; then
    echo -e "${RED}✗ No response${NC}"
else
    sync_health=$(echo "$sync_response" | jq -r '.sync_health // "unknown"' 2>/dev/null || echo "unknown")
    lag=$(echo "$sync_response" | jq -r '.replication_lag_ms // 0' 2>/dev/null || echo "0")
    conflicts=$(echo "$sync_response" | jq -r '.conflicts_detected // 0' 2>/dev/null || echo "0")

    if [ "$sync_health" = "excellent" ] || [ "$sync_health" = "healthy" ]; then
        echo -e "${GREEN}✓ $sync_health${NC} (lag: ${lag}ms, conflicts: $conflicts)"
    else
        echo -e "${YELLOW}⚠ $sync_health${NC} (lag: ${lag}ms, conflicts: $conflicts)"
    fi
fi

echo ""

# ========== SYSTEM RESOURCES ==========

echo -e "${BLUE}[BONUS] SYSTEM RESOURCES${NC}"
echo "────────────────────────────────────────────────────────────"

for node in "${NODES[@]}"; do
    echo "  Node $node:"

    cpu=$(ssh -o ConnectTimeout=5 root@"$node" "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1" 2>/dev/null || echo "?")
    mem=$(ssh -o ConnectTimeout=5 root@"$node" "free | grep Mem | awk '{printf \"%.0f\", \$3/\$2*100}'" 2>/dev/null || echo "?")
    disk=$(ssh -o ConnectTimeout=5 root@"$node" "df /opt/camelot | tail -1 | awk '{print \$5}'" 2>/dev/null || echo "?")

    echo -n "    CPU: ${cpu}% | Memory: ${mem}% | Disk: ${disk}"

    # Check thresholds
    if (( $(echo "$cpu > 70" | bc -l 2>/dev/null || echo 0) )); then
        echo -e " ${YELLOW}(warning: high CPU)${NC}"
    elif (( $(echo "$mem > 80" | bc -l 2>/dev/null || echo 0) )); then
        echo -e " ${YELLOW}(warning: high memory)${NC}"
    else
        echo -e " ${GREEN}(healthy)${NC}"
    fi
done

echo ""

# ========== SUMMARY ==========

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                        SUMMARY                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

pass_count=0
warn_count=0
fail_count=0

for result in "${RESULTS[@]}"; do
    status="${result##*:}"

    if [ "$status" = "PASS" ]; then
        ((pass_count++))
    elif [ "$status" = "WARN" ]; then
        ((warn_count++))
    else
        ((fail_count++))
    fi
done

echo -e "  ${GREEN}✓ Passed: $pass_count${NC}"
[ "$warn_count" -gt 0 ] && echo -e "  ${YELLOW}⚠ Warnings: $warn_count${NC}"
[ "$fail_count" -gt 0 ] && echo -e "  ${RED}✗ Failed: $fail_count${NC}"

echo ""

# ========== VERDICT ==========

if [ "$fail_count" -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ CLUSTER HEALTH: READY FOR TESTING                    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next step: Run load tests"
    echo "  ./run_tests.sh"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ CLUSTER HEALTH: ISSUES FOUND                          ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Issues to resolve:"
    for result in "${RESULTS[@]}"; do
        status="${result##*:}"
        if [ "$status" != "PASS" ]; then
            item="${result%:*}"
            echo "  - $item: $status"
        fi
    done
    echo ""
    exit 1
fi
