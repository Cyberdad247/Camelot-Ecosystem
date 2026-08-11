from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "docs" / "plans" / "camelot-cloudbrain-v701"
RUNTIME_DIR = ROOT / "03_VAULT" / "runtime_state"
MANIFEST_PATH = RUNTIME_DIR / "camelot_cloudbrain_v701_manifest.json"
WARP_WORKFLOW_PATH = ROOT / ".warp" / "workflows" / "camelot-cloudbrain-v701-sync.yaml"
ROSTER_JSON = ROOT / "01_KERNEL" / "agora" / "agents" / "roster.json"
EXCALIBUR_ROSTER = ROOT / "01_KERNEL" / "EXCALIBUR" / "roster.yaml"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return fallback
    return yaml.safe_load(path.read_text(encoding="utf-8")) or fallback


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_terminals() -> list[dict[str, Any]]:
    from control_plane.dispatch.switchboard import TERMINAL_REGISTRY

    terminals: list[dict[str, Any]] = []
    for terminal in TERMINAL_REGISTRY.values():
        payload = asdict(terminal)
        payload["capability"] = ", ".join(payload.get("capability") or [])
        terminals.append(payload)
    return sorted(terminals, key=lambda item: item["id"])


def load_soul_router() -> dict[str, Any]:
    from control_plane.core import soul_router

    return {
        "equation": "S_omega = 0.20*V + 0.35*M + 0.30*P + 0.15*E",
        "dimensions": {
            "V": "velocity / urgency",
            "M": "magnitude / task scope",
            "P": "privacy / sensitivity",
            "E": "environment / engine fit",
        },
        "weights": {weight.name: float(weight.value) for weight in soul_router.EngineWeight},
        "foundry_council": [
            {
                "knight_id": engine.knight_id,
                "engine": engine.engine,
                "weight": engine.weight.name,
                "weight_value": float(engine.weight.value),
                "function": engine.function,
                "privacy_level": engine.privacy_level,
            }
            for engine in soul_router.FOUNDRY_COUNCIL
        ],
        "omni_provider_map": soul_router.OMNI_PROVIDER_MAP,
        "privacy_keywords": sorted(soul_router.PRIVACY_KEYWORDS),
    }


def load_roster() -> dict[str, Any]:
    roster = read_json(ROSTER_JSON, {"agents": []})
    excalibur = read_yaml(EXCALIBUR_ROSTER, {"agents": []})
    return {
        "agora_agents": roster.get("agents", []),
        "excalibur_agents": excalibur.get("agents", []),
        "agora_count": len(roster.get("agents", [])),
        "excalibur_count": len(excalibur.get("agents", [])),
    }


def architecture_layers() -> list[dict[str, str]]:
    return [
        {
            "layer": "L7 Ethereal Interface",
            "owner": "Anya",
            "purpose": "Compile raw human intent into kernel-ready tasks through Triple-QFT and context compression.",
            "source": "01_KERNEL/titan/memory/compiler.py",
        },
        {
            "layer": "L6 Governance",
            "owner": "Arthur / Sir Zenith / Lady Veritas",
            "purpose": "Enforce Iron Gate, provenance, Titanium Law, credential safety, and audit boundaries.",
            "source": "control_plane/ledger_sync.py; 01_KERNEL/iron_gate",
        },
        {
            "layer": "L5 Agentic Swarm",
            "owner": "Merlin / Foundry Council",
            "purpose": "Route work to Knights and harnesses using Switchboard, Soul Router, SARDA, and DKS hot pools.",
            "source": "control_plane/switchboard.py; control_plane/soul_router.py; control_plane/dks_manager.py",
        },
        {
            "layer": "L4 Semantic Memory",
            "owner": "Sir Mnemo / Lady Alexandria",
            "purpose": "Persist UKG, Symbolect, NotebookLM Cloud Brain notes, vector memory, and runtime ledgers.",
            "source": "03_VAULT/UKG; control_plane/cloudbrain_sync.py",
        },
        {
            "layer": "L3 Merlin Reasoning Kernel",
            "owner": "Merlin",
            "purpose": "Execute UKG runtime, distill-anchor-weave loops, Symbolect compression, and model-lowering payloads.",
            "source": "01_KERNEL/merlin/Engines/ukg_runtime.py",
        },
        {
            "layer": "L2 Kinetic Execution",
            "owner": "Lukas",
            "purpose": "Run local write/build/test/scan actions through CLI, Rust, Go, Nano-Knights, and guarded wrappers.",
            "source": "02_FORGE; 03_VAULT/Nano-Knights",
        },
        {
            "layer": "L1 Substrate / Watchtower",
            "owner": "Morgana / Sir Sentinel",
            "purpose": "Probe ports, enforce resource ceilings, bridge local services, and keep the command plane observable.",
            "source": "01_KERNEL/iron_gate/watchtower.py; control_plane/boot_sequence.py",
        },
    ]


def schematic_edges() -> list[dict[str, str]]:
    return [
        {"from": "User / Warp / CLI", "to": "camelot.exe", "contract": "prompt-first command intake"},
        {"from": "camelot.exe", "to": "Anya compiler", "contract": "intent normalization and ambiguity reduction"},
        {"from": "Anya compiler", "to": "Soul Router", "contract": "tensor scoring by velocity, magnitude, privacy, environment"},
        {"from": "Soul Router", "to": "Switchboard", "contract": "terminal capability and health-aware dispatch"},
        {"from": "Switchboard", "to": "Knight / Harness", "contract": "engine-specific execution or planning"},
        {"from": "Knight / Harness", "to": "Ledger", "contract": "hashable operational provenance"},
        {"from": "Ledger", "to": "Cloud Brain queue", "contract": "best-effort NotebookLM sync event"},
        {"from": "Cloud Brain queue", "to": "NotebookLM", "contract": "canonical memory snapshot when endpoint is reachable"},
        {"from": "Watchtower", "to": "Boot Matrix", "contract": "resource, service, and defense-grid health"},
        {"from": "Warp workflow", "to": "camelot.exe", "contract": "repeatable operator cockpit commands"},
    ]


def symbolact_dictionary() -> list[dict[str, str]]:
    return [
        {"token": "Symbolact", "meaning": "Action-bearing symbolic command: a compact token that tells Camelot what to do and why.", "source": "v701 alias for Symbolect action dictionary"},
        {"token": "Symbolect", "meaning": "Camelot symbolic compression layer for logic, prompts, routing, and A2A packets.", "source": "01_KERNEL/merlin/Engines/symbolect_transpiler/symbolect.py"},
        {"token": "UKG", "meaning": "Universal Knowledge Glyph; structured compressed memory that can survive context limits.", "source": "01_KERNEL/merlin/Engines/ukg_runtime.py"},
        {"token": "TOON_v2", "meaning": "Token-oriented object notation for dense agent output and persona manifests.", "source": "01_KERNEL/protocols/knight_evolution_protocol.md"},
        {"token": "S_omega", "meaning": "Soul Router score used to select the best Knight engine for an intent.", "source": "control_plane/soul_router.py"},
        {"token": "V", "meaning": "Velocity: urgency or time pressure component in S_omega.", "source": "control_plane/soul_router.py"},
        {"token": "M", "meaning": "Magnitude: scope and complexity component in S_omega.", "source": "control_plane/soul_router.py"},
        {"token": "P", "meaning": "Privacy: sensitivity component that can force local or air-gapped routing.", "source": "control_plane/soul_router.py"},
        {"token": "E", "meaning": "Environment: engine-fit component based on the active routing matrix.", "source": "control_plane/soul_router.py"},
        {"token": "DKS", "meaning": "Dynamic Knight Swapping; keeps only a small hot pool of Knight context in RAM.", "source": "control_plane/dks_manager.py"},
        {"token": "Iron Gate", "meaning": "Human-in-the-loop and policy boundary for risky kinetic operations.", "source": "01_KERNEL/iron_gate"},
        {"token": "Watchtower", "meaning": "Resource, process, kingdom-status, and governor monitoring surface.", "source": "01_KERNEL/iron_gate/watchtower.py"},
        {"token": "Cloud Brain", "meaning": "NotebookLM-backed long-term memory and canonical sync surface.", "source": "control_plane/cloudbrain_sync.py"},
        {"token": "Ledger is Law", "meaning": "Every meaningful Camelot mutation must be recorded and reconcilable.", "source": "PROVENANCE_LEDGER.md"},
        {"token": "ASSIMILATE", "meaning": "Classify an external project or file into keep, compress, stage, or purge lanes.", "source": "docs/reference/LEGAL/MASTER_GLOSSARY.md"},
        {"token": "Nano-Knight", "meaning": "Small local utility worker for fast scanning, patching, compression, or verification.", "source": "03_VAULT/Nano-Knights"},
        {"token": "Bio-Swarm", "meaning": "Domain-cartridge team mode for research, coding, security, voice, or interface work.", "source": "01_KERNEL/agora/swarms"},
        {"token": "Lukas Verify", "meaning": "Local evidence pass: file existence, ledger status, queue status, and command output.", "source": "current v701 protocol"},
    ]


def classify_project(name: str, path: Path) -> dict[str, str]:
    lower = name.lower()
    role = "reference or staged integration"
    owner = "Sir Liberte"
    verify = f"Test-Path {rel(path)}"
    integration = "reference"
    status = "assimilated" if path.exists() else "missing"
    caveat = "Validate upstream license and active runtime need before deeper coupling."

    if lower in {"claw-code-agent", "pi-mono", "jcode"}:
        role, owner, integration = "agentic CLI harness", "Sir Codex / Sir Pi", "harness"
        verify = "camelot team self-test --target harness_codex --require-pass"
    elif lower in {"cribo"}:
        role, owner, integration = "context compression and AST-aware bundling", "Lukas / Sir Mason", "kinetic"
    elif lower in {"goose", "hermes-agent"}:
        role, owner, integration = "agent orchestration and courier workflows", "Sir Hermes / Sir Link", "harness"
    elif lower in {"lightpanda", "lightpanda-browser"}:
        role, owner, integration = "headless browser and lightweight web automation", "Lady Apis / Sir Castor", "browser"
    elif lower == "livekit":
        role, owner, integration = "voice transport for Camelot receptionist and cockpit", "Sir Sonus / Tasha Prime", "voice"
    elif lower == "mcp_web_search":
        role, owner, integration = "MCP search bridge and research foraging", "Lady Apis", "mcp"
    elif lower == "spacetimedb":
        role, owner, integration = "real-time state substrate candidate", "Morgana / Sir Link", "substrate"
    elif lower in {"tiny-tts", "vibevoice"}:
        role, owner, integration = "local or low-cost text-to-speech", "Sir Sonus", "voice"
    elif lower in {"openclaw", "omni-eye-dashboard", "obsidian-spire-hud"}:
        role, owner, integration = "Camelot cockpit and dashboard surface", "Anya / Sir Stitch", "ui"
        verify = "npm run verify"
    elif lower in {"luxora-prestige", "anya-lyte"}:
        role, owner, integration = "Forge app surface with separate product workflows", "Sir Gareth / Sir Syntax", "app"
    elif lower == "excalibur":
        role, owner, integration = "Merlin kernel, shared Symbolect, A2A, and roster base", "Merlin", "kernel"
        verify = "camelot team roster"
    elif lower in {"nano-knights"}:
        role, owner, integration = "local phials and utility workers", "Lukas", "kinetic"
    elif lower in {"rag"}:
        role, owner, integration = "retrieval and long-context memory lane", "Sir Mnemo", "memory"
    elif lower in {"titan"}:
        role, owner, integration = "Anya compiler, memory compiler, prompt compression", "Anya", "memory"
    elif lower in {"defense_grid"}:
        role, owner, integration = "active defense policy and Watchtower config", "Sir Sentinel", "defense"
    elif lower in {"swarms"}:
        role, owner, integration = "Bio-team and swarm execution cartridges", "Merlin / Lady Apis", "swarm"

    return {
        "project": name,
        "path": rel(path),
        "role": role,
        "integration_type": integration,
        "owner_knight": owner,
        "source_of_truth": rel(path),
        "verification_command": verify,
        "status": status,
        "risk_or_caveat": caveat,
        "v701_action": "Register in Cloud Brain v701 journal, preserve source path, and use ledger-backed changes only.",
    }


def discover_projects() -> list[dict[str, str]]:
    projects: list[tuple[str, Path]] = [
        ("EXCALIBUR", ROOT / "01_KERNEL" / "EXCALIBUR"),
        ("Nano-Knights", ROOT / "03_VAULT" / "Nano-Knights"),
        ("rag", ROOT / "01_KERNEL" / "merlin" / "rag"),
        ("titan", ROOT / "01_KERNEL" / "titan"),
        ("swarms", ROOT / "01_KERNEL" / "agora" / "swarms"),
        ("DEFENSE_GRID", ROOT / "01_KERNEL" / "iron_gate" / "DEFENSE_GRID"),
    ]
    for parent in [
        ROOT / "02_FORGE" / "KINETIC_ARMORY",
        ROOT / "02_FORGE" / "apps",
        ROOT / "02_FORGE" / "tools",
    ]:
        if parent.exists():
            projects.extend((child.name, child) for child in sorted(parent.iterdir()) if child.is_dir())

    seen: set[str] = set()
    journal: list[dict[str, str]] = []
    for name, path in projects:
        key = rel(path).lower()
        if key in seen:
            continue
        seen.add(key)
        journal.append(classify_project(name, path))
    return sorted(journal, key=lambda item: (item["integration_type"], item["project"].lower()))


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        cleaned = [str(cell).replace("\n", " ").replace("|", "/") for cell in row]
        lines.append("| " + " | ".join(cleaned) + " |")
    return "\n".join(lines)


def write_engine_architecture(manifest: dict[str, Any]) -> None:
    rows = [
        [layer["layer"], layer["owner"], layer["purpose"], layer["source"]]
        for layer in manifest["architecture_layers"]
    ]
    terminal_rows = [
        [t["id"], t["engine"], t["weight"], t["cost_tier"], t["capability"], t["probe_port"], t["notes"]]
        for t in manifest["switchboard_terminals"]
    ]
    council_rows = [
        [c["knight_id"], c["engine"], c["weight"], c["weight_value"], c["privacy_level"], c["function"]]
        for c in manifest["soul_router"]["foundry_council"]
    ]
    body = f"""# Camelot-OS v701 Engine Architecture

Generated: {manifest["generated_utc"]}

## Source Contract

This v701 package treats the live repository as the source of truth. It pulls the Switchboard terminal registry, Soul Router weights, DKS roster count, Watchtower contract, Symbolect runtime, open-source project inventory, and Cloud Brain sync path into a single NotebookLM-ready architecture map.

## Seven-Layer Engine Stack

{table(["Layer", "Owner", "Purpose", "Source"], rows)}

## Routing Math

`{manifest["soul_router"]["equation"]}`

{table(["Dimension", "Meaning"], [[k, v] for k, v in manifest["soul_router"]["dimensions"].items()])}

## Immutable Engine Weights

{table(["Weight", "Value"], [[k, v] for k, v in manifest["soul_router"]["weights"].items()])}

## Foundry Council

{table(["Knight", "Engine", "Weight", "Value", "Privacy", "Function"], council_rows)}

## Switchboard Terminals

{table(["Terminal", "Engine", "Weight", "Cost", "Capability", "Port", "Notes"], terminal_rows)}

## DKS Memory Law

- Assembly count from the Excalibur roster: `{manifest["roster"]["excalibur_count"]}`.
- Agora roster count: `{manifest["roster"]["agora_count"]}`.
- Hot-pool rule: at most 5 active Knight contexts in RAM.
- RAM ceiling: 8 GB local Titanium Law.

## Cloud Brain v701 Rule

Architecture changes must land in the local docs and runtime manifest first, then ledger, then Cloud Brain queue/sync. NotebookLM is the memory surface; the repo remains the executable source of truth.
"""
    (OUTPUT_DIR / "ENGINE_ARCHITECTURE.md").write_text(body, encoding="utf-8")


def write_schematics(manifest: dict[str, Any]) -> None:
    edge_rows = [[e["from"], e["to"], e["contract"]] for e in manifest["schematic_edges"]]
    body = f"""# Camelot-OS v701 Schematics

Generated: {manifest["generated_utc"]}

## Control Flow Schematic

{table(["From", "To", "Contract"], edge_rows)}

## Mermaid Flow

```mermaid
flowchart TD
  U[User / Warp / CLI] --> C[camelot.exe]
  C --> A[Anya Intent Compiler]
  A --> R[Soul Router]
  R --> S[Switchboard]
  S --> K[Knight / Harness]
  K --> L[Provenance Ledger]
  L --> Q[Cloud Brain Queue]
  Q --> N[NotebookLM Cloud Brain]
  W[Watchtower] --> B[Boot Matrix]
  B --> C
```

## Execution Contract

1. Every operator action starts from `camelot.exe`, Warp workflow, dashboard, or a known harness.
2. Anya compresses intent before Merlin routes.
3. Soul Router scores the work and Switchboard checks terminal fitness.
4. A Knight, harness, or local engine executes only inside its declared lane.
5. Ledger records the mutation.
6. Cloud Brain sync preserves the memory snapshot or queues it when the endpoint is unreachable.

## Watchtower / Defense Schematic

```mermaid
flowchart LR
  P[Process] --> WT[Watchtower]
  WT --> GOV[Governor Check]
  GOV --> RAM[RAM Limit]
  GOV --> CPU[CPU Limit]
  GOV --> IG[Iron Gate Broadcast]
  IG --> LEDGER[Ledger Evidence]
```
"""
    (OUTPUT_DIR / "SCHEMATICS.md").write_text(body, encoding="utf-8")


def write_symbolact_dictionary(manifest: dict[str, Any]) -> None:
    rows = [[item["token"], item["meaning"], item["source"]] for item in manifest["symbolact_dictionary"]]
    body = f"""# Symbolact Dictionary for Camelot-OS v701

Generated: {manifest["generated_utc"]}

`Symbolact` is the v701 operator-facing name for an action-bearing Symbolect token. In plain terms: a Symbolact is a short symbol, word, or command that carries both meaning and an expected action.

{table(["Token", "Meaning", "Source"], rows)}

## Canonical Symbolect Operators

{table(["Operator", "Meaning"], [
    ["->", "implies"],
    ["<-", "derived_from"],
    ["==", "equivalent_to"],
    ["!=", "not_equivalent_to"],
    ["&&", "and"],
    ["||", "or"],
    [">>", "process_flow_to"],
    ["<<", "process_flow_from"],
    ["[?]", "query"],
    ["[!]", "alert"],
    ["[*]", "insight"],
    ["[@]", "reference"],
    ["{...}", "context_block"],
    ["<...>", "variable"],
    ["#", "entity_tag"],
])}

## v701 Authoring Rule

Use Symbolacts for repeatable command meaning, not decorative language. A valid Symbolact should answer three questions: what action happens, which surface owns it, and what evidence proves it happened.
"""
    (OUTPUT_DIR / "SYMBOLACT_DICTIONARY.md").write_text(body, encoding="utf-8")


def write_assimilation_journal(manifest: dict[str, Any]) -> None:
    rows = [
        [
            item["project"],
            item["integration_type"],
            item["owner_knight"],
            item["path"],
            item["status"],
            item["verification_command"],
            item["risk_or_caveat"],
        ]
        for item in manifest["assimilation_journal"]
    ]
    body = f"""# v701 Assimilation Protocol Journal

Generated: {manifest["generated_utc"]}

## Protocol

1. Identify the open-source project or imported project surface.
2. Assign a Camelot owner Knight and integration lane.
3. Preserve the source path and license boundary.
4. Define a verification command before deeper coupling.
5. Record changes in the ledger and sync the resulting summary to Cloud Brain.

## Journal

{table(["Project", "Type", "Owner", "Path", "Status", "Verification", "Risk / Caveat"], rows)}

## Assimilation States

- `assimilated`: present in the repo and registered in the v701 Cloud Brain package.
- `reference`: useful source material, not necessarily a live runtime dependency.
- `harness`: exposed through CLI or agent command routing.
- `kinetic`: local execution, compression, scan, or build lane.
- `defense`: Watchtower, policy, gate, or security lane.

## v701 Rule

No open-source project becomes a core engine by folder presence alone. It needs an owner, source path, verification command, risk note, and ledger-backed promotion.
"""
    (OUTPUT_DIR / "ASSIMILATION_PROTOCOL_JOURNAL.md").write_text(body, encoding="utf-8")


def write_manifest_doc(manifest: dict[str, Any]) -> None:
    body = f"""# Camelot-OS v701 Cloud Brain Manifest

Generated: {manifest["generated_utc"]}

## Package Contents

- `ENGINE_ARCHITECTURE.md`: live engine stack, routing math, terminal matrix, DKS contract.
- `SCHEMATICS.md`: operator flow, Mermaid execution map, Watchtower/Defense schematic.
- `SYMBOLACT_DICTIONARY.md`: Symbolact/Symbolect command dictionary.
- `ASSIMILATION_PROTOCOL_JOURNAL.md`: open-source integration journal.
- `03_VAULT/runtime_state/camelot_cloudbrain_v701_manifest.json`: machine-readable source.
- `.warp/workflows/camelot-cloudbrain-v701-sync.yaml`: repeatable Warp sync workflow.

## Counts

- Architecture layers: `{len(manifest["architecture_layers"])}`
- Switchboard terminals: `{len(manifest["switchboard_terminals"])}`
- Foundry Council engines: `{len(manifest["soul_router"]["foundry_council"])}`
- Symbolact dictionary entries: `{len(manifest["symbolact_dictionary"])}`
- Assimilation journal entries: `{len(manifest["assimilation_journal"])}`

## Cloud Brain Sync Prompt

Use this summary for the v701 NotebookLM note:

> Camelot-OS v701 architecture package updates the Cloud Brain with live engine architecture, schematics, Symbolact dictionary, and an assimilation protocol journal for each integrated open-source project. Source files are under `docs/plans/camelot-cloudbrain-v701`; machine manifest is `03_VAULT/runtime_state/camelot_cloudbrain_v701_manifest.json`.
"""
    (OUTPUT_DIR / "V701_CLOUD_BRAIN_MANIFEST.md").write_text(body, encoding="utf-8")


def write_warp_workflow() -> None:
    body = """---
name: Camelot Cloud Brain v701 Sync
description: Regenerate v701 architecture docs, reconcile ledger, and sync Cloud Brain.
command: |
  cd C:\\Users\\vizio\\CAMELOT_OS
  cmd /c .venv\\Scripts\\python.exe scripts\\generate_cloudbrain_v701.py
  cmd /c .venv\\Scripts\\camelot.exe --json ledger status
  cmd /c .venv\\Scripts\\camelot.exe --json cloudbrain queue status
tags:
  - camelot
  - cloudbrain
  - v701
  - architecture
  - ledger
"""
    WARP_WORKFLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
    WARP_WORKFLOW_PATH.write_text(body, encoding="utf-8")


def build_manifest() -> dict[str, Any]:
    return {
        "version": "v701.0",
        "generated_utc": utc_now(),
        "source_root": str(ROOT),
        "architecture_layers": architecture_layers(),
        "schematic_edges": schematic_edges(),
        "switchboard_terminals": load_terminals(),
        "soul_router": load_soul_router(),
        "roster": load_roster(),
        "symbolact_dictionary": symbolact_dictionary(),
        "assimilation_journal": discover_projects(),
        "outputs": {
            "engine_architecture": rel(OUTPUT_DIR / "ENGINE_ARCHITECTURE.md"),
            "schematics": rel(OUTPUT_DIR / "SCHEMATICS.md"),
            "symbolact_dictionary": rel(OUTPUT_DIR / "SYMBOLACT_DICTIONARY.md"),
            "assimilation_protocol_journal": rel(OUTPUT_DIR / "ASSIMILATION_PROTOCOL_JOURNAL.md"),
            "manifest_doc": rel(OUTPUT_DIR / "V701_CLOUD_BRAIN_MANIFEST.md"),
            "runtime_manifest": rel(MANIFEST_PATH),
            "warp_workflow": rel(WARP_WORKFLOW_PATH),
        },
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    write_engine_architecture(manifest)
    write_schematics(manifest)
    write_symbolact_dictionary(manifest)
    write_assimilation_journal(manifest)
    write_manifest_doc(manifest)
    write_warp_workflow()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "READY", "manifest": rel(MANIFEST_PATH), "outputs": manifest["outputs"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
