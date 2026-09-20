#!/usr/bin/env bash
# ==============================================================================
# Sovereign S26 & VPS Command Center Health Check Script
# ==============================================================================
set -eo pipefail

echo "=================================================================="
echo "🛡️ CAMELOT-OS SOVEREIGN S26 & VPS HUB HEALTH CHECK"
echo "=================================================================="

FAILED=0

check_service() {
    local svc="$1"
    if systemctl is-active --quiet "$svc"; then
        echo "  [OK] $svc is RUNNING"
    else
        echo "  [FAIL] $svc is NOT ACTIVE"
        FAILED=$((FAILED + 1))
    fi
}

echo "Checking Native Daemon Fleet..."
for service in \
    camelot-s26.slice \
    camelot-audio-dsp.service \
    camelot-streamer.service \
    camelot-bifrost.service \
    camelot-gemini-live.service \
    camelot-arthur.service \
    camelot-sentinel.service; do
    if systemctl list-unit-files | grep -q "^$service"; then
        check_service "$service"
    else
        echo "  [SKIP] $service not installed on this host"
    fi
done

echo "Checking Tailscale Mesh Latency to VPS Hub..."
if command -v tailscale &>/dev/null; then
    tailscale ping -c 1 100.110.180.18 || echo "  [WARN] Could not ping VPS Hub (100.110.180.18)"
fi

echo "=================================================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ ALL VERIFIED SOVEREIGN SERVICES HEALTHY"
    exit 0
else
    echo "⚠️ $FAILED SERVICE(S) REPORTED ANOMALIES"
    exit 1
fi
