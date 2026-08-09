#!/usr/bin/env bash
# Smoke test for the Camelot x Kickbox voice slice (bootstrap-plan T7).
# Requires a running stack: `make demo-dev` or `make demo-up`.
set -euo pipefail

GATEWAY=${GATEWAY:-http://localhost:8788}
NODE_AGENT=${NODE_AGENT:-http://localhost:8789}
HERMES=${HERMES:-http://localhost:8790}
CONSOLE=${CONSOLE:-http://localhost:8080}
LEASE_KEY=${LEASE_KEY:-camelot-demo-key}
ENABLE_HERMES_VOICE=${ENABLE_HERMES_VOICE:-false}
ENABLE_TAILSCALE_MESH=${ENABLE_TAILSCALE_MESH:-false}
CAMELOT_NODE_ID=${CAMELOT_NODE_ID:-local-node}
CAMELOT_TENANT_ID=${CAMELOT_TENANT_ID:-local}
SESSION=sess-anya-demo-001
# smoke.sh stays standalone (no lib.sh) so it can run against any stack; the
# artifact root follows the same override-with-default convention.
# The gateway honours CAMELOT_EFFECT_ROOT, and dev-up passes the environment
# through, so smoke must look where the gateway was actually told to write.
ARTIFACTS=${ARTIFACTS:-${CAMELOT_EFFECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.run/artifacts}}
NOTE_TURN="smoke-note-$(date +%s%N)"
NOTE_DIR="$ARTIFACTS/notes.local.write"

pass=0
step() { printf '── %s\n' "$1"; }
ok() { pass=$((pass+1)); printf '   ✔ %s\n' "$1"; }
fail() { printf '   ✘ %s\n' "$1"; exit 1; }

json() { python3 -c "import json,sys; d=json.load(sys.stdin); print(d$1)"; }

step "1. Health"
[[ $(curl -sf "$GATEWAY/healthz" | json "['status']") == ok ]] || fail "gateway healthz"
ok "gateway healthy"
[[ $(curl -sf "$NODE_AGENT/healthz" | json "['status']") == ok ]] || fail "node-agent healthz"
backend=$(curl -sf "$NODE_AGENT/healthz" | json "['backend']")
ok "node-agent healthy (backend: $backend)"
curl -sf -o /dev/null "$CONSOLE/kickbox/" || fail "console index"
curl -sf -o /dev/null "$CONSOLE/kickbox/dist/app.js" || fail "console app.js"
curl -sf -o /dev/null "$CONSOLE/contracts/dist/index.js" || fail "contracts esm"
ok "console + contracts served"

step "2. Tier-1 read (no lease)"
r=$(curl -sf -X POST "$GATEWAY/v1/voice/turns" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"turnId\":\"smoke-t1\",\"modality\":\"text\",
  \"transcript\":\"read staging status\",\"startedAtMs\":1}")
[[ $(echo "$r" | json "['decision']['effect']") == allow ]] || fail "tier-1 effect"
[[ $(echo "$r" | json ".get('lease')") == None ]] || fail "tier-1 must not carry a lease"
ok "allowed without lease, artifact: $(echo "$r" | json "['artifact']['kind']")"

step "3. Tier-2 draft (auto-lease, consumed)"
r=$(curl -sf -X POST "$GATEWAY/v1/voice/turns" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"turnId\":\"smoke-t2\",\"modality\":\"text\",
  \"transcript\":\"prepare a deployment review\",\"startedAtMs\":1}")
[[ $(echo "$r" | json "['artifact']['kind']") == deployment_review_draft ]] || fail "tier-2 artifact"
[[ $(echo "$r" | json "['lease']['status']") == consumed ]] || fail "tier-2 lease consumed"
ok "draft created under consumed lease $(echo "$r" | json "['lease']['leaseId']")"

step "4. Tier-3 requires confirmation"
r=$(curl -sf -X POST "$GATEWAY/v1/voice/turns" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"turnId\":\"smoke-t3\",\"modality\":\"text\",
  \"transcript\":\"create a change request to scale the api tier\",\"startedAtMs\":1}")
[[ $(echo "$r" | json "['decision']['effect']") == requires_confirmation ]] || fail "tier-3 effect"
[[ $(echo "$r" | json "['uiState']") == blocked ]] || fail "tier-3 uiState"
lease3=$(echo "$r" | json "['lease']['leaseId']")
[[ $(echo "$r" | json "['lease']['status']") == pending ]] || fail "tier-3 pending lease"
ok "blocked with pending lease $lease3"

c=$(curl -sf -X POST "$GATEWAY/v1/confirmations" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"leaseId\":\"$lease3\",\"approve\":true}")
[[ $(echo "$c" | json "['artifact']['kind']") == change_request ]] || fail "confirmed execution"
[[ $(echo "$c" | json "['lease']['status']") == consumed ]] || fail "lease consumed on approval"
ok "approved -> executed -> lease consumed"

step "4b. Durable local effect (real file, brokered)"
r=$(curl -sf -X POST "$GATEWAY/v1/voice/turns" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"turnId\":\"$NOTE_TURN\",\"modality\":\"text\",
  \"transcript\":\"save a note about the smoke run\",\"startedAtMs\":1}")
[[ $(echo "$r" | json "['decision']['skillId']") == notes.local.write ]] || fail "note turn did not resolve to the durable skill"
[[ $(echo "$r" | json "['lease']['status']") == consumed ]] || fail "note lease not consumed"
# Artifacts are named from the LEASE (plus a per-process run id), not the
# turn, so locate the new one rather than reconstructing a server-owned name.
NOTE=$(ls -t "$NOTE_DIR"/*.txt 2>/dev/null | head -1)
[[ -n $NOTE && -s $NOTE ]] || fail "no file was written under $NOTE_DIR"
ok "governed write produced $(wc -c <"$NOTE") bytes at notes.local.write/$(basename "$NOTE")"

# The audit records WHAT the effect did (size + digest), not the material.
a=$(curl -sf "$GATEWAY/v1/audit/$(echo "$r" | json "['auditId']")")
summary=$(echo "$a" | json "['redactedSummary']")
[[ $summary == *bytes* && $summary == *sha256* ]] || fail "audit lacks the effect result: $summary"
[[ $summary != *"smoke run"* ]] || fail "audit leaked the note body"
[[ $(echo "$a" | json "['transcriptSha256']") != "" ]] || fail "audit lacks the transcript hash"
ok "audit carries size+digest, not the body"

# Re-submit the SAME turn id with different content. Policy mints a second
# lease, so this is a second authorized action: it gets its own artifact and
# must not disturb the first. Naming artifacts after the lease rather than the
# turn is what makes that true - and is why a page reload no longer collides.
before=$(sha256sum "$NOTE" | cut -d" " -f1)
count_before=$(ls "$NOTE_DIR"/*.txt | wc -l)
curl -sf -X POST "$GATEWAY/v1/voice/turns" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"turnId\":\"$NOTE_TURN\",\"modality\":\"text\",
  \"transcript\":\"save a note RESUBMITTED with different content\",\"startedAtMs\":1}" >/dev/null
after=$(sha256sum "$NOTE" | cut -d" " -f1)
count_after=$(ls "$NOTE_DIR"/*.txt | wc -l)
[[ $before == $after ]] || fail "re-submitted turn altered the earlier artifact"
(( count_after == count_before + 1 )) || fail "second authorization did not produce its own artifact"
ok "re-submitted turn wrote a separate artifact; the first is untouched"

step "5. Barge-in revokes unused lease"
r=$(curl -sf -X POST "$GATEWAY/v1/voice/turns" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"turnId\":\"smoke-t4\",\"modality\":\"text\",
  \"transcript\":\"create a change request for the barge-in check\",\"startedAtMs\":1}")
lease4=$(echo "$r" | json "['lease']['leaseId']")
b=$(curl -sf -X POST "$GATEWAY/v1/voice/barge-in" -H 'content-type: application/json' -d "{
  \"sessionId\":\"$SESSION\",\"turnId\":\"smoke-t4\",\"atMs\":1,\"reason\":\"mock\"}")
[[ $(echo "$b" | json "['revokedLeaseIds'][0]") == "$lease4" ]] || fail "lease not revoked"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$GATEWAY/v1/confirmations" \
  -H 'content-type: application/json' \
  -d "{\"sessionId\":\"$SESSION\",\"leaseId\":\"$lease4\",\"approve\":true}")
[[ $code == 409 ]] || fail "revoked lease still approvable (got $code)"
ok "barge-in revoked $lease4; later approval rejected (409)"

step "6. Audit trail (redacted, chained)"
audit_id=$(echo "$b" | json "['auditId']")
a=$(curl -sf "$GATEWAY/v1/audit/$audit_id")
echo "$a" | json "['hash']" >/dev/null || fail "audit hash"
echo "$a" | json "['prevHash']" >/dev/null || fail "audit prevHash"
ok "audit $audit_id fetched with hash chain"

step "7. Node-agent compute under signed lease"
exp="2030-01-01T00:00:00Z"
# An ENROLLED agent accepts only leases bound to itself, so the synthetic
# lease must carry this node/tenant when the mesh is on (empty when it is off).
if [[ $ENABLE_TAILSCALE_MESH == true ]]; then
  lease_node=$CAMELOT_NODE_ID
  lease_tenant=$CAMELOT_TENANT_ID
else
  lease_node=""
  lease_tenant=""
fi
token=$(python3 - "$LEASE_KEY" "$exp" "$lease_node" "$lease_tenant" <<'EOF'
import hashlib, hmac, sys
key, exp, node, tenant = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
# Signature covers node and tenant too (Phase 4A binding).
msg = f"smoke-lease|compute:audio.features|{exp}|{node}|{tenant}".encode()
print(hmac.new(key.encode(), msg, hashlib.sha256).hexdigest())
EOF
)
r=$(curl -sf -X POST "$NODE_AGENT/v1/compute" -H 'content-type: application/json' -d "{
  \"jobId\":\"smoke-job\",\"kind\":\"audio.features\",
  \"lease\":{\"leaseId\":\"smoke-lease\",\"capability\":\"compute:audio.features\",
             \"status\":\"approved\",\"expiresAt\":\"$exp\",\"token\":\"$token\",
             \"nodeId\":\"$lease_node\",\"tenantId\":\"$lease_tenant\"},
  \"frames\":[{\"frameId\":\"f0\",\"samples\":[0,0.5,-0.5,0.25]},
              {\"frameId\":\"f1\",\"samples\":[0.1,0.1,0.1,0.1]}],\"frameSize\":2}")
[[ $(echo "$r" | json "['results'][0]['features']['peak']") == 0.5 ]] || fail "compute peak"
count=$(echo "$r" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['results']))")
[[ $count == 2 ]] || fail "batched frames (got $count)"
ok "batched compute on backend: $(echo "$r" | json "['backend']")"

code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$NODE_AGENT/v1/compute" \
  -H 'content-type: application/json' -d "{
  \"jobId\":\"smoke-bad\",\"kind\":\"audio.features\",
  \"lease\":{\"leaseId\":\"smoke-lease\",\"capability\":\"compute:audio.features\",
             \"status\":\"approved\",\"expiresAt\":\"$exp\",\"token\":\"forged\",
             \"nodeId\":\"$lease_node\",\"tenantId\":\"$lease_tenant\"},
  \"frames\":[{\"frameId\":\"f0\",\"samples\":[0]}]}")
[[ $code == 403 ]] || fail "forged compute token accepted (got $code)"
ok "forged compute token rejected (403)"

if [[ $ENABLE_TAILSCALE_MESH == true ]]; then
  # A perfectly signed lease minted for ANOTHER node is still refused.
  other_token=$(python3 - "$LEASE_KEY" "$exp" "$CAMELOT_TENANT_ID" <<'EOF'
import hashlib, hmac, sys
key, exp, tenant = sys.argv[1], sys.argv[2], sys.argv[3]
msg = f"smoke-lease-b|compute:audio.features|{exp}|someone-elses-node|{tenant}".encode()
print(hmac.new(key.encode(), msg, hashlib.sha256).hexdigest())
EOF
)
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$NODE_AGENT/v1/compute" \
    -H 'content-type: application/json' -d "{
    \"jobId\":\"smoke-other-node\",\"kind\":\"audio.features\",
    \"lease\":{\"leaseId\":\"smoke-lease-b\",\"capability\":\"compute:audio.features\",
               \"status\":\"approved\",\"expiresAt\":\"$exp\",\"token\":\"$other_token\",
               \"nodeId\":\"someone-elses-node\",\"tenantId\":\"$CAMELOT_TENANT_ID\"},
    \"frames\":[{\"frameId\":\"f0\",\"samples\":[0]}]}")
  [[ $code == 403 ]] || fail "another node's valid lease was accepted (got $code)"
  ok "another node's validly-signed lease rejected (403)"
fi

step "8. Model routing (deterministic default)"
# Narrations count on completion — poll briefly while streams finish.
requests=0
for _ in $(seq 1 20); do
  m=$(curl -sf "$GATEWAY/v1/models/stats")
  requests=$(echo "$m" | json "['requests']")
  [[ $requests -ge 1 ]] && break
  sleep 0.5
done
[[ $requests -ge 1 ]] || fail "model stats requests never incremented"
provider=$(echo "$m" | json "['provider']")
fallbacks=$(echo "$m" | json "['fallbacks']")
ok "replies narrated by '$provider' (requests=$requests, fallbacks=$fallbacks)"

if [[ $ENABLE_HERMES_VOICE == true ]]; then
  step "9. Hermes voice adapter (ENABLE_HERMES_VOICE=true)"
  [[ $(curl -sf "$HERMES/healthz" | json "['status']") == ok ]] || fail "hermes healthz"
  ok "hermes healthy (stt: $(curl -sf "$HERMES/healthz" | json "['stt']"))"

  # Loud 700ms sine -> scripted transcript; pure silence -> NO transcript.
  loud=$(python3 -c "
import base64, math, struct
sr = 16000
pcm = b''.join(struct.pack('<h', int(math.sin(2*math.pi*440*i/sr)*0.5*32767)) for i in range(int(sr*0.7)))
print(base64.b64encode(pcm).decode())")
  r=$(curl -sf -X POST "$HERMES/v1/stt" -H 'content-type: application/json' \
    -d "{\"sampleRate\":16000,\"pcm16\":\"$loud\"}")
  [[ $(echo "$r" | json "['transcript']") != None ]] || fail "hermes stt on speech-energy audio"
  ok "stt transcribed speech-energy audio: $(echo "$r" | json "['transcript']")"

  silence=$(python3 -c "import base64; print(base64.b64encode(b'\x00\x00'*8000).decode())")
  r=$(curl -sf -X POST "$HERMES/v1/stt" -H 'content-type: application/json' \
    -d "{\"sampleRate\":16000,\"pcm16\":\"$silence\"}")
  [[ $(echo "$r" | json "['transcript']") == None ]] || fail "silence must yield no transcript"
  ok "silence yields no transcript (nothing submittable)"

  wav_header=$(curl -sf -X POST "$HERMES/v1/tts" -H 'content-type: application/json' \
    -d '{"text":"Staging is green."}' | head -c 4)
  [[ $wav_header == RIFF ]] || fail "hermes tts wav"
  ok "tts produced a WAV stream"
fi

if [[ $ENABLE_TAILSCALE_MESH == true ]]; then
  step "10. Mesh node registry (ENABLE_TAILSCALE_MESH=true)"
  nodes=$(curl -sf "$GATEWAY/v1/nodes")
  count=$(echo "$nodes" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['nodes']))")
  [[ $count -ge 1 ]] || fail "no node enrolled"
  ok "$count node(s) enrolled"

  # The local agent is auto-trusted; a node list must never leak an address.
  local_trust=$(echo "$nodes" | python3 -c "
import json,sys
nodes = json.load(sys.stdin)['nodes']
local = [n for n in nodes if n['local']]
print(local[0]['trust'] if local else 'none')")
  [[ $local_trust == trusted ]] || fail "local node band is $local_trust, expected trusted"
  ok "local node trusted; mesh backend: $(echo "$nodes" | python3 -c "
import json,sys
nodes = json.load(sys.stdin)['nodes']
print(nodes[0].get('meshBackend') or 'none')")"

  echo "$nodes" | grep -qE 'https?://' && fail "node list leaked a dispatch address"
  echo "$nodes" | grep -q 'dispatchUrl\|keyFingerprint' && fail "node list leaked identity material"
  ok "node list carries no addresses or key material"

  # Local-first routing actually reaches the agent and returns a result.
  r=$(curl -sf -X POST "$GATEWAY/v1/nodes/jobs" -H 'content-type: application/json' -d "{
    \"sessionId\":\"$SESSION\",\"turnId\":\"smoke-n1\",\"tenantId\":\"$CAMELOT_TENANT_ID\",
    \"capability\":\"compute:audio.features\",
    \"payload\":{\"frames\":[{\"frameId\":\"f0\",\"samples\":[0,0.5,-0.5,0.25]}],\"frameSize\":2}}")
  [[ $(echo "$r" | json "['decision']['target']") == local ]] || fail "job did not route local-first"
  [[ $(echo "$r" | json ".get('failure','')") == "" ]] || fail "local node job failed: $(echo "$r" | json "['failure']")"
  ok "local-first job served under a node lease (audit $(echo "$r" | json "['auditId']"))"

  # An unknown node is refused outright.
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$GATEWAY/v1/nodes/jobs" \
    -H 'content-type: application/json' -d "{
    \"tenantId\":\"$CAMELOT_TENANT_ID\",\"capability\":\"compute:audio.features\",
    \"nodeId\":\"ghost-node\",\"payload\":{\"frames\":[{\"frameId\":\"f0\",\"samples\":[0]}]}}")
  [[ $code == 502 ]] || fail "unregistered node was not refused (got $code)"
  ok "unregistered node refused"

  # Cross-tenant request is refused even for a real, trusted node.
  r=$(curl -s -X POST "$GATEWAY/v1/nodes/jobs" -H 'content-type: application/json' -d "{
    \"tenantId\":\"other-tenant\",\"capability\":\"compute:audio.features\",
    \"nodeId\":\"$CAMELOT_NODE_ID\",\"payload\":{\"frames\":[{\"frameId\":\"f0\",\"samples\":[0]}]}}")
  [[ $(echo "$r" | json ".get('failure','')") != "" ]] || fail "cross-tenant job was served"
  ok "cross-tenant job refused"
fi

printf '\n✅ smoke passed (%d checks) — Anya Console: %s/kickbox/\n' "$pass" "$CONSOLE"
