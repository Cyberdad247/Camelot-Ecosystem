# CLARITY_CORE Duplicate Content Report — Full-Content SHA-256
**Generated:** 2026-09-23 21:42 UTC
**Root:** `C:\Users\vizio\CAMELOT_OS`

---

## Summary

| Metric | Value |
|--------|-------|
| SWEEP header-hash candidates | 2,215 |
| Verified true duplicates | 249 |
| Prefix-only false positives | 1,966 |
| Ground-truth duplicate groups (full SHA-256) | 251 |
| Files involved in true duplication | 521 |
| Redundant files (removable copies) | 270 |
| Redundant bytes reclaimable | 5.1 MB |
| True dupes SWEEP missed (binary / sub-64B) | 42 files |

Method: SWEEP candidates use an identical-first-128-bytes heuristic; the
verification pass compares full-content SHA-256 (computed by the SCAN squire
for every file ≤ 2 MB). A candidate counts as a true duplicate only if its
full hash equals its header-owner's hash. Ground-truth groups additionally
cover binary files, which SWEEP's header pass skips.

## Verified duplicate groups (full-content SHA-256)

Sorted by wasted bytes (descending). Every file in a group is
byte-identical; all but one are removable.

### Group 1 — `f88b2245239c` · 4 files · 1.0 MB each · 3.0 MB wasted

- `03_VAULT/PROVENANCE_LEDGER.md`
- `03_VAULT/training/configs/PROVENANCE_LEDGER.md`
- `PROVENANCE_LEDGER.md`
- `docs/PROVENANCE_LEDGER.md`

### Group 2 — `d346c37d1f41` · 2 files · 992.6 KB each · 992.6 KB wasted

- `03_VAULT/knowledge_vault/PROVENANCE_LEDGER.md`
- `docs/architecture/PROVENANCE_LEDGER.md`

### Group 3 — `899772ac50a4` · 2 files · 222.6 KB each · 222.6 KB wasted

- `01_KERNEL/memory/NOTEBOOK_MANIFEST.json`
- `03_VAULT/runtime_state/NOTEBOOK_MANIFEST.json`

### Group 4 — `7f7351d9d285` · 2 files · 50.0 KB each · 50.0 KB wasted

- `03_VAULT/training/configs/knight_character_sheets.yaml`
- `vfs/roster.yaml`

### Group 5 — `28339ab9868e` · 2 files · 40.2 KB each · 40.2 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/sources.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/sources.py`

### Group 6 — `917604833ee2` · 3 files · 16.8 KB each · 33.6 KB wasted

- `docs/architecture/CAMELOT_OS_V1000_APEX_NORTHSTAR.md`
- `vfs/CAMELOT_OS_V1000_APEX_NORTHSTAR.md`
- `vfs/living_camelot_v1000_system_instruction.md`

### Group 7 — `63bb2615ff4e` · 2 files · 25.6 KB each · 25.6 KB wasted

- `01_KERNEL/forge/nano_forge/extension/_locales/zh_TW/messages.json`
- `03_VAULT/Nano-Knights/_locales/zh_TW/messages.json`

### Group 8 — `2807c4d4920c` · 2 files · 25.0 KB each · 25.0 KB wasted

- `01_KERNEL/forge/nano_forge/extension/_locales/en/messages.json`
- `03_VAULT/Nano-Knights/_locales/en/messages.json`

### Group 9 — `c24d5ccc9e2f` · 2 files · 19.6 KB each · 19.6 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/client.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/client.py`

### Group 10 — `70e60624b73c` · 2 files · 17.8 KB each · 17.8 KB wasted

- `03_VAULT/runtime_state/excalibur_cicd_log.md`
- `docs/architecture/EXCALIBUR_CICD_LOG.md`

### Group 11 — `f7a974ff0139` · 4 files · 5.8 KB each · 17.5 KB wasted

- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_172005/components_3d_MorganaAvatar.tsx`
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_180343/MorganaAvatar.tsx`
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_183443/MorganaAvatar.tsx`
- `02_FORGE/PORTAL_CORE/Modal/morgana/components/3d/MorganaAvatar.tsx`

### Group 12 — `130cef9eecce` · 2 files · 16.4 KB each · 16.4 KB wasted

- `03_VAULT/knowledge_vault/03_CAMELOT_STATE_PLANS/verification.md`
- `vfs/knowledge/state_verification.md`

### Group 13 — `9ae399177751` · 2 files · 14.6 KB each · 14.6 KB wasted

- `03_VAULT/runtime_state/system_triage/latest.json`
- `03_VAULT/runtime_state/system_triage/triage_20260621T075705Z.json`

### Group 14 — `0d316447c6c0` · 2 files · 14.5 KB each · 14.5 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/models.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/models.py`

### Group 15 — `bbef1b9eb002` · 2 files · 13.4 KB each · 13.4 KB wasted

- `control_plane/bifrost_triage_swarm.py`
- `control_plane/dispatch/bifrost_triage_swarm.py`

### Group 16 — `cc41b1df385d` · 2 files · 13.2 KB each · 13.2 KB wasted

- `03_VAULT/knowledge_vault/03_CAMELOT_STATE_PLANS/tasks.md`
- `vfs/knowledge/state_tasks.md`

### Group 17 — `9ce4549f1c8d` · 2 files · 11.2 KB each · 11.2 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/models.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/models.py`

### Group 18 — `9e0650fac326` · 2 files · 10.9 KB each · 10.9 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/sources_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/sources_service.py`

### Group 19 — `d6b49130ddca` · 2 files · 10.2 KB each · 10.2 KB wasted

- `03_VAULT/runtime_state/open_notebook/knowledge_vault_index.json`
- `vfs/knowledge/vault_manifest.json`

### Group 20 — `30509a606671` · 2 files · 9.8 KB each · 9.8 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/notebooks.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/notebooks.py`

### Group 21 — `e48e4cafa4cd` · 2 files · 9.5 KB each · 9.5 KB wasted

- `docs/SEPTEM_REGNA/L7_ETHEREAL/entiremap.md`
- `docs/architecture/entiremap.md`

### Group 22 — `34ca92132054` · 2 files · 9.3 KB each · 9.3 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/transformations.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/transformations.py`

### Group 23 — `5d05973055c1` · 2 files · 9.3 KB each · 9.3 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/episode_profiles.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/episode_profiles.py`

### Group 24 — `b576a1f28d77` · 2 files · 9.2 KB each · 9.2 KB wasted

- `01_KERNEL/senses/integrations/README_HAYSTACK_UKG.md`
- `docs/reference/INTEGRATIONS/README_HAYSTACK_UKG.md`

### Group 25 — `95d4381409e4` · 2 files · 9.1 KB each · 9.1 KB wasted

- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_v94_fastapi.py`
- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_v94_remote.py`

### Group 26 — `77dbd5b02515` · 2 files · 8.6 KB each · 8.6 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/search.py`

### Group 27 — `0af263d98736` · 2 files · 8.5 KB each · 8.5 KB wasted

- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_180343/morgana_core.py`
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_183443/morgana_core.py`

### Group 28 — `7c057fc6d250` · 2 files · 8.2 KB each · 8.2 KB wasted

- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/shape/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/shape/SKILL.md`

### Group 29 — `abeaa7b2ba32` · 2 files · 8.2 KB each · 8.2 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/podcasts.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/podcasts.py`

### Group 30 — `9b4893de6cbd` · 2 files · 7.9 KB each · 7.9 KB wasted

- `02_FORGE/kinetic/vizio-router/cmd/pulse/heartbeat.go`
- `cmd/pulse/heartbeat.go`

### Group 31 — `28d9a131f4e5` · 2 files · 7.7 KB each · 7.7 KB wasted

- `01_KERNEL/memory/hybrid_worldtree_architecture.py`
- `vfs/hybrid_worldtree_architecture.py`

### Group 32 — `c81a7bb45b24` · 2 files · 7.6 KB each · 7.6 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/podcast_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/podcast_service.py`

### Group 33 — `73c42ca319f5` · 2 files · 7.5 KB each · 7.5 KB wasted

- `02_FORGE/PORTAL_CORE/components/ui/GlassOverlay.tsx`
- `02_FORGE/PORTAL_CORE/web/components/ui/GlassOverlay.tsx`

### Group 34 — `c3d8f692d725` · 2 files · 7.5 KB each · 7.5 KB wasted

- `03_VAULT/knowledge_vault/03_CAMELOT_STATE_PLANS/blueprint.md`
- `vfs/knowledge/state_blueprint.md`

### Group 35 — `e7a793322a18` · 2 files · 7.4 KB each · 7.4 KB wasted

- `control_plane/graphify.py`
- `control_plane/infra/graphify.py`

### Group 36 — `6a75cc172159` · 2 files · 7.3 KB each · 7.3 KB wasted

- `02_FORGE/kinetic/vizio-router/cmd/pulse/ops/BARE-METAL-DEPLOY.md`
- `cmd/pulse/ops/BARE-METAL-DEPLOY.md`

### Group 37 — `df4ba2138d68` · 2 files · 7.3 KB each · 7.3 KB wasted

- `02_FORGE/tools/pi-mono/packages/agent/src/harness/utils/truncate.ts`
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/core/tools/truncate.ts`

### Group 38 — `3a48b0089c6f` · 2 files · 7.0 KB each · 7.0 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/embedding_rebuild.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/embedding_rebuild.py`

### Group 39 — `aebc99f14299` · 2 files · 6.8 KB each · 6.8 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/speaker_profiles.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/speaker_profiles.py`

### Group 40 — `85aca7edb501` · 2 files · 6.8 KB each · 6.8 KB wasted

- `01_KERNEL/EXCALIBUR/system/forge_v2.py`
- `01_KERNEL/forge/forge_v2.py`

### Group 41 — `7c3fc1a039ea` · 2 files · 6.5 KB each · 6.5 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/notes.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/notes.py`

### Group 42 — `c19f75d50453` · 2 files · 6.3 KB each · 6.3 KB wasted

- `control_plane/infra/memcastle.py`
- `control_plane/memcastle.py`

### Group 43 — `823a417bfb17` · 2 files · 6.0 KB each · 6.0 KB wasted

- `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/Master_Compendium.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/Master_Compendium.md`

### Group 44 — `29e4d07b6b52` · 2 files · 5.6 KB each · 5.6 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/chat_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/chat_service.py`

### Group 45 — `fab50399ee92` · 2 files · 5.6 KB each · 5.6 KB wasted

- `01_KERNEL/protocols/ukg_integration_v206.md`
- `docs/protocols/ukg_integration_v206.md`

### Group 46 — `cd42cfbcbcae` · 2 files · 5.4 KB each · 5.4 KB wasted

- `02_FORGE/PORTAL_CORE/components/ui/KnightSprites.tsx`
- `02_FORGE/PORTAL_CORE/web/components/ui/KnightSprites.tsx`

### Group 47 — `c1c03f965141` · 2 files · 5.2 KB each · 5.2 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/config.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/config.py`

### Group 48 — `5e80fcf64c85` · 2 files · 5.1 KB each · 5.1 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/commands.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/commands.py`

### Group 49 — `b573148d5dee` · 2 files · 5.1 KB each · 5.1 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/transformations_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/transformations_service.py`

### Group 50 — `8f185a339fcc` · 2 files · 5.1 KB each · 5.1 KB wasted

- `02_FORGE/kinetic/vizio-router/cmd/pulse/ops/camelotd.sh`
- `cmd/pulse/ops/camelotd.sh`

### Group 51 — `8d73414f4e12` · 2 files · 5.0 KB each · 5.0 KB wasted

- `docs/SEPTEM_REGNA/L7_ETHEREAL/EXCALIBUR_ENTIREMAP.md`
- `docs/architecture/EXCALIBUR_ENTIREMAP.md`

### Group 52 — `cebdf93f4f98` · 2 files · 5.0 KB each · 5.0 KB wasted

- `02_FORGE/apps/lux11/src/voice/omnivoice-router.ts`
- `deploy/multivoice-router/src/voice/omnivoice-router.ts`

### Group 53 — `97371bc2f654` · 2 files · 5.0 KB each · 5.0 KB wasted

- `control_plane/infra/memcastle_sync.py`
- `control_plane/memcastle_sync.py`

### Group 54 — `007892568b72` · 2 files · 4.9 KB each · 4.9 KB wasted

- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/to-issues/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/to-issues/SKILL.md`

### Group 55 — `c9fd5564393e` · 2 files · 4.8 KB each · 4.8 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/context.py`

### Group 56 — `cae5644208ea` · 2 files · 4.7 KB each · 4.7 KB wasted

- `control_plane/dispatch/knight_engine_router.py`
- `vfs/knowledge/knight_engine_router.py`

### Group 57 — `6409ca716c33` · 2 files · 4.5 KB each · 4.5 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/podcast_api_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/podcast_api_service.py`

### Group 58 — `10c3baa59380` · 2 files · 4.4 KB each · 4.4 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/models_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/models_service.py`

### Group 59 — `83c086d141b2` · 2 files · 4.3 KB each · 4.3 KB wasted

- `01_KERNEL/EXCALIBUR/system/watchtower.py`
- `01_KERNEL/iron_gate/watchtower.py`

### Group 60 — `77bc6c3ab70a` · 2 files · 4.3 KB each · 4.3 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/episode_profiles_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/episode_profiles_service.py`

### Group 61 — `f430f55a67b9` · 2 files · 4.1 KB each · 4.1 KB wasted

- `02_FORGE/PORTAL_CORE/components/scene/ThroneRoom.tsx`
- `02_FORGE/PORTAL_CORE/web/components/scene/ThroneRoom.tsx`

### Group 62 — `099cca79c616` · 2 files · 3.9 KB each · 3.9 KB wasted

- `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/scaling_architecture.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/scaling_architecture.md`

### Group 63 — `ced49798a0f0` · 2 files · 3.9 KB each · 3.9 KB wasted

- `02_FORGE/apps/lux11/src/voice/multivoice-session.ts`
- `deploy/multivoice-router/src/voice/multivoice-session.ts`

### Group 64 — `62ee3cd362df` · 2 files · 3.7 KB each · 3.7 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/embedding.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/embedding.py`

### Group 65 — `1bdda93d40ec` · 2 files · 3.7 KB each · 3.7 KB wasted

- `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/prompt_frameworks.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/prompt_frameworks.md`

### Group 66 — `ac56fd16c6f0` · 3 files · 1.8 KB each · 3.7 KB wasted

- `03_VAULT/knowledge_vault/01_ARCHITECTURE_AND_PROTOCOLS/[⨹ SYMBOLECT PRIMER 14da3c2b2603813a828fdacd742db09b.md`
- `vfs/knowledge/SYMBOLECT_PRIMER.md`
- `vfs/knowledge/[⨹_SYMBOLECT_PRIMER_14da3c2b2603813a828fdacd742db09b.md`

### Group 67 — `b022aab0455c` · 2 files · 3.7 KB each · 3.7 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/command_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/command_service.py`

### Group 68 — `2d94f87076f3` · 2 files · 3.7 KB each · 3.7 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/settings.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/settings.py`

### Group 69 — `9017e6b459af` · 2 files · 3.6 KB each · 3.6 KB wasted

- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/to-prd/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/to-prd/SKILL.md`

### Group 70 — `1c6fce0c7744` · 2 files · 3.5 KB each · 3.5 KB wasted

- `01_KERNEL/protocols/paladin_htn_protocol.md`
- `docs/protocols/paladin_htn_protocol.md`

### Group 71 — `85ac7ce02aad` · 2 files · 3.5 KB each · 3.5 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/insights_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/insights_service.py`

### Group 72 — `b27c6109ff8c` · 2 files · 3.4 KB each · 3.4 KB wasted

- `01_KERNEL/protocols/assimilation_v4_omega.md`
- `docs/protocols/assimilation_v4_omega.md`

### Group 73 — `e86077754352` · 2 files · 3.4 KB each · 3.4 KB wasted

- `01_KERNEL/protocols/assimilation_v5_evolution.md`
- `docs/protocols/assimilation_v5_evolution.md`

### Group 74 — `ed24a06dee55` · 2 files · 3.4 KB each · 3.4 KB wasted

- `02_FORGE/PORTAL_CORE/web/hooks/use-socket.ts`
- `02_FORGE/hooks/use-socket.ts`

### Group 75 — `3ce7e259e6af` · 2 files · 3.4 KB each · 3.4 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/auth.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/auth.py`

### Group 76 — `e3168a68f7ee` · 2 files · 3.2 KB each · 3.2 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/notes_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/notes_service.py`

### Group 77 — `1e0f713f9056` · 2 files · 3.1 KB each · 3.1 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/notebook_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/notebook_service.py`

### Group 78 — `e11d196304f8` · 2 files · 3.1 KB each · 3.1 KB wasted

- `02_FORGE/cartridges/motorola_edge_hub_cartridge.json`
- `apps/camelot-vps-hub/cartridges/motorola-edge-cartridge-v1.json`

### Group 79 — `063821310957` · 2 files · 3.0 KB each · 3.0 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/insights.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/insights.py`

### Group 80 — `6c214be82a2e` · 2 files · 3.0 KB each · 3.0 KB wasted

- `01_KERNEL/EXCALIBUR/system/culture_bias.py`
- `01_KERNEL/forge/scripts/culture_bias.py`

### Group 81 — `ad0959ecb620` · 2 files · 3.0 KB each · 3.0 KB wasted

- `03_VAULT/runtime_state/cartridges/vps-hub-cartridge-v1.json`
- `apps/camelot-vps-hub/cartridges/vps-hub-cartridge-v1.json`

### Group 82 — `2bc0c5d97a04` · 2 files · 3.0 KB each · 3.0 KB wasted

- `control_plane/dispatch/excalibur_voice_gateway.py`
- `vfs/knowledge/excalibur_voice_gateway.py`

### Group 83 — `e3b14d009ba7` · 2 files · 2.9 KB each · 2.9 KB wasted

- `01_KERNEL/docs/CAMELOT_BIBLE.md`
- `docs/CAMELOT_BIBLE.md`

### Group 84 — `ef529128bc81` · 2 files · 2.9 KB each · 2.9 KB wasted

- `01_KERNEL/protocols/iron_gate_protocol.md`
- `docs/protocols/iron_gate_protocol.md`

### Group 85 — `7903a8d8fca1` · 2 files · 2.8 KB each · 2.8 KB wasted

- `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/skillgraph5.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/skillgraph5.md`

### Group 86 — `57e3f4d16de2` · 2 files · 2.8 KB each · 2.8 KB wasted

- `01_KERNEL/protocols/xp_economy_protocol.md`
- `docs/protocols/xp_economy_protocol.md`

### Group 87 — `fa06b738382f` · 2 files · 2.7 KB each · 2.7 KB wasted

- `02_FORGE/kinetic/vizio-router/src/router/schema.ts`
- `src/router/schema.ts`

### Group 88 — `41bc6e9b4e47` · 2 files · 2.7 KB each · 2.7 KB wasted

- `01_KERNEL/protocols/squire_protocol.md`
- `docs/protocols/squire_protocol.md`

### Group 89 — `b0df54514333` · 2 files · 2.7 KB each · 2.7 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/settings_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/settings_service.py`

### Group 90 — `c0ec401f2283` · 2 files · 2.7 KB each · 2.7 KB wasted

- `vfs/fitness/Master_Compendium.md`
- `vfs/fitness/Master_Compendium_Fitness.md`

### Group 91 — `cb93a2f7bc55` · 2 files · 2.7 KB each · 2.7 KB wasted

- `02_FORGE/apps/lux11/src/voice/voice-profile-registry.ts`
- `deploy/multivoice-router/src/voice/voice-profile-registry.ts`

### Group 92 — `c5728d8685ab` · 2 files · 2.6 KB each · 2.6 KB wasted

- `vfs/edu/Master_Compendium.md`
- `vfs/edu/Master_Compendium_Edu.md`

### Group 93 — `cacdecd20f18` · 2 files · 2.6 KB each · 2.6 KB wasted

- `vfs/general/Master_Compendium.md`
- `vfs/general/Master_Compendium_General.md`

### Group 94 — `13e75c19c104` · 2 files · 2.6 KB each · 2.6 KB wasted

- `vfs/business/Master_Compendium.md`
- `vfs/business/Master_Compendium_Business.md`

### Group 95 — `c5f5547d7493` · 2 files · 2.4 KB each · 2.4 KB wasted

- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/AGENTS.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/CLAUDE.md`

### Group 96 — `e40373b9945a` · 2 files · 2.2 KB each · 2.2 KB wasted

- `01_KERNEL/docs/PHASE_9_ETHEREAL_RESONANCE.md`
- `docs/reference/MANIFESTS/PHASE_9_ETHEREAL_RESONANCE.md`

### Group 97 — `d27a69d5e955` · 2 files · 2.1 KB each · 2.1 KB wasted

- `01_KERNEL/protocols/hive_forge_v1.md`
- `docs/protocols/hive_forge_v1.md`

### Group 98 — `59d6e137bad1` · 2 files · 2.1 KB each · 2.1 KB wasted

- `03_VAULT/runtime_state/system_triage/latest.md`
- `03_VAULT/runtime_state/system_triage/triage_20260621T075705Z.md`

### Group 99 — `069c0476923e` · 2 files · 2.1 KB each · 2.1 KB wasted

- `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/Master_Compendium.md`
- `vfs/notebooks/b4cfc5af-1555-4f23-a131-1ec6d03c2787/Master_Compendium.md`

### Group 100 — `a0a63f602073` · 2 files · 2.0 KB each · 2.0 KB wasted

- `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/Master_Compendium.md`
- `vfs/notebooks/3a09997b-3d65-46c9-b9aa-fb8ebce927a9/Master_Compendium.md`

### Group 101 — `fae1e633ea08` · 2 files · 2.0 KB each · 2.0 KB wasted

- `03_VAULT/UKG/nodes/VKG_CAM_LADY_MNEMOSYNE_SOVEREIGN_NAVIGAT_20260917.json`
- `03_VAULT/runtime_state/open_notebook/vkg_crystals/VKG_CAM_LADY_MNEMOSYNE_SOVEREIGN_NAVIGAT_20260917.json`

### Group 102 — `231654ecac02` · 2 files · 2.0 KB each · 2.0 KB wasted

- `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/Master_Compendium.md`
- `vfs/notebooks/f6466e10-d1b1-4904-9f87-081d031b0595/Master_Compendium.md`

### Group 103 — `c2813772a321` · 2 files · 2.0 KB each · 2.0 KB wasted

- `vfs/notebooks/28d49148-28db-438d-a299-61456fdfdefc/Master_Compendium.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/Master_Compendium.md`

### Group 104 — `edc09fbb123d` · 2 files · 2.0 KB each · 2.0 KB wasted

- `vfs/notebooks/da2e51db-780a-48cf-a40a-4f0f65ff9295/Master_Compendium.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/Master_Compendium.md`

### Group 105 — `981c84e8d73e` · 2 files · 2.0 KB each · 2.0 KB wasted

- `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/Master_Compendium.md`
- `vfs/notebooks/96f9233b-6efa-46a3-8242-98f0c463680c/Master_Compendium.md`

### Group 106 — `7476e67779e6` · 2 files · 2.0 KB each · 2.0 KB wasted

- `vfs/notebooks/e9fcbbbc-cd43-4b2d-a437-b2570267a0a9/Master_Compendium.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/Master_Compendium.md`

### Group 107 — `2943b2511704` · 2 files · 2.0 KB each · 2.0 KB wasted

- `03_VAULT/LEGAL/CONSTITUTION.md`
- `docs/protocols/LAWS/CONSTITUTION.md`

### Group 108 — `ff9837dc0243` · 2 files · 1.9 KB each · 1.9 KB wasted

- `01_KERNEL/protocols/persona_evolution_protocol.md`
- `docs/protocols/persona_evolution_protocol.md`

### Group 109 — `6e4d0b52d73c` · 2 files · 1.9 KB each · 1.9 KB wasted

- `02_FORGE/PORTAL_CORE/components/scene/RoundTable.tsx`
- `02_FORGE/PORTAL_CORE/web/components/scene/RoundTable.tsx`

### Group 110 — `d7ec719d5a30` · 2 files · 1.9 KB each · 1.9 KB wasted

- `03_VAULT/runtime_state/backups/hiveide_cut_20260625T173845Z/node_mcp_cutlist.json`
- `03_VAULT/runtime_state/node_mcp_cutlist.json`

### Group 111 — `5be723e1f1bc` · 2 files · 1.9 KB each · 1.9 KB wasted

- `01_KERNEL/docs/PHASE_8_KINETIC_ASCENSION.md`
- `docs/reference/MANIFESTS/PHASE_8_KINETIC_ASCENSION.md`

### Group 112 — `13544016a8a0` · 2 files · 1.9 KB each · 1.9 KB wasted

- `01_KERNEL/protocols/merlin_identity_forge.md`
- `docs/protocols/merlin_identity_forge.md`

### Group 113 — `624076f3931a` · 3 files · 937 B each · 1.8 KB wasted

- `01_KERNEL/agora/persona/ukg_persona_schema.json`
- `03_VAULT/UKG/SCHEMAS/ukg_persona_schema.json`
- `docs/protocols/PERSONA/ukg_persona_schema.json`

### Group 114 — `c742122b7ee2` · 2 files · 1.7 KB each · 1.7 KB wasted

- `01_KERNEL/protocols/assimilation_v2.md`
- `docs/protocols/assimilation_v2.md`

### Group 115 — `d330c4f581fe` · 2 files · 1.6 KB each · 1.6 KB wasted

- `01_KERNEL/protocols/assimilation_v3.md`
- `docs/protocols/assimilation_v3.md`

### Group 116 — `f514831505b2` · 2 files · 1.6 KB each · 1.6 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/search_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/search_service.py`

### Group 117 — `cbc8520ca6cc` · 2 files · 1.6 KB each · 1.6 KB wasted

- `01_KERNEL/protocols/lukas_architect.md`
- `docs/protocols/lukas_architect.md`

### Group 118 — `59b750fa40a8` · 2 files · 1.6 KB each · 1.6 KB wasted

- `01_KERNEL/docs/CAMELOT_TRIAD_INTEGRATION.md`
- `docs/reference/MANIFESTS/CAMELOT_TRIAD_INTEGRATION.md`

### Group 119 — `484ca31745d2` · 2 files · 1.6 KB each · 1.6 KB wasted

- `01_KERNEL/docs/AUDIT_REPORT_20260131.md`
- `docs/reference/MANIFESTS/AUDIT_REPORT_20260131.md`

### Group 120 — `0689bbe09bf2` · 2 files · 1.5 KB each · 1.5 KB wasted

- `01_KERNEL/docs/AUDIT_REPORT_20260131_2215.md`
- `docs/reference/MANIFESTS/AUDIT_REPORT_20260131_2215.md`

### Group 121 — `309147495d08` · 2 files · 1.5 KB each · 1.5 KB wasted

- `02_FORGE/ARCHITECTURE.md`
- `docs/architecture/ARCH/FORGE_ARCHITECTURE.md`

### Group 122 — `6c6b4add3c89` · 2 files · 1.5 KB each · 1.5 KB wasted

- `03_VAULT/UKG/nodes/VKG_CAM_BIFROST_MESH_AND_EXCALIBUR_COMMA_20260914.json`
- `03_VAULT/runtime_state/open_notebook/vkg_crystals/VKG_CAM_BIFROST_MESH_AND_EXCALIBUR_COMMA_20260914.json`

### Group 123 — `4fb47432abee` · 2 files · 1.5 KB each · 1.5 KB wasted

- `03_VAULT/runtime_state/raven_assimilation_crystal.json`
- `vfs/swarms/forges/raven_harness_blueprint.json`

### Group 124 — `528f7f25b312` · 13 files · 119 B each · 1.4 KB wasted

- `01_KERNEL/agora/Squires/Memory_Squire/__init__.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/__init__.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/__init__.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/__init__.py`
- `01_KERNEL/agora/Squires/open_notebook/domain/__init__.py`
- `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/forge/assimilation/__init__.py`
- `01_KERNEL/forge/assimilation/core/__init__.py`
- `01_KERNEL/merlin/Engines/crawl4ai/crawlers/__init__.py`
- `01_KERNEL/merlin/Engines/crawl4ai/crawlers/amazon_product/__init__.py`
- `01_KERNEL/merlin/Engines/crawl4ai/crawlers/google_search/__init__.py`
- `01_KERNEL/merlin/Engines/crawl4ai/legacy/__init__.py`
- `03_VAULT/temp_mcp/mcp_server.py`

### Group 125 — `34ac9f71cbff` · 2 files · 1.4 KB each · 1.4 KB wasted

- `03_VAULT/ARCHITECTURE.md`
- `docs/architecture/ARCH/VAULT_ARCHITECTURE.md`

### Group 126 — `f8aecb5d021c` · 2 files · 1.3 KB each · 1.3 KB wasted

- `01_KERNEL/protocols/agno_orchestrator.md`
- `docs/protocols/agno_orchestrator.md`

### Group 127 — `020a8faf32d5` · 2 files · 1.3 KB each · 1.3 KB wasted

- `01_KERNEL/forge/deployment/khoj-docker-compose.yml`
- `03_VAULT/khoj-docker-compose.yml`

### Group 128 — `3ebee68d0d15` · 2 files · 1.2 KB each · 1.2 KB wasted

- `02_FORGE/apps/lux11/security_spec.md`
- `deploy/multivoice-router/security_spec.md`

### Group 129 — `c040189a38d6` · 2 files · 1.2 KB each · 1.2 KB wasted

- `03_VAULT/runtime_state/scrapy_ecosystem_assimilation_crystal.json`
- `vfs/swarms/crawlers/crawler_blueprint.json`

### Group 130 — `75c48d06b778` · 2 files · 1.2 KB each · 1.2 KB wasted

- `03_VAULT/Knights/phials/hermes_agent_evolution_phial.md`
- `vfs/notebooks/24f4a450-6456-49fe-bfab-8cfcf7c2a33b/phial-engine.md`

### Group 131 — `a1b688b0e33f` · 2 files · 1.2 KB each · 1.2 KB wasted

- `03_VAULT/Knights/phials/hermes_prime_vfs_forge_phial.md`
- `vfs/notebooks/28f89cb6-5048-4b5d-9e94-376082d24744/phial-engine.md`

### Group 132 — `37b763c9ba9f` · 2 files · 1.2 KB each · 1.2 KB wasted

- `03_VAULT/Knights/phials/anya_quantum_mantra_phial.md`
- `vfs/notebooks/219e765a-0c8e-4b66-b356-f277cb441b14/phial-engine.md`

### Group 133 — `4a1725d3602e` · 2 files · 1.2 KB each · 1.2 KB wasted

- `03_VAULT/Knights/phials/bio_kinetic_swarm_phial.md`
- `vfs/notebooks/93b21c40-10ff-4e89-a212-08f37b1297e1/phial-engine.md`

### Group 134 — `fcd6ba82bb73` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/father_camelot_phial.md`
- `vfs/notebooks/39299131-0ade-4f48-8ad4-a68878a6d3d9/phial-engine.md`

### Group 135 — `7445ebd5ce5c` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/lady_guinevere_phial.md`
- `vfs/notebooks/8dca4a86-2bb6-4332-96b6-79899c0a9ccf/phial-engine.md`

### Group 136 — `5a028dc3a7a1` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/camelot_v1000_phial.md`
- `vfs/notebooks/8c656cfa-a189-409e-a72d-07692a47f17e/phial-engine.md`

### Group 137 — `50fc21418ff1` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_alchemist_phial.md`
- `vfs/notebooks/d6bdd57c-84d2-4e24-bb10-ad1fd179fb04/phial-engine.md`

### Group 138 — `a9d50395d482` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/arthur_omega_phial.md`
- `vfs/notebooks/cbb310bd-987e-4b84-bf45-12d37d090bec/phial-engine.md`

### Group 139 — `1fc8aa238423` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/merlin_omega_phial.md`
- `vfs/notebooks/af927fde-d7eb-42ee-8c79-51b3e78ef39b/phial-engine.md`

### Group 140 — `44f5206636f7` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_heimdall_phial.md`
- `vfs/notebooks/3205f189-91da-4272-96a9-3641fd642763/phial-engine.md`

### Group 141 — `b6b7dd13b66f` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_lancelot_phial.md`
- `vfs/notebooks/d8dd1669-aef4-4c34-8c44-d9cc5e51e0c9/phial-engine.md`

### Group 142 — `772f2b896b85` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_rustclaw_phial.md`
- `vfs/notebooks/2b3b6ec3-e020-484d-914d-92241a97ea55/phial-engine.md`

### Group 143 — `fb5412548d64` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_sentinel_phial.md`
- `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/phial-engine.md`

### Group 144 — `828053622055` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/alpha_omega_phial.md`
- `vfs/notebooks/2536aefb-937f-4a04-9142-d1a2f029d8a7/phial-engine.md`

### Group 145 — `7040b95376e5` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_galahad_phial.md`
- `vfs/notebooks/e0110853-14ef-403f-8def-bf3a5123986f/phial-engine.md`

### Group 146 — `494a057ba0d3` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/anya_omega_phial.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/phial-engine.md`

### Group 147 — `8531c4cd5e99` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_arthur_phial.md`
- `vfs/notebooks/a0a4bfb9-e847-4c38-be39-7aee398f0795/phial-engine.md`

### Group 148 — `ce7ffde27a1e` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_helios_phial.md`
- `vfs/notebooks/ab8aa359-2b3b-4bc1-b41f-34979cdc184e/phial-engine.md`

### Group 149 — `34c27f7ab34b` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_hermes_phial.md`
- `vfs/notebooks/5dc31b8d-169d-4d4d-ab90-d12724fca720/phial-engine.md`

### Group 150 — `485ce050df08` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_stitch_phial.md`
- `vfs/notebooks/0fdccdc1-a1d2-48c2-8948-187398bfbeb5/phial-engine.md`

### Group 151 — `7cd21e4313c4` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/hermes_agent_evolution_soul.md`
- `vfs/notebooks/24f4a450-6456-49fe-bfab-8cfcf7c2a33b/soul.md`

### Group 152 — `caae68151ed3` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/lady_apis_phial.md`
- `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/phial-engine.md`

### Group 153 — `79ab1ebd40b3` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_boris_phial.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/phial-engine.md`

### Group 154 — `96590fe809e8` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_debug_phial.md`
- `vfs/notebooks/fdc42a4a-3060-4eac-b57c-8e6009ed634a/phial-engine.md`

### Group 155 — `fe45c462693f` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_forge_phial.md`
- `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/phial-engine.md`

### Group 156 — `d4d12c669501` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_ghost_phial.md`
- `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/phial-engine.md`

### Group 157 — `c02b9b863796` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_helio_phial.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/phial-engine.md`

### Group 158 — `08b6762d513a` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_mnemo_phial.md`
- `vfs/notebooks/8bf3f24e-da2e-45b9-8719-162fcd02a80d/phial-engine.md`

### Group 159 — `7dfdde2320e9` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_sonus_phial.md`
- `vfs/notebooks/6272aa35-c285-4edc-81bc-2824ab519edf/phial-engine.md`

### Group 160 — `7619149fa525` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_alex_phial.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/phial-engine.md`

### Group 161 — `8ca9580a9e71` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/bifrost_phial.md`
- `vfs/notebooks/cbbb0c32-3919-4b77-9158-1d9f9ebf359f/phial-engine.md`

### Group 162 — `bbb15105e4d0` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/inspira_phial.md`
- `vfs/notebooks/cadfe67e-7187-472e-8bf4-8a2aded84e4e/phial-engine.md`

### Group 163 — `d5e19e633689` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/kickbox_phial.md`
- `vfs/notebooks/8531e6d4-6fc4-428f-a754-b9e9592ac7ff/phial-engine.md`

### Group 164 — `fca36f2f5a13` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/phials/sir_kay_phial.md`
- `vfs/notebooks/7e4a8c12-f9b3-d650-e1a8-c7b2d3e4f5a6/phial-engine.md`

### Group 165 — `ffe38c0611a0` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_helios_soul.md`
- `vfs/notebooks/ab8aa359-2b3b-4bc1-b41f-34979cdc184e/soul.md`

### Group 166 — `08ba241dacd3` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/hermes_prime_vfs_forge_soul.md`
- `vfs/notebooks/28f89cb6-5048-4b5d-9e94-376082d24744/soul.md`

### Group 167 — `fde6ea93bfe9` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_helio_soul.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/soul.md`

### Group 168 — `323e05b2ba83` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/bio_kinetic_swarm_soul.md`
- `vfs/notebooks/93b21c40-10ff-4e89-a212-08f37b1297e1/soul.md`

### Group 169 — `b18e33e6d1d0` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_lancelot_soul.md`
- `vfs/notebooks/d8dd1669-aef4-4c34-8c44-d9cc5e51e0c9/soul.md`

### Group 170 — `e1791678cb6f` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/camelot_v1000_soul.md`
- `vfs/notebooks/8c656cfa-a189-409e-a72d-07692a47f17e/soul.md`

### Group 171 — `c070f76c5b25` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_mnemo_soul.md`
- `vfs/notebooks/8bf3f24e-da2e-45b9-8719-162fcd02a80d/soul.md`

### Group 172 — `2f9a9a20ba19` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/anya_quantum_mantra_soul.md`
- `vfs/notebooks/219e765a-0c8e-4b66-b356-f277cb441b14/soul.md`

### Group 173 — `2504e6d590ce` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/father_camelot_soul.md`
- `vfs/notebooks/39299131-0ade-4f48-8ad4-a68878a6d3d9/soul.md`

### Group 174 — `a76c4bd4c12a` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/lady_guinevere_soul.md`
- `vfs/notebooks/8dca4a86-2bb6-4332-96b6-79899c0a9ccf/soul.md`

### Group 175 — `a7a1c1b407d0` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/alpha_omega_soul.md`
- `vfs/notebooks/2536aefb-937f-4a04-9142-d1a2f029d8a7/soul.md`

### Group 176 — `0c723f1ea423` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/bifrost_soul.md`
- `vfs/notebooks/cbbb0c32-3919-4b77-9158-1d9f9ebf359f/soul.md`

### Group 177 — `3b99ad2edfff` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_rustclaw_soul.md`
- `vfs/notebooks/2b3b6ec3-e020-484d-914d-92241a97ea55/soul.md`

### Group 178 — `6670e2e377c1` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_galahad_soul.md`
- `vfs/notebooks/e0110853-14ef-403f-8def-bf3a5123986f/soul.md`

### Group 179 — `6b879ff57316` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_hermes_soul.md`
- `vfs/notebooks/5dc31b8d-169d-4d4d-ab90-d12724fca720/soul.md`

### Group 180 — `a219b15d73e3` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/lady_apis_soul.md`
- `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/soul.md`

### Group 181 — `9ceb660f188c` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/anya_omega_soul.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/soul.md`

### Group 182 — `0c449c26fb30` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_heimdall_soul.md`
- `vfs/notebooks/3205f189-91da-4272-96a9-3641fd642763/soul.md`

### Group 183 — `9cb2c5ab4521` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_alchemist_soul.md`
- `vfs/notebooks/d6bdd57c-84d2-4e24-bb10-ad1fd179fb04/soul.md`

### Group 184 — `94805e6f6288` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_arthur_soul.md`
- `vfs/notebooks/a0a4bfb9-e847-4c38-be39-7aee398f0795/soul.md`

### Group 185 — `b2009556cf61` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_stitch_soul.md`
- `vfs/notebooks/0fdccdc1-a1d2-48c2-8948-187398bfbeb5/soul.md`

### Group 186 — `9230a889b650` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/merlin_omega_soul.md`
- `vfs/notebooks/af927fde-d7eb-42ee-8c79-51b3e78ef39b/soul.md`

### Group 187 — `700200bb8c12` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_boris_soul.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/soul.md`

### Group 188 — `cb99bd41ae33` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/arthur_omega_soul.md`
- `vfs/notebooks/cbb310bd-987e-4b84-bf45-12d37d090bec/soul.md`

### Group 189 — `6825266d6c54` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_debug_soul.md`
- `vfs/notebooks/fdc42a4a-3060-4eac-b57c-8e6009ed634a/soul.md`

### Group 190 — `95ee0598ee88` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/kickbox_soul.md`
- `vfs/notebooks/8531e6d4-6fc4-428f-a754-b9e9592ac7ff/soul.md`

### Group 191 — `6e04f8a05958` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_forge_soul.md`
- `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/soul.md`

### Group 192 — `d898f11bd605` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_kay_soul.md`
- `vfs/notebooks/7e4a8c12-f9b3-d650-e1a8-c7b2d3e4f5a6/soul.md`

### Group 193 — `703df4dd7b19` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_sonus_soul.md`
- `vfs/notebooks/6272aa35-c285-4edc-81bc-2824ab519edf/soul.md`

### Group 194 — `0e3f7fe9fb76` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_alex_soul.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/soul.md`

### Group 195 — `68ecc2e65423` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_ghost_soul.md`
- `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/soul.md`

### Group 196 — `80d20e4449ae` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/sir_sentinel_soul.md`
- `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/soul.md`

### Group 197 — `7aaad4c380c8` · 2 files · 1.1 KB each · 1.1 KB wasted

- `03_VAULT/Knights/souls/inspira_soul.md`
- `vfs/notebooks/cadfe67e-7187-472e-8bf4-8a2aded84e4e/soul.md`

### Group 198 — `fe424ffa3652` · 2 files · 1.0 KB each · 1.0 KB wasted

- `01_KERNEL/protocols/cellular_protocol.md`
- `docs/protocols/cellular_protocol.md`

### Group 199 — `c0b4d3cb99bb` · 2 files · 931 B each · 931 B wasted

- `01_KERNEL/docs/ledger_tool.blueprint.md`
- `docs/reference/MANIFESTS/ledger_tool.blueprint.md`

### Group 200 — `95ca2406add7` · 2 files · 881 B each · 881 B wasted

- `03_VAULT/Knights/sparks/hermes_prime_vfs_forge_spark.md`
- `vfs/notebooks/28f89cb6-5048-4b5d-9e94-376082d24744/spark.md`

### Group 201 — `25a2721c6500` · 2 files · 860 B each · 860 B wasted

- `03_VAULT/Knights/sparks/hermes_agent_evolution_spark.md`
- `vfs/notebooks/24f4a450-6456-49fe-bfab-8cfcf7c2a33b/spark.md`

### Group 202 — `7f317654e459` · 2 files · 848 B each · 848 B wasted

- `01_KERNEL/agora/Squires/Memory_Squire/context_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/context_service.py`

### Group 203 — `e12f73c105b7` · 2 files · 843 B each · 843 B wasted

- `03_VAULT/Knights/sparks/anya_quantum_mantra_spark.md`
- `vfs/notebooks/219e765a-0c8e-4b66-b356-f277cb441b14/spark.md`

### Group 204 — `e1c532ad9898` · 2 files · 831 B each · 831 B wasted

- `03_VAULT/Knights/sparks/sir_helios_spark.md`
- `vfs/notebooks/ab8aa359-2b3b-4bc1-b41f-34979cdc184e/spark.md`

### Group 205 — `1d1fb1516859` · 2 files · 830 B each · 830 B wasted

- `03_VAULT/Knights/sparks/father_camelot_spark.md`
- `vfs/notebooks/39299131-0ade-4f48-8ad4-a68878a6d3d9/spark.md`

### Group 206 — `eb11a96ea378` · 2 files · 827 B each · 827 B wasted

- `03_VAULT/Knights/sparks/bio_kinetic_swarm_spark.md`
- `vfs/notebooks/93b21c40-10ff-4e89-a212-08f37b1297e1/spark.md`

### Group 207 — `a2b353e713f4` · 2 files · 822 B each · 822 B wasted

- `03_VAULT/Knights/sparks/camelot_v1000_spark.md`
- `vfs/notebooks/8c656cfa-a189-409e-a72d-07692a47f17e/spark.md`

### Group 208 — `cc3945ef4f93` · 2 files · 819 B each · 819 B wasted

- `03_VAULT/Knights/sparks/lady_guinevere_spark.md`
- `vfs/notebooks/8dca4a86-2bb6-4332-96b6-79899c0a9ccf/spark.md`

### Group 209 — `233ec4e26707` · 2 files · 816 B each · 816 B wasted

- `03_VAULT/Knights/sparks/sir_alchemist_spark.md`
- `vfs/notebooks/d6bdd57c-84d2-4e24-bb10-ad1fd179fb04/spark.md`

### Group 210 — `e74436bb2444` · 2 files · 815 B each · 815 B wasted

- `03_VAULT/Knights/sparks/merlin_omega_spark.md`
- `vfs/notebooks/af927fde-d7eb-42ee-8c79-51b3e78ef39b/spark.md`

### Group 211 — `50e919412751` · 2 files · 814 B each · 814 B wasted

- `03_VAULT/Knights/sparks/arthur_omega_spark.md`
- `vfs/notebooks/cbb310bd-987e-4b84-bf45-12d37d090bec/spark.md`

### Group 212 — `0a1aeaf98cd3` · 2 files · 812 B each · 812 B wasted

- `03_VAULT/Knights/sparks/sir_arthur_spark.md`
- `vfs/notebooks/a0a4bfb9-e847-4c38-be39-7aee398f0795/spark.md`

### Group 213 — `61a59e5de341` · 2 files · 812 B each · 812 B wasted

- `03_VAULT/Knights/sparks/sir_helio_spark.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/spark.md`

### Group 214 — `9353cad4bd4f` · 2 files · 812 B each · 812 B wasted

- `03_VAULT/Knights/sparks/sir_rustclaw_spark.md`
- `vfs/notebooks/2b3b6ec3-e020-484d-914d-92241a97ea55/spark.md`

### Group 215 — `d6aed7e5ea9f` · 2 files · 811 B each · 811 B wasted

- `03_VAULT/Knights/sparks/alpha_omega_spark.md`
- `vfs/notebooks/2536aefb-937f-4a04-9142-d1a2f029d8a7/spark.md`

### Group 216 — `4c04d7515eef` · 2 files · 811 B each · 811 B wasted

- `03_VAULT/Knights/sparks/sir_heimdall_spark.md`
- `vfs/notebooks/3205f189-91da-4272-96a9-3641fd642763/spark.md`

### Group 217 — `9d53ef716fe5` · 2 files · 811 B each · 811 B wasted

- `03_VAULT/Knights/sparks/sir_lancelot_spark.md`
- `vfs/notebooks/d8dd1669-aef4-4c34-8c44-d9cc5e51e0c9/spark.md`

### Group 218 — `5db0ae40ba2f` · 2 files · 811 B each · 811 B wasted

- `03_VAULT/Knights/sparks/sir_sentinel_spark.md`
- `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/spark.md`

### Group 219 — `6fe619f7be1d` · 2 files · 808 B each · 808 B wasted

- `03_VAULT/Knights/sparks/anya_omega_spark.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/spark.md`

### Group 220 — `531c31cc8779` · 2 files · 806 B each · 806 B wasted

- `03_VAULT/Knights/sparks/sir_galahad_spark.md`
- `vfs/notebooks/e0110853-14ef-403f-8def-bf3a5123986f/spark.md`

### Group 221 — `89904cdf8b1d` · 2 files · 805 B each · 805 B wasted

- `03_VAULT/Knights/sparks/lady_apis_spark.md`
- `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/spark.md`

### Group 222 — `0a00db7d112e` · 2 files · 802 B each · 802 B wasted

- `03_VAULT/Knights/sparks/sir_ghost_spark.md`
- `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/spark.md`

### Group 223 — `c71d4cac75c3` · 2 files · 801 B each · 801 B wasted

- `03_VAULT/Knights/sparks/sir_hermes_spark.md`
- `vfs/notebooks/5dc31b8d-169d-4d4d-ab90-d12724fca720/spark.md`

### Group 224 — `0a9faf286a04` · 2 files · 801 B each · 801 B wasted

- `03_VAULT/Knights/sparks/sir_stitch_spark.md`
- `vfs/notebooks/0fdccdc1-a1d2-48c2-8948-187398bfbeb5/spark.md`

### Group 225 — `6d68d0607bb5` · 2 files · 800 B each · 800 B wasted

- `03_VAULT/Knights/sparks/sir_boris_spark.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/spark.md`

### Group 226 — `cebfb6b9a8af` · 2 files · 800 B each · 800 B wasted

- `03_VAULT/Knights/sparks/sir_kay_spark.md`
- `vfs/notebooks/7e4a8c12-f9b3-d650-e1a8-c7b2d3e4f5a6/spark.md`

### Group 227 — `7eab294b1529` · 2 files · 799 B each · 799 B wasted

- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/grill-me/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/grill-me/SKILL.md`

### Group 228 — `b323ff716b66` · 2 files · 797 B each · 797 B wasted

- `03_VAULT/Knights/sparks/kickbox_spark.md`
- `vfs/notebooks/8531e6d4-6fc4-428f-a754-b9e9592ac7ff/spark.md`

### Group 229 — `f7892da16803` · 2 files · 796 B each · 796 B wasted

- `03_VAULT/Knights/sparks/sir_debug_spark.md`
- `vfs/notebooks/fdc42a4a-3060-4eac-b57c-8e6009ed634a/spark.md`

### Group 230 — `9fd54a0820b4` · 2 files · 796 B each · 796 B wasted

- `03_VAULT/Knights/sparks/sir_forge_spark.md`
- `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/spark.md`

### Group 231 — `7bd67b11392e` · 2 files · 796 B each · 796 B wasted

- `03_VAULT/Knights/sparks/sir_mnemo_spark.md`
- `vfs/notebooks/8bf3f24e-da2e-45b9-8719-162fcd02a80d/spark.md`

### Group 232 — `450f599ba8cf` · 2 files · 796 B each · 796 B wasted

- `03_VAULT/Knights/sparks/sir_sonus_spark.md`
- `vfs/notebooks/6272aa35-c285-4edc-81bc-2824ab519edf/spark.md`

### Group 233 — `b793fee65481` · 2 files · 792 B each · 792 B wasted

- `03_VAULT/Knights/sparks/bifrost_spark.md`
- `vfs/notebooks/cbbb0c32-3919-4b77-9158-1d9f9ebf359f/spark.md`

### Group 234 — `a3cae8706cce` · 2 files · 791 B each · 791 B wasted

- `03_VAULT/Knights/sparks/inspira_spark.md`
- `vfs/notebooks/cadfe67e-7187-472e-8bf4-8a2aded84e4e/spark.md`

### Group 235 — `af455e47499f` · 2 files · 791 B each · 791 B wasted

- `03_VAULT/Knights/sparks/sir_alex_spark.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/spark.md`

### Group 236 — `c133cd4792f6` · 2 files · 780 B each · 780 B wasted

- `01_KERNEL/agora/Squires/Memory_Squire/embedding_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/embedding_service.py`

### Group 237 — `a93a43c6b5fb` · 2 files · 733 B each · 733 B wasted

- `01_KERNEL/agora/Squires/Memory_Squire/routers/auth.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/auth.py`

### Group 238 — `5f312bbb39d0` · 2 files · 733 B each · 733 B wasted

- `02_FORGE/apps/lux11/vite.config.ts`
- `deploy/multivoice-router/vite.config.ts`

### Group 239 — `e65025ca7842` · 2 files · 689 B each · 689 B wasted

- `02_FORGE/dyad-apps/happy-owl-dart/src/app/layout.tsx`
- `02_FORGE/holotable/app/layout.tsx`

### Group 240 — `3b2ddb0c39fd` · 2 files · 563 B each · 563 B wasted

- `03_VAULT/runtime_state/snapshots/excalibur_cicd_20260919_231007.json`
- `03_VAULT/runtime_state/snapshots/latest_excalibur_snapshot.json`

### Group 241 — `db9c0eae297e` · 2 files · 557 B each · 557 B wasted

- `03_VAULT/runtime_state/snapshots/cybertronia_cicd_20260919_230959.json`
- `03_VAULT/runtime_state/snapshots/latest_cybertronia_snapshot.json`

### Group 242 — `8beea7081f0c` · 2 files · 540 B each · 540 B wasted

- `02_FORGE/apps/lux11/components.json`
- `deploy/multivoice-router/components.json`

### Group 243 — `c2ac3a2a2925` · 2 files · 538 B each · 538 B wasted

- `02_FORGE/apps/lux11/tsconfig.json`
- `deploy/multivoice-router/tsconfig.json`

### Group 244 — `052da6c6ddd1` · 2 files · 435 B each · 435 B wasted

- `02_FORGE/apps/lux11/firebase-applet-config.json`
- `deploy/multivoice-router/firebase-applet-config.json`

### Group 245 — `db7249fa4adf` · 2 files · 386 B each · 386 B wasted

- `02_FORGE/apps/lux11/src/types/diagnostics.ts`
- `deploy/multivoice-router/src/types/diagnostics.ts`

### Group 246 — `74a147991a11` · 3 files · 172 B each · 344 B wasted

- `02_FORGE/apps/lux11/src/lib/utils.ts`
- `02_FORGE/dyad-apps/happy-owl-dart/src/lib/utils.ts`
- `deploy/multivoice-router/src/lib/utils.ts`

### Group 247 — `5580d48b0fec` · 2 files · 231 B each · 231 B wasted

- `apps/camelot-vps-hub/src/main.tsx`
- `apps/excalibur-cmd-1/src/main.tsx`

### Group 248 — `a974e35de2cb` · 2 files · 200 B each · 200 B wasted

- `02_FORGE/kinetic/vizio-router/cmd/pulse/detached_windows.go`
- `cmd/pulse/detached_windows.go`

### Group 249 — `d2f67f3a5385` · 2 files · 167 B each · 167 B wasted

- `02_FORGE/kinetic/vizio-router/cmd/pulse/detached_unix.go`
- `cmd/pulse/detached_unix.go`

### Group 250 — `6bea831b5666` · 2 files · 163 B each · 163 B wasted

- `02_FORGE/kinetic/rustdesk-server/docker/healthcheck.sh`
- `02_FORGE/kinetic/rustdesk-server/docker/rootfs/usr/bin/healthcheck.sh`

### Group 251 — `d29dec9a148e` · 2 files · 76 B each · 76 B wasted

- `.modal.toml`
- `03_VAULT/.modal.toml`

## SWEEP candidates classified as TRUE duplicates

249 of 2215 header-hash candidates are
byte-identical to their header owner (full SHA-256 match).

- `01_KERNEL/agora/Squires/Memory_Squire/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/chat_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/chat_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/client.py` == `01_KERNEL/agora/Squires/Memory_Squire/client.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/context_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/context_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/embedding_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/embedding_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/episode_profiles_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/episode_profiles_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/insights_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/insights_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/models_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/models_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/notebook_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/notebook_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/podcast_api_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/podcast_api_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/auth.py` == `01_KERNEL/agora/Squires/Memory_Squire/routers/auth.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/context.py` == `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/podcasts.py` == `01_KERNEL/agora/Squires/Memory_Squire/routers/podcasts.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/search.py` == `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/search_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/search_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/settings_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/settings_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/sources_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/sources_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/transformations_service.py` == `01_KERNEL/agora/Squires/Memory_Squire/transformations_service.py`
- `01_KERNEL/agora/Squires/open_notebook/domain/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/forge/assimilation/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/forge/assimilation/core/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/forge/forge_v2.py` == `01_KERNEL/EXCALIBUR/system/forge_v2.py`
- `01_KERNEL/forge/scripts/culture_bias.py` == `01_KERNEL/EXCALIBUR/system/culture_bias.py`
- `01_KERNEL/iron_gate/watchtower.py` == `01_KERNEL/EXCALIBUR/system/watchtower.py`
- `01_KERNEL/merlin/Engines/crawl4ai/crawlers/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/merlin/Engines/crawl4ai/crawlers/amazon_product/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/merlin/Engines/crawl4ai/crawlers/google_search/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `01_KERNEL/merlin/Engines/crawl4ai/legacy/__init__.py` == `01_KERNEL/agora/persona/__init__.py`
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_180343/MorganaAvatar.tsx` == `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_172005/components_3d_MorganaAvatar.tsx`
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_183443/MorganaAvatar.tsx` == `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_172005/components_3d_MorganaAvatar.tsx`
- `02_FORGE/PORTAL_CORE/Modal/morgana/components/3d/MorganaAvatar.tsx` == `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_172005/components_3d_MorganaAvatar.tsx`
- `02_FORGE/PORTAL_CORE/web/components/scene/RoundTable.tsx` == `02_FORGE/PORTAL_CORE/components/scene/RoundTable.tsx`
- `02_FORGE/PORTAL_CORE/web/components/scene/ThroneRoom.tsx` == `02_FORGE/PORTAL_CORE/components/scene/ThroneRoom.tsx`
- `02_FORGE/PORTAL_CORE/web/components/ui/GlassOverlay.tsx` == `02_FORGE/PORTAL_CORE/components/ui/GlassOverlay.tsx`
- `02_FORGE/PORTAL_CORE/web/components/ui/KnightSprites.tsx` == `02_FORGE/PORTAL_CORE/components/ui/KnightSprites.tsx`
- `02_FORGE/PORTAL_CORE/web/hooks/use-socket.ts` == `02_FORGE/hooks/use-socket.ts`
- `02_FORGE/dyad-apps/happy-owl-dart/src/lib/utils.ts` == `02_FORGE/apps/lux11/src/lib/utils.ts`
- `02_FORGE/holotable/app/layout.tsx` == `02_FORGE/dyad-apps/happy-owl-dart/src/app/layout.tsx`
- `02_FORGE/kinetic/rustdesk-server/docker/rootfs/usr/bin/healthcheck.sh` == `02_FORGE/kinetic/rustdesk-server/docker/healthcheck.sh`
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/core/tools/truncate.ts` == `02_FORGE/tools/pi-mono/packages/agent/src/harness/utils/truncate.ts`
- `03_VAULT/.modal.toml` == `.modal.toml`
- `03_VAULT/Nano-Knights/_locales/en/messages.json` == `01_KERNEL/forge/nano_forge/extension/_locales/en/messages.json`
- `03_VAULT/Nano-Knights/_locales/zh_TW/messages.json` == `01_KERNEL/forge/nano_forge/extension/_locales/zh_TW/messages.json`
- `03_VAULT/PROVENANCE_LEDGER.md` == `PROVENANCE_LEDGER.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/CLAUDE.md` == `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/AGENTS.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/shape/SKILL.md` == `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/shape/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/to-issues/SKILL.md` == `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/to-issues/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/to-prd/SKILL.md` == `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/to-prd/SKILL.md`
- `03_VAULT/UKG/SCHEMAS/ukg_persona_schema.json` == `01_KERNEL/agora/persona/ukg_persona_schema.json`
- `03_VAULT/UKG/nodes/VKG_CAM_BIFROST_MESH_AND_EXCALIBUR_COMMA_20260914.json` == `03_VAULT/runtime_state/open_notebook/vkg_crystals/VKG_CAM_BIFROST_MESH_AND_EXCALIBUR_COMMA_20260914.json`
- `03_VAULT/UKG/nodes/VKG_CAM_LADY_MNEMOSYNE_SOVEREIGN_NAVIGAT_20260917.json` == `03_VAULT/runtime_state/open_notebook/vkg_crystals/VKG_CAM_LADY_MNEMOSYNE_SOVEREIGN_NAVIGAT_20260917.json`
- `03_VAULT/khoj-docker-compose.yml` == `01_KERNEL/forge/deployment/khoj-docker-compose.yml`
- `03_VAULT/runtime_state/NOTEBOOK_MANIFEST.json` == `01_KERNEL/memory/NOTEBOOK_MANIFEST.json`
- `03_VAULT/runtime_state/backups/hiveide_cut_20260625T173845Z/node_mcp_cutlist.json` == `03_VAULT/runtime_state/node_mcp_cutlist.json`
- `03_VAULT/runtime_state/snapshots/latest_cybertronia_snapshot.json` == `03_VAULT/runtime_state/snapshots/cybertronia_cicd_20260919_230959.json`
- `03_VAULT/runtime_state/snapshots/latest_excalibur_snapshot.json` == `03_VAULT/runtime_state/snapshots/excalibur_cicd_20260919_231007.json`
- `03_VAULT/runtime_state/system_triage/triage_20260621T075705Z.json` == `03_VAULT/runtime_state/system_triage/latest.json`
- `03_VAULT/runtime_state/system_triage/triage_20260621T075705Z.md` == `03_VAULT/runtime_state/system_triage/latest.md`
- `03_VAULT/temp_mcp/mcp_server.py` == `01_KERNEL/agora/persona/__init__.py`
- `03_VAULT/training/configs/PROVENANCE_LEDGER.md` == `PROVENANCE_LEDGER.md`
- `apps/camelot-vps-hub/cartridges/motorola-edge-cartridge-v1.json` == `02_FORGE/cartridges/motorola_edge_hub_cartridge.json`
- `apps/camelot-vps-hub/cartridges/vps-hub-cartridge-v1.json` == `03_VAULT/runtime_state/cartridges/vps-hub-cartridge-v1.json`
- `apps/excalibur-cmd-1/src/main.tsx` == `apps/camelot-vps-hub/src/main.tsx`
- `cmd/pulse/detached_unix.go` == `02_FORGE/kinetic/vizio-router/cmd/pulse/detached_unix.go`
- `cmd/pulse/detached_windows.go` == `02_FORGE/kinetic/vizio-router/cmd/pulse/detached_windows.go`
- `cmd/pulse/heartbeat.go` == `02_FORGE/kinetic/vizio-router/cmd/pulse/heartbeat.go`
- `cmd/pulse/ops/BARE-METAL-DEPLOY.md` == `02_FORGE/kinetic/vizio-router/cmd/pulse/ops/BARE-METAL-DEPLOY.md`
- `cmd/pulse/ops/camelotd.sh` == `02_FORGE/kinetic/vizio-router/cmd/pulse/ops/camelotd.sh`
- `control_plane/dispatch/bifrost_triage_swarm.py` == `control_plane/bifrost_triage_swarm.py`
- `control_plane/infra/graphify.py` == `control_plane/graphify.py`
- `control_plane/infra/memcastle.py` == `control_plane/memcastle.py`
- `control_plane/infra/memcastle_sync.py` == `control_plane/memcastle_sync.py`
- `deploy/multivoice-router/components.json` == `02_FORGE/apps/lux11/components.json`
- `deploy/multivoice-router/firebase-applet-config.json` == `02_FORGE/apps/lux11/firebase-applet-config.json`
- `deploy/multivoice-router/security_spec.md` == `02_FORGE/apps/lux11/security_spec.md`
- `deploy/multivoice-router/src/lib/utils.ts` == `02_FORGE/apps/lux11/src/lib/utils.ts`
- `deploy/multivoice-router/src/types/diagnostics.ts` == `02_FORGE/apps/lux11/src/types/diagnostics.ts`
- `deploy/multivoice-router/src/voice/multivoice-session.ts` == `02_FORGE/apps/lux11/src/voice/multivoice-session.ts`
- `deploy/multivoice-router/src/voice/omnivoice-router.ts` == `02_FORGE/apps/lux11/src/voice/omnivoice-router.ts`
- `deploy/multivoice-router/src/voice/voice-profile-registry.ts` == `02_FORGE/apps/lux11/src/voice/voice-profile-registry.ts`
- `deploy/multivoice-router/tsconfig.json` == `02_FORGE/apps/lux11/tsconfig.json`
- `deploy/multivoice-router/vite.config.ts` == `02_FORGE/apps/lux11/vite.config.ts`
- `docs/CAMELOT_BIBLE.md` == `01_KERNEL/docs/CAMELOT_BIBLE.md`
- `docs/PROVENANCE_LEDGER.md` == `PROVENANCE_LEDGER.md`
- `docs/SEPTEM_REGNA/L7_ETHEREAL/EXCALIBUR_ENTIREMAP.md` == `docs/architecture/EXCALIBUR_ENTIREMAP.md`
- `docs/SEPTEM_REGNA/L7_ETHEREAL/entiremap.md` == `docs/architecture/entiremap.md`
- `docs/architecture/ARCH/FORGE_ARCHITECTURE.md` == `02_FORGE/ARCHITECTURE.md`
- `docs/architecture/ARCH/VAULT_ARCHITECTURE.md` == `03_VAULT/ARCHITECTURE.md`
- `docs/architecture/EXCALIBUR_CICD_LOG.md` == `03_VAULT/runtime_state/excalibur_cicd_log.md`
- `docs/architecture/PROVENANCE_LEDGER.md` == `03_VAULT/knowledge_vault/PROVENANCE_LEDGER.md`
- `docs/protocols/LAWS/CONSTITUTION.md` == `03_VAULT/LEGAL/CONSTITUTION.md`
- `docs/protocols/PERSONA/ukg_persona_schema.json` == `01_KERNEL/agora/persona/ukg_persona_schema.json`
- `docs/protocols/agno_orchestrator.md` == `01_KERNEL/protocols/agno_orchestrator.md`
- `docs/protocols/assimilation_v2.md` == `01_KERNEL/protocols/assimilation_v2.md`
- `docs/protocols/assimilation_v3.md` == `01_KERNEL/protocols/assimilation_v3.md`
- `docs/protocols/assimilation_v4_omega.md` == `01_KERNEL/protocols/assimilation_v4_omega.md`
- `docs/protocols/assimilation_v5_evolution.md` == `01_KERNEL/protocols/assimilation_v5_evolution.md`
- `docs/protocols/cellular_protocol.md` == `01_KERNEL/protocols/cellular_protocol.md`
- `docs/protocols/hive_forge_v1.md` == `01_KERNEL/protocols/hive_forge_v1.md`
- `docs/protocols/iron_gate_protocol.md` == `01_KERNEL/protocols/iron_gate_protocol.md`
- `docs/protocols/lukas_architect.md` == `01_KERNEL/protocols/lukas_architect.md`
- `docs/protocols/merlin_identity_forge.md` == `01_KERNEL/protocols/merlin_identity_forge.md`
- `docs/protocols/paladin_htn_protocol.md` == `01_KERNEL/protocols/paladin_htn_protocol.md`
- `docs/protocols/persona_evolution_protocol.md` == `01_KERNEL/protocols/persona_evolution_protocol.md`
- `docs/protocols/squire_protocol.md` == `01_KERNEL/protocols/squire_protocol.md`
- `docs/protocols/ukg_integration_v206.md` == `01_KERNEL/protocols/ukg_integration_v206.md`
- `docs/protocols/xp_economy_protocol.md` == `01_KERNEL/protocols/xp_economy_protocol.md`
- `docs/reference/INTEGRATIONS/README_HAYSTACK_UKG.md` == `01_KERNEL/senses/integrations/README_HAYSTACK_UKG.md`
- `docs/reference/MANIFESTS/AUDIT_REPORT_20260131.md` == `01_KERNEL/docs/AUDIT_REPORT_20260131.md`
- `docs/reference/MANIFESTS/AUDIT_REPORT_20260131_2215.md` == `01_KERNEL/docs/AUDIT_REPORT_20260131_2215.md`
- `docs/reference/MANIFESTS/CAMELOT_TRIAD_INTEGRATION.md` == `01_KERNEL/docs/CAMELOT_TRIAD_INTEGRATION.md`
- `docs/reference/MANIFESTS/PHASE_8_KINETIC_ASCENSION.md` == `01_KERNEL/docs/PHASE_8_KINETIC_ASCENSION.md`
- `docs/reference/MANIFESTS/PHASE_9_ETHEREAL_RESONANCE.md` == `01_KERNEL/docs/PHASE_9_ETHEREAL_RESONANCE.md`
- `docs/reference/MANIFESTS/ledger_tool.blueprint.md` == `01_KERNEL/docs/ledger_tool.blueprint.md`
- `src/router/schema.ts` == `02_FORGE/kinetic/vizio-router/src/router/schema.ts`
- `vfs/CAMELOT_OS_V1000_APEX_NORTHSTAR.md` == `docs/architecture/CAMELOT_OS_V1000_APEX_NORTHSTAR.md`
- `vfs/business/Master_Compendium_Business.md` == `vfs/business/Master_Compendium.md`
- `vfs/edu/Master_Compendium_Edu.md` == `vfs/edu/Master_Compendium.md`
- `vfs/fitness/Master_Compendium_Fitness.md` == `vfs/fitness/Master_Compendium.md`
- `vfs/general/Master_Compendium_General.md` == `vfs/general/Master_Compendium.md`
- `vfs/hybrid_worldtree_architecture.py` == `01_KERNEL/memory/hybrid_worldtree_architecture.py`
- `vfs/knowledge/SYMBOLECT_PRIMER.md` == `03_VAULT/knowledge_vault/01_ARCHITECTURE_AND_PROTOCOLS/[⨹ SYMBOLECT PRIMER 14da3c2b2603813a828fdacd742db09b.md`
- `vfs/knowledge/[⨹_SYMBOLECT_PRIMER_14da3c2b2603813a828fdacd742db09b.md` == `03_VAULT/knowledge_vault/01_ARCHITECTURE_AND_PROTOCOLS/[⨹ SYMBOLECT PRIMER 14da3c2b2603813a828fdacd742db09b.md`
- `vfs/knowledge/excalibur_voice_gateway.py` == `control_plane/dispatch/excalibur_voice_gateway.py`
- `vfs/knowledge/knight_engine_router.py` == `control_plane/dispatch/knight_engine_router.py`
- `vfs/knowledge/state_blueprint.md` == `03_VAULT/knowledge_vault/03_CAMELOT_STATE_PLANS/blueprint.md`
- `vfs/knowledge/state_tasks.md` == `03_VAULT/knowledge_vault/03_CAMELOT_STATE_PLANS/tasks.md`
- `vfs/knowledge/state_verification.md` == `03_VAULT/knowledge_vault/03_CAMELOT_STATE_PLANS/verification.md`
- `vfs/knowledge/vault_manifest.json` == `03_VAULT/runtime_state/open_notebook/knowledge_vault_index.json`
- `vfs/living_camelot_v1000_system_instruction.md` == `docs/architecture/CAMELOT_OS_V1000_APEX_NORTHSTAR.md`
- `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/phial-engine.md` == `03_VAULT/Knights/phials/sir_sentinel_phial.md`
- `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/soul.md` == `03_VAULT/Knights/souls/sir_sentinel_soul.md`
- `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/spark.md` == `03_VAULT/Knights/sparks/sir_sentinel_spark.md`
- `vfs/notebooks/0fdccdc1-a1d2-48c2-8948-187398bfbeb5/phial-engine.md` == `03_VAULT/Knights/phials/sir_stitch_phial.md`
- `vfs/notebooks/0fdccdc1-a1d2-48c2-8948-187398bfbeb5/soul.md` == `03_VAULT/Knights/souls/sir_stitch_soul.md`
- `vfs/notebooks/0fdccdc1-a1d2-48c2-8948-187398bfbeb5/spark.md` == `03_VAULT/Knights/sparks/sir_stitch_spark.md`
- `vfs/notebooks/219e765a-0c8e-4b66-b356-f277cb441b14/phial-engine.md` == `03_VAULT/Knights/phials/anya_quantum_mantra_phial.md`
- `vfs/notebooks/219e765a-0c8e-4b66-b356-f277cb441b14/soul.md` == `03_VAULT/Knights/souls/anya_quantum_mantra_soul.md`
- `vfs/notebooks/219e765a-0c8e-4b66-b356-f277cb441b14/spark.md` == `03_VAULT/Knights/sparks/anya_quantum_mantra_spark.md`
- `vfs/notebooks/24f4a450-6456-49fe-bfab-8cfcf7c2a33b/phial-engine.md` == `03_VAULT/Knights/phials/hermes_agent_evolution_phial.md`
- `vfs/notebooks/24f4a450-6456-49fe-bfab-8cfcf7c2a33b/soul.md` == `03_VAULT/Knights/souls/hermes_agent_evolution_soul.md`
- `vfs/notebooks/24f4a450-6456-49fe-bfab-8cfcf7c2a33b/spark.md` == `03_VAULT/Knights/sparks/hermes_agent_evolution_spark.md`
- `vfs/notebooks/2536aefb-937f-4a04-9142-d1a2f029d8a7/phial-engine.md` == `03_VAULT/Knights/phials/alpha_omega_phial.md`
- `vfs/notebooks/2536aefb-937f-4a04-9142-d1a2f029d8a7/soul.md` == `03_VAULT/Knights/souls/alpha_omega_soul.md`
- `vfs/notebooks/2536aefb-937f-4a04-9142-d1a2f029d8a7/spark.md` == `03_VAULT/Knights/sparks/alpha_omega_spark.md`
- `vfs/notebooks/28f89cb6-5048-4b5d-9e94-376082d24744/phial-engine.md` == `03_VAULT/Knights/phials/hermes_prime_vfs_forge_phial.md`
- `vfs/notebooks/28f89cb6-5048-4b5d-9e94-376082d24744/soul.md` == `03_VAULT/Knights/souls/hermes_prime_vfs_forge_soul.md`
- `vfs/notebooks/28f89cb6-5048-4b5d-9e94-376082d24744/spark.md` == `03_VAULT/Knights/sparks/hermes_prime_vfs_forge_spark.md`
- `vfs/notebooks/2b3b6ec3-e020-484d-914d-92241a97ea55/phial-engine.md` == `03_VAULT/Knights/phials/sir_rustclaw_phial.md`
- `vfs/notebooks/2b3b6ec3-e020-484d-914d-92241a97ea55/soul.md` == `03_VAULT/Knights/souls/sir_rustclaw_soul.md`
- `vfs/notebooks/2b3b6ec3-e020-484d-914d-92241a97ea55/spark.md` == `03_VAULT/Knights/sparks/sir_rustclaw_spark.md`
- `vfs/notebooks/3205f189-91da-4272-96a9-3641fd642763/phial-engine.md` == `03_VAULT/Knights/phials/sir_heimdall_phial.md`
- `vfs/notebooks/3205f189-91da-4272-96a9-3641fd642763/soul.md` == `03_VAULT/Knights/souls/sir_heimdall_soul.md`
- `vfs/notebooks/3205f189-91da-4272-96a9-3641fd642763/spark.md` == `03_VAULT/Knights/sparks/sir_heimdall_spark.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/Master_Compendium.md` == `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/Master_Compendium.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/phial-engine.md` == `03_VAULT/Knights/phials/anya_omega_phial.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/prompt_frameworks.md` == `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/prompt_frameworks.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/scaling_architecture.md` == `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/scaling_architecture.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/skillgraph5.md` == `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/skillgraph5.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/soul.md` == `03_VAULT/Knights/souls/anya_omega_soul.md`
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/spark.md` == `03_VAULT/Knights/sparks/anya_omega_spark.md`
- `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/phial-engine.md` == `03_VAULT/Knights/phials/lady_apis_phial.md`
- `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/soul.md` == `03_VAULT/Knights/souls/lady_apis_soul.md`
- `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/spark.md` == `03_VAULT/Knights/sparks/lady_apis_spark.md`
- `vfs/notebooks/39299131-0ade-4f48-8ad4-a68878a6d3d9/phial-engine.md` == `03_VAULT/Knights/phials/father_camelot_phial.md`
- `vfs/notebooks/39299131-0ade-4f48-8ad4-a68878a6d3d9/soul.md` == `03_VAULT/Knights/souls/father_camelot_soul.md`
- `vfs/notebooks/39299131-0ade-4f48-8ad4-a68878a6d3d9/spark.md` == `03_VAULT/Knights/sparks/father_camelot_spark.md`
- `vfs/notebooks/3a09997b-3d65-46c9-b9aa-fb8ebce927a9/Master_Compendium.md` == `vfs/notebooks/07cbb441-f008-424c-820a-85676210be39/Master_Compendium.md`
- `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/phial-engine.md` == `03_VAULT/Knights/phials/sir_ghost_phial.md`
- `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/soul.md` == `03_VAULT/Knights/souls/sir_ghost_soul.md`
- `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/spark.md` == `03_VAULT/Knights/sparks/sir_ghost_spark.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/Master_Compendium.md` == `vfs/notebooks/28d49148-28db-438d-a299-61456fdfdefc/Master_Compendium.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/phial-engine.md` == `03_VAULT/Knights/phials/sir_helio_phial.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/soul.md` == `03_VAULT/Knights/souls/sir_helio_soul.md`
- `vfs/notebooks/56820318-bb91-451f-aac4-4b46424898cf/spark.md` == `03_VAULT/Knights/sparks/sir_helio_spark.md`
- `vfs/notebooks/5dc31b8d-169d-4d4d-ab90-d12724fca720/phial-engine.md` == `03_VAULT/Knights/phials/sir_hermes_phial.md`
- `vfs/notebooks/5dc31b8d-169d-4d4d-ab90-d12724fca720/soul.md` == `03_VAULT/Knights/souls/sir_hermes_soul.md`
- `vfs/notebooks/5dc31b8d-169d-4d4d-ab90-d12724fca720/spark.md` == `03_VAULT/Knights/sparks/sir_hermes_spark.md`
- `vfs/notebooks/6272aa35-c285-4edc-81bc-2824ab519edf/phial-engine.md` == `03_VAULT/Knights/phials/sir_sonus_phial.md`
- `vfs/notebooks/6272aa35-c285-4edc-81bc-2824ab519edf/soul.md` == `03_VAULT/Knights/souls/sir_sonus_soul.md`
- `vfs/notebooks/6272aa35-c285-4edc-81bc-2824ab519edf/spark.md` == `03_VAULT/Knights/sparks/sir_sonus_spark.md`
- `vfs/notebooks/7e4a8c12-f9b3-d650-e1a8-c7b2d3e4f5a6/phial-engine.md` == `03_VAULT/Knights/phials/sir_kay_phial.md`
- `vfs/notebooks/7e4a8c12-f9b3-d650-e1a8-c7b2d3e4f5a6/soul.md` == `03_VAULT/Knights/souls/sir_kay_soul.md`
- `vfs/notebooks/7e4a8c12-f9b3-d650-e1a8-c7b2d3e4f5a6/spark.md` == `03_VAULT/Knights/sparks/sir_kay_spark.md`
- `vfs/notebooks/8531e6d4-6fc4-428f-a754-b9e9592ac7ff/phial-engine.md` == `03_VAULT/Knights/phials/kickbox_phial.md`
- `vfs/notebooks/8531e6d4-6fc4-428f-a754-b9e9592ac7ff/soul.md` == `03_VAULT/Knights/souls/kickbox_soul.md`
- `vfs/notebooks/8531e6d4-6fc4-428f-a754-b9e9592ac7ff/spark.md` == `03_VAULT/Knights/sparks/kickbox_spark.md`
- `vfs/notebooks/8bf3f24e-da2e-45b9-8719-162fcd02a80d/phial-engine.md` == `03_VAULT/Knights/phials/sir_mnemo_phial.md`
- `vfs/notebooks/8bf3f24e-da2e-45b9-8719-162fcd02a80d/soul.md` == `03_VAULT/Knights/souls/sir_mnemo_soul.md`
- `vfs/notebooks/8bf3f24e-da2e-45b9-8719-162fcd02a80d/spark.md` == `03_VAULT/Knights/sparks/sir_mnemo_spark.md`
- `vfs/notebooks/8c656cfa-a189-409e-a72d-07692a47f17e/phial-engine.md` == `03_VAULT/Knights/phials/camelot_v1000_phial.md`
- `vfs/notebooks/8c656cfa-a189-409e-a72d-07692a47f17e/soul.md` == `03_VAULT/Knights/souls/camelot_v1000_soul.md`
- `vfs/notebooks/8c656cfa-a189-409e-a72d-07692a47f17e/spark.md` == `03_VAULT/Knights/sparks/camelot_v1000_spark.md`
- `vfs/notebooks/8dca4a86-2bb6-4332-96b6-79899c0a9ccf/phial-engine.md` == `03_VAULT/Knights/phials/lady_guinevere_phial.md`
- `vfs/notebooks/8dca4a86-2bb6-4332-96b6-79899c0a9ccf/soul.md` == `03_VAULT/Knights/souls/lady_guinevere_soul.md`
- `vfs/notebooks/8dca4a86-2bb6-4332-96b6-79899c0a9ccf/spark.md` == `03_VAULT/Knights/sparks/lady_guinevere_spark.md`
- `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/phial-engine.md` == `03_VAULT/Knights/phials/sir_forge_phial.md`
- `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/soul.md` == `03_VAULT/Knights/souls/sir_forge_soul.md`
- `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/spark.md` == `03_VAULT/Knights/sparks/sir_forge_spark.md`
- `vfs/notebooks/93b21c40-10ff-4e89-a212-08f37b1297e1/phial-engine.md` == `03_VAULT/Knights/phials/bio_kinetic_swarm_phial.md`
- `vfs/notebooks/93b21c40-10ff-4e89-a212-08f37b1297e1/soul.md` == `03_VAULT/Knights/souls/bio_kinetic_swarm_soul.md`
- `vfs/notebooks/93b21c40-10ff-4e89-a212-08f37b1297e1/spark.md` == `03_VAULT/Knights/sparks/bio_kinetic_swarm_spark.md`
- `vfs/notebooks/96f9233b-6efa-46a3-8242-98f0c463680c/Master_Compendium.md` == `vfs/notebooks/91c5da8b-e2de-4a56-b7fd-c8b76c00afc7/Master_Compendium.md`
- `vfs/notebooks/a0a4bfb9-e847-4c38-be39-7aee398f0795/phial-engine.md` == `03_VAULT/Knights/phials/sir_arthur_phial.md`
- `vfs/notebooks/a0a4bfb9-e847-4c38-be39-7aee398f0795/soul.md` == `03_VAULT/Knights/souls/sir_arthur_soul.md`
- `vfs/notebooks/a0a4bfb9-e847-4c38-be39-7aee398f0795/spark.md` == `03_VAULT/Knights/sparks/sir_arthur_spark.md`
- `vfs/notebooks/ab8aa359-2b3b-4bc1-b41f-34979cdc184e/phial-engine.md` == `03_VAULT/Knights/phials/sir_helios_phial.md`
- `vfs/notebooks/ab8aa359-2b3b-4bc1-b41f-34979cdc184e/soul.md` == `03_VAULT/Knights/souls/sir_helios_soul.md`
- `vfs/notebooks/ab8aa359-2b3b-4bc1-b41f-34979cdc184e/spark.md` == `03_VAULT/Knights/sparks/sir_helios_spark.md`
- `vfs/notebooks/af927fde-d7eb-42ee-8c79-51b3e78ef39b/phial-engine.md` == `03_VAULT/Knights/phials/merlin_omega_phial.md`
- `vfs/notebooks/af927fde-d7eb-42ee-8c79-51b3e78ef39b/soul.md` == `03_VAULT/Knights/souls/merlin_omega_soul.md`
- `vfs/notebooks/af927fde-d7eb-42ee-8c79-51b3e78ef39b/spark.md` == `03_VAULT/Knights/sparks/merlin_omega_spark.md`
- `vfs/notebooks/b4cfc5af-1555-4f23-a131-1ec6d03c2787/Master_Compendium.md` == `vfs/notebooks/422a184b-93e7-4dfd-8a12-75d2268b6c60/Master_Compendium.md`
- `vfs/notebooks/cadfe67e-7187-472e-8bf4-8a2aded84e4e/phial-engine.md` == `03_VAULT/Knights/phials/inspira_phial.md`
- `vfs/notebooks/cadfe67e-7187-472e-8bf4-8a2aded84e4e/soul.md` == `03_VAULT/Knights/souls/inspira_soul.md`
- `vfs/notebooks/cadfe67e-7187-472e-8bf4-8a2aded84e4e/spark.md` == `03_VAULT/Knights/sparks/inspira_spark.md`
- `vfs/notebooks/cbb310bd-987e-4b84-bf45-12d37d090bec/phial-engine.md` == `03_VAULT/Knights/phials/arthur_omega_phial.md`
- `vfs/notebooks/cbb310bd-987e-4b84-bf45-12d37d090bec/soul.md` == `03_VAULT/Knights/souls/arthur_omega_soul.md`
- `vfs/notebooks/cbb310bd-987e-4b84-bf45-12d37d090bec/spark.md` == `03_VAULT/Knights/sparks/arthur_omega_spark.md`
- `vfs/notebooks/cbbb0c32-3919-4b77-9158-1d9f9ebf359f/phial-engine.md` == `03_VAULT/Knights/phials/bifrost_phial.md`
- `vfs/notebooks/cbbb0c32-3919-4b77-9158-1d9f9ebf359f/soul.md` == `03_VAULT/Knights/souls/bifrost_soul.md`
- `vfs/notebooks/cbbb0c32-3919-4b77-9158-1d9f9ebf359f/spark.md` == `03_VAULT/Knights/sparks/bifrost_spark.md`
- `vfs/notebooks/d6bdd57c-84d2-4e24-bb10-ad1fd179fb04/phial-engine.md` == `03_VAULT/Knights/phials/sir_alchemist_phial.md`
- `vfs/notebooks/d6bdd57c-84d2-4e24-bb10-ad1fd179fb04/soul.md` == `03_VAULT/Knights/souls/sir_alchemist_soul.md`
- `vfs/notebooks/d6bdd57c-84d2-4e24-bb10-ad1fd179fb04/spark.md` == `03_VAULT/Knights/sparks/sir_alchemist_spark.md`
- `vfs/notebooks/d8dd1669-aef4-4c34-8c44-d9cc5e51e0c9/phial-engine.md` == `03_VAULT/Knights/phials/sir_lancelot_phial.md`
- `vfs/notebooks/d8dd1669-aef4-4c34-8c44-d9cc5e51e0c9/soul.md` == `03_VAULT/Knights/souls/sir_lancelot_soul.md`
- `vfs/notebooks/d8dd1669-aef4-4c34-8c44-d9cc5e51e0c9/spark.md` == `03_VAULT/Knights/sparks/sir_lancelot_spark.md`
- `vfs/notebooks/e0110853-14ef-403f-8def-bf3a5123986f/phial-engine.md` == `03_VAULT/Knights/phials/sir_galahad_phial.md`
- `vfs/notebooks/e0110853-14ef-403f-8def-bf3a5123986f/soul.md` == `03_VAULT/Knights/souls/sir_galahad_soul.md`
- `vfs/notebooks/e0110853-14ef-403f-8def-bf3a5123986f/spark.md` == `03_VAULT/Knights/sparks/sir_galahad_spark.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/Master_Compendium.md` == `vfs/notebooks/e9fcbbbc-cd43-4b2d-a437-b2570267a0a9/Master_Compendium.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/phial-engine.md` == `03_VAULT/Knights/phials/sir_alex_phial.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/soul.md` == `03_VAULT/Knights/souls/sir_alex_soul.md`
- `vfs/notebooks/f490c05e-d8c4-4008-87e1-5f901bf57c6a/spark.md` == `03_VAULT/Knights/sparks/sir_alex_spark.md`
- `vfs/notebooks/f6466e10-d1b1-4904-9f87-081d031b0595/Master_Compendium.md` == `vfs/notebooks/378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f/Master_Compendium.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/Master_Compendium.md` == `vfs/notebooks/da2e51db-780a-48cf-a40a-4f0f65ff9295/Master_Compendium.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/phial-engine.md` == `03_VAULT/Knights/phials/sir_boris_phial.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/soul.md` == `03_VAULT/Knights/souls/sir_boris_soul.md`
- `vfs/notebooks/f7707daa-2d10-4db8-8fda-be4661a27793/spark.md` == `03_VAULT/Knights/sparks/sir_boris_spark.md`
- `vfs/notebooks/fdc42a4a-3060-4eac-b57c-8e6009ed634a/phial-engine.md` == `03_VAULT/Knights/phials/sir_debug_phial.md`
- `vfs/notebooks/fdc42a4a-3060-4eac-b57c-8e6009ed634a/soul.md` == `03_VAULT/Knights/souls/sir_debug_soul.md`
- `vfs/notebooks/fdc42a4a-3060-4eac-b57c-8e6009ed634a/spark.md` == `03_VAULT/Knights/sparks/sir_debug_spark.md`
- `vfs/roster.yaml` == `03_VAULT/training/configs/knight_character_sheets.yaml`
- `vfs/swarms/crawlers/crawler_blueprint.json` == `03_VAULT/runtime_state/scrapy_ecosystem_assimilation_crystal.json`
- `vfs/swarms/forges/raven_harness_blueprint.json` == `03_VAULT/runtime_state/raven_assimilation_crystal.json`

## SWEEP candidates that are prefix-only FALSE POSITIVES

These share their first 128 bytes with the owner but differ afterwards —
they must NOT be treated as duplicates.

- `01_KERNEL/EXCALIBUR/config/mcp_servers.json` — shares header with `01_KERNEL/EXCALIBUR/config/mcp_registry.json`, content differs
- `01_KERNEL/EXCALIBUR/config/validate_schema.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/EXCALIBUR/excalibur_autopilot.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/EXCALIBUR/main.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/graphs/tools.py`, content differs
- `01_KERNEL/EXCALIBUR/system/camelot_shell.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/EXCALIBUR/system/gradio_app.py` — shares header with `01_KERNEL/EXCALIBUR/core/excalibur.py`, content differs
- `01_KERNEL/EXCALIBUR/system/test_antigravity.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/auth.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/command_service.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/main.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/models.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/notes_service.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/notebook_service.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/podcast_service.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/chat.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/commands.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/config.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/embedding.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/embedding_rebuild.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/episode_profiles.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/insights.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/models.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/notebooks.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/notes.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/settings.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/source_chat.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/sources.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/speaker_profiles.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Memory_Squire/routers/transformations.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/auth.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/command_service.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/main.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/models.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/notes_service.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/notebook_service.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/podcast_service.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/chat.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/commands.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/config.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/embedding.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/embedding_rebuild.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/episode_profiles.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/insights.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/models.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/notebooks.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/notes.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/settings.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/context.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/source_chat.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/sources.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/speaker_profiles.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/transformations.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/commands/embedding_commands.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/Squires/commands/example_commands.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/commands/podcast_commands.py` — shares header with `01_KERNEL/agora/context.py`, content differs
- `01_KERNEL/agora/Squires/commands/source_commands.py` — shares header with `01_KERNEL/agora/context.py`, content differs
- `01_KERNEL/agora/Squires/ignite_notebook.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/config.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/database/migrate.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/database/repository.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/domain/content_settings.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/domain/models.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/domain/notebook.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/domain/podcast.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/domain/transformation.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/graphs/chat.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/graphs/prompt.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/graphs/source.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/graphs/ask.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/graphs/source_chat.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/Squires/open_notebook/plugins/podcasts.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/agora/cloud_orchestrator_shim/long_term_cloudbrain.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/agora/cloud_orchestrator_shim/modal_services.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/agora/hud_bridge.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/knights/notebook_knight.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/agora/knights/omni_knight.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/orchestration/think_tank.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/agora/persona/persona_extractor.py` — shares header with `01_KERNEL/agora/persona/persona_engine.py`, content differs
- `01_KERNEL/agora/pkg/evolution/chrysalis.go` — shares header with `01_KERNEL/agora/pkg/brain/ukg_schema.go`, content differs
- `01_KERNEL/agora/protocol.py` — shares header with `01_KERNEL/agora/context.py`, content differs
- `01_KERNEL/agora/swarms/hivemind/main.go` — shares header with `01_KERNEL/agora/pkg/brain/ukg_schema.go`, content differs
- `01_KERNEL/agora/swarms/local_intelligence_swarm.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/swarms/vision_swarm.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/agora/videneptus.py` — shares header with `01_KERNEL/agora/bridge.py`, content differs
- `01_KERNEL/agora/war_room_protocol.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/assimilation/core/handlers.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/forge/assimilation/core/parser.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/assimilation/core/registry.py` — shares header with `01_KERNEL/agora/models/proteus_vector.py`, content differs
- `01_KERNEL/forge/assimilation/core/reporting.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/assimilation/core/types.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/forge/assimilation/core/verification.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/forge/assimilation/tests/manual_test_harmony.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/assimilation/tests/test_integration.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/exp/sim_constitutional_safety.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/exp/sim_council_debate.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/exp/sim_engine_actuation.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/exp/sim_excalibur_bridge.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/exp/sim_grand_development.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/exp/sim_notebook_knight.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/exp/sim_oracle.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/exp/sim_oracle_plan_test.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/exp/sim_planning_engine.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/exp/sim_routing.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/exp/verify_all_engines.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/internal/defense/memory_monitor.go` — shares header with `01_KERNEL/agora/pkg/brain/ukg_schema.go`, content differs
- `01_KERNEL/forge/internal/kinetic/cribo_wrapper.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `01_KERNEL/forge/internal/morgana/router.go` — shares header with `01_KERNEL/agora/pkg/brain/ukg_schema.go`, content differs
- `01_KERNEL/forge/nano_forge/mission_dag.py` — shares header with `01_KERNEL/agora/models/proteus_vector.py`, content differs
- `01_KERNEL/forge/nano_forge/nano_forge.py` — shares header with `01_KERNEL/agora/swarms/scout_swarm_prime.py`, content differs
- `01_KERNEL/forge/nano_forge/phantom_grid.py` — shares header with `01_KERNEL/agora/swarms/perplexity/scout_sonar.py`, content differs
- `01_KERNEL/forge/nano_forge/templates/CAMELOT_APEX_SYSTEM_PROMPT.md` — shares header with `01_KERNEL/EXCALIBUR/config/CAMELOT_APEX_SYSTEM_PROMPT.md`, content differs
- `01_KERNEL/forge/rename_project.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/forge/scripts/diagnostics.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/fetch_local_model.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/fix_encoding_build.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/inspect_rustdesk_db.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/knight_swarm_manager.py` — shares header with `01_KERNEL/agora/bridge.py`, content differs
- `01_KERNEL/forge/scripts/live_swarm_audit.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/scripts/nano_cli_auditor.py` — shares header with `01_KERNEL/forge/assimilation/__main__.py`, content differs
- `01_KERNEL/forge/scripts/omega_audit.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/predictive_mission_sim.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/scripts/rapid_assimilate.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/scripts/ready_puter.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/scripts/setup_kobold.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/setup_openvoice.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/setup_phase4_configs.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/scripts/setup_piper.py` — shares header with `01_KERNEL/agora/swarms/piper_tts.py`, content differs
- `01_KERNEL/forge/scripts/setup_training.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/setup_voice_stack.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/tainted_cleanup.py` — shares header with `01_KERNEL/forge/assimilation/__main__.py`, content differs
- `01_KERNEL/forge/scripts/test_hive_swarm.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/scripts/test_kokoro.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/trigger_sync.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/forge/scripts/verify_docs.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/scripts/verify_mcp_hub.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/forge/tools/analytics_engine.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/forge/tools/conductor.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/forge/tools/ingest_dropzone.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/tools/ledger_commit.py` — shares header with `01_KERNEL/forge/scripts/verify_cloud.py`, content differs
- `01_KERNEL/forge/tools/morgana_logger.py` — shares header with `01_KERNEL/forge/scripts/verify_cloud.py`, content differs
- `01_KERNEL/forge/tools/status_reporter.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/forge/tools/swarm_tools_v2.py` — shares header with `01_KERNEL/agora/swarms/swarm_controller.py`, content differs
- `01_KERNEL/forge/tools/verification_matrix.py` — shares header with `01_KERNEL/forge/tools/prod_validator.py`, content differs
- `01_KERNEL/forge/update_map.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/defense_grid.py` — shares header with `01_KERNEL/agora/swarms/scout_swarm_prime.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/knights/__init__.py` — shares header with `01_KERNEL/agora/swarms/perplexity/scout_sonar.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/knights/castor.py` — shares header with `01_KERNEL/forge/modal_cloud.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/knights/heimdall.py` — shares header with `01_KERNEL/iron_gate/DEFENSE_GRID/knights/galahad.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/knights/kronos.py` — shares header with `01_KERNEL/forge/modal_cloud.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/knights/octavian.py` — shares header with `01_KERNEL/forge/modal_cloud.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/knights/sentinel.py` — shares header with `01_KERNEL/forge/modal_cloud.py`, content differs
- `01_KERNEL/iron_gate/DEFENSE_GRID/sit_loop.py` — shares header with `01_KERNEL/forge/modal_cloud.py`, content differs
- `01_KERNEL/iron_gate/__init__.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/iron_gate/forensic_engine.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/iron_gate/gates/zenith_exp_gate.py` — shares header with `01_KERNEL/forge/exp/calculator.py`, content differs
- `01_KERNEL/iron_gate/judge/__init__.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/iron_gate/judge/governance_audit.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/iron_gate/judge/rubric.py` — shares header with `01_KERNEL/iron_gate/judge/llm_judge.py`, content differs
- `01_KERNEL/iron_gate/security/audit_wrapper.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/iron_gate/security/biological_isolation.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/iron_gate/security/enforcer.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/iron_gate/security/hermes.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/iron_gate/security/identity_decay.py` — shares header with `01_KERNEL/EXCALIBUR/system/culture_bias.py`, content differs
- `01_KERNEL/iron_gate/security/iron_gate.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/iron_gate/security/killswitch_controller.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/iron_gate/security/reforge_identity.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/iron_gate/security/scan_secrets.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/iron_gate/security/vault_keeper.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/iron_gate/security/zenith_scanner.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/domain/base.py`, content differs
- `01_KERNEL/iron_gate/test_forensics.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/__init__.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/agent_memory.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/chunk_kv.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/hydration_manager.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/local_store.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/mempalace_l2.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/test_hydration.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/memory/test_mnemosyne.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/merlin/Engines/coherence_engine.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/__version__.py` — shares header with `01_KERNEL/merlin/Engines/crawl4ai/hub.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/async_database.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/async_dispatcher.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/async_logger.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/async_webcrawler.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/browser_manager.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/cache_context.py` — shares header with `01_KERNEL/EXCALIBUR/schemas/anya_constrict.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/chunking_strategy.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/domain/base.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/cli.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/config.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/content_filter_strategy.py` — shares header with `01_KERNEL/forge/scripts/verify_cloud.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/content_scraping_strategy.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/crawlers/google_search/crawler.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/deep_crawling/base_strategy.py` — shares header with `01_KERNEL/merlin/Engines/crawl4ai/async_crawler_strategy.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/deep_crawling/crazy.py` — shares header with `01_KERNEL/merlin/Engines/crawl4ai/async_crawler_strategy.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/deep_crawling/filters.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/docker_client.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/extraction_strategy.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/html2text/cli.py` — shares header with `01_KERNEL/forge/assimilation/__main__.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/html2text/config.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/domain/base.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/html2text/elements.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/install.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/js_snippet/__init__.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/legacy/cli.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/legacy/crawler_strategy.py` — shares header with `01_KERNEL/EXCALIBUR/proxy/bridge.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/legacy/database.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/legacy/web_crawler.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/markdown_generation_strategy.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/domain/base.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/migrations.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/model_loader.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/processors/pdf/__init__.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/processors/pdf/processor.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/processors/pdf/utils.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/domain/base.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/proxy_strategy.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/types.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/user_agent_generator.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/Engines/crawl4ai/utils.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/Engines/symbolect_transpiler/symbolect.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/domain/base.py`, content differs
- `01_KERNEL/merlin/context/test_cep.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `01_KERNEL/merlin/deep_dive_auditor.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/merlin/fusion/merger_engine.py` — shares header with `01_KERNEL/merlin/fusion/capability_graph.py`, content differs
- `01_KERNEL/merlin/fusion/strategies.py` — shares header with `01_KERNEL/merlin/fusion/fusion_router.py`, content differs
- `01_KERNEL/merlin/intelligence/voice_commander.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/merlin/reasoning/aurora_v_jepa.py` — shares header with `01_KERNEL/merlin/reasoning/aurora_vision.py`, content differs
- `01_KERNEL/merlin/reasoning/core.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/merlin/reasoning/council_debate.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/reasoning/omega_learn.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/reasoning/planning_engine.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/reasoning/search.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/merlin/reasoning/titan_forge.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/merlin/reasoning/veritas_audit.py` — shares header with `01_KERNEL/agora/Squires/open_notebook/domain/base.py`, content differs
- `01_KERNEL/merlin/repo_analyzer.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/merlin/rune_phases/experience_check.py` — shares header with `01_KERNEL/forge/exp/calculator.py`, content differs
- `01_KERNEL/merlin/rune_phases/graph_traverse.py` — shares header with `01_KERNEL/forge/exp/calculator.py`, content differs
- `01_KERNEL/merlin/rune_phases/lightrag_retrieve.py` — shares header with `01_KERNEL/forge/exp/calculator.py`, content differs
- `01_KERNEL/ml_persona_engineer/quantization.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/__init__.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/colibri_moe_streamer.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/core.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/deer_research_flow.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/hermes_moa_loop.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/ornith_engine.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/ouroboros_bridge.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/reasoning/ouroboros_loop_starter.py` — shares header with `01_KERNEL/audit_redact.py`, content differs
- `01_KERNEL/reasoning/rlm_engine.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/security/__init__.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/security/zenith_scanner.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/audio/audio_session.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/audio/kitten_service.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/audio/silero_vad.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/audio/sir_sonus.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/audio/vad_interrupt.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/boris_interface.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/connectivity/bridges/clawdbot_client.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/senses/helio_distiller.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/integrations/ollama_client.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/integrations/test_ollama.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/learning/dataset_collector.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/senses/learning/dataset_generator.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/senses/learning/omega_trainer.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/senses/morgana_edge.py` — shares header with `01_KERNEL/merlin/reasoning/oracle_physics.py`, content differs
- `01_KERNEL/senses/train/fine_tune_unsloth.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/senses/train/prep_data.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/swarm/graph_orchestrator.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/swarm/omx_primitives.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/swarm/test_graph.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/system/GENESIS_BOOT.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/system/SYNC_PROTOCOL.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/tests/debug_lac.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/tests/simulate_chrysalis.py` — shares header with `01_KERNEL/agora/context.py`, content differs
- `01_KERNEL/tests/test_api.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/tests/test_api_fusion.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `01_KERNEL/tests/test_beaver.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/tests/test_clawdbot_bridge.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/tests/test_extension_bridge.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/tests/test_helix.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/tests/test_hybrid_routing.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/tests/test_iron_gate_flow.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/tests/test_lac_loop.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/tests/test_merger.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `01_KERNEL/tests/test_ouroboros_bridge.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/tests/test_phantom_handoff.py` — shares header with `01_KERNEL/agora/swarm_controller.py`, content differs
- `01_KERNEL/tests/test_seeder.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `01_KERNEL/titan/memory/anya_memory.py` — shares header with `01_KERNEL/agora/router.py`, content differs
- `01_KERNEL/titan/memory/appwrite_sync.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/titan/memory/base_memory.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/titan/memory/compiler.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/titan/memory/constrict_pipeline.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/titan/memory/notebook_manager.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `01_KERNEL/titan/memory/reflection_engine.py` — shares header with `01_KERNEL/iron_gate/security/warden.py`, content differs
- `01_KERNEL/titan/memory/requirements.txt` — shares header with `01_KERNEL/requirements.txt`, content differs
- `01_KERNEL/titan/memory/seeder.py` — shares header with `01_KERNEL/titan/Data_Pipeline/storage.py`, content differs
- `01_KERNEL/titan/memory/sync_engine.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `01_KERNEL/titan/memory/test_titan_omega.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `01_KERNEL/titan/memory/titan_omega.py` — shares header with `01_KERNEL/titan/Data_Pipeline/storage.py`, content differs
- `01_KERNEL/titan/memory/titan_schemas.py` — shares header with `01_KERNEL/titan/Data_Pipeline/storage.py`, content differs
- `01_KERNEL/titan/storage/code_migrator.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `01_KERNEL/titan/storage/exp_ledger.py` — shares header with `01_KERNEL/merlin/rag/lightrag_engine.py`, content differs
- `01_KERNEL/titan/sync_engine.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/src/components/engine/useScript.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/src/features/brain/KokoroEngine.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/src/features/brain/engineStore.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/src/lib/utils.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/src/test/setup.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/vite.config.ts` — shares header with `01_KERNEL/EXCALIBUR/BRIDGE/GENKIT/genkit.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/vitest.config.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Modal/bridge.py` — shares header with `01_KERNEL/forge/modal_cloud.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/excalibur-resonance/lib/utils.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Modal/excalibur-resonance/v0-quantum-cinematic-engine/lib/utils.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/Modal/excalibur-resonance/v0-quantum-cinematic-engine/pnpm-lock.yaml` — shares header with `02_FORGE/dyad-apps/invoice-generator/pnpm-lock.yaml`, content differs
- `02_FORGE/PORTAL_CORE/Modal/get_started.py` — shares header with `01_KERNEL/merlin/sky_engine.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/kinetic_fortress.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_172005/morgana_core.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_180343/morgana_core.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_183443/morgana_core.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_genesis_v92.py` — shares header with `01_KERNEL/agora/Squires/Memory_Squire/routers/search.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_genesis_v93_patched.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_v94_fastapi.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_v94_remote.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/morgana_core.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/morgana_staging.py` — shares header with `01_KERNEL/agora/knights/opencode_knight.py`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/templates/MorganaAvatar.tsx` — shares header with `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_172005/components_3d_MorganaAvatar.tsx`, content differs
- `02_FORGE/PORTAL_CORE/Modal/morgana/templates/morgana_core.py` — shares header with `01_KERNEL/agora/brain_worker.py`, content differs
- `02_FORGE/PORTAL_CORE/package-lock.json` — shares header with `02_FORGE/package-lock.json`, content differs
- `02_FORGE/PORTAL_CORE/src/hooks/useCamelotNetwork.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/src/hooks/useFireTrail.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/src/lib/utils.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/vite.config.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/web/app/api/livekit-token/route.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/PORTAL_CORE/web/app/layout.tsx` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/src/app/layout.tsx`, content differs
- `02_FORGE/PORTAL_CORE/web/next.config.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/apps/anya-lyte/src/titanLinkClient.ts` — shares header with `01_KERNEL/EXCALIBUR/BRIDGE/GENKIT/genkit.config.ts`, content differs
- `02_FORGE/apps/headartworks/sections/footer-group.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/sections/header-group.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/404.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/article.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/blog.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/cart.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/collection.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/customers/account.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/customers/activate_account.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/customers/addresses.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/customers/login.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/customers/order.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/customers/register.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/customers/reset_password.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/index.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/list-collections.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/page.about.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/page.candles-2.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/page.candles-page.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/page.collections.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/page.coming-soon.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/page.contact.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/page.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/password.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/product.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/apps/headartworks/templates/search.json` — shares header with `02_FORGE/apps/headartworks/config/settings_data.json`, content differs
- `02_FORGE/cartridge/cartridge_cli.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/cartridge_crypto.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/cartridge_rbac.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/cartridge_schemas.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/cartridge_trust.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/cartridge_v2_adapter.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/fabrication_engine.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/packages/CREATIVE_CORE/persona.py` — shares header with `02_FORGE/cartridge/packages/CLOUD_FLUX/persona.py`, content differs
- `02_FORGE/cartridge/packages/OPERATIONS_CORE/persona.py` — shares header with `02_FORGE/cartridge/packages/CLOUD_FLUX/persona.py`, content differs
- `02_FORGE/cartridge/packages/STRATEGY_CORE/persona.py` — shares header with `02_FORGE/cartridge/packages/CLOUD_FLUX/persona.py`, content differs
- `02_FORGE/cartridge/packages/SYNTAX_GUARD/persona.py` — shares header with `02_FORGE/cartridge/packages/CLOUD_FLUX/persona.py`, content differs
- `02_FORGE/cartridge/sandbox.py` — shares header with `02_FORGE/cartridge/cartridge_archive.py`, content differs
- `02_FORGE/cartridge/test_bifrost_bridge.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `02_FORGE/cartridge/test_fabrication.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `02_FORGE/cartridge/test_rbac.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `02_FORGE/cartridge/test_sandbox.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `02_FORGE/cartridge/test_trust.py` — shares header with `01_KERNEL/iron_gate/judge/test_judge.py`, content differs
- `02_FORGE/dyad-apps/happy-owl-dart/src/components/ui/badge.tsx` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/src/components/ui/alert.tsx`, content differs
- `02_FORGE/dyad-apps/happy-owl-dart/tsconfig.json` — shares header with `02_FORGE/apps/i2l-phygital/tsconfig.json`, content differs
- `02_FORGE/dyad-apps/invoice-generator/src/app/manual-entry/page.tsx` — shares header with `02_FORGE/dyad-apps/invoice-generator/src/app/ai-review/page.tsx`, content differs
- `02_FORGE/dyad-apps/invoice-generator/src/components/ui/button.tsx` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/src/components/ui/button.tsx`, content differs
- `02_FORGE/dyad-apps/invoice-generator/src/components/ui/card.tsx` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/src/components/ui/card.tsx`, content differs
- `02_FORGE/dyad-apps/invoice-generator/src/components/ui/label.tsx` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/src/components/ui/label.tsx`, content differs
- `02_FORGE/holotable/next-env.d.ts` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/next-env.d.ts`, content differs
- `02_FORGE/holotable/tsconfig.json` — shares header with `02_FORGE/apps/i2l-phygital/tsconfig.json`, content differs
- `02_FORGE/kinetic/contracts/Cargo.toml` — shares header with `02_FORGE/kinetic/actor/Cargo.toml`, content differs
- `02_FORGE/kinetic/daily_maintenance.py` — shares header with `01_KERNEL/iron_gate/security/warden.py`, content differs
- `02_FORGE/kinetic/hephaestus/src/main.rs` — shares header with `02_FORGE/kinetic/hephaestus/src/lib.rs`, content differs
- `02_FORGE/kinetic/merlin_dispatch.py` — shares header with `01_KERNEL/EXCALIBUR/system/MENTOR.py`, content differs
- `02_FORGE/kinetic/omni_nexus_ide/Cargo.toml` — shares header with `02_FORGE/kinetic/actor/Cargo.toml`, content differs
- `02_FORGE/kinetic/titan_architect.py` — shares header with `01_KERNEL/iron_gate/security/warden.py`, content differs
- `02_FORGE/kinetic/titan_triage.py` — shares header with `02_FORGE/kinetic/titan_grader.py`, content differs
- `02_FORGE/packages/anya-domain/src/index.ts` — shares header with `02_FORGE/holotable/lib/api.ts`, content differs
- `02_FORGE/packages/anya-domain/src/titanLink.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/packages/anya-domain/src/types.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/packages/anya-lyte/src/api/titanlink_client.ts` — shares header with `02_FORGE/packages/anya-domain/src/rustdesk.ts`, content differs
- `02_FORGE/packages/anya-lyte/src/db/schema.ts` — shares header with `02_FORGE/holotable/next.config.ts`, content differs
- `02_FORGE/packages/pocket-squire/app/layout.tsx` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/src/app/layout.tsx`, content differs
- `02_FORGE/packages/pocket-squire/src/lib/kernel-bridge.ts` — shares header with `02_FORGE/holotable/lib/api.ts`, content differs
- `02_FORGE/packages/pocket-squire/tsconfig.json` — shares header with `02_FORGE/apps/i2l-phygital/tsconfig.json`, content differs
- `02_FORGE/pocket_squire/next-env.d.ts` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/next-env.d.ts`, content differs
- `02_FORGE/scrcpy/app/deps/adb_macos.sh` — shares header with `02_FORGE/scrcpy/app/deps/adb_linux.sh`, content differs
- `02_FORGE/scrcpy/app/deps/adb_windows.sh` — shares header with `02_FORGE/scrcpy/app/deps/adb_linux.sh`, content differs
- `02_FORGE/scrcpy/release/build_macos.sh` — shares header with `02_FORGE/scrcpy/release/build_linux.sh`, content differs
- `02_FORGE/scrcpy/release/test_server.sh` — shares header with `02_FORGE/scrcpy/release/build_server.sh`, content differs
- `02_FORGE/tools/pi-mono/packages/agent/test/harness/skills.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/prompt-templates.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/agent/test/utils/get-current-time.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/utils/calculate.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-thinking-disable.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-opus-4-7-smoke.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/fireworks-models.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-eager-tool-input-compat.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/google-shared-image-tool-result-routing.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/google-shared-gemini3-unsigned-tool-call.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/google-thinking-disable.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-opus-4-7-smoke.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/interleaved-thinking.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-eager-tool-input-e2e.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/mistral-reasoning-mode.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-opus-4-7-smoke.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/mistral-tool-schema.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-tool-name-normalization.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/openai-codex-cache-affinity-e2e.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/empty.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/openai-completions-prompt-cache.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/azure-openai-base-url.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/openai-completions-tool-choice.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/openai-completions-cache-control-format.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/openai-responses-cache-affinity-e2e.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/empty.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/openai-responses-reasoning-replay-e2e.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-tool-name-normalization.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/openai-responses-tool-result-images.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/images.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/responseid.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/empty.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/tool-call-without-result.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-tool-name-normalization.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/unicode-surrogate.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/anthropic-tool-name-normalization.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/test/xhigh.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/ai/test/tokens.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/ai/tsconfig.build.json` — shares header with `02_FORGE/tools/pi-mono/packages/agent/tsconfig.build.json`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/README.md` — shares header with `02_FORGE/tools/pi-mono/README.md`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/core/compaction/branch-summarization.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/src/harness/compaction/branch-summarization.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/core/compaction/compaction.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/src/harness/compaction/compaction.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/core/tools/grep.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/src/core/tools/find.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/core/tools/output-accumulator.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/src/harness/utils/shell-output.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/modes/interactive/theme/dark.json` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/examples/extensions/dynamic-resources/dynamic.json`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/src/modes/interactive/theme/light.json` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/examples/extensions/dynamic-resources/dynamic.json`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/agent-session-auto-compaction-queue.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/agent-session-dynamic-provider.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/agent-session-dynamic-tools.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/agent-session-retry.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/agent-session-runtime-events.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/edit-tool-no-full-redraw.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/edit-tool-legacy-input.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/interactive-mode-compaction.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/interactive-mode-anthropic-warning.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/model-registry.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/auth-storage.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/rpc-prompt-response-semantics.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/sdk-openrouter-attribution.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/sdk-skills.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/image-resize-callers.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/session-cwd.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/image-resize-callers.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/agent-session-prompt.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/image-resize-callers.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/agent-session-runtime.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/sdk-session-manager.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/2023-queued-slash-command-followup.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/agent-session-queue.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/2781-skill-collision-precedence.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/image-resize-callers.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/2835-tools-allowlist-filters-extension-tools.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/2860-replaced-session-context.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/3303-find-nested-gitignore.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/3302-find-path-glob.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/3592-no-builtin-tools-keeps-extension-tools.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/3616-settings-inmemory-reload.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/agent/test/harness/session-test-utils.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/3982-message-end-cost-override.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/coding-agent/test/suite/regressions/3317-network-connection-lost-retry.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/coding-agent/tsconfig.build.json` — shares header with `02_FORGE/tools/pi-mono/packages/agent/tsconfig.build.json`, content differs
- `02_FORGE/tools/pi-mono/packages/tui/test/tui-render.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/tui/test/tui-overlay-style-leak.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/tui/test/wrap-ansi.test.ts` — shares header with `02_FORGE/tools/pi-mono/packages/tui/test/regression-regional-indicator-width.test.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/tui/tsconfig.build.json` — shares header with `02_FORGE/tools/pi-mono/packages/agent/tsconfig.build.json`, content differs
- `02_FORGE/tools/pi-mono/packages/web-ui/CHANGELOG.md` — shares header with `02_FORGE/tools/pi-mono/packages/agent/CHANGELOG.md`, content differs
- `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/GenericArtifact.ts` — shares header with `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/ExcelArtifact.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/ImageArtifact.ts` — shares header with `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/ExcelArtifact.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/MarkdownArtifact.ts` — shares header with `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/HtmlArtifact.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/PdfArtifact.ts` — shares header with `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/ExcelArtifact.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/TextArtifact.ts` — shares header with `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/artifacts/SvgArtifact.ts`, content differs
- `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/javascript-repl.ts` — shares header with `02_FORGE/tools/pi-mono/packages/web-ui/src/tools/extract-document.ts`, content differs
- `03_VAULT/00_SECURE_ARCHIVE/a347e580_forge.env.d.ts` — shares header with `02_FORGE/dyad-apps/happy-owl-dart/next-env.d.ts`, content differs
- `03_VAULT/Reference_Architectures/skills/goal-video-resources/02-ralph/00-repo-instructions-AGENTS.md` — shares header with `03_VAULT/Reference_Architectures/skills/goal-video-resources/01-goal/00-repo-instructions-AGENTS.md`, content differs
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/grill-me/SKILL.md` — shares header with `03_VAULT/Reference_Architectures/skills/mattpocock-skills/skills/productivity/grill-me/SKILL.md`, content differs
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/grill-me/SKILL.md` — shares header with `03_VAULT/Reference_Architectures/skills/mattpocock-skills/skills/productivity/grill-me/SKILL.md`, content differs
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/ralph/SKILL.md` — shares header with `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/ralph/SKILL.md`, content differs
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/ralph/prompt.md` — shares header with `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/ralph/prompt.md`, content differs
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/ralph/ralph-once.sh` — shares header with `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/ralph/ralph-once.sh`, content differs
- `03_VAULT/UKG/nodes/CLIProxyAPI_Assimilation_UKG.json` — shares header with `03_VAULT/UKG/nodes/Assimilation_Protocol_UKG.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_2.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_3.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_4.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_5.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_6.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_7.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_8.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/_manifest.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-39/_manifest.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_2.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_3.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_4.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_5.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_6.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_7.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_8.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-50/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-24-57/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/_manifest.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/_manifest.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-25-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-25-16/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_2.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_3.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_4.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_5.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_6.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_7.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_8.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/_manifest.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/_manifest.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_2.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_3.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_4.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_5.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_6.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_7.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_8.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-42/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/_manifest.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/_manifest.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_2.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_3.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_4.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_5.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_6.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_7.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_8.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-34-59/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/_manifest.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-33-52/_manifest.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_2.json` — shares header with `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_3.json` — shares header with `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_4.json` — shares header with `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_5.json` — shares header with `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_6.json` — shares header with `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_7.json` — shares header with `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_1.json`, content differs
- `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_8.json` — shares header with `03_VAULT/runtime_state/2026-08-14T15-02-55/self_test_1.json`, content differs
- `03_VAULT/runtime_state/nano_swarm_generated/Node_A_Frontend/source/rollback.json` — shares header with `03_VAULT/runtime_state/nano_swarm_generated/Node_A_Frontend/rollback.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-14/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-36-47/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T14-37-05/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-07/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-11/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-14/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-16/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-19/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-40/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-43/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-46/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-48/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-32-51/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-53-08/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-54-53/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-08/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-23/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-40/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-43/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-45/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-48/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T15-29-56/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T15-56-50/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T16-53-51/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-14T21-24-11/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T14-35-16/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-19T01-57-34/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-23T14-19-40/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T05-07-49/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T05-07-49/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T05-07-49/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T05-07-49/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T05-07-49/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T05-07-49/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T05-07-49/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-33-59/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-18/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T12-36-54/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-03-40/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/northstar_brief_currency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-04-17/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/lattice_yaml_consistency.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/provenance_ledger_writable.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/tool_registry_presence.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-23-11/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/2026-08-14T14-24-57/vfs_scaffold_integrity.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T13-24-29/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T13-24-10/port_readiness_scan.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-25T22-57-03/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-25T05-06-13/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T01-01-21/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T14-59-21/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T15-04-25/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-08/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-43-36/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T20-44-58/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-28T22-43-16/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-28T00-57-33/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-29T01-47-51/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-27-47/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-28-53/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-30-54/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T21-34-35/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-02-35/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-14-08/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T22-17-18/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-08-31T23-59-51/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-31T14-57-10/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-24/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-01T00-01-49/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-01T00-01-06/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T01-45-47/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-03T16-41-33/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-03T01-44-55/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T17-44-15/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-34-03/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-35-11/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T21-36-01/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-04T22-02-44/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-04T03-19-59/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-06T16-25-35/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-08T07-55-30/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-08T07-55-03/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T07-57-25/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-50-57/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T08-51-16/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-09T13-42-42/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-09T07-56-37/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T21-59-44/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-10T22-26-56/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-10T14-57-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-20/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-05-59/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-06-36/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-08-42/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-12-09/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-31-53/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-33-48/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-35-07/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-36-17/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-36-17/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-36-17/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T03-37-21/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T04-05-23/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-13T07-16-52/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-13T03-03-25/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-14T20-21-38/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-14T16-58-23/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-15T17-45-34/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-15T05-34-28/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-11-39/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-17T16-13-24/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-17T15-07-09/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T10-15-59/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-07-35/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-08-30/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-19-45/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T13-23-58/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-55-16/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T14-56-04/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-09-09/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-11-12/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-45-15/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T15-53-04/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-00-16/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-03-38/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T16-08-40/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T17-47-18/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T17-47-32/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-19T23-49-41/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-19T10-13-48/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-46-50/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T16-47-31/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T17-02-24/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T16-27-35/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-20T18-51-19/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-20T00-16-31/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-21T23-14-14/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-21T19-03-35/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-21T23-14-29/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-21T19-03-35/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T07-23-50/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T13-01-17/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-50-35/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T17-54-41/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-22T18-15-36/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-22T07-23-07/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T02-44-28/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-30-06/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-36-17/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T12-53-26/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-02-52/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/_manifest.json` — shares header with `03_VAULT/runtime_state/preflight/2026-08-14T16-49-36/_manifest.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/env_dependency_match.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/foss_validation_constraints.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/lattice_yaml_consistency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/northstar_brief_currency.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/port_readiness_scan.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/foss_validation_constraints.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/provenance_ledger_writable.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/tool_registry_presence.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/preflight/2026-09-23T13-05-25/vfs_scaffold_integrity.json` — shares header with `03_VAULT/runtime_state/preflight/2026-09-23T02-41-57/env_dependency_match.json`, content differs
- `03_VAULT/runtime_state/pwa_cockpit_swarm_latest.json` — shares header with `03_VAULT/runtime_state/bio_swarm_runtime_latest.json`, content differs
- `03_VAULT/training/configs/hud.py` — shares header with `03_VAULT/runtime_state/backups/hiveide_cut_20260625T173845Z/hud.py`, content differs
- `03_VAULT/training/configs/kinetic_edge/mcp_server/src/turboquant.rs` — shares header with `03_VAULT/training/configs/kinetic_edge/mcp_server/src/ap2_settlement.rs`, content differs
- `03_VAULT/training/configs/kinetic_edge/mcp_server/src/wasi_nn.rs` — shares header with `03_VAULT/training/configs/kinetic_edge/mcp_server/src/ap2_settlement.rs`, content differs
- `03_VAULT/training/configs/requirements.txt` — shares header with `01_KERNEL/requirements.txt`, content differs
- `03_VAULT/vault_manager.py` — shares header with `01_KERNEL/merlin/merlin_omega.py`, content differs
- `Knights/Sir_Kay/phial-engine.md` — shares header with `03_VAULT/Knights/phials/sir_kay_phial.md`, content differs
- `apps/camelot-vps-hub/src/components/Interactive3DShowcase.tsx` — shares header with `apps/camelot-vps-hub/src/components/FixedThreeUiOverlay.tsx`, content differs
- `apps/excalibur-cmd-1/tsconfig.json` — shares header with `apps/camelot-vps-hub/tsconfig.json`, content differs
- `apps/mcp-query/tsconfig.json` — shares header with `apps/bifrost/tsconfig.json`, content differs
- `apps/pwa/tsconfig.json` — shares header with `02_FORGE/dyad-apps/invoice-generator/tsconfig.json`, content differs
- `bin/cloudbrain_hydrate.py` — shares header with `bin/cloudbrain_dedup.py`, content differs
- `bin/cloudbrain_snapshot.py` — shares header with `bin/cloudbrain_dedup.py`, content differs
- `bin/kba_drone_boot.sh` — shares header with `bin/appwrite_bootstrap.sh`, content differs
- `bin/worldtree_nav.py` — shares header with `bin/cloudbrain_dedup.py`, content differs
- `cartridges/system-ui/tailwind.config.js` — shares header with `02_FORGE/PORTAL_CORE/Anya_Dashboard/tailwind.config.js`, content differs
- `cartridges/vps-operator-console/internal/omarchy/manager.go` — shares header with `apps/camelot-vps-hub/apps/operator-console/internal/omarchy/manager.go`, content differs
- `cartridges/vps-operator-console/static/js/WorldTreeScene.js` — shares header with `apps/camelot-vps-hub/apps/operator-console/static/js/WorldTreeScene.js`, content differs
- `cmd/pulse/ops/TAILSCALE-KEY-MINT.md` — shares header with `02_FORGE/kinetic/vizio-router/cmd/pulse/ops/TAILSCALE-KEY-MINT.md`, content differs
- `control_plane/core/sir_socrates.py` — shares header with `01_KERNEL/senses/audio/sonus/compiler.py`, content differs
- `control_plane/dispatch/bifrost_gateway.py` — shares header with `02_FORGE/cartridge/bifrost_bridge.py`, content differs
- `control_plane/dispatch/bifrost_sandbox_adapter.py` — shares header with `02_FORGE/cartridge/bifrost_bridge.py`, content differs
- `control_plane/infra/cognitive_service.py` — shares header with `control_plane/cognitive_service.py`, content differs
- `control_plane/infra/colibri_bridge.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `control_plane/infra/dependency_engine.py` — shares header with `control_plane/infra/deerflow_sandbox.py`, content differs
- `control_plane/infra/jcode_memory_guard.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `control_plane/infra/lmcache_affinity_adapter.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `control_plane/infra/secret_manager.py` — shares header with `01_KERNEL/merlin/Engines/sentinel_compressor.py`, content differs
- `control_plane/infra/supabase_bridge.py` — shares header with `01_KERNEL/titan/memory/supermemory_adapter.py`, content differs
- `control_plane/runes/harness_emulator.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `control_plane/runes/omx_workflow_adapter.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `control_plane/runners/worldtree_vps_cloudbrain_sync.py` — shares header with `bin/cloudbrain_sync.py`, content differs
- `control_plane/test_drone_node.py` — shares header with `01_KERNEL/forge/scripts/test_integrations.py`, content differs
- `deploy/multivoice-router/firebase-blueprint.json` — shares header with `02_FORGE/apps/lux11/firebase-blueprint.json`, content differs
- `deploy/multivoice-router/server.ts` — shares header with `02_FORGE/apps/lux11/server.ts`, content differs
- `deploy/multivoice-router/src/components/CamelotKnightPicker.tsx` — shares header with `deploy/multivoice-router/src/components/CamelotCarousel.tsx`, content differs
- `deploy/multivoice-router/src/hooks/use-gemini-live.ts` — shares header with `02_FORGE/apps/lux11/src/hooks/use-gemini-live.ts`, content differs
- `deploy/multivoice-router/src/lib/audio-utils.ts` — shares header with `02_FORGE/apps/lux11/src/lib/audio-utils.ts`, content differs
- `deploy/multivoice-router/src/lib/firestore.ts` — shares header with `02_FORGE/apps/lux11/src/lib/firestore.ts`, content differs
- `deploy/multivoice-router/src/services/diagnosticService.ts` — shares header with `02_FORGE/apps/lux11/src/services/diagnosticService.ts`, content differs
- `docs/GEMINI.md` — shares header with `GEMINI.md`, content differs
- `docs/architecture/ARCH/KERNEL_ARCHITECTURE.md` — shares header with `01_KERNEL/ARCHITECTURE.md`, content differs
- `docs/catridges/2.txt` — shares header with `docs/catridges/!DOCTYPE html.txt`, content differs
- `docs/catridges/newsletter.txt` — shares header with `docs/catridges/New Text Document.txt`, content differs
- `docs/protocols/titan_protocol.md` — shares header with `01_KERNEL/protocols/titan_protocol.md`, content differs
- `kinetic_edge/saltare/cmd/saltare-mcp/main.go` — shares header with `01_KERNEL/agora/pkg/brain/ukg_schema.go`, content differs
- `kinetic_edge/saltare/cmd/saltare/main.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/analytics/collector.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/analytics/collector_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/codemode/executor.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/codemode/sandbox.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/codemode/sandbox_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/codemode/vmpool.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/directmode/breaker.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/directmode/breaker_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/directmode/client.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/directmode/pool.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/directmode/pool_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/execution/executor.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/cli/commands.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/http/handlers.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/http/middleware.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/http/server.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/mcp/http.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/mcp/server.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/mcp/server_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/gateway/mcp/stdio.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/jobs/jobs_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/jobs/manager.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/jobs/queue.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/jobs/sse.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/jobs/storage.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/jobs/types.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/providers/cerebras.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/providers/cerebras_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/providers/fallback.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/providers/ollama.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/providers/ollama_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/semantic/router.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/semantic/router_llm_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/semantic/router_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/router/soul/matrix.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/badger/db.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/badger/db_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/meilisearch/client.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/meilisearch/client_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/search/factory.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/search/interface.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/typesense/client.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/storage/typesense/client_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/toolkit/loader.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/toolkit/manager.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/version/version.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/internal/version/version_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/pkg/mcpclient/client.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/pkg/mcpclient/http_transport.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/pkg/mcpclient/stdio_transport.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/pkg/mcpclient/stdio_transport_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/pkg/mcpclient/transport.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/pkg/types/types.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/tests/integration/cerebras_llm_test.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/tests/mcp/mock_server.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `kinetic_edge/saltare/tests/mock/weather_server.go` — shares header with `01_KERNEL/forge/cmd/pulse/heartbeat.go`, content differs
- `packages/benchmark/tsconfig.json` — shares header with `apps/bifrost/tsconfig.json`, content differs
- `packages/db/tsconfig.json` — shares header with `apps/bifrost/tsconfig.json`, content differs
- `packages/multivoice-router/src/main.tsx` — shares header with `apps/camelot-vps-hub/src/main.tsx`, content differs
- `packages/multivoice-router/tsconfig.json` — shares header with `apps/camelot-vps-hub/tsconfig.json`, content differs
- `packages/multivoice-router/vite.config.ts` — shares header with `apps/camelot-vps-hub/vite.config.ts`, content differs
- `scripts/daily_system_tuneup.py` — shares header with `bin/tuneup.py`, content differs
- `scripts/run_swarm.sh` — shares header with `scripts/delete_branches_swarm.sh`, content differs
- `scripts/scan_secrets.py` — shares header with `observability/run_observability.py`, content differs
- `scripts/update_ledger_cartridge_audit.py` — shares header with `scripts/update_ledger_branch_audit.py`, content differs
- `scripts/update_ledger_dag.py` — shares header with `scripts/update_ledger_branch_audit.py`, content differs
- `scripts/update_ledger_implementation.py` — shares header with `scripts/update_ledger_branch_audit.py`, content differs
- `scripts/update_ledger_sync.py` — shares header with `scripts/update_ledger_branch_audit.py`, content differs
- `scripts/update_ledger_synthetos.py` — shares header with `scripts/update_ledger_branch_audit.py`, content differs
- `scripts/update_ledger_v702.py` — shares header with `scripts/update_ledger_sanitization.py`, content differs
- `scripts/update_omnivox_ledger.py` — shares header with `scripts/update_ledger_sanitization.py`, content differs
- `scripts/validate_cleanup.sh` — shares header with `scripts/delete_branches_swarm.sh`, content differs
- `scripts/verify_production_readiness.py` — shares header with `bin/verify_production.py`, content differs
- `src/router/policy.ts` — shares header with `02_FORGE/kinetic/vizio-router/src/router/policy.ts`, content differs
- `tests/control_plane/test_repo_assimilation_engine.py` — shares header with `tests/control_plane/test_camelot_vps_hub_deployment.py`, content differs
- `tests/test_colibri_moe.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `tests/test_crucible_and_heal.py` — shares header with `tests/test_camelot_vitals.py`, content differs
- `tests/test_deer_research.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `tests/test_expansion_modules.py` — shares header with `tests/test_camelot_vitals.py`, content differs
- `tests/test_hermes_moa.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `tests/test_inference_contract.py` — shares header with `tests/test_camelot_vitals.py`, content differs
- `tests/test_jcode_memory.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `tests/test_lmcache_affinity.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `tests/test_provenance_crypto.py` — shares header with `tests/test_ledger_audit.py`, content differs
- `tests/test_retention_hints.py` — shares header with `tests/test_affinity_routing.py`, content differs
- `tests/test_rlm_engine.py` — shares header with `01_KERNEL/directory_distiller.py`, content differs
- `tests/test_s26_audio_bridge.py` — shares header with `tests/test_camelot_vitals.py`, content differs
- `tests/test_secret_manager.py` — shares header with `tests/test_observability.py`, content differs
- `tests/test_slo_escape.py` — shares header with `tests/test_affinity_routing.py`, content differs
- `tests/test_tracing.py` — shares header with `tests/test_observability.py`, content differs
- `tests/test_wasmtime_runner.py` — shares header with `tests/test_camelot_vitals.py`, content differs
- `tests/test_worldtree_graph_sync.py` — shares header with `tests/test_camelot_vitals.py`, content differs
- `tools/arthurian-omni-forge/src/components/BlueprintStateMachine.tsx` — shares header with `tools/arthurian-omni-forge/src/components/BlueprintOSStudio.tsx`, content differs
- `tools/arthurian-omni-forge/src/main.tsx` — shares header with `deploy/multivoice-router/src/main.tsx`, content differs
- `tools/arthurian-omni-forge/tsconfig.json` — shares header with `02_FORGE/apps/lux11/tsconfig.json`, content differs
- `tools/arthurian-omni-forge/vite.config.ts` — shares header with `02_FORGE/apps/lux11/vite.config.ts`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/agency/supported_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/agency/supported_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/artifacts_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/artifacts_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/chat_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/chat_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/notebooks_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/notebooks_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/notes_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/notes_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/orchestration_service_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/orchestration_service_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/organization_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/organization_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/read_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/read_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/research_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/research_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/sources_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/sources_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/v1/source_settings_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/v1/source_settings_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/common/protos/common_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/common/protos/common_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/common/protos/metadata_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/common/protos/metadata_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/common/protos/provenance_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/common/protos/provenance_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/sharing/sharing_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/labs/language/tailwind/sharing/sharing_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/android/wire/v1/organization_mutations_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/android/wire/v1/organization_mutations_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/android/wire/v1/sharing_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/android/wire/v1/sharing_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/experiments/v1/exptsandconfigs_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/experiments/v1/exptsandconfigs_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/internal/android/wire/v1/artifacts_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/internal/android/wire/v1/artifacts_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/internal/android/wire/v1/notebooks_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/internal/android/wire/v1/notebooks_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/internal/android/wire/v1/source_content_pb2.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2.py`, content differs
- `tools/notebooklm-py/src/notebooklm/_android/proto/notebooklm/internal/android/wire/v1/source_content_pb2_grpc.py` — shares header with `tools/notebooklm-py/src/notebooklm/_android/proto/google/internal/labs/tailwind/orchestration/v1/account_pb2_grpc.py`, content differs
- `tools/notebooklm-py/tests/cassettes/android/artifact_copy_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/chat_session_control_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/collection_lifecycle_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/delete_chat_turns_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/generate_audio_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/generate_flashcards_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/generate_free_form_streamed_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/generate_notebook_guide_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/generate_report_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/generate_report_suggestions_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/get_labels_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/get_or_create_account_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/get_project_rich_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/label_lifecycle_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/list_artifacts_get_notes_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/list_chat_sessions_turns_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/list_discover_sources_job_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/load_source_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/mutate_account_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/next_step_suggestions_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/note_lifecycle_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/notebook_lifecycle_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/play_books_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/quiz_lifecycle_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/research_discover_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/research_fast_cancel_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/research_fast_import_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/retrieve_relevant_chunks_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/share_project_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/get_project_details_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/source_lifecycle_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/android/source_transfers_recorded.grpc.json` — shares header with `tools/notebooklm-py/tests/cassettes/android/act_on_sources_mind_map_recorded.grpc.json`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_download_data_table.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_download_flashcards.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_download_flashcards_markdown.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_download_mind_map.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_download_quiz.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_download_quiz_markdown.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_download_report.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_export_report.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_generate_flashcards.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_generate_quiz.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_generate_report.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_generate_study_guide.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_audio.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_data_tables.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_empty.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_flashcards.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_infographics.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_quizzes.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_reports.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_slide_decks.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_list_video.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_rename.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/artifacts_suggest_reports.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/chat_ask.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/chat_ask_with_references.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/chat_get_conversation_turns.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/chat_get_history.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/chat_next_steps.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_login_browser_cookies_check.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_notebook_create.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_notebook_delete.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_notebook_list.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_notebook_rename.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_settings_set_language.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_share_add.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_share_remove.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/cli_share_status.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_add.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_add_json.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_create.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_create_json.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_delete.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_delete_json.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_list.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_notebooks.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_remove.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_remove_json.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_rename.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/collection_rename_json.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/error_synthetic_429_rate_limit.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/auth_rotate_cookies_refresh.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/error_synthetic_500_server.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/auth_rotate_cookies_refresh.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/error_synthetic_stale_csrf.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/auth_rotate_cookies_refresh.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/generate_mind_map_chain.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/generate_mind_map_interactive.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/gzip_coverage/artifacts_revise_slide_gzipped.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_revise_slide.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_add.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_create.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_delete.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_emoji.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_generate.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_list.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_remove.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_rename.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/label_sources.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/mcp_chat_configure.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/mcp_note_update.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/mcp_studio_rename.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/mcp_studio_delete_artifact.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebook_zero_sources.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_copy.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_create.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_delete.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_emoji_update.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_get.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_get_description.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_get_raw.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_get_summary.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_list.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_remove_from_recent.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_rename.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_share.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/mind_maps_interactive.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_suggest_next_steps.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notebooks_suggest_prompts.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notes_create.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notes_create_and_update.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notes_delete.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notes_list.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/notes_list_mind_maps.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_get_notebook.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_list_artifacts.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_list_audio.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_list_mind_maps.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_list_notebooks.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_list_quizzes.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_list_reports.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/real_api_list_sources.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_cancel.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_deep_poll_long.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_import_sources.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_import_sources_populated.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_import_verification.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_poll.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_poll_empty.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_start_deep.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/research_start_fast.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/server_add_file.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/server_download_mind_map.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/server_generate_quiz.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/settings_get_output_language.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/settings_set_output_language.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sharing_get_status.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sharing_set_public.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/source_list_label.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_add_drive.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_add_file.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_add_text.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_add_url.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_check_freshness.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_delete.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_get_fulltext.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_get_guide.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_list.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_play_books.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_refresh.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_rename.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_search.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_transfer_lifecycle.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_customization_choices.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/sources_wait.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `tools/notebooklm-py/tests/cassettes/web/workflow_tracer_bullet.yaml` — shares header with `tools/notebooklm-py/tests/cassettes/web/artifacts_delete.yaml`, content differs
- `vfs/knowledge/sovereign_mesh_topology.json` — shares header with `03_VAULT/runtime_state/sovereign_mesh_topology.json`, content differs
- `vfs/notebooks/32d38906-5ae8-4ecc-b77e-705d12c89f4a/manifest.json` — shares header with `vfs/notebooks/140101e0-bc2a-41c8-87c0-cd512f130387/manifest.json`, content differs
- `vfs/skills/superpowers/tests/codex-plugin-sync/test-sync-to-codex-plugin.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs
- `vfs/skills/superpowers/tests/codex/test-marketplace-manifest.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs
- `vfs/skills/superpowers/tests/codex/test-package-codex-plugin.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs
- `vfs/skills/superpowers/tests/hooks/test-session-start.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs
- `vfs/skills/superpowers/tests/kimi/test-plugin-manifest.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs
- `vfs/skills/superpowers/tests/shell-lint/test-lint-shell.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs
- `vfs/skills/superpowers/tests/systematic-debugging/test-find-polluter.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs
- `vfs/skills/superpowers/tests/version-bump/test-bump-version.sh` — shares header with `04_KINETIC/nullclaw/examples/modal-matrix/install.sh`, content differs

## True duplicates SWEEP's header pass missed

Binary files (skipped by SWEEP) or sub-64-byte files that are nevertheless
byte-identical to another file: 42 file(s).

- `01_KERNEL/agora/Squires/Memory_Squire/auth.py`
- `01_KERNEL/agora/Squires/Memory_Squire/command_service.py`
- `01_KERNEL/agora/Squires/Memory_Squire/models.py`
- `01_KERNEL/agora/Squires/Memory_Squire/notes_service.py`
- `01_KERNEL/agora/Squires/Memory_Squire/podcast_service.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/commands.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/config.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/embedding.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/embedding_rebuild.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/episode_profiles.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/insights.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/models.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/notebooks.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/notes.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/settings.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/sources.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/speaker_profiles.py`
- `01_KERNEL/agora/Squires/Memory_Squire/routers/transformations.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/auth.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/command_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/models.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/notes_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/podcast_service.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/commands.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/config.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/embedding.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/embedding_rebuild.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/episode_profiles.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/insights.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/models.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/notebooks.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/notes.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/settings.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/sources.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/speaker_profiles.py`
- `01_KERNEL/agora/Squires/Notebook_Brain/routers/transformations.py`
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_180343/morgana_core.py`
- `02_FORGE/PORTAL_CORE/Modal/morgana/backups/deployment_20260114_183443/morgana_core.py`
- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_v94_fastapi.py`
- `02_FORGE/PORTAL_CORE/Modal/morgana/conductor_v94_remote.py`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-claude/grill-me/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills/ralph/ralph-codex/grill-me/SKILL.md`

---

*Generated by CLARITY_CORE v1.0.0 — Squire Colony (full-content dedup extension)*
*Canonical count source: colony_report.md — SWEEP Report table*