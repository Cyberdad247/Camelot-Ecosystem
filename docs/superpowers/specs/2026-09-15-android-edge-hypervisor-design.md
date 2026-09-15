# Android Edge Supervisor Design

## Status

Approved architecture and protocol design. This document defines the implementation
boundary for the Motorola Moto G Power 5G (2024) Camelot edge node. It is not a
device-enrollment instruction and it contains no credentials.

## Goal

Deliver `camelot-edge`, a native ARM64 Termux-hosted supervisor with a target
binary size at or below 16 MB. It provides offline continuity for the existing
Bifrost/VPS control plane while retaining the VPS as the source of policy and
authority.

The edge supervisor is a user-space process supervisor, not an Android virtual
machine hypervisor. It must not require root, ADB, Shizuku, PRoot, or a desktop
environment.

## Non-goals

- Hosting a language model, model-provider client, or general-purpose agent loop.
- Arbitrary command execution, package installation, VFS mutation, or device
  automation.
- Holding cloud-provider credentials, Bifrost administrative credentials, or an
  authoritative copy of state.
- Replacing the VPS Bifrost gateway, the runic router, or the S26 command center.
- Making Omarchy Android, Hermes Relay, Needle, PocketStrike AI, or mobileLM a
  required dependency of the edge supervisor.

## Topology

```text
Moto G Power / Android 15
  Termux + Termux:Boot
    camelot-edge (native ARM64 supervisor)
      policy snapshot verifier
      bounded local SQLite state
      outbox and receipt sender
      health and route probes
              |
              | Tailscale-only, authenticated edge protocol
              v
KVM563 VPS
  Bifrost Gateway :3001 + mesh bridge :8095
    policy issuer, receipt reconciliation, route authority
```

The Moto originates all communications. No public listener is added to the
phone. The VPS exposes edge endpoints only on the tailnet and no handler may
use permissive cross-origin access for an authenticated route.

## Component boundaries

### `camelot-edge`

New native service, implemented in Rust or Go after the implementation plan
selects the smaller audited dependency surface. It owns only:

- Device identity material stored locally with restrictive file permissions.
- The latest valid signed policy snapshot.
- A bounded outbox and immutable receipt log.
- Health telemetry: process state, battery/charging status when permitted,
  disk/RAM summary, Tailscale reachability, and edge version.
- A strict action dispatcher.

It does not accept a local HTTP control API. Status is printed locally and
reported upstream through the authenticated protocol.

### VPS edge adapter

The existing `control_plane/dispatch/vps_mobile_mesh_bridge.py` is a temporary
topology/telemetry surface, not the authoritative edge protocol. A dedicated
adapter will be introduced behind the Bifrost gateway. It validates device
identity, request signature, timestamp, nonce, schema, and action scope before
persisting any input.

The current runtime-token guard remains a compatibility gate until the edge
adapter replaces its endpoint. The migration must fail closed if either gate is
absent.

### Optional clients

| Candidate | Permitted role | Prohibited role |
| --- | --- | --- |
| Termux | Host and bootstrap environment | Authority or credential store in source |
| Omarchy Android | Optional terminal/HUD desktop | Host for `camelot-edge` or security boundary |
| Hermes Relay | Optional paired operator UI | Device-control or tool grant by default |
| Needle | Future local intent classification pilot | Direct Termux API/device control |
| mobileLM | Future private local chat pilot | Network-exposed Camelot control API |
| PocketStrike AI | Reference-only capability review | Runtime dependency or execution surface |
| Excalibur Command Center | Deferred pending source audit | Runtime dependency |

## Protocol contract

All requests use the tailnet address of the VPS and a versioned `/v1/edge/*`
path. Payloads are canonical JSON and include `device_id`, `issued_at`,
`expires_at`, and `nonce`. The device signs each request with its private
Ed25519 key. The VPS verifies against a registered public key and rejects
replayed, expired, malformed, or unregistered messages.

### Snapshot pull

`GET /v1/edge/snapshot` returns a signed document:

```json
{
  "version": 1,
  "device_id": "motorola-moto-g-power-5g---2024",
  "issued_at": "RFC3339 UTC timestamp",
  "expires_at": "RFC3339 UTC timestamp",
  "allowed_actions": ["health_probe", "notify", "refresh_snapshot"],
  "route": {"state": "tailnet_only"},
  "signature": "base64 Ed25519 signature"
}
```

The edge accepts a snapshot only when the signature verifies, its device ID
matches, and it has not expired. It retains only the latest verified version.

### Receipts and outbox replay

`POST /v1/edge/receipts` records completed safe actions. `POST
/v1/edge/outbox` submits queued requests after reconnect. Both endpoints are
idempotent by `(device_id, nonce)` and return an acknowledgement receipt.

The local outbox is capped by record count and bytes. Every entry has a TTL.
When full, the oldest telemetry item may be dropped; an action request is never
silently overwritten. Invalid or expired entries are deleted locally and
reported on the next successful connection.

## Action policy

Permitted actions are only:

- `health_probe`
- `tailscale_route_check`
- `collect_telemetry`
- `notify`
- `refresh_snapshot`
- `flush_outbox`

The dispatcher rejects all other names before any platform call. In particular,
it rejects shell execution, package changes, filesystem changes outside its
state directory, network scans, ADB/Shizuku calls, SMS, calling, camera,
location, clipboard reads, model-provider requests, and instruction supplied by
an optional client.

## Lifecycle and failure handling

- Termux:Boot launches a small launcher that starts `camelot-edge` once.
- The supervisor uses bounded exponential backoff after a crash; it never spins
  indefinitely or restarts optional clients.
- An unavailable VPS enters offline mode: only cached policy and local health
  work continue.
- Invalid identity, bad signature, clock-skew beyond the permitted window, or
  an authorization failure enters fail-closed mode and emits a local status
  record.
- Android process termination is expected. Termux:Boot provides recovery after
  device restart; battery-optimization changes require a human enrollment step.

## Security invariants

1. Tailscale routing is necessary but insufficient; every protocol message is
   authenticated and replay-protected.
2. Private keys and device tokens never enter source control, logs, runtime
   artifacts committed to the repository, or `config.json`.
3. The edge process owns no administrative capability and cannot promote itself.
4. Every state-changing upstream request is idempotent, auditable, time-bounded,
   and requires a current verified policy.
5. Optional applications have request-only authority; the native allowlist is
   the enforcement point.

## Implementation slices and gates

1. **Contract slice:** typed policy/receipt schemas, signature verifier, nonce
   cache, and unit tests for all reject paths.
2. **Edge core:** native process, bounded SQLite store, snapshot verifier,
   telemetry collector, and fake-VPS integration test.
3. **VPS adapter:** tailnet bind, strict CORS/origin policy, device registry via
   public-key fingerprints, endpoint validation, and reconciliation tests.
4. **Termux packaging:** non-secret install instructions, Termux:Boot launcher,
   health/status command, and no automatic package installation.
5. **Physical enrollment:** human-approved device key generation, Tailscale ACL
   enrollment, battery-policy change, and recovery test on the Moto.
6. **Optional pilots:** Needle intent classifier, mobileLM, Hermes Relay, and
   Omarchy are each separate opt-in work items after the core passes.

Completion requires passing unit and fake-VPS tests, an adversarial replay and
bad-signature test suite, manual Termux restart recovery, and a Moto dry run
that uses no production credentials.

## Evidence and source assessment

The source assessment supporting the optional-client decisions is recorded in
the conversation and must be refreshed before each pilot. The current
`excalibur-command-center` source is deferred because its Git reference was
reachable but public GitHub content inspection was unavailable at assessment
time.
