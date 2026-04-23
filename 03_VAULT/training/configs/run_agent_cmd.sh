#!/bin/bash
# Camelot-OS v60.0 Shim Script
# Wraps all agent terminal executions to preserve environment integrity
# Usage: ./run_agent_cmd.sh <command> [args...]

# Activate virtual environment if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
fi

# Enforce 8GB RAM ceiling check
TOTAL_RAM=$(free -m 2>/dev/null | awk '/^Mem:/{print $2}' || echo "0")
if [ "$TOTAL_RAM" -gt 0 ] && [ "$TOTAL_RAM" -lt 8192 ]; then
    echo "[ROTEL_WARNING] RAM below 8GB ceiling. NPE v3.1 constraints active."
fi

# Execute the command
exec "$@"
