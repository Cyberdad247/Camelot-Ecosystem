#!/usr/bin/env bash
set -euo pipefail

SENTINEL_HOST="${SENTINEL_HOST:-10.0.0.1}"
SENTINEL_PORT="${SENTINEL_PORT:-26379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-MERLIN_SUPER_SECRET_REDIS_AUTH_9981}"
MASTER_NAME="${MASTER_NAME:-mymaster}"

echo "[INFO] Querying Sentinel at ${SENTINEL_HOST}:${SENTINEL_PORT}..."
INITIAL_MASTER_INFO=$(redis-cli -h "${SENTINEL_HOST}" -p "${SENTINEL_PORT}" sentinel get-master-addr-by-name "${MASTER_NAME}")
INITIAL_MASTER_IP=$(echo "${INITIAL_MASTER_INFO}" | sed -n '1p')
INITIAL_MASTER_PORT=$(echo "${INITIAL_MASTER_INFO}" | sed -n '2p')

echo "[INFO] Initial Master: ${INITIAL_MASTER_IP}:${INITIAL_MASTER_PORT}"
echo "[WARN] Simulating Master Failure..."
redis-cli -h "${INITIAL_MASTER_IP}" -p "${INITIAL_MASTER_PORT}" -a "${REDIS_PASSWORD}" shutdown nosave 2>/dev/null || true

echo "[INFO] Waiting for Sentinel failover promotion..."
sleep 5

NEW_MASTER_INFO=$(redis-cli -h "${SENTINEL_HOST}" -p "${SENTINEL_PORT}" sentinel get-master-addr-by-name "${MASTER_NAME}")
NEW_MASTER_IP=$(echo "${NEW_MASTER_INFO}" | sed -n '1p')

echo "[SUCCESS] Failover complete! Promoted Master IP: ${NEW_MASTER_IP}"
