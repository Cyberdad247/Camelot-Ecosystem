#!/bin/bash
# =========================================================================
# Camelot-OS Git Hooks Installation Utility
# Copies enforcement hooks to the local .git/hooks directory.
# =========================================================================

HOOKS_DIR=".git/hooks"
SOURCE_HOOK=".githooks/check-branch-name.sh"

if [ ! -d ".git" ]; then
    echo "❌ ERROR: This command must be run from the root of a Git repository."
    exit 1
fi

echo "Installing branch naming enforcer hooks..."

# Copy to pre-commit and pre-push
cp "$SOURCE_HOOK" "$HOOKS_DIR/pre-commit"
cp "$SOURCE_HOOK" "$HOOKS_DIR/pre-push"

# Make hooks executable
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-push"

echo "✅ Hooks successfully installed into $HOOKS_DIR/"
echo "  - pre-commit hook active"
echo "  - pre-push hook active"
