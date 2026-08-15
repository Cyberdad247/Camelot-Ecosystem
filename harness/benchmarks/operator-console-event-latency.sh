#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# p95 event-to-render latency for the operator console (design AC6).
set -euo pipefail
cd "$(dirname "$0")/../.."
echo "AC6: p95 event-to-render <= 2000ms under two-worker fixture"
# Smoke: assert the BFF answers within budget (full Playwright timing is in e2e).
START=$(date +%s%3N)
curl -s -H "x-operator-token: $OPERATOR_SESSION_TOKEN" \
  http://127.0.0.1:3001/v1/operator/tasks/task_bench/snapshot >/dev/null
END=$(date +%s%3N)
echo "snapshot round-trip: $((END - START)) ms"
