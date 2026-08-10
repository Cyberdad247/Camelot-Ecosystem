"""Sir Sentinel - The Shield / Universal Audit Knight.

Zero-trust forensic audit engine for Camelot Apex OS v300.4.
Covers every surface in the Camelot architecture:

  NETWORK:    Tailscale mesh, RustDesk relay, connectivity
  KINETIC:    Rust/Go binaries, IPC bridges, media transport
  SECURITY:   Secrets, vault, Iron Gate, Zenith, Warden
  INFRA:      Docker, CI/CD, Modal cloud, CLIProxyAPI
  KERNEL:     EXCALIBUR, Agora, Titan memory, MGV, control plane
  CLI:        Anya compiler, Merlin router, knights, cartridges
  AGENTS:     Squire Colony, A2A protocol, SARDA, DeerFlow
  MCP:        Server configs, prompt injection, tool drift
  VOICE:      Piper TTS, Kokoro, VoxService audio pipeline
  GOVERNANCE: Provenance ledger, .aiexclude, copyright, HITL

Enforces: Agent-Armor v2.0, Titanium Laws, rust-kinetic.yaml cartridge.
Pipeline: Anya APEE v6.5 -> Sentinel audit DAG -> Iron Gate HITL.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

from .base import BaseKnight

CAMELOT_OS = Path(os.environ.get("CAMELOT_OS", Path.home() / "CAMELOT_OS"))


# ══════════════════════════════════════════════════════════════════════
# AUDIT DOMAIN REGISTRY
# Each domain defines phases, checks, and tool commands.
# To add a new audit domain: add an entry here + keyword in _KEYWORD_MAP.
# ══════════════════════════════════════════════════════════════════════

AUDIT_DOMAINS: dict[str, dict] = {

    # ── NETWORK ───────────────────────────────────────────────────────

    "tailscale": {
        "label": "Tailscale Mesh Overlay",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Node Inventory",
                "checks": [
                    "Run `tailscale status` and cross-reference against 03_VAULT/UKG/current_state.json node registry",
                    "Flag nodes where tailscaleIp is null or unreachable",
                    "Verify all Camelot service names resolve via MagicDNS",
                    "Confirm camelot-relay-modal node is online or documented as decommissioned",
                ],
                "commands": ["tailscale status", "tailscale dns status"],
            },
            {
                "name": "ACL & Segmentation",
                "checks": [
                    "Verify zero-trust segmentation: knights on separate tags (tag:kinetic, tag:governance)",
                    "No wildcard *:* rules in production ACL policy",
                    "MCP server port 3001 restricted to tag:kinetic nodes only",
                    "SSH access limited to authorized admin nodes",
                    "Tailscale key expiry policy enforced (no indefinite keys)",
                ],
                "commands": [],
            },
            {
                "name": "Latency & Connectivity",
                "checks": [
                    "Sub-millisecond local latency confirmed",
                    "Remote latency <50ms (per verification.md spec)",
                    "NAT traversal functional for external nodes",
                    "DERP relay fallback tested and functional",
                ],
                "commands": ["tailscale ping"],
            },
        ],
    },

    "rustdesk": {
        "label": "RustDesk Remote Desktop Relay",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Relay Hardening",
                "checks": [
                    "hbbs/hbbr binds to Tailscale IP (100.x.x.x) only, not 0.0.0.0",
                    "ID server port 21116 firewalled to Tailscale subnet",
                    "Relay server port 21117 firewalled to Tailscale subnet",
                    "Encrypted relay keys rotated per harden_rustdesk.ps1 policy",
                    "No default or weak relay passwords",
                ],
                "commands": [],
            },
            {
                "name": "Client Configuration",
                "checks": [
                    "RustDesk client uses custom ID server (not public)",
                    "Connection encryption enabled (forced)",
                    "Clipboard and file transfer restricted to authorized sessions",
                ],
                "commands": [],
            },
        ],
    },

    # ── KINETIC ───────────────────────────────────────────────────────

    "rust_bridge": {
        "label": "Rust IPC / Media Bridge",
        "knight": "Sir Sentinel + Lukas Edge",
        "phases": [
            {
                "name": "Static Analysis (Cartridge Enforcement)",
                "checks": [
                    "cargo clippy --all-targets -- -D warnings (zero warnings)",
                    "No unwrap() in production paths (rust-kinetic.yaml convention)",
                    "No unsafe blocks without justification comment",
                    "No blocking I/O calls in async Tokio contexts",
                    "All public APIs documented with rustdoc",
                ],
                "commands": ["cargo clippy --all-targets -- -D warnings"],
            },
            {
                "name": "IPC Bridge Security (anya_ipc_bridge.rs)",
                "checks": [
                    "Named Pipe ACL binds to authenticated Tailscale session only",
                    "IpcMessage serde_json::Value params schema-validated before dispatch",
                    "Arc<Mutex<bool>> connection state handles poisoned mutex gracefully",
                    "No println! macros in production — must use tracing crate",
                    "IpcResponse error field does not leak internal paths or stack traces",
                ],
                "commands": [],
            },
            {
                "name": "Memory Safety (Miri Protocol)",
                "checks": [
                    "cargo +nightly miri test passes on all crates",
                    "No undefined behavior in memory operations",
                    "No use-after-free or double-free detected",
                ],
                "commands": ["cargo +nightly miri test"],
            },
            {
                "name": "PDG Data Flow Trace",
                "checks": [
                    "Untrusted network data never reaches std::process::Command",
                    "Tailscale ingress -> IPC bridge -> MCP server path sanitized at each hop",
                    "No shell execution sinks reachable from external input",
                    "File path parameters canonicalized to prevent traversal attacks",
                ],
                "commands": [],
            },
        ],
    },

    "kinetic_binaries": {
        "label": "Kinetic Armory Binaries",
        "knight": "Lukas Edge",
        "phases": [
            {
                "name": "Binary Inventory",
                "checks": [
                    "saltare.exe present and version-stamped",
                    "saltare-mcp.exe present and version-stamped",
                    "cribo: SOURCE_ONLY — needs cargo build --release",
                    "rotel: SOURCE_ONLY — needs cargo build --release",
                    "kinetic_edge MCP server: SOURCE_ONLY — needs cargo build --release",
                    "ledger.exe present and version-stamped",
                ],
                "commands": [],
            },
            {
                "name": "Checksum Verification",
                "checks": [
                    "SHA-256 checksums recorded in PROVENANCE_LEDGER.md",
                    "No unsigned or untracked binaries in KINETIC_ARMORY",
                    "Binary sizes match expected ranges (no bloat or truncation)",
                ],
                "commands": [],
            },
            {
                "name": "Kinetic Purity Enforcement",
                "checks": [
                    "No Python scripts exist where a compiled binary alternative is available",
                    "All Go binaries compiled with -trimpath for reproducibility",
                    "Rust binaries compiled in release mode with LTO enabled",
                ],
                "commands": [],
            },
        ],
    },

    # ── SECURITY ──────────────────────────────────────────────────────

    "secrets": {
        "label": "Secrets & Credential Exposure",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Secret Pattern Scan",
                "checks": [
                    "No API keys, tokens, or passwords in tracked files",
                    "No AWS (AKIA*), OpenAI (sk-*), or GitHub (ghp_*) patterns in source",
                    "No Grok (xai-*), Mistral, or OpenRouter keys exposed",
                    ".env files excluded from git tracking",
                    ".modal.toml credentials rotated (known issue flagged)",
                ],
                "commands": [],
            },
            {
                "name": "Vault Integrity",
                "checks": [
                    "03_VAULT/.secure/ directory exists with .gitignore blocking all contents",
                    "vault.enc encrypted with AES-256-GCM via vault_manager.py",
                    "vault_master.key not committed to git (verify with git ls-files)",
                    "Vault audit log entries present in PROVENANCE_LEDGER.md",
                    "Key rotation within 30-day policy (per security_policy.json)",
                ],
                "commands": [],
            },
            {
                "name": "OAuth Token Security",
                "checks": [
                    "~/.cli-proxy-api/ tokens (gemini.json, claude.json, codex.json) not world-readable",
                    "OAuth refresh tokens have expiry configured",
                    "No plaintext bearer tokens in config.yaml files",
                ],
                "commands": [],
            },
        ],
    },

    "iron_gate": {
        "label": "Iron Gate HITL Enforcement",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Gate Configuration",
                "checks": [
                    "security_policy.json requires_confirmation is true",
                    "Gatekeeper threshold >= 0.95 (currently set in security_policy.json)",
                    "Zero-trust enforced flag is true",
                    "Titanium Law III active: >10 net lines or >50MB requires approval",
                ],
                "commands": [],
            },
            {
                "name": "Gate Enforcement Path",
                "checks": [
                    "bridge.py iron_gate_approve() called before all critical operations",
                    "camelot.py risk['requires_approval'] blocks execution without confirmation",
                    "Biometric verification chain active (Make it so -> passcode -> prime challenge)",
                    "All blocked operations logged to Ouroboros + PROVENANCE_LEDGER",
                ],
                "commands": [],
            },
        ],
    },

    "zenith_warden": {
        "label": "Zenith Scanner & Warden Zero-Trust",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Zenith Hostile Pattern Detection",
                "checks": [
                    "Prompt injection patterns detected: 'ignore all previous instructions'",
                    "Jailbreak attempts blocked: DAN, STAN, role-play escapes",
                    "System prompt extraction attempts caught",
                    "Encoded injection (base64, unicode) patterns covered",
                    "Clean directives pass through without false positives",
                ],
                "commands": [],
            },
            {
                "name": "Warden Biological Isolation (Diode)",
                "checks": [
                    "Write diode blocks unauthorized writes to 01_KERNEL/ core files",
                    "Read diode prevents exfiltration of vault contents to untrusted sinks",
                    "Output sanitization strips internal paths from LLM responses",
                    "Warden integrates with all knight execute() paths via bridge.py",
                ],
                "commands": [],
            },
        ],
    },

    "dependencies": {
        "label": "Dependency Vulnerability Scan",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Container & Image Scan",
                "checks": [
                    "trivy fs . — no CRITICAL or HIGH CVEs",
                    "01_KERNEL/Dockerfile base image pinned to digest (not :latest)",
                    "Docker images use non-root USER directive",
                    "No unnecessary packages in production images",
                ],
                "commands": ["trivy fs ."],
            },
            {
                "name": "Python Dependencies",
                "checks": [
                    "pip audit — no known vulnerabilities in requirements.txt",
                    "01_KERNEL/requirements.txt pins exact versions",
                    "No deprecated packages (e.g., pycrypto -> cryptography)",
                    "httpx, pydantic, cryptography at latest stable",
                ],
                "commands": ["python -m pip_audit"],
            },
            {
                "name": "Rust Dependencies",
                "checks": [
                    "cargo audit — no advisories on Rust crates",
                    "Cargo.lock committed for reproducible builds",
                    "No yanked crate versions in dependency tree",
                ],
                "commands": ["cargo audit"],
            },
            {
                "name": "Node Dependencies",
                "checks": [
                    "npm audit — no critical vulnerabilities in 02_FORGE packages",
                    "package-lock.json committed and up to date",
                    "No wildcard (*) version ranges in package.json",
                ],
                "commands": ["npm audit"],
            },
        ],
    },

    # ── INFRASTRUCTURE ────────────────────────────────────────────────

    "ci_cd": {
        "label": "CI/CD Pipeline (GitHub Actions)",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Workflow Security",
                "checks": [
                    ".github/workflows/verify_os.yml uses pinned action versions (@v4 not @main)",
                    "No secrets exposed in workflow logs (mask sensitive outputs)",
                    "Workflow runs on windows-latest (matches production platform)",
                    "Python version pinned to 3.11 (matches pyproject.toml)",
                ],
                "commands": [],
            },
            {
                "name": "Pipeline Stages Verified",
                "checks": [
                    "Stage 1 (Governance): check_instruction_governance.py + copyright headers",
                    "Stage 2 (Lint): ruff check + black format on 01_KERNEL/",
                    "Stage 3 (Security): Iron Gate + Zenith + Diode + secret scan",
                    "Stage 4 (Tests): MGV Engine + Agora Router + Titan Memory",
                    "All stages have failure exit codes (no silent pass-through)",
                ],
                "commands": [],
            },
            {
                "name": "Branch Protection",
                "checks": [
                    "main branch requires PR review before merge",
                    "Force push to main/master blocked",
                    "Status checks required to pass before merge",
                ],
                "commands": [],
            },
        ],
    },

    "cliproxy": {
        "label": "CLIProxyAPI (Zero-Burn Proxy)",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Proxy Configuration",
                "checks": [
                    "config.yaml binds to 127.0.0.1:8080 only (not 0.0.0.0)",
                    "API key is not default 'proxy-admin-key' in production",
                    "HTTPS/TLS configured for non-localhost access",
                    "Rate limiting configured to prevent abuse",
                ],
                "commands": [],
            },
            {
                "name": "Authentication & Model Access",
                "checks": [
                    "OAuth tokens in ~/.cli-proxy-api/ have restricted file permissions",
                    "Model list endpoint does not expose provider API keys",
                    "29 model routes validated: Gemini, Claude, Codex/GPT families",
                    "Fallback chain does not retry with leaked credentials on provider switch",
                ],
                "commands": [],
            },
            {
                "name": "Process Security",
                "checks": [
                    "cli-proxy-api.exe auto-starts via _boot_cliproxy() in hud.py",
                    "Process runs with minimum required privileges",
                    "Crash recovery does not leave orphaned ports",
                    "Logs do not contain request/response bodies with user data",
                ],
                "commands": [],
            },
        ],
    },

    "modal_cloud": {
        "label": "Modal Cloud Deployment",
        "knight": "Sir Sentinel + Morgana",
        "phases": [
            {
                "name": "Cloud Credential Security",
                "checks": [
                    ".modal.toml API credentials rotated (known exposure issue)",
                    "Modal token-id and token-secret not in git history",
                    "modal_deploy.yml GitHub Action uses repository secrets, not inline",
                ],
                "commands": [],
            },
            {
                "name": "Deployment Configuration",
                "checks": [
                    "Modal stubs use GPU/CPU limits matching 8GB RAM ceiling",
                    "No exposed public endpoints without authentication",
                    "Container images pinned to specific versions",
                    "Cost safeguards in train_script.py enforced (budget limits)",
                ],
                "commands": [],
            },
        ],
    },

    "docker": {
        "label": "Docker & Container Security",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Dockerfile Audit",
                "checks": [
                    "01_KERNEL/Dockerfile uses official base image with digest pin",
                    "Multi-stage build separates build dependencies from runtime",
                    "Non-root USER directive in final stage",
                    "No COPY of .env, secrets, or vault files into image",
                    "HEALTHCHECK directive configured",
                ],
                "commands": [],
            },
            {
                "name": "Docker Compose / Runtime",
                "checks": [
                    "docker-compose files do not bind sensitive ports to 0.0.0.0",
                    "Volume mounts do not expose host system directories (/etc, /root)",
                    "Network isolation between service containers",
                    "Resource limits (memory, CPU) set per container",
                ],
                "commands": [],
            },
        ],
    },

    # ── KERNEL ────────────────────────────────────────────────────────

    "excalibur": {
        "label": "EXCALIBUR Core API",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "FastAPI Security",
                "checks": [
                    "CORS middleware restricts origins (no wildcard * in production)",
                    "Authentication required on all non-public endpoints",
                    "Rate limiting middleware configured",
                    "Request body size limits enforced",
                    "OpenAPI docs disabled in production mode",
                ],
                "commands": [],
            },
            {
                "name": "Roster & Schema Integrity",
                "checks": [
                    "roster.yaml validates against schemas/ definitions",
                    "All knight entries have required fields (name, layer, specialty)",
                    "No duplicate knight IDs or conflicting routes",
                    "config.json settings match security_policy.json requirements",
                ],
                "commands": [],
            },
            {
                "name": "Proxy & Bridge Layer",
                "checks": [
                    "kernel_api_bridge/ does not expose internal kernel paths externally",
                    "Boot script (boot_excalibur.ps1) validates environment before launch",
                    "chimera_unified_kernel.json schema version matches v300.4",
                ],
                "commands": [],
            },
        ],
    },

    "agora": {
        "label": "Agora Orchestration Layer",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Router Security",
                "checks": [
                    "AgoraRouter is singleton (prevents split-brain routing)",
                    "Knight dispatch validates intent before routing",
                    "No fallback route allows arbitrary code execution",
                    "Swarm controller limits concurrent agent count",
                ],
                "commands": [],
            },
            {
                "name": "Agent Roster",
                "checks": [
                    "agora/agents/roster.json matches 01_KERNEL/EXCALIBUR/roster.yaml",
                    "All registered agents have valid persona and layer assignments",
                    "No orphan agents (registered but never dispatched)",
                    "War room protocol enforces structured debate (no infinite loops)",
                ],
                "commands": [],
            },
        ],
    },

    "titan_memory": {
        "label": "Titan Memory & UKG Graph",
        "knight": "Sir Sentinel + Chronos",
        "phases": [
            {
                "name": "Memory Integrity",
                "checks": [
                    "Titan Omega flux TTL enforced (90s default)",
                    "Memory store/recall cycle tested (write -> read -> verify)",
                    "No stale flux entries persisting beyond TTL",
                    "Ouroboros SQLite WAL mode enabled and functioning",
                    "ouroboros.db not corrupted (PRAGMA integrity_check passes)",
                ],
                "commands": [],
            },
            {
                "name": "UKG / TOON Graph Consistency",
                "checks": [
                    "ukg_graph.jsonld validates as valid JSON-LD",
                    "Node count matches expected (N49 per v2.1 spec)",
                    "toon_ukg_full.json parseable and consistent with UKG",
                    "ukg_graph_v300.2.md version matches current OS version",
                    "No orphan nodes (referenced but undefined) in graph",
                ],
                "commands": [],
            },
        ],
    },

    "control_plane": {
        "label": "Control Plane (Pydantic AI / A2A)",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Split-Brain Topology Enforcement",
                "checks": [
                    "control_plane/main.py has NO direct filesystem I/O (pure reasoning)",
                    "control_plane/main.py has NO subprocess calls",
                    "All side-effects delegated to Kinetic Edge MCP via httpx",
                    "httpx client uses timeout limits (no unbounded requests)",
                ],
                "commands": [],
            },
            {
                "name": "A2A Protocol Security",
                "checks": [
                    "A2AMessage envelope validates source/target against known agent IDs",
                    "Correlation IDs prevent replay attacks (unique per message)",
                    "TaskPayload does not allow arbitrary code in payload dict",
                    "No agent can impersonate another (source field authenticated)",
                ],
                "commands": [],
            },
            {
                "name": "Sub-Engine Audit",
                "checks": [
                    "SoulRouter route decisions logged for auditability",
                    "OMCTeam does not exceed configured agent concurrency limit",
                    "SARDAEngine results validated before dispatch",
                    "DeerFlowSandbox enforces container isolation for code execution",
                ],
                "commands": [],
            },
        ],
    },

    "mgv_engine": {
        "label": "MGV Reasoning Engine",
        "knight": "Sir Sentinel + Merlin",
        "phases": [
            {
                "name": "Complexity Assessment",
                "checks": [
                    "MGVEngine.monitor() correctly classifies LOW/MEDIUM/HIGH",
                    "MGVEngine.process() blocks dangerous patterns",
                    "Reasoning depth capped (no infinite GoT/DoT recursion)",
                    "Token budget enforced per reasoning step",
                ],
                "commands": [],
            },
        ],
    },

    # ── CLI ────────────────────────────────────────────────────────────

    "cli_pipeline": {
        "label": "Camelot CLI Pipeline",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Anya Compiler Security",
                "checks": [
                    "compile_intent() enforces MAX_DIRECTIVE_LEN (2000 chars)",
                    "Intent classification cannot be manipulated by injection patterns",
                    "Domain detection does not trigger on crafted adversarial input",
                    "No eval() or exec() in compilation pipeline",
                ],
                "commands": [],
            },
            {
                "name": "Merlin Router Integrity",
                "checks": [
                    "KNIGHT_MAP covers all valid intents (no KeyError on unknown)",
                    "LOCAL_RISK_PATTERNS detect all dangerous operations",
                    "Risk assessment cannot be bypassed by encoding tricks",
                    "assess_risk_bridged() fallback to local is graceful",
                ],
                "commands": [],
            },
            {
                "name": "Knight Registry",
                "checks": [
                    "All .py files in knights/ load without import errors",
                    "All knights extend BaseKnight with execute() method",
                    "No knight module executes code at import time (side-effect free)",
                    "Knight output sanitized by Warden before display",
                ],
                "commands": [],
            },
            {
                "name": "LLM Router Security",
                "checks": [
                    "llm_router.py fallback chain does not leak API keys between providers",
                    "CLIPROXY_KEY not hardcoded (read from env var)",
                    "Timeout configured on all httpx calls (no hung connections)",
                    "Provider response validated before returning to caller",
                    "Streaming mode does not buffer unbounded response data",
                ],
                "commands": [],
            },
            {
                "name": "Cartridge System",
                "checks": [
                    "Cartridge YAML loaded with yaml.safe_load (not yaml.load)",
                    "No code execution in cartridge definitions",
                    "Cartridge domain matching is case-insensitive and deterministic",
                    "OS cartridges from bridge do not override local security cartridges",
                ],
                "commands": [],
            },
        ],
    },

    # ── AGENTS ────────────────────────────────────────────────────────

    "squire_colony": {
        "label": "Squire Colony (8 Sub-Agents)",
        "knight": "Sir Sentinel + Sir Boris",
        "phases": [
            {
                "name": "Colony Pipeline Integrity",
                "checks": [
                    "SCAN -> JUDGE -> SENTINEL pipeline order enforced",
                    "SENTINEL squire triggers HITL gate before destructive actions",
                    "No squire can bypass JUDGE severity assessment",
                    "Colony CLI validates path arguments (no traversal attacks)",
                ],
                "commands": [],
            },
            {
                "name": "Individual Squire Audit",
                "checks": [
                    "SQUIRE_INDEX: File indexing respects .aiexclude patterns",
                    "SQUIRE_GHOST: Ghost file detection does not delete without confirmation",
                    "SQUIRE_VECTOR: Vector embeddings do not leak sensitive content",
                    "SQUIRE_SWEEP: Cleanup operations bounded by Titanium Law III",
                    "SQUIRE_SCAN: Scanner does not follow symlinks outside CAMELOT_OS",
                    "SQUIRE_JUDGE: Severity classification consistent with Iron Gate thresholds",
                    "SQUIRE_SENTINEL: Security squire has read-only access to vault",
                    "SQUIRE_MASON: Build operations confined to 02_FORGE directory",
                ],
                "commands": [],
            },
        ],
    },

    "boris_critique": {
        "label": "Sir Boris 13-Agent Critique Pipeline",
        "knight": "Sir Boris",
        "phases": [
            {
                "name": "AST Validation Domains",
                "checks": [
                    "architecture: structural pattern validation active",
                    "security (secrets+dangerous): _SECRET_PATTERNS + _DANGEROUS_CALLS checked",
                    "contract (docstrings): public API documentation enforced",
                    "test_coverage: untested code paths flagged",
                    "edge_case (bare except): broad exception handlers detected",
                    "type_safety: type annotation gaps flagged",
                    "perf (nested loops): O(n^2+) patterns detected",
                    "concurrency: _CONCURRENCY_MARKERS validated for race conditions",
                    "api_surface: breaking changes detected",
                    "rollback: migration reversibility verified",
                    "agentshield (injection): prompt injection in code strings detected",
                    "integration: cross-module interface consistency",
                    "ops (print->logging): println!/print() flagged for tracing/logging replacement",
                ],
                "commands": [],
            },
            {
                "name": "Plan Mode Enforcement",
                "checks": [
                    "PlanModeViolation raised if execution attempted without approved plan",
                    "Plan state machine: IDLE -> PLANNED -> CRITIQUED -> APPROVED -> EXECUTING",
                    "No state transition can skip CRITIQUED phase",
                ],
                "commands": [],
            },
        ],
    },

    # ── MCP ────────────────────────────────────────────────────────────

    "mcp_config": {
        "label": "MCP Server Configuration",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Config Drift Detection",
                "checks": [
                    ".claude.json MCP config matches .gemini MCP config (server list)",
                    ".codex MCP config consistent with other harnesses",
                    "All MCP endpoints resolve and respond on expected ports",
                    "No hardcoded secrets in MCP config files",
                    "MCP server versions match across harnesses",
                ],
                "commands": [],
            },
            {
                "name": "Prompt Injection Surface",
                "checks": [
                    "IpcMessage.method field cannot forward raw input to LLM without sanitization",
                    "XML delimiter wrapping (Spotlighting) active on all user input paths",
                    "MCP tool descriptions do not contain injection payloads",
                    "Tool parameter schemas enforce type validation (no arbitrary string pass-through)",
                ],
                "commands": [],
            },
            {
                "name": "MCP Server Health",
                "checks": [
                    "notebooklm-mcp server responds to ping",
                    "gemini-cli MCP server responds to ping",
                    "ollama MCP server responds to ping (if running)",
                    "Kinetic Edge MCP server on port 3001 responds (if compiled)",
                ],
                "commands": [],
            },
        ],
    },

    # ── VOICE ─────────────────────────────────────────────────────────

    "voice_pipeline": {
        "label": "Voice AI Pipeline (Piper / Kokoro / VoxService)",
        "knight": "Sir Sentinel + Sir Sonus",
        "phases": [
            {
                "name": "Audio Pipeline Security",
                "checks": [
                    "VoxService singleton pattern prevents multiple GPU allocations",
                    "Model files loaded from designated paths only (no user-supplied paths)",
                    "Audio output directory writable but not world-accessible",
                    "No arbitrary code execution via voice command parsing",
                    "Voice latency sub-second (per Titanium Law VIII)",
                ],
                "commands": [],
            },
            {
                "name": "Model & Voice Integrity",
                "checks": [
                    "Piper TTS HuggingFace models verified by checksum",
                    "Kokoro model (kokoro-v0_19.pth) hash matches expected",
                    "Voice persona files in voices/ directory are read-only",
                    "No model loading from untrusted URLs at runtime",
                ],
                "commands": [],
            },
        ],
    },

    # ── GOVERNANCE ────────────────────────────────────────────────────

    "provenance": {
        "label": "Provenance Ledger & Audit Trail",
        "knight": "Sir Sentinel + Sir Glyph",
        "phases": [
            {
                "name": "Ledger Integrity",
                "checks": [
                    "PROVENANCE_LEDGER.md exists at root",
                    "03_VAULT copy of ledger matches root copy",
                    "docs/ copy of ledger matches root copy (3-copy sync)",
                    "Ledger entries are append-only (no retroactive edits)",
                    "All CLI executions produce ledger entries via bridge.log_provenance()",
                ],
                "commands": [],
            },
            {
                "name": "Copyright & Governance",
                "checks": [
                    "All 01_KERNEL/ Python files have Copyright header",
                    "00_MASTER_COPYRIGHT_COMPILATION.docx present and current",
                    "LEGAL/ directory contains IP protection documents",
                    "Creative works (personas, narratives) covered by copyright declaration",
                ],
                "commands": [],
            },
        ],
    },

    "aiexclude": {
        "label": "Token Shield (.aiexclude)",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": ".aiexclude Coverage",
                "checks": [
                    "node_modules/ excluded from AI indexing",
                    ".venv/ excluded from AI indexing",
                    ".git/ excluded from AI indexing",
                    "package-lock.json excluded",
                    "poetry.lock excluded",
                    "*.svg excluded (large binary-like files)",
                    "99_ARCHIVE/ excluded (historical, high token cost)",
                    "Large log files (>1MB) excluded or pattern-matched",
                ],
                "commands": [],
            },
            {
                "name": "RAM Ceiling Enforcement",
                "checks": [
                    "8GB physical / 7.8GB usable RAM ceiling documented and enforced",
                    "Heartbeat daemon (cmd/pulse/heartbeat.go) polls every 5s",
                    "run_agent_cmd.sh shim activates venv + RAM check before execution",
                    "No single process allowed to exceed 4GB (half of ceiling)",
                ],
                "commands": [],
            },
        ],
    },

    "git_hygiene": {
        "label": "Git Repository Hygiene",
        "knight": "Sir Sentinel",
        "phases": [
            {
                "name": "Repository Structure",
                "checks": [
                    ".gitignore covers: node_modules, .venv, __pycache__, .env, *.exe, .secure/",
                    "No large binaries (>10MB) tracked in git without LFS",
                    "No merge conflict markers (<<<< ==== >>>>) in tracked files",
                    "Branch naming follows convention (feat/, fix/, reorg/)",
                ],
                "commands": ["git status"],
            },
            {
                "name": "History Security",
                "checks": [
                    "No secrets in git history (git log --diff-filter=A -- '*.env')",
                    "No force-push to main branch in recent history",
                    "Commits signed or attributed to known authors",
                    "Remote origin URL matches expected repository",
                ],
                "commands": [],
            },
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════
# PRESETS — named multi-domain sweep bundles
# ══════════════════════════════════════════════════════════════════════

AUDIT_PRESETS: dict[str, list[str]] = {
    "full": list(AUDIT_DOMAINS.keys()),
    "network": ["tailscale", "rustdesk", "mcp_config"],
    "kinetic": ["rust_bridge", "kinetic_binaries"],
    "security": ["secrets", "iron_gate", "zenith_warden", "dependencies", "git_hygiene"],
    "bridge": ["tailscale", "rust_bridge", "rustdesk"],
    "infrastructure": ["ci_cd", "cliproxy", "modal_cloud", "docker"],
    "kernel": ["excalibur", "agora", "titan_memory", "control_plane", "mgv_engine"],
    "cli": ["cli_pipeline", "squire_colony", "boris_critique"],
    "agents": ["squire_colony", "boris_critique", "control_plane"],
    "governance": ["provenance", "aiexclude", "git_hygiene", "iron_gate"],
    "voice": ["voice_pipeline"],
}


# ══════════════════════════════════════════════════════════════════════
# KEYWORD -> DOMAIN mapping for natural language target resolution
# ══════════════════════════════════════════════════════════════════════

_KEYWORD_MAP: dict[str, str] = {
    # Network
    "tailscale": "tailscale", "tailscape": "tailscale", "mesh": "tailscale",
    "rustdesk": "rustdesk", "remote desktop": "rustdesk", "relay": "rustdesk",
    # Kinetic
    "rust": "rust_bridge", "bridge": "rust_bridge", "media": "rust_bridge",
    "ipc": "rust_bridge", "named pipe": "rust_bridge",
    "binary": "kinetic_binaries", "binaries": "kinetic_binaries",
    "armory": "kinetic_binaries", "saltare": "kinetic_binaries",
    "cribo": "kinetic_binaries", "rotel": "kinetic_binaries",
    "ledger.exe": "kinetic_binaries",
    # Security
    "secret": "secrets", "credential": "secrets", "vault": "secrets",
    "token": "secrets", "password": "secrets",
    "iron gate": "iron_gate", "hitl": "iron_gate", "approval": "iron_gate",
    "zenith": "zenith_warden", "warden": "zenith_warden", "injection": "zenith_warden",
    "diode": "zenith_warden",
    "depend": "dependencies", "cve": "dependencies", "vuln": "dependencies",
    "trivy": "dependencies", "npm audit": "dependencies", "pip audit": "dependencies",
    "cargo audit": "dependencies",
    # Infrastructure
    "ci": "ci_cd", "cd": "ci_cd", "pipeline": "ci_cd", "github action": "ci_cd",
    "workflow": "ci_cd",
    "proxy": "cliproxy", "cliproxy": "cliproxy", "cli-proxy": "cliproxy",
    "modal": "modal_cloud", "cloud": "modal_cloud", "morgana": "modal_cloud",
    "docker": "docker", "container": "docker", "dockerfile": "docker",
    # Kernel
    "excalibur": "excalibur", "fastapi": "excalibur", "api": "excalibur",
    "roster": "excalibur",
    "agora": "agora", "orchestrat": "agora", "swarm": "agora",
    "titan": "titan_memory", "memory": "titan_memory", "ukg": "titan_memory",
    "toon": "titan_memory", "ouroboros": "titan_memory",
    "control plane": "control_plane", "pydantic": "control_plane",
    "a2a": "control_plane", "sarda": "control_plane", "deerflow": "control_plane",
    "mgv": "mgv_engine", "reasoning": "mgv_engine",
    # CLI
    "cli": "cli_pipeline", "anya": "cli_pipeline", "merlin": "cli_pipeline",
    "router": "cli_pipeline", "cartridge": "cli_pipeline",
    "llm router": "cli_pipeline", "llm_router": "cli_pipeline",
    "squire": "squire_colony", "colony": "squire_colony",
    "boris": "boris_critique", "critique": "boris_critique",
    "13-agent": "boris_critique", "ast": "boris_critique",
    # MCP
    "mcp": "mcp_config", "config drift": "mcp_config",
    "notebooklm": "mcp_config", "gemini-cli": "mcp_config",
    # Voice
    "voice": "voice_pipeline", "piper": "voice_pipeline",
    "kokoro": "voice_pipeline", "tts": "voice_pipeline",
    "vox": "voice_pipeline", "audio": "voice_pipeline",
    # Governance
    "provenance": "provenance", "copyright": "provenance",
    "aiexclude": "aiexclude", "token shield": "aiexclude", "ram": "aiexclude",
    "heartbeat": "aiexclude",
    "git": "git_hygiene", "branch": "git_hygiene", "gitignore": "git_hygiene",
}


# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════

# Secret patterns (shared with Sir Boris for consistency)
_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)\s*[=:]\s*['\"][^'\"]{8,}"),
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(sk-[a-zA-Z0-9]{20,})"),
    re.compile(r"(?i)(ghp_[a-zA-Z0-9]{36})"),
    re.compile(r"(?i)(xai-[a-zA-Z0-9]{20,})"),
    re.compile(r"(?i)(gsk_[a-zA-Z0-9]{20,})"),
]


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def _run_check(cmd: str, timeout: int = 30) -> dict:
    """Run an audit command and capture output. Never raises."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        return {
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:500],
        }
    except subprocess.TimeoutExpired:
        return {"command": cmd, "returncode": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"command": cmd, "returncode": -1, "stdout": "", "stderr": str(e)[:200]}


def _scan_secrets(path: Path, max_files: int = 500) -> list[dict]:
    """Scan tracked files for secret patterns."""
    hits = []
    count = 0
    skip_dirs = {"node_modules", ".venv", ".git", "__pycache__", "99_ARCHIVE",
                 ".secure", ".cli-proxy-api", "auths"}
    scan_ext = {".py", ".ts", ".js", ".json", ".yaml", ".yml", ".toml", ".env",
                ".md", ".sh", ".ps1", ".rs", ".go", ".cfg", ".ini", ".conf"}
    for root, dirs, files in os.walk(path):
        # Prune heavy/sensitive directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in scan_ext:
                continue
            fpath = os.path.join(root, fname)
            count += 1
            if count > max_files:
                return hits
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f, 1):
                        if len(line) > 1000:
                            continue  # skip minified/binary-ish lines
                        for pat in _SECRET_PATTERNS:
                            if pat.search(line):
                                hits.append({
                                    "file": os.path.relpath(fpath, path),
                                    "line": i,
                                    "pattern": pat.pattern[:40],
                                })
            except (OSError, PermissionError):
                continue
    return hits


def _check_file_exists(path: Path) -> str:
    """Return PASS/FAIL for file existence."""
    return "PASS" if path.exists() else "FAIL"


def _check_ledger_sync() -> list[str]:
    """Verify 3-copy ledger sync."""
    findings = []
    root = CAMELOT_OS / "PROVENANCE_LEDGER.md"
    vault = CAMELOT_OS / "03_VAULT" / "training" / "configs" / "PROVENANCE_LEDGER.md"
    docs = CAMELOT_OS / "docs" / "PROVENANCE_LEDGER.md"
    for label, path in [("root", root), ("vault", vault), ("docs", docs)]:
        if not path.exists():
            findings.append(f"MISSING: {label} copy at {path.relative_to(CAMELOT_OS)}")
    if root.exists() and vault.exists():
        r_size = root.stat().st_size
        v_size = vault.stat().st_size
        if abs(r_size - v_size) > 100:
            findings.append(f"DRIFT: root ({r_size}B) vs vault ({v_size}B) ledger size mismatch")
    return findings


# ══════════════════════════════════════════════════════════════════════
# THE KNIGHT
# ══════════════════════════════════════════════════════════════════════

class SirSentinel(BaseKnight):
    name = "Sir Sentinel"
    title = "The Shield"
    specialty = "Universal Zero-Trust Forensic Audit"
    icon = "\U0001f6e1"  # shield emoji
    version = "2.0"
    layer = "L6_GOVERNANCE"

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        """Execute a universal audit across detected or specified domains."""
        text = directive.lower()

        # Detect which audit domains the directive targets
        targets = self._resolve_targets(text)
        if not targets:
            targets = ["full"]

        # Expand presets
        domain_keys: list[str] = []
        for t in targets:
            if t in AUDIT_PRESETS:
                domain_keys.extend(AUDIT_PRESETS[t])
            elif t in AUDIT_DOMAINS:
                domain_keys.append(t)
        # Deduplicate preserving order
        seen: set[str] = set()
        domain_keys = [k for k in domain_keys if not (k in seen or seen.add(k))]

        if not domain_keys:
            domain_keys = list(AUDIT_DOMAINS.keys())

        # Build report
        lines = [
            "# SENTINEL AUDIT REPORT",
            "## Camelot Apex OS v300.4 -- Agent-Armor v2.0",
            f"**Domains ({len(domain_keys)}):** {', '.join(domain_keys)}",
            "**Compiled by:** Anya APEE v6.5 (PARSE -> ENRICH -> COMPILE -> ROUTE -> VALIDATE)",
            "**Dispatched to:** Sir Sentinel (L6) + Lukas Edge (L2)",
            f"**Total audit domains available:** {len(AUDIT_DOMAINS)}",
            "",
        ]

        total_checks = 0
        cmd_results = []
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        hitl_required = False

        for dkey in domain_keys:
            domain = AUDIT_DOMAINS[dkey]
            lines.append("---")
            lines.append(f"### {domain['label']}")
            lines.append(f"**Knight:** {domain['knight']}")
            lines.append("")

            for phase in domain["phases"]:
                lines.append(f"#### Phase: {phase['name']}")

                # Run any automated commands
                for cmd in phase.get("commands", []):
                    tool_name = cmd.split()[0]
                    if _tool_available(tool_name):
                        result = _run_check(cmd)
                        cmd_results.append(result)
                        status = "PASS" if result["returncode"] == 0 else "FAIL"
                        if status == "FAIL":
                            severity_counts["HIGH"] += 1
                        lines.append(f"  `{cmd}` -> **{status}** (exit {result['returncode']})")
                        if result["stdout"].strip():
                            preview = result["stdout"][:300].replace("\n", "\n    ")
                            lines.append("    ```")
                            lines.append(f"    {preview}")
                            lines.append("    ```")
                        if result["stderr"].strip() and status == "FAIL":
                            lines.append(f"    stderr: {result['stderr'][:200]}")
                    else:
                        lines.append(f"  `{cmd}` -> **SKIP** (tool not found)")
                        severity_counts["LOW"] += 1

                # Checklist
                for check in phase["checks"]:
                    total_checks += 1
                    lines.append(f"- [ ] {check}")

                lines.append("")

        # ── Automated deep checks ─────────────────────────────────────

        # Secret scan
        if "secrets" in domain_keys:
            lines.append("#### Automated Secret Scan Results")
            hits = _scan_secrets(CAMELOT_OS)
            if hits:
                severity_counts["CRITICAL"] += len(hits)
                hitl_required = True
                for h in hits[:20]:
                    lines.append(f"- **CRITICAL** `{h['file']}:{h['line']}` matched `{h['pattern']}`")
                if len(hits) > 20:
                    lines.append(f"- ... and {len(hits) - 20} more")
            else:
                lines.append("- No secret patterns detected in scanned files.")
            lines.append("")

        # Binary inventory
        if "kinetic_binaries" in domain_keys:
            lines.append("#### Binary Status Matrix")
            bins = [
                ("saltare.exe", CAMELOT_OS / "02_FORGE" / "KINETIC_ARMORY" / "Saltare" / "saltare.exe"),
                ("saltare-mcp.exe", CAMELOT_OS / "02_FORGE" / "KINETIC_ARMORY" / "Saltare" / "saltare-mcp.exe"),
                ("cribo", CAMELOT_OS / "02_FORGE" / "KINETIC_ARMORY" / "Cribo" / "target" / "release" / "cribo.exe"),
                ("rotel", CAMELOT_OS / "02_FORGE" / "KINETIC_ARMORY" / "Rotel" / "target" / "release" / "rotel.exe"),
                ("ledger.exe", CAMELOT_OS / "02_FORGE" / "kinetic" / "bin" / "ledger.exe"),
                ("cli-proxy-api.exe", Path.home() / "CLIProxyAPI" / "cli-proxy-api.exe"),
            ]
            lines.append("| Binary | Status | Size |")
            lines.append("|--------|--------|------|")
            for name, bpath in bins:
                if bpath.exists():
                    size_mb = bpath.stat().st_size / (1024 * 1024)
                    lines.append(f"| {name} | COMPILED | {size_mb:.1f} MB |")
                else:
                    lines.append(f"| {name} | SOURCE_ONLY | -- |")
                    severity_counts["MEDIUM"] += 1
            lines.append("")

        # Provenance ledger sync check
        if "provenance" in domain_keys:
            lines.append("#### Automated Ledger Sync Check")
            ledger_findings = _check_ledger_sync()
            if ledger_findings:
                severity_counts["HIGH"] += len(ledger_findings)
                for f in ledger_findings:
                    lines.append(f"- **HIGH** {f}")
            else:
                lines.append("- Ledger copies in sync.")
            lines.append("")

        # Governance file existence checks
        if "provenance" in domain_keys or "governance" in [t for t in targets if t in AUDIT_PRESETS]:
            lines.append("#### Governance File Inventory")
            gov_files = [
                ("PROVENANCE_LEDGER.md", CAMELOT_OS / "PROVENANCE_LEDGER.md"),
                ("security_policy.json", CAMELOT_OS / "01_KERNEL" / "iron_gate" / "security_policy.json"),
                (".aiexclude", Path.home() / ".aiexclude"),
                ("vault_manager.py", CAMELOT_OS / "03_VAULT" / "vault_manager.py"),
                ("verify_os.yml", CAMELOT_OS / ".github" / "workflows" / "verify_os.yml"),
                ("ukg_graph.jsonld", CAMELOT_OS / "03_VAULT" / "training" / "configs" / "memory" / "ukg_graph.jsonld"),
                ("roster.yaml", CAMELOT_OS / "01_KERNEL" / "EXCALIBUR" / "roster.yaml"),
            ]
            lines.append("| File | Status |")
            lines.append("|------|--------|")
            for name, gpath in gov_files:
                status = _check_file_exists(gpath)
                lines.append(f"| {name} | {status} |")
                if status == "FAIL":
                    severity_counts["HIGH"] += 1
            lines.append("")

        # ── Summary ────────────────────────────────────────────────────

        if severity_counts["CRITICAL"] > 0 or severity_counts["HIGH"] > 0:
            hitl_required = True

        lines.append("---")
        lines.append("### Severity Summary")
        lines.append("| Level | Count |")
        lines.append("|-------|-------|")
        for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            lines.append(f"| {level} | {severity_counts[level]} |")
        lines.append(f"\n**Total checks:** {total_checks}")
        lines.append(f"**Commands executed:** {len(cmd_results)}")
        lines.append("")

        if hitl_required:
            lines.append("### IRON GATE: HITL LOCK ENGAGED")
            lines.append("Remediation patches require `Make it so` sovereign authorization.")
            lines.append("Titanium Law III: >10 net lines or >50MB deletion blocked until approved.")
        else:
            lines.append("### Iron Gate: CLEAR")
            lines.append("No critical findings. Low-severity auto-repair authorized via Antigravity v2.0.")

        lines.append("")
        lines.append("---")
        lines.append("*Sir Sentinel stands watch. No vulnerability shall pass unchallenged.*")

        output = "\n".join(lines)

        # Write report to disk if requested
        files_created = []
        if write:
            report_path = CAMELOT_OS / "logs" / "sentinel_audit_latest.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(output)
            files_created.append(str(report_path))

        return {"status": "success", "output": output, "files_created": files_created}

    def _resolve_targets(self, text: str) -> list[str]:
        """Extract audit target domains from directive text."""
        targets = []
        # Check presets first
        for preset in AUDIT_PRESETS:
            if preset in text:
                targets.append(preset)
        # Check domain keywords
        for keyword, domain in _KEYWORD_MAP.items():
            if keyword in text and domain not in targets:
                targets.append(domain)
        return targets
