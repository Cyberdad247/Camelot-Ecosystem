# PWA Cockpit Validation

Validated: 2026-07-13

## Requirement Evidence

| Requirement | Current evidence | State |
| --- | --- | --- |
| Mastering UI/UX Cloud Brain guidance | Live NotebookLM notebook `Mastering Professional UI/UX` (`5ffaf13c-4db5-4619-9d6d-4bb1f660e91a`) was queried for voice, A2UI, HITL, accessibility, trust, and resource guidance. | PASS |
| Blueprint OS factory model | Factory cartridge implements the Assimilate, Forge, Validate, Release flow and identifies the Digital Creation Factory plan as provenance. | PASS |
| Antigravity PWA and Titan audit inputs | Runtime and layout decisions were checked against the PWA plan, metadata, full Titan audit, and current Camelot runtime evidence. | PASS |
| Jarvis-inspired Agent OS shell | Desktop rail, phase rail, thought trace, Iron Gate, resource guard, and Anya command presence render in one responsive shell. | PASS |
| Cartridge micro-frontends | Command, Factory, Forge Queue, Intelligence, Live Interphase, Device Hall, and Mesh mount from an explicit trusted dynamic-import catalog with declarative capability manifests, proactive cache prewarming, and a per-cartridge error boundary. | PASS |
| Kickbox + Mark XLVIII assimilation | The durable cross-architecture audit records adopted and rejected patterns. Live Interphase adds device/save-data/reduced-motion profiling, visible transport backoff, immediate interruption, transient-state reset, local visual capture, and a four-second duplicate-capture guard without importing vendor keys, unrestricted desktop actions, committed certificates, or unlicensed source. | PASS |
| Full-stack control plane | Session, status, events, reconnecting SSE, commands, and approvals are server routes backed by runtime probes and a durable local state store. | PASS |
| Governed execution | Mutating runes enter Iron Gate; live execution is shell-free, canonical-CLI-only, and constrained to `//CRYSTALLIZE` and `//EXECUTE_PROMPT`. Ordinary grants bind the approval and command digest; Forge v2 grants also bind the immutable cartridge digest and target root. Python verifies them, atomically rejects replay, and binds retained provenance to the generated queue task ID. `//STATUS` is resolved locally and never queues a harness task. | PASS |
| Forge Law R&D pipeline | A successful chained `forge_upgrade_verified` event automatically crystallizes the hashed source bundle into a deterministic cartridge. LUKAS accepts only typed, root-scoped operations with exact argv policies, atomic writes, receipts, and rollback. Markdown is never parsed as executable code, protected ledgers cannot be targeted, and service restart remains a separate disabled path. | PASS |
| Durable evidence recovery | UUID receipts, schema filtering, one-write approval transitions, fsync, backup rotation, corruption archival, and restart recovery were fault-injection tested against the live task. | PASS |
| Installable/offline PWA | Manifest, 192/512 icons, deterministic service-worker versioning, API cache exclusion, acknowledged cartridge prewarming, sanitized status-only IndexedDB fallback, and offline reload are verified. | PASS |
| Mobile delivery | Next binds to `127.0.0.1:3006`; `Camelot-PWA-Cockpit` runs as a user scheduled task; Tailscale Serve publishes private HTTPS at `https://cybertronia.tailcd0c29.ts.net/`. | PASS |
| Remote security | Passkeys are the primary operator authentication method with required user verification, one-time five-minute challenges, persisted authenticator counters, atomic local public-key storage, and explicit sign-out. The ignored 256-bit token is retained only for bootstrap/recovery. Successful authentication mints a unique HMAC-signed 12-hour HttpOnly/SameSite Strict/Secure session; cross-site mutations are rejected and the backend binds to loopback. | PASS |
| Bio-Kinetic verification | A fresh `camelot bio-swarm once --fixture --timeout 15 --json` release receipt reports `PASS`, one completed Formica task, zero failures, and a verified `swarm-spawner.exe` SHA-256. The earlier isolated PWA receipt remains available at `03_VAULT/runtime_state/pwa_cockpit_swarm_latest.json`. | PASS |
| Anya multimodal presence | Explicitly enabled speech replies, deterministic local voice preference, concise receipt-safe speech, visible speaking state, mic barge-in, voice input, text fallback, reduced motion, and resource-based animation suppression are implemented. | PASS |
| Persistent Anya identity | The bundled transparent full-body Arthurian render now drives a zero-cost local companion capsule with distinct idle, listening, thinking, and speaking motion. Reduced-motion and high-memory conditions fail closed to the static full-body asset. `NEXT_PUBLIC_ANYA_AVATAR_VIDEO_URL` remains an optional enhancement rather than a release dependency. | PASS |
| Explainable knight council | Anya ranks the five most qualified knights from live Cloud Brain, service, memory, freshness, execution-mode, voice, and swarm signals. Every recommendation exposes its reason, action, severity, and score; convening the council emits a bounded `//PLAN` command that remains subject to Iron Gate. | PASS |
| Sovereign avatar ULTRAPLAN | The shell-level Anya presence uses a full-body Arthurian asset, remains mounted across cartridge transitions, supports bounded pointer drag, docking and collapse, exposes browser hardware capabilities, and labels native device control as gated rather than claiming ambient PC or mobile authority. Camelot queued the implementation plan as `rune-e838c39c`. | PASS |
| Local embodied intelligence | An opt-in MediaPipe Face Landmarker worker loads local WASM and model assets, samples at no more than 10 fps, transfers rather than copies frames, closes every frame, returns only bounded animation signals, and stops camera tracks on disable. Same-origin camera permission is explicit. | PASS |
| Governed native device mesh | Device Hall enrolls Ed25519 public keys, grants platform-specific capabilities, queues every action behind Iron Gate, verifies timestamped signatures and body digests, rejects nonce replay, records results, and revokes devices. Tauri desktop and Capacitor Android/iOS companions implement the same signed poll and receipt contract. | PASS |
| Optional VRM motion runtime | The lazy Three.js and `three-vrm` chunk implements 30/60 fps tiers, VRM expressions, resize handling, WebGL cleanup, deep model disposal, and raster fallback. No unlicensed sample character is bundled; an identity-matched licensed VRM remains an external art asset. | PASS |

## Automated Gates

- `npm run verify`: 21 architecture tests passed, strict TypeScript passed, and the Next.js 16.2.10 production build passed with both Forge API routes.
- Camelot Forge and approval tests: 10 passed; the broader integration selection passed 14 tests. The only warning is the repository's existing unknown `cache_dir` pytest option.
- Authenticated Playwright verification over tailnet HTTPS:
  - desktop 1440x960: no console errors, no framework overlay, no horizontal overflow;
  - visible operator pairing form completed successfully;
  - Factory, Intelligence, and Mesh lazy cartridges mounted after Command;
  - mobile 390x844: no horizontal overflow and composer/navigation separation verified;
  - the mobile composer is in document flow and does not obscure telemetry;
  - a fresh browser that had opened only Command received a cache acknowledgement, went offline, and mounted Factory, Intelligence, and Mesh;
  - the offline trace used sanitized status and retained no commands, events, approvals, or last-command details.
  - a browser speech double verified the spoken status summary, speaking phase callbacks, native voice fallback, and immediate mic barge-in cancellation.
- Local production-build avatar verification:
  - desktop 1440x960 and mobile 390x844 rendered the local Anya pill with no console errors, framework overlay, or horizontal overflow;
  - the real 92% memory-pressure state disabled motion and reported `Resource guard active`;
  - a controlled 42% telemetry response enabled `avatar-presence` and reported `Ready at the edge` without changing production state.
- Isolated production passkey verification:
  - Chromium's virtual CTAP2 authenticator enrolled one user-verified resident credential against a disposable Camelot root;
  - sign-out removed the operator session and exposed passkey-first authentication with the recovery token collapsed;
  - passkey-only authentication restored the signed operator session with no console errors;
  - the disposable credential store and server were removed after verification, leaving the real cockpit ready for operator enrollment.
- Live Interphase browser verification:
  - desktop 1440x960 and mobile 390x844 mounted the fifth trusted cartridge with five stable mobile navigation targets;
  - both viewports had zero horizontal overflow, framework errors, or console errors;
  - controlled operator denial moved visual context to `blocked`, retained no preview, and wrote no local/session storage;
  - synthetic successful capture produced a volatile preview, stopped the display media track, wrote zero storage entries, and reconciled the real host memory guard to `poster-only`;
  - the fifth cartridge mounted offline after trusted prewarming with no console errors;
  - SSE transport reported live with zero reconnect attempts after authentication.
- Anya council browser verification:
  - mobile 390x844 rendered five live-ranked recommendations with no horizontal overflow or console errors;
  - the degraded host state selected Sir Debug, Sir Link, Sir Sentinel, Lady Mnemosyne, and Sir Boris in descending qualification order;
  - the convene action generated a bounded `//PLAN Anya council [...]` request; the browser test intercepted it before submission, so verification did not mutate the real approval queue.
- Sovereign avatar browser verification:
  - desktop 1440x960 decoded the local full-body asset, moved the capsule by its pointer handle, kept it inside viewport bounds, restored its dock, and collapsed it below 100 pixels high;
  - mobile 390x844 kept the expanded capsule inside the viewport with zero horizontal overflow, no framework overlay, and no console errors;
  - haptic and Wake Lock controls expose only browser-supported capabilities, while native control remains gated until a signed Tauri or Capacitor companion is explicitly enrolled.
- Local perception verification:
  - a fake browser camera initialized the local Face Landmarker worker without capturing a person;
  - the SIMD loader, 11 MB WASM binary, and 3.8 MB model each returned HTTP 200;
  - the worker reached `no-face`, emitted no console errors, and closed on operator disable;
  - controlled 42% memory telemetry enabled perception while the live high-memory runtime still fails closed.
- Device bridge protocol verification:
  - a disposable Ed25519 desktop identity enrolled with three explicit capabilities;
  - `system.status` entered Iron Gate as `act-2d7b09e4-a8c5-46e9-b280-72c25459b26f` and was approved as `appr-7b608d3e-af65-43f8-bb78-1bfaca25c9fb`;
  - signed poll and receipt completed the action, device revocation rejected the next signed poll with HTTP 401, and no shell command was accepted;
  - Device Hall rendered on desktop and mobile with seven cartridge targets, zero overflow, and zero console errors.
- Forge Law browser verification:
  - the authenticated production host rendered cartridge `forge-7f397ff17f18d2c6` with its digest, source, risk, two-step DAG, and validated state;
  - desktop and 390x844 mobile views had no framework overlay or browser errors;
  - mobile Anya and DAG geometry did not overlap after the companion moved into document flow;
  - a real execution request created an Iron Gate approval and rejection receipt without entering the LUKAS queue.
- Native companion gates:
  - Tauri frontend production build passed, Rust endpoint-policy test passed, and `tauri build --debug --no-bundle` produced `native/desktop-bridge/src-tauri/target/debug/nativedesktop-bridge.exe`;
  - Capacitor 8.4.1 and Vite 8.1.4 built a 15 KB JavaScript entry and synchronized both generated Android and iOS projects;
  - Android compilation remains unavailable until Java and the Android SDK are installed; iOS compilation and signing require macOS with Xcode.
- Dependency and tooling gates:
  - production `npm audit` reports zero vulnerabilities after constraining Next's nested PostCSS to 8.5.18;
  - both native project audits report zero vulnerabilities;
  - Vercel CLI 55.0.0 is installed globally.
- API transition check:
  - `//STATUS` produced a receipt without changing the 1,207-line harness queue;
  - an unknown rune created an Iron Gate approval and rejection receipt without changing the queue;
  - with the master execution switch temporarily enabled and the allowlist empty, an approved `//PLAN POLICY_BLOCK_TEST` produced `execution_blocked` and did not change the queue; execution was then restored to `false`;
  - cross-site command request returned HTTP 403.
- SSE rollover check: an authenticated browser observed two `ready` events across the intentional 55-second server lease and reconnected after the expected transport error.
- Recovery check: an injected malformed primary store was archived, the backup restored, the recovery event surfaced, and both primary and backup parsed after the next receipt. The injected fixture was removed afterward.

## Live Runtime Caveats

The Cockpit currently reports `degraded` because the host is under high memory pressure and Cloud Brain has two queued sync events. Those are truthful Camelot runtime conditions, not fabricated telemetry or a Cockpit build failure. Live command execution is enabled only for `//CRYSTALLIZE` and `//EXECUTE_PROMPT`; all other mutating runes remain outside the adapter allowlist.

Browser pairing and Python factory-lane `HUMAN_GATE` authorization remain separate trust boundaries. The PWA runic path no longer treats `CAMELOT_DASHBOARD_OPERATOR_TOKEN` presence as proof of approval: it uses a signed, expiring, single-use grant bound to the approval, exact command, and generated queue task. Factory-lane jobs continue to use their existing suspension and resume protocol.

## Optional Identity Enhancement

An identity-matched licensed VRM can be supplied through `NEXT_PUBLIC_ANYA_VRM_URL`, or an externally rendered video through `NEXT_PUBLIC_ANYA_AVATAR_VIDEO_URL`. The production PWA does not require either remote media or a paid avatar service: its local Arthurian full-body raster remains the offline, low-resource, reduced-motion, and failed-model fallback.
