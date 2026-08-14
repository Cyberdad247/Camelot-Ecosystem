#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# Sync CLI source from ~/.camelot/ -> CAMELOT_OS/.camelot/
# Excludes runtime data (DB, logs, __pycache__, config secrets)

set -euo pipefail

SRC="$HOME/.camelot"
DST="$(cd "$(dirname "$0")/.." && pwd)/.camelot"

if [ ! -d "$SRC" ]; then
    echo "ERROR: Source $SRC not found"
    exit 1
fi

echo "Syncing CLI: $SRC -> $DST"

# Python source
for f in camelot.py anya.py merlin.py bridge.py ouroboros.py llm_router.py hud.py; do
    if [ -f "$SRC/$f" ]; then
        cp "$SRC/$f" "$DST/$f"
        echo "  [OK] $f"
    fi
done

# Entry points
for f in camelot-os camelot-os.ps1; do
    if [ -f "$SRC/$f" ]; then
        cp "$SRC/$f" "$DST/$f"
        echo "  [OK] $f"
    fi
done

# Knights (source only)
mkdir -p "$DST/knights"
for f in "$SRC"/knights/*.py "$SRC"/knights/*.md; do
    [ -f "$f" ] && cp "$f" "$DST/knights/" && echo "  [OK] knights/$(basename "$f")"
done

# Cartridges
mkdir -p "$DST/cartridges"
for f in "$SRC"/cartridges/*; do
    [ -f "$f" ] && cp "$f" "$DST/cartridges/" && echo "  [OK] cartridges/$(basename "$f")"
done

echo "Sync complete."
