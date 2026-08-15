#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Native slice #2 service set + fixture inside the 8 GB host budget (design AC21).
set -euo pipefail
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    # Windows: report process memory for node processes.
    powershell -NoProfile -Command \
      "Get-Process node -ErrorAction SilentlyContinue | Measure-Object -Property WorkingSet64 -Sum | ForEach-Object { '{0:N1} MB' -f (\$_.Sum / 1MB) }"
    ;;
  *)
    ps -o rss= -p "$(pgrep -d, node 2>/dev/null)" 2>/dev/null | awk '{s+=$1} END {printf "%.1f MB (node aggregate)\n", s/1024}'
    ;;
esac
echo "Budget: 8 GB host. If aggregate node RSS exceeds ~6 GB, stop services and retune."
