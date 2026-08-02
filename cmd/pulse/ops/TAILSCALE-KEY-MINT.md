# Tailscale Auth-Key Mint & Revocation Runbook

> **STOP — these commands cannot be executed from this Windows dev host without
> a `tailscale` token + network reach to `api.tailscale.com`.** This document
> is the operator-facing recipe. The Tailscale **ACL policy** that consumes
> these auth-keys lives at https://login.tailscale.com/admin/acls/file (and
> is NOT committed to this repo). The Tailscale CLI on Windows can CONSUME
> an auth-key via `tailscale up --authkey=…` but **cannot MINT** one — minting
> is admin-console or API only.

This runbook covers the four phases of a one-off Tailscale node enrollment
on the Camelot-OS Tailnet: (1) preflight, (2) mint the auth-key, (3) enroll
the node + verify, (4) rotate or revoke when no longer needed. The default
recipe below is the **single-use / 1-hour TTL** flavor — the smallest blast
radius for one-off enrollments such as the `100.125.205.66` KBA build node.

## 1. Preflight

- [ ] `TS_API_TOKEN` env var is set in the shell:
      `[ -n "$TS_API_TOKEN" ] && echo "present" || echo "MISSING"`. The token
      is generated at https://login.tailscale.com/admin/settings/personal
      (copied once, stored in your password manager). It must have the
      `keys` capability — a read-only token returns 403 on every mint.
- [ ] API endpoint is reachable from this host:
      `curl -sS -o NUL -w "%{http_code}\n" https://api.tailscale.com` →
      expect `200` in <1s. If it hangs or returns non-200, **Warp is
      intercepting egress** — toggle Warp to bypass-mode for tailnet scopes
      and retry.
- [ ] You're in **Git Bash** (not `cmd.exe` or PowerShell). `tailscale.exe`
      is on the PATH under `/c/Program Files/Tailscale`, but the curl
      payload below uses single quotes + multi-line strings that only bash
      handles cleanly. Check: `echo "$BASH_VERSION"`.
- [ ] You have the **destination ACL** already published at
      https://login.tailscale.com/admin/acls/file. The mint below attaches
      `tag:KBA`; if no `tagOwners` rule allows that tag, the new node will
      join in an unauthorized state and silently fail the SSH path.

## 2. Mint-decision matrix

Pick the flavor that fits the rollout. The default is **single-use 1h**;
move to a longer-lived flavor only if you have a concrete reason.

| Scenario                              | `reusable` | `expirySeconds` | `ephemeral` | Blast radius                              |
| ------------------------------------- | ---------- | --------------- | ----------- | ----------------------------------------- |
| **One-off build node / single KBA**   | `false`    | `3600` (1 h)    | `false`     | 1 device × ≤1 h                           |
| Long-lived ops node, but trusted ops  | `false`    | `2592000` (30 d)| `false`     | 1 device × ≤30 d                          |
| Air-gapped auto-provisioner fleet     | `true`     | `7776000` (90 d)| `true`      | ∞ devices × ≤90 d, each auto-deletes     |
| Manual lab / test node                | `false`    | `86400` (1 d)   | `false`     | 1 device × ≤1 d                           |

> **Rule of thumb:** start with **single-use 1h**. Escalate only if the
> key keeps dying during enrollment, and only after the next failure root
> cause is identified (typo in `--advertise-tags`, wrong Warp bypass,
> etc). Reusable+long-lived is a password-equivalent secret — it should be
> the LAST option, not the first.

## 3. Mint the auth-key (default: single-use 1h)

The secret never touches terminal scrollback. It routes to the clipboard
via `clip.exe` (Windows). You'll paste it directly into the `tailscale up`
command on the target node.

```bash
# Set once per shell — DO NOT paste inline. Pick it up from your password
# manager via its CLI (bw get item "<name>" | jq -r .notes, or 1Password CLI).
export TS_API_TOKEN="tskey-api-XXXXXXXXXX"

# Mint
curl -sS -X POST "https://api.tailscale.com/api/v2/tailnet/-/keys" \
  -H  "Authorization: Bearer ${TS_API_TOKEN}" \
  -H  "Content-Type: application/json" \
  -d '{
    "capabilities": {
      "devices": {
        "create": {
          "reusable":      false,
          "ephemeral":     false,
          "preauthorized": true,
          "tags":          ["tag:KBA"]
        }
      }
    },
    "expirySeconds": 3600,
    "description":   "KBA self-attach (single-use, 1h TTL)"
  }' \
  | tee /tmp/tailscale-key-mint.json \
  | jq -r .key \
  | clip
```

```bash
# Sanity-check the .key never landed in scrollback-bound history
history -c   # bash: clears current-shell history
unset TS_API_TOKEN
```

> **If you used a reusable key (any flavor except the default single-use 1h),
> complete §10.1 (vault entry with `key_id`) and §10.3 (30-day calendar
> reminder) BEFORE `unset TS_API_TOKEN`.** Once the token is gone from your
> shell, you can't easily mint the next key in 30 days without re-loading
> the token from your password manager.

```bash
# If you also need the NON-secret key id (for later revoke), grab it now:
jq '{id: .id, description: .description, expires: .expires,
     reusable: .capabilities.devices.create.reusable,
     expirySeconds: .expiresSeconds}' /tmp/tailscale-key-mint.json
# → {"id":"<key-id>","description":"KBA self-attach (single-use, 1h TTL)",
#    "expires":"<ISO8601>","reusable":false,"expirySeconds":3600}
# The key id is NON-secret. Store it in your runbook notes keyed to date.
```

## 4. Enroll the node

You have a 1-hour window from mint to `tailscale up` completing. After
that, the key returns 401 `"key expired"` and you re-mint.

```powershell
# Windows OpenSSH Server as the destination shell
Get-Clipboard | ForEach-Object { tailscale up --advertise-tags=tag:KBA --authkey="$_" --accept-dns=false }
tailscale status
# Confirm the line starting with "100.125.205.66" appears with no errors
```

```bash
# Linux destination shell (most KBA dev nodes)
sudo tailscale up --advertise-tags=tag:KBA --authkey="$(xclip -selection clipboard -o)"
tailscale status
```

If `tailscale up` fails with `key expired` or `key invalid`, the mint
window has passed or the key was already consumed (`reusable: false`).
**Mint fresh — never retry the same key.**

If `tailscale up` returns `403 tag not permitted`, the destination ACL's
`tagOwners` rule does not allow your machine to attach `tag:KBA`. Fix the
ACL before re-minting (it's at https://login.tailscale.com/admin/acls/file).

## 5. Verify on a command-center host

Run these from a host bearing the `tag:command-center` or `tag:cybertron`
tag (the ACL rule permits both → `tag:KBA:22`).

```bash
# Peer visible? Tag attached? IP matches what was expected?
tailscale status --json \
  | jq -e '
      .Self.ID as $self
      | $self,
        (.Peer
         | to_entries[]
         | select(.value.Tags[]? == "tag:KBA")
         | {HostName:    .value.HostName,
            DNSName:     .value.DNSName,
            Tags:        .value.Tags,
            TailscaleIPs:.value.TailscaleIPs,
            Online:      .value.Online})
    '
```

Expected stdout shape:

```
"nodeid-<command-center-self-id>"
{ "HostName":     "kba-<n>",
  "DNSName":      "kba-<n>.tailnet.ts.net.",
  "Tags":         ["tag:KBA"],
  "TailscaleIPs": ["100.125.205.66"],
  "Online":       true }
```

```bash
# SSH reachability into the new node (port 22 / OpenSSH).
# Knobs that bite you without them:
#   StrictHostKeyChecking=accept-new — non-interactive on first exchange
#   ConnectTimeout=10               — fail fast instead of hanging on misroute
#   ServerAliveInterval / CountMax  — terminate idle hangs after ~15s
ssh -o StrictHostKeyChecking=accept-new \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=5 \
    -o ServerAliveCountMax=2 \
    <remote-user>@100.125.205.66 \
    'whoami && hostname && (uname -a 2>/dev/null || ver)'
```

`<remote-user>`:
- Linux KBA → your shell account name on the box
- Windows KBA → the account bound to OpenSSH Server (Settings → Apps →
  Optional Features → OpenSSH Server → account selection). Standalone
  installs default to `Administrator`.

## 6. Revoke a prior key

If you previously minted a `reusable: true` long-lived key, **revoke it
once the new node enrolls**. Revocation does NOT take the already-enrolled
device offline — the device holds its own auth from the original key
exchange. It only voids the secret for any future use. Without this step,
the longer-lived secret is still in your key list, expanded blast radius.

```bash
# 1. List all currently-valid auth keys. Identify the reusable one(s).
curl -sS "https://api.tailscale.com/api/v2/tailnet/-/keys" \
  -H "Authorization: Bearer ${TS_API_TOKEN}" \
  | jq '.[] | {id,
                description,
                reusable:      .capabilities.devices.create.reusable,
                expirySeconds, used, revoked}'
```

```bash
# 2. Revoke by id (key is gone; device stays up)
curl -sS -X DELETE \
  -H "Authorization: Bearer ${TS_API_TOKEN}" \
  "https://api.tailscale.com/api/v2/tailnet/-/keys/<key-id>" \
  -w "revoke HTTP %{http_code}\n"
# Expect: revoke HTTP 200
```

```bash
# 3. Verify the key list no longer shows the revoked id (filter to deleted:true)
curl -sS "https://api.tailscale.com/api/v2/tailnet/-/keys" \
  -H "Authorization: Bearer ${TS_API_TOKEN}" \
  | jq '.[] | select(.id == "<key-id>") | {id, revoked}'
# Expect: { "id": "<key-id>", "revoked": true }
```

## 7. Offboard a node (different from key revoke)

Removing the node from the Tailnet (different from revoking the auth-key):

```bash
# From the KBA node itself — pulls its own auth state
tailscale logout

# From the admin console or API, the node entry disappears from
# `tailscale status --json` on command-center within ~30s.
# Force-purge from the API if it stays online after logout (rare):
curl -sS -X POST \
  -H "Authorization: Bearer ${TS_API_TOKEN}" \
  "https://api.tailscale.com/api/v2/device/<node-id>/delete" \
  -w "delete HTTP %{http_code}\n"
```

Offboarding does **not** automatically revoke the auth-key used to enroll
the node — the original mint, if reusable, could still be reused until
its expiry. Always pair **offboarding** with the §6 **revoke** flow.

## 8. ACL coupling (out of repo)

This runbook covers the **enrollment credential** (auth-keys). The matching
**ACL policy** that consumes the enrolled node lives at
https://login.tailscale.com/admin/acls/file and is NOT committed to this
repo. The minimum policy required for §5 verification to succeed:

```json
{
  "tagOwners": {
    "tag:KBA":            ["autogroup:admin", "tag:command-center"],
    "tag:command-center": ["autogroup:admin"],
    "tag:cybertron":      ["autogroup:admin"]
  },
  "acls": [
    { "action": "accept",
      "src":    ["tag:command-center", "tag:cybertron"],
      "dst":    ["tag:KBA:22"] }
  ]
}
```

Tag-based, not IP-based — if the KBA node re-auths and gets a new
`100.125.x` IP, the ACL still routes correctly.

## 9. Secret handling (Sovereign Compass rule)

Per the CAMELOT-OS Sovereign Compass, API keys MUST NEVER be committed
as actual values. Only boolean presence markers in config. The auth-key
materialized by §3 has a 1-hour lifespan; treat it as password-equivalent
during that window:

- Never paste it into chat, ticket comments, or git history.
- Never `tee` the raw `.key` field to a file under version control.
- Don't reuse the same `TS_API_TOKEN` across multiple operators — each
  operator should mint their own personal access token.
- After the node is enrolled (§4) and verified (§5), rotate your personal
  access token if there's any chance it leaked: regenerate via
  https://login.tailscale.com/admin/settings/personal → Access tokens →
  Generate access token. The prior token cannot be rotated by API; it
  has to be deleted manually from the admin console.

## 10. Revoke-and-rotate lifecycle

The single-use 1h key from §3 self-destructs on its own and does NOT
need this section. The lifecycle below is for any **reusable** key from
Ref §2's matrix — the longer-lived flavors that linger in your key list
until their `expirySeconds` runs out. Operators minting reusable keys
should treat this section as mandatory.

### 10.1 Vault entry format — key id ONLY, never the secret

The password-manager entry that backs a reusable key must contain the
**non-secret `key_id`** plus rotation metadata, and absolutely nothing
else from §3. The `tskey-auth-…` secret lives only in the clipboard for
the ~5 seconds between mint and `tailscale up --authkey=…`. After that,
the secret is gone from the operator's host.

```
Title:       Tailscale key — KBA self-attach — 2026-06-29
Type:        API Token
Username:    (n/a)
Password:    <LEAVE EMPTY — do not paste the tskey-auth-… secret here>
Notes:       key_id=nodekey-auth:abc123def
             created=2026-06-29
             expires=2026-07-29
             description=KBA self-attach (reusable, 30d TTL)
             tags=tag:KBA
             revoke=curl -X DELETE -H "Authorization: Bearer ${TS_API_TOKEN}" \
                    https://api.tailscale.com/api/v2/tailnet/-/keys/nodekey-auth:abc123def
             next_rotation=2026-07-22
```

The Notes block is what makes the §10.2 emergency-revoke one-liner
copy-pastable in 3am panic mode. `key_id` and `revoke` are non-secret;
paste them into chat, tickets, or runbooks without concern. The
`Password` field is intentionally blank — Tailscale's API does not need
a password, and putting the secret there defeats the rotation hygiene.

### 10.2 Emergency-revoke one-liner

If the key is ever leaked (chat, ticket, git history, terminal
scrollback, accidental paste into a public channel), the **non-secret
`key_id` from the vault entry** is all you need to fire the kill
switch. The already-enrolled device STAYS UP — revocation only voids
future uses of the key, never the device's existing auth.

```bash
# Pull the key_id from your vault Notes field
KEY_ID="nodekey-auth:abc123def"
curl -sS -X DELETE \
  -H  "Authorization: Bearer ${TS_API_TOKEN}" \
  "https://api.tailscale.com/api/v2/tailnet/-/keys/${KEY_ID}" \
  -w "revoke HTTP %{http_code}\n"
# Expect: revoke HTTP 200
```

```bash
# Confirm the key is dead
curl -sS "https://api.tailscale.com/api/v2/tailnet/-/keys" \
  -H  "Authorization: Bearer ${TS_API_TOKEN}" \
  | jq ".[] | select(.id == \"${KEY_ID}\") | {id, revoked}"
# Expect: { "id": "nodekey-auth:abc123def", "revoked": true }
```

**Why the `already-enrolled device stays up` clause matters:** the
build agent does not need a re-enroll after a leak-revoke. You can
fire this at 3am without disrupting the running KBA node — the device
holds its own auth state from the original key exchange, and Tailscale
nodes do not phone home to revalidate the auth-key on every packet.
This is why the kill switch is "fire and forget" rather than "coordinate
with the build pipeline."

**After revoke, future enrollments need a fresh key.** Revoking does
NOT free the original `tskey-auth-…` secret for re-use on a future
KBA node — that secret is dead. Any new device you enroll will
require a fresh mint per §3.

### 10.3 30-day rotation calendar reminder

A reusable key with a 30-day `expirySeconds` is the most common
operator mistake — the key is valid for a month, which is long enough
to forget about. Schedule a **recurring 30-day calendar event** so
the rotation becomes a habit, not a panic. One event per active
reusable key.

```powershell
# Preflight (one-time per host): install + connect the Microsoft Graph Calendar module
#   Install-Module Microsoft.Graph.Calendar -Scope CurrentUser
#   Connect-MgGraph -Scopes Calendars.ReadWrite

# Microsoft 365 / Outlook via Microsoft Graph (personal or work calendar)
$start   = (Get-Date).AddDays(30).AddHours(9)   # 09:00 local, 30 days from now
$end     = $start.AddMinutes(15)
$subject = "Rotate Tailscale key — KBA reusable (was issued YYYY-MM-DD)"
$body    = "Mint a fresh tskey-auth-… key tagged tag:KBA per §3 of " +
           "TAILSCALE-KEY-MINT.md, distribute to the KBA node per §4, " +
           "verify per §5, then revoke the prior key per §6. " +
           "Update the vault entry's key_id, expires, and revoke fields."

# Recurrence: absoluteMonthly on the same day-of-month, no end date.
# Per Microsoft Graph API spec — Recurrence has nested Pattern and Range.
$rec = @{
    Pattern = @{
        Type       = "absoluteMonthly"
        Interval   = 1
        DayOfMonth = $start.Day
    }
    Range = @{
        Type      = "noEnd"
        StartDate = $start.ToString("yyyy-MM-dd")
    }
}

New-MgEvent -Subject $subject -Start $start -End $end -Body $body `
  -Recurrence $rec
```

```bash
# Cron has no native "every N days" syntax — `*/30` in day-of-month means
# "day 1 and day 31 of the month" (step from 1), not "every 30 days".
# Portable approach: a daily check + a sentinel file that tracks the
# last fire timestamp. Fires when ≥30 days have elapsed.

sudo tee /usr/local/bin/tailscale-key-rotate >/dev/null <<'ROTATE_EOF'
#!/bin/sh
set -eu
F=/var/lib/tailscale/last-rotation
if [ ! -f "$F" ]; then
    mkdir -p "$(dirname "$F")"
    touch "$F"      # first run: stamp sentinel, do not fire
    exit 0
fi
NOW=$(date +%s)
LAST=$(stat -c %Y "$F" 2>/dev/null || echo 0)
DAYS=$(( (NOW - LAST) / 86400 ))
[ "$DAYS" -ge 30 ] || exit 0
echo "Mint a fresh Tailscale key per §3 of TAILSCALE-KEY-MINT.md, \
distribute per §4, verify per §5, revoke prior per §6, \
update vault entry's key_id." | mail -s "Rotate Tailscale key" root
touch "$F"
ROTATE_EOF
sudo chmod +x /usr/local/bin/tailscale-key-rotate

# Register the daily check at 09:00 (cron is happy with this syntax):
( crontab -l 2>/dev/null; echo "0 9 * * * /usr/local/bin/tailscale-key-rotate" ) \
  | crontab -

# macOS alternative: the `ical` CLI from libical + the `khal` / `remind`
# calendar frontends, or `icalBuddy` for the macOS Calendar.app event
# store. None of these match Graph's `New-MgEvent` semantics 1:1, so
# the portable cron + sentinel approach above is preferred.
```

The 30-day cadence is opinionated. Adjust it for your risk appetite:
- 7-day rotation → higher hygiene, more operational toil
- 90-day rotation → less toil, longer window if a leak goes unnoticed
- 30-day rotation → industry-standard service-account rotation cadence

The reminder does NOT need to align with the key's `expires` field —
if the key was minted with `expirySeconds: 2592000` (30 d) and you
schedule a 30-day rotation, they happen to coincide. If you mint with
`expirySeconds: 7776000` (90 d) but still rotate every 30 days, the
calendar fires 3 times before the underlying key would have expired.
This is intentional: rotation hygiene is independent of token TTL.

### 10.4 Key hygiene checklist

After every mint of a reusable key:

- [ ] Vault entry created with `key_id` only — `Password` field is empty
- [ ] `description` field in the §3 curl payload matches the vault title
- [ ] `revoke` one-liner in vault `Notes` references the actual `key_id`
- [ ] 30-day recurring calendar reminder scheduled (§10.3)
- [ ] `/tmp/tailscale-key-mint.json` shredded (see prior §3 follow-up)
- [ ] `history -c` run to clear the `export TS_API_TOKEN=…` command
- [ ] `TS_API_TOKEN` unset from the shell after the operation
- [ ] Vault entry cross-checked against the live key list: `GET /api/v2/tailnet/-/keys`

After every 30-day rotation (when the calendar reminder fires):

- [ ] Mint a fresh key per §3 (use the same `description` prefix)
- [ ] Enroll it on the KBA node per §4 (the old one keeps working until expiry — no rush)
- [ ] Verify per §5
- [ ] Revoke the prior key per §6 (or §10.2 if the prior key was leaked)
- [ ] Update the vault entry's `key_id`, `expires`, `revoke`, and `next_rotation` fields
- [ ] Archive the old vault entry (do NOT delete — audit trail value)

### 10.5 Single-use 1h exception

The default §3 flavor (`reusable: false`, `expirySeconds: 3600`)
self-destructs within 1h of mint, so §10.1 / §10.3 do not apply. The
emergency-revoke one-liner in §10.2 STILL applies if the key leaks
during the 1h window — a `DELETE` on a `reusable: false` key succeeds
even though the key has not been used yet. Schedule **no calendar
reminder** for a single-use key; it has no future to rotate into.
