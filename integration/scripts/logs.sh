#!/usr/bin/env bash
# Show recent logs. Usage: logs.sh [service] [-f]
#   logs.sh              last 40 lines of every service
#   logs.sh gateway -f   follow one service
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

if [[ ${1:-} =~ ^(gateway|node-agent|hermes|console)$ ]]; then
  if [[ ${2:-} == "-f" ]]; then
    exec tail -f "$(log_file "$1")"
  fi
  exec tail -40 "$(log_file "$1")"
fi

for s in "${ALL_SERVICES[@]}"; do
  echo "───── $s ─────"
  tail -40 "$(log_file "$s")" 2>/dev/null || echo "(no log)"
done
