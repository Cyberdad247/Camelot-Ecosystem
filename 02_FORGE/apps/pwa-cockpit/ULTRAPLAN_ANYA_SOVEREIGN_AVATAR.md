# ULTRAPLAN: Anya Sovereign Avatar

Plan rune: `rune-e838c39c`

## Product Rule

Anya is the persistent operating layer, not another cartridge. Her companion capsule mounts once in the Cockpit shell and remains available while cartridges change. The capsule is movable, dockable, collapsible, voice-aware, resource-aware, and explicit about the hardware capabilities available on the current device.

## Architecture

| Layer | Responsibility | Implementation |
| --- | --- | --- |
| Sovereign capsule | Full-body Arthurian identity, voice state, drag, dock, collapse, capability visibility | React, native Pointer Events, local transparent raster fallback |
| Motion cartridge | Optional gaze, expression, lip sync, body pose, and WebGPU/WebGL rendering | Dynamically imported `three` + [`@pixiv/three-vrm`](https://github.com/pixiv/three-vrm) |
| Perception worker | Optional local face, hand, and pose signals without sending camera frames to a server | [`MediaPipe Tasks`](https://github.com/google-ai-edge/mediapipe) in a worker |
| Browser broker | Microphone, camera, display capture, vibration, and Wake Lock under browser permission rules | Existing PWA interphase plus `device-capabilities.ts` |
| Desktop bridge | Windows/macOS/Linux automation, tray, filesystem, and approved local tools | [`Tauri`](https://github.com/tauri-apps/tauri) command allowlist |
| Mobile bridge | iOS/Android native permissions, haptics, notifications, Bluetooth, and app intents | [`Capacitor`](https://github.com/ionic-team/capacitor) plugins |
| Camelot control plane | Knight routing, policy, receipts, replay defense, and operator approval | Runic router, Iron Gate, signed approval grants |

## Device Control Contract

The PWA never receives arbitrary shell access. A device bridge advertises named capabilities such as `display.wake`, `haptic.confirm`, `camera.capture-local`, `desktop.window.focus`, or `mobile.intent.open`. Each request contains a device ID, capability ID, arguments, nonce, expiry, active cartridge, and operator-session proof.

Read-only actions may execute immediately when policy allows. Any action that changes files, launches applications, types text, controls another device, or crosses an account boundary must create an Iron Gate approval. Native bridges must reject unknown capabilities, expired requests, replayed nonces, and commands not bound to the current authenticated operator.

## Delivery Lanes

### Lane 1: shipped in this slice

- Replace the portrait crop with a local full-body Arthurian Anya.
- Keep Anya outside cartridge mounts so every cartridge shares one presence and voice state.
- Add pointer drag, viewport bounds, dock reset, expand/collapse, haptic pulse, and display Wake Lock.
- Show browser-available and native-gated capability states.
- Preserve static and reduced-motion paths under resource pressure.

### Lane 2: motion cartridge - runtime shipped

- The Cockpit lazy-loads Three.js and `@pixiv/three-vrm` only when `NEXT_PUBLIC_ANYA_VRM_URL` is configured and motion policy permits it.
- Rendering runs at poster, 30 fps reduced, or 60 fps full tiers with cleanup and deep disposal.
- Blink, gaze, `aa` viseme, idle shift, and speech state are wired to the VRM expression manager.
- The raster asset remains the offline, low-memory, reduced-motion, missing-model, and failed-model fallback.
- A licensed identity-matched VRM remains an external art deliverable; the model contract is in `public/models/README.md`.

### Lane 3: governed native bridges - shipped

- The Tauri desktop companion exposes only status, notification, and window-focus actions; its private key uses the OS credential store.
- Capacitor 8 Android and iOS projects expose status, haptics, notifications, and allowlisted app intents.
- Devices use per-device Ed25519 keys and never receive the recovery token.
- Device Hall provides enrollment, explicit grants, revocation, online state, action history, and Iron Gate delivery.

### Lane 4: local embodied intelligence - shipped

- MediaPipe perception runs in a worker and closes each transferred frame after inference.
- Only bounded gaze, blink, mouth, and presence signals return to the shell; no frame or biometric template enters storage.
- Spoken intent remains routed through Sir Helio and all hardware action risk remains under Sir Sentinel and Iron Gate.
- Motion automatically degrades through poster, reduced, and full tiers from device and resource policy.

## Performance Budgets

- Base capsule: no drag library and no 3D dependency in the initial route.
- Raster fallback: target under 1.5 MB and decode once per session.
- Motion chunk: lazy, separately cached, and absent from poster-only devices.
- VRM model: target under 6 MB after mesh, texture, and animation compression.
- Perception: worker-owned, frame-throttled, and disabled by default.
- Hardware bridge: zero ambient authority; capabilities are discovered and invoked individually.

## Acceptance Gates

- Anya remains visible and functional across every cartridge transition.
- Dragging cannot move the capsule outside the viewport; docking restores a predictable position.
- Mobile layouts retain access to navigation and command composition.
- Reduced-motion and resource-guard modes stop nonessential animation.
- No native action exists without a named capability, policy decision, and receipt.
- Desktop, iOS, and Android bridges use the same versioned action envelope.
