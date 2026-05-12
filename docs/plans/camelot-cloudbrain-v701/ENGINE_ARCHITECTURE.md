# Camelot-OS v701 Engine Architecture

Generated: 2026-05-12T15:09:37.054474+00:00

## Source Contract

This v701 package treats the live repository as the source of truth. It pulls the Switchboard terminal registry, Soul Router weights, DKS roster count, Watchtower contract, Symbolect runtime, open-source project inventory, and Cloud Brain sync path into a single NotebookLM-ready architecture map.

## Seven-Layer Engine Stack

| Layer | Owner | Purpose | Source |
| --- | --- | --- | --- |
| L7 Ethereal Interface | Anya | Compile raw human intent into kernel-ready tasks through Triple-QFT and context compression. | 01_KERNEL/titan/memory/compiler.py |
| L6 Governance | Arthur / Sir Zenith / Lady Veritas | Enforce Iron Gate, provenance, Titanium Law, credential safety, and audit boundaries. | control_plane/ledger_sync.py; 01_KERNEL/iron_gate |
| L5 Agentic Swarm | Merlin / Foundry Council | Route work to Knights and harnesses using Switchboard, Soul Router, SARDA, and DKS hot pools. | control_plane/switchboard.py; control_plane/soul_router.py; control_plane/dks_manager.py |
| L4 Semantic Memory | Sir Mnemo / Lady Alexandria | Persist UKG, Symbolect, NotebookLM Cloud Brain notes, vector memory, and runtime ledgers. | 03_VAULT/UKG; control_plane/cloudbrain_sync.py |
| L3 Merlin Reasoning Kernel | Merlin | Execute UKG runtime, distill-anchor-weave loops, Symbolect compression, and model-lowering payloads. | 01_KERNEL/merlin/Engines/ukg_runtime.py |
| L2 Kinetic Execution | Lukas | Run local write/build/test/scan actions through CLI, Rust, Go, Nano-Knights, and guarded wrappers. | 02_FORGE; 03_VAULT/Nano-Knights |
| L1 Substrate / Watchtower | Morgana / Sir Sentinel | Probe ports, enforce resource ceilings, bridge local services, and keep the command plane observable. | 01_KERNEL/iron_gate/watchtower.py; control_plane/boot_sequence.py |

## Routing Math

`S_omega = 0.20*V + 0.35*M + 0.30*P + 0.15*E`

| Dimension | Meaning |
| --- | --- |
| V | velocity / urgency |
| M | magnitude / task scope |
| P | privacy / sensitivity |
| E | environment / engine fit |

## Immutable Engine Weights

| Weight | Value |
| --- | --- |
| W_ORCHESTRATION | 0.85 |
| W_COGNITIVE | 0.88 |
| W_CONTEXT | 0.9 |
| W_VELOCITY | 0.75 |
| W_PRIVACY | 1.0 |
| W_SOVEREIGNTY | 0.8 |
| W_KINETIC | 0.7 |
| W_BRIDGE | 0.78 |
| W_MEMORY | 0.92 |

## Foundry Council

| Knight | Engine | Weight | Value | Privacy | Function |
| --- | --- | --- | --- | --- | --- |
| sir_boris | claude_code | W_ORCHESTRATION | 0.85 | 0.3 | Architecture, Colony Command, 13-Agent Critique |
| sir_alex | claude_code | W_COGNITIVE | 0.88 | 0.3 | Cognitive cartridge orchestration, decision framing, bridge governance |
| sir_helio | gemini_cli | W_CONTEXT | 0.9 | 0.2 | 1M+ token context mapping |
| sir_codex | openai_codex | W_VELOCITY | 0.75 | 0.2 | High-velocity code generation |
| sir_forge | open_coder | W_KINETIC | 0.7 | 0.7 | L2 Kinetic Code Generation â€” local open-weight |
| sir_link | gemini_cli | W_BRIDGE | 0.78 | 0.2 | Bridge coordination across UI, cloud brain, and local terminal |
| sir_ghost | local_qwen | W_PRIVACY | 1.0 | 1.0 | Zero-Trust, air-gapped execution |
| sir_liberte | open_source | W_SOVEREIGNTY | 0.8 | 0.5 | Anti-vendor lock-in, sovereign execution, HuggingFace Hub integration |
| sir_mnemo | integration_brain | W_MEMORY | 0.92 | 0.4 | Memory routing Ã¢â‚¬â€ ST/LT/both tier scoring for Integration Brain |
| sir_sentinel | claude_code | W_ORCHESTRATION | 0.85 | 0.4 | Security audit, Agent-Armor PDG review, and governance escalation |
| sir_midas | meta_optimizer | W_ORCHESTRATION | 0.85 | 0.5 | Autonomous self-enhancement, performance optimization, and slop removal |
| sir_syntax | open_coder | W_KINETIC | 0.7 | 0.6 | DeepSeek-R1 / Llama-3 open-weight kinetic generation |

## Switchboard Terminals

| Terminal | Engine | Weight | Cost | Capability | Port | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| sir_alex | claude_code | 0.88 | medium | cognitive, reasoning, critical, decision | 8080 | Claude Code — cognitive cartridge orchestration |
| sir_boris | claude_code | 0.85 | medium | orchestration, architecture, critique, forge | 8080 | Claude Code — CLIProxy gateway |
| sir_codex | openai_codex | 0.75 | high | velocity, rapid_proto, openai | 0 | OpenAI Codex — high-velocity generation |
| sir_forge | open_coder | 0.7 | free | code_gen, scaffold, technical, kinetic | 11434 | Open Coder local — kinetic code gen |
| sir_ghost | local_qwen | 1.0 | free | privacy, air_gapped, zero_trust | 11434 | Local Qwen 3.5 — air-gapped, zero trust |
| sir_gideon | local_audit | 0.85 | free | security, audit, scorpion, gideon, forensic | 0 | Forensic auditor — GIDEON_RISK_MATRIX //SCORPION pass |
| sir_helio | gemini_cli | 0.9 | low | context, research, burst, 1m_token | 0 | Gemini CLI — 1M+ context mapping |
| sir_jcode | jcode_harness | 0.87 | free | harness, cli, mcp, swarm, multi_agent, microsecond, self_dev | 0 | jcode v0.11.6 — Rust harness, 14ms latency, swarm coord, routes via CLIProxy :8080 |
| sir_liberte | open_source | 0.8 | free | sovereignty, oss, anti_lock | 0 | Open Source — anti-vendor lock-in |
| sir_link | gemini_cli | 0.78 | low | bridge, handoff, terminal, ui, switchboard | 0 | Sir Link — handshake coordinator, switchboard ATC |
| sir_merlin | excalibur_kernel | 0.82 | free | kernel, a2a, handoff, orchestration, fusion | 8000 | Excalibur Merlin_Ω kernel — A2A orchestration, fusion router |
| sir_mnemo | integration_brain | 0.92 | low | memory, archive, recall, synthesize, route | 0 | Integration Brain router — ST/LT memory (module probe) |
| sir_pi | pi_agent | 0.82 | low | coding_agent, agentic, read, write, edit, bash, session | 8080 | pi-mono v0.73.0 — agentic coding, LLM routed via CLIProxy :8080 |
| sir_qdrant | qdrant_vector | 0.9 | free | vector, search, embed, semantic, mnemo_store | 6333 | Qdrant v1.17.1 — vector store for SIR_MNEMO, ~/bin/qdrant.exe |
| sir_saltare | saltare_gateway | 0.8 | free | mcp, gateway, routing, tool_dispatch, kinetic | 8085 | Saltare MCP Gateway v3.0.0-beta.3 — 24 handlers, port 8085 |
| sir_sentinel | claude_code | 0.85 | medium | security, audit, armor, pdg | 3001 | Security warden — Agent-Armor PDG |

## DKS Memory Law

- Assembly count from the Excalibur roster: `31`.
- Agora roster count: `31`.
- Hot-pool rule: at most 5 active Knight contexts in RAM.
- RAM ceiling: 8 GB local Titanium Law.

## Cloud Brain v701 Rule

Architecture changes must land in the local docs and runtime manifest first, then ledger, then Cloud Brain queue/sync. NotebookLM is the memory surface; the repo remains the executable source of truth.
