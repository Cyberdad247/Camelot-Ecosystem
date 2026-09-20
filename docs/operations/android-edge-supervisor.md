# Android Edge Supervisor

`camelot-edge` is a native, no-listener Termux supervisor for the Motorola Moto G Power 5G (2024). It is limited to six signed actions: health probe, Tailnet route check, telemetry collection, notification, snapshot refresh, and outbox flush. It does not run an LLM, shell executor, ADB bridge, root helper, or public HTTP server.

## Enrollment boundary

1. Install Termux and Termux:Boot from the same verified signing source, then exclude both from Android battery optimization.
2. Build the ARM64 release binary on a trusted machine. Before copying it to the phone, strip it and record its size in the local enrollment receipt; it must not exceed 16 MB.
3. Generate the device Ed25519 key on the device. Register only its public key in the VPS runtime environment as `CAMELOT_EDGE_PUBLIC_KEYS_JSON`. Keep the private key and all runtime output outside this repository.
4. Generate the VPS snapshot-signing key in the VPS secret store as `CAMELOT_EDGE_SNAPSHOT_SIGNING_KEY_B64`; provision its public key into the phone's local trusted-signer configuration. Do not accept a signer key carried solely by a received snapshot.
5. Install `infra/systemd/camelot-edge-bus.service` on the VPS as a separate `camelot-edge-bus` service. It binds only the Tailnet IP on port 8096 and does not replace the legacy mesh bridge.
6. Set `CAMELOT_EDGE_HUB_URL` on the phone to the VPS Tailnet edge-bus URL, never to a public IP or DNS endpoint. Copy `kinetic_edge/camelot_edge/termux/boot/start-camelot-edge` to `~/.termux/boot/` and make it executable.

## Dry run and recovery

Run `camelot-edge status`; it must report `listener=disabled`. Then run `camelot-edge refresh --state-dir "$HOME/.camelot-edge"`. A successful staged run validates the state directory and Tailnet-only hub URL without opening a listener.

If a snapshot, signature, device registration, expiry, or nonce check fails, stop the supervisor, preserve the local SQLite file for inspection, rotate the affected runtime key, and re-enroll through the human-controlled VPS secret store. Never bypass the failure by substituting a mesh token, public endpoint, or unsigned snapshot.

Optional Omarchy Android, Hermes Relay, Needle, mobileLM, PocketStrike, and Excalibur Command Center remain outside this runtime and require separate permission review.
