# Camelot-OS v701 Engine Architecture

Generated: 2026-08-12T17:36:02.237472+00:00

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
| W_LINEAR | 0.95 |
| W_WARDEN | 0.93 |
| W_FINANCE | 0.82 |
| W_BIFROST | 0.91 |
| W_VOICE | 0.86 |
| W_AGENTIC | 0.87 |

## Foundry Council

| Knight | Engine | Weight | Value | Privacy | Function |
| --- | --- | --- | --- | --- | --- |
| sir_boris | claude_code | W_ORCHESTRATION | 0.85 | 0.3 | Architecture & Lead |
| sir_alex | claude_code | W_COGNITIVE | 0.88 | 0.3 | Cognitive Orchestration |
| sir_helio | antigravity.cli | W_CONTEXT | 0.9 | 0.2 | 1M+ Context Mapping |
| sir_codex | openai_codex | W_VELOCITY | 0.75 | 0.2 | High-Velocity Code |
| sir_forge | open_coder | W_KINETIC | 0.7 | 0.7 | Local Code Gen |
| sir_sonus | vox_anima | W_VOICE | 0.86 | 0.3 | Voice & Resonance |
| sir_link | antigravity.cli | W_BRIDGE | 0.78 | 0.2 | Cross-UI Handoff |
| sir_ghost | local_qwen | W_PRIVACY | 1.0 | 1.0 | Zero-Trust Execution |
| sir_liberte | open_source | W_SOVEREIGNTY | 0.8 | 0.5 | Anti-Vendor Sovereign |
| sir_mnemo | integration_brain | W_MEMORY | 0.92 | 0.4 | Memory Routing |
| sir_ouroboros | ouroboros_ssm | W_LINEAR | 0.95 | 0.1 | Linear Reasoning |
| sir_sentinel | gemini_flash | W_WARDEN | 0.93 | 0.8 | Security Warden |
| sir_valerian | gemini_flash | W_FINANCE | 0.82 | 0.4 | Financial/ROI |
| sir_heimdall | pydantic_ai | W_BIFROST | 0.91 | 0.9 | Bifrost Guardian |
| sir_openclaw | openclaw | W_CONTEXT | 0.9 | 0.6 | Compliant Trend Harvester |
| sir_rustclaw | rustclaw | W_KINETIC | 0.7 | 0.5 | Rust Image Pipeline Executor |
| sir_hermes | hermes_cli | W_BRIDGE | 0.78 | 0.6 | Shopify GraphQL/Webhook Courier |
| lady_nanobot | next_edge | W_VELOCITY | 0.75 | 0.6 | Edge Component Swarm |
| sir_zeroclaw | local_qwen | W_PRIVACY | 1.0 | 1.0 | Zero-Trust Commerce Sentry |
| sir_agentis | agents_a1 | W_AGENTIC | 0.87 | 0.9 | Agentic MoE Orchestrator |

## Switchboard Terminals

| Terminal | Engine | Weight | Cost | Capability | Port | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| bifrost_gateway | bifrost_gateway | 0.8 | free | gateway, websocket, webhook, ingress, swarm, pwa, voice | 0 | Bifrost TS gateway — voice/webhook ingress + Microcubic swarm (:3001); bridge via control_plane.bifrost_gateway |
| lady_nanobot | next_edge | 0.84 | free | edge_component_agents, webgl_mockup_contract, nfc_route_contract, telemetry_event_contract | 0 | Claw Suite edge component swarm contract |
| sir_agentis | agents_a1 | 0.87 | free | agentic, tool_use, planning, local, openai_compat | 0 | Agents-A1 35B MoE — local vLLM/SGLang, OpenAI-compat (35B MoE agentic LLM; Cyberdad247/Agents-A1) |
| sir_alex | claude_code | 0.88 | medium | cognitive, reasoning, critical, decision | 8080 | Claude Code — cognitive cartridge orchestration |
| sir_boris | claude_code | 0.85 | medium | orchestration, architecture, critique, forge | 8080 | Claude Code — CLIProxy gateway |
| sir_codex | openai_codex | 0.75 | free | velocity, rapid_proto, openai | 8080 | OpenAI Codex via CLIProxyAPI :8080 — free provider pool |
| sir_forge | sovereign | 0.7 | free | code_gen, scaffold, technical, kinetic | 0 | SIE qwen2.5-coder:3b — sovereign code gen |
| sir_ghost | sovereign | 1.0 | free | privacy, air_gapped, zero_trust | 0 | SIE qwen3:4b — air-gapped sovereign inference |
| sir_gideon | local_audit | 0.85 | free | security, audit, scorpion, gideon, forensic | 0 | Forensic auditor — GIDEON_RISK_MATRIX //SCORPION pass |
| sir_gravity | antigravity | 0.88 | free | code_gen, ide_native, gemini, google, antigravity, kinetic | 8080 | Google Antigravity — Gemini models via CLIProxyAPI antigravity OAuth channel |
| sir_heimdall | pydantic_ai | 0.99 | low | security, mesh, bifrost, zero_trust, network, sentinel | 0 | Sir Heimdall — Bifrost Guardian & Mesh Network Sentinel |
| sir_helio | pydantic_ai | 0.95 | low | context, research, burst, 1m_token, pydantic_ai | 0 | Sir Helio v400 — Pydantic AI Context Lord |
| sir_hermes | hermes_cli | 0.78 | free | agent, tool_use, nous, openrouter, kinetic, autonomous, shopify_admin, shopify_storefront, graphql_orchestration, webhook_choreography | 0 | Nous Hermes Agent — autonomous tool-calling via subprocess (-q mode) |
| sir_kimi | kimi_cli | 0.82 | free | long_context, research, chinese, moonshot, kimi, k2 | 8080 | Moonshot Kimi K2.5 — 1M context via CLIProxyAPI kimi OAuth channel |
| sir_liberte | open_source | 0.8 | free | sovereignty, oss, anti_lock | 0 | Open Source — anti-vendor lock-in |
| sir_link | antigravity.cli | 0.78 | low | bridge, handoff, terminal, ui, switchboard | 0 | Sir Link — handshake coordinator, switchboard ATC |
| sir_mnemo | integration_brain | 0.92 | low | memory, archive, recall, synthesize, route | 0 | Integration Brain router — ST/LT memory (module probe) |
| sir_octavian | local_ops | 0.82 | free | ops, metrics, monitoring, telemetry, status, alerts, factory | 8400 | Ops & metrics sentinel — factory throughput, health dashboard (:8400) |
| sir_openclaw | openclaw | 0.9 | free | compliant_trend_research, source_attribution, robots_policy, rate_limit_respect | 0 | Claw Suite harvester: compliant public-source research only |
| sir_rustclaw | rustclaw | 0.86 | free | rust_image_pipeline, cmyk_contrast_check, halftone_underbase_plan, avif_transcode_contract | 0 | Claw Suite Rust image pipeline contract |
| sir_sentinel | claude_code | 0.85 | medium | security, audit, armor, pdg | 3001 | Security warden — Agent-Armor PDG |
| sir_sonus | kitten_tts | 0.88 | free | tts, audio, voice, speak, synthesize, kitten, streaming | 8300 | Kitten TTS streaming node — chunked audio synthesis HTTP :8300 |
| sir_zeroclaw | sovereign | 1.0 | free | zero_trust, ip_trademark_guard, affiliate_abuse_guard, checkout_risk_gate | 0 | SIE qwen3:4b — zero-trust sentry; HUMAN_GATE for fraud and fingerprint actions |

## DKS Memory Law

- Assembly count from the Excalibur roster: `9`.
- Agora roster count: `43`.
- Hot-pool rule: at most 5 active Knight contexts in RAM.
- RAM ceiling: 8 GB local Titanium Law.

## Cloud Brain v701 Rule

Architecture changes must land in the local docs and runtime manifest first, then ledger, then Cloud Brain queue/sync. NotebookLM is the memory surface; the repo remains the executable source of truth.
