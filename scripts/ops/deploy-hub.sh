#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# Deploy a committed ref of this repository to the Camelot-OS hub.
#
# Why releases instead of `git pull` on the hub: the hub carries several checkout
# trees (/opt/camelot-ecosystem, /opt/camelot-vps, /opt/camelot-os) and only one of
# them is what systemd actually executes — the units' WorkingDirectory is
# /opt/camelot-ecosystem. A pull in any tree can silently revert working-tree edits,
# and a pull in the *wrong* tree changes nothing that runs. So a deploy here means:
# materialize an immutable release from a commit, then move a symlink. The commit
# sha in the directory name makes "what is running" answerable without ssh archaeology.
#
# Safety model:
#   * staging is additive — it never touches the live tree;
#   * cutover moves the old tree aside rather than deleting it, and rolls back on
#     its own if the health probes fail after restart;
#   * nothing restarts a service unless --activate is passed.
#
# Usage:
#   bash scripts/ops/deploy-hub.sh                     # stage HEAD as a release
#   bash scripts/ops/deploy-hub.sh --ref <ref>         # stage another commit/branch
#   bash scripts/ops/deploy-hub.sh --activate          # stage, cut over, restart, verify
#   bash scripts/ops/deploy-hub.sh --dry-run --activate
#   bash scripts/ops/deploy-hub.sh --no-build          # skip the bifrost build step
#   bash scripts/ops/deploy-hub.sh --rollback          # cut back to the previous release
#   bash scripts/ops/deploy-hub.sh --prune             # prune old releases, change nothing else
#
# Retention:
#   Releases accumulate forever by default — each cutover stages a new one and a
#   deploy only ever adds. Others holding rollback material would not know which
#   trees are still needed, so the budget is a number here (CAMELOT_KEEP, default
#   5): the newest N releases plus whatever is live survive, everything older is
#   removed after a *verified* cutover. Never before: pruning first would delete
#   the tree a failing deploy is about to roll back to.
#
# Environment:
#   CAMELOT_HUB        ssh target          (default: vps-camelot-hub)
#   CAMELOT_RELEASES   release root on hub (default: /opt/camelot-releases)
#   CAMELOT_LIVE       live tree on hub    (default: /opt/camelot-ecosystem)
#   CAMELOT_UNITS      units to restart    (default: camelot-vps-mesh camelot-edge-bus camelot-bifrost)
#   CAMELOT_STATE      mutable state root  (default: /opt/camelot-state)
#   CAMELOT_KEEP       releases to keep    (default: 5, live always kept)

set -euo pipefail

HUB="${CAMELOT_HUB:-vps-camelot-hub}"
RELEASES="${CAMELOT_RELEASES:-/opt/camelot-releases}"
LIVE="${CAMELOT_LIVE:-/opt/camelot-ecosystem}"
STATE="${CAMELOT_STATE:-/opt/camelot-state}"
UNITS="${CAMELOT_UNITS:-camelot-vps-mesh camelot-edge-bus camelot-bifrost}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

REF="HEAD"
MODE="stage" # stage | activate | rollback | prune
DRY_RUN=0
BUILD=1
KEEP="${CAMELOT_KEEP:-5}"

SSH=(ssh -o BatchMode=yes -o ConnectTimeout=15 "$HUB")
SCP=(scp -o BatchMode=yes -o ConnectTimeout=15)

say()  { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32mok\033[0m   %s\n' "$1"; }
warn() { printf '  \033[33mwarn\033[0m %s\n' "$1"; }
die()  { printf '  \033[31mFAIL\033[0m %s\n' "$1" >&2; exit 1; }

# `ssh` is wrapped so --dry-run can be honest about what it would do without
# performing it. Every remote mutation in this script goes through run_remote.
run_remote() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '  \033[36mdry-run\033[0m would run on %s: %s\n' "$HUB" "$1"
    return 0
  fi
  "${SSH[@]}" "$1"
}

# Health is checked from the hub's own perspective, and from the interface each
# service actually binds. :8095/:8096 bind the tailnet address only, so a loopback
# probe reports a healthy bridge as dead — the exact false negative that made the
# hub look down in the first place.
health_payload() {
  cat <<'EOF'
set -u
fail=0
# curl prints its -w value even when the connection fails, so `|| echo 000` appended
# a second 000 and the probe logged "000000" — an unreadable number in exactly the
# report someone reads during an outage.
code() { local c; c=$(curl -s -o /dev/null -m 4 -w '%{http_code}' "$1" 2>/dev/null); printf '%s' "${c:-000}"; }
b=$(code http://127.0.0.1:3001/health)          # bifrost binds all interfaces
m=$(code http://100.110.180.18:8095/mesh/status) # tailnet-only; 401 = alive, auth-gated
e=$(code http://100.110.180.18:8096/healthz)     # tailnet-only
printf '    bifrost :3001/health      %s\n' "$b"
printf '    mesh    :8095/mesh/status %s\n' "$m"
printf '    edge    :8096/healthz     %s\n' "$e"
[ "$b" = 200 ] || fail=1
[ "$m" != 000 ] || fail=1
[ "$e" != 000 ] || fail=1
printf '    units: '
systemctl is-active camelot-bifrost camelot-vps-mesh camelot-edge-bus | tr '\n' ' '
echo
for u in camelot-bifrost camelot-vps-mesh camelot-edge-bus; do
  [ "$(systemctl is-active "$u")" = active ] || fail=1
done
exit $fail
EOF
}

# Prune is the one destructive step in this script, so it is written to be boring
# and bounded: it only ever removes paths under $RELEASES whose name is a commit
# sha, and it can never select the live release. Legacy aliases ($LIVE.legacy-*)
# are symlinks moved aside by previous cutovers — cheap to keep, but stale ones
# pointing at pruned trees are noise in every "what is here" listing, so the
# newest is kept as a manual rescue handle and the rest go.
do_prune() {
  [[ "$KEEP" =~ ^[0-9]+$ ]] || die "CAMELOT_KEEP must be a number, got '$KEEP'"
  say "Prune $RELEASES (keeping $KEEP newest + live)"
  # In dry-run every remote read is a *print*, so parsing its output would invent
  # release names out of the command text itself. Report the policy and stop.
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "  dry-run: would keep the newest $KEEP sha-named releases plus whatever $LIVE points at,"
    echo "           delete older ones, stale .incoming-*.tar.gz (>1h), and all but the newest $LIVE.legacy-*"
    return 0
  fi
  local live list keepers doomed path n=0
  live=$(run_remote "readlink -f '$LIVE' 2>/dev/null || true")
  list=$(run_remote "ls -1dt '$RELEASES'/*/ 2>/dev/null | sed 's:/$::' || true")
  if [[ -z "$list" ]]; then
    ok "no releases staged — nothing to prune"
    return 0
  fi
  # Newest first, minus the live tree. The first $KEEP are the rollback window.
  keepers=$(printf '%s\n' "$list" | grep -vxF "${live:-/nonexistent}" | head -n "$KEEP")
  doomed=$(printf '%s\n' "$list" | grep -vxF "${live:-/nonexistent}" | tail -n "+$((KEEP + 1))")
  printf '%s\n' "$keepers" | while read -r path; do [[ -n "$path" ]] && printf '  \033[32mkeep\033[0m   %s\n' "$(basename "$path")"; done
  if [[ -n "$live" ]]; then printf '  \033[32mkeep\033[0m   %s (live)\n' "$(basename "$live")"; fi
  if [[ -z "$doomed" ]]; then
    ok "within budget — nothing to remove"
    return 0
  fi
  while read -r path; do
    [[ -n "$path" ]] || continue
    # Two independent guards: the path must sit directly in $RELEASES and its name
    # must look like a commit. A glob that expanded unexpectedly (or an empty live
    # target turning a filter into a no-op) then deletes nothing.
    if [[ "$(dirname "$path")" != "$RELEASES" ]]; then
      warn "skipping $path — not directly under $RELEASES"; continue
    fi
    if ! [[ "$(basename "$path")" =~ ^[0-9a-f]{7,40}$ ]]; then
      warn "skipping $path — name is not a commit sha"; continue
    fi
    if [[ -e "$LIVE" && "$(run_remote "readlink -f '$LIVE'")" == "$path" ]]; then
      warn "skipping $path — it is live"; continue
    fi
    run_remote "rm -rf '$path'" && { n=$((n + 1)); printf '  \033[33mpruned\033[0m %s\n' "$(basename "$path")"; }
  done <<< "$doomed"
  ok "pruned $n release(s)"

  # Interrupted uploads leave .incoming-<sha>.tar.gz behind; they are never valid
  # releases and can be a hundred megabytes each.
  run_remote "find '$RELEASES' -maxdepth 1 -name '.incoming-*.tar.gz' -mmin +60 -print -delete | sed 's/^/  pruned /'" || true

  # Legacy aliases: keep the newest, drop the rest (and any already broken).
  local aliases
  aliases=$(run_remote "ls -1dt '$LIVE'.legacy-* 2>/dev/null || true")
  if [[ -n "$aliases" ]]; then
    printf '%s\n' "$aliases" | tail -n +2 | while read -r path; do
      [[ -n "$path" ]] && run_remote "rm -rf '$path'" && printf '  \033[33mpruned\033[0m %s\n' "$(basename "$path")"
    done
  fi
}

do_rollback() {
  local current target
  current=$(run_remote "readlink -f '$LIVE' || true")
  # Candidates are every tree that can actually serve: staged releases and the
  # legacy trees earlier cutovers moved aside. Restricting rollback to $RELEASES
  # made it fail on a first deploy — the only working tree was the one just moved
  # aside, so the one moment rollback is most needed was the moment it was empty.
  # Prefer a canonical staged release over a legacy alias, so a rollback leaves
  # $LIVE pointing at /opt/camelot-releases/<sha> rather than at
  # /opt/camelot-ecosystem.legacy-<ts> (which is itself a symlink to a release —
  # same bytes, but the alias makes "what is live" ambiguous for the next cutover).
  pick() { run_remote "ls -1dt $1 2>/dev/null | sed 's:/*\$::' | grep -vx '$current' | head -1"; }
  target=$(pick "$RELEASES/*/")
  [[ -n "$target" ]] || target=$(pick "$LIVE.legacy-*/")
  [[ -n "$target" ]] || die "no other tree available to roll back to"
  say "Rolling back $LIVE -> $target"
  run_remote "ln -sfn '$target' '$LIVE.tmp' && mv -Tf '$LIVE.tmp' '$LIVE' && readlink -f '$LIVE'"
  run_remote "systemctl restart $UNITS"
  if run_remote "$(health_payload)"; then ok "rollback verified"; else die "rollback completed but health still failing"; fi
}

# ── argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref)       REF="${2:?--ref needs a value}"; shift 2 ;;
    --host)      HUB="${2:?--host needs a value}"; SSH=(ssh -o BatchMode=yes -o ConnectTimeout=15 "$HUB"); SCP=(scp -o BatchMode=yes -o ConnectTimeout=15); shift 2 ;;
    --activate)  MODE="activate"; shift ;;
    --rollback)  MODE="rollback"; shift ;;
    --prune)     MODE="prune"; shift ;;
    --keep)      KEEP="${2:?--keep needs a value}"; shift 2 ;;
    --dry-run)   DRY_RUN=1; shift ;;
    --no-build)  BUILD=0; shift ;;
    -h|--help)   sed -n '1,34p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)           die "unknown argument: $1" ;;
  esac
done

cd "$REPO_ROOT"

if [[ "$MODE" == "rollback" ]]; then
  do_rollback
  exit 0
fi

if [[ "$MODE" == "prune" ]]; then
  do_prune
  exit 0
fi

# ── 1. resolve the ref to a commit ────────────────────────────────────────────
say "1) resolve ref"
SHA=$(git rev-parse --verify "$REF^{commit}" 2>/dev/null) || die "'$REF' is not a commit — only committed trees can be deployed"
SHORT=$(git rev-parse --short "$SHA")
DIR="$RELEASES/$SHORT"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
ok "$REF -> $SHA ($(git log -1 --format='%s' "$SHA" | cut -c1-60))"
if [[ -n "$(git status --porcelain)" && "$REF" == "HEAD" ]]; then
  warn "working tree is dirty — only committed files ship; uncommitted edits are NOT deployed"
fi

# ── 2. preflight the hub ──────────────────────────────────────────────────────
say "2) preflight $HUB"
run_remote "mkdir -p '$RELEASES' && df -h '$RELEASES' | tail -1 && echo '  releases dir ready'"
if [[ "$(run_remote "test -d '$DIR' && echo staged" || true)" == "staged" ]]; then
  ok "release $SHORT already staged — skipping upload (idempotent)"
fi

# ── 3. stage the release ──────────────────────────────────────────────────────
if [[ "$(run_remote "test -d '$DIR' && echo staged" || true)" != "staged" ]]; then
  say "3) stage release $SHORT"
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' EXIT
  git archive --format=tar.gz "$SHA" > "$TMP/release.tar.gz" || die "git archive failed"
  SUM=$(sha256sum "$TMP/release.tar.gz" | cut -d' ' -f1)
  SIZE=$(wc -c < "$TMP/release.tar.gz")
  ok "archive built: $((SIZE / 1024 / 1024)) MB, sha256 ${SUM:0:16}…"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    run_remote "scp/untar -> $DIR"
  else
    "${SCP[@]}" "$TMP/release.tar.gz" "$HUB:$RELEASES/.incoming-$SHORT.tar.gz"
    # Verify the bytes that arrived, not the bytes that left: a dropped connection
    # during a 100 MB upload produces a truncated archive that extracts into a
    # half-populated tree. tar would report success on the files it did get.
    REMOTE_SUM=$("${SSH[@]}" "sha256sum '$RELEASES/.incoming-$SHORT.tar.gz' | cut -d' ' -f1")
    [[ "$REMOTE_SUM" == "$SUM" ]] || die "transfer corrupted (local $SUM != remote $REMOTE_SUM)"
    ok "transfer verified end to end"
    "${SSH[@]}" "mkdir -p '$DIR' && tar -xzf '$RELEASES/.incoming-$SHORT.tar.gz' -C '$DIR' && rm -f '$RELEASES/.incoming-$SHORT.tar.gz'"
    ok "extracted to $DIR"

    cat > "$TMP/manifest.json" <<JSON
{
  "commit": "$SHA",
  "release": "$SHORT",
  "ref": "$REF",
  "branch": "$BRANCH",
  "deployed_at": "$(date -Is)",
  "deployed_from": "$(hostname)",
  "tarball_sha256": "$SUM",
  "size_bytes": $SIZE,
  "hub": "$HUB"
}
JSON
    "${SCP[@]}" "$TMP/manifest.json" "$HUB:$DIR/DEPLOY_MANIFEST.json"
    FILES=$("${SSH[@]}" "find '$DIR' -type f | wc -l")
    ok "release staged: $FILES files + DEPLOY_MANIFEST.json"
  fi
fi

if [[ "$MODE" == "stage" ]]; then
  say "Done (staged only — nothing was restarted)"
  echo "  cut over with:  bash scripts/ops/deploy-hub.sh --activate --ref $SHORT"
  exit 0
fi

# ── 4. cutover ────────────────────────────────────────────────────────────────
say "4) cut over $LIVE -> $DIR"
# Refuse to activate a tree that cannot run. bifrost serves committed dist/*.js, so
# its absence means the release would come up as a CSPR-failing unit rather than a
# gateway; that is a deploy defect, not something to discover after the restart.
run_remote "test -f '$DIR/control_plane/dispatch/edge_bus.py'" || die "release is missing control_plane/ — refusing to activate"
has_dist() {
  [[ "$(run_remote "test -f '$DIR/apps/bifrost/dist/server.js' && echo yes" || true)" == "yes" ]]
}

# dist/ is gitignored, so a git-archive release never carries bifrost's compiled
# server — and without it the unit cannot start at all. The hub therefore builds it
# from the staged source *before* the cutover: discovering a missing build after the
# symlink flip means the gateway is down while the rest of the hub is up, which is
# worse than not deploying at all.
if ! has_dist && [[ "$BUILD" -eq 1 ]]; then
  say "4a) build bifrost inside the release (apps/bifrost/dist is gitignored)"
  # Root workspace install is required: bifrost's build script calls the repo-root
  # typescript and prisma binaries. The placeholder DATABASE_URL is what
  # `prisma generate` needs — it reads the schema, not a live database.
  # npm comes from packageManager in package.json (npm@11.11.0), not from the
  # hub's global install (10.9.8): the two hoist differently, and a lockfile built
  # by npm 11 is rejected by npm 10 with "Missing: ... from lock file". npx runs
  # the pinned version without changing the hub's global npm.
  #
  # --legacy-peer-deps is still required, but no longer because the workspaces
  # disagree: all of them now declare React 18, matching the root override and
  # Next 14. The remaining conflict is one external package — apps/pwa's
  # @agent-native/core peers on react >=19.2.7, which cannot coexist with Next 14's
  # React 18. Strict resolution fails on that peer alone; every published version
  # of that package declares it, so the choice is Next 15 + React 19 or dropping
  # the dependency, not a version bump.
  # The npm install fallback stays only as a safety net: it resolves fresh instead
  # of reproducing the lockfile, so it announces itself rather than failing quietly.
  # export, not a VAR=value prefix on the group below: `VAR=x { ...; }` is not a
  # command position, so bash aborts with "syntax error near unexpected token `}'"
  # and the build silently never runs.
  run_remote "cd '$DIR' && export DATABASE_URL='postgresql://placeholder:placeholder@localhost:5432/placeholder?schema=public' && \
      { npx -y npm@11.11.0 ci --no-audit --no-fund --legacy-peer-deps || \
        { echo '  npm ci rejected the lockfile — using npm install (not lockfile-reproducible)'; \
          npx -y npm@11.11.0 install --no-audit --no-fund --legacy-peer-deps; }; } > /tmp/camelot-deploy-build.log 2>&1 && \
      npx -y npm@11.11.0 --prefix apps/bifrost run build >> /tmp/camelot-deploy-build.log 2>&1 && echo '  build finished'"
  # tsc compiles only src/**/*.ts, so Prisma's generated .js client never lands in
  # dist/ by itself — and dist/db/SovereignDB.js requires ../generated/client at
  # runtime, which threw MODULE_NOT_FOUND on the first cutover. Copy it here as
  # well as in the package build script, so a release built from an untagged tree
  # is still runnable.
  run_remote "cd '$DIR/apps/bifrost' && if [ -d src/generated ]; then rm -rf dist/generated && cp -a src/generated dist/generated && echo '  generated client -> dist/generated'; fi"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    has_dist || die "bifrost build produced no dist/server.js (see /tmp/camelot-deploy-build.log on the hub) — refusing to cut over"
    run_remote "test -f '$DIR/apps/bifrost/dist/generated/client/index.js'" \
      || die "dist/generated/client missing — bifrost would throw MODULE_NOT_FOUND on boot"
    ok "bifrost built: dist/server.js + generated client present"
  fi
fi

# ── 4a. carry runtime state and config forward ────────────────────────────
# A git-archive release carries the *committed* snapshot of
# 03_VAULT/runtime_state, but the running hub has been appending to it for weeks,
# and the .env files are gitignored so they are in no release at all. Flipping the
# symlink as-is would start bifrost with no environment and present a stale ledger
# snapshot as current. So the mutable state lives outside every release, in
# $STATE, and each release points at it — the same split the releases dir makes for
# code, applied to data.
say "4b) carry runtime state and config into the release"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "  dry-run: would seed $STATE from the live tree, then point $DIR at it"
else
  run_remote "set -e
    mkdir -p '$STATE'
    if [ -d '$LIVE/03_VAULT/runtime_state' ] && [ ! -e '$STATE/runtime_state' ]; then
      cp -a '$LIVE/03_VAULT/runtime_state' '$STATE/runtime_state'
    fi
    mkdir -p '$STATE/logs'
    # The loop variable must stay unexpanded here so the remote shell expands it;
    # single-quoting it silently matched nothing and copied zero env files.
    for f in .env apps/bifrost/.env; do
      if [ -f \"$LIVE/\$f\" ] && [ ! -f \"$DIR/\$f\" ]; then
        mkdir -p \"\$(dirname \"$DIR/\$f\")\"; cp -a \"$LIVE/\$f\" \"$DIR/\$f\"
      fi
    done
    # Bifrost's environment comes from systemd, not from Prisma incidentally reading
    # apps/bifrost/.env: a client generated inside a fresh tree does not do that, and
    # the gateway refuses to boot without DATABASE_URL (it crashed the first
    # cutover). Seeding the drop-in makes the dependency explicit and idempotent.
    if [ -f '$LIVE/apps/bifrost/.env' ] && [ ! -f /etc/camelot/bifrost.env ]; then
      mkdir -p /etc/camelot
      cp '$LIVE/apps/bifrost/.env' /etc/camelot/bifrost.env
      chmod 600 /etc/camelot/bifrost.env
      mkdir -p /etc/systemd/system/camelot-bifrost.service.d
      printf '[Service]\n# explicit env seeded by scripts/ops/deploy-hub.sh\nEnvironmentFile=-/etc/camelot/bifrost.env\n' \\
        > /etc/systemd/system/camelot-bifrost.service.d/10-envfile.conf
      systemctl daemon-reload
    fi
    rm -rf '$DIR/03_VAULT/runtime_state' '$DIR/logs'
    mkdir -p '$DIR/03_VAULT'
    ln -sfn '$STATE/runtime_state' '$DIR/03_VAULT/runtime_state'
    ln -sfn '$STATE/logs' '$DIR/logs'
    echo '  runtime_state -> '\$(readlink '$DIR/03_VAULT/runtime_state')
    echo '  logs          -> '\$(readlink '$DIR/logs')
    echo '  env files     -> '\$(ls -1 '$DIR/.env' '$DIR/apps/bifrost/.env' 2>/dev/null | wc -l) copied"
  ok "state and config carried forward"
fi

RESTART_UNITS=""
for u in $UNITS; do
  # In dry-run, has_dist() cannot answer (run_remote only prints), so the check
  # would always look like a missing build. Don't turn that into a false warning.
  if [[ "$u" == "camelot-bifrost" ]] && [[ "$DRY_RUN" -eq 0 ]] && ! has_dist; then
    warn "--no-build: release has no compiled bifrost — excluded from the restart"
    continue
  fi
  RESTART_UNITS="$RESTART_UNITS $u"
done
RESTART_UNITS="${RESTART_UNITS# }"

PREV=$(run_remote "readlink -f '$LIVE' 2>/dev/null || true")
if [[ -n "$PREV" && "$PREV" != "$DIR" ]]; then
  LEGACY="$LIVE.legacy-$(date +%Y%m%dT%H%M%S)"
  # Move, never delete: a symlink flip is reversible only while the old bytes exist.
  run_remote "mv '$LIVE' '$LEGACY' && echo '  previous tree kept at $LEGACY'"
fi
run_remote "ln -sfn '$DIR' '$LIVE.tmp' && mv -Tf '$LIVE.tmp' '$LIVE' && readlink -f '$LIVE'"

# ── 5. restart + verify, with automatic rollback ─────────────────────────────
say "5) restart and verify: $RESTART_UNITS"
if [[ "$DRY_RUN" -eq 1 ]]; then
  run_remote "systemctl restart $RESTART_UNITS"
  echo "  dry-run: skipping the restart and the health verification"
  exit 0
fi
run_remote "systemctl restart $RESTART_UNITS"
# A restart is not instant: node takes seconds to bind :3001. Probing 3s after the
# restart reported a healthy gateway as down and rolled a good release back, so the
# health gate retries instead of measuring how fast the machine happened to be.
VERIFY_OK=0
for attempt in 1 2 3 4 5 6 7 8; do
  echo "  attempt $attempt/8 (up to $(($attempt * 3))s after restart)"
  if run_remote "$(health_payload)"; then VERIFY_OK=1; break; fi
  [[ $attempt -lt 8 ]] && sleep 3
done
if [[ "$VERIFY_OK" -eq 1 ]]; then
  ok "cutover verified on $SHORT"
else
  warn "post-cutover health failed — rolling back"
  do_rollback
  die "deploy of $SHORT rolled back; hub is on the previous release"
fi

# ── 6. retention ──────────────────────────────────────────────────────────────
# Only after the health gate passed: at this point the previous release is
# rollback material for a cutover that has already been verified, so the oldest
# trees beyond the budget are safe to drop. On the rolled-back path do_rollback
# exits before reaching here — which is exactly the guarantee needed, since a
# failed deploy must not have had its fallback pruned.
say "6) prune old releases"
do_prune

say "Done — $SHORT is live"
run_remote "cat '$DIR/DEPLOY_MANIFEST.json'"
