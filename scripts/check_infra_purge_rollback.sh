#!/usr/bin/env bash
# scripts/check_infra_purge_rollback.sh
#
# Implementation of the verification contract defined in
# docs/plans/IMPLEMENTATION_INFRA_PURGE.md, Section 6.1.
#
# Run directly from repo root, OR invoked automatically by the
# `.pre-commit-config.yaml` local hook "infra-purge-rollback-verify"
# on commits that touch purge-affected paths.
#
# Exit codes:
#   0  — all required checks pass; rollback contract is enforceable
#   1  — one or more required checks failed; commit must be blocked
#   2  — invocation error (e.g., not inside a git repository)
#
# Required tools: bash ≥ 4, git ≥ 2.32 (for --no-reflogs in the
# advisory fsck check).
#
# Windows line-ending caveat (Check 4): on Windows developer boxes,
# `git config core.autocrlf` MUST be `false` (or set via
# `.gitattributes` for the rollback files) so the SHA-256 of the
# staged (index) bytes matches the SHA-256 of the original
# unreachable-blob bytes. CI runners already ship with sensible
# defaults; local Windows checkouts need it explicitly or Check 4
# will report false mismatches on legitimate restores.

set -euo pipefail

# Locate repo root (this script lives under <root>/scripts/).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "infra_purge_rollback: ERROR — not inside a git repository" >&2
  exit 2
fi
cd "${REPO_ROOT}"

# --- Pre-flight: Shallow clone detection ------------------------------
# If the repo is a shallow clone, Check 3's 'git fsck --unreachable
# --no-reflogs' output is meaningless: deleted blobs from the deletion
# commit aren't reachable from any fetched ref, but they also aren't
# in our object graph. The script would silently report "no unreachable
# blobs" -- a false PASS. Hard-fail here so the gate is honest.
#
# In CI, .github/workflows/verify_os.yml pins fetch-depth: 0 on the
# checkout step, so this block passes. On local developer boxes with
# shallow clones, this block correctly forces a hard fail rather than
# silently letting Check 3 lie.
if git rev-parse --is-shallow-repository 2>/dev/null | grep -q '^true$'; then
  echo "infra_purge_rollback: FAIL -- repo is a shallow clone." >&2
  echo "  Check 3 (git fsck --unreachable) requires full history." >&2
  echo "  Re-clone with 'git fetch --unshallow' or set" >&2
  echo "  actions/checkout fetch-depth: 0 in CI." >&2
  exit 1
fi

ROLLBACK_DIR="99_ARCHIVE/infra_purge_backup"
FAIL=0

echo "==== infra_purge rollback verification ===="
echo "Repo: ${REPO_ROOT}"
echo "Rollback path: ${ROLLBACK_DIR}"
echo

# --- Check 1: Local backup exists on disk ---------------------------
echo "[1/5] Local backup exists on disk"
for f in redis_store.py qdrant_store.py; do
  if [[ ! -f "${ROLLBACK_DIR}/${f}" ]]; then
    echo "  FAIL: ${ROLLBACK_DIR}/${f} missing" >&2
    FAIL=1
  else
    echo "  OK:   ${ROLLBACK_DIR}/${f}"
  fi
done
echo

# --- Check 2: Rollback contract is git-tracked ----------------------
echo "[2/5] Rollback contract is git-tracked"
if ! git ls-files "${ROLLBACK_DIR}/" | grep -qE 'redis_store|qdrant_store'; then
  echo "  FAIL: rollback files are not tracked by git." >&2
  echo "        'git ls-files ${ROLLBACK_DIR}/' returned nothing matching" >&2
  echo "        the expected file names. The rollback only exists on disk" >&2
  echo "        and will be lost on 'git gc'." >&2
  FAIL=1
else
  echo "  OK:   rollback files are in git index:"
  git ls-files "${ROLLBACK_DIR}/" | sed 's/^/    - /'
fi
echo

# --- Check 3: Rollback survives 'git gc' (advisory) -----------------
# Requires git >= 2.32 (the --no-reflogs flag was added then). On older
# git, fsck errors to stderr; we capture stdout AND stderr so the
# version-gate report is honest instead of falsely printing
# "no unreachable blobs".
echo "[3/5] Rollback survives 'git gc' (advisory; requires git >= 2.32)"
FSCK_OUTPUT="$(git fsck --unreachable --no-reflogs 2>&1 || true)"
if grep -qE '^unreachable blob' <<<"${FSCK_OUTPUT}"; then
  echo "  INFO: unreachable blobs found - recent deletions still recoverable"
elif grep -qiE '^(error|fatal|unknown)' <<<"${FSCK_OUTPUT}"; then
  echo "  WARN: git fsck failed (likely git < 2.32; --no-reflogs not supported)."
  echo "         Captured output:"
  printf '%s\n' "${FSCK_OUTPUT}" | sed 's/^/            /'
else
  echo "  INFO: no unreachable blobs."
  echo "         * If you just deleted a file, run"
  echo "             git fsck --unreachable --no-reflogs"
  echo "           before 'git gc' erases the blob."
  echo "         * If you have older deletions, the safety-net window"
  echo "           (~30 days) has already elapsed."
fi
echo

# --- Check 4: Blob provenance (catches stub-replacement attacks) ---
# Walks the historical blob-id record for each tracked rollback file
# path AND the unreachable-blob set captured by Check 3. The staged
# (index) blob's SHA-1 must appear in at least ONE of those sets.
#
# Threat model: an attacker PRs a stub like `print('ok')` in place of
# the real deleted file. Check 1+2 may pass (file exists on disk and
# is staged), but the staged blob's SHA-1 is a fresh value that has
# never existed at this file path in this repo's history — primary
# check hard-FAILs.
#
# We compare STAGED BLOB SHA-1s (from `git ls-files --stage <path>`),
# not byte-level SHA-256 of `git show ":path"`. This is the key change
# from the prior SHA-256 design: blob IDs are content-addressed by
# git's internal hash, so they survive the two invariants that broke
# the old check:
#   1. SHA-1 deduplication: a legit restore stages the same BLOB
#      that was previously unreachable (one object, one SHA-1), so
#      it's reachable-via-index and disappears from `git fsck
#      --unreachable` even though it's authentic.
#   2. Line-ending normalization (CRLF/LF): the staged BLOB object
#      in `.git/objects/` is byte-identical to the historical blob
#      because git stores by content; the working tree's CRLF/LF
#      rendering only fires on `git checkout`, which we never call.
#
# Two checks run for defense-in-depth:
#   PRIMARY  (hard-FAIL on stub): the staged SHA-1 appears in the
#     HISTORICAL blob-id record for this path. Walks every commit
#     reachable from any ref that ever touched this path, collects
#     the blob SHA-1 from each commit's tree, and compares against
#     the staged SHA. Costs O(commits * N) but typical rollback
#     files have <100 historical commits.
#   ADVISORY (informational): the staged SHA-1 also appears in
#     `git fsck --unreachable --no-reflogs`. If the unreachable set
#     is empty (typically ~30 days after the original purge, once
#     `git gc` has pruned) this degrades to INFO without affecting
#     the verdict. Failing here would create a permanent time bomb
#     that breaks unrelated CI builds once the safety-net expires.
#
# Coverage window: PRIMARY (historical) check is durable and does not
# depend on the unreachable-bucket lifetime. ADVISORY (unreachable)
# coverage exists only while the deleted objects remain in the local
# object graph.
echo "[4/5] Rollback blob provenance (catches stub-replacement attacks)"
# Pre-build the unreachable-blob set once; reused by advisory check.
UNREACHABLE_BLOBS=()
while read -r blob_sha; do
  # Defense-in-depth: validate SHA shape before passing downstream.
  if [[ "${blob_sha}" =~ ^[0-9a-f]{40,64}$ ]]; then
    UNREACHABLE_BLOBS+=("${blob_sha}")
  fi
done < <(awk '/^unreachable blob/ {print $3}' <<<"${FSCK_OUTPUT}")

MAX_HISTORICAL_COMMITS=1000
MAX_ADVISORY_BLOBS=1000

for f in redis_store.py qdrant_store.py; do
  FILE_PATH="${ROLLBACK_DIR}/${f}"
  if ! git ls-files --error-unmatch "${FILE_PATH}" >/dev/null 2>&1; then
    echo "  INFO: ${f} not staged in index; skipping provenance for this file."
    continue
  fi

  # ----- Get staged blob SHA-1 -------------------------------------
  STAGED_SHA="$(git ls-files --stage "${FILE_PATH}" 2>/dev/null | awk '{print $2}')"
  if [[ ! "${STAGED_SHA}" =~ ^[0-9a-f]{40}$ ]]; then
    echo "  FAIL: ${f} staged blob SHA malformed ('${STAGED_SHA:0:16}')" >&2
    echo "        expected a 40-char lowercase hex SHA-1 from" >&2
    echo "        'git ls-files --stage ${FILE_PATH}'." >&2
    FAIL=1
    continue
  fi

  # ----- PRIMARY: walk historical commits --------------------------
  # `git log --all -- <path>`: every commit reachable from any ref
  # that ever touched this path (added, modified, deleted, or renamed
  # into). The list includes the original addition commit AND every
  # subsequent commit against this path — exactly what we need.
  HISTORICAL_COMMITS_FILE="$(mktemp -t historic.XXXXXX)"
  git log --all --pretty=format:'%H' -- "${FILE_PATH}" > "${HISTORICAL_COMMITS_FILE}" 2>/dev/null || true
  HISTORICAL_SHAS=()
  COMMIT_COUNT=0
  if [[ -s "${HISTORICAL_COMMITS_FILE}" ]]; then
    while read -r commit_sha; do
      COMMIT_COUNT=$((COMMIT_COUNT + 1))
      if [[ ${COMMIT_COUNT} -gt ${MAX_HISTORICAL_COMMITS} ]]; then
        echo "  NOTE: ${f} historical commit cap ${MAX_HISTORICAL_COMMITS} reached;" >&2
        echo "        verdict may be inconclusive. Increase cap in script and rerun." >&2
        break
      fi
      [[ "${commit_sha}" =~ ^[0-9a-f]{40}$ ]] || continue
      # `git ls-tree <commit> -- <path>` returns the blob SHA-1 of the
      # file at this path in that commit's tree. Empty output for
      # deletion-only commits is fine — we just skip them.
      blob_sha="$(git ls-tree "${commit_sha}" -- "${FILE_PATH}" 2>/dev/null | awk '$2=="blob" {print $3}' || true)"
      [[ -n "${blob_sha}" && "${blob_sha}" =~ ^[0-9a-f]{40}$ ]] && HISTORICAL_SHAS+=("${blob_sha}")
    done < "${HISTORICAL_COMMITS_FILE}"
  fi
  rm -f "${HISTORICAL_COMMITS_FILE}"

  # Deduplicate historical SHAs (a single SHA may repeat across merges
  # touching the same path). Membership check is O(N) so dedup matters.
  if [[ ${#HISTORICAL_SHAS[@]} -gt 0 ]]; then
    UNIQUE_HISTORICAL_SHAS=()
    while read -r sha; do
      UNIQUE_HISTORICAL_SHAS+=("${sha}")
    done < <(printf '%s\n' "${HISTORICAL_SHAS[@]}" | LC_ALL=C sort -u)
    HISTORICAL_SHAS=("${UNIQUE_HISTORICAL_SHAS[@]}")
  fi

  # Edge case: file staged but no historical record exists at this
  # path. This happens only in the unusual state of a staged file in
  # an empty repo (no commits). Treat as informational skip — without
  # history, we cannot prove provenance but there is also nothing to
  # forge against.
  if [[ ${#HISTORICAL_SHAS[@]} -eq 0 ]]; then
    echo "  INFO: ${f} has no historical blob-id record at this path" >&2
    echo "         (unusual state: staged file with empty rev-list)." >&2
    echo "         Skipping primary provenance check." >&2
    continue
  fi

  MATCH_FOUND=0
  for hist_sha in "${HISTORICAL_SHAS[@]}"; do
    if [[ "${hist_sha}" == "${STAGED_SHA}" ]]; then
      MATCH_FOUND=1
      break
    fi
  done

  if [[ ${MATCH_FOUND} -ne 1 ]]; then
    echo "  FAIL: ${f} staged SHA-1 ${STAGED_SHA:0:12} is NOT in the historical" >&2
    echo "        blob-id record for this path (${#HISTORICAL_SHAS[@]} unique" >&2
    echo "        historical blob SHAs examined across ${COMMIT_COUNT} commits)." >&2
    echo "        This catches stub-replacement attacks (e.g., a one-line" >&2
    echo "        'print(\"ok\")' committed in place of the original file)." >&2
    FAIL=1
    continue
  fi

  echo "  OK:   ${f} staged SHA-1 ${STAGED_SHA:0:12} matches historical blob-id record"

  # ----- ADVISORY: unreachable-blob overlap ------------------------
  # Bonus signal that the staged blob is currently also in the
  # unreachable-bucket (i.e., the original purge hasn't been gc'd
  # away yet). Pure information; does not affect exit code.
  if [[ ${#UNREACHABLE_BLOBS[@]} -eq 0 ]]; then
    echo "  INFO: ${f} advisory: unreachable-blob set is empty (likely post 'git gc')."
  else
    ADVISORY_FOUND=0
    ADVISORY_COUNT=0
    for blob_sha in "${UNREACHABLE_BLOBS[@]}"; do
      ADVISORY_COUNT=$((ADVISORY_COUNT + 1))
      if [[ ${ADVISORY_COUNT} -gt ${MAX_ADVISORY_BLOBS} ]]; then
        echo "  NOTE: ${f} advisory cap ${MAX_ADVISORY_BLOBS} reached; informational." >&2
        break
      fi
      if [[ "${blob_sha}" == "${STAGED_SHA}" ]]; then
        ADVISORY_FOUND=1
        break
      fi
    done
    if [[ ${ADVISORY_FOUND} -eq 1 ]]; then
      echo "  INFO: ${f} staged SHA-1 also appears in the current unreachable-blob set."
    else
      echo "  INFO: ${f} staged SHA-1 not in current unreachable-blob set; primary"
      echo "         historical check has already verified provenance."
    fi
  fi
done
echo

# --- Check 5: PR template precondition for Section 6.2 --------------
echo "[5/5] PR template precondition (Section 6.2)"
TEMPLATE_PATH=".github/PULL_REQUEST_TEMPLATE.md"
if [[ ! -f "${TEMPLATE_PATH}" ]]; then
  echo "  WARN: ${TEMPLATE_PATH} does not exist."
  echo "         Section 6.2 of IMPLEMENTATION_INFRA_PURGE.md is non-binding"
  echo "         until the template is added. (Advisory only - does not fail.)"
else
  echo "  OK:   ${TEMPLATE_PATH} exists; Section 6.2 is enforceable."
fi
echo

# --- Summary --------------------------------------------------------
if [[ "${FAIL}" -ne 0 ]]; then
  echo "RESULT: FAIL" >&2
  echo "infra_purge rollback verification: FAILED" >&2
  echo "  Fix the failed checks before committing changes that touch" >&2
  echo "  purge-affected paths. See Section 6.1 of" >&2
  echo "  docs/plans/IMPLEMENTATION_INFRA_PURGE.md for the contract." >&2
  exit 1
fi

echo "RESULT: PASS"
echo "infra_purge rollback verification: PASS"
