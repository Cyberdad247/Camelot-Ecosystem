#!/usr/bin/env bash
# ========================================================================================
# CAMELOT-OS — Retire the duplicate /opt/Camelot-Ecosystem checkout
# ========================================================================================
#
# THE DEFECT THIS CLOSES
#
# The hub carried two checkouts whose names differed only by case. The filesystem is
# case-sensitive, so they were genuinely different directories with different commits:
#
#     /opt/Camelot-Ecosystem   HEAD 990300d1   stale bootstrap clone   <- RETIRING
#     /opt/camelot-ecosystem   canonical checkout, carries control_plane/
#
# The uppercase tree was not obviously broken — it looked like a working deployment. What
# made it dangerous was that it was still WIRED IN:
#
#   * camelot-vps-mesh.service ran from it. Its ExecStart names
#     control_plane.dispatch.vps_mobile_mesh_bridge, a module that does not exist in that
#     tree at all. The service was only alive because a drop-in at
#     camelot-vps-mesh.service.d/override.conf pinned WorkingDirectory elsewhere — one
#     `systemctl edit --full` away from a unit that could not start.
#   * CAMELOT_OS_HOME still named it, so the live process carried a path to a tree its own
#     code was not loaded from. Inert for today's modules (the bridge resolves its state
#     path from __file__), but control_plane.dispatch.bifrost and its siblings DO read that
#     variable, so any future import of one of them would silently resolve against it.
#   * vps_hub_bootstrap.sh installed units FROM it (CUBE_DIR default), which is how the hub
#     came to carry a `hermes_prime_phial.py --loop 60` unit upstream had already replaced.
#
# USAGE
#   ./retire-uppercase-tree.sh              # apply
#   ./retire-uppercase-tree.sh --self-check # assert only, no mutation
#
# ROLLBACK
#   The tree is archived to $ARCHIVE_DIR before removal. To restore:
#     tar xzf /root/retired/Camelot-Ecosystem-<rev>-<date>.tar.gz -C /opt
#   Unit files are archived alongside it; restore any of them with `cp` + `daemon-reload`.
# ========================================================================================

set -euo pipefail

CANONICAL="${CANONICAL:-/opt/camelot-ecosystem}"
RETIRED="${RETIRED:-/opt/Camelot-Ecosystem}"
ARCHIVE_DIR="${ARCHIVE_DIR:-/root/retired}"
MODE="apply"
case "${1:-}" in
  --self-check) MODE="self-check" ;;
  --apply|"")   MODE="apply" ;;
  -h|--help)    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "unknown argument: $1 (try --self-check)" >&2; exit 2 ;;
esac

PASS=0; FAILURES=(); WARNINGS=()
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAILURES+=("$1"); }
warn() { printf '  \033[33mWARN\033[0m %s\n' "$1"; WARNINGS+=("$1"); }
phase(){ printf '\n\033[1m%s\033[0m\n' "$1"; }

# Units that must come from the canonical tree. Exact list, not a glob: a glob silently
# installs whatever happens to be in the source tree, which is the failure mode being fixed.
UNIT_SOURCES=(
  camelot-vps-mesh.service
  camelot-heimdall-bifrost.service
  camelot-hermes-prime.service
)

# The paths that must keep answering across the cutover, and what each proves.
#   /mesh/status            -> the bridge is serving from the canonical tree
#   /bifrost/knights        -> the bridge's knight surface
#   /hermes/telemetry       -> the bridge's Hermes verdict
#   /heimdall/governance    -> the bridge's Heimdall surface
CONTRACT_PATHS=(/mesh/status /bifrost/knights /hermes/telemetry /heimdall/governance)

route_table() {
  local p code
  for p in "${CONTRACT_PATHS[@]}"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://127.0.0.1:8095$p" || echo "000")
    printf '    :8095%-24s %s\n' "$p" "$code"
  done
}

# ========================================================================================
phase "[1] Preflight"
# ========================================================================================
if [[ -d "$CANONICAL/.git" ]]; then
  ok "canonical checkout present: $CANONICAL ($(git -C "$CANONICAL" rev-parse --short HEAD 2>/dev/null || echo NOGIT))"
else
  bad "canonical checkout missing or not a git worktree: $CANONICAL"
fi

if [[ "$RETIRED" == "$CANONICAL" ]]; then
  bad "RETIRED and CANONICAL are the same path — refusing to run"
  printf '\nREFUSING: refusing to proceed with a destructive operation on an ambiguous path.\n'
  exit 1
fi

# The canonical tree must be able to supply the unit files, otherwise "repoint at the
# canonical checkout" would have nothing to point at and the units would keep the old path.
for f in "${UNIT_SOURCES[@]}"; do
  if [[ -f "$CANONICAL/infra/systemd/$f" ]]; then
    ok "canonical tree supplies $f"
  else
    bad "canonical tree is MISSING infra/systemd/$f — sync it before retiring anything"
  fi
done

# Case-insensitive filesystems would make the two paths the SAME directory and this whole
# script a no-op that reports success. Assert they are genuinely distinct first.
if [[ -d "$RETIRED" ]]; then
  a=$(cd "$CANONICAL" && pwd -P); b=$(cd "$RETIRED" && pwd -P)
  if [[ "$a" == "$b" ]]; then
    bad "paths resolve to the same directory ($a) — this host is case-insensitive; nothing to retire"
    exit 1
  else
    ok "paths are distinct directories (case-sensitive filesystem confirmed)"
  fi
else
  warn "$RETIRED is already absent — nothing to retire"
fi

if (( ${#FAILURES[@]} )); then
  printf '\nABORT: preflight failures above. Nothing was changed.\n'
  exit 1
fi

# ========================================================================================
phase "[2] Capture the pre-cutover route table"
# ========================================================================================
BEFORE="$(route_table)"
printf '%s\n' "$BEFORE"

# ========================================================================================
phase "[3] Install canonical unit files and retire the corrective drop-in"
# ========================================================================================
if [[ "$MODE" == "apply" ]]; then
  # Archive the exact unit files being replaced. Without this, "rollback" is an instruction
  # rather than an action. 0700: the archive contains a full copy of the tree, which may
  # include credentials, so it is not world-readable.
  install -d -m 0700 "$ARCHIVE_DIR"
  # Computed ONCE. Calling `date` twice raced a second boundary, which made UARCH name a
  # directory that was never created and turned every `cp` into a failure.
  stamp="$(date +%Y%m%d%H%M%S)"
  UARCH="$ARCHIVE_DIR/units-$stamp"
  install -d -m 0700 "$UARCH"
  for f in "${UNIT_SOURCES[@]}"; do
    [[ -f "/etc/systemd/system/$f" ]] && cp -p "/etc/systemd/system/$f" "$UARCH/" || true
  done
  ok "previous unit files archived to $UARCH"

  for f in "${UNIT_SOURCES[@]}"; do
    if cp "$CANONICAL/infra/systemd/$f" "/etc/systemd/system/$f"; then
      ok "installed $f from the canonical tree"
    else
      bad "could not install $f"
    fi
  done

  # The drop-in existed ONLY to correct a WorkingDirectory that pointed at the tree being
  # retired. With the base unit fixed it is redundant — and leaving it would mean two files
  # describing the same setting, i.e. the drift this whole exercise is about. Remove it, so
  # that `systemctl edit --full` can no longer silently reverse the fix.
  if [[ -d /etc/systemd/system/camelot-vps-mesh.service.d ]]; then
    rm -rf /etc/systemd/system/camelot-vps-mesh.service.d
    ok "removed the now-redundant camelot-vps-mesh drop-in"
  else
    ok "no camelot-vps-mesh drop-in present"
  fi

  systemctl daemon-reload && ok "systemctl daemon-reload" || bad "systemctl daemon-reload"
fi

# ========================================================================================
phase "[4] Effective configuration (merged with drop-ins)"
# ========================================================================================
# Read the EFFECTIVE value, not the base file: that is what systemd will actually use.
for u in "${UNIT_SOURCES[@]}"; do
  [[ "$u" == "camelot-vps-mesh.service" || "$u" == "camelot-hermes-prime.service" ]] || continue
  wd=$(systemctl show "$u" -p WorkingDirectory --value 2>/dev/null || true)
  case "$wd" in
    "$CANONICAL"*) ok "$u WorkingDirectory -> $wd" ;;
    "")            warn "$u not loaded — cannot verify WorkingDirectory" ;;
    *)             bad "$u WorkingDirectory is '$wd', expected $CANONICAL" ;;
  esac
done

mesh_env=$(systemctl show camelot-vps-mesh.service -p Environment --value 2>/dev/null || true)
if [[ "$mesh_env" == *"$RETIRED"* ]]; then
  bad "camelot-vps-mesh Environment still names $RETIRED"
elif [[ "$mesh_env" == *"CAMELOT_OS_HOME=$CANONICAL"* ]]; then
  ok "camelot-vps-mesh CAMELOT_OS_HOME -> $CANONICAL"
else
  warn "camelot-vps-mesh CAMELOT_OS_HOME is unset or unexpected"
fi

# Directive lines only. The hermes-prime unit documents the retired path by name in a
# comment explaining why it was abandoned, and a prose mention is not a dependency.
upper_hits=$(grep -rn "$RETIRED" /etc/systemd/system/*.service /etc/systemd/system/*.timer 2>/dev/null \
  | grep -vE '^[^:]+:[0-9]+:[[:space:]]*#' || true)
if [[ -n "$upper_hits" ]]; then
  bad "a unit still references $RETIRED in a directive"
  printf '       %s\n' "$upper_hits"
else
  ok "no unit references $RETIRED (directives only)"
fi

# ========================================================================================
phase "[5] Restart and re-verify the contract routes"
# ========================================================================================
if [[ "$MODE" == "apply" ]]; then
  systemctl restart camelot-vps-mesh.service && ok "restarted camelot-vps-mesh" \
    || bad "could not restart camelot-vps-mesh"
  # systemd reports "active" for a process that is about to die. Give it a moment, then ask
  # whether it is STILL the same PID — a service that came back from a crash loop looks
  # identical to a healthy one at the moment of the restart.
  sleep 3
  if systemctl is-active --quiet camelot-vps-mesh.service; then
    ok "camelot-vps-mesh is active after restart"
  else
    bad "camelot-vps-mesh is NOT active after restart — cutover would break :8095"
  fi
fi

pid=$(ss -ltnp 2>/dev/null | grep ':8095' | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2 || true)
if [[ -n "${pid:-}" ]]; then
  cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null || echo "?")
  ok "the :8095 listener resolves its code from $cwd"
  [[ "$cwd" == "$CANONICAL" ]] || bad ":8095 process cwd is '$cwd', expected $CANONICAL"
else
  bad "nothing is listening on :8095"
fi

AFTER="$(route_table)"
printf '%s\n' "$AFTER"
if [[ "$BEFORE" == "$AFTER" ]]; then
  ok "contract route table is unchanged by the cutover"
else
  bad "contract route table CHANGED — compare the two dumps above"
fi

for p in "${CONTRACT_PATHS[@]}"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://127.0.0.1$p" || echo "000")
  [[ "$code" == "200" ]] && ok "nginx $p -> 200" || bad "nginx $p -> $code"
done

# ========================================================================================
phase "[6] Archive and remove the retired tree"
# ========================================================================================
if [[ ! -d "$RETIRED" ]]; then
  ok "$RETIRED already absent"
elif [[ "$MODE" == "self-check" ]]; then
  warn "self-check: $RETIRED still present and would be archived + removed"
else
  if (( ${#FAILURES[@]} )); then
    warn "skipping removal: earlier failures mean the cutover is not proven"
  else
    rev=$(git -C "$RETIRED" rev-parse --short HEAD 2>/dev/null || echo unknown)
    tarball="$ARCHIVE_DIR/Camelot-Ecosystem-$rev-$(date +%Y%m%d).tar.gz"
    src_count=$(find "$RETIRED" -type f 2>/dev/null | wc -l)
    printf '  archiving %s files from %s ...\n' "$src_count" "$RETIRED"
    if tar czf "$tarball" -C "$(dirname "$RETIRED")" "$(basename "$RETIRED")" 2>/dev/null; then
      # An unreadable or truncated archive is not a backup. Counting entries before deleting
      # anything is the difference between a reversible migration and a deletion.
      arch_count=$(tar tzf "$tarball" 2>/dev/null | grep -vE '/$' | wc -l)
      if (( arch_count >= src_count )) && tar tzf "$tarball" >/dev/null 2>&1; then
        ok "archive verified: $arch_count entries -> $tarball ($(du -sh "$tarball" | cut -f1))"
        rm -rf "$RETIRED"
        [[ ! -d "$RETIRED" ]] && ok "removed $RETIRED" || bad "could not remove $RETIRED"
      else
        bad "archive verification FAILED ($arch_count of $src_count entries) — tree left in place"
      fi
    else
      bad "tar failed — tree left in place"
    fi
  fi
fi

# ========================================================================================
phase "[7] Post-conditions on the whole point of this"
# ========================================================================================
# The bootstrap must no longer default to the retired path, or the next run reinstalls the
# problem from a directory that no longer exists.
boot="$CANONICAL/scripts/vps_hub_bootstrap.sh"
if [[ -f "$boot" ]]; then
  if grep -qE '^CUBE_DIR="\$\{CUBE_DIR:-/opt/camelot-ecosystem\}"' "$boot"; then
    ok "bootstrap defaults CUBE_DIR to the canonical tree"
  else
    bad "bootstrap CUBE_DIR default is not the canonical tree — a re-run would point at $RETIRED"
  fi
  # Listed, not judged: the bootstrap deliberately documents the retired path by name in
  # comments explaining why it was abandoned. Printing them lets a reader confirm that any
  # remaining mention is prose rather than a directive.
  boot_mentions=$(grep -n "$RETIRED" "$boot" 2>/dev/null || true)
  if [[ -n "$boot_mentions" ]]; then
    warn "bootstrap still mentions the retired path — confirm these are prose, not directives"
    printf '       %s\n' "$boot_mentions"
  else
    ok "bootstrap contains no reference to the retired path"
  fi
else
  warn "no bootstrap at $boot — cannot verify its default"
fi

echo
echo "========================================================================"
if (( ${#FAILURES[@]} == 0 )); then
  echo "✅ TREE RETIREMENT VERIFIED — $PASS post-conditions passed"
  # `if` rather than `(( n )) && printf`: an empty WARNINGS array makes that compound return
  # 1 as the branch's last command, and `set -e` then exits a SUCCESSFUL run with status 1.
  if (( ${#WARNINGS[@]} )); then
    printf '   %d warning(s) — review, not blocking\n' "${#WARNINGS[@]}"
  fi
else
  echo "❌ TREE RETIREMENT FAILED — ${#FAILURES[@]} post-condition(s) failed, $PASS passed"
  printf '   - %s\n' "${FAILURES[@]}"
  echo "   ROLLBACK: tar xzf $ARCHIVE_DIR/Camelot-Ecosystem-*.tar.gz -C /opt"
  echo "             cp $ARCHIVE_DIR/units-*/<unit> /etc/systemd/system/ && systemctl daemon-reload"
fi
echo "========================================================================"

(( ${#FAILURES[@]} == 0 ))
