#!/usr/bin/env bash
# Fail if the committed generated files no longer match skills.manifest.json.
#
# This runs in `make test`, NOT only in CI. A drift guard that lives only in a
# pipeline is a guarantee in name: this repository's CI has been red on main
# for months and the last PR run aborted before executing a single job. The
# check has to hold on the machine making the change.
#
# The generated files are COMMITTED deliberately — `make dev-up` needs no
# codegen step, so the startup path keeps working with only the compilers it
# already required.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$INTEGRATION_DIR"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

if ! node contracts/gen/generate.mjs "$TMP" >/dev/null; then
  echo "✘ skills.manifest.json failed validation (see above)" >&2
  exit 1
fi

status=0
check() { # generated-file  committed-path
  if ! diff -q "$TMP/$1" "$2" >/dev/null 2>&1; then
    echo "✘ $2 is stale — regenerate with: make generate" >&2
    diff -u "$2" "$TMP/$1" | head -40 >&2
    status=1
  else
    echo "   ✔ $2 matches the manifest"
  fi
}

check skills_gen.go   gateway/skills_gen.go
check skills.gen.ts   contracts/src/skills.gen.ts

if [[ $status -eq 0 ]]; then
  echo "generated contracts: in sync with contracts/skills.manifest.json"
fi
exit $status
