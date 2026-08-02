#!/usr/bin/env bash
# Camelot-Ecosystem upgrade — companion automation for HANDOVER.md
# Run from the handover/ directory on a machine with GitHub auth.
# Claude Code: prefer following HANDOVER.md interactively; this script is the
# non-interactive fallback for Task A + scaffolding Task B.
set -euo pipefail

PAYLOAD="$(cd "$(dirname "$0")/payload" && pwd)"
WORK="${WORK:-$PWD/work}"
mkdir -p "$WORK" && cd "$WORK"

echo "── Task A: Multivoice-router ─────────────────────────"
if [ ! -d Multivoice-router ]; then
  git clone https://github.com/Cyberdad247/Multivoice-router.git
fi
cd Multivoice-router
git checkout -B bifrost-trust-plane
if git apply --check "$PAYLOAD/multivoice-router.patch" 2>/dev/null; then
  git apply "$PAYLOAD/multivoice-router.patch"
  echo "patch applied"
else
  echo "patch conflicted — falling back to direct copy"
  mkdir -p src/bifrost src/tests
  cp "$PAYLOAD"/bifrost/*.ts src/bifrost/
  cp "$PAYLOAD/bifrost-smoke.test.ts" src/tests/smoke.test.ts
fi
npm install --no-audit --no-fund

echo "── Verify gates (A) ─────────────────────────────────"
npx tsc --noEmit
npx tsx src/tests/smoke.test.ts

git add -A
git commit -m "feat(bifrost): trust plane + control plane + predictive + Yggdrasil ledger (spec: Bifrost bridge chapter)"
git push -u origin bifrost-trust-plane
echo "Task A pushed. Open PR: https://github.com/Cyberdad247/Multivoice-router/pull/new/bifrost-trust-plane"

echo "── Task B: Camelot-Ecosystem (clone + stage only) ───"
cd "$WORK"
if [ ! -d Camelot-Ecosystem ]; then
  git clone https://github.com/Cyberdad247/Camelot-Ecosystem.git
fi
cd Camelot-Ecosystem
git checkout -B bifrost-upgrade
echo ""
echo "Repo structure (top 2 levels):"
find . -maxdepth 2 -type d -not -path './.git*' | sort
echo ""
echo "STOP: placement is a judgment call — see HANDOVER.md Task B."
echo "Payload ready at: $PAYLOAD  (bifrost/ and tower-r3f/)"
