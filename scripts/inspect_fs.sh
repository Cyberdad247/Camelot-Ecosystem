#!/bin/bash
# SPDX-License-Identifier: MIT

# inspect_fs.sh — READ-ONLY audit of the Camelot-OS layout BEFORE any reorg.
# Deletes nothing, creates nothing, changes no permissions. Run this on the
# real node first; only after reviewing its output should any move/purge happen.
#
# Usage:  ./inspect_fs.sh            # inspect default /opt/camelot
#         ROOT=/opt/camelot ./inspect_fs.sh
set -u

ROOT="${ROOT:-/opt/camelot}"

# Paths the original reorganize_fs.sh wanted to `rm -rf`. We only LOOK at them.
PURGE_CANDIDATES=(
  "$ROOT/cybertronia"
  "$ROOT/system/gateway"
  "$ROOT/os/lib/bus.js"
)

line() { printf '%s\n' "----------------------------------------------------------------"; }

echo "🔍 [inspect_fs] node=$(hostname)  root=$ROOT  $(date -u +%FT%TZ)"
line

if [ ! -d "$ROOT" ]; then
  echo "NOTE: $ROOT does not exist on this node. Nothing to inspect; a reorg here"
  echo "      would be creating fresh dirs, not purging anything."
  exit 0
fi

echo "## Top-level of $ROOT"
ls -la "$ROOT"
line

echo "## Purge candidates from reorganize_fs.sh (contents + size)"
for p in "${PURGE_CANDIDATES[@]}"; do
  if [ -e "$p" ]; then
    echo ">> EXISTS: $p"
    if [ -d "$p" ]; then
      echo "   size:  $(du -sh "$p" 2>/dev/null | cut -f1)"
      echo "   files: $(find "$p" -type f 2>/dev/null | wc -l)"
      echo "   newest modified:"
      find "$p" -type f -printf '     %TY-%Tm-%Td %TH:%TM  %p\n' 2>/dev/null | sort -r | head -5
    else
      ls -la "$p"
    fi
  else
    echo ">> absent: $p  (purge would be a no-op)"
  fi
  echo
done
line

echo "## Running processes referencing $ROOT (anything live we'd disrupt?)"
ps -eo pid,comm,args 2>/dev/null | grep -i "camelot" | grep -v grep || echo "   (none found via ps)"
line

echo "✅ Inspection complete. Review the above, especially any EXISTS candidate"
echo "   with a recent 'newest modified' timestamp — that means live/active code."
echo "   Decide per-path whether to archive (mv) or leave it before touching anything."
