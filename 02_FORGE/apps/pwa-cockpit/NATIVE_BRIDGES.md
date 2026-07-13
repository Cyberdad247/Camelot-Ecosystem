# Camelot Native Device Bridges

## Desktop

Path: `native/desktop-bridge`

```powershell
npm install
npm run build
cargo test --manifest-path src-tauri/Cargo.toml
npm run tauri dev
```

The Ed25519 private key is stored in the operating-system credential store. Copy the displayed public key into Device Hall, enroll it as `Desktop`, and enter the returned `dev-...` identifier in the companion.

Implemented capabilities: `system.status`, `desktop.notification`, and `desktop.window.focus`.

## Android and iOS

Path: `native/mobile-bridge`

```powershell
npm install
npm run sync
npm run android
```

Run `npm run ios` on macOS with Xcode. The mobile private key is a non-extractable WebCrypto key persisted in the application WebView. Copy only the public key into Device Hall.

Implemented capabilities: `system.status`, `mobile.haptic`, `mobile.notification`, and allowlisted `mobile.intent.open`.

## Protocol

Every poll and receipt includes device ID, timestamp, random nonce, body digest, and Ed25519 signature. The server rejects requests older than 60 seconds, replayed nonces, revoked devices, unknown capabilities, and unapproved actions. Hardware actions enter the delivery queue only after Iron Gate approval.
