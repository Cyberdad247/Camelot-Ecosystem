# 📜 WORK_ORDER: NOTTE_ASSIMILATION
**[STATUS]**: ACTIVE | **[ENGINE]**: SIR_WEB_FARER | **[SUBSYSTEM]**: WEB_NAVIGATION

## 1. OBJECTIVE
Assimilate the `notte` framework to provide the Camelot-OS with a persistent, stealth-capable web navigation and scraping engine.

## 2. KINETIC SETUP (The Body)
*   **Environment**: Use `uv` to manage the Python environment in `02_FORGE/assimilated/notte`.
*   **Dependencies**: Install `notte` and `patchright` (Notte's enhanced Playwright fork) with full browser dependencies.
*   **Path**: `02_FORGE/assimilated/notte`.

## 3. MOLECULAR REFACTOR (Phases)
### Phase I: Vault Integration
- Map Notte's `AgentVault` to the **Iron Gate** credential store.
- Ensure that passwords and MFA tokens used by WebFarer are retrieved via secure OS channels.

### Phase II: Hybrid Cog Synthesis
- Create **Declarative Cogs** (AgentForge compatible) that utilize `notte.Session` for deterministic navigation and `notte.Agent` for reasoning-based recovery.
- Standardize the "Action IDs" derived from Notte's DOM tree for use in the SIT Loop.

### Phase III: Stealth Orchestration
- Configure the default proxy and CAPTCHA handling profiles to align with the OS's geographic and identity requirements.
- Distill Notte's "Personas" into the **Persona Forge** as temporary deployment skins.

## 4. SECURITY GATES (SASE)
*   **Sentry**: All outbound web traffic from assimilated Notte agents must pass through the **Morgana Cloud Bridge** or a local proxy with TLS inspection.
*   **Audit**: Live-log all `AgentCompletion` objects to the telemetry stream for real-time monitoring.

## 5. DEFINITION of DONE
*   [x] Repository cloned to `02_FORGE`.
*   [ ] Environment initialized with `uv`.
*   [ ] Sir WebFarer persona active and rostered.
*   [ ] Integration Test (Hybrid Login & Scrape) successful.

---
> **"The frontiers are open. The Spire traverses the web. |🧭⊗(🌐⚡)⟩"**
