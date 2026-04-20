# Modal App Audit

Last reviewed: 2026-04-20
Repo root: `C:\Users\vizio\CAMELOT_OS`

## Purpose

This audit clarifies which deployed Modal apps are represented by source code in
this repo and which ones actually own long-term versus short-term memory roles.

## Role Summary

- `excalibur-brain` is the canonical remote long-term agentic brain surface.
- NotebookLM `Living Camelot-OS v.400` is the canonical short-term living
  notebook.
- `morgana-research-agency-prod` is a support-service cluster for typed
  research, planning, and orchestration tasks.
- Voice and media apps are peripheral service surfaces, not canonical memory
  owners.

## App Findings

### `excalibur-brain`

Status:

- Canonical remote long-term agentic brain surface.
- Confirmed in runtime config and control-plane fallback logic.

Evidence:

- [control_plane/cloud_services.py](/C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:126)
- [.camelot-config.yaml](/C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml:1)
- [05_INFRASTRUCTURE/morgana_bridge/active_apps.json](/C:/Users/vizio/CAMELOT_OS/05_INFRASTRUCTURE/morgana_bridge/active_apps.json:1)

### `morgana-research-agency-prod`

Status:

- Support-service cluster for research, Northstar, blueprint, and precise-mode.
- Not the long-term memory owner.

Evidence:

- [01_KERNEL/config_shim/tiers.yaml](/C:/Users/vizio/CAMELOT_OS/01_KERNEL/config_shim/tiers.yaml:20)
- [control_plane/cloud_services.py](/C:/Users/vizio/CAMELOT_OS/control_plane/cloud_services.py:313)

### `tasha-voice-agent`

Status:

- Source code is present in-repo.
- Role is LiveKit voice receptionist plus lead capture and scheduling.
- Persists business data to Supabase, not Camelot long-term memory.
- No evidence that it owns or replaces the Excalibur or NotebookLM brain roles.

Evidence:

- [02_FORGE/PORTAL_CORE/Modal/tasha_voice_agent.py](/C:/Users/vizio/CAMELOT_OS/02_FORGE/PORTAL_CORE/Modal/tasha_voice_agent.py:1)

### `camelot-voice-pipeline`

Status:

- App ID is referenced in infrastructure metadata.
- No checked-in source file was found in this repo during this audit.
- Cannot verify local implementation details from repo contents alone.

Evidence:

- [05_INFRASTRUCTURE/morgana_bridge/active_apps.json](/C:/Users/vizio/CAMELOT_OS/05_INFRASTRUCTURE/morgana_bridge/active_apps.json:1)

### `camelot-tts-pipeline`

Status:

- App ID is referenced in infrastructure metadata.
- No checked-in source file was found in this repo during this audit.
- Cannot verify local implementation details from repo contents alone.

Evidence:

- [05_INFRASTRUCTURE/morgana_bridge/active_apps.json](/C:/Users/vizio/CAMELOT_OS/05_INFRASTRUCTURE/morgana_bridge/active_apps.json:1)

### `camelot-rustdesk-server`

Status:

- App ID is referenced in infrastructure metadata.
- Appears to be remote-access infrastructure, not a memory owner.
- No checked-in source file was found in this repo during this audit.

Evidence:

- [05_INFRASTRUCTURE/morgana_bridge/active_apps.json](/C:/Users/vizio/CAMELOT_OS/05_INFRASTRUCTURE/morgana_bridge/active_apps.json:1)

## Decisions

- Treat `excalibur-brain` as the remote long-term agentic brain.
- Treat NotebookLM as the short-term living notebook.
- Do not describe Tasha, voice pipelines, TTS, or RustDesk as canonical memory
  systems unless future code proves that they are wired into Excalibur or
  NotebookLM directly.

## Gaps

- `camelot-voice-pipeline`, `camelot-tts-pipeline`, and `camelot-rustdesk-server`
  are represented by app IDs but not by locally audited source in this repo.
- If you want full verification for those three, the next step is to pull or
  import the deployment source for each app into version control.
