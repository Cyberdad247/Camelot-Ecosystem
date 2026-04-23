# CAMELOT APEX OS v400.1.0 — ENTIRE MAP (Territory)
**Timestamp:** 2026-04-19T16:18:29.176251
**Version:** 400.1.0 (Universal Singularity)
**Mode:** Kinetic Purity [Active]
**Root:** `C:\Users\vizio\CAMELOT_OS`

## CYBERTRON TOPOLOGY (Multi-Node)

| Node | Location | Function | Status |
|------|----------|----------|--------|
| CONTROL_PLANE | control_plane/ | Pydantic AI, A2A, Knight dispatch | LOCAL |
| KINETIC_EDGE | kinetic_edge/mcp_server/ | Rust Axum MCP, port 3001 | LOCAL |
| EXCALIBUR | 01_KERNEL/EXCALIBUR/ | Core FastAPI kernel | LOCAL |
| SQUIRE_COLONY | squires/ | 8 nano-knight sub-agents | LOCAL |
| CLIPROXY | ~/CLIProxyAPI/ | Zero-Burn proxy, 29+ models, port 8080 | LOCAL |
| LIGHTPANDA | WSL Ubuntu :9222 | Zig headless browser CDP | LOCAL (WSL) |
| MODAL_BRAIN | Modal cloud | excalibur-brain, T4 GPU | CLOUD |
| MODAL_TASHA | Modal cloud | tasha-voice-agent, LiveKit | CLOUD |
| FORGE_UI | 02_FORGE/web/ | TypeScript/React dashboard | LOCAL |
| VAULT | 03_VAULT/ | AES-256-GCM credentials, training configs | LOCAL |
| CLOUD_BRAIN | NotebookLM (RPC) | Living Camelot-OS v.400, 132 notebooks | CLOUD |

## KINETIC EDGE — Module Architecture (Lukas_Omega / L2)

| Module | File | Purpose | Status |
|--------|------|---------|--------|
| AgentArmor PDG | main.rs | Program Dependency Graph taint analysis — 5 rules, sandbox enforcement | ACTIVE |
| Bifrost Gate | bifrost.rs | 3-layer auth: loopback / Tailnet+token / reject. Constant-time comparison | ACTIVE |
| AP2 Settlement | ap2_settlement.rs | ed25519 cryptographic compute settlement between agents | ACTIVE |
| TurboQuant | turboquant.rs | PolarQuant KV cache compression, 32K context, 2GB RAM budget | SCAFFOLD |
| WASI-NN | wasi_nn.rs | WASM neural inference bindings (Ternary158/ONNX/OpenVINO) | SCAFFOLD |

## KINETIC ARMORY — Binary Status

| Binary | Language | Location | Size | Status |
|--------|----------|----------|------|--------|
| Saltare | Go | 02_FORGE/KINETIC_ARMORY/Saltare/saltare.exe | 37.6MB | COMPILED |
| Saltare-MCP | Go | 02_FORGE/KINETIC_ARMORY/Saltare/bin/saltare-mcp.exe | 8.3MB | COMPILED |
| Cribo | Rust | 02_FORGE/kinetic/bin/cribo.exe | 669KB | COMPILED |
| Rotel | Rust | 02_FORGE/kinetic/bin/rotel.exe | 894KB | COMPILED |
| Ledger | Go | 02_FORGE/kinetic/bin/ledger.exe | 734KB | COMPILED |
| camelot-mcp-edge | Rust | kinetic_edge/mcp_server/target/release/ | ~4MB | COMPILED |

## DIRECTORY TREE

---

📂 CAMELOT_OS/
  - .camelot-config.yaml
  - .modal.toml
  - .prettierrc
  - .python-version
  - CONTRIBUTING.md
  - COPYRIGHT.md
  - Camelot-OS.cmd
  - Dockerfile.kernel
  - Dockerfile.sandbox
  - GOD_MODE_QUICKSTART.md
  - LICENSE
  - NOTICE.md
  - OS_MANIFEST.md
  - PROVENANCE_LEDGER.md
  - VERSION
  - blueprint.md
  - claude-ollama.cmd
  - docker-compose.yml
  - entiremap.md
  - notebook_context.md
  - package.json
  - pnpm-workspace.yaml
  - pyproject.toml
  - tasks.md
  - tier.py
  - upgrade_cloudbrain.py
  - uv.lock
  - verification.md
  📂 .github/
    📂 workflows/
      - verify_os.yml
  📂 00_SECURE_ARCHIVE/
    - run_all_tests.ps1
  📂 01_KERNEL/ [CORE]
    - .dockerignore
    - ARCHITECTURE.md
    - Dockerfile
    - README.md
    - __init__.py
    - pyproject.toml
    - requirements.txt
    📂 EXCALIBUR/ [CORE]
      - boot_excalibur.ps1
      - excalibur_autopilot.py
      - main.py
      - roster.yaml
      📂 BRIDGE/ [CORE]
        📂 GENKIT/ [CORE]
          - genkit.config.ts
          - package.json
          - run_flow.ts
        📂 OPENMCP/ [CORE]
          - connection.json
      📂 config/ [CORE]
        - .modal.toml
        - CAMELOT_APEX_SYSTEM_PROMPT.md
        - api_manifest.yaml
        - cartridges.json
        - council_peers.json
        - cribo.toml
        - dna.json
        - extension_integration.json
        - hitl_gate.json
        - llm_routing.json
        - mcp_perplexity.json
        - mcp_registry.json
        - mcp_servers.json
        - phials_registry.json
        - saltare.toml
        - saltare.yaml
        - secrets.json
        - system_manifest.json
        - validate_schema.py
        - videneptus_config.json
        📂 defense/ [CORE]
          - defense_grid_manifest.json
        📂 lattice/ [CORE]
          - SYSTEM_LATTICE_DEF.json
        📂 registry/ [CORE]
          - god_prompt.json
          - package.json
          - tissue_catalog.json
          - tsconfig.json
        📂 schemas/ [CORE]
          - agent_dispatch.schema.json
          - memory_query.schema.json
          - system_health.schema.json
      📂 core/ [CORE]
        - excalibur.py
      📂 kernel_api_bridge/ [CORE]
        - Cargo.lock
        - Cargo.toml
        - build_error.log
        📂 src/ [CORE]
          - main.rs
      📂 proxy/ [CORE]
        - bridge.py
        - start_bridge.ps1
      📂 schemas/ [CORE]
        - anya_constrict.py
        - logging_schema.json
      📂 shared/ [CORE]
        - __init__.py
        - symbolect.py
      📂 system/ [CORE]
        - MENTOR.py
        - __init__.py
        - camelot_shell.py
        - culture_bias.py
        - forge_v2.py
        - gradio_app.py
        - test_antigravity.py
        - test_safe.py
        - watchtower.py
      📂 types/ [CORE]
        - camelot.d.ts
    📂 agora/ [CORE]
      - __init__.py
      - brain_worker.py
      - bridge.py
      - context.py
      - hud_bridge.py
      - node.py
      - protocol.py
      - router.py
      - swarm_controller.py
      - sync_cli.sh
      - videneptus.py
      - war_room_protocol.py
      📂 Squires/ [CORE]
        - ignite_notebook.py
        📂 Memory_Squire/ [CORE]
          - __init__.py
          - auth.py
          - chat_service.py
          - client.py
          - command_service.py
          - context_service.py
          - embedding_service.py
          - episode_profiles_service.py
          - insights_service.py
          - main.py
          - models.py
          - models_service.py
          - notebook_service.py
          - notes_service.py
          - podcast_api_service.py
          - podcast_service.py
          - search_service.py
          - settings_service.py
          - sources_service.py
          - transformations_service.py
          📂 routers/ [CORE]
            - __init__.py
            - auth.py
            - chat.py
            - commands.py
            - config.py
            - context.py
            - embedding.py
            - embedding_rebuild.py
            - episode_profiles.py
            - insights.py
            - models.py
            - notebooks.py
            - notes.py
            - podcasts.py
            - search.py
            - settings.py
            - source_chat.py
            - sources.py
            - speaker_profiles.py
            - transformations.py
        📂 Notebook_Brain/ [CORE]
          - __init__.py
          - auth.py
          - chat_service.py
          - client.py
          - command_service.py
          - context_service.py
          - embedding_service.py
          - engine_v1.py
          - episode_profiles_service.py
          - insights_service.py
          - main.py
          - memory.json
          - models.py
          - models_service.py
          - notebook_service.py
          - notes_service.py
          - podcast_api_service.py
          - podcast_service.py
          - search_service.py
          - settings_service.py
          - sources_service.py
          - transformations_service.py
          📂 routers/ [CORE]
            - __init__.py
            - auth.py
            - chat.py
            - commands.py
            - config.py
            - context.py
            - embedding.py
            - embedding_rebuild.py
            - episode_profiles.py
            - insights.py
            - models.py
            - notebooks.py
            - notes.py
            - podcasts.py
            - search.py
            - settings.py
            - source_chat.py
            - sources.py
            - speaker_profiles.py
            - transformations.py
        📂 commands/ [CORE]
          - __init__.py
          - embedding_commands.py
          - example_commands.py
          - podcast_commands.py
          - source_commands.py
        📂 data/ [CORE]
          📂 sqlite-db/ [CORE]
            - checkpoints.sqlite
          📂 tiktoken-cache/ [CORE]
          📂 uploads/ [CORE]
        📂 migrations/ [CORE]
          - 1.surrealql
          - 1_down.surrealql
          - 2.surrealql
          - 2_down.surrealql
          - 3.surrealql
          - 3_down.surrealql
          - 4.surrealql
          - 4_down.surrealql
          - 5.surrealql
          - 5_down.surrealql
          - 6.surrealql
          - 6_down.surrealql
          - 7.surrealql
          - 7_down.surrealql
          - 8.surrealql
          - 8_down.surrealql
          - 9.surrealql
          - 9_down.surrealql
        📂 open_notebook/ [CORE]
          - __init__.py
          - config.py
          - exceptions.py
          📂 database/ [CORE]
            - async_migrate.py
            - migrate.py
            - repository.py
          📂 domain/ [CORE]
            - __init__.py
            - base.py
            - content_settings.py
            - models.py
            - notebook.py
            - podcast.py
            - transformation.py
          📂 graphs/ [CORE]
            - ask.py
            - chat.py
            - prompt.py
            - source.py
            - source_chat.py
            - tools.py
            - transformation.py
            - utils.py
          📂 plugins/ [CORE]
            - podcasts.py
          📂 utils/ [CORE]
            - __init__.py
            - context_builder.py
            - text_utils.py
            - token_utils.py
            - version_utils.py
      📂 agents/ [CORE]
        - armory.py
        - knight_base.py
        - roster.json
        - soul_binder.py
        📂 templates/ [CORE]
          - config.yaml
      📂 fleet/ [CORE]
        - fleet_cmd.exe
        - go.mod
        - go.sum
        - main.go
      📂 knights/ [CORE]
        - notebook_knight.py
        - omni_knight.py
        - opencode_knight.py
      📂 models/ [CORE]
        - proteus_vector.py
      📂 orchestration/ [CORE]
        - __init__.py
        - agent_dispatcher.py
        - handoff_manager.py
        - harvest_personas.py
        - test_harness.py
        - think_tank.py
      📂 persona/ [CORE]
        - __init__.py
        - claude_pattern_miner.py
        - persona_engine.py
        - persona_extractor.py
        - trace_v1.log
        - ukg_persona_schema.json
      📂 pkg/ [CORE]
        📂 brain/ [CORE]
          - ukg_schema.go
        📂 evolution/ [CORE]
          - chrysalis.go
      📂 prompts/ [CORE]
        - assimilation.jinja
        - self_update_protocol.md
        - subagent_collaboration.md
        📂 AUDIO/ [CORE]
          - Ω_PERPLEXITY_SONUS_BOOTSTRAP.nkg
          - Ω_SONUS_SKILL_DISTILLER.nkg
        📂 DEVELOPMENT/ [CORE]
        📂 FORGE/ [CORE]
          - Ω_AUDIT_SWARM_PRIME.nkg
          - Ω_KNIGHT_COMPILER_v100.nkg
        📂 HYBRID_OMEGA/ [CORE]
        📂 LEGACY/ [CORE]
        📂 LEGAL/ [CORE]
          - Ω_CAMELOT_IP_FORTRESS.nkg
        📂 RESEARCH/ [CORE]
          - Ω_ECO_RESEARCH_PROTOCOL.nkg
          - Ω_MORGANA_SWARM.nkg
          - Ω_SCOUT_SWARM.nkg
        📂 SYNTHESIS/ [CORE]
        📂 guilds/ [CORE]
          - legal_guild.jinja
          - pm_guild.jinja
        📂 oracle/ [CORE]
      📂 squire/ [CORE]
        - biome.json
      📂 swarms/ [CORE]
        - atomic_pattern.py
        - directive_queue.py
        - live_voice_bridge.py
        - local_intelligence_swarm.py
        - merlin_agent_swarm.py
        - piper_tts.py
        - research_swarm.py
        - scout_swarm_prime.py
        - sit_loop.py
        - swarm_controller.py
        - vision_swarm.py
        - voice_swarm.py
        📂 hivemind/ [CORE]
          - go.mod
          - hivemind.exe
          - main.go
        📂 perplexity/ [CORE]
          - scout_sonar.py
    📂 config/ [CORE]
      📂 registry/ [CORE]
        - chimera_unified_kernel.json
        - config.json
        - secrets.json
    📂 docs/ [CORE]
      - AUDIT_REPORT_20260131.md
      - AUDIT_REPORT_20260131_2215.md
      - CAMELOT_BIBLE.md
      - CAMELOT_TRIAD_INTEGRATION.md
      - EMPIRE_MAP.md
      - Entire_map.md
      - GEMINI.md
      - OS_MANIFEST.md
      - PHASE_8_KINETIC_ASCENSION.md
      - PHASE_9_ETHEREAL_RESONANCE.md
      - SEPTEM_REGNA_ARCH.md
      - ledger_tool.blueprint.md
      - Ω_SKILL_MATRIX_PRIME.md
    📂 forge/ [CORE]
      - forge_v2.py
      - modal_cloud.py
      - rename_project.py
      - update_map.py
      📂 assimilation/ [CORE]
        - __init__.py
        - __main__.py
        📂 core/ [CORE]
          - __init__.py
          - handlers.py
          - parser.py
          - registry.py
          - reporting.py
          - types.py
          - verification.py
        📂 tests/ [CORE]
          - manual_test_harmony.py
          - test_integration.py
      📂 cmd/ [CORE]
        - launch_warden.ps1
        📂 pulse/ [CORE]
          - heartbeat.exe
          - heartbeat.go
      📂 deployment/ [CORE]
        - khoj-docker-compose.yml
        📂 cribo/ [CORE]
          - bundler.py
          - cribo.toml
        📂 manifests/ [CORE]
      📂 diagnostics/ [CORE]
        - got_debugger.py
      📂 exp/ [CORE]
        - __init__.py
        - calculator.py
        - sim_constitutional_safety.py
        - sim_council_debate.py
        - sim_engine_actuation.py
        - sim_excalibur_bridge.py
        - sim_grand_development.py
        - sim_notebook_knight.py
        - sim_oracle.py
        - sim_oracle_plan_test.py
        - sim_planning_engine.py
        - sim_routing.py
        - verify_all_engines.py
      📂 internal/ [CORE]
        📂 defense/ [CORE]
          - memory_monitor.go
        📂 kinetic/ [CORE]
          - cribo_wrapper.go
        📂 morgana/ [CORE]
          - router.go
      📂 modal/ [CORE]
        📂 logic/ [CORE]
          - lac_protocol.py
      📂 monitoring/ [CORE]
        - __init__.py
        - telemetry_bridge.py
      📂 nano_forge/ [CORE]
        - fingerprints.json
        - hybrid_conductor.py
        - mission_dag.py
        - nano_forge.py
        - phantom_engine.py
        - phantom_grid.py
        - phantom_injection.js
        - profile_manager.py
        - rich_fingerprint_schema.json
        - system_manifest_schema.json
        📂 behaviors/ [CORE]
          - human_simulator.py
        📂 extension/ [CORE]
          - background.iife.js
          - background.js
          - bg.jpg
          - buildDomTree.js
          - content_sentry.js
          - icon-128.png
          - icon-32.png
          - llm_client.js
          - manifest.json
          - offscreen.html
          - offscreen.js
          - options.css
          - options.html
          - options.js
          - package.json
          - popup.css
          - popup.html
          - popup.js
          - skills_registry.js
          - vault_bridge.js
          📂 _locales/ [CORE]
          📂 content/ [CORE]
            - _content.css
            - index.iife.js
          📂 options/ [CORE]
            - _options.css
            - index.html
            - war_room.html
            - war_room.js
          📂 permission/ [CORE]
            - index.html
            - permission.js
          📂 side-panel/ [CORE]
            - index.html
          📂 side_panel/ [CORE]
            - research_panel.css
            - research_panel.html
            - research_panel.js
          📂 src/ [CORE]
            - action_resolver.js
          📂 tests/ [CORE]
            - test_chunk_manager.js
            - test_cognitive_parser.js
            - test_context_pruner.js
            - test_data_privacy.js
            - test_nano_knights.js
            - test_ouroboros.js
            - test_persona_logic.js
            - test_precise_mode.js
            - test_prometheus_integration.js
            - test_self_healing.js
            - test_social_engineering.js
            - test_specialized_skills.js
            - test_stealth.js
            - test_token_efficiency.js
            - test_voice_squire.js
            - verify_agent_logic.js
        📂 templates/ [CORE]
          - CAMELOT_APEX_SYSTEM_PROMPT.md
          - knight_python.py.tpl
      📂 scripts/ [CORE]
        - audit_report.json
        - culture_bias.py
        - diagnostics.py
        - fetch_local_model.py
        - fix_encoding_build.py
        - inspect_rustdesk_db.py
        - knight_swarm_manager.py
        - knowledge_hive_ingestion.py
        - live_swarm_audit.py
        - nano_cli_auditor.py
        - omega_audit.py
        - predictive_mission_sim.py
        - rapid_assimilate.py
        - ready_puter.py
        - setup_kobold.py
        - setup_openvoice.py
        - setup_phase4_configs.py
        - setup_piper.py
        - setup_training.py
        - setup_voice_stack.py
        - tainted_cleanup.py
        - test_hive_swarm.py
        - test_integrations.py
        - test_kokoro.py
        - trigger_sync.py
        - trivy_scan.py
        - verify_cloud.py
        - verify_docs.py
        - verify_mcp_hub.py
        - verify_ollama.js
        - verify_resonance.py
        - verify_vault.js
      📂 skills/ [CORE]
      📂 tools/ [CORE]
        - analytics_engine.py
        - antigravity_safe.py
        - conductor.py
        - ingest_dropzone.py
        - ledger_commit.py
        - morgana_logger.py
        - prod_validator.py
        - status_reporter.py
        - swarm_tools_v2.py
        - verification_matrix.py
        📂 scripts/ [CORE]
          - check_gemini_updates.ps1
          - clean_forge.ps1
          - gatekeeper.ps1
          - start-khoj.ps1
        📂 surreal/ [CORE]
      📂 workflows/ [CORE]
        - Feature_Build.crusade
        - validation_workflow.json
    📂 iron_gate/ [CORE]
      - __init__.py
      - security_policy.json
      - watchtower.py
      📂 DEFENSE_GRID/ [CORE]
        - activate_aegis.ps1
        - config.yaml
        - defense_grid.py
        - setup_aegis_startup.ps1
        - sit_loop.py
        - watchtower.exe
        - watchtower.pdb
        - watchtower.rs
        📂 knights/ [CORE]
          - __init__.py
          - castor.py
          - kronos.py
          - octavian.py
          - sentinel.py
      📂 gates/ [CORE]
        - __init__.py
        - zenith_exp_gate.py
      📂 judge/ [CORE]
        - __init__.py
        - governance_audit.py
        - llm_judge.py
        - rubric.py
        - test_judge.py
      📂 security/ [CORE]
        - __init__.py
        - audit_wrapper.py
        - biological_isolation.py
        - enforcer.py
        - hermes.py
        - identity_decay.py
        - iron_gate.py
        - killswitch_controller.py
        - policy.yaml
        - redaction_patterns.json
        - reforge_identity.py
        - scan_secrets.py
        - shadow_mode.py
        - vault_keeper.py
        - warden.py
        - zenith_scanner.py
    📂 merlin/ [CORE]
      - deep_dive_auditor.py
      - merlin_omega.py
      - repo_analyzer.py
      - sky_engine.py
      📂 Engines/ [CORE]
        - __init__.py
        - coherence_engine.py
        - mcp_adapter.py
        - merlin_llm.py
        - prism_gateway.py
        - sentinel_compressor.py
        - ukg_runtime.py
        - videneptus_lac.py
        📂 crawl4ai/ [CORE]
          - __init__.py
          - __version__.py
          - async_configs.py
          - async_crawler_strategy.py
          - async_database.py
          - async_dispatcher.py
          - async_logger.py
          - async_webcrawler.py
          - browser_manager.py
          - browser_profiler.py
          - cache_context.py
          - chunking_strategy.py
          - cli.py
          - config.py
          - content_filter_strategy.py
          - content_scraping_strategy.py
          - docker_client.py
          - extraction_strategy.py
          - hub.py
          - install.py
          - markdown_generation_strategy.py
          - migrations.py
          - model_loader.py
          - models.py
          - prompts.py
          - proxy_strategy.py
          - ssl_certificate.py
          - types.py
          - user_agent_generator.py
          - utils.py
          📂 components/ [CORE]
            - crawler_monitor.py
          📂 crawlers/ [CORE]
            - __init__.py
          📂 deep_crawling/ [CORE]
            - __init__.py
            - base_strategy.py
            - bff_strategy.py
            - bfs_strategy.py
            - crazy.py
            - dfs_strategy.py
            - filters.py
            - scorers.py
          📂 html2text/ [CORE]
            - __init__.py
            - __main__.py
            - _typing.py
            - cli.py
            - config.py
            - elements.py
            - utils.py
          📂 js_snippet/ [CORE]
            - __init__.py
            - navigator_overrider.js
            - remove_overlay_elements.js
            - update_image_dimensions.js
          📂 legacy/ [CORE]
            - __init__.py
            - cli.py
            - crawler_strategy.py
            - database.py
            - docs_manager.py
            - llmtxt.py
            - version_manager.py
            - web_crawler.py
          📂 processors/ [CORE]
        📂 symbolect_transpiler/ [CORE]
          - symbolect.py
      📂 context/ [CORE]
        - cache_manager.py
        - cep_api.py
        - expansion_engine.py
        - got_expander.py
        - rag_backbone.py
        - test_cep.py
        📂 data/ [CORE]
          - omega_graph.json
      📂 fusion/ [CORE]
        - __init__.py
        - capability_graph.py
        - fusion_router.py
        - merger_engine.py
        - strategies.py
      📂 intelligence/ [CORE]
        - voice_commander.py
      📂 rag/ [CORE]
        - __init__.py
        - chronos.py
        - chronos_haystack.py
        - lightrag_engine.py
        - recursive_search.py
      📂 reasoning/ [CORE]
        - __init__.py
        - aurora_v_jepa.py
        - aurora_vision.py
        - core.py
        - council_debate.py
        - dream_state.py
        - helix_loop.py
        - lyricus_voice.py
        - omega_learn.py
        - oracle_physics.py
        - planning_engine.py
        - prometheus_decomp.py
        - search.py
        - titan_forge.py
        - veritas_audit.py
      📂 rune_phases/ [CORE]
        - __init__.py
        - experience_check.py
        - graph_traverse.py
        - lightrag_retrieve.py
    📂 protocols/ [CORE]
      - agno_orchestrator.md
      - assimilation_v2.md
      - assimilation_v3.md
      - assimilation_v4_omega.md
      - assimilation_v5_evolution.md
      - cellular_protocol.md
      - distill_reconstruct_protocol.md
      - hive_forge_v1.md
      - iron_gate_protocol.md
      - knight_evolution_protocol.md
      - lukas_architect.md
      - merlin_identity_forge.md
      - paladin_htn_protocol.md
      - persona_evolution_protocol.md
      - sarda_engine_v1.md
      - squire_protocol.md
      - titan_protocol.md
      - triple_qft_compilation.md
      - ukg_integration_v206.md
      - xp_economy_protocol.md
      - Ω_CHIMERA_AUDIT.md
      - Ω_KNIGHT_FORGE.md
      - Ω_THINK_TANK_PRIME.md
    📂 reasoning/ [CORE]
      - __init__.py
      - core.py
    📂 security/ [CORE]
      - __init__.py
      - zenith_scanner.py
    📂 senses/ [CORE]
      - morgana_edge.py
      - telemetry_client.py
      📂 audio/ [CORE]
        - knight_voices.py
        - vox_anima.py
        - vox_service.py
        📂 sonus/ [CORE]
          - compiler.py
      📂 connectivity/ [CORE]
        - __init__.py
        - aether.py
        - anya_ipc_bridge.rs
        - rustdesk_bridge.py
        - titanlink_server.py
        📂 bridges/ [CORE]
          - clawdbot_client.py
      📂 integrations/ [CORE]
        - README_HAYSTACK_UKG.md
        - __init__.py
        - haystack_requirements.txt
        - haystack_ukg_bridge.py
        - merlin_haystack_generator.py
        - ollama_client.py
        - ouroboros_sync.ps1
        - test_ollama.py
      📂 learning/ [CORE]
        - dataset_collector.py
        - dataset_generator.py
        - omega_trainer.py
        📂 datasets/ [CORE]
          - feedback_20260127.jsonl
        📂 training_data/ [CORE]
          - ledger_sft_20260120.jsonl
      📂 morgana_bridge/ [CORE]
        - Cargo.lock
        - Cargo.toml
        📂 src/ [CORE]
          - main.rs
      📂 train/ [CORE]
        - camelot_dataset.jsonl
        - fine_tune_unsloth.py
        - prep_data.py
    📂 system/ [CORE]
      - GENESIS_BOOT.py
      - SYNC_PROTOCOL.py
      - excalibur.py
    📂 tests/ [CORE]
      - debug_lac.py
      - demo_haystack_ukg.py
      - demo_rag_interactive.py
      - grand_unification_test.py
      - output.txt
      - output_utf8.txt
      - simulate_chrysalis.py
      - simulation_chrysalis.go
      - stress_test_fusion.py
      - test_api.py
      - test_api_fusion.py
      - test_beaver.py
      - test_clawdbot_bridge.py
      - test_extension_bridge.py
      - test_haystack_ukg.py
      - test_helix.py
      - test_hybrid_routing.py
      - test_iron_gate_flow.py
      - test_lac_loop.py
      - test_lac_loop_real.py
      - test_merger.py
      - test_phantom_handoff.py
      - test_phase1_integration.py
      - test_seeder.py
      - verification.mlo
    📂 titan/ [CORE]
      - seed_knowledge.py
      - sync_engine.py
      📂 Data_Pipeline/ [CORE]
        - storage.py
        - titan_ledger.db
      📂 Titan_Graph/ [CORE]
        📂 chromadb/ [CORE]
          - chroma.sqlite3
          📂 5dfb72b2-4fea-4aea-9eed-c45e3d4a26e2/ [CORE]
      📂 data/ [CORE]
        - omega_graph.json
        - titan_ledger.json
        - ukg_seed.json
        - wvs_map.json
      📂 graph/ [CORE]
        - __init__.py
        - knowledge_graph.py
      📂 memory/ [CORE]
        - UKG_ANYA_v6_seed.json
        - UKG_CORE.toon
        - __init__.py
        - anya_memory.py
        - appwrite_sync.py
        - base_memory.py
        - clara_assimilation.json
        - compiler.py
        - constrict_pipeline.py
        - mobile_bridge_api.py
        - notebook_manager.py
        - reflection_engine.py
        - requirements.txt
        - seeder.py
        - sentinel_compression.py
        - skillgraph.py
        - supermemory_adapter.py
        - sync_engine.py
        - test_titan_omega.py
        - titan_omega.py
        - titan_schemas.py
        - ukg_graph.json
        - workspace_memory.jsonld
        📂 data/ [CORE]
          - omega_graph.json
          - omega_vault.index
          - omega_vault.json
        📂 graphrag/ [CORE]
          - compressor.py
      📂 phials/ [CORE]
        - map_generator.py
        - memory_decay.py
        - nano_graph_adapter.py
        - semantic_tree_rag.py
        - tree_sitter_phial.py
        📂 regex_cleaner/ [CORE]
          - main.py
      📂 storage/ [CORE]
        - __init__.py
        - code_migrator.py
        - exp_ledger.py
        - exp_ledger_schema.sql
        - sync_protocol.py
  📂 02_FORGE/ [FORGE]
    - ARCHITECTURE.md
    - README.md
    📂 KINETIC_ARMORY/ [FORGE]
      📂 Saltare/ [FORGE]
        - .dockerignore
        - Dockerfile
        - LICENSE
        - Makefile
        - config.yaml
        - go.mod
        - go.sum
        - saltare.exe
        - saltare.jpg
        - saltare_gateway.exe
        📂 bin/ [FORGE]
          - saltare-mcp.exe
          - saltare.exe
        📂 cmd/ [FORGE]
          📂 saltare/ [FORGE]
            - main.go
          📂 saltare-mcp/ [FORGE]
            - main.go
        📂 configs/ [FORGE]
          - saltare.yaml
        📂 data/ [FORGE]
          📂 badger/ [FORGE]
            - 000003.vlog
            - 000004.vlog
            - DISCARD
            - KEYREGISTRY
            - MANIFEST
        📂 demo/ [FORGE]
          - demo.sh
          - demo_stdio_proxy.sh
        📂 deployments/ [FORGE]
          📂 kubernetes/ [FORGE]
            - configmap.yaml
            - hpa.yaml
            - ingress.yaml
            - kustomization.yaml
            - meilisearch.yaml
            - namespace.yaml
            - networkpolicy.yaml
            - saltare-deployment.yaml
            - saltare-service.yaml
            - secrets.yaml
            - typesense.yaml
        📂 docker/ [FORGE]
          - docker-compose.meilisearch.yml
          - docker-compose.typesense.yml
        📂 docs/ [FORGE]
          - SALTARE_TECHNICAL_SPEC.md
        📂 internal/ [FORGE]
          📂 analytics/ [FORGE]
            - collector.go
            - collector_test.go
          📂 execution/ [FORGE]
            - executor.go
          📂 gateway/ [FORGE]
          📂 jobs/ [FORGE]
            - jobs_test.go
            - manager.go
            - queue.go
            - sse.go
            - storage.go
            - types.go
          📂 router/ [FORGE]
          📂 storage/ [FORGE]
          📂 toolkit/ [FORGE]
            - loader.go
            - manager.go
          📂 version/ [FORGE]
            - version.go
            - version_test.go
        📂 pkg/ [FORGE]
          📂 mcpclient/ [FORGE]
            - client.go
            - http_transport.go
            - stdio_transport.go
            - stdio_transport_test.go
            - transport.go
          📂 types/ [FORGE]
            - types.go
        📂 tests/ [FORGE]
          📂 integration/ [FORGE]
            - cerebras_llm_test.go
          📂 mcp/ [FORGE]
            - mock_server.go
          📂 mock/ [FORGE]
            - weather_server.go
      📂 SpacetimeDB/ [FORGE]
        - .dockerignore
        - .envrc
        - .gitattributes
        - .prettierignore
        - .prettierrc
        - .rustfmt.toml
        - Cargo.lock
        - Cargo.toml
        - Dockerfile
        - LICENSE.txt
        - README.md
        - clippy.toml
        - d3-flamegraph-base.html
        - docker-compose.yml
        - eslint.config.js
        - flake.lock
        - flake.nix
        - global.json
        - librusty_v8.nix
        - package.json
        - pnpm-workspace.yaml
        - query-builder-syntax-analysis.md
        - run_standalone_temp.sh
        - rust-toolchain.toml
        - tsconfig.json
        📂 .cargo/ [FORGE]
          - config.toml
        📂 .github/ [FORGE]
          - CODEOWNERS
          - Dockerfile
          - GREMLINS.md
          - docker-compose.yml
          - pull_request_template.md
          📂 workflows/ [FORGE]
            - attach-artifacts.yml
            - benchmarks.yml
            - check-merge-labels.yml
            - check-pr-base.yml
            - ci.yml
            - discord-posts.yml
            - docker.yml
            - docs-publish.yaml
            - docs-test.yaml
            - llm-benchmark-update.yml
            - package.yml
            - rust_matcher.json
            - tag-release.yml
            - typescript-lint.yml
            - typescript-test.yml
            - upgrade-version-check.yml
        📂 crates/ [FORGE]
          📂 auth/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 bench/ [FORGE]
            - Cargo.toml
            - Dockerfile
            - LICENSE
            - README.md
            - callgrind-docker.sh
            - clippy.toml
            - flamegraph.sh
            - hyper_cmp.py
            - instruments.sh
          📂 bindings/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
            - bindings-doctests.sh
          📂 bindings-cpp/ [FORGE]
            - ARCHITECTURE.md
            - CMakeLists.txt
            - DEVELOP.md
            - LICENSE
            - QUICKSTART.md
            - README.md
            - REFERENCE.md
          📂 bindings-csharp/ [FORGE]
            - .editorconfig
            - Directory.Build.props
            - LICENSE
            - README.md
            - SpacetimeSharpSATS.sln
            - logo.png
          📂 bindings-macro/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 bindings-sys/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 bindings-typescript/ [FORGE]
            - .editorconfig
            - .gitattributes
            - .npmignore
            - DEVELOP.md
            - LICENSE.txt
            - README.md
            - package.json
            - tsconfig.build.json
            - tsconfig.json
            - tsconfig.typecheck.json
            - tsup.config.ts
            - vitest.config.ts
          📂 cli/ [FORGE]
            - Cargo.toml
            - LICENSE
            - build.rs
            - clippy.toml
          📂 client-api/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 client-api-messages/ [FORGE]
            - Cargo.toml
            - DEVELOP.md
            - LICENSE
            - README.md
            - ws_schema-2.json
            - ws_schema.json
          📂 codegen/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 commitlog/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 core/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 data-structures/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 datastore/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 durability/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 execution/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 expr/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 fs-utils/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 guard/ [FORGE]
            - Cargo.toml
          📂 lib/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
            - build.rs
          📂 memory-usage/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 metrics/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 paths/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 pg/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 physical-plan/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 primitives/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 query/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 query-builder/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 sats/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 schema/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 smoketests/ [FORGE]
            - Cargo.toml
            - DEVELOP.md
          📂 snapshot/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 sql-parser/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 sqltest/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
            - build_standard.py
            - clippy.toml
            - override_with_output.sh
            - reformat.sh
            - run_all_sequential.sh
          📂 standalone/ [FORGE]
            - Cargo.toml
            - Dockerfile
            - LICENSE
            - README.md
            - config.toml
          📂 subscription/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 table/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 testing/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 update/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
            - build.rs
            - spacetime-install.ps1
            - spacetime-install.sh
          📂 vm/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
        📂 demo/ [FORGE]
          📂 Blackholio/ [FORGE]
            - DEVELOP.md
            - LICENSE
            - README.md
        📂 docs/ [FORGE]
          - .editorconfig
          - DEVELOP.md
          - LICENSE.txt
          - README.md
          - STYLE.md
          - docusaurus.config.ts
          - package.json
          - sidebars.ts
          - tsconfig.json
          - versions.json
          📂 docs/ [FORGE]
          📂 llms/ [FORGE]
            - docs-benchmark-analysis.md
            - docs-benchmark-comment.md
            - docs-benchmark-details.json
            - docs-benchmark-details.lock
            - docs-benchmark-summary.json
            - llm-comparison-details.json
            - llm-comparison-summary.json
            - oneshot-grades.json
            - oneshot-summary.md
          📂 scripts/ [FORGE]
            - generate-cli-docs.mjs
            - get-old-docs.sh
            - rewrite-doc-links.mjs
          📂 src/ [FORGE]
          📂 static/ [FORGE]
            - .nojekyll
            - llms.md
          📂 test-csharp-snippets/ [FORGE]
            - Module.cs
            - TestProcedures.csproj
          📂 versioned_docs/ [FORGE]
          📂 versioned_sidebars/ [FORGE]
            - version-1.12.0-sidebars.json
        📂 git-hooks/ [FORGE]
          - install-hooks.sh
          📂 hooks/ [FORGE]
            - applypatch-msg.sample
            - commit-msg.sample
            - fsmonitor-watchman.sample
            - post-update.sample
            - pre-applypatch.sample
            - pre-commit
            - pre-commit.sample
            - pre-merge-commit.sample
            - pre-push.sample
            - pre-rebase.sample
            - pre-receive.sample
            - prepare-commit-msg.sample
            - push-to-checkout.sample
            - update.sample
        📂 images/ [FORGE]
          - basic-architecture-diagram.png
          📂 dark/ [FORGE]
            - logo-text.svg
            - logo.svg
          📂 light/ [FORGE]
            - logo-text.svg
            - logo.svg
          📂 social/ [FORGE]
            - discord.svg
            - github.svg
            - linkedin.svg
            - stackoverflow.svg
            - twitch.svg
            - twitter.svg
            - youtube.svg
        📂 licenses/ [FORGE]
          - BSL.txt
          - apache2.txt
        📂 modules/ [FORGE]
          - Directory.Build.props
          - Directory.Build.targets
          📂 benchmarks/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
            - config.toml
          📂 benchmarks-cpp/ [FORGE]
            - CMakeLists.txt
            - build.bat
          📂 benchmarks-cs/ [FORGE]
            - LICENSE
            - README.md
            - benchmarks-cs.csproj
            - circles.cs
            - ia_loop.cs
            - lib.cs
            - synthetic.cs
          📂 benchmarks-ts/ [FORGE]
            - package.json
            - tsconfig.json
          📂 keynote-benchmarks/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 module-test/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
            - index.html
          📂 module-test-cpp/ [FORGE]
            - CMakeLists.txt
            - compare_module_schemas.py
            - compile.bat
          📂 module-test-cs/ [FORGE]
            - LICENSE
            - Lib.cs
            - README.md
            - module-test-cs.csproj
            - module-test-cs.sln
          📂 module-test-ts/ [FORGE]
            - package.json
            - tsconfig.json
          📂 perf-test/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 sdk-test/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 sdk-test-connect-disconnect/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 sdk-test-connect-disconnect-cpp/ [FORGE]
            - CMakeLists.txt
            - README.md
          📂 sdk-test-connect-disconnect-cs/ [FORGE]
            - LICENSE
            - Lib.cs
            - README.md
            - sdk-test-connect-disconnect-cs.csproj
          📂 sdk-test-connect-disconnect-ts/ [FORGE]
            - package.json
            - tsconfig.json
          📂 sdk-test-cpp/ [FORGE]
            - CMakeLists.txt
            - README.md
            - compile.bat
          📂 sdk-test-cs/ [FORGE]
            - LICENSE
            - Lib.cs
            - README.md
            - sdk-test-cs.csproj
            - sdk-test-cs.sln
          📂 sdk-test-event-table/ [FORGE]
            - Cargo.toml
          📂 sdk-test-procedure/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 sdk-test-procedure-cpp/ [FORGE]
            - CMakeLists.txt
            - README.md
            - compile.bat
          📂 sdk-test-procedure-ts/ [FORGE]
            - package.json
            - tsconfig.json
          📂 sdk-test-ts/ [FORGE]
            - package.json
            - tsconfig.json
          📂 sdk-test-view/ [FORGE]
            - Cargo.toml
            - LICENSE
            - README.md
          📂 sdk-test-view-cpp/ [FORGE]
            - CMakeLists.txt
            - README.md
            - compile.bat
        📂 sdks/ [FORGE]
          - typescript
          📂 csharp/ [FORGE]
            - .meta-check-ignore
            - DEVELOP.md
            - DEVELOP.md.meta
            - Directory.Build.props
            - Directory.Build.props.meta
            - LICENSE.txt
            - LICENSE.txt.meta
            - README.dotnet.md
            - README.dotnet.md.meta
            - README.md
            - README.md.meta
            - SpacetimeDB.ClientSDK.csproj
            - SpacetimeDB.ClientSDK.csproj.meta
            - SpacetimeDB.ClientSDK.sln
            - SpacetimeDB.ClientSDK.sln.meta
            - after.SpacetimeDB.ClientSDK.sln.targets
            - after.SpacetimeDB.ClientSDK.sln.targets.meta
            - logo.png
            - logo.png.meta
            - package.json
            - package.json.meta
            - packages.meta
            - src.meta
          📂 rust/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 unreal/ [FORGE]
            - Cargo.toml
            - DEVELOP.md
            - README.md
        📂 skills/ [FORGE]
          📂 spacetimedb-cli/ [FORGE]
            - SKILL.md
          📂 spacetimedb-concepts/ [FORGE]
            - SKILL.md
          📂 spacetimedb-csharp/ [FORGE]
            - SKILL.md
          📂 spacetimedb-rust/ [FORGE]
            - SKILL.md
          📂 spacetimedb-typescript/ [FORGE]
            - SKILL.md
          📂 spacetimedb-unity/ [FORGE]
            - SKILL.md
        📂 smoketests/ [FORGE]
          - README.md
          - __init__.py
          - __main__.py
          - config.toml
          - docker.py
          - requirements.txt
          - unittest_parallel.py
          📂 tests/ [FORGE]
            - __init__.py
            - add_remove_index.py
            - auto_inc.py
            - auto_migration.py
            - call.py
            - clear_database.py
            - client_connected_error_rejects_connection.py
            - confirmed_reads.py
            - connect_disconnect_from_cli.py
            - create_project.py
            - csharp_module.py
            - default_module_clippy.py
            - delete_database.py
            - describe.py
            - detect_wasm_bindgen.py
            - dml.py
            - domains.py
            - fail_initial_publish.py
            - filtering.py
            - module_nested_op.py
            - modules.py
            - namespaces.py
            - new_user_flow.py
            - panic.py
            - permissions.py
            - quickstart.py
            - replication.py
            - rls.py
            - schedule_reducer.py
            - servers.py
            - sql.py
            - teams.py
            - timestamp_route.py
            - views.py
            - zz_docker.py
        📂 templates/ [FORGE]
          📂 angular-ts/ [FORGE]
            - .template.json
            - angular.json
            - package.json
            - tsconfig.app.json
            - tsconfig.json
          📂 basic-cpp/ [FORGE]
            - .template.json
            - Cargo.toml
            - LICENSE
          📂 basic-cs/ [FORGE]
            - .template.json
            - LICENSE
            - Program.cs
            - client.csproj
          📂 basic-rs/ [FORGE]
            - .template.json
            - Cargo.toml
            - LICENSE
            - README.md
          📂 basic-ts/ [FORGE]
            - .template.json
            - LICENSE
            - package.json
            - tsconfig.json
          📂 browser-ts/ [FORGE]
            - .template.json
            - LICENSE
            - index.html
            - package.json
            - tsconfig.json
            - vite.config.ts
          📂 bun-ts/ [FORGE]
            - .template.json
            - LICENSE
            - package.json
            - tsconfig.json
          📂 chat-console-cs/ [FORGE]
            - .template.json
            - LICENSE
            - Program.cs
            - README.md
            - client.csproj
          📂 chat-console-rs/ [FORGE]
            - .template.json
            - Cargo.toml
            - LICENSE
            - README.md
          📂 chat-react-ts/ [FORGE]
            - .template.json
            - CHANGELOG.md
            - LICENSE
            - README.md
            - index.html
            - package.json
            - tsconfig.app.json
            - tsconfig.json
            - tsconfig.node.json
            - vite.config.ts
            - vitest.config.ts
          📂 deno-ts/ [FORGE]
            - .template.json
            - LICENSE
            - package.json
          📂 keynote-2/ [FORGE]
            - .dockerignore
            - .env.example
            - .prettierrc
            - DEVELOP.md
            - Dockerfile.bench
            - Dockerfile.bun
            - Dockerfile.rpc
            - Dockerfile.sqlite-seed
            - README.md
            - contention-chart.png
            - docker-compose-crdb-loadbalancer.yml
            - docker-compose-crdb-rpc-server.yml
            - docker-compose-linux-raid-crdb.yml
            - docker-compose-linux-raid.yml
            - docker-compose.yml
            - nginx-crdb-local.conf
            - nginx-crdb.conf
            - package.json
            - tsconfig.json
          📂 nextjs-ts/ [FORGE]
            - .template.json
            - LICENSE
            - next.config.ts
            - package.json
            - tsconfig.json
          📂 nodejs-ts/ [FORGE]
            - .template.json
            - LICENSE
            - package.json
            - tsconfig.json
          📂 nuxt-ts/ [FORGE]
            - .template.json
            - LICENSE
            - app.vue
            - env.d.ts
            - nuxt.config.ts
            - package.json
            - tsconfig.json
          📂 react-ts/ [FORGE]
            - .template.json
            - LICENSE
            - index.html
            - package.json
            - tsconfig.json
            - vite.config.ts
          📂 remix-ts/ [FORGE]
            - .template.json
            - LICENSE
            - package.json
            - tsconfig.json
            - vite.config.ts
          📂 svelte-ts/ [FORGE]
            - .template.json
            - LICENSE
            - index.html
            - package.json
            - svelte.config.js
            - tsconfig.json
            - vite.config.ts
          📂 tanstack-ts/ [FORGE]
            - .template.json
            - LICENSE
            - package.json
            - tsconfig.json
            - vite.config.ts
          📂 vue-ts/ [FORGE]
            - .template.json
            - LICENSE
            - env.d.ts
            - index.html
            - package.json
            - tsconfig.json
            - vite.config.ts
        📂 tools/ [FORGE]
          - check-diff.sh
          - clippy.sh
          - crate-publish-checks.py
          - find-publish-list.py
          - merge-docker-images.sh
          - perf.sh
          - publish-crates.sh
          - run-all-tests.sh
          - update-test-snapshots.sh
          📂 ci/ [FORGE]
            - Cargo.toml
            - README.md
          📂 gen-bindings/ [FORGE]
            - Cargo.toml
          📂 generate-client-api/ [FORGE]
            - Cargo.toml
          📂 license-check/ [FORGE]
            - Cargo.toml
            - main.rs
          📂 llm-oneshot/ [FORGE]
            - README.md
            - package.json
          📂 replace-spacetimedb/ [FORGE]
            - Cargo.toml
          📂 upgrade-version/ [FORGE]
            - Cargo.toml
            - LICENSE
          📂 xtask-llm-benchmark/ [FORGE]
            - Cargo.toml
            - build.rs
      📂 VibeVoice/ [FORGE]
        - CONTRIBUTING.md
        - LICENSE
        - README.md
        - SECURITY.md
        - pyproject.toml
        📂 Figures/ [FORGE]
          - DER.jpg
          - MOS-preference.png
          - VibeVoice-TTS-results.jpg
          - VibeVoice.jpg
          - VibeVoice_ASR_archi.png
          - VibeVoice_Realtime.png
          - VibeVoice_logo.png
          - VibeVoice_logo_white.png
          - cpWER.jpg
          - language_distribution_horizontal.png
          - tcpWER.jpg
        📂 demo/ [FORGE]
          - download_experimental_voices.sh
          - realtime_model_inference_from_file.py
          - vibevoice_asr_gradio_demo.py
          - vibevoice_asr_inference_from_file.py
          - vibevoice_realtime_colab.ipynb
          - vibevoice_realtime_demo.py
          📂 asr_demo/ [FORGE]
            - demo1-chat.mp3
            - demo1-chat.mp4
            - demo2-song.mp3
            - demo2-song.mp4
            - demo3-hotwords.wav
          📂 text_examples/ [FORGE]
            - 1p_abs.txt
            - 1p_vibevoice.txt
          📂 voices/ [FORGE]
          📂 web/ [FORGE]
            - app.py
            - index.html
        📂 docs/ [FORGE]
          - setup_gradio_demo.md
          - vibevoice-asr.md
          - vibevoice-realtime-0.5b.md
          - vibevoice-tts.md
          - vibevoice-vllm-asr.md
        📂 finetuning-asr/ [FORGE]
          - README.md
          - inference_lora.py
          - lora_finetune.py
          📂 toy_dataset/ [FORGE]
            - 0.json
            - 0.mp3
            - 1.json
            - 1.mp3
        📂 vibevoice/ [FORGE]
          - __init__.py
          📂 configs/ [FORGE]
            - qwen2.5_1.5b_64k.json
            - qwen2.5_7b_32k.json
          📂 modular/ [FORGE]
            - __init__.py
            - configuration_vibevoice.py
            - configuration_vibevoice_streaming.py
            - modeling_vibevoice.py
            - modeling_vibevoice_asr.py
            - modeling_vibevoice_streaming.py
            - modeling_vibevoice_streaming_inference.py
            - modular_vibevoice_diffusion_head.py
            - modular_vibevoice_text_tokenizer.py
            - modular_vibevoice_tokenizer.py
            - streamer.py
          📂 processor/ [FORGE]
            - __init__.py
            - audio_utils.py
            - vibevoice_asr_processor.py
            - vibevoice_processor.py
            - vibevoice_streaming_processor.py
            - vibevoice_tokenizer_processor.py
          📂 schedule/ [FORGE]
            - __init__.py
            - dpm_solver.py
            - timestep_sampler.py
          📂 scripts/ [FORGE]
            - __init__.py
            - convert_nnscaler_checkpoint_to_transformers.py
        📂 vibevoice.egg-info/ [FORGE]
          - PKG-INFO
          - SOURCES.txt
          - dependency_links.txt
          - entry_points.txt
          - requires.txt
          - top_level.txt
        📂 vllm_plugin/ [FORGE]
          - __init__.py
          - inputs.py
          - model.py
          📂 scripts/ [FORGE]
            - gradio_asr_demo_api_video.py
            - start_server.py
          📂 tests/ [FORGE]
            - test_api.py
            - test_api_auto_recover.py
          📂 tools/ [FORGE]
            - generate_tokenizer_files.py
      📂 claw-code-agent/ [FORGE]
        - README.md
        - pyproject.toml
        📂 claw_code_agent.egg-info/ [FORGE]
          - PKG-INFO
          - SOURCES.txt
          - dependency_links.txt
          - entry_points.txt
          - top_level.txt
        📂 images/ [FORGE]
          - demo1.gif
          - demo_2.gif
          - logo.png
        📂 src/ [FORGE]
          - QueryEngine.py
          - Tool.py
          - __init__.py
          - agent_context.py
          - agent_context_usage.py
          - agent_prompting.py
          - agent_runtime.py
          - agent_session.py
          - agent_slash_commands.py
          - agent_tools.py
          - agent_types.py
          - bootstrap_graph.py
          - command_graph.py
          - commands.py
          - context.py
          - costHook.py
          - cost_tracker.py
          - deferred_init.py
          - dialogLaunchers.py
          - direct_modes.py
          - execution_registry.py
          - history.py
          - ink.py
          - interactiveHelpers.py
          - main.py
          - models.py
          - openai_compat.py
          - parity_audit.py
          - permissions.py
          - port_manifest.py
          - prefetch.py
          - projectOnboardingState.py
          - query.py
          - query_engine.py
          - remote_runtime.py
          - replLauncher.py
          - runtime.py
          - session_store.py
          - setup.py
          - system_init.py
          - task.py
          - tasks.py
          - tool_pool.py
          - tools.py
          - transcript.py
          📂 assistant/ [FORGE]
            - __init__.py
          📂 bootstrap/ [FORGE]
            - __init__.py
          📂 bridge/ [FORGE]
            - __init__.py
          📂 buddy/ [FORGE]
            - __init__.py
          📂 cli/ [FORGE]
            - __init__.py
          📂 components/ [FORGE]
            - __init__.py
          📂 constants/ [FORGE]
            - __init__.py
          📂 coordinator/ [FORGE]
            - __init__.py
          📂 entrypoints/ [FORGE]
            - __init__.py
          📂 hooks/ [FORGE]
            - __init__.py
          📂 keybindings/ [FORGE]
            - __init__.py
          📂 memdir/ [FORGE]
            - __init__.py
          📂 migrations/ [FORGE]
            - __init__.py
          📂 moreright/ [FORGE]
            - __init__.py
          📂 native_ts/ [FORGE]
            - __init__.py
          📂 outputStyles/ [FORGE]
            - __init__.py
          📂 plugins/ [FORGE]
            - __init__.py
          📂 reference_data/ [FORGE]
            - __init__.py
            - archive_surface_snapshot.json
            - commands_snapshot.json
            - tools_snapshot.json
          📂 remote/ [FORGE]
            - __init__.py
          📂 schemas/ [FORGE]
            - __init__.py
          📂 screens/ [FORGE]
            - __init__.py
          📂 server/ [FORGE]
            - __init__.py
          📂 services/ [FORGE]
            - __init__.py
          📂 skills/ [FORGE]
            - __init__.py
          📂 state/ [FORGE]
            - __init__.py
          📂 types/ [FORGE]
            - __init__.py
          📂 upstreamproxy/ [FORGE]
            - __init__.py
          📂 utils/ [FORGE]
            - __init__.py
          📂 vim/ [FORGE]
            - __init__.py
          📂 voice/ [FORGE]
            - __init__.py
        📂 tests/ [FORGE]
          - test_agent_context.py
          - test_agent_context_usage.py
          - test_agent_prompting.py
          - test_agent_runtime.py
          - test_agent_slash_commands.py
          - test_porting_workspace.py
      📂 cribo/ [FORGE]
        - Dockerfile
      📂 goose/ [FORGE]
        - .dockerignore
        - .gitattributes
        - .goosehints
        - AGENTS.md
        - BUILDING_DOCKER.md
        - BUILDING_LINUX.md
        - CONTRIBUTING.md
        - CONTRIBUTING_RECIPES.md
        - Cargo.lock
        - Cargo.toml
        - Cross.toml
        - Dockerfile
        - GOVERNANCE.md
        - HOWTOAI.md
        - Justfile
        - LICENSE
        - MAINTAINERS.md
        - README.md
        - RELEASE.md
        - RELEASE_CHECKLIST.md
        - SECURITY.md
        - clippy.toml
        - deny.toml
        - download_cli.ps1
        - download_cli.sh
        - flake.lock
        - flake.nix
        - goose-self-test.yaml
        - recipe.yaml
        - run_cross_local.md
        - rust-toolchain.toml
        - test_acp_client.py
        📂 .devcontainer/ [FORGE]
          - Dockerfile
          - devcontainer.json
        📂 .github/ [FORGE]
          - CODEOWNERS
          - copilot-instructions.md
          - pull_request_template.md
          📂 DISCUSSION_TEMPLATE/ [FORGE]
            - qa.yml
          📂 ISSUE_TEMPLATE/ [FORGE]
            - bug_report.md
            - config.yml
            - feature_request.md
            - submit-recipe.yml
          📂 actions/ [FORGE]
          📂 workflows/ [FORGE]
            - autoclose
            - build-cli.yml
            - build-notify.yml
            - bundle-desktop-intel.yml
            - bundle-desktop-linux.yml
            - bundle-desktop-manual.yml
            - bundle-desktop-windows.yml
            - bundle-desktop.yml
            - canary.yml
            - cargo-deny.yml
            - check-release-pr.yaml
            - ci.yml
            - create-release-pr.yaml
            - deploy-docs-and-extensions.yml
            - docs-update-recipe-ref.yml
            - goose-issue-solver.yml
            - goose-pr-reviewer.yml
            - merge-release-pr-on-tag.yaml
            - minor-release.yaml
            - patch-release.yaml
            - pr-comment-build-cli.yml
            - pr-comment-bundle-intel.yml
            - pr-comment-bundle-windows.yml
            - pr-comment-bundle.yml
            - pr-smoke-test.yml
            - pr-website-preview.yml
            - publish-ask-ai-bot.yml
            - publish-docker.yml
            - quarantine.yml
            - rebuild-skills-marketplace.yml
            - recipe-security-scanner.yml
            - release-branches.yml
            - release.yml
            - scorecard.yml
            - stale.yml
            - take.yml
            - test-finder.yml
            - update-hacktoberfest-leaderboard.yml
            - update-health-dashboard.yml
            - update-release-pr.yaml
        📂 .husky/ [FORGE]
          - pre-commit
        📂 .intersect/ [FORGE]
          - intersect-config.yaml
        📂 bin/ [FORGE]
          - .just-1.40.0.pkg
          - .node-24.10.0.pkg
          - .protoc-31.1.pkg
          - .rustup-1.28.2.pkg
          - .temporal-cli-1.3.0.pkg
          - README.hermit.md
          - activate-hermit
          - activate-hermit.fish
          - cargo
          - cargo-clippy
          - cargo-fmt
          - cargo-miri
          - clippy-driver
          - corepack
          - hermit
          - hermit.hcl
          - just
          - node
          - npm
          - npx
          - protoc
          - rls
          - rust-analyzer
          - rust-gdb
          - rust-gdbgui
          - rust-lldb
          - rustc
          - rustdoc
          - rustfmt
          - rustup
          - temporal
        📂 crates/ [FORGE]
          📂 goose/ [FORGE]
            - Cargo.toml
            - canonical_mapping_report.json
          📂 goose-acp/ [FORGE]
            - Cargo.toml
          📂 goose-cli/ [FORGE]
            - Cargo.toml
            - WEB_INTERFACE.md
          📂 goose-mcp/ [FORGE]
            - Cargo.toml
            - README.md
          📂 goose-server/ [FORGE]
            - ALLOWLIST.md
            - Cargo.toml
            - build.rs
          📂 goose-test/ [FORGE]
            - Cargo.toml
          📂 goose-test-support/ [FORGE]
            - Cargo.toml
        📂 documentation/ [FORGE]
          - .goosehints
          - .npmrc
          - AGENTS.md
          - README.md
          - docusaurus.config.ts
          - package.json
          - postcss.config.js
          - sidebars.ts
          - tailwind.config.js
          - tsconfig.json
          📂 .goose/ [FORGE]
          📂 automation/ [FORGE]
            - README.md
          📂 blog/ [FORGE]
            - README.md
            - authors.yml
            - tags.yml
          📂 docs/ [FORGE]
            - quickstart.md
          📂 plugins/ [FORGE]
            - custom-webpack.cjs
            - markdown-export.cjs
            - tailwind-config.cjs
          📂 scripts/ [FORGE]
            - community_stars.py
            - community_stars_teams.txt
            - generate-docs-map.js
            - generate-docs-map.test.js
            - generate-skills-manifest.js
            - generate-skills-zips.js
            - serve-static.js
            - verify-build.sh
          📂 src/ [FORGE]
          📂 static/ [FORGE]
            - .nojekyll
            - llms.txt
            - robots.txt
            - servers.json
        📂 evals/ [FORGE]
          📂 open-model-gym/ [FORGE]
            - Justfile
            - README.md
            - config.yaml
            - gym.png
        📂 examples/ [FORGE]
          - frontend_tools.py
          📂 mcp-wiki/ [FORGE]
            - .python-version
            - README.md
            - pyproject.toml
        📂 recipe-scanner/ [FORGE]
          - Dockerfile
          - base_recipe.yaml
          - config.yaml
          - decode-training-data.py
          - scan-recipe.sh
        📂 scripts/ [FORGE]
          - README.md
          - check-no-native-tls.sh
          - check-openapi-schema.sh
          - clean-gh-pages.sh
          - diagnostics-viewer.py
          - goose-db-helper.sh
          - parse-benchmark-results.sh
          - run-benchmarks.sh
          - test_compaction.sh
          - test_lead_worker.sh
          - test_mcp.sh
          - test_providers.sh
          - test_subrecipes.sh
          - test_web.sh
          📂 bench-postprocess-scripts/ [FORGE]
            - generate_leaderboard.py
            - prepare_aggregate_metrics.py
          📂 provider-error-proxy/ [FORGE]
            - README.md
            - proxy.py
            - pyproject.toml
            - uv.lock
          📂 test-subrecipes-examples/ [FORGE]
            - project_analyzer.yaml
            - project_analyzer_parallel.yaml
        📂 services/ [FORGE]
          📂 ask-ai-bot/ [FORGE]
            - .dockerignore
            - .env.example
            - Dockerfile
            - bun.lock
            - index.ts
            - package.json
            - tsconfig.json
        📂 ui/ [FORGE]
          📂 desktop/ [FORGE]
            - .eslintrc.json
            - .goosehints
            - .npmrc
            - .prettierignore
            - .prettierrc.json
            - README.md
            - components.json
            - entitlements.plist
            - eslint.config.js
            - forge.config.ts
            - forge.deb.desktop
            - forge.env.d.ts
            - forge.rpm.desktop
            - image.d.ts
            - index.html
            - openapi-ts.config.ts
            - openapi.json
            - package.json
            - playwright.config.ts
            - tsconfig.json
            - tsconfig.node.json
            - vite.config.mts
            - vite.main.config.mts
            - vite.preload.config.mts
            - vite.renderer.config.mts
            - vitest.config.ts
          📂 install-link-generator/ [FORGE]
            - index.html
            - script.js
            - styles.css
      📂 hermes-agent/ [FORGE]
        - .env.example
        - .gitmodules
        - AGENTS.md
        - CONTRIBUTING.md
        - LICENSE
        - README.md
        - RELEASE_v0.2.0.md
        - RELEASE_v0.3.0.md
        - batch_runner.py
        - cli-config.yaml.example
        - cli.py
        - hermes
        - hermes_constants.py
        - hermes_state.py
        - hermes_time.py
        - mini_swe_runner.py
        - minisweagent_path.py
        - model_tools.py
        - package.json
        - pyproject.toml
        - requirements.txt
        - rl_cli.py
        - run_agent.py
        - setup-hermes.sh
        - toolset_distributions.py
        - toolsets.py
        - trajectory_compressor.py
        - utils.py
        - uv.lock
        📂 .github/ [FORGE]
          - PULL_REQUEST_TEMPLATE.md
          📂 ISSUE_TEMPLATE/ [FORGE]
            - bug_report.yml
            - config.yml
            - feature_request.yml
            - setup_help.yml
          📂 workflows/ [FORGE]
            - deploy-site.yml
            - docs-site-checks.yml
            - tests.yml
        📂 .plans/ [FORGE]
          - openai-api-server.md
          - streaming-support.md
        📂 acp_adapter/ [FORGE]
          - __init__.py
          - __main__.py
          - auth.py
          - entry.py
          - events.py
          - permissions.py
          - server.py
          - session.py
          - tools.py
        📂 acp_registry/ [FORGE]
          - agent.json
          - icon.svg
        📂 agent/ [FORGE]
          - __init__.py
          - anthropic_adapter.py
          - auxiliary_client.py
          - context_compressor.py
          - display.py
          - insights.py
          - model_metadata.py
          - prompt_builder.py
          - prompt_caching.py
          - redact.py
          - skill_commands.py
          - smart_model_routing.py
          - title_generator.py
          - trajectory.py
          - usage_pricing.py
        📂 assets/ [FORGE]
          - banner.png
        📂 cron/ [FORGE]
          - __init__.py
          - jobs.py
          - scheduler.py
        📂 datagen-config-examples/ [FORGE]
          - example_browser_tasks.jsonl
          - run_browser_tasks.sh
          - trajectory_compression.yaml
          - web_research.yaml
        📂 docs/ [FORGE]
          - acp-setup.md
          - honcho-integration-spec.html
          - honcho-integration-spec.md
          📂 migration/ [FORGE]
            - openclaw.md
          📂 plans/ [FORGE]
            - 2026-03-16-pricing-accuracy-architecture-design.md
          📂 skins/ [FORGE]
            - example-skin.yaml
        📂 environments/ [FORGE]
          - README.md
          - __init__.py
          - agent_loop.py
          - agentic_opd_env.py
          - hermes_base_env.py
          - patches.py
          - tool_context.py
          - web_research_env.py
          📂 benchmarks/ [FORGE]
            - __init__.py
          📂 hermes_swe_env/ [FORGE]
            - __init__.py
            - default.yaml
            - hermes_swe_env.py
          📂 terminal_test_env/ [FORGE]
            - __init__.py
            - default.yaml
            - terminal_test_env.py
          📂 tool_call_parsers/ [FORGE]
            - __init__.py
            - deepseek_v3_1_parser.py
            - deepseek_v3_parser.py
            - glm45_parser.py
            - glm47_parser.py
            - hermes_parser.py
            - kimi_k2_parser.py
            - llama_parser.py
            - longcat_parser.py
            - mistral_parser.py
            - qwen3_coder_parser.py
            - qwen_parser.py
        📂 gateway/ [FORGE]
          - __init__.py
          - channel_directory.py
          - config.py
          - delivery.py
          - hooks.py
          - mirror.py
          - pairing.py
          - run.py
          - session.py
          - status.py
          - sticker_cache.py
          - stream_consumer.py
          📂 platforms/ [FORGE]
            - ADDING_A_PLATFORM.md
            - __init__.py
            - api_server.py
            - base.py
            - dingtalk.py
            - discord.py
            - email.py
            - homeassistant.py
            - matrix.py
            - mattermost.py
            - signal.py
            - slack.py
            - sms.py
            - telegram.py
            - whatsapp.py
        📂 hermes_agent.egg-info/ [FORGE]
          - PKG-INFO
          - SOURCES.txt
          - dependency_links.txt
          - entry_points.txt
          - requires.txt
          - top_level.txt
        📂 hermes_cli/ [FORGE]
          - __init__.py
          - auth.py
          - banner.py
          - callbacks.py
          - checklist.py
          - claw.py
          - clipboard.py
          - codex_models.py
          - colors.py
          - commands.py
          - config.py
          - cron.py
          - curses_ui.py
          - default_soul.py
          - doctor.py
          - env_loader.py
          - gateway.py
          - main.py
          - models.py
          - pairing.py
          - plugins.py
          - runtime_provider.py
          - setup.py
          - skills_config.py
          - skills_hub.py
          - skin_engine.py
          - status.py
          - tools_config.py
          - uninstall.py
        📂 honcho_integration/ [FORGE]
          - __init__.py
          - cli.py
          - client.py
          - session.py
        📂 landingpage/ [FORGE]
          - apple-touch-icon.png
          - favicon-16x16.png
          - favicon-32x32.png
          - favicon.ico
          - hermes-agent-banner.png
          - icon-192.png
          - icon-512.png
          - index.html
          - nous-logo.png
          - script.js
          - style.css
        📂 mini-swe-agent/ [FORGE]
        📂 optional-skills/ [FORGE]
          - DESCRIPTION.md
          📂 autonomous-ai-agents/ [FORGE]
            - DESCRIPTION.md
          📂 blockchain/ [FORGE]
          📂 creative/ [FORGE]
          📂 email/ [FORGE]
          📂 health/ [FORGE]
            - DESCRIPTION.md
          📂 migration/ [FORGE]
            - DESCRIPTION.md
          📂 productivity/ [FORGE]
          📂 research/ [FORGE]
          📂 security/ [FORGE]
            - DESCRIPTION.md
        📂 scripts/ [FORGE]
          - discord-voice-doctor.py
          - hermes-gateway
          - install.cmd
          - install.ps1
          - install.sh
          - kill_modal.sh
          - release.py
          - sample_and_compress.py
          📂 whatsapp-bridge/ [FORGE]
            - bridge.js
            - package.json
        📂 skills/ [FORGE]
          📂 apple/ [FORGE]
            - DESCRIPTION.md
          📂 autonomous-ai-agents/ [FORGE]
            - DESCRIPTION.md
          📂 creative/ [FORGE]
            - DESCRIPTION.md
          📂 data-science/ [FORGE]
            - DESCRIPTION.md
          📂 diagramming/ [FORGE]
            - DESCRIPTION.md
          📂 dogfood/ [FORGE]
            - SKILL.md
          📂 domain/ [FORGE]
            - DESCRIPTION.md
          📂 email/ [FORGE]
            - DESCRIPTION.md
          📂 feeds/ [FORGE]
            - DESCRIPTION.md
          📂 gaming/ [FORGE]
            - DESCRIPTION.md
          📂 gifs/ [FORGE]
            - DESCRIPTION.md
          📂 github/ [FORGE]
            - DESCRIPTION.md
          📂 index-cache/ [FORGE]
            - anthropics_skills_skills_.json
            - claude_marketplace_anthropics_skills.json
            - lobehub_index.json
            - openai_skills_skills_.json
          📂 inference-sh/ [FORGE]
            - DESCRIPTION.md
          📂 leisure/ [FORGE]
          📂 mcp/ [FORGE]
            - DESCRIPTION.md
          📂 media/ [FORGE]
            - DESCRIPTION.md
          📂 mlops/ [FORGE]
            - DESCRIPTION.md
          📂 music-creation/ [FORGE]
            - DESCRIPTION.md
          📂 note-taking/ [FORGE]
            - DESCRIPTION.md
          📂 productivity/ [FORGE]
            - DESCRIPTION.md
          📂 research/ [FORGE]
            - DESCRIPTION.md
          📂 smart-home/ [FORGE]
            - DESCRIPTION.md
          📂 social-media/ [FORGE]
            - DESCRIPTION.md
          📂 software-development/ [FORGE]
        📂 tests/ [FORGE]
          - __init__.py
          - conftest.py
          - run_interrupt_test.py
          - test_1630_context_overflow_loop.py
          - test_413_compression.py
          - test_860_dedup.py
          - test_agent_guardrails.py
          - test_agent_loop.py
          - test_agent_loop_tool_calling.py
          - test_agent_loop_vllm.py
          - test_anthropic_adapter.py
          - test_anthropic_error_handling.py
          - test_anthropic_oauth_flow.py
          - test_anthropic_provider_persistence.py
          - test_api_key_providers.py
          - test_atomic_json_write.py
          - test_atomic_yaml_write.py
          - test_auth_codex_provider.py
          - test_auth_nous_provider.py
          - test_auxiliary_config_bridge.py
          - test_batch_runner_checkpoint.py
          - test_cli_approval_ui.py
          - test_cli_init.py
          - test_cli_interrupt_subagent.py
          - test_cli_loading_indicator.py
          - test_cli_mcp_config_watch.py
          - test_cli_model_command.py
          - test_cli_new_session.py
          - test_cli_plan_command.py
          - test_cli_prefix_matching.py
          - test_cli_preloaded_skills.py
          - test_cli_provider_resolution.py
          - test_cli_retry.py
          - test_cli_secret_capture.py
          - test_cli_skin_integration.py
          - test_cli_status_bar.py
          - test_cli_tools_command.py
          - test_codex_execution_paths.py
          - test_codex_models.py
          - test_context_token_tracking.py
          - test_dict_tool_call_args.py
          - test_display.py
          - test_evidence_store.py
          - test_external_credential_detection.py
          - test_fallback_model.py
          - test_file_permissions.py
          - test_flush_memories_codex.py
          - test_hermes_state.py
          - test_honcho_client_config.py
          - test_insights.py
          - test_interactive_interrupt.py
          - test_interrupt_propagation.py
          - test_managed_server_tool_support.py
          - test_minisweagent_path.py
          - test_model_provider_persistence.py
          - test_model_tools.py
          - test_openai_client_lifecycle.py
          - test_personality_none.py
          - test_plugins.py
          - test_provider_parity.py
          - test_quick_commands.py
          - test_real_interrupt_subagent.py
          - test_reasoning_command.py
          - test_redirect_stdout_issue.py
          - test_resume_display.py
          - test_run_agent.py
          - test_run_agent_codex_responses.py
          - test_runtime_provider_resolution.py
          - test_setup_model_selection.py
          - test_streaming.py
          - test_timezone.py
          - test_tool_call_parsers.py
          - test_toolset_distributions.py
          - test_toolsets.py
          - test_trajectory_compressor.py
          - test_worktree.py
          - test_worktree_security.py
          📂 acp/ [FORGE]
            - __init__.py
            - test_auth.py
            - test_events.py
            - test_permissions.py
            - test_server.py
            - test_session.py
            - test_tools.py
          📂 agent/ [FORGE]
            - __init__.py
            - test_auxiliary_client.py
            - test_context_compressor.py
            - test_display_emoji.py
            - test_model_metadata.py
            - test_prompt_builder.py
            - test_prompt_caching.py
            - test_redact.py
            - test_skill_commands.py
            - test_smart_model_routing.py
            - test_subagent_progress.py
            - test_title_generator.py
            - test_usage_pricing.py
          📂 cron/ [FORGE]
            - __init__.py
            - test_jobs.py
            - test_scheduler.py
          📂 fakes/ [FORGE]
            - __init__.py
            - fake_ha_server.py
          📂 gateway/ [FORGE]
            - __init__.py
            - test_api_server.py
            - test_async_memory_flush.py
            - test_background_command.py
            - test_background_process_notifications.py
            - test_base_topic_sessions.py
            - test_channel_directory.py
            - test_config.py
            - test_config_cwd_bridge.py
            - test_delivery.py
            - test_dingtalk.py
            - test_discord_bot_filter.py
            - test_discord_free_response.py
            - test_discord_imports.py
            - test_discord_media_metadata.py
            - test_discord_opus.py
            - test_discord_send.py
            - test_discord_slash_commands.py
            - test_discord_thread_persistence.py
            - test_document_cache.py
            - test_email.py
            - test_extract_local_files.py
            - test_gateway_shutdown.py
            - test_homeassistant.py
            - test_honcho_lifecycle.py
            - test_hooks.py
            - test_interrupt_key_match.py
            - test_matrix.py
            - test_mattermost.py
            - test_media_extraction.py
            - test_mirror.py
            - test_pairing.py
            - test_pii_redaction.py
            - test_plan_command.py
            - test_platform_base.py
            - test_reasoning_command.py
            - test_resume_command.py
            - test_retry_replacement.py
            - test_retry_response.py
            - test_run_progress_topics.py
            - test_runner_fatal_adapter.py
            - test_runner_startup_failures.py
            - test_send_image_file.py
            - test_session.py
            - test_session_env.py
            - test_session_hygiene.py
            - test_signal.py
            - test_slack.py
            - test_sms.py
            - test_ssl_certs.py
            - test_status.py
            - test_status_command.py
            - test_sticker_cache.py
            - test_stt_config.py
            - test_telegram_conflict.py
            - test_telegram_documents.py
            - test_telegram_format.py
            - test_telegram_photo_interrupts.py
            - test_telegram_text_batching.py
            - test_title_command.py
            - test_transcript_offset.py
            - test_update_command.py
            - test_voice_command.py
            - test_whatsapp_connect.py
            - test_whatsapp_reply_prefix.py
          📂 hermes_cli/ [FORGE]
            - __init__.py
            - test_chat_skills_flag.py
            - test_claw.py
            - test_cmd_update.py
            - test_coalesce_session_args.py
            - test_commands.py
            - test_config.py
            - test_cron.py
            - test_doctor.py
            - test_env_loader.py
            - test_gateway.py
            - test_gateway_linger.py
            - test_gateway_runtime_health.py
            - test_gateway_service.py
            - test_mcp_tools_config.py
            - test_model_validation.py
            - test_models.py
            - test_path_completion.py
            - test_placeholder_usage.py
            - test_session_browse.py
            - test_sessions_delete.py
            - test_set_config_value.py
            - test_setup.py
            - test_setup_model_provider.py
            - test_setup_noninteractive.py
            - test_setup_openclaw_migration.py
            - test_setup_prompt_menus.py
            - test_skills_config.py
            - test_skills_hub.py
            - test_skills_install_flags.py
            - test_skills_skip_confirm.py
            - test_skills_subparser.py
            - test_skin_engine.py
            - test_status.py
            - test_status_model_provider.py
            - test_tools_config.py
            - test_tools_disable_enable.py
            - test_update_autostash.py
            - test_update_check.py
            - test_update_gateway_restart.py
          📂 honcho_integration/ [FORGE]
            - __init__.py
            - test_async_memory.py
            - test_cli.py
            - test_client.py
            - test_session.py
          📂 integration/ [FORGE]
            - __init__.py
            - test_batch_runner.py
            - test_checkpoint_resumption.py
            - test_daytona_terminal.py
            - test_ha_integration.py
            - test_modal_terminal.py
            - test_voice_channel_flow.py
            - test_web_tools.py
          📂 skills/ [FORGE]
            - test_google_oauth_setup.py
            - test_openclaw_migration.py
            - test_telephony_skill.py
          📂 tools/ [FORGE]
            - __init__.py
            - test_approval.py
            - test_browser_cleanup.py
            - test_browser_console.py
            - test_checkpoint_manager.py
            - test_clarify_tool.py
            - test_clipboard.py
            - test_code_execution.py
            - test_command_guards.py
            - test_cron_prompt_injection.py
            - test_cronjob_tools.py
            - test_daytona_environment.py
            - test_debug_helpers.py
            - test_delegate.py
            - test_docker_environment.py
            - test_docker_find.py
            - test_file_operations.py
            - test_file_tools.py
            - test_file_tools_live.py
            - test_file_write_safety.py
            - test_force_dangerous_override.py
            - test_fuzzy_match.py
            - test_hidden_dir_filter.py
            - test_homeassistant_tool.py
            - test_honcho_tools.py
            - test_interrupt.py
            - test_local_env_blocklist.py
            - test_local_persistent.py
            - test_mcp_probe.py
            - test_mcp_tool.py
            - test_mcp_tool_issue_948.py
            - test_memory_tool.py
            - test_mixture_of_agents_tool.py
            - test_modal_sandbox_fixes.py
            - test_parse_env_var.py
            - test_patch_parser.py
            - test_process_registry.py
            - test_read_loop_detection.py
            - test_registry.py
            - test_rl_training_tool.py
            - test_search_hidden_dirs.py
            - test_send_message_tool.py
            - test_session_search.py
            - test_singularity_preflight.py
            - test_skill_manager_tool.py
            - test_skill_view_path_check.py
            - test_skill_view_traversal.py
            - test_skills_guard.py
            - test_skills_hub.py
            - test_skills_hub_clawhub.py
            - test_skills_sync.py
            - test_skills_tool.py
            - test_ssh_environment.py
            - test_symlink_prefix_confusion.py
            - test_terminal_disk_usage.py
            - test_terminal_requirements.py
            - test_terminal_tool_requirements.py
            - test_tirith_security.py
            - test_todo_tool.py
            - test_transcription.py
            - test_transcription_tools.py
            - test_vision_tools.py
            - test_voice_cli_integration.py
            - test_voice_mode.py
            - test_web_tools_config.py
            - test_web_tools_tavily.py
            - test_website_policy.py
            - test_windows_compat.py
            - test_write_deny.py
            - test_yolo_mode.py
        📂 tinker-atropos/ [FORGE]
        📂 tools/ [FORGE]
          - __init__.py
          - approval.py
          - browser_tool.py
          - checkpoint_manager.py
          - clarify_tool.py
          - code_execution_tool.py
          - cronjob_tools.py
          - debug_helpers.py
          - delegate_tool.py
          - file_operations.py
          - file_tools.py
          - fuzzy_match.py
          - homeassistant_tool.py
          - honcho_tools.py
          - image_generation_tool.py
          - interrupt.py
          - mcp_tool.py
          - memory_tool.py
          - mixture_of_agents_tool.py
          - neutts_synth.py
          - openrouter_client.py
          - patch_parser.py
          - process_registry.py
          - registry.py
          - rl_training_tool.py
          - send_message_tool.py
          - session_search_tool.py
          - skill_manager_tool.py
          - skills_guard.py
          - skills_hub.py
          - skills_sync.py
          - skills_tool.py
          - terminal_tool.py
          - tirith_security.py
          - todo_tool.py
          - transcription_tools.py
          - tts_tool.py
          - vision_tools.py
          - voice_mode.py
          - web_tools.py
          - website_policy.py
          📂 browser_providers/ [FORGE]
            - __init__.py
            - base.py
            - browser_use.py
            - browserbase.py
          📂 environments/ [FORGE]
            - __init__.py
            - base.py
            - daytona.py
            - docker.py
            - local.py
            - modal.py
            - persistent_shell.py
            - singularity.py
            - ssh.py
          📂 neutts_samples/ [FORGE]
            - jo.txt
            - jo.wav
        📂 website/ [FORGE]
          - README.md
          - docusaurus.config.ts
          - package.json
          - sidebars.ts
          - tsconfig.json
          📂 docs/ [FORGE]
            - index.md
          📂 src/ [FORGE]
          📂 static/ [FORGE]
            - .nojekyll
      📂 lightpanda/ [FORGE]
        - README.md
        - lightpanda-serve.sh
      📂 lightpanda-browser/ [FORGE]
        - CLA.md
        - CONTRIBUTING.md
        - Dockerfile
        - LICENSE
        - LICENSING.md
        - Makefile
        - README.md
        - build.zig
        - build.zig.zon
        - flake.lock
        - flake.nix
        📂 .github/ [FORGE]
          📂 actions/ [FORGE]
          📂 workflows/ [FORGE]
            - cla.yml
            - e2e-integration-test.yml
            - e2e-test.yml
            - nightly.yml
            - wpt.yml
            - zig-test.yml
        📂 src/ [FORGE]
          - App.zig
          - ArenaPool.zig
          - Config.zig
          - Notification.zig
          - SemanticTree.zig
          - Server.zig
          - Sighandler.zig
          - TestHTTPServer.zig
          - crash_handler.zig
          - crypto.zig
          - datetime.zig
          - id.zig
          - lightpanda.zig
          - log.zig
          - main.zig
          - main_legacy_test.zig
          - main_snapshot_creator.zig
          - mcp.zig
          - slab.zig
          - string.zig
          - test_runner.zig
          - testing.zig
          📂 browser/ [FORGE]
            - Browser.zig
            - EventManager.zig
            - Factory.zig
            - HttpClient.zig
            - Mime.zig
            - Page.zig
            - ScriptManager.zig
            - Session.zig
            - URL.zig
            - actions.zig
            - color.zig
            - dump.zig
            - interactive.zig
            - markdown.zig
            - reflect.zig
            - structured_data.zig
          📂 cdp/ [FORGE]
            - AXNode.zig
            - Node.zig
            - cdp.zig
            - id.zig
            - testing.zig
          📂 data/ [FORGE]
            - public_suffix_list.zig
            - public_suffix_list_gen.go
          📂 html5ever/ [FORGE]
            - Cargo.lock
            - Cargo.toml
            - lib.rs
            - sink.rs
            - types.rs
          📂 mcp/ [FORGE]
            - Server.zig
            - protocol.zig
            - resources.zig
            - router.zig
            - tools.zig
          📂 network/ [FORGE]
            - Robots.zig
            - Runtime.zig
            - WebBotAuth.zig
            - http.zig
            - websocket.zig
          📂 sys/ [FORGE]
            - libcurl.zig
          📂 telemetry/ [FORGE]
            - lightpanda.zig
            - telemetry.zig
      📂 livekit/ [FORGE]
        - .goreleaser.yaml
        - CHANGELOG.md
        - Dockerfile
        - LICENSE
        - NOTICE
        - README.md
        - bootstrap.sh
        - config-sample.yaml
        - go.mod
        - go.sum
        - install-livekit.sh
        - livekit-server.exe
        - magefile.go
        - magefile_unix.go
        - magefile_windows.go
        - renovate.json
        📂 .github/ [FORGE]
          - banner_dark.png
          - banner_light.png
          📂 ISSUE_TEMPLATE/ [FORGE]
            - bug_report.md
          📂 workflows/ [FORGE]
            - buildtest.yaml
            - docker.yaml
            - release.yaml
            - slack-notifier.yaml
        📂 cmd/ [FORGE]
          📂 server/ [FORGE]
            - commands.go
            - main.go
            - main_test.go
        📂 deploy/ [FORGE]
          - README.md
          📂 grafana/ [FORGE]
            - livekit-server-overview.json
        📂 pkg/ [FORGE]
          📂 agent/ [FORGE]
            - agent_test.go
            - client.go
            - config.go
            - worker.go
          📂 clientconfiguration/ [FORGE]
            - conf.go
            - conf_test.go
            - match.go
            - staticconfiguration.go
            - types.go
          📂 config/ [FORGE]
            - config.go
            - config_test.go
          📂 metric/ [FORGE]
            - metric_config.go
            - metric_timestamper.go
            - metrics_collector.go
            - metrics_reporter.go
          📂 routing/ [FORGE]
            - errors.go
            - interfaces.go
            - localrouter.go
            - messagechannel.go
            - messagechannel_test.go
            - node.go
            - nodestats.go
            - redisrouter.go
            - roommanager.go
            - signal.go
          📂 rtc/ [FORGE]
            - clientinfo.go
            - clientinfo_test.go
            - config.go
            - datadowntrack.go
            - datatrack.go
            - egress.go
            - errors.go
            - mediaengine.go
            - mediaengine_test.go
            - medialossproxy.go
            - mediatrack.go
            - mediatrack_test.go
            - mediatrackreceiver.go
            - mediatracksubscriptions.go
            - migrationdatacache.go
            - migrationdatacache_test.go
            - participant.go
            - participant_data_track.go
            - participant_internal_test.go
            - participant_sdp.go
            - participant_signal.go
            - room.go
            - room_test.go
            - roomtrackmanager.go
            - signalanddatastats.go
            - subscribedtrack.go
            - subscriptionmanager.go
            - subscriptionmanager_test.go
            - testutils.go
            - transport.go
            - transport_test.go
            - transportmanager.go
            - updatatrackmanager.go
            - uptrackmanager.go
            - uptrackmanager_test.go
            - user_packet_deduper.go
            - utils.go
            - utils_test.go
            - wrappedreceiver.go
          📂 service/ [FORGE]
            - agent_dispatch_service.go
            - agentservice.go
            - auth.go
            - auth_test.go
            - basic_auth.go
            - clients.go
            - docker_test.go
            - egress.go
            - egressid.go
            - errors.go
            - ingress.go
            - interfaces.go
            - ioservice.go
            - ioservice_ingress.go
            - ioservice_sip.go
            - ioservice_sip_test.go
            - localstore.go
            - redisstore.go
            - redisstore_sip.go
            - redisstore_sip_test.go
            - redisstore_test.go
            - roomallocator.go
            - roomallocator_test.go
            - roommanager.go
            - roommanager_service.go
            - roomservice.go
            - roomservice_test.go
            - rtcservice.go
            - server.go
            - signal.go
            - signal_test.go
            - sip.go
            - turn.go
            - twirp.go
            - twirp_test.go
            - utils.go
            - utils_test.go
            - whipservice.go
            - wire.go
            - wire_gen.go
            - wsprotocol.go
          📂 sfu/ [FORGE]
            - NOTICE
            - downtrack.go
            - errors.go
            - forwarder.go
            - forwarder_test.go
            - forwardstats.go
            - playoutdelay.go
            - playoutdelay_test.go
            - receiver.go
            - receiver_base.go
            - receiver_test.go
            - redprimaryreceiver.go
            - redreceiver.go
            - redreceiver_test.go
            - rtpmunger.go
            - rtpmunger_test.go
            - sequencer.go
            - sequencer_test.go
            - sfu.go
            - streamtrackermanager.go
            - track_remote.go
          📂 telemetry/ [FORGE]
            - analyticsservice.go
            - events.go
            - events_test.go
            - stats.go
            - stats_test.go
            - statsconn.go
            - statsworker.go
            - statsworker_test.go
            - telemetryservice.go
          📂 testutils/ [FORGE]
            - timeout.go
          📂 utils/ [FORGE]
            - changenotifier.go
            - context.go
            - iceconfigcache.go
            - iceconfigcache_test.go
            - incrementaldispatcher.go
            - incrementaldispatcher_test.go
            - logging.go
            - math.go
            - opsqueue.go
            - protocol.go
            - slice.go
        📂 test/ [FORGE]
          - agent.go
          - agent_test.go
          - integration_helpers.go
          - multinode_roomservice_test.go
          - multinode_test.go
          - scenarios.go
          - singlenode_test.go
          - webhook_test.go
          📂 client/ [FORGE]
            - client.go
            - datachannel_reader.go
            - datatrack_remote.go
            - datatrack_writer.go
            - trackwriter.go
        📂 tools/ [FORGE]
          - tools.go
        📂 version/ [FORGE]
          - version.go
      📂 mcp_web_search/ [FORGE]
        - .dockerignore
        - Dockerfile.ubuntu
        - LICENSE
        - README.md
        - README.zh-CN.md
        - cli.py
        - dotenv.env
        - requirements.txt
        - run_mcp_direct_call.py
        - run_mcp_get_html.py
        📂 .github/ [FORGE]
          📂 instructions/ [FORGE]
            - todos.instructions.md
          📂 workflows/ [FORGE]
            - ci.yml
        📂 common/ [FORGE]
          - __init__.py
          - logger.py
          - types.py
        📂 google_search/ [FORGE]
          - REFACTOR_README.md
          - __init__.py
          - browser_manager.py
          - distiller.py
          - engine.py
          - fingerprint.py
          - html_extractor.py
          - search_executor.py
          - utils.py
        📂 mcp_integration/ [FORGE]
          - __init__.py
          - client.py
          - server.py
        📂 tests/ [FORGE]
          - smoke_mcp_call.py
      📂 rotel/ [FORGE]
        - Cargo.lock
        - Cargo.toml
        - Dockerfile
        - build_log.txt
        - error.log
        - error.txt
        📂 src/ [FORGE]
          - main.rs
      📂 tiny-tts/ [FORGE]
        - LICENSE
        - MANIFEST.in
        - README.md
        - TinyTTS.png
        - app.py
        - benchmark.py
        - benchmark_onnx.py
        - export_onnx.py
        - pyproject.toml
        - requirements.txt
        - setup.py
        📂 assets/ [FORGE]
          - paragraph.mp4
          - paragraph.wav
        📂 checkpoints/ [FORGE]
          - G.pth
        📂 onnx/ [FORGE]
          - decoder.onnx
          - duration_predictor.onnx
          - flow.onnx
          - text_encoder.onnx
        📂 samples/ [FORGE]
          - kittentts_mini.wav
          - kittentts_nano.wav
          - kokoro.wav
          - piper.wav
          - pocket_tts.wav
          - supertonic.wav
          - tinytts.wav
        📂 tiny_tts/ [FORGE]
          - __init__.py
          - infer.py
          - infer_onnx.py
          📂 alignment/ [FORGE]
            - __init__.py
            - core.py
          📂 models/ [FORGE]
            - __init__.py
            - synthesizer.py
          📂 nn/ [FORGE]
            - __init__.py
            - attentions.py
            - commons.py
            - modules.py
            - transforms.py
          📂 text/ [FORGE]
            - __init__.py
            - cmudict.rep
            - cmudict_cache.pickle
            - english.py
            - symbols.py
          📂 utils/ [FORGE]
            - __init__.py
            - config.py
        📂 tiny_tts.egg-info/ [FORGE]
          - PKG-INFO
          - SOURCES.txt
          - dependency_links.txt
          - entry_points.txt
          - requires.txt
          - top_level.txt
    📂 PORTAL_CORE/ [FORGE]
      - biome.json
      - eslint.config.mjs
      - index.html
      - package.json
      - tsconfig.json
      - tsconfig.node.json
      - vite.config.ts
      📂 Anya_Dashboard/ [FORGE]
        - dashboard_boot.log
        - dashboard_correct.log
        - dashboard_final.log
        - dashboard_fixed.log
        - index.html
        - package.json
        - postcss.config.js
        - tailwind.config.js
        - tsconfig.json
        - tsconfig.node.json
        - vercel.json
        - vite.config.ts
        - vitest.config.ts
        📂 .vercel/ [FORGE]
          - README.txt
          - project.json
        📂 src/ [FORGE]
          - App.tsx
          - index.css
          - main.tsx
          📂 __tests__/ [FORGE]
            - Card.test.tsx
          📂 components/ [FORGE]
          📂 features/ [FORGE]
          📂 lib/ [FORGE]
            - utils.ts
          📂 test/ [FORGE]
            - setup.ts
      📂 Modal/ [FORGE]
        - bridge.py
        - get_started.py
        - kinetic_fortress.py
        - tasha_voice_agent.py
        📂 excalibur-resonance/ [FORGE]
          📂 app/ [FORGE]
            - layout.tsx
            - page.tsx
          📂 components/ [FORGE]
            - actuator.tsx
            - hud-header.tsx
            - the-armory.tsx
          📂 lib/ [FORGE]
            - utils.ts
          📂 proxy/ [FORGE]
            - bridge.py
          📂 v0-quantum-cinematic-engine/ [FORGE]
            - components.json
            - next.config.mjs
            - package.json
            - postcss.config.mjs
            - tsconfig.json
        📂 morgana/ [FORGE]
          - Dockerfile
          - cleanup_backups.py
          - conductor_genesis_v92.py
          - conductor_genesis_v93_patched.py
          - conductor_v94_fastapi.py
          - conductor_v94_remote.py
          - config.yaml
          - deployment_state.json
          - local_modal.toml
          - main.py
          - morgana_core.py
          - morgana_staging.py
          📂 components/ [FORGE]
          📂 templates/ [FORGE]
            - MorganaAvatar.tsx
            - morgana_core.py
      📂 components/ [FORGE]
        - Terminal.tsx
        📂 scene/ [FORGE]
          - RoundTable.tsx
          - ThroneRoom.tsx
        📂 studio/ [FORGE]
          - AgentSidebar.tsx
          - CodeEditor.tsx
          - PreviewPane.tsx
        📂 ui/ [FORGE]
          - GlassOverlay.tsx
          - KnightSprites.tsx
      📂 public/ [FORGE]
        - file.svg
        - globe.svg
        - icon-192.png
        - icon-512.png
        - manifest.json
        - next.svg
        - vercel.svg
        - window.svg
        📂 assets/ [FORGE]
          - throne_bg.webp
          📂 knights/ [FORGE]
            - anya.png
            - merlin.png
            - zenith.png
      📂 src/ [FORGE]
        - App.tsx
        - index.css
        - main.tsx
        📂 components/ [FORGE]
          - AgnoDebateBridge.tsx
          - AlchemyLab.tsx
          - BrainMonitor.tsx
          - GravityAnchor.tsx
          - PersonaStudio.tsx
          - RawDataArchive.tsx
          - RotelMonitor.tsx
          - SaltareController.tsx
          - SignalTower.tsx
          - Terminal.tsx
        📂 hooks/ [FORGE]
          - useCamelotNetwork.ts
          - useFireTrail.ts
        📂 lib/ [FORGE]
          - utils.ts
          📂 intelligence/ [FORGE]
            - adapter.ts
      📂 web/ [FORGE]
        - eslint.config.mjs
        - next-env.d.ts
        - next.config.ts
        - package.json
        - tsconfig.json
        📂 app/ [FORGE]
          - favicon.ico
          - globals.css
          - layout.tsx
          - page.tsx
          📂 api/ [FORGE]
        📂 components/ [FORGE]
          📂 scene/ [FORGE]
            - RoundTable.tsx
            - ThroneRoom.tsx
          📂 ui/ [FORGE]
            - GlassOverlay.tsx
            - KnightSprites.tsx
            - TashaVoiceWidget.tsx
        📂 hooks/ [FORGE]
          - use-socket.ts
    📂 _templates/ [FORGE]
      📂 component/ [FORGE]
        📂 new/ [FORGE]
          - component.ejs.t
    📂 apps/ [FORGE]
      📂 anya-lyte/ [FORGE]
        - App.tsx
        - package.json
        📂 src/ [FORGE]
          - titanLinkClient.ts
          📂 api/ [FORGE]
          📂 components/ [FORGE]
          📂 hooks/ [FORGE]
          📂 ui/ [FORGE]
            - ApprovalSheet.tsx
            - ChatScreen.tsx
            - JobsScreen.tsx
            - RemoteSessionScreen.tsx
            - SettingsScreen.tsx
            - VoiceDeck.tsx
      📂 headartworks/ [FORGE]
        📂 .phoenix-portal/ [FORGE]
          - ANYA_SWARM_PROMPT_PHASE9.md
          - BLUEPRINT.md
          - LADY_APIS_tasks.md
          - LADY_APIS_verification.md
          - PHOENIX_PORTAL_EMAIL_TEMPLATES.html
          - SHOPIFY_FLOW_SETUP.md
          - SIR_BORIS_tasks.md
          - SIR_BORIS_verification.md
          - SIR_DEBUG_tasks.md
          - SIR_DEBUG_verification.md
          - SIR_FORGE_tasks.md
          - SIR_FORGE_verification.md
          - SIR_SENTINEL_tasks.md
          - SIR_SENTINEL_verification.md
        📂 assets/ [FORGE]
          - animations.js
          - base.css
          - cart-drawer.js
          - cart-notification.js
          - cart.js
          - collage.css
          - collapsible-content.css
          - component-accordion.css
          - component-article-card.css
          - component-card.css
          - component-cart-drawer.css
          - component-cart-items.css
          - component-cart-notification.css
          - component-cart.css
          - component-collection-hero.css
          - component-complementary-products.css
          - component-deferred-media.css
          - component-discounts.css
          - component-facets.css
          - component-image-with-text.css
          - component-list-menu.css
          - component-list-payment.css
          - component-list-social.css
          - component-loading-overlay.css
          - component-localization-form.css
          - component-mega-menu.css
          - component-menu-drawer.css
          - component-modal-video.css
          - component-model-viewer-ui.css
          - component-newsletter.css
          - component-pagination.css
          - component-pickup-availability.css
          - component-predictive-search.css
          - component-price.css
          - component-product-model.css
          - component-rating.css
          - component-search.css
          - component-show-more.css
          - component-slider.css
          - component-slideshow.css
          - component-totals.css
          - component-volume-pricing.css
          - constants.js
          - custom.css
          - customer.css
          - customer.js
          - details-disclosure.js
          - details-modal.js
          - facets.js
          - global.js
          - localization-form.js
          - magnify.js
          - main-search.js
          - mask-blobs.css
          - media-gallery.js
          - newsletter-section.css
          - pagefly-animation.css
          - pagefly-main.css
          - pagefly.67600291.css
          - pagefly.blog.css
          - password-modal.js
          - pickup-availability.js
          - predictive-search.js
          - price-per-item.js
          - product-form.js
          - product-info.js
          - product-modal.js
          - product-model.js
          - pubsub.js
          - quantity-popover.css
          - quantity-popover.js
          - quick-add.css
          - quick-add.js
          - quick-order-list.css
          - quick-order-list.js
          - recipient-form.js
          - search-form.js
          - section-blog-post.css
          - section-collection-list.css
          - section-contact-form.css
          - section-email-signup-banner.css
          - section-featured-blog.css
          - section-featured-product.css
          - section-footer.css
          - section-image-banner.css
          - section-main-blog.css
          - section-main-page.css
          - section-main-product.css
          - section-multicolumn.css
          - section-password.css
          - section-related-products.css
          - section-rich-text.css
          - share.js
          - show-more.js
          - sparkle.gif
          - template-collection.css
          - template-giftcard.css
          - theme-editor.js
          - video-section.css
        📂 config/ [FORGE]
          - settings_data.json
          - settings_schema.json
        📂 layout/ [FORGE]
          - password.liquid
          - theme-backup-booster-seo.liquid
          - theme.liquid
          - theme.pagefly.liquid
        📂 sections/ [FORGE]
          - announcement-bar.liquid
          - apps.liquid
          - background-video.liquid
          - cart-drawer.liquid
          - cart-icon-bubble.liquid
          - cart-live-region-text.liquid
          - cart-notification-button.liquid
          - cart-notification-product.liquid
          - collage.liquid
          - collapsible-content.liquid
          - collection-list.liquid
          - contact-form.liquid
          - custom-liquid.liquid
          - email-signup-banner.liquid
          - featured-artist.liquid
          - featured-artists-banner.liquid
          - featured-blog.liquid
          - featured-collection.liquid
          - featured-product.liquid
          - footer-group.json
          - footer.liquid
          - header-group.json
          - header.liquid
          - image-banner.liquid
          - image-with-text.liquid
          - main-404.liquid
          - main-account.liquid
          - main-activate-account.liquid
          - main-addresses.liquid
          - main-article.liquid
          - main-blog.liquid
          - main-cart-footer.liquid
          - main-cart-items.liquid
          - main-collection-banner.liquid
          - main-collection-product-grid.liquid
          - main-list-collections.liquid
          - main-login.liquid
          - main-order.liquid
          - main-page.liquid
          - main-password-footer.liquid
          - main-password-header.liquid
          - main-product.liquid
          - main-register.liquid
          - main-reset-password.liquid
          - main-search.liquid
          - multicolumn.liquid
          - multirow.liquid
          - newsletter.liquid
          - page.liquid
          - pagefly-home.liquid
          - pagefly-section.liquid
          - pickup-availability.liquid
          - predictive-search.liquid
          - quick-order-list.liquid
          - related-products.liquid
          - rich-text.liquid
          - slideshow.liquid
          - team-section.liquid
          - video.liquid
        📂 snippets/ [FORGE]
          - phoenix-portal-standalone.liquid
        📂 templates/ [FORGE]
          - 404.json
          - article.json
          - blog.json
          - cart.json
          - collection.json
          - gift_card.liquid
          - index.json
          - list-collections.json
          - page.Featured-Artists.liquid
          - page.about.json
          - page.author-landing.liquid
          - page.candles-2.json
          - page.candles-page.json
          - page.collections.json
          - page.coming-soon.json
          - page.contact.json
          - page.json
          - page.judgeme_all_reviews.liquid
          - password.json
          - product.json
          - search.json
          - search.preorderjson.liquid
          📂 customers/ [FORGE]
            - account.json
            - activate_account.json
            - addresses.json
            - login.json
            - order.json
            - register.json
            - reset_password.json
      📂 headartworks-live-pull/ [FORGE]
        📂 layout/ [FORGE]
          - password.liquid
          - theme-backup-booster-seo.liquid
          - theme.liquid
          - theme.pagefly.liquid
        📂 sections/ [FORGE]
          - main-page.liquid
        📂 templates/ [FORGE]
          - page.author-landing.liquid
          - page.json
    📂 cartridge/ [FORGE]
      - cartridge_schemas.py
      - fabrication_engine.py
      - sandbox.py
      - test_fabrication.py
      - test_sandbox.py
      📂 packages/ [FORGE]
        📂 CLOUD_FLUX/ [FORGE]
          - manifest.json
          - persona.py
        📂 CREATIVE_CORE/ [FORGE]
          - manifest.json
          - persona.py
        📂 ENGINEERING_CORE/ [FORGE]
          - manifest.json
          - persona.py
        📂 OPERATIONS_CORE/ [FORGE]
          - manifest.json
          - persona.py
        📂 STRATEGY_CORE/ [FORGE]
          - manifest.json
          - persona.py
        📂 SYNTAX_GUARD/ [FORGE]
          - manifest.json
          - persona.py
    📂 dyad-apps/ [FORGE]
      📂 New folder/ [FORGE]
        - AI_RULES.md
        - HCCP Framework Summary.md
        - Implementation Roadmap and Documentation for Invoice Generator MVP.md
        - Invoice Generator MVP Development Plan_ A Human-AI Collaborative Planning (HCCP) Approach.md
        - Invoice Generator MVP Requirements.md
        - RecreatingandOptimizingtheManus.aiSuperAgentWorkflow.txt
        - Technical Architecture and Database Design for Invoice Generator MVP.md
        - next.config.js
        - package.json
        - pasted_content.txt
        - plan.md
        - project_summary.md
        - todo.md
        - tsconfig.json
        - wireframe_ai_review.png
        - wireframe_dashboard.png
        - wireframe_invoice_modal.png
        - wireframe_manual_form.png
        - wireframe_recurring_dashboard.png
        📂 UI/ [FORGE]
          - UX Design and Wireframes for Invoice Generator MVP.md
        📂 prisma/ [FORGE]
          - schema.prisma
        📂 src/ [FORGE]
          📂 app/ [FORGE]
            - globals.css
            - layout.tsx
            - page.tsx
          📂 components/ [FORGE]
            - navigation.tsx
          📂 lib/ [FORGE]
            - email.ts
            - generator.ts
            - ocr.ts
            - pdf.tsx
            - prisma.ts
            - scheduler.ts
            - schemas.ts
            - utils.ts
            - validator.ts
            - visionPrompt.ts
      📂 happy-owl-dart/ [FORGE]
        - AI_RULES.md
        - LICENSE
        - README.md
        - components.json
        - next-env.d.ts
        - next.config.ts
        - package.json
        - postcss.config.mjs
        - tailwind.config.ts
        - tsconfig.json
        📂 public/ [FORGE]
          - file.svg
          - globe.svg
          - next.svg
          - vercel.svg
          - window.svg
        📂 src/ [FORGE]
          📂 app/ [FORGE]
            - favicon.ico
            - globals.css
            - layout.tsx
            - page.tsx
          📂 components/ [FORGE]
            - made-with-dyad.tsx
          📂 hooks/ [FORGE]
            - use-mobile.tsx
          📂 lib/ [FORGE]
            - utils.ts
    📂 hive_api/ [FORGE]
      - agno_core.py
    📂 holotable/ [FORGE]
      - eslint.config.mjs
      - next-env.d.ts
      - next.config.ts
      - package.json
      - postcss.config.mjs
      - tsconfig.json
      📂 app/ [FORGE]
        - favicon.ico
        - globals.css
        - layout.tsx
        - page.tsx
      📂 components/ [FORGE]
        - DevHub.tsx
        - GenesisDesigner.tsx
        - OracleCanvas.tsx
        - TheLedger.tsx
        - TheRoster.tsx
      📂 lib/ [FORGE]
        - api.ts
      📂 public/ [FORGE]
        - file.svg
        - globe.svg
        - next.svg
        - vercel.svg
        - window.svg
    📂 hooks/ [FORGE]
      - use-socket.ts
    📂 kinetic/ [FORGE]
      - KNIGHTS_ROUND_GUIDE.md
      - daily_maintenance.py
      - knight_upgrade.py
      - merlin_dispatch.py
      - ocular_scout.py
      - scribe_translate.py
      - titan_alchemist.py
      - titan_architect.py
      - titan_evolve.py
      - titan_grader.py
      - titan_loom.py
      - titan_scribe.py
      - titan_telemetry.py
      - titan_triage.py
      📂 bin/ [FORGE]
        - cribo.exe
        - ledger.exe
        - rotel.exe
        📂 grafana/ [FORGE]
          - Dockerfile
          - LICENSE
          - NOTICE.md
          - README.md
          - VERSION
          📂 bin/ [FORGE]
            - grafana-cli.exe
            - grafana-server.exe
            - grafana.exe
          📂 conf/ [FORGE]
            - defaults.ini
            - ldap.toml
            - ldap_multiple.toml
            - sample.ini
          📂 docs/ [FORGE]
          📂 npm-artifacts/ [FORGE]
            - @grafana-data-v11.4.0.tgz
            - @grafana-e2e-selectors-v11.4.0.tgz
            - @grafana-flamegraph-v11.4.0.tgz
            - @grafana-prometheus-v11.4.0.tgz
            - @grafana-runtime-v11.4.0.tgz
            - @grafana-schema-v11.4.0.tgz
            - @grafana-ui-v11.4.0.tgz
          📂 packaging/ [FORGE]
          📂 plugins-bundled/ [FORGE]
            - README.md
            - external.json
          📂 public/ [FORGE]
            - api-enterprise-spec.json
            - api-merged.json
            - mockServiceWorker.js
            - openapi3.json
            - robots.txt
          📂 storybook/ [FORGE]
            - 1064.5a03b5f6.iframe.bundle.js
            - 1067.d812f96e.iframe.bundle.js
            - 1253.977d0329.iframe.bundle.js
            - 1253.977d0329.iframe.bundle.js.LICENSE.txt
            - 133.d7ae3658.iframe.bundle.js
            - 133.d7ae3658.iframe.bundle.js.LICENSE.txt
            - 1332.4f7fbd1e.iframe.bundle.js
            - 1463.0077940e.iframe.bundle.js
            - 1500.9456e8af.iframe.bundle.js
            - 1626.7379b775.iframe.bundle.js
            - 1639.95035edd.iframe.bundle.js
            - 1653.4ff56cd5.iframe.bundle.js
            - 1653.4ff56cd5.iframe.bundle.js.LICENSE.txt
            - 1685.88252d16.iframe.bundle.js
            - 1685.88252d16.iframe.bundle.js.LICENSE.txt
            - 1898.ca2cd108.iframe.bundle.js
            - 1898.ca2cd108.iframe.bundle.js.LICENSE.txt
            - 1973.12dd8f28.iframe.bundle.js
            - 1973.12dd8f28.iframe.bundle.js.LICENSE.txt
            - 1993.68966c15.iframe.bundle.js
            - 2014.f70aa35e.iframe.bundle.js
            - 2157.f21aaf8d.iframe.bundle.js
            - 2227.db88e5ba.iframe.bundle.js
            - 2227.db88e5ba.iframe.bundle.js.LICENSE.txt
            - 2258.7de2a80e.iframe.bundle.js
            - 2258.7de2a80e.iframe.bundle.js.LICENSE.txt
            - 2409.c02a35de.iframe.bundle.js
            - 2459.5861460d.iframe.bundle.js
            - 2459.5861460d.iframe.bundle.js.LICENSE.txt
            - 2487.9f2b8616.iframe.bundle.js
            - 2487.9f2b8616.iframe.bundle.js.LICENSE.txt
            - 250.fdc0d65a.iframe.bundle.js
            - 2509.9dc74e62.iframe.bundle.js
            - 2581.e62908b9.iframe.bundle.js
            - 2581.e62908b9.iframe.bundle.js.LICENSE.txt
            - 2709.afb429ae.iframe.bundle.js
            - 2709.afb429ae.iframe.bundle.js.LICENSE.txt
            - 2725.ce0eb30a.iframe.bundle.js
            - 2725.ce0eb30a.iframe.bundle.js.LICENSE.txt
            - 295.d72dfe29.iframe.bundle.js
            - 295.d72dfe29.iframe.bundle.js.LICENSE.txt
            - 2962.c0c1abc9.iframe.bundle.js
            - 302.339bacbd.iframe.bundle.js
            - 3035.e0dc9059.iframe.bundle.js
            - 3053.6d101d5a.iframe.bundle.js
            - 3053.6d101d5a.iframe.bundle.js.LICENSE.txt
            - 3120.a962c6e2.iframe.bundle.js
            - 3173.498523fd.iframe.bundle.js
            - 3173.498523fd.iframe.bundle.js.LICENSE.txt
            - 3215.73abcb9e.iframe.bundle.js
            - 3245.45babb00.iframe.bundle.js
            - 3245.45babb00.iframe.bundle.js.LICENSE.txt
            - 3269.690309c5.iframe.bundle.js
            - 3269.690309c5.iframe.bundle.js.LICENSE.txt
            - 3275.165163ec.iframe.bundle.js
            - 3275.165163ec.iframe.bundle.js.LICENSE.txt
            - 3284.95e05b39.iframe.bundle.js
            - 3289.af8eed9a.iframe.bundle.js
            - 3289.af8eed9a.iframe.bundle.js.LICENSE.txt
            - 3317.774edb39.iframe.bundle.js
            - 3317.774edb39.iframe.bundle.js.LICENSE.txt
            - 3435.dcd25783.iframe.bundle.js
            - 3435.dcd25783.iframe.bundle.js.LICENSE.txt
            - 3505.f3079359.iframe.bundle.js
            - 3505.f3079359.iframe.bundle.js.LICENSE.txt
            - 3583.483936aa.iframe.bundle.js
            - 3605.ad58dba8.iframe.bundle.js
            - 3605.ad58dba8.iframe.bundle.js.LICENSE.txt
            - 3644.199ce94d.iframe.bundle.js
            - 3686.6f9f0648.iframe.bundle.js
            - 3725.d2d3c5d5.iframe.bundle.js
            - 3725.d2d3c5d5.iframe.bundle.js.LICENSE.txt
            - 3746.14e5ca39.iframe.bundle.js
            - 3757.dfed6054.iframe.bundle.js
            - 3772.3d9d7a92.iframe.bundle.js
            - 3939.5717c620.iframe.bundle.js
            - 3939.5717c620.iframe.bundle.js.LICENSE.txt
            - 405.286c0173.iframe.bundle.js
            - 4126.97397406.iframe.bundle.js
            - 4450.6b99a39c.iframe.bundle.js
            - 4541.e3f12a93.iframe.bundle.js
            - 4541.e3f12a93.iframe.bundle.js.LICENSE.txt
            - 4608.6d641a80.iframe.bundle.js
            - 4617.98750dc9.iframe.bundle.js
            - 4617.98750dc9.iframe.bundle.js.LICENSE.txt
            - 4697.a065a6ac.iframe.bundle.js
            - 4697.a065a6ac.iframe.bundle.js.LICENSE.txt
            - 4732.80b60ca6.iframe.bundle.js
            - 4806.4d46bf74.iframe.bundle.js
            - 4809.77520fb4.iframe.bundle.js
            - 4809.77520fb4.iframe.bundle.js.LICENSE.txt
            - 485.dddda793.iframe.bundle.js
            - 485.dddda793.iframe.bundle.js.LICENSE.txt
            - 4857.f0b378f4.iframe.bundle.js
            - 4873.14d1e897.iframe.bundle.js
            - 4873.14d1e897.iframe.bundle.js.LICENSE.txt
            - 4901.d13a172a.iframe.bundle.js
            - 4933.506dcdf7.iframe.bundle.js
            - 4933.506dcdf7.iframe.bundle.js.LICENSE.txt
            - 4997.02331be7.iframe.bundle.js
            - 4997.02331be7.iframe.bundle.js.LICENSE.txt
            - 5109.dd9db537.iframe.bundle.js
            - 5135.f3c5e98a.iframe.bundle.js
            - 5135.f3c5e98a.iframe.bundle.js.LICENSE.txt
            - 5157.0ac19bde.iframe.bundle.js
            - 5157.0ac19bde.iframe.bundle.js.LICENSE.txt
            - 519.a3f5f395.iframe.bundle.js
            - 519.a3f5f395.iframe.bundle.js.LICENSE.txt
            - 5205.c2bc78ca.iframe.bundle.js
            - 5205.c2bc78ca.iframe.bundle.js.LICENSE.txt
            - 5259.a078e871.iframe.bundle.js
            - 5259.a078e871.iframe.bundle.js.LICENSE.txt
            - 5286.231b17fe.iframe.bundle.js
            - 5286.231b17fe.iframe.bundle.js.LICENSE.txt
            - 5325.9bdcf605.iframe.bundle.js
            - 5325.9bdcf605.iframe.bundle.js.LICENSE.txt
            - 5381.86fdbc49.iframe.bundle.js
            - 5381.86fdbc49.iframe.bundle.js.LICENSE.txt
            - 5458.d63b7713.iframe.bundle.js
            - 5458.d63b7713.iframe.bundle.js.LICENSE.txt
            - 5497.bc7acb26.iframe.bundle.js
            - 5497.bc7acb26.iframe.bundle.js.LICENSE.txt
            - 5532.8c4b645a.iframe.bundle.js
            - 5532.8c4b645a.iframe.bundle.js.LICENSE.txt
            - 5567.fb9ca180.iframe.bundle.js
            - 5567.fb9ca180.iframe.bundle.js.LICENSE.txt
            - 5637.f84b388d.iframe.bundle.js
            - 5637.f84b388d.iframe.bundle.js.LICENSE.txt
            - 5679.21485810.iframe.bundle.js
            - 5701.6c0637f7.iframe.bundle.js
            - 5701.6c0637f7.iframe.bundle.js.LICENSE.txt
            - 5763.e7255665.iframe.bundle.js
            - 5763.e7255665.iframe.bundle.js.LICENSE.txt
            - 5793.b5eeafda.iframe.bundle.js
            - 5793.b5eeafda.iframe.bundle.js.LICENSE.txt
            - 5821.18e9fcf1.iframe.bundle.js
            - 5821.18e9fcf1.iframe.bundle.js.LICENSE.txt
            - 5833.63c50cc3.iframe.bundle.js
            - 585.69a2c356.iframe.bundle.js
            - 5856.e2ce0ac0.iframe.bundle.js
            - 5856.e2ce0ac0.iframe.bundle.js.LICENSE.txt
            - 5920.658a8696.iframe.bundle.js
            - 6159.23cb7020.iframe.bundle.js
            - 6192.1990ec0a.iframe.bundle.js
            - 6220.b8676318.iframe.bundle.js
            - 6220.b8676318.iframe.bundle.js.LICENSE.txt
            - 6224.01c918d2.iframe.bundle.js
            - 6469.3015a9c5.iframe.bundle.js
            - 6469.3015a9c5.iframe.bundle.js.LICENSE.txt
            - 653.c4307529.iframe.bundle.js
            - 653.c4307529.iframe.bundle.js.LICENSE.txt
            - 6693.25099afe.iframe.bundle.js
            - 6693.25099afe.iframe.bundle.js.LICENSE.txt
            - 6729.9dc2dfc8.iframe.bundle.js
            - 6729.9dc2dfc8.iframe.bundle.js.LICENSE.txt
            - 6741.12b3b3bd.iframe.bundle.js
            - 6741.12b3b3bd.iframe.bundle.js.LICENSE.txt
            - 6820.daaa0eff.iframe.bundle.js
            - 6961.605209fc.iframe.bundle.js
            - 6961.605209fc.iframe.bundle.js.LICENSE.txt
            - 6981.f21302b3.iframe.bundle.js
            - 7089.25ac42b9.iframe.bundle.js
            - 7089.25ac42b9.iframe.bundle.js.LICENSE.txt
            - 71.8fe8a11c.iframe.bundle.js
            - 715.9d0edb3f.iframe.bundle.js
            - 7266.8491ce16.iframe.bundle.js
            - 7266.8491ce16.iframe.bundle.js.LICENSE.txt
            - 7445.c061637d.iframe.bundle.js
            - 7445.c061637d.iframe.bundle.js.LICENSE.txt
            - 7455.746c6251.iframe.bundle.js
            - 7455.746c6251.iframe.bundle.js.LICENSE.txt
            - 7496.a40d1585.iframe.bundle.js
            - 7509.8fc67590.iframe.bundle.js
            - 7509.8fc67590.iframe.bundle.js.LICENSE.txt
            - 7581.529b6834.iframe.bundle.js
            - 7660.62f6659c.iframe.bundle.js
            - 7663.c222708b.iframe.bundle.js
            - 7663.c222708b.iframe.bundle.js.LICENSE.txt
            - 7733.f712621f.iframe.bundle.js
            - 7733.f712621f.iframe.bundle.js.LICENSE.txt
            - 7861.4e8e1ef3.iframe.bundle.js
            - 7861.4e8e1ef3.iframe.bundle.js.LICENSE.txt
            - 7863.46a6dd54.iframe.bundle.js
            - 7863.46a6dd54.iframe.bundle.js.LICENSE.txt
            - 7925.f8f1dc5e.iframe.bundle.js
            - 7925.f8f1dc5e.iframe.bundle.js.LICENSE.txt
            - 8025.b481b2ad.iframe.bundle.js
            - 8025.b481b2ad.iframe.bundle.js.LICENSE.txt
            - 8059.8e640c3f.iframe.bundle.js
            - 8059.8e640c3f.iframe.bundle.js.LICENSE.txt
            - 8065.47ebbb5b.iframe.bundle.js
            - 8079.a8221028.iframe.bundle.js
            - 8079.a8221028.iframe.bundle.js.LICENSE.txt
            - 8130.480ac8f8.iframe.bundle.js
            - 8133.8250a0f9.iframe.bundle.js
            - 8133.8250a0f9.iframe.bundle.js.LICENSE.txt
            - 814.ff8209f7.iframe.bundle.js
            - 8140.b7d61fe2.iframe.bundle.js
            - 8140.b7d61fe2.iframe.bundle.js.LICENSE.txt
            - 8238.466b3c2d.iframe.bundle.js
            - 8433.35e36413.iframe.bundle.js
            - 8433.35e36413.iframe.bundle.js.LICENSE.txt
            - 8453.789925b4.iframe.bundle.js
            - 8453.789925b4.iframe.bundle.js.LICENSE.txt
            - 8577.668c32f5.iframe.bundle.js
            - 8577.668c32f5.iframe.bundle.js.LICENSE.txt
            - 8581.9b55345d.iframe.bundle.js
            - 8581.9b55345d.iframe.bundle.js.LICENSE.txt
            - 8761.ac2161d9.iframe.bundle.js
            - 8761.ac2161d9.iframe.bundle.js.LICENSE.txt
            - 8905.f344316e.iframe.bundle.js
            - 8905.f344316e.iframe.bundle.js.LICENSE.txt
            - 8917.22108e73.iframe.bundle.js
            - 8917.22108e73.iframe.bundle.js.LICENSE.txt
            - 8968.0f4bbe5d.iframe.bundle.js
            - 9013.737a05b0.iframe.bundle.js
            - 9013.737a05b0.iframe.bundle.js.LICENSE.txt
            - 9077.367dff8b.iframe.bundle.js
            - 9141.beef960e.iframe.bundle.js
            - 9141.beef960e.iframe.bundle.js.LICENSE.txt
            - 925.b856128e.iframe.bundle.js
            - 925.b856128e.iframe.bundle.js.LICENSE.txt
            - 931.2a454204.iframe.bundle.js
            - 931.2a454204.iframe.bundle.js.LICENSE.txt
            - 933.5a9893c9.iframe.bundle.js
            - 933.5a9893c9.iframe.bundle.js.LICENSE.txt
            - 9362.cb09134c.iframe.bundle.js
            - 9391.80cacb60.iframe.bundle.js
            - 9391.80cacb60.iframe.bundle.js.LICENSE.txt
            - 9428.e1f36aef.iframe.bundle.js
            - 9428.e1f36aef.iframe.bundle.js.LICENSE.txt
            - 9454.5eea41df.iframe.bundle.js
            - 9454.5eea41df.iframe.bundle.js.LICENSE.txt
            - 9454.5eea41df.iframe.bundle.js.map
            - 9485.2a97500f.iframe.bundle.js
            - 9485.2a97500f.iframe.bundle.js.LICENSE.txt
            - 9503.11cce125.iframe.bundle.js
            - 9566.c1606063.iframe.bundle.js
            - 9580.5e5a35b5.iframe.bundle.js
            - 9653.c28f7c12.iframe.bundle.js
            - 9653.c28f7c12.iframe.bundle.js.LICENSE.txt
            - 9773.9ce0d89d.iframe.bundle.js
            - 9773.9ce0d89d.iframe.bundle.js.LICENSE.txt
            - 9774.1cbb1777.iframe.bundle.js
            - 9849.1b0d64ba.iframe.bundle.js
            - 9849.1b0d64ba.iframe.bundle.js.LICENSE.txt
            - 9888.cbcde4df.iframe.bundle.js
            - 9915.9a02f0cf.iframe.bundle.js
            - 9957.402eaa1e.iframe.bundle.js
            - 9957.402eaa1e.iframe.bundle.js.LICENSE.txt
            - Alert-InlineBanner-story.71cc89a9.iframe.bundle.js
            - Alert-Toast-story.a0c34f42.iframe.bundle.js
            - AutoSaveField-AutoSaveField-story.83ac885b.iframe.bundle.js
            - Badge-Badge-story.764673d6.iframe.bundle.js
            - BarGauge-BarGauge-story.991738ce.iframe.bundle.js
            - BigValue-BigValue-story.a1c75375.iframe.bundle.js
            - Button-Button-story.a415cd2f.iframe.bundle.js
            - ButtonCascader-ButtonCascader-story.8a4560b7.iframe.bundle.js
            - Card-Card-story.d5063cbc.iframe.bundle.js
            - Cascader-Cascader-story.9ff0e4fc.iframe.bundle.js
            - ClickOutsideWrapper-ClickOutsideWrapper-story.d97a37b6.iframe.bundle.js
            - Collapse-CollapsableSection-story.b71ebc27.iframe.bundle.js
            - Collapse-Collapse-story.33987f9f.iframe.bundle.js
            - ColorPicker-ColorPicker-story.45735597.iframe.bundle.js
            - ColorPicker-ColorPickerPopover-story.38564d8c.iframe.bundle.js
            - ColorPicker-Palettes-story.27c6140f.iframe.bundle.js
            - Combobox-Combobox-story.ce35a8fd.iframe.bundle.js
            - ConfirmButton-ConfirmButton-story.91f975ba.iframe.bundle.js
            - ConfirmModal-ConfirmModal-story.7a83cbb5.iframe.bundle.js
            - ContextMenu-ContextMenu-story.752f060b.iframe.bundle.js
            - DataSourceSettings-DataSourceHttpSettings-story.c4acd90f.iframe.bundle.js
            - DataSourceSettings-DataSourceHttpSettings-story.c4acd90f.iframe.bundle.js.LICENSE.txt
            - DateTimePickers-DatePicker-DatePicker-story.4c9a7108.iframe.bundle.js
            - DateTimePickers-DatePickerWithInput-DatePickerWithInput-story.dd9c67c4.iframe.bundle.js
            - DateTimePickers-DateTimePicker-DateTimePicker-story.c01d19ac.iframe.bundle.js
            - DateTimePickers-RelativeTimeRangePicker-RelativeTimeRangePicker-story.38e5735a.iframe.bundle.js
            - DateTimePickers-TimeOfDayPicker-story.5dd47cbe.iframe.bundle.js
            - DateTimePickers-TimeRangeInput-story.aea02720.iframe.bundle.js
            - DateTimePickers-TimeRangePicker-story.64cabf72.iframe.bundle.js
            - DateTimePickers-TimeZonePicker-story.855a8318.iframe.bundle.js
            - DateTimePickers-WeekStartPicker-story.9c4a17b1.iframe.bundle.js
            - Divider-Divider-story.4b8ddb5c.iframe.bundle.js
            - Drawer-Drawer-story.e0186250.iframe.bundle.js
            - Dropdown-Dropdown-story.3a835c02.iframe.bundle.js
            - EmptySearchResult-EmptySearchResult-story.178d43de.iframe.bundle.js
            - EmptyState-EmptyState-story.d62dc656.iframe.bundle.js
            - ErrorBoundary-ErrorBoundary-story.72bcabe1.iframe.bundle.js
            - FeatureBadge-FeatureBadge-story.d5be6ce6.iframe.bundle.js
            - FileDropzone-FileDropzone-story.22ae6d30.iframe.bundle.js
            - FileDropzone-FileListItem-story.8e0b9121.iframe.bundle.js
            - FileUpload-FileUpload-story.1d662ce5.iframe.bundle.js
            - FilterPill-FilterPill-story.29005405.iframe.bundle.js
            - FormattedValueDisplay-FormattedValueDisplay-story.2db860f5.iframe.bundle.js
            - Forms-Checkbox-story.95ce5eec.iframe.bundle.js
            - Forms-Field-story.a624439b.iframe.bundle.js
            - Forms-FieldArray-story.664753c0.iframe.bundle.js
            - Forms-FieldSet-story.a6ffab9b.iframe.bundle.js
            - Forms-FieldValidationMessage-story.7faf7431.iframe.bundle.js
            - Forms-Form-story.90d3f52c.iframe.bundle.js
            - Forms-InlineField-story.1f0eabad.iframe.bundle.js
            - Forms-InlineFieldRow-story.697ae4ff.iframe.bundle.js
            - Forms-InlineLabel-story.f94690bb.iframe.bundle.js
            - Forms-Label-story.cdf4e950.iframe.bundle.js
            - Forms-Legend-story.9dc277af.iframe.bundle.js
            - Forms-RadioButtonGroup-RadioButtonGroup-story.8bea73b4.iframe.bundle.js
            - Forms-RadioButtonList-RadioButtonList-story.31b9fd4f.iframe.bundle.js
            - Icon-Icon-story.b6a18e28.iframe.bundle.js
            - IconButton-IconButton-story.9220cc38.iframe.bundle.js
            - InfoBox-InfoBox-story.159ecea4.iframe.bundle.js
            - Input-AutoSizeInput-story.ee9b03b9.iframe.bundle.js
            - Input-Input-story.dc421c1f.iframe.bundle.js
            - InteractiveTable-InteractiveTable-story.e49aa659.iframe.bundle.js
            - Intro-mdx.d35faf44.iframe.bundle.js
            - Layout-Box-Box-story.b9e35f8e.iframe.bundle.js
            - Layout-Grid-Grid-story.ba35b14b.iframe.bundle.js
            - Layout-Layout-story.1831736b.iframe.bundle.js
            - Layout-Space-story.08a9e479.iframe.bundle.js
            - Layout-Stack-Stack-story.13b7ceee.iframe.bundle.js
            - Link-TextLink-story.e46e07bd.iframe.bundle.js
            - LoadingBar-LoadingBar-story.8714b9b4.iframe.bundle.js
            - LoadingPlaceholder-LoadingPlaceholder-story.1129382a.iframe.bundle.js
            - Menu-Menu-story.63c080b8.iframe.bundle.js
            - Modal-Modal-story.1a62cf82.iframe.bundle.js
            - PageLayout-PageToolbar-story.5fa9d9a6.iframe.bundle.js
            - Pagination-Pagination-story.075cae05.iframe.bundle.js
            - PanelChrome-PanelChrome-story.af7105be.iframe.bundle.js
            - PanelChrome-PanelChrome-story.af7105be.iframe.bundle.js.map
            - PanelContainer-PanelContainer-story.f91d8542.iframe.bundle.js
            - PluginSignatureBadge-PluginSignatureBadge-story.9ecea5fa.iframe.bundle.js
            - QueryField-QueryField-story.831fd9ef.iframe.bundle.js
            - RefreshPicker-RefreshPicker-story.252236e5.iframe.bundle.js
            - RenderUserContentAsHTML-RenderUserContentAsHTML-story.ba0f9761.iframe.bundle.js
            - SecretInput-SecretInput-story.f2d13861.iframe.bundle.js
            - SecretTextArea-SecretTextArea-story.e031ef10.iframe.bundle.js
            - Segment-Segment-story.86d4be87.iframe.bundle.js
            - Segment-SegmentAsync-story.addea9ab.iframe.bundle.js
            - Segment-SegmentInput-story.d7926a07.iframe.bundle.js
            - Select-Select-story.4ed547eb.iframe.bundle.js
            - Slider-RangeSlider-story.84c190a8.iframe.bundle.js
            - Slider-Slider-story.a4a90ca4.iframe.bundle.js
            - Slider-Slider-story.a4a90ca4.iframe.bundle.js.LICENSE.txt
            - Spinner-Spinner-story.7a53df74.iframe.bundle.js
            - Splitter-useSplitter-story.e28d9f9e.iframe.bundle.js
            - StatsPicker-StatsPicker-story.23bd2225.iframe.bundle.js
            - Switch-Switch-story.7bbbd5e3.iframe.bundle.js
            - Table-Table-story.334399ac.iframe.bundle.js
            - Tabs-Tabs-story.28c764a9.iframe.bundle.js
            - Tags-Tag-story.0c1cf3cf.iframe.bundle.js
            - Tags-TagList-story.8ba38460.iframe.bundle.js
            - TagsInput-TagsInput-story.ee710600.iframe.bundle.js
            - Text-Text-story.371ccd61.iframe.bundle.js
            - TextArea-TextArea-story.67ae4b8c.iframe.bundle.js
            - ThemeDemos-ThemeDemo-story.6e28d5c6.iframe.bundle.js
            - ThemeDemos-ThemeDemo-story.6e28d5c6.iframe.bundle.js.LICENSE.txt
            - Toggletip-Toggletip-story.df8fa3c2.iframe.bundle.js
            - ToolbarButton-ToolbarButton-story.cd0df50f.iframe.bundle.js
            - ToolbarButton-ToolbarButtonRow-story.a62639fd.iframe.bundle.js
            - Tooltip-Tooltip-story.0fee74bc.iframe.bundle.js
            - UnitPicker-UnitPicker-story.939c83fe.iframe.bundle.js
            - UsersIndicator-Avatar-story.e0ef2819.iframe.bundle.js
            - UsersIndicator-UserIcon-story.bbd0f865.iframe.bundle.js
            - UsersIndicator-UsersIndicator-story.55b8da23.iframe.bundle.js
            - ValuePicker-ValuePicker-story.cfafa880.iframe.bundle.js
            - VizLayout-VizLayout-story.55848ce2.iframe.bundle.js
            - VizLegend-VizLegend-story.7d3f1932.iframe.bundle.js
            - VizTooltip-SeriesTable-story.b688eba2.iframe.bundle.js
            - favicon.svg
            - iframe.html
            - index.html
            - index.json
            - main.e9ee1e8a.iframe.bundle.js
            - main.e9ee1e8a.iframe.bundle.js.LICENSE.txt
            - project.json
            - react-monaco-editor.95b5bcf8.iframe.bundle.js
            - runtime~main.40c7ec87.iframe.bundle.js
          📂 tools/ [FORGE]
            - zoneinfo.zip
        📂 prometheus/ [FORGE]
          - LICENSE
          - NOTICE
          - prometheus.exe
          - prometheus.yml
          - promtool.exe
      📂 cribo/ [FORGE]
        - Cargo.lock
        - Cargo.toml
        - Dockerfile
        📂 src/ [FORGE]
          - main.rs
      📂 nano_knights/ [FORGE]
        - nano_crawler.py
      📂 rotel/ [FORGE]
        - Cargo.lock
        - Cargo.toml
        - Dockerfile
        📂 src/ [FORGE]
          - main.rs
      📂 rustdesk-server/ [FORGE]
        - .gitattributes
        - .gitmodules
        - Cargo.lock
        - Cargo.toml
        - LICENSE
        - MAINTENANCE_NOTE.md
        - README.md
        - build.rs
        - control-panel.bat
        - db_v2.sqlite3
        - docker-compose.yml
        📂 .cargo/ [FORGE]
          - config.toml
        📂 .github/ [FORGE]
          - dependabot.yml
          📂 ISSUE_TEMPLATE/ [FORGE]
            - bug_report.md
            - config.yml
            - feature_request.md
          📂 workflows/ [FORGE]
            - build.yaml
        📂 .vscode/ [FORGE]
          - settings.json
        📂 data/ [FORGE]
          - db_v2.sqlite3
          - db_v2.sqlite3-shm
          - db_v2.sqlite3-wal
          - id_ed25519
          - id_ed25519.pub
          📂 .config/ [FORGE]
        📂 debian/ [FORGE]
          - README.source
          - changelog
          - compat
          - control.tpl
          - copyright
          - rules
          - rustdesk-server-hbbr.install
          - rustdesk-server-hbbr.postinst
          - rustdesk-server-hbbr.postrm
          - rustdesk-server-hbbr.prerm
          - rustdesk-server-hbbs.install
          - rustdesk-server-hbbs.postinst
          - rustdesk-server-hbbs.postrm
          - rustdesk-server-hbbs.prerm
          - rustdesk-server-utils.install
          📂 source/ [FORGE]
            - format
        📂 docker/ [FORGE]
          - Dockerfile
          - healthcheck.sh
          📂 rootfs/ [FORGE]
        📂 docker-classic/ [FORGE]
          - Dockerfile
        📂 kubernetes/ [FORGE]
          - example.yaml
        📂 libs/ [FORGE]
          📂 hbb_common/ [FORGE]
            - .git
            - Cargo.toml
            - build.rs
        📂 rcd/ [FORGE]
          - rustdesk-hbbr
          - rustdesk-hbbs
        📂 src/ [FORGE]
          - common.rs
          - database.rs
          - hbbr.rs
          - lib.rs
          - main.rs
          - mod.rs
          - peer.rs
          - relay_server.rs
          - rendezvous_server.rs
          - utils.rs
          - version.rs
        📂 systemd/ [FORGE]
          - rustdesk-hbbr.service
          - rustdesk-hbbs.service
        📂 ui/ [FORGE]
          - Cargo.lock
          - Cargo.toml
          - build.rs
          - setup.nsi
          - tauri.conf.json
          📂 .cargo/ [FORGE]
            - config.toml
          📂 html/ [FORGE]
            - index.html
            - main.js
            - package.json
            - style.css
            - vite.config.js
          📂 icons/ [FORGE]
            - 128x128.png
            - 128x128@2x.png
            - 32x32.png
            - Square107x107Logo.png
            - Square142x142Logo.png
            - Square150x150Logo.png
            - Square284x284Logo.png
            - Square30x30Logo.png
            - Square310x310Logo.png
            - Square44x44Logo.png
            - Square71x71Logo.png
            - Square89x89Logo.png
            - StoreLogo.png
            - icon.icns
            - icon.ico
            - icon.png
          📂 setup/ [FORGE]
          📂 src/ [FORGE]
            - lib.rs
            - main.rs
    📂 kinetic_sovereign/ [FORGE]
      - go.mod
      - go.sum
      - kinetic-sovereign.exe
      - main.go
      📂 src/ [FORGE]
    📂 packages/ [FORGE]
      📂 anya-domain/ [FORGE]
        - package.json
        📂 src/ [FORGE]
          - index.ts
          - ironGate.ts
          - rustdesk.ts
          - titanLink.ts
          - types.ts
      📂 anya-lyte/ [FORGE]
        - App.tsx
        - package.json
        📂 migrations/ [FORGE]
          - 0001_agency_factory.sql
        📂 src/ [FORGE]
          - App.tsx
          📂 api/ [FORGE]
            - titanlink_client.ts
          📂 components/ [FORGE]
            - Hudson.tsx
          📂 db/ [FORGE]
            - schema.ts
          📂 services/ [FORGE]
            - AvatarManager.ts
            - TitanLink.ts
          📂 ui/ [FORGE]
            - ApprovalSheet.tsx
            - ChatScreen.tsx
            - JobsScreen.tsx
            - RemoteControlScreen.tsx
            - SettingsScreen.tsx
            - VoiceDeck.tsx
      📂 pocket-squire/ [FORGE]
        - eslint.config.mjs
        - next-env.d.ts
        - next.config.js
        - package.json
        - postcss.config.mjs
        - tsconfig.json
        📂 app/ [FORGE]
          - favicon.ico
          - globals.css
          - layout.tsx
          - page.tsx
        📂 public/ [FORGE]
          - file.svg
          - globe.svg
          - manifest.json
          - next.svg
          - vercel.svg
          - window.svg
        📂 src/ [FORGE]
          📂 lib/ [FORGE]
            - kernel-bridge.ts
    📂 pocket_squire/ [FORGE]
      - eslint.config.mjs
      - next-env.d.ts
      - next.config.ts
      - package.json
      - postcss.config.mjs
      - tsconfig.json
      📂 public/ [FORGE]
        - file.svg
        - globe.svg
        - next.svg
        - vercel.svg
        - window.svg
      📂 src/ [FORGE]
        📂 app/ [FORGE]
          - favicon.ico
          - globals.css
          - layout.tsx
          - page.tsx
    📂 scrcpy/ [FORGE]
      - FAQ.md
      - LICENSE
      - README.md
      - build.gradle
      - bump_version
      - cross_win32.txt
      - cross_win64.txt
      - gradle.properties
      - gradlew
      - gradlew.bat
      - install_release.sh
      - meson.build
      - meson_options.txt
      - run
      - settings.gradle
      📂 .github/ [FORGE]
        - FUNDING.yml
        📂 ISSUE_TEMPLATE/ [FORGE]
          - bug_report.md
          - feature_request.md
          - question.md
        📂 workflows/ [FORGE]
          - release.yml
      📂 app/ [FORGE]
        - meson.build
        - scrcpy-windows.manifest
        - scrcpy-windows.rc
        - scrcpy.1
        📂 data/ [FORGE]
          - icon.ico
          - icon.png
          - icon.svg
          - open_a_terminal_here.bat
          - scrcpy-console.bat
          - scrcpy-console.desktop
          - scrcpy-noconsole.vbs
          - scrcpy.desktop
          📂 bash-completion/ [FORGE]
            - scrcpy
          📂 zsh-completion/ [FORGE]
            - _scrcpy
        📂 deps/ [FORGE]
          - README
          - adb_linux.sh
          - adb_macos.sh
          - adb_windows.sh
          - common
          - dav1d.sh
          - ffmpeg.sh
          - libusb.sh
          - sdl.sh
        📂 src/ [FORGE]
          - audio_player.c
          - audio_player.h
          - audio_regulator.c
          - audio_regulator.h
          - cli.c
          - cli.h
          - clock.c
          - clock.h
          - common.h
          - compat.c
          - compat.h
          - control_msg.c
          - control_msg.h
          - controller.c
          - controller.h
          - coords.h
          - decoder.c
          - decoder.h
          - delay_buffer.c
          - delay_buffer.h
          - demuxer.c
          - demuxer.h
          - device_msg.c
          - device_msg.h
          - display.c
          - display.h
          - events.c
          - events.h
          - file_pusher.c
          - file_pusher.h
          - fps_counter.c
          - fps_counter.h
          - frame_buffer.c
          - frame_buffer.h
          - icon.c
          - icon.h
          - input_events.h
          - input_manager.c
          - input_manager.h
          - keyboard_sdk.c
          - keyboard_sdk.h
          - main.c
          - mouse_capture.c
          - mouse_capture.h
          - mouse_sdk.c
          - mouse_sdk.h
          - opengl.c
          - opengl.h
          - options.c
          - options.h
          - packet_merger.c
          - packet_merger.h
          - receiver.c
          - receiver.h
          - recorder.c
          - recorder.h
          - scrcpy.c
          - scrcpy.h
          - screen.c
          - screen.h
          - server.c
          - server.h
          - shortcut_mod.h
          - v4l2_sink.c
          - v4l2_sink.h
          - version.c
          - version.h
          📂 adb/ [FORGE]
            - adb.c
            - adb.h
            - adb_device.c
            - adb_device.h
            - adb_parser.c
            - adb_parser.h
            - adb_tunnel.c
            - adb_tunnel.h
          📂 android/ [FORGE]
            - input.h
            - keycodes.h
          📂 hid/ [FORGE]
            - hid_event.h
            - hid_gamepad.c
            - hid_gamepad.h
            - hid_keyboard.c
            - hid_keyboard.h
            - hid_mouse.c
            - hid_mouse.h
          📂 sys/ [FORGE]
          📂 trait/ [FORGE]
            - frame_sink.h
            - frame_source.c
            - frame_source.h
            - gamepad_processor.h
            - key_processor.h
            - mouse_processor.h
            - packet_sink.h
            - packet_source.c
            - packet_source.h
          📂 uhid/ [FORGE]
            - gamepad_uhid.c
            - gamepad_uhid.h
            - keyboard_uhid.c
            - keyboard_uhid.h
            - mouse_uhid.c
            - mouse_uhid.h
            - uhid_output.c
            - uhid_output.h
          📂 usb/ [FORGE]
            - aoa_hid.c
            - aoa_hid.h
            - gamepad_aoa.c
            - gamepad_aoa.h
            - keyboard_aoa.c
            - keyboard_aoa.h
            - mouse_aoa.c
            - mouse_aoa.h
            - scrcpy_otg.c
            - scrcpy_otg.h
            - screen_otg.c
            - screen_otg.h
            - usb.c
            - usb.h
          📂 util/ [FORGE]
            - acksync.c
            - acksync.h
            - audiobuf.c
            - audiobuf.h
            - average.c
            - average.h
            - binary.h
            - env.c
            - env.h
            - file.c
            - file.h
            - intmap.c
            - intmap.h
            - intr.c
            - intr.h
            - log.c
            - log.h
            - memory.c
            - memory.h
            - net.c
            - net.h
            - net_intr.c
            - net_intr.h
            - process.c
            - process.h
            - process_intr.c
            - process_intr.h
            - rand.c
            - rand.h
            - str.c
            - str.h
            - strbuf.c
            - strbuf.h
            - term.c
            - term.h
            - thread.c
            - thread.h
            - tick.c
            - tick.h
            - timeout.c
            - timeout.h
            - vecdeque.h
            - vector.h
        📂 tests/ [FORGE]
          - test_adb_parser.c
          - test_audiobuf.c
          - test_binary.c
          - test_cli.c
          - test_control_msg_serialize.c
          - test_device_msg_deserialize.c
          - test_orientation.c
          - test_str.c
          - test_strbuf.c
          - test_vecdeque.c
          - test_vector.c
      📂 assets/ [FORGE]
        - screenshot-debian-600.jpg
      📂 config/ [FORGE]
        - android-checkstyle.gradle
        📂 checkstyle/ [FORGE]
          - checkstyle.xml
      📂 doc/ [FORGE]
        - audio.md
        - build.md
        - camera.md
        - connection.md
        - control.md
        - develop.md
        - device.md
        - gamepad.md
        - keyboard.md
        - linux.md
        - macos.md
        - mouse.md
        - otg.md
        - recording.md
        - shortcuts.md
        - tunnels.md
        - v4l2.md
        - video.md
        - virtual_display.md
        - window.md
        - windows.md
      📂 gradle/ [FORGE]
        📂 wrapper/ [FORGE]
          - gradle-wrapper.jar
          - gradle-wrapper.properties
      📂 release/ [FORGE]
        - build_common
        - build_linux.sh
        - build_macos.sh
        - build_server.sh
        - build_windows.sh
        - generate_checksums.sh
        - package_client.sh
        - package_server.sh
        - release.sh
        - test_client.sh
        - test_server.sh
      📂 server/ [FORGE]
        - build.gradle
        - build_without_gradle.sh
        - meson.build
        - proguard-rules.pro
        📂 scripts/ [FORGE]
          - build-wrapper.sh
        📂 src/ [FORGE]
          📂 main/ [FORGE]
            - AndroidManifest.xml
          📂 test/ [FORGE]
    📂 tools/ [FORGE]
      📂 awesome-cli/ [FORGE]
        - check-for-deprecation.sh
  📂 03_VAULT/ [SECURE]
    - .modal.toml
    - ARCHITECTURE.md
    - CONTROL_SCHEMATIC.md
    - PROVENANCE_LEDGER.md
    - README.md
    - installation_id
    - khoj-docker-compose.yml
    - vault_manager.py
    📂 .secure/ [SECURE]
      - cost_ledger.jsonl
      - master.key
      - vault.enc
      - vault_master.key
      📂 key_backups/ [SECURE]
        - vault_master.key.20260412_152748.bak
    📂 00_SECURE_ARCHIVE/ [SECURE]
      - .example.env
      - 2da8309b_.env.development.local
      - 51f49886869bdb28660ea21e25f354c3_.env
      - 5d7ded41_.env.bundle
      - 61b1c3e3_.env.local
      - 82170b47_.env.tests
      - 8abaaa5d_.env.txt
      - 9391a7b5_.env.txt
      - CAMELOT_ARCHIVE_FINAL.zip
      - a347e580_forge.env.d.ts
      - b460f3f0480053f8da667c02f3a23e97_.env
      - c8f151f5_.env.e2e
      - d2f5c94e_.env.production.local
      - docker.env
      - e60377bc_.env.local
      - f3abe8bb_.env.local
      - logs.json
      - sample.env
      - settings.env
      📂 QUARANTINE_ENV/ [SECURE]
        - _00_SECURE_ARCHIVE_EXTERNAL_WORKSPACE_Misc_LLM-Applications_scripts_awesome-llm-apps_rag_tutorials_agentic_rag_math_agent_config_env.quarantine
        - _00_SECURE_ARCHIVE_EXTERNAL_WORKSPACE_Misc_LLM-Applications_scripts_awesome-llm-apps_starter_ai_agents_local_news_agent_openai_swarm_env.quarantine
        - _00_SECURE_ARCHIVE_EXTERNAL_WORKSPACE_Misc_inspira_FInalized_env.quarantine
        - _00_SECURE_ARCHIVE_EXTERNAL_WORKSPACE_Misc_inspira_temp_repo_analysis_env.quarantine
        - _03_VAULT_00_SECURE_ARCHIVE_env.quarantine
        - _03_VAULT_gemini_extensions_gemini-flow_node_modules_bottleneck_env.quarantine
        - _env.quarantine
    📂 00_TEMPLATES/ [SECURE]
      - BEAVER_TECTONIC_CARTRIDGE.md
      - PRD_TEMPLATE.md
    📂 99_HISTORY/ [SECURE]
      - AGNO_SESSION_LOG.md
    📂 99_SCRATCHPAD/ [SECURE]
      - Learning_Log.md
      - dummy_sales.csv
      - efficiency_metrics.json
      - loom_state.json
      - mrr_report.md
      - performance_metrics.json
      📂 Gemini-plans/ [SECURE]
      📂 SCAVENGE_DOWNLOADS/ [SECURE]
        - The CameloOS 2_.0 Bible copy right (1).docx
        - The CameloOS 2_.0 Bible copy right.docx
        - act as 🧙_♂️ Merlin, the Mythosmith_ The Weaver of.pdf
        - ai_studio_code (1).html
        - ai_studio_code (1).py
        - ai_studio_code (2).html
        - ai_studio_code.html
        - ai_studio_code.py
        - book Father's camelot a journal of AI.docx
        - ssh-key-2025-10-09 (1).key
        - ssh-key-2025-10-09.key
        - ssh-key-2025-10-09.key (1).pub
        - ssh-key-2025-10-09.key.pub
        - ssh-key-2026-01-13 (1).key
        - ssh-key-2026-01-13 (2).key
        - ssh-key-2026-01-13.key
        - ssh-key-2026-01-13.key (1).pub
        - ssh-key-2026-01-13.key (2).pub
        - ssh-key-2026-01-13.key.pub
      📂 SCAVENGE_WORKSPACE/ [SECURE]
        - blueprint.mermaid
    📂 BOUNTY_HUNTER/ [SECURE]
    📂 CAMELOT_NOTEBOOK/ [SECURE]
      📂 decisions/ [SECURE]
      📂 personas/ [SECURE]
    📂 CLOUD_SYNC/ [SECURE]
      - MANIFEST_LATEST.json
    📂 COMMERCE/ [SECURE]
    📂 EXTERNAL_TOOLS/ [SECURE]
    📂 GLYPHS/ [SECURE]
      - ANYA_SEED_Ω.json
    📂 HCCP-Strategy/ [SECURE]
    📂 KINETIC_REFERENCES/ [SECURE]
      📂 CrIBo/ [SECURE]
        - LICENSE
        - README.md
        - eval_launcher.py
        - main_cribo.py
        📂 checkpoints/ [SECURE]
          - vitb16-in_args.json
          - vits16-coco_args.json
          - vits16-in_args.json
        📂 cribo_utils/ [SECURE]
          - data_transforms.py
          - datasets.py
          - hpc.py
          - parser.py
        📂 figures/ [SECURE]
          - cribo_pipeline.jpg
        📂 segmentation/ [SECURE]
          - __init__.py
          📂 configs/ [SECURE]
            - __init__.py
          📂 models/ [SECURE]
            - __init__.py
            - concat_fcn.py
            - dino_vision_transformer.py
            - freezable_vision_transformer.py
          📂 tools/ [SECURE]
            - __init__.py
            - train.py
        📂 source/ [SECURE]
          - __init__.py
          📂 datasets/ [SECURE]
            - __init__.py
            - ade20k.py
            - dummy_dataset.py
            - imagenet100_dataset.py
            - pascal_voc_aug.py
          📂 models/ [SECURE]
            - __init__.py
            - resnet.py
            - swin_transformer.py
            - vision_transformer.py
          📂 utils/ [SECURE]
            - __init__.py
            - utils.py
      📂 rotel/ [SECURE]
        - Cargo.lock
        - Cargo.toml
        - DEVELOPING.md
        - Dockerfile
        - Dockerfile.clickhouse-ddl
        - Dockerfile.context-processor
        - Dockerfile.python-processor
        - KAFKA_INTEGRATION_TESTS.md
        - LICENSE
        - README.md
        - RELEASING.md
        - build.rs
        - docker-compose.kafka-test.yml
        - rust-toolchain.toml
        📂 .github/ [SECURE]
          📂 workflows/ [SECURE]
            - auto-release.yml
            - auto-tag.yml
            - bump-version.yml
            - ci.yml
            - processor-release.yml
            - release.yml
            - rotel-sdk-release.yml
        📂 benches/ [SECURE]
          - clone_trace_request_bench.rs
          - encode_otlp_trace_bench.rs
          - flume_bench.rs
        📂 examples/ [SECURE]
          - .keep
        📂 otel_benchmark_builder/ [SECURE]
          📂 otel-collector/ [SECURE]
            - Makefile
            - build.sh
            - builder-config.yaml
            - collector-config.yaml
        📂 proto/ [SECURE]
          📂 datadog/ [SECURE]
            - agent_payload.proto
            - span.proto
            - stats.proto
            - tracer_payload.proto
        📂 rotel_python_processor_sdk/ [SECURE]
          - Cargo.lock
          - Cargo.toml
          - pyproject-dist.toml
          - pyproject.toml
          📂 processors/ [SECURE]
            - attributes_processor.py
            - context_processor.py
            - redaction_processor.py
          📂 python_tests/ [SECURE]
            - add_log_record_test.py
            - attributes_processor_test.py
            - context_processor_test.py
            - read_and_write_attributes_array_value_test.py
            - read_and_write_attributes_key_value_list_test.py
            - read_and_write_instrumentation_scope_test.py
            - read_and_write_logs_test.py
            - read_and_write_metrics_test.py
            - read_and_write_resource_entities_test.py
            - read_and_write_spans_test.py
            - read_key_value_key_test.py
            - read_key_value_value_test.py
            - read_resource_attributes_test.py
            - read_value_test.py
            - redaction_processor_blocking_test.py
            - redaction_processor_log_body_test.py
            - redaction_processor_restrictive_test.py
            - remove_log_record_test.py
            - resource_attributes_append_attribute.py
            - resource_attributes_set_attributes.py
            - resource_logs_append_attribute.py
            - resource_spans_append_attribute.py
            - resource_spans_iterate_spans.py
            - set_instrumentation_scope_test.py
            - set_scope_spans_span_test.py
            - traces_delitem_test.py
            - write_bool_value_test.py
            - write_bytes_value_test.py
            - write_key_value_bytes_value_test.py
            - write_key_value_key_test.py
            - write_key_value_value_test.py
            - write_resource_attributes_key_value_key_test.py
            - write_resource_attributes_key_value_value_test.py
            - write_resource_spans_resource_test.py
            - write_scope_spans_test.py
            - write_span_events_test.py
            - write_spans_test.py
            - write_string_value_test.py
          📂 rotel_sdk/ [SECURE]
            - README.md
            - __init__.py
          📂 src/ [SECURE]
            - lib.rs
        📂 scripts/ [SECURE]
          - benchmark-file-receiver.sh
          - kafka-test-env.sh
          - measure-latency.sh
          - nginx-log-generator.sh
          - verify-file-receiver.sh
        📂 src/ [SECURE]
          - bounded_channel.rs
          - crypto.rs
          - lib.rs
          - listener.rs
          📂 aws_api/ [SECURE]
            - arn.rs
            - auth.rs
            - creds.rs
            - error.rs
            - host.rs
            - mod.rs
          📂 bin/ [SECURE]
          📂 exporters/ [SECURE]
            - blackhole.rs
            - crypto_init_tests.rs
            - mod.rs
          📂 init/ [SECURE]
            - activation.rs
            - agent.rs
            - args.rs
            - awsemf_exporter.rs
            - batch.rs
            - clickhouse_exporter.rs
            - config.rs
            - datadog_exporter.rs
            - file_exporter.rs
            - file_receiver.rs
            - fluent_receiver.rs
            - kafka_exporter.rs
            - kafka_receiver.rs
            - misc.rs
            - mod.rs
            - otlp_exporter.rs
            - otlp_receiver.rs
            - parse.rs
            - pprof.rs
            - retry.rs
            - wait.rs
            - xray_exporter.rs
          📂 otlp/ [SECURE]
            - cvattr.rs
            - mod.rs
          📂 receivers/ [SECURE]
            - mod.rs
            - otlp_output.rs
          📂 semconv/ [SECURE]
            - cloud.rs
            - containers.rs
            - db_system.rs
            - misc.rs
            - mod.rs
          📂 telemetry/ [SECURE]
            - internal_exporter.rs
            - metrics_server.rs
            - mod.rs
          📂 topology/ [SECURE]
            - batch.rs
            - batch_resources.rs
            - fanout.rs
            - flush_control.rs
            - generic_pipeline.rs
            - mod.rs
            - payload.rs
            - processors.rs
        📂 test/ [SECURE]
          📂 data/ [SECURE]
        📂 tests/ [SECURE]
          - kafka_integration_tests.rs
          📂 integration/ [SECURE]
            - kafka_integration_tests.rs
        📂 utilities/ [SECURE]
          - Cargo.lock
          - Cargo.toml
          📂 src/ [SECURE]
            - lib.rs
            - otlp.rs
    📂 Knights/ [SECURE]
      - README.md
      - SYSTEM_PERSONAS_CRYSTAL.md
      📂 Creative/ [SECURE]
        - Amara_Aura.md
        - Dame_Maya.md
        - Sir_Sonus.md
        - Sir_Visage.md
      📂 Engineering/ [SECURE]
        - Sir_Alchemist.md
        - Sir_Architect.md
        - Sir_Boris.md
        - Sir_ForgeMaster.md
        - Sir_Scribe.md
        - Sir_SkillSmith.md
        - Sir_Systéma.md
        - Sir_WebFarer.md
      📂 Finance/ [SECURE]
        - Sir_Sterling.md
      📂 Governance/ [SECURE]
        - Anya_Ω.md
        - Elder_Kaelen.md
        - Lady_Veritas.md
        - Sir_Arthur.md
        - Sir_Aurelius.md
        - Sir_Octavian.md
        - Sir_Proxy_Knight.md
      📂 Growth/ [SECURE]
        - Sir_Growth.md
      📂 Kinetic/ [SECURE]
        - Lukas_Ω.md
      📂 Memory/ [SECURE]
        - Sir_Myrmidon.md
        - Sir_Octavian.md
      📂 Monitoring/ [SECURE]
        - Sir_Chrome_Warden.md
        - Sir_Kronos.md
      📂 Perception/ [SECURE]
        - Sir_Aurora.md
      📂 Reasoning/ [SECURE]
        - Merlin_Ω.md
        - Sir_Aris.md
        - Sir_Vega.md
      📂 Research/ [SECURE]
        - Lady_Apis.md
      📂 Security/ [SECURE]
        - Sir_Castor.md
        - Sir_Sentinel_Ω.md
      📂 Strategy/ [SECURE]
        - General_Strategos.md
      📂 Substrate/ [SECURE]
        - Morgana_Ω.md
      📂 souls/ [SECURE]
        - anya_soul.txt
        - apis_soul.txt
        - arthur_soul.txt
        - aura_soul.txt
        - aurelius_soul.txt
        - boris_soul.txt
        - forge_soul.txt
        - lukas_soul.txt
        - merlin_soul.txt
        - morgana_soul.txt
        - sentinel_soul.txt
        - sonus_soul.txt
        - visage_soul.txt
    📂 LEGAL/ [SECURE]
      - CONSTITUTION.md
      📂 IP_FORTRESS/ [SECURE]
        - CAMELOT_APEX_IP_DECLARATION.md
        - EULA.md
        - NARRATIVE_BIBLE.md
        - SOURCE_CODE_INVENTORY.md
        - TOPOLOGY_SPEC.md
    📂 LLM-Apps-Ref/ [SECURE]
      📂 Advanced-Agents/ [SECURE]
        📂 agent_teams/ [SECURE]
          📂 ai_competitor_intelligence_agent_team/ [SECURE]
            - competitor_agent_team.py
          📂 ai_finance_agent_team/ [SECURE]
            - finance_agent_team.py
          📂 ai_game_design_agent_team/ [SECURE]
            - game_design_agent_team.py
          📂 ai_legal_agent_team/ [SECURE]
            - legal_agent_team.py
          📂 ai_real_estate_agent_team/ [SECURE]
            - ai_real_estate_agent_team.py
            - local_ai_real_estate_agent_team.py
          📂 ai_recruitment_agent_team/ [SECURE]
            - ai_recruitment_agent_team.py
          📂 ai_services_agency/ [SECURE]
            - agency.py
          📂 ai_teaching_agent_team/ [SECURE]
            - teaching_agent_team.py
          📂 ai_travel_planner_agent_team/ [SECURE]
          📂 multimodal_coding_agent_team/ [SECURE]
            - ai_coding_agent_o3.py
          📂 multimodal_design_agent_team/ [SECURE]
            - design_agent_team.py
        📂 ai_Self-Evolving_agent/ [SECURE]
          - ai_Self-Evolving_agent.py
        📂 ai_aqi_analysis_agent/ [SECURE]
          - ai_aqi_analysis_agent_gradio.py
          - ai_aqi_analysis_agent_streamlit.py
        📂 ai_domain_deep_research_agent/ [SECURE]
          - ai_domain_deep_research_agent.py
        📂 ai_email_gtm_outreach_agent/ [SECURE]
          - ai_email_gtm_outreach_agent.py
        📂 ai_financial_coach_agent/ [SECURE]
          - ai_financial_coach_agent.py
        📂 ai_mental_wellbeing_agent/ [SECURE]
          - ai_mental_wellbeing_agent.py
        📂 ai_news_and_podcast_agents/ [SECURE]
          📂 beifong/ [SECURE]
            - __init__.py
            - bootstrap_demo.py
            - celery_worker.py
            - main.py
            - pack_demo.py
            - ruff.toml
            - scheduler.py
          📂 web/ [SECURE]
            - .prettierrc.json
            - package.json
        📂 ai_speech_trainer_agent/ [SECURE]
          📂 backend/ [SECURE]
            - main.py
          📂 frontend/ [SECURE]
            - Home.py
            - page_congif.py
            - sidebar.py
            - style.css
          📂 visuals/ [SECURE]
            - ai_speech_trainer.drawio.png
            - feedback.png
            - home.png
        📂 multi_agent_researcher/ [SECURE]
          - research_agent.py
          - research_agent_llama3.py
        📂 product_launch_intelligence_agent/ [SECURE]
          - product_launch_intelligence_agent.py
      📂 MCP-Agents/ [SECURE]
        📂 ai_travel_planner_mcp_agent_team/ [SECURE]
          - app.py
        📂 browser_mcp_agent/ [SECURE]
          - main.py
          - mcp_agent.config.yaml
          - mcp_agent.secrets.yaml.example
        📂 github_mcp_agent/ [SECURE]
          - github_agent.py
        📂 multi_mcp_agent/ [SECURE]
          - multi_mcp_agent.py
        📂 notion_mcp_agent/ [SECURE]
          - notion_mcp_agent.py
        📂 react_native_agent/ [SECURE]
          - mcp_server.py
          - native.py
    📂 Missions/ [SECURE]
      - verification_ledger.jsonl
    📂 Nano-Knights/ [SECURE]
      - README.md
      - Sir_Forge.md
      - Sir_Sentinel.md
      - Squire_Audit.md
      - Squire_Clean.md
      - Squire_Format.md
      - background.iife.js
      - background.js
      - bg.jpg
      - buildDomTree.js
      - content_sentry.js
      - icon-128.png
      - icon-32.png
      - llm_client.js
      - manifest.json
      - offscreen.html
      - offscreen.js
      - options.css
      - options.html
      - options.js
      - package.json
      - popup.css
      - popup.html
      - popup.js
      - skills_registry.js
      - vault_bridge.js
      📂 Assimilation_Reports/ [SECURE]
        - CAMELOT_OS.code-workspace
        - assimilation_report_cherry_studio.md
        - assimilation_report_openclaw.md
        - assimilation_report_pi_mono.md
        - awesome_cli_apps_report.md
      📂 _locales/ [SECURE]
        📂 en/ [SECURE]
          - messages.json
        📂 zh_TW/ [SECURE]
          - messages.json
      📂 content/ [SECURE]
        - _content.css
        - index.iife.js
      📂 options/ [SECURE]
        - _options.css
        - index.html
        - war_room.html
        - war_room.js
        📂 assets/ [SECURE]
          - index--c-fjoQp.js
          - index-Zp7vqqqw.css
      📂 permission/ [SECURE]
        - index.html
        - permission.js
      📂 side-panel/ [SECURE]
        - index.html
        📂 assets/ [SECURE]
          - index-BmTGaeXG.css
          - index-CQ9-rncf.js
        📂 icons/ [SECURE]
          - navigator.svg
          - planner.svg
          - system.svg
          - user.svg
          - validator.svg
      📂 side_panel/ [SECURE]
        - research_panel.css
        - research_panel.html
        - research_panel.js
      📂 src/ [SECURE]
        - action_resolver.js
        📂 agents/ [SECURE]
          - agent_hand.js
        📂 diagnostics/ [SECURE]
          - diagnostic_core.js
        📂 intelligence/ [SECURE]
          - synthesis_engine.js
        📂 knights/ [SECURE]
          - knight_spawner.js
          - personas.js
        📂 logic/ [SECURE]
          - action_executor.js
          - chunk_manager.js
          - cognitive_parser.js
          - context_pruner.js
          - hive_crawler.js
          - observer.js
          - specialized_skills.js
          - vision_healer.js
        📂 prometheus/ [SECURE]
          - encoder.js
          - graphrag.js
          - index.js
          - memory_exporter.js
          - sentinel.js
        📂 security/ [SECURE]
          - auth_manager.js
          - crypto_utils.js
          - crypto_vault.js
          - profile_manager.js
          - proxy_manager.js
          - stealth_injector.js
        📂 skills/ [SECURE]
          - social_skills.js
        📂 squires/ [SECURE]
          - resource_squire.js
          - voice_squire.js
      📂 tests/ [SECURE]
        - test_chunk_manager.js
        - test_cognitive_parser.js
        - test_context_pruner.js
        - test_data_privacy.js
        - test_nano_knights.js
        - test_ouroboros.js
        - test_persona_logic.js
        - test_prometheus_integration.js
        - test_self_healing.js
        - test_social_engineering.js
        - test_specialized_skills.js
        - test_stealth.js
        - test_token_efficiency.js
        - test_voice_squire.js
        - verify_agent_logic.js
    📂 PROMPTS/ [SECURE]
      - OMEGA_TRANSCENDENCE_ENHANCER.md
    📂 Protocols/ [SECURE]
      - AGENT_FORGE_PROTOCOL.md
      - CHIMERA_AUDIT_PROTOCOL.md
      - CHROME_WARDEN_PROTOCOL.md
      - DEFENSE_GRID_PROTOCOL.md
      - DISTILLER_PROTOCOL.md
      - ENGINE_TECHNICAL_SCAN.md
      - GENESIS_PROTOCOL.md
      - KINETIC_GOOSE_INTEGRATION.md
      - KNIGHT_FORGE_PROTOCOL.md
      - NDR_S_PROTOCOL.md
      - NOTTE_PROTOCOL.md
      - TRIPLE_QFT_PROTOCOL.md
      - VERDENT_CLAW_PROTOCOL.md
    📂 SENSES/ [SECURE]
    📂 SNIPPETS/ [SECURE]
    📂 UKG/ [SECURE]
      - AEGIS_DEFENSE_GRID.toon
      - AGENT_ARMOR_PDG.toon
      - AGENT_FORGE.toon
      - AIOS_KERNEL_CONCURRENCY.toon
      - ANYA_v6_CONFIG.json
      - CAMELOT_APEX_Ω_PRIME_CRYSTAL.jsonld
      - CAMELOT_APEX_Ω_PRIME_CRYSTAL.nkg
      - CAMELOT_STERLING_PRIME.toon
      - CHIMERA_SWARM_LOGIC.toon
      - CHROME_DEVTOOLS_MCP.toon
      - DISTILLER_PRIME.toon
      - ENGINE_TECH_SYNTHESIS.toon
      - GENESIS_PROTOCOL.toon
      - KINETIC_GOOSE_INTEGRATION.toon
      - KNIGHT_INTERNAL_ARCH.toon
      - KNIGHT_OMEGA_UPGRADE.toon
      - MERLIN_PERSONA.jsonld
      - MULTIMODAL_VIDEO_RAG.toon
      - NOTTE.toon
      - NPE_SINGULARITY_V4.toon
      - SALTARE_GATEWAY.toon
      - TRIPLE_QFT.toon
      - UKG_MEMORY.jsonld
      - VERDENT_CLAW.toon
      - current_state.json
      - distilled_80af2d6f.jsonld
      - kinetic_seeds.json
      📂 CARTRIDGES/ [SECURE]
        - CAMELOT_APEX_v214_2_0.toon
        - Ω_DISTILL_AND_RECONSTRUCT.nkg
        - Ω_KINETIC_DELTA_CRUSADE.md
      📂 SCHEMAS/ [SECURE]
        - ukg_persona_schema.json
      📂 nodes/ [SECURE]
        - Assimilation_Protocol_UKG.json
        - CLIProxyAPI_Assimilation_UKG.json
        - Inspira_Analysis_UKG.json
        - Sovereign_Ecosystem_UKG.json
        📂 swarm/ [SECURE]
          - manifest.json
    📂 WorkOrders/ [SECURE]
      - AGENTFORGE_ASSIMILATION.md
      - CHROME_WARDEN_INTEGRATION.md
      - NOTTE_ASSIMILATION.md
      📂 queue/ [SECURE]
    📂 credentials/ [SECURE]
      - google_accounts.json
      - oauth_creds.json
      - settings.json
    📂 data_store/ [SECURE]
      📂 Data/ [SECURE]
        - database.sqlite
        📂 sqlite-db/ [SECURE]
          - checkpoints.sqlite
        📂 tiktoken-cache/ [SECURE]
        📂 uploads/ [SECURE]
    📂 directives/ [SECURE]
      - completed_log.json
      - pending_queue.json
    📂 docs/ [SECURE]
      - sovereign_swarm_strategy.md
    📂 evidence/ [SECURE]
      - knight_scout_01_evidence.png
      - phantom_v2_test.png
      - {{KNIGHT_ID}}_evidence.png
    📂 external/ [SECURE]
      📂 EXTERNAL/ [SECURE]
    📂 incoming/ [SECURE]
    📂 knowledge/ [SECURE]
      - distilled_80af2d6f.jsonld
      - lerndatei.jsonld
      📂 AUDITS/ [SECURE]
        - report_v3.markdown
      📂 CLI_RESOURCES/ [SECURE]
        📂 awesome-cli-apps/ [SECURE]
          - readme.md
          📂 media/ [SECURE]
            - banner.png
      📂 LEGAL/ [SECURE]
        - MASTER_IP_STRATEGY.md
        📂 Copyright/ [SECURE]
          - 00_MASTER_COPYRIGHT_COMPILATION.pdf
          - 01_PROPRIETARY_LICENSE.pdf
          - 02_COPYRIGHT_DECLARATION.pdf
          - 03_IP_STRATEGY.pdf
          - 04_TRADEMARK_REGISTER.pdf
          - 05_TRADE_SECRET_MANIFEST.pdf
          - 06_EULA.pdf
          - 07_IP_DECLARATION.pdf
          - 08_CONSTITUTION.pdf
          - 09_TITANIUM_LAWS.pdf
          - 10_THIRD_PARTY_NOTICE.pdf
          - 11_COPYRIGHT_HEADERS.pdf
          - 12_PROVENANCE_LEDGER.pdf
          - 13_MASTER_GLOSSARY.pdf
          - generate_pdfs.py
          - glossary_raw.txt
      📂 TITAN_SWARM/ [SECURE]
        - ASSIMILATION_MAPPING.md
        - INTEGRATION_BLUEPRINT.md
        - PHASE_1_COMPLETE.md
        - QUICK_REFERENCE.md
      📂 persona_library/ [SECURE]
        - kinetic_architect.jsonld
        - legal_lawkeeper.jsonld
        - lukas.json
        - merlin.json
        - persona.schema.json
        - registry_index.json
        - sec_expert.json
        - security_auditor.jsonld
        - sir_webfarer.json
        - strategy_oracle.jsonld
        - swarm_conductor.jsonld
        - system_engineer.jsonld
        - ux_guardian.jsonld
      📂 reasoning_bank/ [SECURE]
        - reasoning_02A85F2A.json
        - reasoning_2A51A36F.json
        - reasoning_92849C1B.json
        - reasoning_AA6BB7CF.json
        - reasoning_B07E77D1.json
        - reasoning_C76A612E.json
        - reasoning_D5AFAE1B.json
        - reasoning_D8AEF8E8.json
        - reasoning_DE5039B9.json
    📂 merlins-think-tank/ [SECURE]
      - ARCHITECTURE.md
      - CONSTITUTION.md
      - README.md
    📂 skills/ [SECURE]
      📂 browser-forensics/ [SECURE]
        - SKILL.md
      📂 forge-coding/ [SECURE]
        - SKILL.md
      📂 oracle-planning/ [SECURE]
        - SKILL.md
      📂 research-apis/ [SECURE]
        - SKILL.md
      📂 sentinel-security/ [SECURE]
        - SKILL.md
      📂 systematic-debugging/ [SECURE]
        - SKILL.md
    📂 temp_mcp/ [SECURE]
      - mcp_server.py
    📂 training/ [SECURE]
      - golden_samples.jsonl
      📂 configs/ [SECURE]
        - .aiexclude
        - BOOTSTRAP.md
        - OS_MANIFEST.md
        - PROVENANCE_LEDGER.md
        - TestRunnerAgent.py
        - anya.py
        - append_ledger.py
        - bridge.py
        - camelot-os
        - camelot-os.ps1
        - camelot.py
        - camelot_cli.py
        - camelot_gradio.py
        - chat.py
        - claude.md
        - gemini.md
        - hud.py
        - llm_router.py
        - merlin.py
        - notebooklm_bridge.py
        - ouroboros.db
        - ouroboros.py
        - plan.md
        - requirements.txt
        - run_agent_cmd.sh
        - verify_v400.py
        📂 cartridges/ [SECURE]
          - nextjs.yaml
          - python-api.yaml
          - reasoning.yaml
          - rust-kinetic.yaml
          - security.yaml
          - swarm-colony.yaml
          - voice-media.yaml
        📂 config/ [SECURE]
          - mcp_config.json
          - mcp_servers.json
          - omniroute.json
          - saltare.toml
        📂 context/ [SECURE]
          - HALLUCINATION_PROTOCOL.md
        📂 kinetic_edge/ [SECURE]
          📂 mcp_server/ [SECURE]
            - Cargo.toml
        📂 knights/ [SECURE]
          - __init__.py
          - agenteer.py
          - alchemist.py
          - architect.py
          - base.py
          - boris.py
          - coder.py
          - creative.py
          - debug.py
          - forgemaster.py
          - lancelot.py
          - researcher.py
          - sentinel.py
          - stitch.py
          - syntax.py
          - synthesis.py
          - vaelen.py
          - warden.py
        📂 memory/ [SECURE]
          - toon_ukg_full.json
          - ukg_graph.jsonld
          - ukg_graph_v300.2.md
        📂 skills/ [SECURE]
          - NPE_PERSONAS.md
          - PYTHON.md
          - REASONING.md
          - SECURITY.md
          - SWARM.md
          - TYPESCRIPT.md
          - VISUAL.md
          - VOICE.md
        📂 tests/ [SECURE]
          - __init__.py
          - test_anya.py
          - test_bridge.py
          - test_camelot_cli.py
          - test_knights.py
          - test_llm_router.py
          - test_notebooklm_bridge.py
          - test_ouroboros.py
    📂 verification/ [SECURE]
  📂 05_INFRASTRUCTURE/
    📂 secrets/
  📂 LisaCustomKeychains/
    - .eslintrc.json
    - ARCHITECTURE.md
    - Applications.code-workspace
    - CAMELOT_OS_MANIFEST.md
    - HANDOVER.md
    - HIVE_DIRECTIVE.md
    - LICENSE
    - PROVENANCE_LEDGER.md
    - README.md
    - SHOPIFY_CHECKOUT_INTEGRATION.md
    - SHOPIFY_CLEANUP_REPORT.md
    - SWARM_REPORT.md
    - TASK.md
    - VERIFICATION.md
    - inspect_images_output.txt
    - inspect_output.json
    - inventory_log.txt
    - listings_log.txt
    - next.config.mjs
    - package.json
    - postcss.config.mjs
    - publish_all_log.txt
    - publish_log.txt
    - publish_log_2.txt
    - pubs.json
    - sync_full_log.txt
    - sync_full_log_utf8.txt
    - tailwind.config.ts
    - tsconfig.json
    - verify_check_final.txt
    - verify_check_final_2.txt
    - verify_compact.txt
    - verify_compact_final.txt
    - verify_final_3.txt
    - verify_final_4.txt
    - verify_output.txt
    - verify_output_utf8.txt
    - verify_raw.txt
    - verify_specific.txt
    - verify_specific_2.txt
    - verify_specific_3.txt
    - verify_specific_final.txt
    - verify_storefront_final.txt
    - verify_utf8.txt
    - vitest.config.ts
    📂 .agent/
      - agents.md
      - audit_report.json
      - audit_report_v2.json
      📂 prompts/
        - SHOPIFY_SYNC_VALIDATION.md
      📂 skills/
        📂 FORGE_TITAN/ [FORGE]
          - SKILL.md
        📂 PRP_GENERATOR/
          - SKILL.md
        📂 RED_TEAM_AUDITOR/
          - SKILL.md
        📂 TDD_ARCHITECT/
          - SKILL.md
        📂 UI_UX_AUDIT/
          - SKILL.md
        📂 kinetic_bridge/
          - SKILL.md
      📂 workflows/
        - blueprint-forge.md
        - connect_domain.md
        - deep-dive-audit.md
        - deploy.md
        - forge-titan-actuate.md
        - mock-reforge.md
        - shopify-sync.md
    📂 docs/
      - CUSTOMIZER_ARCHITECTURE.md
      - SHOPIFY_ADMIN_AUTH_GUIDE.md
      📂 audits/
        - TASK.md
        - UIUX_AUDIT_BLUEPRINT.md
        - VERIFICATION.md
    📂 public/
      - featured-earrings.jpg
      📂 images/
        - 1000011817.jpg
        - 1000012019.jpg
        - 1000012138.jpg
        - 1000012195.jpg
        - 1000012197.jpg
        - 1000020990.jpg
        - 1000020991.jpg
        - 1000020992.jpg
        - 1000020993.jpg
        - 1473986136160.jpg
        - 1474164466462.jpg
        - 1529285017581-529.jpg
        - 20180228_134138.jpg
        - 20180228_134358.jpg
        - 20180419_165849.jpg
        - 20180605_225108.jpg
        - 20180605_225132.jpg
        - 20180707_193545.jpg
        - 20180711_211046.jpg
        - 590264777_25630868533184608_3338479643030823326_n.jpg
        - Lisa'sSelfie.jpg
        - assorted_charms_heritage.jpg
        - custom_heart_earrings.jpg
        - earrings_1.jpg
        - earrings_2.jpg
        - earrings_3.jpg
        - earrings_feature.jpg
        - featured_model_earrings.jpg
        - heart_earrings_close_up.jpg
        - lisa_maker_profile.png
        - mockearring.png
        📂 sports/
          - basketball_mockup.jpg
          - football_mockup.jpg
          - soccer_mockup.jpg
          - softball_mockup.jpg
    📂 scripts/
      - audit_product_metadata.js
      - camelot.js
      - camelot_utils.js
      - check_shopify_domains.js
      - check_shopify_prices.js
      - check_shopify_redirects.js
      - create_earrings_admin.js
      - enable_overselling.js
      - hash1.txt
      - hash2.txt
      - hash3.txt
      - inspect_earring_images.js
      - inspect_product_admin.js
      - list_all_domains.js
      - list_publications.js
      - probe_earrings.js
      - publish_all_channels.js
      - publish_earrings.js
      - publish_via_listings.js
      - scrape_etsy.js
      - sync_shopify_all.js
      - sync_shopify_products.js
      - test_admin_connection.js
      - test_admin_direct.js
      - test_auth.js
      - test_cart.js
      - test_mock_fallback.js
      - test_mock_fallback.ts
      - test_shopify_connection.js
      - test_with_lib.js
      - update_inventory.js
      - verify_earring_charms.js
      - verify_image_url.js
      - verify_shopify.js
      - verify_specific_product.js
      - verify_sync_probe.js
    📂 src/
      📂 app/
        - LisaCustomKeychains.com.code-workspace
        - error.tsx
        - globals.css
        - layout.tsx
        - page.tsx
        - sitemap.ts
        📂 api/
          📂 design-ai/
            - route.ts
        📂 customize/
          - page.tsx
        📂 dev-portal/
          - page.tsx
        📂 sports/
          - page.tsx
      📂 components/
        - AboutSection.tsx
        - BlogSection.tsx
        - CartDrawer.tsx
        - CartProvider.tsx
        - DedicationSection.tsx
        - EventsSection.tsx
        - FeaturedSection.tsx
        - Footer.tsx
        - HeritageSection.tsx
        - HeroSection.tsx
        - Navbar.tsx
        - NotificationSentry.tsx
        - PolaroidWrapper.tsx
        - ProductCard.tsx
        - ProductGallery.tsx
        - ProductGrid.tsx
        - ProductJSONLD.tsx
        - SEOWrapper.tsx
        - SocialFeedSection.tsx
        - TestimonySection.tsx
        - VibeInput.tsx
        📂 customize/
          - EarringCustomizer.tsx
          - KeychainBuilder.tsx
          - KeychainCustomizer.tsx
          - SetCustomizer.tsx
        📂 ui/
          - sheet.tsx
      📂 lib/
        - crm.ts
        - data.ts
        - shopify.ts
        - types.ts
        - utils.ts
        - vibeEngine.ts
        📂 agents/
          - vibe_mapper.py
        📂 camelot/
          - index.ts
          - laws.ts
          - registry.ts
          - schemas.ts
          - tiers.ts
          📂 __tests__/
            - registry.test.ts
        📂 shopify/
          - mocks.ts
          - types.ts
        📂 validation/
          - earring.ts
          - keychain.ts
      📂 mocks/
        📂 content/
          - .gitkeep
        📂 entities/
          - .gitkeep
        📂 state/
          - .gitkeep
        📂 streams/
          - .gitkeep
        📂 visual/
          - .gitkeep
      📂 test/
        - setup.ts
  📂 bin/
    - awaken.py
    - bifrost.py
    - test_oracle.py
  📂 cloud/
    - __init__.py
  📂 cloud_orchestrator/
    - __init__.py
    - long_term_cloudbrain.py
    - modal_brain.py
    - modal_services.py
  📂 config/
    - tiers.yaml
  📂 control_plane/ [CONTROL]
    - __init__.py
    - camelot_cli.py
    - cli_intercept.py
    - cloud_services.py
    - cloudbrain_sync.py
    - config_manager.py
    - deerflow_sandbox.py
    - ledger_sync.py
    - main.py
    - omc_team.py
    - provenance.py
    - sarda_engine.py
    - soul_router.py
    - supabase_bridge.py
    - test_runner_agent.py
  📂 docs/
    - AGENTS.md
    - CAMELOT_BIBLE.md
    - CAMELOT_THREADS_GLYTH_V1.yaml
    - CONTRIBUTING.md
    - GEMINI.md
    - INDEX.md
    - OS_MANIFEST.md
    - PROVENANCE_LEDGER.md
    - newtech.md
    - upgrade.txt
    - Ω_SCOUT_SWARM.nkg
    📂 EXTERNAL/
      📂 piper/
        📂 models/
          📂 en_GB-alba-medium/
            - en_GB-alba-medium.onnx
            - en_GB-alba-medium.onnx.json
          📂 en_GB-cori-medium/
            - en_GB-cori-medium.onnx
            - en_GB-cori-medium.onnx.json
          📂 en_GB-jenny_dioco-medium/
            - en_GB-jenny_dioco-medium.onnx
            - en_GB-jenny_dioco-medium.onnx.json
          📂 en_US-joe-medium/
            - en_US-joe-medium.onnx
            - en_US-joe-medium.onnx.json
          📂 en_US-lessac-high/
            - en_US-lessac-high.onnx
            - en_US-lessac-high.onnx.json
          📂 en_US-lessac-medium/
            - en_US-lessac-medium.onnx
            - en_US-lessac-medium.onnx.json
          📂 en_US-ryan-medium/
            - en_US-ryan-medium.onnx
            - en_US-ryan-medium.onnx.json
    📂 architecture/
      - AGENTS.md
      - EMPIRE_MAP.md
      - SOLO_FACTORY_BLUEPRINT.md
      - SOURCE_OF_TRUTH_MAP.md
      - UNIVERSAL_MCP_SYSTEM.md
      📂 ANYA/
      📂 ARCH/
        - ANYA_MOBILE_BRIDGE.md
        - FORGE_ARCHITECTURE.md
        - INSTRUCTION_GOVERNANCE.md
        - KERNEL_ARCHITECTURE.md
        - L7_ETHEREAL_SPEC.md
        - ORACLE_SYSTEM_DIAGRAM.mermaid
        - SIR_MASQUE_UKG.jsonld
        - STRATEGY_CAMELOT_APEX_V200.jsonld
        - VAULT_ARCHITECTURE.md
        - docker-compose-swarm.yml
    📂 diagrams/
      - sentinel_audit_architecture.md
    📂 guides/
      - BEST_PRACTICES.md
      - DEFENSE_GRID_AGENT_RUNBOOK.md
      - HIVE_IDE_OMEGA_MANUAL.md
      - LUKAS_Ω_EDGE_BOOTSTRAP_v2.0.nkg
      - NANO_KNIGHTS_MANUAL.md
      - TROUBLESHOOTING_STRATEGY.md
      - USER_TUTORIAL.md
      📂 MANUALS/
      📂 TUTORIALS/
      📂 USE_CASES/
    📂 plans/
      - MAX_COMPRESSION_STRATEGY.md
      - OVERHAUL_BLUEPRINT.md
      - PLATFORM_BRAINSTORM.md
      - SMALL_LLM_GRID_ENHANCEMENTS.md
      - TASK.md
      📂 ENHANCEMENTS/
      📂 ROADMAP/
      📂 STRATEGY/
    📂 protocols/
      - agno_orchestrator.md
      - assimilation_v2.md
      - assimilation_v3.md
      - assimilation_v4_omega.md
      - assimilation_v5_evolution.md
      - cellular_protocol.md
      - hive_forge_v1.md
      - iron_gate_protocol.md
      - lukas_architect.md
      - merlin_identity_forge.md
      - paladin_htn_protocol.md
      - persona_evolution_protocol.md
      - squire_protocol.md
      - titan_protocol.md
      - ukg_integration_v206.md
      - xp_economy_protocol.md
      📂 BOOT_PROTOCOLS/
      📂 LAWS/
        - CONSTITUTION.md
        - TITANIUM_LAWS.md
      📂 PERSONA/
        - ukg_persona_schema.json
    📂 reference/
      - ARTIFACTS.md
      - COMMANDS.md
      - GEMINI.md
      - MEDIA_BRIDGE_CONTROL.md
      - MODAL_RUNBOOK.md
      - PROTOCOLS.md
      📂 ARTIFACTS/
        - test_synthesis.wav
        - Ω_ASSIMILATION_ENGINE.nkg
        - Ω_CAMELOT_SINGULARITY_v100.nkg
        - Ω_INTEGRATION_CONFIGS.nkg
        - Ω_PHASE_1_BLUEPRINTS.nkg
        - Ω_PHASE_2_BLUEPRINTS.nkg
        📂 voice_samples/
      📂 EXTERNAL/
        📂 AgentFlow/
          - LICENSE
          - pyproject.toml
          - quick_start.py
          - setup.sh
          📂 agentflow/
            - .env.template
            - __init__.py
            - client.py
            - config.py
            - litagent.py
            - logging.py
            - pyproject.toml
            - reward.py
            - runner.py
            - server.py
            - trainer.py
            - types.py
          📂 assets/
          📂 data/
            - aime24_data.py
            - get_train_data.py
          📂 scripts/
            - restart_ray.sh
            - serve_vllm.sh
            - setup_stable_gpu.sh
          📂 test/
            - calculate_score_unified.py
            - solve.py
            - utils.py
          📂 train/
            - config.yaml
            - rollout.py
            - rollout_dev.py
            - serve_with_logs.sh
            - train_agent.py
            - train_with_logs.sh
            - utils.py
          📂 util/
            - __init__.py
            - get_pub_ip.py
            - model_merger.py
            - parse_config.py
            - port_cleanup.py
            - upload_hf_model.py
        📂 CogFlow/
          📂 Llama-Factory/
            - .dockerignore
            - .gitattributes
            - .pre-commit-config.yaml
            - CITATION.cff
            - LICENSE
            - MANIFEST.in
            - Makefile
            - pyproject.toml
            - setup.py
          📂 attention_visualizer/
            - attention_calculater.py
            - attention_visualizer.py
            - config_cog.json
            - sankey_visualizer_en.html
            - sankey_visualizer_zh.html
          📂 data_generation/
            - api_config.py
            - chain_adder.py
            - chain_eval_utils.py
            - chain_evaluater.py
            - chain_output_eval.py
            - chain_process_eval.py
            - cogflow_simulate.py
            - collect_and_convert_to_dataset.py
            - evaluate_template.py
            - generate_and_collect.sh
            - prompt_template_json.py
            - run_all.py
            - scene_gen.py
            - utils_4.py
          📂 dataset/
            - rm_eval.json
            - rm_test.json
            - rm_train.json
            - test.json
            - train.json
          📂 figure/
            - cognitive_flow_training_framwork.png
          📂 test/
            - config_tokenizer.py
            - run_all.sh
            - run_rm.py
            - run_rollout.py
          📂 veRL/
            - .readthedocs.yaml
            - .style.yapf
            - LICENSE
            - pyproject.toml
            - setup.py
        📂 DesktopCommanderMCP/
          - .codespellrc
          - .npmignore
          - 1080_60.mp4
          - Dockerfile
          - LICENSE
          - config.json
          - header.png
          - install.sh
          - logo.png
          - package.json
          - setup-claude-server.js
          - smithery.yaml
          - tsconfig.json
          📂 .github/
            - FUNDING.yml
          📂 docs/
            - .htaccess
            - CNAME
            - apple-touch-icon.png
            - browserconfig.xml
            - cropped_video.mp4
            - favicon-96x96.png
            - favicon.ico
            - favicon.png
            - favicon.svg
            - header.png
            - index.html
            - logo.png
            - site copy.webmanifest
            - site.webmanifest
            - sitemap.xml
            - testimonials.png
            - testimonials_1080.png
            - vertical_video_mobile.mp4
            - web-app-manifest-192x192.png
            - web-app-manifest-512x512.png
          📂 scripts/
            - analyze-fuzzy-logs.js
            - clear-fuzzy-logs.js
            - export-fuzzy-logs.js
            - sync-version.js
            - view-fuzzy-logs.js
          📂 src/
            - command-manager.ts
            - config-manager.ts
            - config.ts
            - custom-stdio.ts
            - error-handlers.ts
            - index.ts
            - server.ts
            - terminal-manager.ts
            - types.ts
            - version.ts
          📂 test/
            - run-all-tests.js
            - test-allowed-directories.js
            - test-blocked-commands.js
            - test-directory-creation.js
            - test-edit-block-line-endings.js
            - test-edit-block-occurrences.js
            - test-error-sanitization.js
            - test-home-directory.js
            - test.js
          📂 testemonials/
            - analyticsindiamag.png
            - img.png
            - img_1.png
            - img_2.png
            - img_3.png
            - img_4.png
        📂 Fooocus/
          - .dockerignore
          - .gitattributes
          - Dockerfile
          - LICENSE
          - args_manager.py
          - auth-example.json
          - build_launcher.py
          - docker-compose.yml
          - entry_with_update.py
          - entrypoint.sh
          - environment.yaml
          - experiments_expansion.py
          - experiments_face.py
          - experiments_interrogate.py
          - experiments_mask_generation.py
          - fooocus_colab.ipynb
          - fooocus_version.py
          - launch.py
          - notification-example.mp3
          - shared.py
          - webui.py
          📂 .github/
            - CODEOWNERS
            - dependabot.yml
          📂 css/
            - style.css
          📂 extras/
            - censor.py
            - expansion.py
            - face_crop.py
            - inpaint_mask.py
            - interrogate.py
            - ip_adapter.py
            - preprocessors.py
            - resampler.py
            - vae_interpose.py
            - wd14tagger.py
          📂 javascript/
            - contextMenus.js
            - edit-attention.js
            - imageviewer.js
            - localization.js
            - script.js
            - viewer.js
            - zoom.js
          📂 language/
            - en.json
            - example.json
          📂 ldm_patched/
          📂 models/
          📂 modules/
            - __init__.py
            - anisotropic.py
            - async_worker.py
            - auth.py
            - config.py
            - constants.py
            - core.py
            - default_pipeline.py
            - extra_utils.py
            - flags.py
            - gradio_hijack.py
            - hash_cache.py
            - html.py
            - inpaint_worker.py
            - launch_util.py
            - localization.py
            - lora.py
            - meta_parser.py
            - model_loader.py
            - ops.py
            - patch.py
            - patch_clip.py
            - patch_precision.py
            - private_logger.py
            - sample_hijack.py
            - sdxl_styles.py
            - style_sorter.py
            - ui_gradio_extensions.py
            - upscaler.py
            - util.py
          📂 presets/
            - anime.json
            - default.json
            - lcm.json
            - lightning.json
            - playground_v2.5.json
            - pony_v6.json
            - realistic.json
            - sai.json
          📂 sdxl_styles/
            - sdxl_styles_diva.json
            - sdxl_styles_fooocus.json
            - sdxl_styles_marc_k3nt3l.json
            - sdxl_styles_mre.json
            - sdxl_styles_sai.json
            - sdxl_styles_twri.json
          📂 tests/
            - __init__.py
            - test_extra_utils.py
            - test_utils.py
          📂 wildcards/
        📂 Geo-Phone/
          - LICENSE
          - installer.sh
          - maps.jpg
          - phone.png
          - phone.py
        📂 MultiTalk/
          - Dockerfile
          - test.sh
          - train.sh
          📂 MultiTalk_dataset/
            - dataset.sh
            - download_and_process.py
          📂 assets/
            - statistic.png
            - teaser.png
          📂 base/
            - __init__.py
            - baseTrainer.py
            - base_model.py
            - config.py
            - utilities.py
          📂 config/
          📂 dataset/
            - __init__.py
            - data_loader_multi.py
          📂 demo/
          📂 eval_avlr/
            - avlr_utils.py
            - eval_avlr.py
            - utils.py
          📂 main/
            - __init__.py
            - cal_metric.py
            - demo_dir.py
            - test_multi_pred.py
            - train_multi_pred.py
            - train_multi_vq.py
          📂 metrics/
            - __init__.py
            - loss.py
          📂 models/
            - __init__.py
            - stage1_vocaset.py
            - stage2.py
            - utils.py
          📂 sample_dataset/
            - templates.pkl
          📂 scripts/
            - __init__.py
            - demo.sh
            - test.sh
            - train_multi.sh
          📂 utils/
            - __init__.py
            - base_model_util.py
            - util.py
        📂 OpenVoice/
          - LICENSE
          - demo_part1.ipynb
          - demo_part2.ipynb
          - demo_part3.ipynb
          - setup.py
          📂 checkpoints_v2/
          📂 docs/
          📂 openvoice/
            - __init__.py
            - api.py
            - attentions.py
            - commons.py
            - mel_processing.py
            - models.py
            - modules.py
            - openvoice_app.py
            - se_extractor.py
            - transforms.py
            - utils.py
          📂 resources/
            - demo_speaker0.mp3
            - demo_speaker1.mp3
            - demo_speaker2.mp3
            - example_reference.mp3
            - framework-ipa.png
            - huggingface.png
            - lepton-hd.png
            - myshell-hd.png
            - openvoicelogo.jpg
            - tts-guide.png
            - voice-clone-guide.png
        📂 Shoutify/
          - .env.example
          - .eslintignore
          - .eslintrc.json
          - .npmrc
          - .nvmrc
          - .prettierignore
          - .prettierrc.json
          - LICENSE
          - commitlint.config.js
          - next-env.d.ts
          - next.config.mjs
          - package.json
          - postcss.config.cjs
          - postcss.config.js
          - tailwind.config.cjs
          - tsconfig.json
          📂 .github/
            - CODE_OF_CONDUCT.md
            - CONTRIBUTING.md
            - HACKING.md
            - TWITTER.md
          📂 .husky/
            - pre-commit
          📂 .storybook/
            - main.js
            - preview.js
          📂 prisma/
            - schema.prisma
          📂 public/
            - favicon.ico
          📂 src/
        📂 SuperAGI/
          - .dockerignore
          - .gitattributes
          - .pre-commit-config.yaml
          - Dockerfile
          - Dockerfile-gpu
          - DockerfileCelery
          - DockerfileRedis
          - LICENSE
          - README.MD
          - alembic.ini
          - cli2.py
          - config.yaml
          - config_template.yaml
          - docker-compose-dev.yaml
          - docker-compose-gpu.yml
          - docker-compose.image.example.yaml
          - docker-compose.yaml
          - entrypoint.sh
          - entrypoint_celery.sh
          - install_tool_dependencies.sh
          - local-llm
          - local-llm-gpu
          - main.py
          - package.json
          - run.bat
          - run.sh
          - run_gui.py
          - run_gui.sh
          - test.py
          - test_main.http
          - tools.json
          - ui.py
          - wait-for-it.sh
          📂 .do/
            - app.yaml
            - deploy.template.yaml
          📂 .github/
            - PULL_REQUEST_TEMPLATE.md
          📂 gui/
            - .dockerignore
            - .eslintrc.json
            - Dockerfile
            - DockerfileProd
            - jsconfig.json
            - next.config.js
            - package.json
          📂 migrations/
            - README
            - env.py
            - script.py.mako
          📂 nginx/
            - default.conf
          📂 static/
            - super-agi-1.png
          📂 superagi/
            - __init__.py
            - tool_manager.py
            - worker.py
          📂 tests/
            - __init__.py
          📂 tgwui/
            - DockerfileTGWUI
          📂 workspace/
        📂 activepieces/
          - .all-contributorsrc
          - .dockerignore
          - .editorconfig
          - .env.example
          - .eslintignore
          - .eslintrc.base.json
          - .eslintrc.json
          - .npmrc
          - .nvmrc
          - .nxignore
          - .prettierignore
          - .prettierrc
          - .typos.toml
          - Dockerfile
          - LICENSE
          - commitlint.config.js
          - crowdin.yml
          - depot.json
          - docker-compose.dev.yml
          - docker-compose.test.yml
          - docker-compose.yml
          - docker-entrypoint.sh
          - jest.config.ts
          - jest.preset.js
          - karma.conf.js
          - migrations.json
          - nginx.react.conf
          - nx.json
          - package.json
          - project.json
          - tsconfig.base.json
          📂 .devcontainer/
            - Dockerfile
            - codespaces.sh
            - default.cf
            - devcontainer.json
            - docker-compose.yml
            - setup.sh
          📂 .github/
            - CODE_OF_CONDUCT.md
            - pre-release-drafter.yml
            - pull_request_template.md
            - release-drafter.yml
            - stale.yml
          📂 .husky/
            - commit-msg
            - pre-push
          📂 .verdaccio/
            - config.yml
          📂 .vscode/
            - extensions.json
            - launch.json
            - settings.json
          📂 assets/
            - ap-logo.png
          📂 deploy/
          📂 docs/
            - favicon.png
            - favicon.svg
            - mint.json
            - openapi.json
            - script.js
          📂 packages/
          📂 tools/
            - deploy.sh
            - reset-dev.sh
            - reset.sh
            - setup-dev.js
            - tsconfig.tools.json
            - update.sh
        📂 atomic_agents/
          - .coveragerc
          - .flake8
          - LICENSE
          - poetry.lock
          - pyproject.toml
          - setup.py
          📂 .assets/
            - architecture_highlevel_overview.png
            - atomic-cli-tool-menu.png
            - atomic-cli.png
            - docs.png
            - logo.png
            - video-thumbnail-1.png
            - video-thumbnail-2.png
            - video-thumbnail.png
            - what_is_sent_in_prompt.png
          📂 .github/
            - funding.yml
          📂 atomic-agents/
            - MANIFEST.in
          📂 atomic-assembler/
          📂 atomic-examples/
          📂 atomic-forge/
          📂 docs/
            - index.html
          📂 guides/
        📂 awesome_opencode/
          - LICENSE
          - package.json
          📂 .github/
            - PULL_REQUEST_TEMPLATE.md
          📂 data/
            - schema.json
          📂 docs/
          📂 scripts/
            - export-json.js
            - generate-readme.js
            - validate.js
          📂 templates/
        📂 big-AGI/
          - .dockerignore
          - .prettierrc
          - Dockerfile
          - LICENSE
          - docker-compose.yaml
          - eslint.config.mjs
          - middleware_BASIC_AUTH.ts
          - next.config.ts
          - package.json
          - tsconfig.json
          📂 .github/
            - FUNDING.yml
            - dependabot.yml
          📂 app/
          📂 docs/
          📂 kb/
          📂 pages/
            - _app.tsx
            - _document.tsx
            - call.tsx
            - diff.tsx
            - draw.tsx
            - index.tsx
            - news.tsx
            - personas.tsx
            - tokens.tsx
            - workspace.tsx
          📂 public/
            - apple-touch-icon.png
            - favicon.ico
            - manifest.json
          📂 src/
            - data.ts
          📂 tools/
        📂 bolt.diy/
          - .dockerignore
          - .editorconfig
          - .env.example
          - .prettierignore
          - .prettierrc
          - .tool-versions
          - Dockerfile
          - LICENSE
          - bindings.sh
          - docker-compose.yaml
          - eslint.config.mjs
          - load-context.ts
          - package.json
          - tsconfig.json
          - uno.config.ts
          - vite.config.ts
          - worker-configuration.d.ts
          - wrangler.toml
          📂 .github/
          📂 .husky/
            - pre-commit
          📂 app/
            - commit.json
            - entry.client.tsx
            - entry.server.tsx
            - root.tsx
          📂 docs/
            - mkdocs.yml
            - poetry.lock
            - pyproject.toml
          📂 functions/
            - [[path]].ts
          📂 icons/
            - chat.svg
            - logo-text.svg
            - logo.svg
            - stars.svg
          📂 public/
            - favicon.svg
            - logo-dark-styled.png
            - logo-dark.png
            - logo-light-styled.png
            - logo-light.png
            - logo.svg
            - social_preview_index.jpg
          📂 types/
            - istextorbinary.d.ts
        📂 github-repo-to-prompt/
          - app.py
        📂 goose/
          - .dockerignore
          - .gitattributes
          - .goosehints
          - Cargo.lock
          - Cargo.toml
          - Cross.toml
          - Dockerfile
          - Justfile
          - LICENSE
          - download_cli.ps1
          - download_cli.sh
          - flake.lock
          - flake.nix
          - goose-self-test.yaml
          - recipe.yaml
          - rust-toolchain.toml
          - test_acp_client.py
          📂 .devcontainer/
            - Dockerfile
            - devcontainer.json
          📂 .github/
            - CODEOWNERS
            - copilot-instructions.md
            - pull_request_template.md
          📂 .husky/
            - pre-commit
          📂 .intersect/
            - intersect-config.yaml
          📂 bin/
            - .just-1.40.0.pkg
            - .node-24.10.0.pkg
            - .protoc-31.1.pkg
            - .rustup-1.28.2.pkg
            - .temporal-cli-1.3.0.pkg
            - README.hermit.md
            - activate-hermit
            - activate-hermit.fish
            - cargo
            - cargo-clippy
            - cargo-fmt
            - cargo-miri
            - clippy-driver
            - corepack
            - hermit
            - hermit.hcl
            - just
            - node
            - npm
            - npx
            - protoc
            - rls
            - rust-analyzer
            - rust-gdb
            - rust-gdbgui
            - rust-lldb
            - rustc
            - rustdoc
            - rustfmt
            - rustup
            - temporal
          📂 clippy-baselines/
          📂 crates/
          📂 documentation/
            - .goosehints
            - .npmrc
            - docusaurus.config.ts
            - package.json
            - postcss.config.js
            - sidebars.ts
            - tailwind.config.js
            - tsconfig.json
          📂 examples/
            - frontend_tools.py
          📂 recipe-scanner/
            - Dockerfile
            - base_recipe.yaml
            - config.yaml
            - decode-training-data.py
            - scan-recipe.sh
          📂 scripts/
            - check-no-native-tls.sh
            - check-openapi-schema.sh
            - clean-gh-pages.sh
            - clippy-baseline.sh
            - clippy-lint.sh
            - goose-db-helper.sh
            - parse-benchmark-results.sh
            - run-benchmarks.sh
            - test_compaction.sh
            - test_lead_worker.sh
            - test_mcp.sh
            - test_providers.sh
            - test_subrecipes.sh
            - test_web.sh
          📂 ui/
        📂 kestra/
          - .editorconfig
          - .gitattributes
          - .gitpod.yml
          - .plugins
          - .prettierignore
          - Dockerfile
          - Dockerfile.pr
          - LICENSE
          - Makefile
          - build-and-start-e2e-tests.sh
          - build.gradle
          - codecov.yml
          - docker-compose-ci.yml
          - docker-compose-dind.yml
          - docker-compose.yml
          - gradle.properties
          - gradlew
          - gradlew.bat
          - lombok.config
          - owasp-dependency-suppressions.xml
          - settings.gradle
          📂 .devcontainer/
            - Dockerfile
            - README.md
            - devcontainer.json
          📂 .github/
            - CODE_OF_CONDUCT.md
            - CONTRIBUTING.md
            - dependabot.yml
            - node_option_env_var.png
            - pull_request_template.md
            - run-app.png
          📂 cli/
            - build.gradle
          📂 core/
            - build.gradle
          📂 dev-tools/
            - check-plugin-artifacts.sh
            - copy-plugin.sh
            - release-plugins.sh
            - setversion-tag-plugins.sh
            - update-plugin-kestra-version.sh
          📂 docker/
          📂 e2e-tests/
            - build.gradle
          📂 executor/
            - build.gradle
          📂 gradle/
          📂 jdbc/
            - build.gradle
          📂 jdbc-h2/
            - build.gradle
          📂 jdbc-mysql/
            - build.gradle
          📂 jdbc-postgres/
            - build.gradle
          📂 jmh-benchmarks/
            - build.gradle
          📂 model/
            - build.gradle
          📂 platform/
            - build.gradle
          📂 processor/
            - build.gradle
          📂 repository-memory/
            - build.gradle
          📂 runner-memory/
            - build.gradle
          📂 scheduler/
            - build.gradle
          📂 script/
            - build.gradle
          📂 storage-local/
            - build.gradle
          📂 tests/
            - build.gradle
          📂 ui/
            - .jshintrc
            - .nvmrc
            - build.gradle
            - eslint.config.js
            - index.html
            - package.json
            - run-e2e-tests.sh
            - stylelint.config.mjs
            - tsconfig.json
            - vite.config.js
            - vitest.config.js
            - vitest.config.unit.js
            - vitest.shims.d.ts
          📂 webserver/
            - build.gradle
            - openapi.properties
          📂 worker/
            - build.gradle
        📂 kokoro-onnx/
          - .python-version
          - LICENSE
          - pyproject.toml
          - uv.lock
          📂 .github/
            - FUNDING.yml
            - PULL_REQUEST_TEMPLATE.md
          📂 .vscode/
            - extensions.json
            - settings.json
          📂 examples/
            - app.py
            - chinese.py
            - english.py
            - french.py
            - hindi.py
            - italian.py
            - japanese.py
            - play.py
            - podcast.py
            - portuguese.py
            - save.py
            - spanish.py
            - with_blending.py
            - with_cuda.py
            - with_espeak_data.py
            - with_espeak_lib.py
            - with_log.py
            - with_phonemes.py
            - with_provider.py
            - with_quant.py
            - with_session.py
            - with_stream.py
            - with_stream_save.py
            - with_voice.py
          📂 models/
            - kokoro-v1.0.onnx
            - voices-v1.0.bin
          📂 scripts/
            - export.py
            - fetch_voices.py
          📂 src/
        📂 langgraph/
          - LICENSE
          - Makefile
          📂 .github/
            - CONTRIBUTING.md
            - PULL_REQUEST_TEMPLATE.md
            - dependabot.yml
          📂 examples/
            - react-agent-from-scratch.ipynb
            - react-agent-structured-output.ipynb
            - run-id-langsmith.ipynb
            - subgraph.ipynb
            - tool-calling.ipynb
          📂 libs/
        📂 leon/
          - .changelogrc
          - .editorconfig
          - .env.sample
          - .eslintrc.json
          - .gitpod.yml
          - .lintstagedrc
          - .npmrc
          - .nvmrc
          - .prettierrc.json
          - eslint.config.mjs
          - jsconfig.json
          - nodemon.json
          - package.json
          - ruff.toml
          - tsconfig.json
          📂 .github/
            - CODE_OF_CONDUCT.md
            - CONTRIBUTING.md
            - FUNDING.yml
            - PULL_REQUEST_TEMPLATE.md
          📂 .husky/
            - commit-msg
            - pre-commit
          📂 app/
            - vite.config.js
          📂 bin/
          📂 bridges/
          📂 core/
            - langs.json
            - skills-endpoints.json
          📂 hotword/
            - index.js
            - package.json
          📂 scripts/
            - build-binaries.js
            - check-os.js
            - check.js
            - clean-test-dbs.js
            - commit-msg.js
            - lint.js
            - run-clean-test-dbs.js
            - skill-package.js
            - test-module.js
          📂 server/
          📂 skills/
            - tsconfig.json
          📂 tcp_server/
            - settings.json
          📂 test/
            - paths.setup.js
        📂 lightning/
          - .codecov.yml
          - .git-blame-ignore-revs
          - .gitmodules
          - .pre-commit-config.yaml
          - .readthedocs.yml
          - CITATION.cff
          - LICENSE
          - Makefile
          - pyproject.toml
          - setup.py
          📂 .actions/
            - assistant.py
            - pull_legacy_checkpoints.sh
            - requirements.txt
          📂 .github/
            - BECOMING_A_CORE_CONTRIBUTOR.md
            - CODEOWNERS
            - CODE_OF_CONDUCT.md
            - CONTRIBUTING.md
            - PULL_REQUEST_TEMPLATE.md
            - advanced-issue-labeler.yml
            - checkgroup.yml
            - dependabot.yml
            - label-change.yml
            - lightning-probot.yml
            - markdown-links-config.json
            - stale.yml
          📂 .lightning/
          📂 _notebooks/
          📂 docs/
            - crossroad.html
            - generate_docs_for_tags.sh
            - redirect.html
            - rtfd-build.sh
          📂 examples/
            - run_fabric_examples.sh
            - run_pl_examples.sh
          📂 requirements/
            - collect_env_details.py
          📂 src/
            - version.info
          📂 tests/
        📂 litellm/
          - .dockerignore
          - .env.example
          - .flake8
          - .git-blame-ignore-revs
          - .gitattributes
          - .pre-commit-config.yaml
          - Dockerfile
          - LICENSE
          - Makefile
          - codecov.yaml
          - docker-compose.yml
          - index.yaml
          - mcp_servers.json
          - model_prices_and_context_window.json
          - package.json
          - poetry.lock
          - prometheus.yml
          - proxy_server_config.yaml
          - pyproject.toml
          - pyrightconfig.json
          - render.yaml
          - ruff.toml
          - schema.prisma
          - test_bulk_update_all_users.py
          📂 .circleci/
            - config.yml
            - requirements.txt
          📂 .devcontainer/
            - devcontainer.json
          📂 .github/
            - FUNDING.yml
            - dependabot.yaml
            - deploy-to-aws.png
            - pull_request_template.md
            - template.yaml
          📂 ci_cd/
            - baseline_db.py
            - check_file_length.py
            - check_files_match.py
            - publish-proxy-extras.sh
            - run_migration.py
          📂 cookbook/
            - Benchmarking_LLMs_by_use_case.ipynb
            - Claude_(Anthropic)_with_Streaming_liteLLM_Examples.ipynb
            - Evaluating_LLMs.ipynb
            - LiteLLM_Azure_and_OpenAI_example.ipynb
            - LiteLLM_Bedrock.ipynb
            - LiteLLM_Comparing_LLMs.ipynb
            - LiteLLM_Completion_Cost.ipynb
            - LiteLLM_HuggingFace.ipynb
            - LiteLLM_NovitaAI_Cookbook.ipynb
            - LiteLLM_OpenRouter.ipynb
            - LiteLLM_Petals.ipynb
            - LiteLLM_PromptLayer.ipynb
            - LiteLLM_User_Based_Rate_Limits.ipynb
            - LiteLLM_batch_completion.ipynb
            - Migrating_to_LiteLLM_Proxy_from_OpenAI_Azure_OpenAI.ipynb
            - Parallel_function_calling.ipynb
            - Proxy_Batch_Users.ipynb
            - TogetherAI_liteLLM.ipynb
            - Using_Nemo_Guardrails_with_LiteLLM_Server.ipynb
            - VLLM_Model_Testing.ipynb
            - google_adk_litellm_tutorial.ipynb
            - liteLLM_A121_Jurrasic_example.ipynb
            - liteLLM_Baseten.ipynb
            - liteLLM_Getting_Started.ipynb
            - liteLLM_IBM_Watsonx.ipynb
            - liteLLM_Langchain_Demo.ipynb
            - liteLLM_Ollama.ipynb
            - liteLLM_Replicate_Demo.ipynb
            - liteLLM_Streaming_Demo.ipynb
            - liteLLM_VertextAI_Example.ipynb
            - liteLLM_clarifai_Demo.ipynb
            - liteLLM_function_calling.ipynb
            - litellm_Test_Multiple_Providers.ipynb
            - litellm_model_fallback.ipynb
            - litellm_test_multiple_llm_demo.ipynb
            - mlflow_langchain_tracing_litellm_proxy.ipynb
            - result.html
          📂 db_scripts/
            - create_views.py
            - migrate_keys.py
            - update_unassigned_teams.py
          📂 deploy/
            - Dockerfile.ghcr_base
          📂 docker/
            - .env.example
            - Dockerfile.alpine
            - Dockerfile.custom_ui
            - Dockerfile.database
            - Dockerfile.dev
            - Dockerfile.non_root
            - build_admin_ui.sh
            - entrypoint.sh
            - prod_entrypoint.sh
            - supervisord.conf
          📂 docs/
          📂 enterprise/
            - __init__.py
            - poetry.lock
            - pyproject.toml
          📂 litellm/
            - __init__.py
            - _logging.py
            - _redis.py
            - _service_logger.py
            - _version.py
            - budget_manager.py
            - constants.py
            - cost.json
            - cost_calculator.py
            - exceptions.py
            - main.py
            - model_prices_and_context_window_backup.json
            - mypy.ini
            - py.typed
            - router.py
            - scheduler.py
            - timeout.py
            - utils.py
          📂 litellm-js/
          📂 litellm-proxy-extras/
            - LICENSE
            - poetry.lock
            - pyproject.toml
          📂 tests/
            - README.MD
            - __init__.py
            - gettysburg.wav
            - large_text.py
            - openai_batch_completions.jsonl
            - test_budget_management.py
            - test_callbacks_on_proxy.py
            - test_config.py
            - test_debug_warning.py
            - test_end_users.py
            - test_entrypoint.py
            - test_fallbacks.py
            - test_health.py
            - test_keys.py
            - test_logging.conf
            - test_models.py
            - test_openai_endpoints.py
            - test_organizations.py
            - test_passthrough_endpoints.py
            - test_ratelimit.py
            - test_resource_cleanup.py
            - test_spend_logs.py
            - test_team.py
            - test_team_logging.py
            - test_team_members.py
            - test_users.py
          📂 ui/
        📂 opencode_swarm/
          - .gitattributes
          - bun.lock
          - package.json
          - turbo.json
          📂 .changeset/
            - README.md
            - config.json
            - dex-inspired-improvements.md
          📂 .claude-plugin/
            - marketplace.json
          📂 .github/
          📂 .hive/
            - .local_version
            - README.md
            - config.yaml
            - issues.jsonl
            - memories.jsonl
            - metadata.json
          📂 .opencode/
          📂 .turbo/
          📂 apps/
          📂 docs/
          📂 packages/
          📂 research/
          📂 scripts/
            - bump-version.sh
        📂 outspeed/
          - poetry.lock
          - pyproject.toml
          - ruff.toml
          📂 .circleci/
            - config.yml
          📂 .github/
            - outspeed_dark.jpg
            - outspeed_light.jpg
          📂 examples/
            - replay.py
          📂 outspeed/
            - __init__.py
            - __main__.py
            - _realtime_function.py
            - app.py
            - cli.py
            - data.py
            - nodes.py
            - server.py
            - streams.py
            - tool.py
          📂 tests/
        📂 pastemax/
          - .eslintrc.cjs
          - Dockerfile
          - LICENSE
          - build.js
          - dev.js
          - docker-compose.yml
          - excluded-files.js
          - index.html
          - main.js
          - package.json
          - preload.js
          - renderer.js
          - tsconfig.json
          - tsconfig.node.json
          - vite.config.ts
          📂 .github/
            - README.actions.md
          📂 .repomix/
            - bundles.json
          📂 docs/
          📂 public/
            - favicon.icns
            - favicon.ico
            - favicon.png
            - favicon.svg
          📂 scripts/
            - fix-dependencies.js
            - notarize.js
            - test-local-build.js
            - verify-build.js
          📂 src/
            - App.tsx
            - declarations.d.ts
            - index.html
            - main.tsx
            - react-app-env.d.ts
        📂 pathway/
          - .coveragerc
          - .dockerignore
          - Cargo.lock
          - Cargo.toml
          - build.rs
          - clippy.toml
          - pyproject.toml
          - rust-toolchain.toml
          📂 .github/
            - pull_request_template.md
          📂 docs/
          📂 examples/
            - LICENSE
            - Pathway-PyData_Global_2022.pdf
          📂 external/
          📂 integration_tests/
            - __init__.py
            - conftest.py
          📂 library_licenses/
            - abomonation-LICENSE-MIT
            - adler2-LICENSE-0BSD
            - adler2-LICENSE-APACHE
            - adler2-LICENSE-MIT
            - adler32-LICENSE-ZLIB
            - ahash-LICENSE-APACHE
            - ahash-LICENSE-MIT
            - aho-corasick-LICENSE-MIT
            - airbyte_serverless-LICENSE-MIT
            - alloc-no-stdlib-LICENSE-BSD
            - alloc-stdlib-LICENSE-BSD
            - allocator-api2-LICENSE-APACHE
            - allocator-api2-LICENSE-MIT
            - anyhow-LICENSE-APACHE
            - anyhow-LICENSE-MIT
            - apache-avro-LICENSE-APACHE
            - arc-swap-LICENSE-APACHE
            - arc-swap-LICENSE-MIT
            - arcstr-LICENSE-APACHE
            - arcstr-LICENSE-MIT
            - arcstr-LICENSE-ZLIB
            - array-init-LICENSE-APACHE
            - array-init-LICENSE-MIT
            - arrayref-LICENSE-BSD
            - arrayvec-LICENSE-APACHE
            - arrayvec-LICENSE-MIT
            - arrow-LICENSE-APACHE
            - arrow-arith-LICENSE-APACHE
            - arrow-array-LICENSE-APACHE
            - arrow-buffer-LICENSE-APACHE
            - arrow-cast-LICENSE-APACHE
            - arrow-csv-LICENSE-APACHE
            - arrow-data-LICENSE-APACHE
            - arrow-ipc-LICENSE-APACHE
            - arrow-json-LICENSE-APACHE
            - arrow-ord-LICENSE-APACHE
            - arrow-row-LICENSE-APACHE
            - arrow-schema-LICENSE-APACHE
            - arrow-select-LICENSE-APACHE
            - arrow-string-LICENSE-APACHE
            - assert_matches-LICENSE-APACHE
            - assert_matches-LICENSE-MIT
            - async-compression-LICENSE-APACHE
            - async-compression-LICENSE-MIT
            - async-lock-LICENSE-APACHE
            - async-lock-LICENSE-MIT
            - async-nats-LICENSE-APACHE
            - async-stream-LICENSE-MIT
            - async-stream-impl-LICENSE-MIT
            - async-trait-LICENSE-APACHE
            - async-trait-LICENSE-MIT
            - atoi-LICENSE-MIT
            - atomic-waker-LICENSE-APACHE
            - atomic-waker-LICENSE-MIT
            - attohttpc-LICENSE
            - autocfg-LICENSE-APACHE
            - autocfg-LICENSE-MIT
            - aws-config-LICENSE-APACHE
            - aws-credential-types-LICENSE-APACHE
            - aws-creds-LICENSE-MIT
            - aws-region-LICENSE-MIT
            - aws-runtime-LICENSE-APACHE
            - aws-sdk-dynamodb-LICENSE-APACHE
            - aws-sdk-sso-LICENSE-APACHE
            - aws-sdk-ssooidc-LICENSE-APACHE
            - aws-sdk-sts-LICENSE-APACHE
            - aws-sigv4-LICENSE-APACHE
            - aws-smithy-async-LICENSE-APACHE
            - aws-smithy-http-LICENSE-APACHE
            - aws-smithy-json-LICENSE-APACHE
            - aws-smithy-query-LICENSE-APACHE
            - aws-smithy-runtime-LICENSE-APACHE
            - aws-smithy-runtime-api-LICENSE-APACHE
            - aws-smithy-types-LICENSE-APACHE
            - aws-smithy-xml-LICENSE-APACHE
            - aws-types-LICENSE-APACHE
            - axum-LICENSE-MIT
            - backon-LICENSE-APACHE
            - base32-LICENSE-APACHE
            - base32-LICENSE-MIT
            - base64-LICENSE-APACHE
            - base64-LICENSE-MIT
            - base64-simd-LICENSE-MIT
            - base64ct-LICENSE-APACHE
            - base64ct-LICENSE-MIT
            - bigdecimal-LICENSE-APACHE
            - bigdecimal-LICENSE-MIT
            - bimap-rs-LICENSE-MIT
            - bincode-LICENSE-MIT
            - bitflags-LICENSE-APACHE
            - bitflags-LICENSE-MIT
            - bitpacking-LICENSE-MIT
            - bitvec-LICENSE-MIT
            - blake3-LICENSE-APACHE
            - borsh-LICENSE-APACHE
            - borsh-LICENSE-MIT
            - borsh-derive-LICENSE-APACHE
            - brotli-decompressor-LICENSE-BSD
            - brotli-decompressor-LICENSE-MIT
            - bson-LICENSE-MIT
            - bytecheck-LICENSE-MIT
            - bytecheck_derive-LICENSE-MIT
            - bytemuck-LICENSE-APACHE
            - bytemuck-LICENSE-MIT
            - bytemuck-LICENSE-ZLIB
            - byteorder-LICENSE-MIT
            - bytes-LICENSE-MIT
            - bytes-utils-LICENSE-APACHE
            - bytes-utils-LICENSE-MIT
            - bzip2-LICENSE-APACHE
            - bzip2-LICENSE-MIT
            - bzip2-sys-LICENSE-APACHE
            - bzip2-sys-LICENSE-MIT
            - cached-LICENSE-MIT
            - cached_proc_macro-LICENSE-MIT
            - cached_proc_macro_types-LICENSE-MIT
            - cc-LICENSE-APACHE
            - cc-LICENSE-MIT
            - census-LICENSE-MIT
            - cfg-if-LICENSE-APACHE
            - cfg-if-LICENSE-MIT
            - cfg_aliases-LICENSE-MIT
            - chrono-LICENSE-APACHE
            - chrono-LICENSE-MIT
            - chrono-tz-LICENSE-APACHE
            - chrono-tz-LICENSE-MIT
            - chrono-tz-build-LICENSE-APACHE
            - chrono-tz-build-LICENSE-MIT
            - cmake-LICENSE-APACHE
            - cmake-LICENSE-MIT
            - codespan-reporting-LICENSE-APACHE
            - comfy-table-LICENSE-MIT
            - concurrent-queue-LICENSE-APACHE
            - concurrent-queue-LICENSE-MIT
            - const-oid-LICENSE-APACHE
            - const-oid-LICENSE-MIT
            - const-random-LICENSE-APACHE
            - const-random-LICENSE-MIT
            - const-random-macro-LICENSE-APACHE
            - const-random-macro-LICENSE-MIT
            - constant_time_eq-LICENSE-APACHE
            - constant_time_eq-LICENSE-MIT0
            - convert_case-LICENSE-MIT
            - core2-LICENSE-APACHE
            - core2-LICENSE-MIT
            - crc32fast-LICENSE-APACHE
            - crc32fast-LICENSE-MIT
            - crossbeam-channel-LICENSE-APACHE
            - crossbeam-channel-LICENSE-MIT
            - crossbeam-deque-LICENSE-APACHE
            - crossbeam-deque-LICENSE-MIT
            - crossbeam-epoch-LICENSE-APACHE
            - crossbeam-epoch-LICENSE-MIT
            - crossbeam-utils-LICENSE-APACHE
            - crossbeam-utils-LICENSE-MIT
            - csv-LICENSE-MIT
            - csv-core-LICENSE-MIT
            - curve25519-dalek-derive-LICENSE-APACHE
            - curve25519-dalek-derive-LICENSE-MIT
            - cxx-LICENSE-APACHE
            - cxx-LICENSE-MIT
            - cxx-build-LICENSE-APACHE
            - cxx-build-LICENSE-MIT
            - cxxbridge-flags-LICENSE-APACHE
            - cxxbridge-flags-LICENSE-MIT
            - cxxbridge-macro-LICENSE-APACHE
            - cxxbridge-macro-LICENSE-MIT
            - darling-LICENSE-MIT
            - darling_core-LICENSE-MIT
            - darling_macro-LICENSE-MIT
            - dary_heap-LICENSE-APACHE
            - dary_heap-LICENSE-MIT
            - dashmap-LICENSE-MIT
            - data-encoding-LICENSE-MIT
            - datafusion-LICENSE-APACHE
            - datafusion-catalog-LICENSE-APACHE
            - datafusion-common-LICENSE-APACHE
            - datafusion-common-runtime-LICENSE-APACHE
            - datafusion-doc-LICENSE-APACHE
            - datafusion-execution-LICENSE-APACHE
            - datafusion-expr-LICENSE-APACHE
            - datafusion-expr-common-LICENSE-APACHE
            - datafusion-functions-LICENSE-APACHE
            - datafusion-functions-aggregate-LICENSE-APACHE
            - datafusion-functions-aggregate-common-LICENSE-APACHE
            - datafusion-functions-nested-LICENSE-APACHE
            - datafusion-functions-table-LICENSE-APACHE
            - datafusion-functions-window-LICENSE-APACHE
            - datafusion-functions-window-common-LICENSE-APACHE
            - datafusion-macros-LICENSE-APACHE
            - datafusion-optimizer-LICENSE-APACHE
            - datafusion-physical-expr-LICENSE-APACHE
            - datafusion-physical-expr-common-LICENSE-APACHE
            - datafusion-physical-optimizer-LICENSE-APACHE
            - datafusion-physical-plan-LICENSE-APACHE
            - datafusion-proto-LICENSE-APACHE
            - datafusion-proto-common-LICENSE-APACHE
            - datafusion-sql-LICENSE-APACHE
            - delta_kernel-LICENSE-APACHE
            - delta_kernel_derive-LICENSE-APACHE
            - deltalake-LICENSE-APACHE
            - deltalake-aws-LICENSE-APACHE
            - deltalake-core-LICENSE-APACHE
            - der-LICENSE-APACHE
            - der-LICENSE-MIT
            - deranged-LICENSE-APACHE
            - deranged-LICENSE-MIT
            - derivative-LICENSE-APACHE
            - derivative-LICENSE-MIT
            - derive-syn-parse-LICENSE-APACHE
            - derive-syn-parse-LICENSE-MIT
            - derive-where-LICENSE-APACHE
            - derive-where-LICENSE-MIT
            - derive_builder-LICENSE-APACHE
            - derive_builder-LICENSE-MIT
            - derive_builder_core-LICENSE-APACHE
            - derive_builder_core-LICENSE-MIT
            - derive_builder_macro-LICENSE-APACHE
            - derive_builder_macro-LICENSE-MIT
            - derive_more-LICENSE-MIT
            - deunicode-LICENSE-BSD
            - differential-dataflow-LICENSE-MIT
            - displaydoc-LICENSE-APACHE
            - displaydoc-LICENSE-MIT
            - dlv-list-LICENSE-APACHE
            - dlv-list-LICENSE-MIT
            - downcast-LICENSE-MIT
            - downcast-rs-LICENSE-APACHE
            - downcast-rs-LICENSE-MIT
            - dtoa-LICENSE-APACHE
            - dtoa-LICENSE-MIT
            - dyn-clone-LICENSE-APACHE
            - dyn-clone-LICENSE-MIT
            - ed25519-LICENSE-APACHE
            - ed25519-LICENSE-MIT
            - either-LICENSE-APACHE
            - either-LICENSE-MIT
            - elasticsearch-LICENSE-APACHE
            - encoding_rs-LICENSE-APACHE
            - encoding_rs-LICENSE-MIT
            - encoding_rs-LICENSE-WHATWG
            - enum-as-inner-LICENSE-APACHE
            - enum-as-inner-LICENSE-MIT
            - equivalent-LICENSE-APACHE
            - equivalent-LICENSE-MIT
            - errno-LICENSE-APACHE
            - errno-LICENSE-MIT
            - event-listener-LICENSE-APACHE
            - event-listener-LICENSE-MIT
            - event-listener-strategy-LICENSE-APACHE
            - event-listener-strategy-LICENSE-MIT
            - eyre-LICENSE-APACHE
            - eyre-LICENSE-MIT
            - fallible-iterator-LICENSE-APACHE
            - fallible-iterator-LICENSE-MIT
            - fallible-streaming-iterator-LICENSE-APACHE
            - fallible-streaming-iterator-LICENSE-MIT
            - fastdivide-LICENSE-MIT
            - fastdivide-LICENSE-ZLIB
            - fastrand-LICENSE-APACHE
            - fastrand-LICENSE-MIT
            - fix-hidden-lifetime-bug-LICENSE-APACHE
            - fix-hidden-lifetime-bug-LICENSE-MIT
            - fix-hidden-lifetime-bug-LICENSE-ZLIB
            - fix-hidden-lifetime-bug-proc_macros-LICENSE-APACHE
            - fix-hidden-lifetime-bug-proc_macros-LICENSE-MIT
            - fix-hidden-lifetime-bug-proc_macros-LICENSE-ZLIB
            - fixedbitset-LICENSE-APACHE
            - fixedbitset-LICENSE-MIT
            - flagset-LICENSE-APACHE
            - flatbuffers-LICENSE-APACHE
            - flate2-LICENSE-APACHE
            - flate2-LICENSE-MIT
            - fnv-LICENSE-APACHE
            - fnv-LICENSE-MIT
            - foldhash-LICENSE-ZLIB
            - foreign-types-LICENSE-APACHE
            - foreign-types-LICENSE-MIT
            - foreign-types-shared-LICENSE-APACHE
            - foreign-types-shared-LICENSE-MIT
            - form_urlencoded-LICENSE-APACHE
            - form_urlencoded-LICENSE-MIT
            - fragile-LICENSE-APACHE
            - fs4-LICENSE-APACHE
            - fs4-LICENSE-MIT
            - funty-LICENSE-MIT
            - futures-LICENSE-APACHE
            - futures-LICENSE-MIT
            - futures-channel-LICENSE-APACHE
            - futures-channel-LICENSE-MIT
            - futures-core-LICENSE-APACHE
            - futures-core-LICENSE-MIT
            - futures-executor-LICENSE-APACHE
            - futures-executor-LICENSE-MIT
            - futures-io-LICENSE-APACHE
            - futures-io-LICENSE-MIT
            - futures-macro-LICENSE-APACHE
            - futures-macro-LICENSE-MIT
            - futures-sink-LICENSE-APACHE
            - futures-sink-LICENSE-MIT
            - futures-task-LICENSE-APACHE
            - futures-task-LICENSE-MIT
            - futures-util-LICENSE-APACHE
            - futures-util-LICENSE-MIT
            - generic-array-LICENSE-MIT
            - getopts-LICENSE-APACHE
            - getopts-LICENSE-MIT
            - getrandom-LICENSE-APACHE
            - getrandom-LICENSE-MIT
            - glob-LICENSE-APACHE
            - glob-LICENSE-MIT
            - h2-LICENSE-MIT
            - half-LICENSE-APACHE
            - half-LICENSE-MIT
            - hashbrown-LICENSE-APACHE
            - hashbrown-LICENSE-MIT
            - hashlink-LICENSE-APACHE
            - hashlink-LICENSE-MIT
            - heck-LICENSE-APACHE
            - heck-LICENSE-MIT
            - hex-LICENSE-APACHE
            - hex-LICENSE-MIT
            - hickory-proto-LICENSE-APACHE
            - hickory-proto-LICENSE-MIT
            - hickory-resolver-LICENSE-APACHE
            - hickory-resolver-LICENSE-MIT
            - home-LICENSE-APACHE
            - home-LICENSE-MIT
            - hostname-LICENSE-MIT
            - http-LICENSE-APACHE
            - http-LICENSE-MIT
            - http-body-LICENSE-MIT
            - http-body-util-LICENSE-MIT
            - httparse-LICENSE-APACHE
            - httparse-LICENSE-MIT
            - httpdate-LICENSE-APACHE
            - httpdate-LICENSE-MIT
            - humantime-LICENSE-APACHE
            - humantime-LICENSE-MIT
            - hyper-LICENSE-MIT
            - hyper-rustls-LICENSE-APACHE
            - hyper-rustls-LICENSE-ISC
            - hyper-rustls-LICENSE-MIT
            - hyper-timeout-LICENSE-APACHE
            - hyper-timeout-LICENSE-MIT
            - hyper-tls-LICENSE-APACHE
            - hyper-tls-LICENSE-MIT
            - hyper-util-LICENSE-MIT
            - iana-time-zone-LICENSE-APACHE
            - iana-time-zone-LICENSE-MIT
            - iceberg-LICENSE-APACHE
            - iceberg-catalog-rest-LICENSE-APACHE
            - icu-LICENSE-UNICODE
            - id-arena-LICENSE-APACHE
            - id-arena-LICENSE-MIT
            - ident_case-LICENSE-APACHE
            - ident_case-LICENSE-MIT
            - idna-LICENSE-APACHE
            - idna-LICENSE-MIT
            - idna_adapter-LICENSE-APACHE
            - idna_adapter-LICENSE-MIT
            - indenter-LICENSE-APACHE
            - indenter-LICENSE-MIT
            - indexmap-LICENSE-APACHE
            - indexmap-LICENSE-MIT
            - indoc-LICENSE-APACHE
            - indoc-LICENSE-MIT
            - instant-LICENSE-BSD
            - integer-encoding-LICENSE-MIT
            - inventory-LICENSE-APACHE
            - inventory-LICENSE-MIT
            - ipnet-LICENSE-APACHE
            - ipnet-LICENSE-MIT
            - itertools-LICENSE-APACHE
            - itertools-LICENSE-MIT
            - itoa-LICENSE-APACHE
            - itoa-LICENSE-MIT
            - jemalloc-sys-LICENSE-APACHE
            - jemalloc-sys-LICENSE-MIT
            - jemallocator-LICENSE-APACHE
            - jemallocator-LICENSE-MIT
            - jmespath-LICENSE-MIT
            - jobserver-LICENSE-APACHE
            - jobserver-LICENSE-MIT
            - lazy_static-LICENSE-APACHE
            - lazy_static-LICENSE-MIT
            - levenshtein_automata-LICENSE-MIT
            - lexical-core-LICENSE-APACHE
            - lexical-core-LICENSE-MIT
            - lexical-parse-float-LICENSE-APACHE
            - lexical-parse-float-LICENSE-MIT
            - lexical-parse-integer-LICENSE-APACHE
            - lexical-parse-integer-LICENSE-MIT
            - lexical-util-LICENSE-APACHE
            - lexical-util-LICENSE-MIT
            - lexical-write-float-LICENSE-APACHE
            - lexical-write-float-LICENSE-MIT
            - lexical-write-integer-LICENSE-APACHE
            - lexical-write-integer-LICENSE-MIT
            - libc-LICENSE-APACHE
            - libc-LICENSE-MIT
            - libflate-LICENSE-MIT
            - libflate_lz77-LICENSE-MIT
            - libm-LICENSE
            - libm-LICENSE-APACHE
            - libsqlite3-sys-LICENSE-MIT
            - libz-sys-LICENSE-APACHE
            - libz-sys-LICENSE-MIT
            - link-cplusplus-LICENSE-APACHE
            - link-cplusplus-LICENSE-MIT
            - linked-hash-map-LICENSE-APACHE
            - linked-hash-map-LICENSE-MIT
            - linux-raw-sys-LICENSE-APACHE
            - linux-raw-sys-LICENSE-MIT
            - lock_api-LICENSE-APACHE
            - lock_api-LICENSE-MIT
            - log-LICENSE-APACHE
            - log-LICENSE-MIT
            - lru-LICENSE-MIT
            - lru-cache-LICENSE-APACHE
            - lru-cache-LICENSE-MIT
            - lz4_flex-LICENSE-MIT
            - lzma-sys-LICENSE-APACHE
            - lzma-sys-LICENSE-MIT
            - macro_magic-LICENSE-MIT
            - macro_magic_core-LICENSE-MIT
            - macro_magic_core_macros-LICENSE-MIT
            - macro_magic_macros-LICENSE-MIT
            - maplit-LICENSE-APACHE
            - maplit-LICENSE-MIT
            - match_cfg-LICENSE-APACHE
            - match_cfg-LICENSE-MIT
            - matchit-LICENSE-MIT
            - matrixmultiply-LICENSE-APACHE
            - matrixmultiply-LICENSE-MIT
            - maybe-async-LICENSE-MIT
            - md5-LICENSE-APACHE
            - md5-LICENSE-MIT
            - measure_time-LICENSE-MIT
            - memchr-LICENSE-MIT
            - memmap2-LICENSE-APACHE
            - memmap2-LICENSE-MIT
            - memoffset-LICENSE-MIT
            - mime-LICENSE-APACHE
            - mime-LICENSE-MIT
            - minimal-lexical-LICENSE-APACHE
            - minimal-lexical-LICENSE-MIT
            - miniz_oxide-LICENSE-APACHE
            - miniz_oxide-LICENSE-MIT
            - miniz_oxide-LICENSE-ZLIB
            - mio-LICENSE-MIT
            - mockall-LICENSE-APACHE
            - mockall-LICENSE-MIT
            - mockall_derive-LICENSE-APACHE
            - mockall_derive-LICENSE-MIT
            - moka-LICENSE-APACHE
            - moka-LICENSE-MIT
            - mongodb-LICENSE-APACHE
            - murmur3-LICENSE-APACHE
            - murmur3-LICENSE-MIT
            - murmurhash32-LICENSE-MIT
            - native-tls-LICENSE-APACHE
            - native-tls-LICENSE-MIT
            - ndarray-LICENSE-APACHE
            - ndarray-LICENSE-MIT
            - nix-LICENSE-MIT
            - nkeys-LICENSE-APACHE
            - nom-LICENSE-MIT
            - nuid-LICENSE-APACHE
            - num-LICENSE-APACHE
            - num-LICENSE-MIT
            - num-bigint-LICENSE-APACHE
            - num-bigint-LICENSE-MIT
            - num-complex-LICENSE-APACHE
            - num-complex-LICENSE-MIT
            - num-conv-LICENSE-APACHE
            - num-conv-LICENSE-MIT
            - num-integer-LICENSE-APACHE
            - num-integer-LICENSE-MIT
            - num-iter-LICENSE-APACHE
            - num-iter-LICENSE-MIT
            - num-rational-LICENSE-APACHE
            - num-rational-LICENSE-MIT
            - num-traits-LICENSE-APACHE
            - num-traits-LICENSE-MIT
            - num_cpus-LICENSE-APACHE
            - num_cpus-LICENSE-MIT
            - num_enum-LICENSE-APACHE
            - num_enum-LICENSE-BSD
            - num_enum-LICENSE-MIT
            - num_enum_derive-LICENSE-APACHE
            - num_enum_derive-LICENSE-BSD
            - num_enum_derive-LICENSE-MIT
            - numpy-LICENSE-BSD
            - object-store-LICENSE-APACHE
            - once_cell-LICENSE-APACHE
            - once_cell-LICENSE-MIT
            - oneshot-LICENSE-APACHE
            - oneshot-LICENSE-MIT
            - opendal-LICENSE-APACHE
            - openssl-probe-LICENSE-APACHE
            - openssl-probe-LICENSE-MIT
            - openssl-src-LICENSE-APACHE
            - openssl-src-LICENSE-MIT
            - opentelemetry-LICENSE-APACHE
            - opentelemetry-otlp-LICENSE-APACHE
            - opentelemetry-proto-LICENSE-APACHE
            - opentelemetry-semantic-conventions-LICENSE-APACHE
            - opentelemetry_sdk-LICENSE-APACHE
            - ordered-float-LICENSE-MIT
            - ordered-multimap-LICENSE-MIT
            - outref-LICENSE-MIT
            - ownedbytes-LICENSE-MIT
            - parking-LICENSE-APACHE
            - parking-LICENSE-MIT
            - parking_lot-LICENSE-APACHE
            - parking_lot-LICENSE-MIT
            - parking_lot_core-LICENSE-APACHE
            - parking_lot_core-LICENSE-MIT
            - parquet-LICENSE-APACHE
            - parse-zoneinfo-LICENSE-MIT
            - paste-LICENSE-APACHE
            - paste-LICENSE-MIT
            - pbkdf2-LICENSE-APACHE
            - pbkdf2-LICENSE-MIT
            - pem-rfc7468-LICENSE-APACHE
            - pem-rfc7468-LICENSE-MIT
            - percent-encoding-LICENSE-APACHE
            - percent-encoding-LICENSE-MIT
            - petgraph-LICENSE-APACHE
            - petgraph-LICENSE-MIT
            - phf-LICENSE-MIT
            - phf_codegen-LICENSE-MIT
            - phf_generator-LICENSE-MIT
            - phf_shared-LICENSE-MIT
            - pin-project-LICENSE-APACHE
            - pin-project-LICENSE-MIT
            - pin-project-internal-LICENSE-APACHE
            - pin-project-internal-LICENSE-MIT
            - pin-project-lite-LICENSE-APACHE
            - pin-project-lite-LICENSE-MIT
            - pin-utils-LICENSE-APACHE
            - pin-utils-LICENSE-MIT
            - pkcs8-LICENSE-APACHE
            - pkcs8-LICENSE-MIT
            - pkg-config-LICENSE-APACHE
            - pkg-config-LICENSE-MIT
            - portable-atomic-LICENSE-APACHE
            - portable-atomic-LICENSE-MIT
            - postgres-LICENSE-APACHE
            - postgres-LICENSE-MIT
            - postgres-protocol-LICENSE-APACHE
            - postgres-protocol-LICENSE-MIT
            - postgres-types-LICENSE-APACHE
            - postgres-types-LICENSE-MIT
            - powerfmt-LICENSE-APACHE
            - powerfmt-LICENSE-MIT
            - ppv-lite86-LICENSE-APACHE
            - ppv-lite86-LICENSE-MIT
            - predicates-LICENSE-APACHE
            - predicates-LICENSE-MIT
            - predicates-core-LICENSE-APACHE
            - predicates-core-LICENSE-MIT
            - predicates-tree-LICENSE-APACHE
            - predicates-tree-LICENSE-MIT
            - proc-macro-crate-LICENSE-APACHE
            - proc-macro-crate-LICENSE-MIT
            - proc-macro2-LICENSE-APACHE
            - proc-macro2-LICENSE-MIT
            - prometheus-client-LICENSE-APACHE
            - prometheus-client-LICENSE-MIT
            - prometheus-client-derive-encode-LICENSE-APACHE
            - prometheus-client-derive-encode-LICENSE-MIT
            - prost-LICENSE-APACHE
            - prost-derive-LICENSE-APACHE
            - psm-LICENSE-APACHE
            - psm-LICENSE-MIT
            - ptr_meta-LICENSE-MIT
            - ptr_meta_derive-LICENSE-MIT
            - pyo3-LICENSE-APACHE
            - pyo3-LICENSE-MIT
            - pyo3-asyncio-0-21-LICENSE-APACHE
            - pyo3-build-config-LICENSE-APACHE
            - pyo3-build-config-LICENSE-MIT
            - pyo3-ffi-LICENSE-APACHE
            - pyo3-ffi-LICENSE-MIT
            - pyo3-log-LICENSE-APACHE
            - pyo3-log-LICENSE-MIT
            - pyo3-macros-LICENSE-APACHE
            - pyo3-macros-LICENSE-MIT
            - pyo3-macros-backend-LICENSE-APACHE
            - pyo3-macros-backend-LICENSE-MIT
            - quick-xml-LICENSE-MIT
            - quinn-LICENSE-APACHE
            - quinn-LICENSE-MIT
            - quinn-proto-LICENSE-APACHE
            - quinn-proto-LICENSE-MIT
            - quinn-udp-LICENSE-APACHE
            - quinn-udp-LICENSE-MIT
            - quote-LICENSE-APACHE
            - quote-LICENSE-MIT
            - radium-LICENSE-MIT
            - rand-LICENSE-APACHE
            - rand-LICENSE-MIT
            - rand_chacha-LICENSE-APACHE
            - rand_chacha-LICENSE-MIT
            - rand_core-LICENSE-APACHE
            - rand_core-LICENSE-MIT
            - rand_distr-LICENSE-APACHE
            - rand_distr-LICENSE-MIT
            - rawpointer-LICENSE-APACHE
            - rawpointer-LICENSE-MIT
            - rayon-LICENSE-APACHE
            - rayon-LICENSE-MIT
            - rayon-core-LICENSE-APACHE
            - rayon-core-LICENSE-MIT
            - rdkafka-LICENSE-MIT
            - rdkafka-sys-LICENSE-MIT
            - recursive-LICENSE-MIT
            - recursive-proc-macro-impl-LICENSE-MIT
            - regex-LICENSE-APACHE
            - regex-LICENSE-MIT
            - regex-automata-LICENSE-APACHE
            - regex-automata-LICENSE-MIT
            - regex-lite-LICENSE-APACHE
            - regex-lite-LICENSE-MIT
            - regex-syntax-LICENSE-APACHE
            - regex-syntax-LICENSE-MIT
            - rend-LICENSE-MIT
            - reqsign-LICENSE-APACHE
            - reqwest-LICENSE-APACHE
            - reqwest-LICENSE-MIT
            - ring-LICENSE
            - rkyv-LICENSE-MIT
            - rkyv_derive-LICENSE-MIT
            - rle-decode-fast-LICENSE-APACHE
            - rle-decode-fast-LICENSE-MIT
            - roaring-LICENSE-APACHE
            - roaring-LICENSE-MIT
            - rusqlite-LICENSE-MIT
            - rust-ini-LICENSE-MIT
            - rust-s3-LICENSE-MIT
            - rust-stemmers-LICENSE-BSD
            - rust-stemmers-LICENSE-MIT
            - rust_decimal-LICENSE-MIT
            - rustc-hash-LICENSE-APACHE
            - rustc-hash-LICENSE-MIT
            - rustc_version-LICENSE-APACHE
            - rustc_version-LICENSE-MIT
            - rustc_version_runtime-LICENSE-MIT
            - rustix-LICENSE-APACHE
            - rustix-LICENSE-MIT
            - rustls-LICENSE-APACHE
            - rustls-LICENSE-ISC
            - rustls-LICENSE-MIT
            - rustls-native-certs-LICENSE-APACHE
            - rustls-native-certs-LICENSE-ISC
            - rustls-native-certs-LICENSE-MIT
            - rustls-pemfile-LICENSE-APACHE
            - rustls-pemfile-LICENSE-ISC
            - rustls-pemfile-LICENSE-MIT
            - rustls-pki-types-LICENSE-APACHE
            - rustls-pki-types-LICENSE-MIT
            - rustls-webpki-LICENSE-ISC
            - rustversion-LICENSE-APACHE
            - rustversion-LICENSE-MIT
            - ryu-LICENSE-APACHE
            - ryu-LICENSE-BOOST
            - same-file-LICENSE-MIT
            - scopeguard-LICENSE-APACHE
            - scopeguard-LICENSE-MIT
            - scratch-LICENSE-APACHE
            - scratch-LICENSE-MIT
            - sct-LICENSE-APACHE
            - sct-LICENSE-ISC
            - sct-LICENSE-MIT
            - seahash-LICENSE-MIT
            - semver-LICENSE-APACHE
            - semver-LICENSE-MIT
            - send_wrapper-LICENSE-APACHE
            - send_wrapper-LICENSE-MIT
            - seq-macro-LICENSE-APACHE
            - seq-macro-LICENSE-MIT
            - serde-LICENSE-APACHE
            - serde-LICENSE-MIT
            - serde_bytes-LICENSE-APACHE
            - serde_bytes-LICENSE-MIT
            - serde_derive-LICENSE-APACHE
            - serde_derive-LICENSE-MIT
            - serde_json-LICENSE-APACHE
            - serde_json-LICENSE-MIT
            - serde_nanos-LICENSE-APACHE
            - serde_nanos-LICENSE-MIT
            - serde_repr-LICENSE-APACHE
            - serde_repr-LICENSE-MIT
            - serde_urlencoded-LICENSE-APACHE
            - serde_urlencoded-LICENSE-MIT
            - serde_with-LICENSE-APACHE
            - serde_with-LICENSE-MIT
            - serde_with_macros-LICENSE-APACHE
            - serde_with_macros-LICENSE-MIT
            - shlex-LICENSE-APACHE
            - shlex-LICENSE-MIT
            - signal-hook-registry-LICENSE-APACHE
            - signal-hook-registry-LICENSE-MIT
            - signatory-LICENSE-APACHE
            - signatory-LICENSE-MIT
            - signature-LICENSE-APACHE
            - signature-LICENSE-MIT
            - simdutf8-LICENSE-APACHE
            - simdutf8-LICENSE-MIT
            - sketches-ddsketch-LICENSE-APACHE
            - slab-LICENSE-MIT
            - slug-LICENSE-APACHE
            - slug-LICENSE-MIT
            - smallvec-LICENSE-APACHE
            - smallvec-LICENSE-MIT
            - snafu-LICENSE-APACHE
            - snafu-LICENSE-MIT
            - snafu-derive-LICENSE-APACHE
            - snafu-derive-LICENSE-MIT
            - snap-BSD-LICENSE
            - socket2-LICENSE-APACHE
            - socket2-LICENSE-MIT
            - spin-LICENSE-MIT
            - spki-LICENSE-APACHE
            - spki-LICENSE-MIT
            - sqlparser-LICENSE-APACHE
            - stable_deref_trait-LICENSE-APACHE
            - stable_deref_trait-LICENSE-MIT
            - stacker-LICENSE-APACHE
            - stacker-LICENSE-MIT
            - static_assertions-LICENSE-APACHE
            - static_assertions-LICENSE-MIT
            - stringprep-LICENSE-APACHE
            - stringprep-LICENSE-MIT
            - strsim-LICENSE-MIT
            - strum-LICENSE-MIT
            - strum_macros-LICENSE-MIT
            - subtle-LICENSE-BSD
            - syn-LICENSE-APACHE
            - syn-LICENSE-MIT
            - sync_wrapper-LICENSE-APACHE
            - synstructure-LICENSE-MIT
            - sysinfo-LICENSE-MIT
            - tagptr-LICENSE-APACHE
            - tagptr-LICENSE-MIT
            - take_mut-LICENSE-MIT
            - tantivy-LICENSE-MIT
            - tantivy-bitpacker-LICENSE-MIT
            - tantivy-columnar-LICENSE-MIT
            - tantivy-common-LICENSE-MIT
            - tantivy-fst-LICENSE-MIT
            - tantivy-query-grammar-LICENSE-MIT
            - tantivy-sstable-LICENSE-MIT
            - tantivy-stacker-LICENSE-MIT
            - tantivy-tokenizer-api-LICENSE-MIT
            - tap-LICENSE-MIT
            - target-lexicon-LICENSE-APACHE
            - tempfile-LICENSE-APACHE
            - tempfile-LICENSE-MIT
            - termcolor-LICENSE-MIT
            - termtree-LICENSE-MIT
            - thiserror-LICENSE-APACHE
            - thiserror-LICENSE-MIT
            - thiserror-impl-LICENSE-APACHE
            - thiserror-impl-LICENSE-MIT
            - thrift-LICENSE-APACHE
            - time-LICENSE-APACHE
            - time-LICENSE-MIT
            - time-core-LICENSE-APACHE
            - time-core-LICENSE-MIT
            - time-macros-LICENSE-APACHE
            - time-macros-LICENSE-MIT
            - timely-LICENSE-MIT
            - timely_bytes-LICENSE-MIT
            - timely_communication-LICENSE-MIT
            - timely_logging-LICENSE-MIT
            - tinyvec-LICENSE-APACHE
            - tinyvec-LICENSE-MIT
            - tinyvec-LICENSE-ZLIB
            - tinyvec_macros-LICENSE-APACHE
            - tinyvec_macros-LICENSE-MIT
            - tinyvec_macros-LICENSE-ZLIB
            - tokio-LICENSE-MIT
            - tokio-macros-LICENSE-MIT
            - tokio-native-tls-LICENSE-MIT
            - tokio-postgres-LICENSE-APACHE
            - tokio-postgres-LICENSE-MIT
            - tokio-rustls-LICENSE-APACHE
            - tokio-rustls-LICENSE-MIT
            - tokio-stream-LICENSE-MIT
            - tokio-util-LICENSE-MIT
            - tokio-websockets-LICENSE-MIT
            - toml_datetime-LICENSE-APACHE
            - toml_datetime-LICENSE-MIT
            - toml_edit-LICENSE-APACHE
            - toml_edit-LICENSE-MIT
            - tonic-LICENSE-MIT
            - tower-LICENSE-MIT
            - tower-layer-LICENSE-MIT
            - tower-service-LICENSE-MIT
            - tracing-LICENSE-MIT
            - tracing-attributes-LICENSE-MIT
            - tracing-core-LICENSE-MIT
            - trim-in-place-LICENSE-MIT
            - try-lock-LICENSE-MIT
            - tryhard-LICENSE-APACHE
            - tryhard-LICENSE-MIT
            - twox-hash-LICENSE-MIT
            - typed-builder-LICENSE-APACHE
            - typed-builder-LICENSE-MIT
            - typed-builder-macro-LICENSE-APACHE
            - typed-builder-macro-LICENSE-MIT
            - typenum-LICENSE-APACHE
            - typenum-LICENSE-MIT
            - unicode-bidi-LICENSE-APACHE
            - unicode-bidi-LICENSE-MIT
            - unicode-ident-LICENSE-APACHE
            - unicode-ident-LICENSE-MIT
            - unicode-ident-LICENSE-UNICODE
            - unicode-normalization-LICENSE-APACHE
            - unicode-normalization-LICENSE-MIT
            - unicode-properties-LICENSE-APACHE
            - unicode-properties-LICENSE-MIT
            - unicode-segmentation-LICENSE-APACHE
            - unicode-segmentation-LICENSE-MIT
            - unicode-width-LICENSE-APACHE
            - unicode-width-LICENSE-MIT
            - unicode-xid-LICENSE-APACHE
            - unicode-xid-LICENSE-MIT
            - unindent-LICENSE-APACHE
            - unindent-LICENSE-MIT
            - untrusted-LICENSE-ISC
            - url-LICENSE-APACHE
            - url-LICENSE-MIT
            - urlencoding-LICENSE-MIT
            - usearch-LICENSE-APACHE
            - utf16_iter-LICENSE-APACHE
            - utf16_iter-LICENSE-MIT
            - utf8-ranges-LICENSE-MIT
            - utf8_iter-LICENSE-APACHE
            - utf8_iter-LICENSE-MIT
            - uuid-LICENSE-APACHE
            - uuid-LICENSE-MIT
            - vcpkg-LICENSE-APACHE
            - vcpkg-LICENSE-MIT
            - version_check-LICENSE-APACHE
            - version_check-LICENSE-MIT
            - visibility-LICENSE-APACHE
            - visibility-LICENSE-MIT
            - visibility-LICENSE-ZLIB
            - void-LICENSE-MIT
            - vsimd-LICENSE-MIT
            - walkdir-LICENSE-MIT
            - want-LICENSE-MIT
            - web-time-LICENSE-APACHE
            - web-time-LICENSE-MIT
            - webpki-roots-LICENSE
            - whoami-LICENSE-APACHE
            - whoami-LICENSE-BOOST
            - whoami-LICENSE-MIT
            - winnow-LICENSE-MIT
            - write16-LICENSE-APACHE
            - write16-LICENSE-MIT
            - wyz-LICENSE-MIT
            - xmlparser-LICENSE-APACHE
            - xmlparser-LICENSE-MIT
            - xxhash-rust-LICENSE-BOOST
            - xz2-LICENSE-APACHE
            - xz2-LICENSE-MIT
            - z85-LICENSE-APACHE
            - z85-LICENSE-MIT
            - zerocopy-LICENSE-APACHE
            - zerocopy-LICENSE-BSD
            - zerocopy-LICENSE-MIT
            - zerocopy-derive-LICENSE-APACHE
            - zerocopy-derive-LICENSE-BSD
            - zerocopy-derive-LICENSE-MIT
            - zeroize-LICENSE-APACHE
            - zeroize-LICENSE-MIT
            - zstd-LICENSE-MIT
            - zstd-safe-LICENSE-APACHE
            - zstd-safe-LICENSE-MIT
            - zstd-sys-LICENSE-APACHE
            - zstd-sys-LICENSE-MIT
          📂 python/
          📂 src/
            - async_runtime.rs
            - deepcopy.rs
            - env.rs
            - fs_helpers.rs
            - lib.rs
            - mat_mul.rs
            - pipe.rs
            - python_api.rs
            - retry.rs
            - timestamp.rs
          📂 tests/
        📂 pi-mono/
          - LICENSE
          - biome.json
          - package.json
          - pi-mono.code-workspace
          - pi-test.sh
          - test.sh
          - tsconfig.base.json
          - tsconfig.json
          📂 .github/
            - APPROVED_CONTRIBUTORS
          📂 .husky/
            - pre-commit
          📂 .pi/
          📂 packages/
          📂 scripts/
            - build-binaries.sh
            - cost.ts
            - release.mjs
            - session-transcripts.ts
            - sync-versions.js
        📂 puter/
          - .dockerignore
          - .env.example
          - .gitattributes
          - .gitmodules
          - .is_puter_repository
          - .npmrc
          - .prettierignore
          - Dockerfile
          - docker-compose.yml
          - eslint.config.js
          - exports.js
          - package.json
          - rust-toolchain.toml
          - tsconfig.base.json
          - tsconfig.build.json
          - tsconfig.json
          - ws-debug.mjs
          📂 .github/
            - FUNDING.yml
          📂 .husky/
            - pre-commit
          📂 .idx/
            - dev.nix
            - icon.png
          📂 doc/
            - File Structure.drawio
            - File Structure.drawio.png
          📂 eslint/
            - bang-space-if.js
            - control-structure-spacing.js
            - mandatory.eslint.config.js
            - space-unary-ops-with-exception.js
          📂 extensions/
            - .gitkeep
            - api.d.ts
            - data.js
            - example-kv.js
            - example_gui_extension.js
            - exports_something.js
            - extension-util.js
            - imports_something.js
            - jsconfig.json
            - tsconfig.json
            - utilities.js
          📂 mod_packages/
          📂 mods/
          📂 puter/
          📂 scripts/
            - gen.sh
          📂 src/
          📂 submodules/
          📂 tests/
            - example-client-config.yaml
            - tsconfig.json
          📂 tools/
            - .commit
            - build_relay.sh
            - build_v86.sh
            - check-translations.js
            - doc_helper.js
            - gen-release-notes.js
            - l_checker_config.json
            - run-selfhosted.js
            - validate-eslint.js
          📂 volatile/
        📂 remotion/
          - .cursorignore
          - .gitattributes
          - .npmrc
          - .prettierrc.js
          - FUNDING.yml
          - bun.lock
          - bunfig.toml
          - go.work
          - go.work.sum
          - package.json
          - publish.ts
          - set-version.ts
          - tsconfig.json
          - turbo.json
          📂 .cursor/
            - mcp.json
          📂 .github/
            - copilot-instructions.md
            - pull_request_template.md
          📂 .vscode/
            - extensions.json
            - settings.json
            - tasks.json
          📂 packages/
            - tsconfig.settings.json
        📂 supermemory/
          - LICENSE
          - biome.json
          - package.json
          - turbo.json
          📂 .github/
          📂 apps/
          📂 packages/
        📂 superpowers/
          - .gitattributes
          - LICENSE
          📂 .claude-plugin/
            - marketplace.json
            - plugin.json
          📂 .github/
            - FUNDING.yml
          📂 .opencode/
            - INSTALL.md
          📂 agents/
          📂 commands/
          📂 docs/
          📂 hooks/
            - hooks.json
            - run-hook.cmd
            - session-start.sh
          📂 lib/
            - skills-core.js
          📂 skills/
          📂 tests/
        📂 tomcp/
          - LICENSE
          - index.html
          - logo.png
          - logo.svg
          - logoblack.png
          - logowhite.svg
          - sitemap.xml
          📂 .github/
            - FUNDING.yml
          📂 worker/
            - package.json
            - tsconfig.json
            - wrangler.toml
        📂 trivy/
          - .dockerignore
          - .gitattributes
          - .golangci.yaml
          - .release-please-manifest.json
          - Dockerfile
          - Dockerfile.canary
          - LICENSE
          - NOTICE
          - buf.gen.yaml
          - buf.yaml
          - go.mod
          - go.sum
          - goreleaser-canary.yml
          - goreleaser.yml
          - mkdocs.yml
          - release-please-config.json
          📂 .github/
            - CODEOWNERS
            - dependabot.yml
            - pull_request_template.md
          📂 .vex/
            - oci.openvex.json
            - trivy.openvex.json
          📂 brand/
            - Trivy-OSS-Logo-Color-Horizontal-RGB.png
            - Trivy-OSS-Logo-Color-Horizontal-RGB.svg
            - Trivy-OSS-Logo-Color-Stacked-RGB.png
            - Trivy-OSS-Logo-Color-Stacked-RGB.svg
            - Trivy-OSS-Logo-White-Horizontal-RGB.png
            - Trivy-OSS-Logo-White-Horizontal-RGB.svg
            - Trivy-OSS-Logo-White-Stacked-RGB.png
            - Trivy-OSS-Logo-White-Stacked-RGB.svg
          📂 ci/
            - deploy-deb.sh
            - deploy-rpm.sh
          📂 cmd/
          📂 contrib/
            - Trivy.gitlab-ci.yml
            - asff.tpl
            - gitlab-codequality.tpl
            - gitlab.tpl
            - html.tpl
            - install.sh
            - junit.tpl
          📂 docs/
          📂 e2e/
            - e2e_test.go
          📂 examples/
          📂 helm/
          📂 integration/
            - client_server_test.go
            - config_test.go
            - convert_test.go
            - docker_engine_test.go
            - integration_test.go
            - k8s_test.go
            - module_test.go
            - plugin_test.go
            - registry_test.go
            - repo_test.go
            - sbom_test.go
            - standalone_tar_test.go
            - testimages.ini
            - vm_test.go
          📂 internal/
          📂 magefiles/
            - config_schema.go
            - docs.go
            - fixture.go
            - helm.go
            - helm_test.go
            - magefile.go
            - schema.go
            - spdx.go
            - terraformplan.go
            - vex.go
          📂 misc/
          📂 pkg/
          📂 rpc/
          📂 schema/
            - trivy-config.json
        📂 unsloth/
          - .gitattributes
          - .pre-commit-ci.yaml
          - .pre-commit-config.yaml
          - LICENSE
          - pyproject.toml
          - unsloth-cli.py
          📂 .github/
            - FUNDING.yml
          📂 images/
            - Assistant.png
            - Colab.png
            - Discord button.png
            - Discord.png
            - Documentation Button.png
            - Free version button.png
            - Kaggle.png
            - Kofi button.png
            - LAION 2GPU.png
            - Merge.png
            - Run.png
            - Slim Orca 2GPUs.png
            - Terminal_Type.png
            - Where_Terminal.png
            - buy me a coffee button.png
            - documentation github button.png
            - documentation green button.png
            - documentation lighter.png
            - documentation white button.png
            - made with unsloth.png
            - ollama.png
            - peft x trl button.png
            - start free finetune button.png
            - unsloth end.png
            - unsloth loading page render.png
            - unsloth logo black text.png
            - unsloth logo only.png
            - unsloth logo white text.png
            - unsloth made with love.png
            - unsloth new logo.png
            - unsloth sticker.png
          📂 scripts/
            - enforce_kwargs_spacing.py
            - run_ruff_format.py
          📂 tests/
            - __init__.py
            - test_model_registry.py
            - test_raw_text.py
          📂 unsloth/
            - __init__.py
            - _auto_install.py
            - chat_templates.py
            - device_type.py
            - import_fixes.py
            - ollama_template_mappers.py
            - save.py
            - tokenizer_utils.py
            - trainer.py
      📂 INTEGRATION/
      📂 INTEGRATIONS/
        - README_HAYSTACK_UKG.md
      📂 KNIGHTS/
      📂 LEGAL/
        - COPYRIGHT_HEADER.md
        - IP_STRATEGY.md
        - MASTER_GLOSSARY.md
        - TRADEMARK_REGISTER.md
        - TRADE_SECRET_MANIFEST.md
      📂 MANIFESTS/
        - AUDIT_REPORT_20260131.md
        - AUDIT_REPORT_20260131_2215.md
        - CAMELOT_TRIAD_INTEGRATION.md
        - Entire_map.md
        - PHASE_8_KINETIC_ASCENSION.md
        - PHASE_9_ETHEREAL_RESONANCE.md
        - ledger_tool.blueprint.md
      📂 PROMPTS/
        - CAMELOT_DEFENSE_GRID_ACTIVATE_AUTONOMOUS.md
        - CAMELOT_DEFENSE_GRID_NOTEBOOKLM_AGGRESSIVE_VARIANT.md
        - CAMELOT_DEFENSE_GRID_NOTEBOOKLM_LIVE_PROFILE.md
        - CAMELOT_DEFENSE_GRID_NOTEBOOKLM_MASTER_PROMPT.md
        - CAMELOT_DEFENSE_GRID_ROLE_CARDS.md
        - CAMELOT_DEFENSE_GRID_SAFETY_POLICY.md
        - CAMELOT_DEFENSE_GRID_VALIDATION_CHECKLIST.md
        - PROMPT_REGISTRY.md
      📂 RESEARCH/
      📂 SECURITY/
      📂 SPECS/
        - FUNCTIONAL_SPEC_FORGE_LUKAS_V200.md
      📂 TEMPLATES/
    📂 reports/
      - AUDIT_REPORT.md
      - BRIEFING.md
      - THINK_TANK_SESSION.md
      - VERIFICATION.md
      - audit_activepieces.json
      - audit_agentflow.json
      - audit_atomic_agents.json
      - audit_big_agi.json
      - audit_bolt_diy.json
      - audit_cogflow.json
      - audit_fooocus.json
      - audit_geophone.json
      - audit_goose.json
      - audit_kestra.json
      - audit_koboldcpp.json
      - audit_kokoro.json
      - audit_langgraph.json
      - audit_leon.json
      - audit_lightning.json
      - audit_litellm.json
      - audit_multitalk.json
      - audit_openvoice.json
      - audit_outspeed.json
      - audit_pastemax.json
      - audit_pathway.json
      - audit_remotion.json
      - audit_shoutify.json
      - audit_superagi.json
      - audit_supermemory.json
      - audit_superpowers.json
      - audit_ten.json
      - audit_trivy.json
      - audit_unsloth.json
      - verification_report_v300.4.md
      📂 ANALYSIS/
      📂 BRIEFINGS/
        - BRIEFING.md
        📂 BRIEFINGS/
      📂 CASE_STUDIES/
      📂 QA/
      📂 REMEDIATION/
  📂 edge/
    - __init__.py
  📂 infra/
    📂 caddy/
      - Caddyfile
  📂 k8s/
    - deployment.yaml
  📂 kinetic_edge/ [KINETIC]
    📂 mcp_server/ [KINETIC]
      - Cargo.lock
      - Cargo.toml
      📂 src/ [KINETIC]
        - ap2_settlement.rs
        - bifrost.rs
        - main.rs
        - turboquant.rs
        - wasi_nn.rs
    📂 wasi_guest/ [KINETIC]
      - Cargo.lock
      - Cargo.toml
      📂 src/ [KINETIC]
        - main.rs
  📂 ledger_keeper/
    - Cargo.lock
    - Cargo.toml
    📂 src/
      - ap2_settlement.rs
      - main.rs
  📂 local/
    - __init__.py
  📂 local_brain/
    - __init__.py
    - main.py
  📂 monitoring/
    - BINARIES_REQUIRED.md
    - prometheus.yml
    - start_observability.ps1
  📂 security/
    - __init__.py
    - morgana_vault.py
    - smart_cost_controller.py
  📂 squires/ [COLONY]
    - __init__.py
    - colony.py
    - compression_guardian.py
    - ledger_guardian.py
    📂 bridge/ [COLONY]
      - __init__.py
      - bridge_script.py
      - lightpanda_bridge.py
      - listener.py
      - train_script.py
    📂 cloud/ [COLONY]
      - __init__.py
      - squire_grid_council.py
      - squire_judge.py
      - squire_mason.py
      - squire_scan.py
      - squire_sentinel.py
      - squire_sweep.py
      - squire_vector.py
    📂 local/ [COLONY]
      - __init__.py
      - sir_proxy_knight.py
      - squire_ghost.py
      - squire_index.py
  📂 src/
    📂 blueprints/
      - anya_lyte.md
      - fleet_test.md
      - sir_masque.md
  📂 tests/
    - backend_integrity.js
    - conftest.py
    - genesis_simulation.py
    - integration_phase3.py
    - neural_link_verifier.js
    - smoke_test.py
    - test_cli.py
    - test_cloudbrain_sync.py
    - test_defense_grid_agent.py
    - test_grid_council.py
    - test_kernel.py
    - test_ledger_guardian.py
    - test_security.py
    - verify_bridge.js
    📂 data/
      - validate_sync.js
    📂 fleet/
      - test_swarm_integrity.py
    📂 ui/
      - test_ui_consistency.js
  📂 tools/
    - Perplexity_Distiller.py
    - antigravity.py
    - camelot_defense_grid_agent.py
    - install_ledger_guardian_task.ps1
    - install_personal_inference_bootstrap.ps1
    - nano_scan.py
    - run_bootstrap_daemon.ps1
    - run_bootstrap_maintenance.ps1
    - scout_agent.py
    - squire_cli.py
    📂 chronos_gate/
      - scheduler.py
    📂 merlin_eye/
      - vision.py
    📂 nano_physics/
      - core.py
      - physics_log.json
      - run_sim.py
      - validate.py
    📂 phials/
      - regex_cleaner.py
    📂 sir_ears/
      - transcribe.py
    📂 sir_masque/
      - __init__.py
      - orchestrator.py
      - proxy.py
      - puppet.py
      - vault.py
      📂 missions/
        - twitter_monitor.py
    📂 sir_sonus/
      - Dockerfile
      - config.json
      - config.yaml
      - engine.py
      - kokoro-v0_19.onnx
      - server.py
      📂 voices/
        - af_bella.bin
        - voices.bin

---
**[SYSTEM_NOTE]:** This map is auto-generated. Do not edit manually. Run `01_KERNEL/titan/phials/map_generator.py` to refresh.
