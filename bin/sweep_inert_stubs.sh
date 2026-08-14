#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# bin/sweep_inert_stubs.sh — CAMELOT-GCMN activation ADR §7 sunset cron.
#
# What this script does:
#   Reads the activation_timestamp from PROVENANCE_LEDGER entry 1735 (the
#   GCMN_ACTIVATION_OPERATOR_HITL_RATIFIED record). Computes deadline =
#   activation_timestamp + 90 days. If `now` is past the deadline:
#     * Tier 1 (recovery-model, default — consecutive_counter <= 0):
#         - Append sweep_tier1_<timestamp> marker to PROVENANCE_LEDGER.md
#         - Flip Plan.json status: SUNSET_TIER1
#         - Set Plan.json.operator_signoff.expired=true, expired_reason=tier1
#         - This run is recoverable: re-flipping CAMELOT_GCMN_STUBS_ENABLED=1
#           (operator's runtime act) keeps the stub path live.
#     * Tier 2 (destructive, after one consecutive unrecovered Tier-1 cycle):
#         - Same as Tier 1, plus:
#         - Permanently prune the GCMN_STUB_RUNES entries from
#           control_plane/runic_router.py (atomic Python rewrite)
#         - Set Plan.json.status: ARCHIVED_ABANDONED
#     * Renewal hook (`--renew`):
#         - Append ASR record to PROVENANCE_LEDGER.md; resets the
#           consecutive-cycle counter to zero.
#
# Activation ADR §7 contract:
#   * implicit_rollover_allowed = false (must explicitly renew)
#   * The script NEVER auto-unset CAMELOT_GCMN_STUBS_ENABLED on the
#     operator's shell — that is a runtime act between operator and their
#     .env file. The cron reports the sunset to stderr and updates Plan.json
#     so an external operator can act.
#
# Schedule: install as a daily cron job. Idempotent — re-running after a
# completed Tier 1/2 phase is a no-op (the script exits cleanly).
#
# Exit codes:
#   0 — success (before-deadline no-op; renewal recorded; Tier N applied).
#   1 — FATAL (activation_timestamp not found; Plan.json parse fail;
#       Python reraise).
set -euo pipefail

# Locate CAMELOT_HOME relative to this script (../)
CAMELOT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEDGER_FILE="${CAMELOT_HOME}/docs/PROVENANCE_LEDGER.md"
PLAN_FILE="${CAMELOT_HOME}/docs/seeds/gcmn_vmax_nano_seed/Plan.json"
ROUTER_FILE="${CAMELOT_HOME}/control_plane/runic_router.py"

log() {
    echo "sweep_inert_stubs: $*" >&2
}

# ---------------------------------------------------------------------------
# 1. Renewal hook (`--renew`): exit fast before any other logic.
# ---------------------------------------------------------------------------
if [[ "${1:-}" == "--renew" ]]; then
    now_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "| ${now_iso} | SYSTEM | ASR: Activation Sunset Renewal; consecutive_counter reset to 0 | RENEWED |" >> "${LEDGER_FILE}"
    log "Renewal recorded at ${now_iso}. Sunset deadline reset."
    exit 0
fi

if [[ ! -f "${LEDGER_FILE}" ]]; then
    log "FATAL: PROVENANCE_LEDGER.md not found at ${LEDGER_FILE}. Cannot determine activation_timestamp."
    exit 1
fi
if [[ ! -f "${PLAN_FILE}" ]]; then
    log "FATAL: Plan.json not found at ${PLAN_FILE}. Cannot update status field."
    exit 1
fi
if [[ ! -f "${ROUTER_FILE}" ]]; then
    log "FATAL: runic_router.py not found at ${ROUTER_FILE}."
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Discovery, deadline computation, tier selection — delegated to Python
#    for atomic rewrite safety + ISO-8601 date math + robust JSON handling.
# ---------------------------------------------------------------------------
python3 - "${LEDGER_FILE}" "${PLAN_FILE}" "${ROUTER_FILE}" <<'PYEOF'
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ledger_path = Path(sys.argv[1])
plan_path = Path(sys.argv[2])
router_path = Path(sys.argv[3])

ledger_text = ledger_path.read_text(encoding="utf-8")
ACTIVATION_EVENT = "GCMN_ACTIVATION_OPERATOR_HITL_RATIFIED"

# Activation timestamp lives in PROVENANCE_LEDGER entry 1735 under the
# `**Timestamp**:` bullet. We accept either the canonical `2026-07-15T05:30:00Z`
# format or the line-prefixed `| ISO |` form (defensive — older entries may
# carry either).
match = re.search(
    rf"{ACTIVATION_EVENT}[\s\S]{{0,800}}?\*\*Timestamp\*\*:\s*([0-9T:Z\-]+)",
    ledger_text,
)
if not match:
    match = re.search(
        rf"{ACTIVATION_EVENT}[\s\S]{{0,800}}?\|\s*(20[0-9]{{2}}-[0-9T:Z\-]+)\s*\|",
        ledger_text,
    )
if not match:
    print("sweep_inert_stubs: FATAL: activation_timestamp not found in ledger.", file=sys.stderr)
    sys.exit(1)

activation_str = match.group(1).strip()
try:
    activation_dt = datetime.strptime(activation_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
except ValueError:
    try:
        activation_dt = datetime.fromisoformat(activation_str.replace("Z", "+00:00"))
    except ValueError:
        print(f"sweep_inert_stubs: FATAL: failed to parse timestamp {activation_str!r}.", file=sys.stderr)
        sys.exit(1)

now = datetime.now(timezone.utc)
deadline = activation_dt + timedelta(days=90)

if now < deadline:
    print(
        f"sweep_inert_stubs: Before deadline ({deadline.isoformat()}); no action.",
        file=sys.stderr,
    )
    sys.exit(0)

# Tier selection:
#   consecutive_counter = (count of prior sweep_tier1 markers) - (count of ASR renewals)
# When counter <= 0, fire Tier 1 (the first sunset).
# When counter >= 1, fire Tier 2 (after one consecutive unrecovered cycle).
sweep_tier1_count = len(re.findall(r"sweep_tier1_\d{4}-\d{2}-\d{2}", ledger_text))
asr_count = len(re.findall(r"ASR: Activation Sunset Renewal", ledger_text))
consecutive_counter = sweep_tier1_count - asr_count
print(
    f"sweep_inert_stubs: deadline passed; consecutive_counter={consecutive_counter}; "
    f"prior_tier1={sweep_tier1_count}; renewals={asr_count}",
    file=sys.stderr,
)

# Plan.json: load + flip status + write atomically.
import json
try:
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
except Exception as e:
    print(f"sweep_inert_stubs: FATAL: Plan.json parse failed: {e}", file=sys.stderr)
    sys.exit(1)

now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
op_signoff = plan.setdefault("operator_signoff", {})
op_signoff["expired"] = True

if consecutive_counter <= 0:
    plan["status"] = "SUNSET_TIER1"
    op_signoff["expired_reason"] = "tier1 sunset reached without operator ratification"
    plan.setdefault("notes", []).append(
        f"Sweep @ {now_iso}: Tier 1 sunset reached (deadline {deadline.isoformat()})."
    )
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(
            f"\n| {now_iso} | SYSTEM | SUNSET: sweep_tier1_{now_iso} "
            f"(non-destructive; recoverable by re-flipping CAMELOT_GCMN_STUBS_ENABLED=1) | EXPIRED |\n"
        )
    print("sweep_inert_stubs: Tier 1 applied. Recovery model: re-flip env-var to reactivate.", file=sys.stderr)
    sys.exit(0)

# Tier 2 — destructive: prune GCMN_STUB_RUNES from runic_router.py.
print(
    "sweep_inert_stubs: Triggering Tier 2 (destructive). Pruning GCMN_STUB_RUNES entries from "
    "control_plane/runic_router.py.",
    file=sys.stderr,
)
plan["status"] = "ARCHIVED_ABANDONED"
op_signoff["expired_reason"] = "tier2 sunset reached after consecutive unrecovered cycle"
plan.setdefault("notes", []).append(
    f"Sweep @ {now_iso}: Tier 2 sunset (destructive). GCMN_STUB_RUNES pruned from runic_router.py."
)
with open(plan_path, "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=2, ensure_ascii=False)
    f.write("\n")

# Pruning the GCMN_STUB_RUNES literal-block. Runic_router.py declares:
#   GCMN_STUB_RUNES: dict[str, dict[str, Any]] = {
#       "//SYNC_KBA_DATABASES_SQLCIPHER": {
#           "knight_hint": "sir_sentinel",
#           ...inner-dict has its own closing brace...
#       },
#       ...
#   }
# We MUST anchor on the column-0 outer closing brace (^\} with MULTILINE)
# rather than `\n\}` to avoid terminating at an inner-dict closing brace.
# The non-greedy [\s\S]*? requires an anchor that is unambiguous; the column-0
# close brace anchors only at the outermost `}`.
router_text = router_path.read_text(encoding="utf-8")
pattern = re.compile(
    r"GCMN_STUB_RUNES:\s*dict\[str,\s*dict\[str,\s*Any\]\]\s*=\s*\{[\s\S]*?^\}",
    re.MULTILINE,
)
match_router = pattern.search(router_text)
if not match_router:
    print(
        "sweep_inert_stubs: WARNING: GCMN_STUB_RUNES literal block not found; skipping prune.",
        file=sys.stderr,
    )
else:
    new_router_text = pattern.sub(
        r"# PRUNED by bin/sweep_inert_stubs.sh at " + now_iso + "\nGCMN_STUB_RUNES: dict[str, dict[str, Any]] = {}\n",
        router_text,
        count=1,
    )
    if new_router_text == router_text:
        print(
            "sweep_inert_stubs: WARNING: GCMN_STUB_RUNES prune produced no diff; skipping write.",
            file=sys.stderr,
        )
    else:
        router_path.write_text(new_router_text, encoding="utf-8")
        print(
            f"sweep_inert_stubs: Pruned GCMN_STUB_RUNES ({len(pattern.findall(router_text))} entries).",
            file=sys.stderr,
        )

with open(ledger_path, "a", encoding="utf-8") as f:
    f.write(
        f"\n| {now_iso} | SYSTEM | SUNSET: prune_{now_iso} (Tier 2 destructive; "
        f"GCMN_STUB_RUNES pruned from runic_router.py) | ARCHIVED |\n"
    )

print("sweep_inert_stubs: Tier 2 applied. Status: ARCHIVED_ABANDONED.", file=sys.stderr)
PYEOF
