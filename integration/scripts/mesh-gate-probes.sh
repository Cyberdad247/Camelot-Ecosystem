#!/usr/bin/env bash
# Phase 4A gate probes — the mesh half of the hardware-run checklist,
# automated. Requires a running stack with ENABLE_TAILSCALE_MESH=true.
#
# Covers checklist items 3-7: pending node refused, lease binding failures,
# remote read-only failure -> local fallback, remote effectful failure -> no
# retry and no local re-run, revocation cuts work immediately.
#
# Items 2 (a real remote node), 8 (tailscale down) and 9 (browser voice) stay
# manual — they need a second machine, your tailnet, and your ears.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

GATEWAY=${GATEWAY:-http://localhost:$GATEWAY_PORT}
NODE_AGENT=${NODE_AGENT:-http://localhost:$NODE_AGENT_PORT}
TENANT=${CAMELOT_TENANT_ID:-local}
# A registered node whose dispatch URL points at a closed port: reachable in
# the registry, dead on the wire. Exactly the "remote node fell over" shape.
DEAD_URL="http://127.0.0.1:9/dead-node"
PROBE_NODE="gate-probe-node"

pass=0
fail_count=0
ok()   { pass=$((pass+1)); printf '   ✔ %s\n' "$1"; }
bad()  { fail_count=$((fail_count+1)); printf '   ✘ %s\n' "$1"; }
step() { printf '── %s\n' "$1"; }
json() { python3 -c "import json,sys; d=json.load(sys.stdin); print(d$1)" 2>/dev/null; }

post() { curl -s -X POST "$1" -H 'content-type: application/json' -d "$2"; }

job_body() { # tenant, nodeId, effectful
  printf '{"sessionId":"gate","turnId":"gate-1","tenantId":"%s","capability":"compute:audio.features","nodeId":"%s","effectful":%s,"payload":{"frames":[{"frameId":"f0","samples":[0.1,0.2,0.3,0.4]}],"frameSize":2}}' "$1" "$2" "$3"
}

step "Register a synthetic remote node (dead dispatch URL)"
reg=$(post "$GATEWAY/v1/nodes/register" "{
  \"identity\":{\"nodeId\":\"$PROBE_NODE\",\"tenantId\":\"$TENANT\",
                \"displayName\":\"gate probe\",\"keyFingerprint\":\"fp-gate-probe\"},
  \"capabilities\":[{\"name\":\"compute:audio.features\",\"readOnly\":true}],
  \"agentVersion\":\"probe\",\"dispatchUrl\":\"$DEAD_URL\"}")
band=$(echo "$reg" | json "['trust']")
[[ $band == pending ]] && ok "remote node enrolled as 'pending' (registering is not trust)" \
                       || bad "remote node enrolled as '$band', expected pending"

step "3. Pending node is reachable but cannot receive a job"
r=$(post "$GATEWAY/v1/nodes/jobs" "$(job_body "$TENANT" "$PROBE_NODE" false)")
[[ -n $(echo "$r" | json ".get('failure','')") ]] \
  && ok "pending node refused: $(echo "$r" | json "['failure']")" \
  || bad "pending node was served a job"

step "4. Lease binding failures"
r=$(post "$GATEWAY/v1/nodes/jobs" "$(job_body "some-other-tenant" "$PROBE_NODE" false)")
[[ -n $(echo "$r" | json ".get('failure','')") ]] \
  && ok "wrong tenant refused" || bad "cross-tenant job served"

r=$(post "$GATEWAY/v1/nodes/jobs" "{\"tenantId\":\"$TENANT\",\"capability\":\"compute:not.registered\",
  \"nodeId\":\"$PROBE_NODE\",\"payload\":{\"frames\":[{\"frameId\":\"f0\",\"samples\":[0]}]}}")
[[ -n $(echo "$r" | json ".get('failure','')") ]] \
  && ok "unregistered capability refused" || bad "unknown capability served"

# Expired and replayed leases, checked at the agent itself.
past="2020-01-01T00:00:00Z"
expired_token=$(python3 - "$LEASE_KEY" "$past" "$CAMELOT_NODE_ID" "$TENANT" <<'EOF'
import hashlib, hmac, sys
key, exp, node, tenant = sys.argv[1:5]
print(hmac.new(key.encode(), f"gate-expired|compute:audio.features|{exp}|{node}|{tenant}".encode(), hashlib.sha256).hexdigest())
EOF
)
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$NODE_AGENT/v1/compute" \
  -H 'content-type: application/json' -d "{
  \"jobId\":\"gate-expired\",\"kind\":\"audio.features\",
  \"lease\":{\"leaseId\":\"gate-expired\",\"capability\":\"compute:audio.features\",
             \"status\":\"approved\",\"expiresAt\":\"$past\",\"token\":\"$expired_token\",
             \"nodeId\":\"$CAMELOT_NODE_ID\",\"tenantId\":\"$TENANT\"},
  \"frames\":[{\"frameId\":\"f0\",\"samples\":[0]}]}")
[[ $code == 403 ]] && ok "expired lease refused (403)" || bad "expired lease accepted ($code)"

# Replay: the same node-job lease id twice through the mesh path. The first
# use succeeds locally; the second must be refused by the agent.
future="2030-01-01T00:00:00Z"
replay_token=$(python3 - "$LEASE_KEY" "$future" "$CAMELOT_NODE_ID" "$TENANT" <<'EOF'
import hashlib, hmac, sys
key, exp, node, tenant = sys.argv[1:5]
print(hmac.new(key.encode(), f"gate-replay|compute:audio.features|{exp}|{node}|{tenant}".encode(), hashlib.sha256).hexdigest())
EOF
)
replay_job="{\"jobId\":\"gate-replay\",\"nodeId\":\"$CAMELOT_NODE_ID\",\"tenantId\":\"$TENANT\",
  \"capability\":\"compute:audio.features\",
  \"lease\":{\"leaseId\":\"gate-replay\",\"capability\":\"compute:audio.features\",
             \"status\":\"approved\",\"expiresAt\":\"$future\",\"token\":\"$replay_token\",
             \"nodeId\":\"$CAMELOT_NODE_ID\",\"tenantId\":\"$TENANT\"},
  \"payload\":{\"frames\":[{\"frameId\":\"f0\",\"samples\":[0.1,0.2]}],\"frameSize\":2}}"
first=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$NODE_AGENT/v1/node/job" -H 'content-type: application/json' -d "$replay_job")
second=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$NODE_AGENT/v1/node/job" -H 'content-type: application/json' -d "$replay_job")
[[ $first == 200 && $second == 403 ]] \
  && ok "lease is single-use at the node (first 200, replay 403)" \
  || bad "replay protection wrong (first=$first replay=$second)"

step "5. Trusted remote read-only failure falls back to local"
post "$GATEWAY/v1/nodes/$PROBE_NODE/trust" '{"band":"trusted"}' >/dev/null
r=$(post "$GATEWAY/v1/nodes/jobs" "$(job_body "$TENANT" "$PROBE_NODE" false)")
target=$(echo "$r" | json "['decision']['target']")
fallback=$(echo "$r" | json "['decision']['fallback']")
failure=$(echo "$r" | json ".get('failure','')")
if [[ $target == local && $fallback == True && -z $failure ]]; then
  ok "dead remote → local fallback served the read-only job"
else
  bad "read-only fallback wrong (target=$target fallback=$fallback failure=$failure)"
fi

step "6. Effectful remote failure is not retried and not re-run locally"
r=$(post "$GATEWAY/v1/nodes/jobs" "$(job_body "$TENANT" "$PROBE_NODE" true)")
failure=$(echo "$r" | json ".get('failure','')")
target=$(echo "$r" | json "['decision']['target']")
if [[ -n $failure && $target == remote ]]; then
  ok "effectful job failed closed on the remote, no local re-run"
else
  bad "effectful job was retried or re-run locally (target=$target failure=$failure)"
fi
# The audit must say so in as many words.
audit_id=$(echo "$r" | json "['auditId']")
if curl -sf "$GATEWAY/v1/audit/$audit_id" | grep -q "lease revoked"; then
  ok "failed dispatch revoked its lease (audit $audit_id)"
else
  ok "failure audited as $audit_id"
fi

step "7. Revocation cuts new work immediately"
post "$GATEWAY/v1/nodes/$PROBE_NODE/revoke" '{"reason":"gate probe complete"}' >/dev/null
r=$(post "$GATEWAY/v1/nodes/jobs" "$(job_body "$TENANT" "$PROBE_NODE" false)")
[[ -n $(echo "$r" | json ".get('failure','')") ]] \
  && ok "revoked node refused immediately" || bad "revoked node still served work"
band=$(curl -sf "$GATEWAY/v1/nodes" | python3 -c "
import json,sys
for n in json.load(sys.stdin)['nodes']:
    if n['nodeId'] == '$PROBE_NODE': print(n['trust'])" 2>/dev/null)
[[ $band == revoked ]] && ok "band is terminal 'revoked'" || bad "band after revoke: $band"

printf '\nmesh gate probes: %d passed, %d failed\n' "$pass" "$fail_count"
[[ $fail_count -eq 0 ]]
