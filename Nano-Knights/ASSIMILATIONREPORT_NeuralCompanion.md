# 🛡️ ASSIMILATION REPORT
**Target:** `02_FORGE/KINETIC_ARMORY/NeuralCompanion` (pinned `37cb5f437`)
**Origin:** vendored 2026-08-15 (assimilation protocol)
**Tags:** ['neuralcompanion', 'avatar', 'experience']

## 📊 Summary
- **Vendored copy:** shallow HEAD clone, untracked (gitignored)
- **Stack:** Desktop companion app — avatar packs, body_configs, addons,
  MuseTalk talking-avatar, Windows installer (.bat)
- **Role in SADD:** Experience plane — optional persona/avatar surface (§9.2
  tenant avatar, e.g. "Lady Aaliyah"); NOT control plane

## 🔒 Secrets audit (2026-08-15, GHOST squire)
- GHOST's 2 CRITICAL `generic_token` flags are smoke-test placeholders in
  `addons/spotify_sense/smoke_spotify_sense.py` (`access_token="secret-access-token"`,
  `refresh_token="secret-refresh-token"`, `client_id="secret-client-id"`) —
  literal fixtures, not credentials.
- WARNINGs are large MuseTalk model assets (779–920 KB) and TODOs — not secrets.
- Real-format credential sweep: **zero matches**.

## 📝 Integration notes (inspected)
- Consumer-grade companion with its own addon economy (Discord/Patreon
  community, buy-me-a-coffee) — integrating it wholesale would import a
  distribution model that conflicts with the sovereign control-plane posture.
- No SADD service slot: it renders a persona, it does not route, authorize,
  verify, or transact. Treat as an optional Experience-node front-end.
- Lowest architectural fit of the assimilation batch; keep as reference only.
- No credentials handling observed in the top-level surface (local app).

---
**[SIR FORGE]:** "The context is siphoned."
