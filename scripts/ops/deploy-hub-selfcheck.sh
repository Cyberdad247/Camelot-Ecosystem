#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Deploy the Camelot-OS hub self-check to the hub. Idempotent; safe to re-run.
#
# Why the artifacts land in /usr/local/lib/camelot rather than in a git checkout:
# the hub carries two divergent checkouts whose names differ only by case, and a
# `git pull` in either one can overwrite working-tree files. An operational asset that
# a pull can silently revert is the exact failure mode this whole exercise is about, so
# the deployed copy lives outside both trees.
#
# The tradeoff is staleness, and it is handled rather than ignored: the runner records
# `audit_sha256` for the deployed audit in status.json, so a deployed copy that has
# fallen behind the repository is visible in the status artifact.
#
# Usage:
#   bash scripts/ops/deploy-hub-selfcheck.sh            # deploy
#   CAMELOT_HUB=user@host bash scripts/ops/deploy-hub-selfcheck.sh

set -euo pipefail

HUB="${CAMELOT_HUB:-root@162.35.107.134}"
LIB=/usr/local/lib/camelot
STATE=/var/lib/camelot/selfcheck
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

SSH=(ssh -o BatchMode=yes -o ConnectTimeout=15 "$HUB")
SCP=(scp -o BatchMode=yes -o ConnectTimeout=15)

say() { printf '\n\033[1m%s\033[0m\n' "$1"; }

say "1) preflight: shell sources parse"
# Only shell is checked here. Unit files are NOT shell and must not be run through
# `bash -n` — it fails on innocuous things like `Description=... (parenthetical)` and a
# suppressed failure teaches you to ignore the check. Units are verified on the hub
# with `systemd-analyze verify`, which is the tool that actually knows the grammar.
for f in "$REPO_ROOT/scripts/vps_hub_bootstrap.sh" \
         "$REPO_ROOT/scripts/ops/hub-selfcheck.sh"; do
  [[ -f "$f" ]] || { echo "  MISSING $f" >&2; exit 1; }
  bash -n "$f" || { echo "  SYNTAX FAIL $f" >&2; exit 1; }
  echo "  ok $f"
done
for f in "$REPO_ROOT/infra/systemd/camelot-selfcheck.service" \
         "$REPO_ROOT/infra/systemd/camelot-selfcheck.timer" \
         "$REPO_ROOT/infra/systemd/camelot-selfcheck-alert.service" \
         "$REPO_ROOT/infra/systemd/camelot-selfcheck-watchdog.service" \
         "$REPO_ROOT/infra/systemd/camelot-selfcheck-watchdog.timer"; do
  [[ -f "$f" ]] || { echo "  MISSING $f" >&2; exit 1; }
  echo "  ok $f"
done

say "2) install state + library dirs"
"${SSH[@]}" "mkdir -p '$LIB' '$STATE' && chmod 0755 '$LIB' '$STATE' && echo '  dirs ready'"

say "3) deploy the audit and the runner"
"${SCP[@]}" "$REPO_ROOT/scripts/vps_hub_bootstrap.sh" "$HUB:$LIB/vps_hub_bootstrap.sh"
"${SCP[@]}" "$REPO_ROOT/scripts/ops/hub-selfcheck.sh"  "$HUB:$LIB/hub-selfcheck.sh"
"${SSH[@]}" "chmod 0755 '$LIB/vps_hub_bootstrap.sh' '$LIB/hub-selfcheck.sh' && ls -la '$LIB' | tail -n +2"

say "3b) post-condition: the deployed scripts can actually execute on Linux"
# This is the check whose absence let a CRLF working copy ship. A CR byte in a shebang
# makes `/usr/bin/env bash\r` unresolvable, so the script exits 127 without running —
# and an audit that never ran reports ZERO failures, which is indistinguishable from a
# healthy hub at every layer above it. `bash -n` passes on a CRLF file, and a grep-based
# check is unreliable on the Windows host, so the bytes are counted directly.
"${SSH[@]}" "rc=0
  for f in $LIB/vps_hub_bootstrap.sh $LIB/hub-selfcheck.sh; do
    n=\$(tr -cd '\r' < \"\$f\" | wc -c)
    if [ \"\$n\" -ne 0 ]; then
      echo \"  FAIL \$f carries \$n CR byte(s) — its shebang cannot execute on Linux\"
      rc=1
    fi
  done
  [ \"\$rc\" -eq 0 ] && echo '  ok deployed scripts are LF'
  exit \$rc"

say "4) install units"
for u in camelot-selfcheck.service camelot-selfcheck.timer camelot-selfcheck-alert.service \
         camelot-selfcheck-watchdog.service camelot-selfcheck-watchdog.timer; do
  "${SCP[@]}" "$REPO_ROOT/infra/systemd/$u" "$HUB:/etc/systemd/system/$u"
  echo "  ok $u"
done
"${SSH[@]}" "systemctl daemon-reload && echo '  daemon-reload ok'"

say "5) verify unit syntax with the tool that knows the grammar"
# systemd-analyze verify exits non-zero for genuine errors; warnings (e.g. references to
# units that are not installed on this host) are reported but do not block the deploy.
"${SSH[@]}" "for u in camelot-selfcheck.service camelot-selfcheck.timer camelot-selfcheck-alert.service \
    camelot-selfcheck-watchdog.service camelot-selfcheck-watchdog.timer; do
    out=\$(systemd-analyze verify \"/etc/systemd/system/\$u\" 2>&1)
    if [ -z \"\$out\" ]; then echo \"  ok \$u\"; else echo \"  WARN \$u: \$(echo \"\$out\" | head -3 | tr '\n' ' ')\"; fi
  done"

say "6) enable both timers (services are timer-driven, not enabled directly)"
# The watchdog timer is enabled alongside the audit timer: a dead-man's switch that is
# not enabled is not a switch.
"${SSH[@]}" "systemctl enable --now camelot-selfcheck.timer camelot-selfcheck-watchdog.timer 2>&1 | tail -2"

say "7) verify: run the audit once and report honestly"
# The audit is EXPECTED to fail while the hub is not production-ready; a non-zero exit
# here is a result, not a deploy failure, so it is reported rather than raised.
"${SSH[@]}" "systemctl start camelot-selfcheck.service; rc=\$?; \
  if [ \"\$rc\" -eq 126 ] || [ \"\$rc\" -eq 127 ]; then \
    echo \"  unit exit: \$rc\"; \
    echo '  FATAL: the audit could not execute. 126/127 is a DEPLOY defect, not a'; \
    echo '         failing post-condition — and it reports zero failures, which reads'; \
    echo '         exactly like a healthy hub. Refusing to report success.'; \
    exit 1; \
  fi; \
  echo \"  unit exit: \$rc\"; \
  echo \"  unit state: \$(systemctl is-active camelot-selfcheck.service) / \$(systemctl is-failed camelot-selfcheck.service)\"; \
  echo; \
  echo '  status.json:'; \
  python3 -c \"import json;d=json.load(open('$STATE/status.json'));print('    ok:',d['ok']);print('    failures:',d['failure_count']);print('    warnings:',d['warning_count']);print('    audit_sha256:',d['audit_sha256'])\"; \
  echo; \
  echo '  watchdog (validates the monitor itself):'; \
  /usr/local/lib/camelot/hub-selfcheck.sh watchdog || true; \
  echo; \
  echo '  timers:'; \
  systemctl list-timers camelot-selfcheck.timer camelot-selfcheck-watchdog.timer --no-pager | head -3"

say "8) alert reachability"
# A notification that only reaches root's mailbox on the hub IS a real delivery, but it
# is not a notification to a person. Saying so at deploy time stops an operator from
# assuming alerting is wired because the units are enabled — which is the same
# "installed is not running" mistake this whole layer exists to catch.
"${SSH[@]}" "if ls /etc/systemd/system/camelot-selfcheck-alert.service.d/*.conf >/dev/null 2>&1; then
    echo '  remote channel configured:'
    grep -hE 'Environment=' /etc/systemd/system/camelot-selfcheck-alert.service.d/*.conf | sed 's/^/    /'
  else
    echo '  WARN no remote alert channel: alerts land in the root mailbox on this host and in the journal.'
    echo '       To reach a person:  systemctl edit camelot-selfcheck-alert'
    echo '       and set  Environment=CAMELOT_ALERT_EMAIL=you@example.com'
    echo '       or       Environment=CAMELOT_ALERT_WEBHOOK=https://...'
  fi"
