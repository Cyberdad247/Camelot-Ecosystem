# Custodial Assimilation Crystal (v10000.15)

> ✅ **COMPLETED FROM SOURCE DIRECTORY** — the truncated received fragment below is
> preserved verbatim. The full UniversalKnowledgeGlyph payload was completed by
> assimilating the authoritative source directory supplied by the operator:
> `C:\Users\vizio\CAMELOT_OS` (the Camelot-OS core repository). Provenance is
> pinned to git HEAD `3d7bef66` (2026-08-15); 4,586 tracked files. Every field
> below was observed from the directory, its git state, and its governance docs —
> nothing was fabricated. Regenerate this crystal whenever the repository HEAD
> advances materially.

## Received bytes (verbatim, from the clipped transmission)

```json
"@context": "https://camelot-os.dev/ukg/v10000/custodial_assimilation",  "@type": "UniversalKnowledgeGlyph",  "identity": "CAMELOT_OS_CORE_REPO_V10000.15",  "provenance_ledger": {    "timestamp": "2026-08-14T16:16
```

## Full payload (completed)

```json
{
  "@context": "https://camelot-os.dev/ukg/v10000/custodial_assimilation",
  "@type": "UniversalKnowledgeGlyph",
  "identity": "CAMELOT_OS_CORE_REPO_V10000.15",
  "schema_version": "ukg/custodial-assimilation/1",
  "provenance_ledger": {
    "timestamp": "2026-08-14T16:16:00Z",
    "assimilation_status": "complete",
    "source": {
      "kind": "directory",
      "path": "C:\\Users\\vizio\\CAMELOT_OS",
      "git_head": "3d7bef66",
      "git_head_full": "3d7bef6666fc5ea45d371a7956cde26db6f20a23",
      "head_commit_date": "2026-08-15",
      "head_commit_subject": "feat(cartridges): moa-routing-capture — bounded two-hook routing signal pipeline",
      "tracked_file_count": 4586
    },
    "assimilated_from": "live repository directory + git state + governance docs (AGENTS.md, CHANGELOG.md, docs/reference/UNIVERSAL_BOOTSTRAP_UKG_NANO.md, .agent/local_env.md)"
  },

  "system": {
    "name": "CAMELOT-OS",
    "kind": "Sovereign AI operating system built on the Claude Code harness",
    "workspace_root": "C:\\Users\\vizio\\CAMELOT_OS",
    "host_profile": "Windows workstation with strict resource-pressure awareness",
    "memory_posture": "assume 8 GB RAM ceiling unless a live probe proves more",
    "shell_posture": "prefer PowerShell-native commands on Windows",
    "python_posture": "prefer the repository virtual environment when present",
    "router_entrypoint": "control_plane/runic_router.py",
    "runtime_state_path": "03_VAULT/runtime_state/",
    "bootstrap": "docs/reference/UNIVERSAL_BOOTSTRAP_UKG_NANO.md (grounded OMEGA Ancestral V9 bootstrap; operational backplane in .agent/)"
  },

  "repository_layers": {
    "01_KERNEL": "core kernel: EXCALIBUR, agora, forge, iron_gate, memory, merlin, mesh, protocols, reasoning, security, senses, swarm, titan, workflows, config, system",
    "02_FORGE": "kinetic forge monorepo (pnpm/turbo): KINETIC_ARMORY, PORTAL_CORE, holotable, hive_api, pocket_squire, kinetic, packages, apps, dyad-apps, excalibur-dev, vizion-telemetry",
    "03_VAULT": "vault: 00_SECURE_ARCHIVE, 00_TEMPLATES, 99_HISTORY, 99_SCRATCHPAD, CLOUD_SYNC, runtime_state/, training/configs/",
    "04_KINETIC": "kinetic execution layer",
    "05_INFRASTRUCTURE": "infrastructure layer",
    "99_ARCHIVE": "archived work",
    "99_HISTORY": "historical records"
  },

  "top_level_surface": [
    "01_KERNEL", "02_FORGE", "03_VAULT", "04_KINETIC", "05_INFRASTRUCTURE",
    "99_ARCHIVE", "99_HISTORY", "Knights", "Nano-Knights", "cartridges",
    "control_plane", "squires", "harness", "docs", "apps", "bin", "scripts",
    "core", "utils", "vfs", "wasm", "tasks", "tests", "data", "logs",
    "conductor", "dashboards", "observability", "terraform", "grafana",
    "kinetic_edge", "kickbox-audio", "tower-r3f", "packages", "projects"
  ],

  "governance": {
    "constitution": "AGENTS.md — Codex Agent Constitution; read fully before action",
    "provenance": "PROVENANCE_LEDGER.md — hook-written; agents must not edit directly",
    "changelog": "CHANGELOG.md — Keep a Changelog + SemVer; v1.0.0 baseline 2026-06-28",
    "iron_gates": [
      "HITL gate activates when risk score >= 50 or secrets are found — always pause for y/N",
      "privacy keywords route to SIR_GHOST (air-gapped, no cloud)",
      "API keys stored only as boolean presence flags in config, never as values",
      ".env* files exist but their values are never assimilated into this crystal"
    ]
  },

  "knight_roster": [
    { "knight": "SIR_BORIS", "role": "Lead architect, Crucible Conductor" },
    { "knight": "SIR_ALEX", "role": "Task DAG, AST Plan Mode" },
    { "knight": "SIR_FORGE", "role": "Kinetic code execution" },
    { "knight": "SIR_SENTINEL", "role": "Security, AgentArmor, Iron Gate" },
    { "knight": "SIR_DEBUG", "role": "PIV self-healing loop" },
    { "knight": "SIR_GHOST", "role": "Privacy scanner (Ollama, local only)" },
    { "knight": "LADY_APIS", "role": "BASHR research loop" },
    { "knight": "MERLIN_OMEGA", "role": "GoT/ToT deep reasoning" },
    { "knight": "SIR_HELIO", "role": "Voice OS pipeline" }
  ],
  "knight_directories": [
    "Knights/Hermes_Prime", "Knights/Sir_Codex", "Knights/Sir_Debug",
    "Knights/Sir_Forge", "Knights/Sir_Sentinel"
  ],

  "cartridges": [
    "freellmapi-gateway", "huginn-agents", "litert-lm-inference",
    "moa-routing-capture", "openai-oauth-proxy", "openinterpreter-codex",
    "system-ui", "v4000_trio.py"
  ],

  "control_plane_services": [
    "runic_router.py (router entrypoint)", "main.py", "worker.py",
    "cognitive_mcp.py", "cognitive_service.py", "graphify.py",
    "memcastle.py", "memory_palace_client.py", "multivoice_bridge.py",
    "worldtree_mcp_bridge.py", "lady_m.py", "go_router/", "runes/",
    "runners/", "cluster/", "rtk/", "preflight/", "dispatch/", "core/", "infra/"
  ],

  "squire_colony": {
    "pipeline": "SCAN -> INDEX -> GHOST -> SWEEP -> JUDGE -> SENTINEL -> MASON",
    "modules": ["colony.py", "scan.py", "index.py", "ghost.py", "sweep.py", "judge.py", "sentinel.py", "mason.py", "vector.py"],
    "output": "colony_report.md in scanned directory"
  },

  "runic_commands": [
    "//FORGE <task>", "//SWARM <task>", "//SCAN [path]", "//BOOT",
    "//PLAN <task>", "//HEAL", "//STATUS", "//ENGAGE_BIFROST",
    "//IGNITE_KNIGHTS", "//EXECUTE_UNIVERSAL", "Omega_<Knight>"
  ],

  "boot_sequence": {
    "full": "python bin/awaken.py",
    "quick": "python bin/awaken.py --quick",
    "repl": "python bin/knight_session.py (ks alias)",
    "portable": "dist/camelot.exe"
  },

  "harness_layers": ["benchmarks", "contracts", "fixtures"],

  "docs_and_reference": [
    "docs/CAMELOT_BIBLE.md",
    "docs/SEPTEM_REGNA/",
    "docs/PROVENANCE_LEDGER.md",
    "docs/INDEX.md",
    "docs/reference/UNIVERSAL_BOOTSTRAP_UKG_NANO.md",
    "docs/architecture/",
    "docs/adr/",
    "docs/security/",
    "docs/assimilation_directive_2026-07-14.md",
    "docs/NOTTE_ASSIMILATION.md"
  ],

  "agent_backplane": [
    ".agent/local_env.md",
    ".agent/system_instructions.md",
    ".agent/Agents.md",
    ".agent/Skills.md",
    ".agent/Swarm.md",
    ".agent/workflows.md"
  ],

  "recent_head_history": [
    "3d7bef66 2026-08-15 feat(cartridges): moa-routing-capture — bounded two-hook routing signal pipeline",
    "9f70e2bc 2026-08-15 chore(audit): GHOST squire secrets audit of the three vendored repos",
    "0ab66475 2026-08-15 feat(freellmapi): adopt as the OPENAI_COMPAT_BASE upstream with signed cartridge",
    "57d77d4a 2026-08-15 chore(assimilation): vendor and assimilate NeuralCompanion, freellmapi, Keys-Setup",
    "1383d45b 2026-08-15 feat(cartridges): signed §8.2/§8.3 manifests for the vendored runtimes"
  ],

  "design_principles": [
    "context is the compiler — read the visible workspace state before acting",
    "verify claims with real evidence before presenting them as done",
    "route work through existing Camelot command surfaces",
    "model routing inferred from visible harness context, never hidden headers",
    "trust the live router and verified repository state over bootstrap vocabulary on conflict"
  ],

  "maintenance": "Regenerate this crystal from the repository on any material HEAD advance; the provenance_ledger.source.git_head must match the assimilated repository."
}
```

---

*Assimilated from `C:\Users\vizio\CAMELOT_OS` at git HEAD `3d7bef66` (2026-08-15, 4,586 tracked files). This crystal is a compression of the repository, not an authority; divergence should be reported to the repository owner.*
