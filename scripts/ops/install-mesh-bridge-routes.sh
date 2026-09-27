#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Install the mesh bridge routes (`/mesh/status`, `/bifrost/knights`) into the hub's nginx
# ingress, from the versioned snippet in infra/nginx/.
#
# WHY THIS SCRIPT EXISTS RATHER THAN A HAND EDIT
#
# The hub's server block is `/etc/nginx/sites-enabled/hermesagent.conf`, written by the
# Hermes installer and versioned nowhere. Editing it in place produces an operational
# asset that exists on one machine only: a re-install, or a regenerated config, silently
# reverts the routes and the two client endpoints go back to answering 302 and 404. The
# versioned snippet plus this installer makes the change reproducible — and because both
# endpoints are already post-conditions of `vps_hub_bootstrap.sh --self-check`, a reverted
# route now fails the audit and raises an alert instead of going unnoticed.
#
# The include goes INSIDE the server block, not in /etc/nginx/conf.d/: conf.d is included
# in the `http` context, where a `location` directive is not valid.
#
# Idempotent; safe to re-run.
#
# Usage:
#   bash scripts/ops/install-mesh-bridge-routes.sh
#   CAMELOT_HUB=user@host bash scripts/ops/install-mesh-bridge-routes.sh

set -euo pipefail

HUB="${CAMELOT_HUB:-root@162.35.107.134}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SNIPPET_SRC="$REPO_ROOT/infra/nginx/camelot-mesh-bridge.conf"

SNIPPET_DST=/etc/nginx/snippets/camelot-mesh-bridge.conf
SITE=/etc/nginx/sites-enabled/hermesagent.conf
AVAIL=/etc/nginx/sites-available/hermesagent.conf
INCLUDE_LINE='    include /etc/nginx/snippets/camelot-mesh-bridge.conf;'

# Backups MUST NOT live in sites-enabled/ or conf.d/: both are pulled in by `include`
# globs, so a backup taken there is itself loaded as a live config. A backup of a site
# containing `listen 80 default_server` therefore becomes a SECOND default server and
# takes the whole ingress down on the next reload — which is exactly what happened on the
# first run of this script, and why `nginx -t` is run before every reload.
BACKUP_DIR=/etc/nginx/backups
# Directories nginx includes wholesale; nothing may be parked in them.
INCLUDE_GLOBS=(/etc/nginx/sites-enabled /etc/nginx/conf.d)

# Paths whose behaviour must NOT change. `/bifrost/` and `/ws` belong to the Bifrost
# gateway on :3001; `/` is the Hermes dashboard. The bug being fixed was a missing route,
# so the risk of the fix is a route that now shadows one of these.
UNTOUCHED=(/ /bifrost/ /ws)

SSH=(ssh -o BatchMode=yes -o ConnectTimeout=15 "$HUB")
SCP=(scp -o BatchMode=yes -o ConnectTimeout=15)
STAMP="$(date -u +%Y%m%d%H%M%S)"
SITE_BACKUP="$BACKUP_DIR/hermesagent.conf.bak-$STAMP"
AVAIL_BACKUP="$BACKUP_DIR/hermesagent.conf.sites-available.bak-$STAMP"
SNIPPET_BACKUP="$BACKUP_DIR/camelot-mesh-bridge.conf.bak-$STAMP"
install_started=0
install_committed=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

say() { printf '\n\033[1m%s\033[0m\n' "$1"; }
die() { printf '  FAIL %s\n' "$1" >&2; exit 1; }

restore_install() {
  "${SSH[@]}" "if [ -e '$SNIPPET_BACKUP' ] || [ -L '$SNIPPET_BACKUP' ]; then rm -f '$SNIPPET_DST'; cp -a '$SNIPPET_BACKUP' '$SNIPPET_DST'; else rm -f '$SNIPPET_DST'; fi" || true
  "${SSH[@]}" "if [ -e '$SITE_BACKUP' ] || [ -L '$SITE_BACKUP' ]; then rm -f '$SITE'; cp -a '$SITE_BACKUP' '$SITE'; else rm -f '$SITE'; fi" || true
  "${SSH[@]}" "if [ -e '$AVAIL_BACKUP' ] || [ -L '$AVAIL_BACKUP' ]; then rm -f '$AVAIL'; cp -a '$AVAIL_BACKUP' '$AVAIL'; fi" || true
  "${SSH[@]}" "nginx -t && systemctl reload nginx" || true
}

rollback_on_exit() {
  if (( install_started && ! install_committed )); then
    restore_install
  fi
  rm -rf "$TMP"
}

trap rollback_on_exit EXIT

# One batched probe: `path|status|bytes|identifying headers`. Batching keeps the baseline
# and the comparison consistent (same moment, same method) rather than 12 separate
# round-trips that can straddle a reload.
probe() {
  local paths="$1"
  "${SSH[@]}" "for p in $paths; do
      code=\$(curl -s -o /dev/null -m 5 -w '%{http_code}' http://localhost\$p 2>/dev/null || echo 000)
      size=\$(curl -s -o /dev/null -m 5 -w '%{size_download}' http://localhost\$p 2>/dev/null || echo 0)
      hdr=\$(curl -sI -m 5 http://localhost\$p 2>/dev/null | tr -d '\r' | grep -iE '^(server|x-powered-by):' | tr -d ' ' | tr '\n' ',')
      echo \"\$p|\$code|\$size|\$hdr\"
    done"
}

say "1) preflight: the snippet exists, is LF-clean, and carries both locations"
[[ -f "$SNIPPET_SRC" ]] || die "missing $SNIPPET_SRC"
# A CR would ship verbatim and nginx would reject the include — which on reload takes the
# whole ingress down. `tr` counts raw bytes; grep is unreliable on this host.
cr=$(tr -cd '\r' < "$SNIPPET_SRC" | wc -c | tr -d ' ')
[[ "$cr" -eq 0 ]] || die "$SNIPPET_SRC carries $cr CR byte(s); nginx would reject it"
# The four paths the lab deploy's own check_endpoint calls verify. If the snippet loses
# one, the deploy script fails its own contract — so make that a preflight failure here.
CONTRACT_PATHS=(/mesh/status /bifrost/knights /hermes/telemetry /heimdall/governance)
for p in "${CONTRACT_PATHS[@]}"; do
  grep -qF "location = $p" "$SNIPPET_SRC" || die "snippet lacks a route for $p"
done
echo "  ok $(basename "$SNIPPET_SRC") — LF, all ${#CONTRACT_PATHS[@]} contract locations present"

say "2) baseline: how each path answers BEFORE the change"
probe "/ /bifrost/ /ws /mesh/status /bifrost/knights" | tee "$TMP/baseline.txt" | sed 's/^/  /'

say "3) fetch the live server block and place the include idempotently"
"${SCP[@]}" "$HUB:$SITE" "$TMP/site.conf"

anchor=$(grep -c '^[[:space:]]*location / {' "$TMP/site.conf" || true)
[[ "$anchor" -eq 1 ]] || die "expected exactly 1 'location / {' anchor, found ${anchor:-0}"

if grep -qF "$INCLUDE_LINE" "$TMP/site.conf"; then
  echo "  include already present — no edit needed"
  cp "$TMP/site.conf" "$TMP/site.new"
else
  awk -v inc="$INCLUDE_LINE" '
    !placed && /^[[:space:]]*location \/ \{/ { print inc; placed = 1 }
    { print }
    END { exit(placed ? 0 : 1) }
  ' "$TMP/site.conf" > "$TMP/site.new" || die "could not anchor the include; hub untouched"
  grep -qF "$INCLUDE_LINE" "$TMP/site.new" || die "include not inserted; hub untouched"
  echo "  include inserted before the dashboard catch-all"
fi

# The include must be INSIDE the server block. The file has exactly one bare `}` (the
# server's closing brace); the include must appear before it.
awk -v inc="$INCLUDE_LINE" '
  $0 == inc { seen = NR }
  $0 == "}" { last = NR }
  END { exit (seen && last && seen < last) ? 0 : 1 }
' "$TMP/site.new" || die "include landed outside the server block; hub untouched"
echo "  include is inside the server block"

say "4) back up, then install the snippet and the edited server block"
"${SSH[@]}" "set -e
  mkdir -p '$BACKUP_DIR' /etc/nginx/snippets
  cp -a '$SITE' '$SITE_BACKUP'
  if [ -e '$AVAIL' ] || [ -L '$AVAIL' ]; then cp -a '$AVAIL' '$AVAIL_BACKUP'; fi
  if [ -e '$SNIPPET_DST' ] || [ -L '$SNIPPET_DST' ]; then cp -a '$SNIPPET_DST' '$SNIPPET_BACKUP'; fi
  echo '  backup: $SITE_BACKUP'"
install_started=1
"${SCP[@]}" "$SNIPPET_SRC" "$HUB:$SNIPPET_DST"
"${SCP[@]}" "$TMP/site.new" "$HUB:$SITE"

say "5) validate BEFORE reloading — a bad config must never reach the live ingress"
# Guard the mistake this script made on its first run: a backup parked in an include
# glob is a live config, not a backup.
for d in "${INCLUDE_GLOBS[@]}"; do
  if "${SSH[@]}" "ls $d/*.bak-* >/dev/null 2>&1"; then
    die "a backup is sitting inside the include glob $d — nginx would load it as a second default server; restored on exit"
  fi
done

if ! "${SSH[@]}" "nginx -t" 2>&1 | sed 's/^/  /'; then
  die "nginx rejected the new config; restored on exit from $SITE_BACKUP (ingress was never reloaded)"
fi

say "6) reload"
"${SSH[@]}" "systemctl reload nginx && echo '  nginx reloaded'"

say "7) post-conditions"
fail=0
mesh_contract_code() {
  local url="$1"
  "${SSH[@]}" "token=\$(grep -s '^MESH_BRIDGE_TOKEN=' /etc/camelot/mesh.env 2>/dev/null | head -1 | cut -d= -f2-); if [ -n \"\$token\" ]; then curl -s -o /dev/null -m 8 -w '%{http_code}' -H \"x-camelot-token: \$token\" '$url'; else curl -s -o /dev/null -m 8 -w '%{http_code}' '$url'; fi"
}
for p in "${CONTRACT_PATHS[@]}"; do
  code="$(mesh_contract_code "http://localhost$p")"
  if [[ "$code" == "200" ]]; then
    echo "  PASS $p -> 200"
  else
    echo "  FAIL $p -> $code (expected authenticated 200)"; fail=1
  fi
done

echo
echo "  untouched paths, before -> after:"
probe "${UNTOUCHED[*]}" > "$TMP/after.txt"
while IFS='|' read -r path code size hdr; do
  before="$(grep -F "$path|" "$TMP/baseline.txt" | head -1)"
  printf '    %-12s %s\n' "$path" "before: ${before:-<none>}"
  printf '    %-12s %s\n' ""      "after : $path|$code|$size|$hdr"
done < "$TMP/after.txt"

# `/bifrost/` must still be answered by Express on :3001. If the bridge ever answers it,
# an exact-match bug has shadowed the gateway.
if grep -F '/bifrost/|' "$TMP/after.txt" | grep -qi 'express'; then
  echo
  echo "  PASS /bifrost/ still answered by the Express gateway, not the Python bridge"
else
  echo
  echo "  FAIL /bifrost/ no longer identifies as the Express gateway — prefix match may be shadowed"
  fail=1
fi

for p in "${UNTOUCHED[@]}"; do
  before="$(awk -F'|' -v p="$p" '$1 == p { print; exit }' "$TMP/baseline.txt")"
  after="$(awk -F'|' -v p="$p" '$1 == p { print; exit }' "$TMP/after.txt")"
  if [[ -z "$before" || "$before" != "$after" ]]; then
    echo "  FAIL untouched path changed: $p (before=${before:-<none>}, after=${after:-<none>})"
    fail=1
  fi
done

say "8) rollback"
echo "  restore config : cp -a $BACKUP_DIR/hermesagent.conf.bak-$STAMP $SITE && if [ -f $SNIPPET_BACKUP ]; then cp -a $SNIPPET_BACKUP $SNIPPET_DST; else rm -f $SNIPPET_DST; fi && nginx -t && systemctl reload nginx"
echo "  drop the route : rm $SNIPPET_DST, delete the include line from $SITE, then reload"

(( fail == 0 )) || die "post-conditions failed; restored on exit"
install_committed=1
echo
echo "  done — all ${#CONTRACT_PATHS[@]} contract paths served through nginx."
