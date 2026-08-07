#!/usr/bin/env bash
# Stop the slice. SAFETY: only terminates PIDs whose metadata was created by
# dev-up in integration/.run/ AND whose live /proc cmdline still matches that
# metadata — a recycled PID is never signalled. SIGTERM first (both services
# shut down gracefully), SIGKILL only after a 5s grace window.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

for s in "${SERVICES[@]}"; do
  pid=$(service_pid "$s")
  if [[ -z $pid ]]; then
    rm -f "$(pid_file "$s")" "$(meta_file "$s")"
    continue
  fi
  if ! service_alive "$s"; then
    echo "skip $s: pid $pid is not ours or already gone"
    rm -f "$(pid_file "$s")" "$(meta_file "$s")"
    continue
  fi
  kill -TERM "$pid" 2>/dev/null && echo "stopping $s (pid $pid, SIGTERM)"
  deadline=$(( $(date +%s) + 5 ))
  while kill -0 "$pid" 2>/dev/null && (( $(date +%s) < deadline )); do
    sleep 0.2
  done
  if kill -0 "$pid" 2>/dev/null; then
    kill -KILL "$pid" 2>/dev/null && echo "forced $s (pid $pid, SIGKILL)"
  fi
  rm -f "$(pid_file "$s")" "$(meta_file "$s")"
done
