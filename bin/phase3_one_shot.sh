#!/usr/bin/env bash
# bin/phase3_one_shot.sh
# ---------------------------------------------------------------------------
# Single-shot Phase 3 (MICROVM_LATCH) operator wrapper for HiveIDE_Apex_v1000.
# ---------------------------------------------------------------------------
# Chain executed in order:
#   1) scripts/wsl2_preflight.sh           (baseline /dev/kvm + libkrun state)
#   2) bin/install_libkrun.sh              (apt-get install libkrun0 librun0
#                                           OR `cargo install --locked krun-cli`)
#   3) scripts/wsl2_preflight.sh  (post #1) (libkrun now installed + /dev/kvm)
#   4) scripts/wsl2_preflight.sh  (post #2) (v7 polish #4: /dev/kvm stability
#                                           re-check — race + sandbox-leak canary)
#
# Final JSON verdict emitted on stdout:
#   {"final":"GO", ...}       exit 0
#   {"final":"NO-GO", ...}    exit 1
#   {"final":"PARTIAL", ...}  exit 2
#
# Safety posture:
#   - Pure additive scaffolding. Reads no secrets. Writes no host state.
#   - Idempotent: install_libkrun.sh re-checks before each step; safe to re-run.
#   - Pre-WSL2 call emits NO-GO without executing any sudo/apt/cargo command
#     (`bin/install_libkrun.sh` exits at its own wsl-detect gate before doing work).
#   - Phase 3 DESTRUCTIVE edits to 01_KERNEL/core/microvm_cages/ still require
#     CAMELOT_DASHBOARD_OPERATOR_TOKEN via control_plane/soul_oversight.pre_execute
#     (HUMAN_GATE tier per AGENTS.md). This wrapper does NOT unlock that gate.
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Defensive: refuse to run if the project layout isn't what we expect.
if [ ! -f "$PROJECT_ROOT/scripts/wsl2_preflight.sh" ] \
   || [ ! -f "$PROJECT_ROOT/bin/install_libkrun.sh" ]; then
    printf '{"final":"NO-GO","detail":"project layout mismatch; expected scripts/wsl2_preflight.sh + bin/install_libkrun.sh under %s"}\n' "$PROJECT_ROOT"
    exit 2
fi

cd "$PROJECT_ROOT"

# Run a subcommand and capture its full stdout+stderr.
run_preflight() {
    bash scripts/wsl2_preflight.sh 2>&1
}
run_install() {
    # install_libkrun.sh exits non-zero on NO-GO; tolerate so the wrapper
    # can still parse the verdict from the captured body.
    bash bin/install_libkrun.sh 2>&1 || true
}

# Extract the verdict field from a JSON-ish blob. Defensive under `set -o
# pipefail`: returns "?" rather than aborting when no verdict line is found.
extract_verdict() {
    local body=$1
    local raw
    raw=$(printf '%s' "$body" | tr -d '\n' | grep -oE '"verdict":[[:space:]]*"[A-Z-]+"' | head -1 || true)
    if [ -z "$raw" ]; then
        printf '?'
    else
        printf '%s' "$raw" | sed 's/^"verdict":[[:space:]]*"//; s/"$//'
    fi
}

echo "===== 1/4 pre-install preflight ====="
PRE_BODY=$(run_preflight)
PRE_V=$(extract_verdict "$PRE_BODY")
echo "$PRE_BODY"
printf '\n[verdict=%s]\n\n' "$PRE_V"

echo "===== 2/4 install libkrun ====="
INSTALL_BODY=$(run_install)
INSTALL_V=$(extract_verdict "$INSTALL_BODY")
echo "$INSTALL_BODY"
printf '\n[verdict=%s]\n\n' "$INSTALL_V"

echo "===== 3/4 post-install preflight #1 ====="
POST1_BODY=$(run_preflight)
POST1_V=$(extract_verdict "$POST1_BODY")
echo "$POST1_BODY"
printf '\n[verdict=%s]\n\n' "$POST1_V"

echo "===== 4/4 post-install preflight #2 (v7 polish #4 /dev/kvm stability) ====="
POST2_BODY=$(run_preflight)
POST2_V=$(extract_verdict "$POST2_BODY")
echo "$POST2_BODY"
printf '\n[verdict=%s]\n\n' "$POST2_V"

# v7 polish #4: assert /dev/kvm stability across the two post-install preflight
# runs. If POST1 != POST2 the state flapped mid-install (race / sandbox-leak
# canary). Surface as a stderr WARN — final verdict math still gates on GO.
if [ "$POST1_V" != "$POST2_V" ]; then
    printf 'WARN: polish #4 /dev/kvm stability FAILED — POST1=%s POST2=%s\n' "$POST1_V" "$POST2_V" >&2
    POLISH4_STABLE=0
else
    POLISH4_STABLE=1
fi

# Stringify the polish #4 canary for the final JSON verdict.
if [ "$POLISH4_STABLE" -eq 1 ]; then
    POLISH4_STR="stable"
else
    POLISH4_STR="flapped"
fi

# Final JSON verdict. Branch on the canonical patterns we expect to see.
if [ "$POST1_V" = "GO" ] && [ "$POST2_V" = "GO" ] && [ "$INSTALL_V" = "GO" ]; then
    printf '{"final":"GO","detail":"Phase 3 MICROVM_LATCH unblocked; libkrun installed; /dev/kvm stable across post-install re-runs","preflight_pre":"%s","install":"%s","preflight_post1":"%s","preflight_post2":"%s","polish_4":"%s"}\n' \
        "$PRE_V" "$INSTALL_V" "$POST1_V" "$POST2_V" "$POLISH4_STR"

    # Persist the GO verdict to the runtime-state capture path. The file is
    # git-tracked under 03_VAULT/ so the Iron Gate ledger can pin the artifact
    # at promotion time. Reversible via `git checkout HEAD -- <path>`.
    # Atomic publish: write to .tmp then `mv` so a killed-by-signal process
    # cannot leave a partial JSON in the verified path.
    VERDICT_DIR="03_VAULT/runtime_state/hive_ide_apex_v1000"
    VERDICT_FILE="$VERDICT_DIR/wsl2_verdict.json"
    # Leading dot deliberately omitted: POSIX treats dotfiles as hidden but
    # Windows NTFS does NOT, so the operator browsing from the host would
    # still see it. Plain suffix keeps cross-OS visibility consistent.
    VERDICT_FILE_TMP="$VERDICT_DIR/wsl2_verdict.json.tmp"
    mkdir -p "$VERDICT_DIR"
    CAPTURED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    # EXIT trap removes the .tmp on any exit path. On success the file has
    # already been mv'd away so the rm is a no-op. On failure (ENOSPC mid
    # write, signal) the trap prevents orphan .tmp files accumulating in
    # the capture dir across runs.
    trap 'rm -f "$VERDICT_FILE_TMP"' EXIT
    printf '{"final":"GO","detail":"Phase 3 MICROVM_LATCH unblocked","preflight_pre":"%s","install":"%s","preflight_post1":"%s","preflight_post2":"%s","polish_4":"%s","captured_at":"%s","captured_by":"phase3_one_shot"}\n' \
        "$PRE_V" "$INSTALL_V" "$POST1_V" "$POST2_V" \
        "$POLISH4_STR" "$CAPTURED_AT" > "$VERDICT_FILE_TMP"
    mv "$VERDICT_FILE_TMP" "$VERDICT_FILE"
    printf '[phase3_one_shot] verdict written: %s\n' "$VERDICT_FILE" >&2

    exit 0
fi

if [ "$PRE_V" = "NO-GO" ] && [ "$INSTALL_V" = "NO-GO" ] && [ "$POST1_V" = "NO-GO" ]; then
    printf '{"final":"NO-GO","detail":"WSL2 + /dev/kvm not yet available; enable via: wsl --install (admin PowerShell) + BIOS nested-virt (Intel VT-x or AMD-V) + reboot, then run this script from inside the WSL2 distro","preflight_pre":"%s","install":"%s","preflight_post1":"%s","preflight_post2":"%s","polish_4":"%s"}\n' \
        "$PRE_V" "$INSTALL_V" "$POST1_V" "$POST2_V" "$POLISH4_STR"
    exit 1
fi

printf '{"final":"PARTIAL","detail":"mixed verdicts — some checks passed but full Phase 3 substrate not confirmed; inspect dumps above","preflight_pre":"%s","install":"%s","preflight_post1":"%s","preflight_post2":"%s","polish_4":"%s"}\n' \
    "$PRE_V" "$INSTALL_V" "$POST1_V" "$POST2_V" "$POLISH4_STR"
exit 3
