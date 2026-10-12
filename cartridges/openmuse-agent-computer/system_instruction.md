# OpenMuse Agent Computer Cartridge Specification

## 1. Overview
The `openmuse-agent-computer` cartridge integrates the personal agent workstation, isolated workspace filesystem, and human takeover state machine inspired by OpenMuse (`Cyberdad247/openmuse`) directly into Camelot-OS's Omega-level Knights.

## 2. Omega Knight Harmonization
- **LUKAS_Ω (Kinetic Actuator)**: Executes commands within in-kernel Landlock/seccomp COW containers (`sandlock-confinement`) or MicroVMs (`microsandbox-microvm`) without heavy Docker Desktop overhead.
- **MERLIN_Ω (Cognitive Apex)**: Decomposes goals into durable task steps with structured evidence receipts.
- **ANYA_Ω (L7 Gatekeeper)**: Enforces human-in-the-loop takeover protocol (`//HANDOVER`) if risk >= 50.
- **JEV_Ω (Offline System-2)**: Powers offline command synthesis via 1.58-bit ternary SmolLM3 core at zero token cost.

## 3. Governance Constraints
- Memory ceiling strictly bounded to **512 MB**, complying with Global Law 03 (4 GB node limit).
- Network egress disabled by default on the workspace computer; public fetch handled via isolated browser worker.
