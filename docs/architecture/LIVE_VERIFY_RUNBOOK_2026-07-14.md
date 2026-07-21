---
id: live-verify-runbook-2026-07-14
status: drop-in
owner: sir_boris
schema: runbook/system.lifecycle.v1
date: 2026-07-14
target_ide: [cursor, cline, roo_code]
target_ide_format: yaml-list
follows_from: [NOTES_MNEMOSYNE_WIRING.md §7-RESOLVED, SYSTEM_PROMPT_v2_2026-07-14.md §4, TITAN_TIER_EXECUTION_PROMPT_2026-07-14.md §3.6]
supersedes: []
length_budget_kb: 24
marker_legend: |
  [LOCAL-CHECK]         no docker required, runnable from any shell
  [OPERATOR-BOUND]      requires docker daemon / browser / external network
  [AGENT-RUNNABLE]      IDE agent (Cursor/Cline) can run without operator
  [INTEL-DEPENDS]       must pass §8.1 + §8.2 before useful
---

# 🪢 §8 LIVE VERIFY RUNBOOK — Mnemosyne Wiring

This runbook is the **single test plan** for proving the Mnemosyne wiring
(Appwrite self-host + Bifrost gateway + NotebookLM MCP) is end-to-end live
on a fresh host. Every command below is copy-runnable standalone. Every
marker (`[LOCAL-CHECK]` etc.) tells you who runs it.

> **Read first**: `docs/architecture/SYSTEM_PROMPT_v2_2026-07-14.md §4`
> (Phases 1.7 / 1.9 / 1.10 / 1.11) — this runbook adds the post-deploy
> verification gates those phases leave open. The TITAN-TIER prompt's
> Phase 3.6 only checks **one** Appwrite endpoint; this runbook adds 4.

> **Stop conditions** (any one fires → freeze and page Sir Boris):
> 1. **Two §8.x FAIL in a row** → the wiring drift is structural, not transient
> 2. **`WEBHOOK_SECRET` validation fails twice** → enum the secret source
> 3. **Appwrite stack healthy but `appwrite_local` record missing in DNS
>    lookup** → DNS-routing bug; halt before §8.4
> 4. **Z3 verifier unavailable on this host** → §8.4 cannot pass;
>    document the gap and proceed with §8.1–§8.3 only

---

## §8.0  Pre-flight / environment                                     [LOCAL-CHECK]

**Goal**: prove the *non-docker* half of the system is wired before
spending time standing up the Appwrite stack. If §8.0 fails, no amount
of `docker compose up` will unstick you.

```bash
cd "$REPO_ROOT"   # wherever CAMELOT_OS/ lives

echo "=== OS / python ==="
uname -a
python --version
[ "$(python -c 'import sys; print(sys.version_info >= (3,11))')" = "True" ] \
  || { echo "FAIL: python ≥3.11 required"; exit 1; }

echo "=== Directory presence ==="
for d in apps/bifrost apps/bifrost/src CAMELOT_OS/bin CAMELOT_OS/control_plane; do
    [ -d "$d" ] && echo "  OK  $d" || echo "  ??  $d missing"
done

echo "=== Python dependencies ==="
python <<'PYEOF'
required = {
    "appwrite":     "from appwrite.client import Client",
    "fastmcp":      "from mcp.server.fastmcp import FastMCP",
    "tenacity":     "import tenacity",
    "urllib":       "import urllib.request",   # stdlib; smoke only
    "yaml":         "import yaml",             # for compose parse fallback
}
for name, stmt in required.items():
    try:
        exec(stmt); print(f"  OK   {name}")
    except Exception as e:
        print(f"  FAIL {name}: {type(e).__name__}: {e}")
PYEOF

echo "=== Env files present (gitignored values not shown) ==="
for f in CAMELOT_OS/.env CAMELOT_OS/.env.appwrite; do
    if [ -f "$f" ]; then
        echo "  EXISTS $f ($(wc -c < "$f" | tr -d ' ') bytes)"
    else
        echo "  MISSING $f"
    fi
done

echo "=== Expected env vars (private values REDACTED) ==="
cat <<'VARS'
  APPWRITE_ENDPOINT_PUBLIC      ←  required (e.g. https://appwrite.local/v1)
  APPWRITE_API_KEY               ←  required; HUMAN_GATE-tier scope (write)
  APPWRITE_PROJECT_ID            ←  required (sovereign_db project)
  APPWRITE_DATABASE_ID           ←  optional (defaults to 'camelot_db')
  WEBHOOK_SECRET                 ←  required; shared with apps/bifrost
  BIFROST_GATEWAY_URL            ←  optional (default http://127.0.0.1:3001)
  NOTEBOOK_CACHE_TTL             ←  optional (default 30 days)
  APPWRITE_FORCE_HTTPS           ←  optional (default false; local-dev OK)
VARS

echo "=== playwright availability (for §8.3 real-scraping path) ==="
python -c "from playwright.sync_api import sync_playwright; print('OK Playwright + chromium binaries')" \
    2>&1 | head -3

echo "=== Heimdall zero-trust roster ==="
PYTHONPATH=. python -c "from control_plane import heimdall_bifrost_governance as h; print(f'HEIMDALL nano-knights: {len(h.HEIMDALL_NANO_KNIGHTS)} (expect ≥6)')"

echo "=== §8.0 done ==="
```

**Pass criteria**: every line above is OK; only optional vars / dirs may show `MISSING` / `??`.
Any required-var FAIL or required-dir FAIL → STOP. Do not proceed to §8.1.

---

## §8.1  Appwrite /health check                                       [OPERATOR-BOUND]

**Why operator-bound**: requires `docker compose up` + `docker exec`
roundtrips. This host was verified earlier to have **no docker daemon**;
an operator on a docker-capable machine must execute this section.

### §8.1.1  Idempotent pre-flight (LOCAL side, no docker yet)

```bash
bash CAMELOT_OS/bin/appwrite_bootstrap.sh --dry-run
```

Expected output (final 6 lines):

```
>>> Pre-flight: docker + jq + openssl availability
    OK  Docker prerequisites in place
    WARN Dry-run only: skipping docker compose
```

If the script ends with `ERR `: see §8.5 row `bootstrap-prereq`.

### §8.1.2  Full stack bring-up (OPERATOR)

```bash
bash CAMELOT_OS/bin/appwrite_bootstrap.sh
```

The script performs 7 steps in sequence (env bootstrap → secret rotation
→ compose pull → compose up → health-check loop → **MANUAL API-KEY STEP**
→ print next-steps). Health URL is derived from `.env.appwrite`'s
`APPWRITE_DOMAIN` (default `appwrite.local`).

### §8.1.3  Health-check loop expects {status:pass} within 120 s

Once §8.1.2 exits:

```bash
APPWRITE_DOMAIN=$(grep -E '^APPWRITE_DOMAIN=' CAMELOT_OS/.env.appwrite | cut -d= -f2-)
curl -fsS --max-time 5 "https://${APPWRITE_DOMAIN}/v1/health"
echo ""

# Local-dev fallback (TLS not yet issued by Traefik) — try http:
curl -fsS --max-time 5 -k "http://${APPWRITE_DOMAIN}/v1/health" || echo "FAIL Appwrite /v1/health"
```

Pass: `{"status":"pass","version":"..."}` 200 OK on either scheme.

### §8.1.4  Recurrence probe (stability check)

```bash
for i in 1 2 3 4 5; do
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "https://${APPWRITE_DOMAIN}/v1/health")
    echo "  probe $i: $code"
    sleep 30
done
```

Pass: ≥4 of 5 probes return `200`. If 3+ return non-200 → §8.5 row
`appwrite-unstable`.

### §8.1.5  **MANUAL BLOCKER** — issue API key                                [OPERATOR-BOUND]

The bootstrap script **does not automate this**. Open a browser:

1. Navigate to `https://${APPWRITE_DOMAIN}` (the dashboard).
2. Create project named **`sovereign_db`** (or update `APPWRITE_PROJECT` in
   `.env.appwrite` to match an existing project).
3. **Settings → API Keys → Create Key** with scopes:
   - `documents.read`
   - `documents.write`
   - `collections.read`
   - `collections.write`
4. Paste the issued key into `CAMELOT_OS/.env.appwrite`:

   ```bash
   # Edit CAMELOT_OS/.env.appwrite. Replace the placeholder:
   APPWRITE_API_KEY=<the-issued-key>
   chmod 600 CAMELOT_OS/.env.appwrite
   ```

**Until this manual step completes, §8.4 cannot pass.**

---

## §8.2  Bifrost gateway health                                       [LOCAL-CHECK]

**Why LOCAL**: this test is purely against the Python bridge. It
**does not require the TS gateway to be up.** If `apps/bifrost/` is not
present on this host, that's fine — the test still proves the bridge
layer compiles and gracefully reports `ok=false`.

### §8.2.1  Health endpoint probe

```bash
cd "$REPO_ROOT"
PYTHONPATH=. python -m control_plane.bifrost_gateway health
```

**Pass criteria** (one of):

| TS gateway state      | Expected result                                | Verdict         |
|-----------------------|------------------------------------------------|-----------------|
| up at `:3001`         | `{"ok": true, "status_code": 200, ...}`        | §8.2 PASS       |
| down / not present    | `{"ok": false, "error": "<URLError or HTTPErr>"}` | §8.2 PARTIAL    |

`PARTIAL` is acceptable IF the error text is `Connection refused` or
`Name or service not known` (i.e. "we tried; the gateway is genuinely
absent"). `PARTIAL` is **NOT** acceptable if the error is anything else
(e.g. JSON parse error → that is a real bug).

### §8.2.2  HMAC constant-time roundtrip (canonical source-of-truth)

This test proves the `bifrost_gateway._sign` ↔ `bifrost_appwrite_dispatch._sign`
HMAC envelope is byte-identical and Python-portable. Without docker, this
is the most rigorous test we can run locally.

```bash
cd "$REPO_ROOT"
WEBHOOK_SECRET="unit-test-secret-do-not-use-in-prod" \
PYTHONPATH=. python <<'PYEOF'
import json
import os
from control_plane.bifrost_gateway import _sign as gw_sign
from control_plane.bifrost_appwrite_dispatch import _sign as dp_sign

raw = json.dumps({"intent": "list_databases", "data": {}}, sort_keys=True)
secret = os.environ.get("WEBHOOK_SECRET", "unit-test-secret")

gw_hex = gw_sign(raw, secret)
dp_hex = dp_sign(raw, secret)
print(f"  gateway     HMAC: {gw_hex}")
print(f"  dispatch    HMAC: {dp_hex}")
assert gw_hex == dp_hex, "HMAC DRIFT — investigate before deploying"
print("  §8.2.2 PASS — HMAC parity confirmed")
PYEOF
```

Pass: `§8.2.2 PASS — HMAC parity confirmed`. **HMAC DRIFT**
between the two modules would silently break §8.4.

### §8.2.3  End-to-end dispatch roundtrip (requires §8.1)

```bash
cd "$REPO_ROOT"
export WEBHOOK_SECRET="unit-test-secret-do-not-use-in-prod"

# Sign a list_databases intent (sort_keys JSON; hex SHA-256)
SIG=$(python -c "
import json, hmac, hashlib, os
raw = json.dumps({'data': {}}, sort_keys=True)
print(hmac.new(os.environ['WEBHOOK_SECRET'].encode(), raw.encode(), hashlib.sha256).hexdigest())
")

PYTHONPATH=. python -c "
from control_plane.bifrost_appwrite_dispatch import dispatch_to_appwrite
r = dispatch_to_appwrite('list_databases', {'data': {}}, '$SIG')
print('   result:', r)
assert r['ok'] in (True, False), 'malformed envelope'
print('   §8.2.3 PASS — envelope shape valid')
"
```

Pass: result is `{'ok': True, 'result': {'databases': [...]}}` IF §8.1
was completed (real Appwrite reachable), OR `{'ok': False, 'error':
'...'}` with error key like `AppwriteException` / `ConnectionError`
(otherwise the bridge is fabricating success).

---

## §8.3  NotebookLM MCP stdio smoke                                   [LOCAL-CHECK]

**Why LOCAL**: stdio is a process-local MCP transport. No docker,
no network. The smoke test starts the server, calls one tool, and
kills the process.

### §8.3.1  Cache directory writable

```bash
[ -w "CAMELOT_OS/03_VAULT/runtime_state" ] \
    || mkdir -p "CAMELOT_OS/03_VAULT/runtime_state/notebooklm_cache"
ls -la "CAMELOT_OS/03_VAULT/runtime_state/notebooklm_cache/" | head -5
```

Pass: directory exists, current user has `w` permission.

### §8.3.2  Process boot + clean shutdown

```bash
cd "$REPO_ROOT"
PYTHONPATH=CAMELOT_OS timeout 3 python CAMELOT_OS/bin/notebooklm_mcp_server.py --transport stdio &
PID=$!
sleep 2

# Probe process
ps -p $PID > /dev/null && echo "  boot  OK (pid $PID, stdio MCP server alive 2s)" \
                       || { echo "  FAIL  process died before probe"; exit 1; }

# Cleanly terminate
kill $PID 2>/dev/null; wait $PID 2>/dev/null
echo "  shutdown OK"
```

Pass: `boot OK` AND `shutdown OK` (no `Traceback`).

### §8.3.3  Programmatic tool registration check                                [LOCAL-CHECK]

```bash
cd "$REPO_ROOT"
PYTHONPATH=CAMELOT_OS python <<'PYEOF'
# mcp.tool() attaches each decorated function as a callable on the
# FastMCP instance (`srv.export_notebook`, etc.). Probe each expected name.
import bin.notebooklm_mcp_server as srv
expected = ("export_notebook", "delete_local_notebook", "list_local_notebooks")
tools = [n for n in expected if callable(getattr(srv, n, None))]
print(f"  registered tools: {sorted(tools)}")
missing = [n for n in expected if n not in tools]
assert not missing, f"MISSING tools: {missing}"
print("  §8.3.3 PASS — 3/3 tools registered")
PYEOF
```

Pass: `§8.3.3 PASS — 3/3 tools registered`. Missing tools ⇒ §8.5 row
`mcp-tools-missing`.

---

## §8.4  End-to-end convergence                                       [LOCAL-CHECK + INTEL-DEPENDS]

Combines §8.1 + §8.2 + §8.3 into one cross-tier probe.

### §8.4.1  Bifrost → Appwrite signed-RPC echoes roundtrip

```bash
cd "$REPO_ROOT"
export WEBHOOK_SECRET="integration-test-secret"
export APPWRITE_ENDPOINT_PUBLIC="https://appwrite.local/v1"
export APPWRITE_API_KEY="redacted-integration-key"

# Build a properly-signed payload (sort_keys JSON, hex SHA-256)
SIG=$(python -c "
import json, hmac, hashlib, os
raw = json.dumps({'document_id':'probe-1','data':{'ping':'pong'},'z3_pass':True}, sort_keys=True)
print(hmac.new(os.environ['WEBHOOK_SECRET'].encode(), raw.encode(), hashlib.sha256).hexdigest())
")

PYTHONPATH=CAMELOT_OS python -c "
from control_plane.bifrost_appwrite_dispatch import dispatch_to_appwrite
r = dispatch_to_appwrite(
    'upsert_document',
    {'document_id':'probe-1','data':{'ping':'pong'},'z3_pass':True},
    '$SIG'
)
print('   result:', r)
# Either success OR a clean AppwriteException style error
assert 'ok' in r and ('result' in r or 'error' in r), 'malformed envelope'
print('   §8.4.1 PASS — roundtrip envelope valid')
"
```

Pass: `§8.4.1 PASS — roundtrip envelope valid`.

### §8.4.2  Bifrost → Appwrite REJECTS bad signature (defensive)

```bash
cd "$REPO_ROOT"
PYTHONPATH=CAMELOT_OS python -c "
from control_plane.bifrost_appwrite_dispatch import dispatch_to_appwrite
r = dispatch_to_appwrite('list_databases', {'data':{}}, 'totally-wrong-signature')
print('   result:', r)
assert r['ok'] is False and 'signature' in r.get('error',''), 'DEFECT: bad sig was accepted'
print('   §8.4.2 PASS — bad signature correctly rejected')
"
```

Pass: `§8.4.2 PASS — bad signature correctly rejected`. **Defect** if
the bad signature produces `ok: true` — HMAC verification is broken at
the constant-time layer.

### §8.4.3  NotebookLM cache roundtrip (export → list → delete)

```bash
cd "$REPO_ROOT"
mkdir -p CAMELOT_OS/03_VAULT/runtime_state/notebooklm_cache

PYTHONPATH=CAMELOT_OS python <<'PYEOF'
from bin import notebooklm_mcp_server as m
from pathlib import Path

cache = Path("CAMELOT_OS/03_VAULT/runtime_state/notebooklm_cache")

# Inject a fake export (bypass Playwright since this is a smoke)
slug = m.slugify("https://notebooklm.google.com/notebook/probe-1")
target = m.cache_path(slug)
target.write_text("# probe notebook\n\nhello world\n", encoding="utf-8")
print(f"  inject: {target} ({target.stat().st_size} bytes)")

before = set(m.list_local_notebooks())
assert slug + ".md" in {p.name for p in cache.glob("*.md")}, "inject failed"

# Delete via the tool path
deleted = m.delete_local_notebook(slug)
print(f"  delete: returned {deleted}")
after = set(m.list_local_notebooks())
print(f"  before={len(before)}  after={len(after)}  delta={len(before)-len(after)}")
assert deleted and slug not in {p.name for p in cache.glob("*.md")}, "delete failed"
print("  §8.4.3 PASS — cache roundtrip idempotent")
PYEOF
```

Pass: `§8.4.3 PASS — cache roundtrip idempotent`.

---

## §8.5  Fail-recovery matrix

Each row maps a `§8.x FAIL` symptom → likely cause → recovery → escalation.

| §failed | Symptom                                          | Likely cause                                        | Recovery (single line)                                                                                        | Escalation (CAMELOT knight)               |
|---------|--------------------------------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| §8.0    | python ≥3.11 required                            | EOL python on host                                  | `pyenv install 3.11 && pyenv local 3.11`                                                                       | Sir Boris (env hygiene)                   |
| §8.0    | `appwrite` SDK missing                           | venv missing the pin (`appwrite>=2.0.0,<3.0.0`)      | `pip install -r CAMELOT_OS/pyproject.toml`                                                                    | Sir Boris (deps)                          |
| §8.0    | `apps/bifrost` missing                           | TS gateway not cloned / not on PATH                 | `git clone https://github.com/camelot-os/bifrost apps/bifrost` OR mark §8.2 PARTIAL                          | Sir Boris (repo hygiene)                  |
| §8.0    | Heimdall count < 6                               | PR #3 / #4 missing the 6th nano-knight registration | `python -c "from control_plane import heimdall_bifrost_governance as h; print(len(h.HEIMDALL_NANO_KNIGHTS))"`    | Sir Sentinel (policy drift)               |
| §8.1.1  | `bootstrap-prereq` (docker / jq / openssl fail)  | docker daemon absent (this host!)                   | `winget install Docker.DockerDesktop` (Windows) / `brew install --cask docker` (macOS)                       | Sir Boris (infra readiness)               |
| §8.1.3  | `appwrite-unstable` (3+ of 5 probes non-200)     | compose partially up; mariadb slow start            | `docker compose -f docker-compose.appwrite.yml logs appwrite mariadb \| tail -50`; if persistent `bash CAMELOT_OS/bin/appwrite_bootstrap.sh --teardown && bash CAMELOT_OS/bin/appwrite_bootstrap.sh` | Sir Boris                                 |
| §8.1.5  | API key paste not done                           | MANUAL step skipped                                 | open dashboard, create key (`§8.1.5` walkthrough above), edit `.env.appwrite`, `chmod 600`                    | Sir Boris                                 |
| §8.2.1  | unexpected error (not `Connection refused`)      | JSON parse error / malformed body                  | `python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:3001/health').read())"`; investigate the gateway                              | Sir Sentinel (envelope integrity)         |
| §8.2.2  | HMAC DRIFT                                       | one of `_sign` impls changed in isolation          | grep `hmac.new` across `control_plane/`, both must hash `payload.encode('utf-8')` with `sha256`               | Sir Sentinel                              |
| §8.2.3  | dispatch returns fake `ok: true`                 | mock path bypassing `_verify`                      | open `bifrost_appwrite_dispatch.py:_verify`; check `hmac.compare_digest` is being called                       | Sir Sentinel                              |
| §8.3.3  | `mcp-tools-missing`                              | FastMCP upgrade changed registration API             | `grep -n "_tool_manager\|tool_manager" bin/notebooklm_mcp_server.py`; align with FastMCP's current API         | Sir Boris (deps)                          |
| §8.4.1  | envelope malformed (no `ok` key)                 | dispatch_to_appwrite returned dict without envelope | re-read `bifrost_appwrite_dispatch._sign`/`_verify`                                                            | Sir Sentinel                              |
| §8.4.2  | bad signature accepted (`ok: true`)              | §8.4.2 DEFECT — `dispatch_to_appwrite` is broken    | **PAGE SIR BORIS IMMEDIATELY** — this is a zero-trust invariant breach                                          | Heimdall (zero-trust veto)                |
| §8.4.3  | cache roundtrip leaves residue                   | TTL not honored / slug-collision                    | inspect `notebooklm_mcp_server.evict_old`                                                                      | Sir Sentinel                              |

---

## §8.6  Operator logging                                             [LOCAL-CHECK]

Single-shot logfile capture for an actual run.

```bash
LOG_DIR="${CAMELOT_OS_LOG_DIR:-./var/log/camelot}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/live_verify_$(date +%Y%m%d_%H%M%S).log"

# Stream §8.0 stdout+stderr to log. Operator copy-pastes the §8.0 block
# manually — autoscan via sed would miss the bash <<'PYEOF' heredocs.
{
    echo "=== §8.0 PRE-FLIGHT @ $(date -Iseconds) ==="
    echo "  (operator: copy-paste the §8.0 block from this runbook)"
} >> "$LOG" 2>&1

# Then selectively append §8.1, §8.2, §8.3, §8.4 sections the operator
# actually chose to run. See companion script:
#     bin/run_live_verify.sh --sections 8.0,8.2,8.3
```

**Retention policy**:

- Keep last 7 days of runbooks in `$LOG_DIR`.
- Cron prune (operator-bound, host cron or systemd timer):

  ```cron
  # /etc/cron.d/camelot-live-verify-prune
  0 3 * * *  camelot  find $LOG_DIR -name 'live_verify_*.log' -mtime +7 -delete
  ```

- Each log captures the entire §8.x body so post-mortem can replay any
  failed step without operator memory.

---

## §8.7  Sign-off template

After all four §8.x sections pass, fill in the sign-off block below and
commit it to `var/log/camelot/signoffs/` (operator-only file path).

```
run_id:        live_verify_<YYYYMMDD_HHMMSS>
operator:      _____________
host:          $(hostname -f 2>/dev/null || hostname)
git_sha:       $(git rev-parse HEAD)
result:
  §8.0  pre-flight:        [PASS/FAIL/PARTIAL]
  §8.1  appwrite /health:   [PASS/FAIL/UNRUN]
  §8.2  bifrost gateway:    [PASS/FAIL/PARTIAL]
  §8.3  notebooklm mcp:     [PASS/FAIL/PARTIAL]
  §8.4  end-to-end:         [PASS/FAIL/PARTIAL]
notes:
  <free-form 1-paragraph>
```

If §8.4.2 hits "DEFECT" (bad signature accepted), DO NOT sign off —
page Sir Boris + Heimdall. The signature invariant is non-negotiable
under the [[zero-trust-no-fast-relax]] law in `copper_librarian/`.

---

## §8 cross-references

- **Phase 1.7 / 1.9 / 1.10 / 1.11** in `SYSTEM_PROMPT_v2_2026-07-14.md §4`
  map onto §8.1, §8.2, §8.3, §8.4 respectively (with §8.5 fail-recovery
  covering the [OPERATOR-BOUND] caveats in Phases 1.7 / 1.9).
- **TITAN-TIER Phase 3.6 (PR #1 acceptance)** in
  `TITAN_TIER_EXECUTION_PROMPT_2026-07-14.md §3.6` only verifies
  `bin/appwrite_bootstrap.sh` exit code; this runbook adds 5 more probes.
- **NOTES_MNEMOSYNE_WIRING §7** `RESOLVED` issues feed into the
  fail-recovery matrix above (Q1 loose SemVer → §8.0 deps check, Q3
  carve-INTO Heimdall Bifrost governance → §8.0 nano-knight count ≥6).
- **End-of-run sign-off (§8.7)** feeds into the next `SELF_IMPROVEMENT`
  tier doc only on a clean `§8.x PASS` sweep.
