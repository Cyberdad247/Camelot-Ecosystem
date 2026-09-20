#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# scripts/ops/check-helio-dry.sh
#
# Runs scripts/regen-helio-patch.mjs in dry-run mode and asserts that the emit
# is well-formed, schema-complete, and that the dry run did NOT mutate the
# committed HELIO_PATCH.json.
#
# History — why this was rewritten (2026-09-14):
#
#   The original form asserted `jq -e '.status == "PASS"'`. That key has never
#   existed in the emitted schema; the top-level keys are `project`,
#   `audit_version`, `design_tokens_conformance`, `security_conformance`, and
#   `performance_conformance`. `jq -e` on a missing key evaluates to boolean
#   `false`, so the gate could not pass for ANY input: it looked like a
#   conformance gate while asserting nothing.
#
#   It also never verified the "no file mutation" property that
#   docs/security/PRODUCTION_CHECKLIST.md claims it verifies. That is checked here.
#
#   The artifact-versus-source comparison lives in
#   scripts/check_generated_artifact_parity.py (the `helio-patch` target); this
#   script covers generator hygiene only, so the two are complementary.
#
#   jq was dropped in favour of `python` (already required by this repo's CI)
#   because a missing jq made the gate report "invalid JSON" — a misleading
#   failure mode that hides the real cause.
#
# Exit codes:
#   0 — dry run emitted valid, schema-complete JSON and mutated nothing
#   1 — a hygiene assertion failed, or a required tool is unavailable

set -uo pipefail

PY="${PYTHON:-python}"

# Anchor to the repo root from this script's own location so the gate behaves
# identically whether invoked by CI, pre-commit, or a human in any cwd.
HOST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$HOST_ROOT"

ARTIFACT="HELIO_PATCH.json"
EMIT=".helio-dry.$$.json"
trap 'rm -f "$EMIT"' EXIT

for tool in node "$PY"; do
  if ! command -v "$tool" > /dev/null 2>&1; then
    echo "::error::check-helio-dry requires '$tool', which is not on PATH"
    exit 1
  fi
done

if [ ! -f "$ARTIFACT" ]; then
  echo "::error::$ARTIFACT not found at $HOST_ROOT"
  exit 1
fi

sha256() {
  "$PY" -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1"
}

BEFORE="$(sha256 "$ARTIFACT")"

# The generator prints a human-readable DRY-RUN line on stderr; let it through.
if ! HELIO_DRY_RUN=1 node scripts/regen-helio-patch.mjs > "$EMIT"; then
  echo "::error::regen dry-run failed to execute"
  exit 1
fi

# 1 + 2. Valid JSON, with a string status on every conformance block.
#        Asserting the real schema (rather than a key that does not exist) is
#        the entire point of this rewrite.
if ! "$PY" -c '
import json, sys

BLOCKS = ("design_tokens_conformance", "security_conformance", "performance_conformance")
raw = open(sys.argv[1], encoding="utf-8").read()
try:
    doc = json.loads(raw)
except Exception as exc:
    print(f"::error::regen dry-run emitted invalid JSON: {exc}")
    sys.exit(1)
if not isinstance(doc, dict):
    print("::error::regen dry-run emitted JSON that is not an object")
    sys.exit(1)
for block in BLOCKS:
    status = (doc.get(block) or {}).get("status")
    if not isinstance(status, str):
        print(f"::error::regen dry-run is missing a string status at .{block}")
        sys.exit(1)
print("  schema OK: " + ", ".join("%s=%s" % (b, doc[b]["status"]) for b in BLOCKS))
' "$EMIT"; then
  exit 1
fi

# 3. A dry run must not touch the committed artifact. This is the property
#    PRODUCTION_CHECKLIST.md asserts but which nothing previously checked.
AFTER="$(sha256 "$ARTIFACT")"
if [ "$BEFORE" != "$AFTER" ]; then
  echo "::error::regen dry-run mutated $ARTIFACT (HELIO_DRY_RUN should suppress writes)"
  exit 1
fi

echo "regen dry-run satisfied (valid JSON, schema complete, no mutation)"
