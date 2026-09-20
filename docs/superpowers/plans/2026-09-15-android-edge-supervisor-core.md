# Android Edge Supervisor Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use \`superpowers:executing-plans\` to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Turn the existing \`camelot-edge\` Rust pill into a Termux-compatible, signed, offline-capable Moto edge supervisor with a matched VPS protocol adapter.

**Architecture:** The Rust crate owns its identity, canonical protocol encoding, signed snapshot verification, bounded SQLite state, and standard-library HTTP/Tailscale client. A Python adapter owns VPS-side public-key registration, signed snapshot issuance, replay protection, and request validation; the existing mesh bridge delegates \`/v1/edge/*\` without widening legacy routes.

**Tech Stack:** Rust 2021, \`ed25519-dalek\`, \`serde\`, \`serde_json\`, bundled \`rusqlite\`, Python 3.13 plus existing \`cryptography\`, \`pytest\`, Termux and Termux:Boot.

**Spec:** \`docs/superpowers/specs/2026-09-15-android-edge-hypervisor-design.md\`

## Global Constraints

- Keep \`camelot-edge\` a native ARM64 Termux process; it must not require root, ADB, Shizuku, PRoot, Python, Node, or a local listener.
- Release binary target is at or below 16 MB. Measure stripped ARM64 output before enrollment.
- Use strict Ed25519 verification and bundled SQLite. Add no model, browser, agent, or general HTTP-client dependency.
- Transmit only through a configured Tailscale VPS endpoint and \`/v1/edge/*\`; never fall back to public WAN.
- Never commit key material, device tokens, runtime databases, snapshots, or enrollment output.
- Permit only \`health_probe\`, \`tailscale_route_check\`, \`collect_telemetry\`, \`notify\`, \`refresh_snapshot\`, and \`flush_outbox\`.
- Keep Omarchy, Hermes Relay, Needle, mobileLM, PocketStrike, and Excalibur Command Center outside this runtime.

---

## File structure

| File | Responsibility |
| --- | --- |
| \`kinetic_edge/camelot_edge/Cargo.toml\` | Audited Rust dependencies and release settings. |
| \`kinetic_edge/camelot_edge/src/lib.rs\` | Public error, action, and module boundary. |
| \`kinetic_edge/camelot_edge/src/protocol.rs\` | Canonical encoding plus Ed25519 signature verification. |
| \`kinetic_edge/camelot_edge/src/state.rs\` | SQLite snapshot, outbox, receipt, cap, TTL, and nonce persistence. |
| \`kinetic_edge/camelot_edge/src/client.rs\` | Standard-library, Tailscale-only HTTP client. |
| \`kinetic_edge/camelot_edge/src/main.rs\` | \`status\`, \`refresh\`, and \`flush-outbox\` commands; no listener. |
| \`control_plane/dispatch/edge_protocol.py\` | VPS device registry, snapshot issuer, request validator, replay cache. |
| \`control_plane/dispatch/vps_mobile_mesh_bridge.py\` | Explicit edge-route delegation and tailnet bind. |
| \`tests/test_edge_protocol.py\` | VPS signature, nonce, expiry, and action-scope tests. |
| \`tests/test_vps_mobile_mesh_bridge.py\` | HTTP boundary regression tests. |
| \`kinetic_edge/camelot_edge/termux/boot/start-camelot-edge\` | Non-secret Termux:Boot launcher. |
| \`docs/operations/android-edge-supervisor.md\` | Build, dry-run, enrollment, recovery, and size runbook. |

## Task 1: Define the Rust signed protocol contract

**Files:**
- Modify: \`kinetic_edge/camelot_edge/Cargo.toml\`
- Create: \`kinetic_edge/camelot_edge/src/lib.rs\`
- Create: \`kinetic_edge/camelot_edge/src/protocol.rs\`
- Modify: \`kinetic_edge/camelot_edge/src/main.rs\`
- Test: \`kinetic_edge/camelot_edge/tests/protocol_contract.rs\`

**Interfaces:**
- Produces: \`PolicySnapshot::verify_for\`, \`SignedEnvelope::sign\`, \`SignedEnvelope::verify\`, and \`Action::parse_allowlisted\`.

- [ ] **Step 1: Write failing tests**

\`\`\`rust
#[test]
fn rejects_snapshot_for_a_different_device() {
    let snapshot = signed_snapshot("other-device", 4_102_444_800);
    assert!(snapshot.verify_for("motorola-moto-g-power-5g---2024", 1_700_000_000).is_err());
}

#[test]
fn rejects_tampered_snapshot_signature() {
    let mut snapshot = signed_snapshot("motorola-moto-g-power-5g---2024", 4_102_444_800);
    snapshot.allowed_actions.push("shell".to_owned());
    assert!(snapshot.verify_for("motorola-moto-g-power-5g---2024", 1_700_000_000).is_err());
}

#[test]
fn rejects_action_outside_allowlist() {
    assert!(Action::parse_allowlisted("execute_shell").is_err());
}
\`\`\`

- [ ] **Step 2: Verify the red state**

Run: \`cargo test -p camelot-edge --test protocol_contract\`

Expected: FAIL because the library and protocol types do not exist.

- [ ] **Step 3: Implement the minimal contract**

Add:

\`\`\`toml
[dependencies]
base64 = "0.22"
ed25519-dalek = "2.2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
\`\`\`

Implement:

\`\`\`rust
pub fn verify_for(&self, device_id: &str, now_unix: i64) -> Result<(), EdgeError> {
    if self.device_id != device_id || self.expires_at <= now_unix {
        return Err(EdgeError::RejectedSnapshot);
    }
    self.verifying_key.verify_strict(&self.canonical_bytes(), &self.signature)?;
    Ok(())
}
\`\`\`

Use an explicit unsigned serializable struct for canonical bytes; never serialize the signature field into the bytes being verified.

- [ ] **Step 4: Verify green**

Run: \`cargo fmt --check -p camelot-edge; cargo test -p camelot-edge --test protocol_contract\`

Expected: PASS.

- [ ] **Step 5: Commit**

\`\`\`bash
git add kinetic_edge/camelot_edge/Cargo.toml kinetic_edge/camelot_edge/src/lib.rs kinetic_edge/camelot_edge/src/protocol.rs kinetic_edge/camelot_edge/src/main.rs kinetic_edge/camelot_edge/tests/protocol_contract.rs Cargo.lock
git commit -m "feat: add signed edge protocol contract"
\`\`\`

## Task 2: Add bounded local edge state

**Files:**
- Modify: \`kinetic_edge/camelot_edge/Cargo.toml\`
- Create: \`kinetic_edge/camelot_edge/src/state.rs\`
- Modify: \`kinetic_edge/camelot_edge/src/lib.rs\`
- Test: \`kinetic_edge/camelot_edge/tests/state_store.rs\`

**Interfaces:**
- Consumes: verified \`PolicySnapshot\`, \`SignedEnvelope\`, and \`Action\`.
- Produces: \`EdgeState::open\`, \`save_snapshot\`, \`enqueue\`, \`due_outbox\`, \`acknowledge\`, and \`purge_expired\`.

- [ ] **Step 1: Write failing tests**

\`\`\`rust
#[test]
fn retains_only_the_newest_two_telemetry_records_at_cap() {
    let state = EdgeState::open(temp_db(), OutboxLimits { max_records: 2, max_bytes: 512 }).unwrap();
    state.enqueue(telemetry("one"), 1_700_000_600).unwrap();
    state.enqueue(telemetry("two"), 1_700_000_600).unwrap();
    state.enqueue(telemetry("three"), 1_700_000_600).unwrap();
    assert_eq!(state.due_outbox(1_700_000_000).unwrap().len(), 2);
}

#[test]
fn rejects_duplicate_nonce_without_overwriting_the_original() {
    let state = EdgeState::open(temp_db(), OutboxLimits::test_defaults()).unwrap();
    state.enqueue(envelope("same-nonce"), 1_700_000_600).unwrap();
    assert!(state.enqueue(envelope("same-nonce"), 1_700_000_600).is_err());
}
\`\`\`

- [ ] **Step 2: Verify the red state**

Run: \`cargo test -p camelot-edge --test state_store\`

Expected: FAIL because \`EdgeState\` and \`OutboxLimits\` do not exist.

- [ ] **Step 3: Implement SQLite storage**

Add:

\`\`\`toml
[dependencies.rusqlite]
version = "0.40.1"
features = ["bundled"]
\`\`\`

Create a database schema with \`UNIQUE(nonce)\`; save only verified snapshots; purge expired records before use; evict only the oldest telemetry record under quota pressure.

\`\`\`rust
pub fn enqueue(&mut self, envelope: SignedEnvelope, expires_at: i64) -> Result<(), EdgeError> {
    self.purge_expired(now_unix())?;
    let tx = self.connection.transaction()?;
    tx.execute("INSERT INTO outbox (nonce, kind, payload, expires_at) VALUES (?1, ?2, ?3, ?4)", params![...])?;
    trim_telemetry_to_limits(&tx, self.limits)?;
    tx.commit()?;
    Ok(())
}
\`\`\`

- [ ] **Step 4: Verify green**

Run: \`cargo fmt --check -p camelot-edge; cargo test -p camelot-edge --test state_store\`

Expected: PASS.

- [ ] **Step 5: Commit**

\`\`\`bash
git add kinetic_edge/camelot_edge/Cargo.toml kinetic_edge/camelot_edge/src/lib.rs kinetic_edge/camelot_edge/src/state.rs kinetic_edge/camelot_edge/tests/state_store.rs Cargo.lock
git commit -m "feat: persist bounded edge state"
\`\`\`

## Task 3: Implement the VPS edge protocol adapter

**Files:**
- Create: \`control_plane/dispatch/edge_protocol.py\`
- Test: \`tests/test_edge_protocol.py\`

**Interfaces:**
- Produces: \`EdgeProtocol.issue_snapshot\`, \`validate_envelope\`, \`record_receipt\`, and \`accept_outbox\`.

- [ ] **Step 1: Write failing Python tests**

\`\`\`python
def test_valid_edge_envelope_is_accepted_once(edge_protocol, signed_envelope):
    assert edge_protocol.validate_envelope(signed_envelope, now=1_700_000_000).ok
    assert not edge_protocol.validate_envelope(signed_envelope, now=1_700_000_001).ok

def test_unregistered_device_key_is_rejected(edge_protocol, signed_envelope):
    signed_envelope["device_id"] = "unknown-device"
    assert edge_protocol.validate_envelope(signed_envelope, now=1_700_000_000).reason == "unregistered-device"
\`\`\`

- [ ] **Step 2: Verify the red state**

Run: \`.venv\\Scripts\\python.exe -m pytest tests/test_edge_protocol.py -q\`

Expected: FAIL because \`control_plane.dispatch.edge_protocol\` does not exist.

- [ ] **Step 3: Implement strict validation**

Use existing \`cryptography.hazmat.primitives.asymmetric.ed25519\`. Registry configuration contains public-key fingerprints only; enrollment supplies actual public-key bytes at runtime. Require device registration, valid timestamp, unused nonce, strict Ed25519 verification, and one of the six allowed action values.

\`\`\`python
def validate_envelope(self, envelope: Mapping[str, object], *, now: int) -> ValidationResult:
    device = self._devices.get(str(envelope.get("device_id", "")))
    if device is None:
        return ValidationResult(False, "unregistered-device")
    if not now < int(envelope["expires_at"]) or self._nonces.seen(device.id, str(envelope["nonce"])):
        return ValidationResult(False, "expired-or-replayed")
    device.public_key.verify(base64.b64decode(str(envelope["signature"])), canonical_envelope_bytes(envelope))
    return ValidationResult(True, "accepted")
\`\`\`

- [ ] **Step 4: Verify green**

Run: \`.venv\\Scripts\\python.exe -m pytest tests/test_edge_protocol.py -q\`

Expected: PASS.

- [ ] **Step 5: Commit**

\`\`\`bash
git add control_plane/dispatch/edge_protocol.py tests/test_edge_protocol.py
git commit -m "feat: add VPS edge protocol validator"
\`\`\`

## Task 4: Wire authenticated endpoints and native client commands

**Files:**
- Create: \`kinetic_edge/camelot_edge/src/client.rs\`
- Modify: \`kinetic_edge/camelot_edge/src/lib.rs\`
- Modify: \`kinetic_edge/camelot_edge/src/main.rs\`
- Modify: \`control_plane/dispatch/vps_mobile_mesh_bridge.py\`
- Modify: \`tests/test_vps_mobile_mesh_bridge.py\`
- Test: \`kinetic_edge/camelot_edge/tests/client_contract.rs\`

**Interfaces:**
- Consumes: \`EdgeProtocol\`, \`EdgeState\`, and \`SignedEnvelope\`.
- Produces: \`TailnetClient::fetch_snapshot\`, \`send_receipts\`, \`flush_outbox\`, plus bridge handlers for snapshot, receipts, and outbox.

- [ ] **Step 1: Write failing boundary tests**

\`\`\`python
def test_edge_endpoint_rejects_missing_signature_headers():
    response = request("GET", "/v1/edge/snapshot")
    assert response.status == 401

def test_authenticated_edge_endpoint_has_no_wildcard_cors_header(authenticated_request):
    response = authenticated_request("GET", "/v1/edge/snapshot")
    assert response.headers.get("Access-Control-Allow-Origin") is None
\`\`\`

\`\`\`rust
#[test]
fn refuses_a_non_tailnet_base_url() {
    assert!(TailnetClient::new("https://example.com:8095").is_err());
}
\`\`\`

- [ ] **Step 2: Verify the red state**

Run: \`.venv\\Scripts\\python.exe -m pytest tests/test_vps_mobile_mesh_bridge.py -q; cargo test -p camelot-edge --test client_contract\`

Expected: FAIL because edge routes and \`TailnetClient\` are absent.

- [ ] **Step 3: Implement the narrow endpoint family**

The client uses \`std::net::TcpStream\` and rejects hosts that are neither a \`100.*\` tailnet IP nor \`.ts.net\`. It signs every request. The Python bridge delegates only \`/v1/edge/snapshot\`, \`/v1/edge/receipts\`, and \`/v1/edge/outbox\`; these endpoints emit no wildcard CORS header. Their bind defaults to \`VPS_TAILSCALE_IP\` and has no wildcard fallback.

- [ ] **Step 4: Verify green**

Run: \`.venv\\Scripts\\python.exe -m pytest tests/test_edge_protocol.py tests/test_vps_mobile_mesh_bridge.py -q; cargo test -p camelot-edge --test protocol_contract --test state_store --test client_contract\`

Expected: PASS.

- [ ] **Step 5: Commit**

\`\`\`bash
git add kinetic_edge/camelot_edge/src/client.rs kinetic_edge/camelot_edge/src/lib.rs kinetic_edge/camelot_edge/src/main.rs kinetic_edge/camelot_edge/tests/client_contract.rs control_plane/dispatch/vps_mobile_mesh_bridge.py tests/test_vps_mobile_mesh_bridge.py Cargo.lock
git commit -m "feat: connect edge supervisor to Bifrost"
\`\`\`

## Task 5: Add Termux packaging and operational verification

**Files:**
- Create: \`kinetic_edge/camelot_edge/termux/boot/start-camelot-edge\`
- Create: \`docs/operations/android-edge-supervisor.md\`
- Modify: \`kinetic_edge/camelot_edge/src/main.rs\`
- Test: \`kinetic_edge/camelot_edge/tests/cli_contract.rs\`

**Interfaces:**
- Consumes: \`camelot-edge status\`, \`refresh\`, and \`flush-outbox\`.
- Produces: Termux:Boot launch behavior and a non-secret operator runbook.

- [ ] **Step 1: Write failing CLI tests**

\`\`\`rust
#[test]
fn status_command_does_not_open_a_listener() {
    let output = run_edge(&["status"]);
    assert!(output.status.success());
    assert!(String::from_utf8_lossy(&output.stdout).contains("listener=disabled"));
}

#[test]
fn unknown_command_fails_closed() {
    assert!(!run_edge(&["execute-shell"]).status.success());
}
\`\`\`

- [ ] **Step 2: Verify the red state**

Run: \`cargo test -p camelot-edge --test cli_contract\`

Expected: FAIL because the CLI commands are absent.

- [ ] **Step 3: Add the minimal launcher and runbook**

\`\`\`sh
#!/data/data/com.termux/files/usr/bin/sh
set -eu
exec "$HOME/.local/bin/camelot-edge" refresh --state-dir "$HOME/.camelot-edge"
\`\`\`

Document only explicit human steps: install Termux and Termux:Boot from one signing source, install the binary, place the launcher under \`~/.termux/boot/\`, opt out of battery optimization, generate/register the key outside the repository, and execute a dry run. Do not add auto-install, curl-pipe-shell, or auto-enrollment commands.

- [ ] **Step 4: Run complete checks**

Run: \`cargo fmt --check -p camelot-edge; cargo test -p camelot-edge; cargo build --release -p camelot-edge; .venv\\Scripts\\python.exe -m pytest tests/test_edge_protocol.py tests/test_vps_mobile_mesh_bridge.py -q\`

Expected: PASS. Record stripped ARM64 binary size only in the local enrollment receipt.

- [ ] **Step 5: Commit**

\`\`\`bash
git add kinetic_edge/camelot_edge/termux/boot/start-camelot-edge docs/operations/android-edge-supervisor.md kinetic_edge/camelot_edge/src/main.rs kinetic_edge/camelot_edge/tests/cli_contract.rs Cargo.lock
git commit -m "docs: add Termux edge supervisor runbook"
\`\`\`

## Plan self-review

- **Spec coverage:** Tasks 1–2 cover signature, allowed actions, SQLite state, TTL, and caps. Tasks 3–4 cover VPS registration, signed issuance, replay prevention, tailnet-only transport, and CORS isolation. Task 5 covers Termux:Boot, no-listener operation, size verification, and human enrollment.
- **Scope check:** Optional app pilots are intentionally excluded; each changes permissions and receives a separate design/approval cycle.
- **Completeness scan:** No incomplete or undefined implementation steps remain.
- **Type consistency:** Rust \`PolicySnapshot\`, \`SignedEnvelope\`, \`Action\`, \`EdgeState\`, and \`TailnetClient\` are defined before use. Python \`EdgeProtocol\` precedes bridge integration.
