# CAMELOT-OS ARTIFACT REGISTRY v300.4.0
# All system artifacts, binaries, databases, and generated outputs
# Generated: 2026-03-31

---

## COMPILED BINARIES

| Artifact | Tech | Size | Location | Status |
|---|---|---|---|---|
| Saltare | Go | 37.6 MB | `02_FORGE/KINETIC_ARMORY/Saltare/saltare.exe` | OPERATIONAL |
| Saltare MCP | Go | 8.3 MB | `02_FORGE/KINETIC_ARMORY/Saltare/bin/saltare-mcp.exe` | OPERATIONAL |
| Saltare Gateway | Go | 37.6 MB | `02_FORGE/KINETIC_ARMORY/Saltare/saltare_gateway.exe` | OPERATIONAL |
| CLIProxyAPI | Go | 50 MB | `~/CLIProxyAPI/cli-proxy-api.exe` | OPERATIONAL |
| Ledger | Go | 751 KB | `02_FORGE/kinetic/bin/ledger.exe` | OPERATIONAL |
| Cribo | Rust | Source only | `02_FORGE/KINETIC_ARMORY/Cribo/` | NEEDS BUILD |
| Rotel | Rust | Source only | `02_FORGE/KINETIC_ARMORY/Rotel/` | NEEDS BUILD |
| Kinetic Edge MCP | Rust | Source only | `kinetic_edge/mcp_server/` | NEEDS BUILD |

---

## DATABASES

| Database | Tech | Size | Location | Function |
|---|---|---|---|---|
| Ouroboros | SQLite WAL | 32 KB | `03_VAULT/training/configs/ouroboros.db` | CLI state persistence |
| ChromaDB | SQLite | 323 KB | `01_KERNEL/titan/Titan_Graph/chromadb/chroma.sqlite3` | Vector embeddings |
| Titan Ledger | SQLite | 24 KB | `01_KERNEL/titan/Data_Pipeline/titan_ledger.db` | Event ledger |
| Saltare Badger | BadgerDB | varies | `02_FORGE/KINETIC_ARMORY/Saltare/data/badger/` | KV store |

---

## KNOWLEDGE ARTIFACTS

| Artifact | Format | Size | Location | Function |
|---|---|---|---|---|
| UKG Graph | JSON-LD | ~8 KB | `03_VAULT/training/configs/memory/ukg_graph.jsonld` | Universal Knowledge Glyph (50 nodes, 42 edges) |
| TOON Boris | JSON | 10.4 KB | `03_VAULT/training/configs/memory/toon_ukg_full.json` | Compressed Sir Boris entity (TOON v3.1) |
| Entire Map | Markdown | 12,116 lines | `entiremap.md` | Comprehensive system documentation |
| OS Manifest | Markdown | 1.6 KB | `OS_MANIFEST.md` | Split-brain topology spec |
| Provenance Ledger | Markdown | 81 KB | `PROVENANCE_LEDGER.md` | 1045+ line audit trail (3 copies synced) |
| Golden Samples | JSONL | 9.3 KB | `03_VAULT/training/golden_samples.jsonl` | Training data |

---

## CONFIGURATION ARTIFACTS

| Artifact | Format | Location | Function |
|---|---|---|---|
| Saltare Config | TOML | `01_KERNEL/EXCALIBUR/config/saltare.toml` | Gateway routing rules |
| MCP Config | JSON | `03_VAULT/training/configs/config/mcp_config.json` | MCP server definitions |
| OmniRoute | JSON | `03_VAULT/training/configs/config/omniroute.json` | Multi-route config |
| CLIProxy Config | YAML | `~/CLIProxyAPI/config.yaml` | Proxy settings (port 8080) |
| Docker Compose | YAML | `docker-compose.yml` | 7 services (merlin, rotel, cribo, sonus, memory, hbbs, hbbr) |
| K8s Deployment | YAML | `k8s/deployment.yaml` | Kubernetes deployment |
| Chimera Kernel | JSON | `01_KERNEL/EXCALIBUR/chimera_unified_kernel.json` | Kernel config |

---

## SKILL ARTIFACTS (Cross-Engine)

| Artifact | Engine | Size | Location |
|---|---|---|---|
| Sir Boris Skill | Claude Code | 9.8 KB | `~/.claude/skills/sir_boris.md` |
| Vocal Skill | Claude Code | 2.2 KB | `~/.claude/skills/vocal.md` |
| Boris Gemini Ext | Gemini CLI | 3.5 KB | `~/.gemini/extensions/sir-boris/GEMINI.md` |
| Boris Codex Skill | OpenAI Codex | 2.9 KB | `~/.codex/skills/sir_boris.md` |

---

## NKG ARTIFACTS (Nano-Knowledge Glyphs)

Location: `docs/reference/ARTIFACTS/`

| File | Function |
|---|---|
| `Ω_ASSIMILATION_ENGINE.nkg` | Assimilation pipeline definition |
| `Ω_CAMELOT_SINGULARITY_v100.nkg` | v100 system snapshot |
| `Ω_INTEGRATION_CONFIGS.nkg` | Integration configuration crystal |
| `Ω_PHASE_1_BLUEPRINTS.nkg` | Phase 1 build blueprints |
| `Ω_PHASE_2_BLUEPRINTS.nkg` | Phase 2 build blueprints |
| `Ω_SCOUT_SWARM.nkg` | Scout swarm configuration (in docs/) |

---

## CARTRIDGE ARTIFACTS

Location: `03_VAULT/training/configs/cartridges/`

| File | Format | Function |
|---|---|---|
| `nextjs.yaml` | YAML | Next.js framework knowledge |
| `python-api.yaml` | YAML | Python API patterns |
| `security.yaml` | YAML | Security best practices |

---

## LOG ARTIFACTS

Location: `logs/`

| File | Function |
|---|---|
| `defense_grid/` | Defense system event logs |
| `rotel_traces/` | OpenTelemetry trace data |
| `squire_ghost_scan.json` | Last ghost process scan (13 KB) |
| `squire_index_scan.json` | Last directory index (681 KB) |
| `kernel_status.log` | Kernel health log |
| `excalibur_errors.log` | Kernel error log |
| `aegis_pulse.log` | Heartbeat pulse log |

---

## VOICE / MEDIA ARTIFACTS

Location: `docs/reference/ARTIFACTS/`

| File | Function |
|---|---|
| `test_synthesis.wav` | Voice synthesis test sample |
| `voice_samples/` | Voice sample collection |

---

## IP FORTRESS ARTIFACTS

Location: `03_VAULT/knowledge/Copyright/` (14 PDFs)

Referenced by: UKG node N36 (IP_Fortress_Suite)

| Document | Location |
|---|---|
| Master Glossary | `docs/reference/LEGAL/MASTER_GLOSSARY.md` |
| Copyright Header | `docs/reference/LEGAL/COPYRIGHT_HEADER.md` |
| IP Strategy | `docs/reference/LEGAL/IP_STRATEGY.md` |
| Trademark Register | `docs/reference/LEGAL/TRADEMARK_REGISTER.md` |
| Trade Secret Manifest | `docs/reference/LEGAL/TRADE_SECRET_MANIFEST.md` |

---

## BRAND ARTIFACTS

| Artifact | Location | Status |
|---|---|---|
| Brand Architecture v2.0 | Notion (32ca3c2b-2603-812e-a6fb-f1ac593026f6) | 7 sections |
| Master Tagline | "Visions Come True." | ACTIVE |
| Color Palette | Primary: #B4962D (Sovereign Gold) | ACTIVE |
| Service Tiers | Dream Stage, Vision Stage, Empire Stage | ACTIVE |
| Business Plan | Notion | 5 of 9 sections filled |
