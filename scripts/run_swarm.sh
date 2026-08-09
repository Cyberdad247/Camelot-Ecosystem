#!/bin/bash
# =========================================================================
# Camelot-OS Swarm Execution Orchestrator
# Executes the 5-phase pipeline and handles pre/post configurations.
# =========================================================================

# Ensure colors are defined
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================================${NC}"
echo -e "${GREEN}🚀  Camelot-OS Swarm Orchestrator Launching Pipeline  🚀${NC}"
echo -e "${GREEN}========================================================${NC}"
echo ""

# 1. Environment Verification
if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Git is not installed or not in PATH.${NC}"
    exit 1
fi

# Determine python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}ERROR: Python is not installed or not in PATH.${NC}"
        exit 1
    fi
fi

# Run with virtual environment if present
if [ -d ".venv" ]; then
    if [ -f ".venv/Scripts/python" ]; then
        PYTHON_CMD=".venv/Scripts/python"
    elif [ -f ".venv/Scripts/python.exe" ]; then
        PYTHON_CMD=".venv/Scripts/python.exe"
    elif [ -f ".venv/bin/python" ]; then
        PYTHON_CMD=".venv/bin/python"
    fi
fi

# 2. Run Pipeline
echo "Initiating 5-Phase pipeline execution..."
$PYTHON_CMD scripts/swarm_executor.py "$@"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Swarm Execution Failed. Check data/swarm_executor.log for details.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Swarm Pipeline executed successfully.${NC}"
echo ""
echo "Generated Artifacts:"
echo "  - scripts/delete_branches_swarm.sh"
echo "  - scripts/validate_cleanup.sh"
echo "  - data/swarm_execution_report.json"
echo "  - data/swarm_execution_complete.json"
echo ""
