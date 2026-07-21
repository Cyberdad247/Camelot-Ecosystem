# Tailscale-Tag ⇄ Bifrost-ACL Mapping

> **Purpose.** Prevent split-brain auth: today the Tailscape ACL is owned by
> `cmd/pulse/ops/TAILSCALE-KEY-MINT.md` and the Bifrost admission gate is owned
> by `bin/bifrost.py`. They are two separate files with two separate trust
> models. This one-pager locks the contract between them so that a tag minted
> on the Tailnet side automatically has a known Bifrost counterpart.
>
> **Status.** Draft v0.1 · owner: vizio · last touched 2026-06-29.

---

## 1. Side A — Tailnet ACL contract

Source of truth: `cmd/pulse/ops/TAILSCALE-KEY-MINT.md` §3/§5/§6.

```jsonc
"tagOwners": {
  "tag:KBA":            ["autogroup:admin", "tag:command-center"],
  "tag:command-center": ["autogroup:admin"],
  "tag:cybertron":      ["autogroup:admin"]
},
"acls": [
  { "action": "accept",
    "src":    ["tag:command-center", "tag:cybertron"],
    "dst":    ["tag:KBA:22"] }                            // SSH :22 only, inbound to KBA
],
"ssh": [
  // Allow all users to SSH into their own devices in check mode.
  // Comment this section out if you want to define specific restrictions.
  {
    "action": "check",
    "src":    ["autogroup:member"],
    "dst":    ["autogroup:self"],
    "users":  ["autogroup:nonroot", "root"],
  }
]
```

Effective grants:
- `tag:command-center` and `tag:cybertron` hosts can SSH into any `tag:KBA` host on :22.
- `tag:command-center` and `autogroup:admin` can mint `tag:KBA` authkeys (so a KBA enrolls clean).
- Nothing in the ACL grants the **reverse** direction (KBA → command-center) and nothing grants either of them reach to Bifrost endpoints — that is intentionally handled by the application-layer gate, not the netlayer.

## 2. Side B — Bifrost gate rules

Source of truth: `bin/bifrost.py::verify_caller()` — first match wins, in order:

| Rule | Trigger | What it checks |
|---|---|---|
| **A** | caller is local (loopback IP) | `getpass.getuser() == CAMELOT_OWNER` (± optional token if `BIFROST_REQUIRE_TOKEN_ON_LOOPBACK=1`) |
| **D** | caller presents mTLS client cert | fingerprint in `BIFROST_TRUSTED_CERT_FINGERPRINTS` *or* CN in `BIFROST_TRUSTED_CERT_CNS` *or* any-valid if `BIFROST_ALLOW_ANY_VALID_CERT=1` |
| **C** | caller presents a JWT bearer | `iss ∈ BIFROST_OIDC_ISSUERS` and not expired and `aud` contains `camelot-os` |
| **B** | caller is on the tailnet (`100.64.0.0/10`) | presents matching `~/.camelot/bifrost.token` **and** `tailscale whois <ip>` returns a `Name:` whose value is in `BIFROST_TRUSTED_TAILNET_OWNERS` (default `Cyberdad247@github`, `Cyberdad247@`) |

The `Name:` field in `tailscale whois` is the **user identity**, not the node's tags. `_tailscale_whois()` in `bin/bifrost.py` extracts only that field — it never inspects `Tags:` — **so today Bifrost has no notion of any Tailscale tag**, only of the human/account owner string. This is the drift surface.

## 3. The Mapping (canonical)

| Tag | Tailnet role | Tailnet can reach | Bifrost counterpart (today) | Drift signal |
|---|---|---|---|---|
| `tag:KBA` | short-TTL build nodes / crawlers | inbound `:22` from command-center / cybertron | **none** — KBA nodes run as a machine user, not a `Cyberdad247@github` owner; Rule B fails on `whois` | KBA hosts connect to the tailnet fine, but Bifrost 403s them on every call. SSH works, API doesn't. |
| `tag:command-center` | core admin / operator hosts | out to KBA `:22`, plus general admin per `tagOwners` | **Rule B** (only if the host's owner is in `BIFROST_TRUSTED_TAILNET_OWNERS`, *and* the caller presents the token) | Drift if you add a new admin host whose Tailscale login ≠ Cyberdad247 → it silently loses Bifrost access. |
| `tag:cybertron` | tier-2 admin / build orchestration | out to KBA `:22` | **Rule B** under the same owner-string constraint as command-center | Same drift surface as command-center. Also: cybertron was never added to `BIFROST_TRUSTED_TAILNET_OWNERS` — it implicitly shares command-center's trust via owner string, *not* via tag. |
| `tag:bifrost-mesh` | **PROPOSED** — inter-node mesh between Bifrost instances | *no ACL yet* | proposed: **Rule D (mTLS)** — by-tag cert fingerprint allow-listed via `BIFROST_TRUSTED_CERT_FINGERPRINTS` | mesh node A gets a cert → mesh node B has no fingerprint rule → mTLS handshake fails. Drift visible immediately, often mistaken for a TLS bug. |

## 4. Drift — what actually breaks when these disagree

- **KBA can't reach Bifrost.** Most common failure mode. Tailnet ACL happily routes the traffic; `_tailscale_whois` returns the node's machine identity (no `@`) and Rule B short-circuits to `tailnet-untrusted-owner`. Symptom: 403 with `reason=tailnet-untrusted-owner: ...` in `bin/bifrost.py::status_report()` JSON.
- **New admin host loses Bifrost silently.** Owner rename on Tailscale (e.g. moving to a work account) breaks Rule B for that host. The host can still SSH to KBA via the ACL rule, but every Bifrost call 403s.
- **Reusable KBA key pasts expiry but the ACL is gone.** A host with no `tagOwners` entry silently joins the tailnet unauthorized and the SSH grant is denied. Visible in `tailscale status` as "tag not permitted".

## 5. Open questions / version notes

- `tag:bifrost-mesh` does **not exist** in `cmd/pulse/ops/TAILSCALE-KEY-MINT.md`, `bin/bifrost.py`, or anywhere in the repo (code_search returned 0 hits). It is a forward-looking tag — adding it requires changes in three places: (1) the `tagOwners` block above, (2) an `acls` grant allowing the tag to call Bifrost internals, (3) `bin/bifrost.py` to honor the tag — see §6.
- `tag:cybertron` was not named in the mapping request but is already in the ACL block — left in the table for visibility, not silently dropped.
- The list of trusted owners (`Cyberdad247@github`, `Cyberdad247@`) is hard-coded as the default in `bin/bifrost.py` and overridable via `BIFROST_TRUSTED_TAILNET_OWNERS`. Today the only realistic way to grant a *new* host Bifrost access is to add its Tailscale login to that env var.

## 6. Recommended fix to `bin/bifrost.py` (NOT YET IMPLEMENTED)

To close the drift gap, three changes are recommended (none applied yet — propose in a PR with this doc as the linked design):

1. **Extend `_tailscale_whois`** to additionally parse `tailscale whois --json`, returning both the user-login **and** the node's tag list.
2. **Add `BIFROST_TRUSTED_TAILNET_TAGS`** env var (comma-separated, e.g. `tag:command-center,tag:cybertron,tag:bifrost-mesh`).
3. **Update Rule B** so the caller clears the gate if `presented_token` matches **and** (`owner ∈ TRUSTED_TAILNET_OWNERS` *OR* any node tag ∈ `BIFROST_TRUSTED_TAILNET_TAGS`).

Effect: `tag:KBA` still gets no Bifrost access (intentional — KBA nodes don't need app-layer privilege, only SSH), `tag:command-center` and `tag:cybertron` get explicit per-tag trust independent of owner string, and `tag:bifrost-mesh` lands ready when it's minted. The doc and the code can then be reviewed as a single PR.

---

*See also: `cmd/pulse/ops/TAILSCALE-KEY-MINT.md` §3, `bin/bifrost.py::verify_caller`, `tests/test_bifrost_gate.py` for the live test matrix.*
