#!/bin/bash
# =========================================================================
# Camelot-OS Git Branch Naming Enforcer Hook
# Rejects commits/pushes if the branch name is non-compliant.
# =========================================================================

# Compliant prefixes: feat/, fix/, chore/, docs/, perf/, refactor/, test/, ci/, claude/
VALID_PREFIXES="^(feat|fix|chore|docs|perf|refactor|test|ci|claude)/"

# Get current branch name
branch_name=$(git symbolic-ref --short HEAD 2>/dev/null)

# If not in a git branch, exit gracefully
if [ -z "$branch_name" ]; then
    exit 0
fi

# Allow main and master by default
if [ "$branch_name" = "main" ] || [ "$branch_name" = "master" ] || [ "$branch_name" = "HEAD" ]; then
    exit 0
fi

# Validate prefix
if [[ ! "$branch_name" =~ $VALID_PREFIXES ]]; then
    echo "========================================================"
    echo "❌ ERROR: Non-compliant Git Branch Name: '$branch_name'"
    echo "========================================================"
    echo "Your branch name does not match the repository taxonomy."
    echo "Please use one of the following prefixes:"
    echo "  feat/      - New features"
    echo "  fix/       - Bug fixes"
    echo "  chore/     - Build/Tooling/Dependency changes"
    echo "  docs/      - Documentation updates"
    echo "  perf/      - Performance improvements"
    echo "  refactor/  - Code refactoring"
    echo "  test/      - Testing suites"
    echo "  ci/        - CI/CD automation"
    echo "  claude/    - Autonomous agent work streams"
    echo "========================================================"
    echo "Rename your branch using: git branch -m <new-name>"
    echo "========================================================"
    exit 1
fi

exit 0
