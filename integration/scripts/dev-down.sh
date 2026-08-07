#!/usr/bin/env bash
# Stop all native slice processes and clear PID files.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

for s in "${SERVICES[@]}"; do
  pid=$(service_pid "$s")
  if [[ -n $pid ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null && echo "stopped $s (pid $pid)"
  fi
  rm -f "$(pid_file "$s")"
done
