# Camelot PWA Cockpit Architecture

Status: production candidate, 2026-07-11

## System Shape

```text
Mobile/Desktop PWA
  -> Cockpit shell: navigation, Anya presence, resource guard, session gate
  -> Trusted cartridge registry: Command | Factory | Intelligence | Mesh
  -> Same-origin control plane: session, status, events, stream, commands, approvals
  -> Server adapters: runtime files + TCP probes | durable store | Camelot CLI
  -> Camelot-OS: Cloud Brain | Bio-Kinetic Swarm | Bifrost services | ledgers
```

The browser never mounts remote executable UI. Each cartridge is a build-time trusted dynamic import with a declarative manifest, capability list, stable shell contract, and local error boundary. A failed cartridge can present recovery controls without taking down Anya, navigation, authentication, or the command boundary.

The production host binds Next.js to `127.0.0.1:3006`. A user-scoped Windows scheduled task keeps it alive, while Tailscale Serve terminates HTTPS and publishes only to the private tailnet. This preserves service-worker secure-context behavior without exposing the local control plane to the public internet.

## Runtime Layers

1. **Experience shell**: responsive desktop rail, mobile bottom navigation, Anya's voice-first presence, session pairing, offline/runtime indicators, and reduced-motion behavior.
2. **Cartridge layer**: four lazy micro-frontends registered in `src/cartridges/registry.tsx`. New cartridges must export the local cartridge contract and declare capabilities in `manifests.ts`.
3. **Control plane**: same-origin route handlers provide live status, event streaming, durable command receipts, and HITL approval transitions.
4. **Adapter layer**: runtime status reads canonical Camelot state and performs bounded TCP probes. Live runes use `execFile` against the canonical Camelot CLI with no shell interpolation.
5. **Sovereign runtime**: Cloud Brain, Bio-Kinetic Swarm, Bifrost, and ledgers remain owned by Camelot-OS. The Cockpit observes or invokes them through explicit adapters; it does not duplicate them.

## Trust Boundaries

- Production requires a `CAMELOT_COCKPIT_TOKEN`; loopback bypass is development-only.
- The operator token becomes an HttpOnly, SameSite Strict session cookie and is never exposed to client JavaScript.
- Cross-site pairing, command, approval, and session mutations are rejected.
- Every mutating runic directive enters Iron Gate. Approval creates a durable receipt before optional execution.
- Live command execution is off by default and requires `CAMELOT_COCKPIT_EXEC_ENABLED=true`.
- Enabled execution still requires an exact directive in `CAMELOT_COCKPIT_ALLOWED_RUNES`; approval alone cannot bypass that policy.
- The command adapter passes an argument array to `camelot.exe`; it never invokes a shell.
- Runtime and event APIs use `no-store`; the service worker excludes all `/api/*` traffic.
- The production process listens on loopback only; tailnet HTTPS is the remote ingress boundary.
- SSE connections use bounded 55-second leases, explicit retry guidance, and interval cleanup; browser reconnection preserves the event stream without leaking timers.

## Command Lifecycle

```text
operator intent
  -> authenticate and validate origin/content type
  -> classify read-only vs mutating rune
  -> mutating: create pending approval
  -> operator approves or rejects
  -> persist receipt and event
  -> execute only when the canonical adapter gate is enabled
```

`//STATUS` is the only current read-only rune and is resolved directly from the Cockpit runtime API, so it never touches the harness queue. Every other runic directive requires approval and an explicit execution allowlist entry. Unknown operator text is recorded as an intent receipt without being executed.

## Offline Contract

The service worker precaches the shell, icons, fallback page, and all trusted cartridge chunks after the initial authenticated mount. Its cache version is derived from the source tree during every production build, preventing stale cartridge bundles after a release. It uses same-origin cache strategies only and never caches privileged APIs. IndexedDB holds only a sanitized status snapshot: commands, events, approvals, and last-command data are excluded.

## Resource Envelope

The shell derives memory pressure from the host rather than synthetic telemetry. At high pressure it enters constrained mode, suppresses avatar video, reduces animation, and keeps command and approval controls available. User `prefers-reduced-motion` is honored independently.

## Anya Presence

Anya is voice-first, not voice-only. Browser speech recognition and synthesis have visible text controls and ready, listening, thinking, speaking, and unavailable phases. Spoken replies require an explicit user tap, prefer a configured or high-quality local English voice, remove receipt identifiers, compress operational responses, and support mic barge-in. `/anya.png` is the local fallback; a reviewed persistent video can be supplied through `NEXT_PUBLIC_ANYA_AVATAR_VIDEO_URL`. High-memory mode always falls back to the still image.

## Production Configuration

Copy the variable names from `.env.example` into the deployment secret store. Use a random operator token of at least 16 characters, keep execution disabled until the host command policy is reviewed, and serve remote sessions over HTTPS.

Verification gates:

```powershell
npm run verify
npm run host:install -- -SkipBuild
$env:PWA_COCKPIT_URL='http://localhost:3005'
$env:PWA_COCKPIT_TOKEN='<operator-token>'
& 'C:\Users\vizio\CAMELOT_OS\.venv\Scripts\python.exe' scripts\verify_ui.py
```

Release requires passing architecture tests, strict TypeScript, a production build, authenticated desktop/mobile browser checks, service-worker control, offline cartridge mounting, and a Bio-Kinetic preflight/release receipt.

`npm run host:remove` removes the scheduled task, stops the owned listener, and resets this node's Tailscale Serve route.
