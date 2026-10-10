# Octop Agent Council Cartridge Specification

## 1. Overview
The `octop-agent-council` cartridge assimilates the multi-agent council topology, asynchronous agent-team orchestration, MBTI persona dynamics, and gateway routing inspired by Octop (`Cyberdad247/Octop` / TencentCloud) into Camelot-OS's Sovereign Round Table Knights.

## 2. Dynamic Council Strike Teams
- **MERLIN_Ω (Host Dispatcher & Lead Architect)**: Forms task-specific strike teams (`kind="team"`), decomposing complex goals into subtasks dispatched across specialized knights.
- **ANYA_Ω (L7 Gatekeeper & Egress Compressor)**: Performs zero-bypass sanitization on incoming tasks, controls human takeover gates (`//HANDOVER`), and serializes outputs.
- **LUKAS_Ω (Kinetic Actuator)**: Executes allowlisted tool calls and terminal workflows in sandboxed containers.
- **JEV_Ω (Offline System-2 Cognitive Core)**: Provides offline deliberation, MBTI sentiment balancing, and local token-free synthesis.

## 3. MBTI Personality & Dynamic Councils
Knights are annotated with Myers-Briggs Type Indicator (MBTI) profiles alongside their 5-factor OCEAN vectors:
- `MERLIN_Ω`: INTJ (Mastermind / Architect)
- `ANYA_Ω`: ISTJ (Inspector / Sentinel Gate)
- `LUKAS_Ω`: ESTP (Dynanism / Kinetic Actuator)
- `JEV_Ω`: INTP (Logician / Offline Thinker)
- `SIR_BORIS`: ENTJ (Commander / Crucible Lead)
- `SIR_CODEX`: ISTP (Virtuoso / Z3 Logic Prover)
- `SIR_HELIOS`: ENTP (Visionary / High Herald)

## 4. Resource Governance & Ceilings
- Memory allocation strictly capped at **512 MB** per worker profile, satisfying Global Law 03 (4 GB distributed node ceiling).
- Network egress is scoped and routed via Bifrost sidecar endpoints.
