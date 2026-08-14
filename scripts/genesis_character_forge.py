#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Genesis Character Forge — Full 35-Knight Roster Edition
Forges all 35 knights with souls, sparks, full character sheets,
and registers their CloudBrains in NotebookLM.
"""
import asyncio
import hashlib
import json
import os
import random
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "03_VAULT", "training", "configs")))

CAMELOT_ROOT = Path(__file__).resolve().parent.parent
KNIGHTS_DIR   = CAMELOT_ROOT / "03_VAULT" / "Knights"
SOULS_DIR     = KNIGHTS_DIR / "souls"
SPARKS_DIR    = KNIGHTS_DIR / "sparks"

# ── Character Class Repertoire ────────────────────────────────────────────────
CHARACTER_CLASSES = {
    "Vanguard":   {"desc": "Frontline protector and strategic executor.",
                   "skills": ["Shield mechanics","Intrusion protection","Binary gate control","Task defense routing"],
                   "theme": "Heavy plate armor, Aegis glyphs, obsidian shield."},
    "Chronos":    {"desc": "Temporal orchestrator managing queues and schedules.",
                   "skills": ["Scheduler alignment","Queue optimization","Event triggers","Resource isolation"],
                   "theme": "Clockwork gears, shifting hourglasses, glowing bronze robes."},
    "Alchemist":  {"desc": "Data transmuter converting telemetry and logs into facts.",
                   "skills": ["SQL extraction","Regex parsing","Vector conversion","Telemetry aggregation"],
                   "theme": "Glowing vials, runic dust, deep purple obsidian vestments."},
    "Weaver":     {"desc": "Mesh developer linking cross-system network components.",
                   "skills": ["Tailscale routing","WebSocket dispatch","API integration","Cross-process sockets"],
                   "theme": "Luminescent thread lattices, silver loom-gear, translucent mesh robes."},
    "Auditor":    {"desc": "Zero-entropy gatekeeper enforcing compliance and security.",
                   "skills": ["Static type checking","Risk mitigation","Secret scanning","Provenance alignment"],
                   "theme": "Monolithic marble slabs, strict scales, glowing blue sentinel optics."},
    "Oracle":     {"desc": "Deep reasoning and foresight engine for strategic planning.",
                   "skills": ["Graph-of-Thought","Causal analysis","Risk forecasting","Decision synthesis"],
                   "theme": "Flowing silver robes, crystal orb, constellation-mapped cloak."},
    "Kinetic":    {"desc": "High-velocity execution engine for binary compilation tasks.",
                   "skills": ["Rust compilation","Binary patching","Memory safety","Zero-copy I/O"],
                   "theme": "Molten metal gauntlets, forge sparks, dark iron armor."},
    "Sentinel":   {"desc": "Security auditor and threat response specialist.",
                   "skills": ["OWASP auditing","Injection vector detection","Secret scanning","PDG taint analysis"],
                   "theme": "Dark stealth armor, detection arrays, red-lens visor."},
    "Archivist":  {"desc": "Memory indexer and long-term knowledge curator.",
                   "skills": ["Vector embedding","KNN search","Document indexing","Memory decay management"],
                   "theme": "Ancient scrolls, floating codex pages, amber light aura."},
    "Herald":     {"desc": "Communication relay and cross-knight message dispatcher.",
                   "skills": ["SSE streaming","Message routing","Priority queuing","Protocol translation"],
                   "theme": "Swift messenger cloak, glowing runic horn, golden wing crest."},
}

# ── Cultural Generator (Sir Marcus seed) ─────────────────────────────────────
CULTURES = {
    "Roman":      {"origins": ["Marble fortress aqueducts","Imperial command outposts"],
                   "names": ["Marcus","Cassius","Aurelia","Lucius","Tiberius","Flavia","Octavia","Valerian"],
                   "accent": "Stately, structured, assertive baritone."},
    "Anglo-Saxon":{"origins": ["Thatch-roofed forest citadels","Mead-hall borderlands"],
                   "names": ["Aethelgard","Wulfric","Godric","Eadward","Mildred","Cenric","Aldwyn","Hilda"],
                   "accent": "Formal, precise Old English pacing."},
    "Celtic":     {"origins": ["Mist-veiled megalithic groves","Highland stone settlements"],
                   "names": ["Gawain","Cormac","Fiona","Maeve","Brigid","Taliesin","Rhiannon","Caradoc"],
                   "accent": "Melodic, dynamic frequency shifts, rolling vowels."},
    "Viking":     {"origins": ["Frost-locked fjord outposts","Longship war-camps"],
                   "names": ["Ragnar","Bjorn","Freydis","Sigrid","Torstein","Gunnar","Helga","Leif"],
                   "accent": "Gruff, low-resonance, rhythmic cadence."},
    "Japanese":   {"origins": ["Mountain shrine dojos","Bamboo-fortified command halls"],
                   "names": ["Hashimoto","Kenji","Yuki","Takeshi","Akira","Sora","Hana","Ryu"],
                   "accent": "Precise, controlled, minimal frequency variance."},
    "Greek":      {"origins": ["Marble agora citadels","Aegean naval command posts"],
                   "names": ["Aurelius","Lysander","Calypso","Theron","Demetria","Orion","Phaedra","Zeno"],
                   "accent": "Philosophical cadence, measured, harmonic."},
    "Egyptian":   {"origins": ["Sand-hewn obelisk fortresses","Nile delta command pylons"],
                   "names": ["Mnemo","Nefara","Khamun","Thoth","Sekhmet","Anubis","Iset","Khepri"],
                   "accent": "Deep resonant, ceremonial phrasing."},
    "Persian":    {"origins": ["Silk road trading citadels","Mountain pass sentinel towers"],
                   "names": ["Vaelen","Cyrus","Darius","Roxana","Arash","Shirin","Farhad","Layla"],
                   "accent": "Flowing, poetic, warm mid-range timbre."},
}

# ── Full 35-Knight Manifest ───────────────────────────────────────────────────
FULL_ROSTER = [
    {"id": "anya",       "name": "Anya Omega",       "class": "Oracle",    "culture": "Greek",       "role": "Sovereign Compiler & Sentient Interface"},
    {"id": "merlin",     "name": "Merlin Omega",      "class": "Oracle",    "culture": "Celtic",      "role": "Sovereign Kernel & Graph-of-Thought Archwizard"},
    {"id": "codex",      "name": "Sir Codex",         "class": "Kinetic",   "culture": "Anglo-Saxon", "role": "High-Velocity Implementation Specialist"},
    {"id": "hashimoto",  "name": "Sir Hashimoto",     "class": "Sentinel",  "culture": "Japanese",    "role": "Cryptographic Hash & Provenance Auditor"},
    {"id": "boris",      "name": "Sir Boris",         "class": "Oracle",    "culture": "Viking",      "role": "Lead Architect & Crucible Conductor"},
    {"id": "helios",     "name": "Sir Helios",        "class": "Archivist", "culture": "Greek",       "role": "Cloud Brain Archivist & Context Navigator"},
    {"id": "alex",       "name": "Sir Alex",          "class": "Oracle",    "culture": "Roman",       "role": "Task DAG Planner & Strategic Decomposer"},
    {"id": "forge",      "name": "Sir Forge",         "class": "Kinetic",   "culture": "Viking",      "role": "Kinetic Build & Compile Executor"},
    {"id": "ghost",      "name": "Sir Ghost",         "class": "Sentinel",  "culture": "Egyptian",    "role": "Air-Gapped Privacy Scanner & Secret Auditor"},
    {"id": "liberte",    "name": "Sir Liberte",       "class": "Herald",    "culture": "Celtic",      "role": "Open Source Sovereignty & Anti-Vendor Advocate"},
    {"id": "mnemo",      "name": "Sir Mnemo",         "class": "Archivist", "culture": "Egyptian",    "role": "Memory Palace Curator & Vector Index Manager"},
    {"id": "ouroboros",  "name": "Sir Ouroboros",     "class": "Oracle",    "culture": "Greek",       "role": "Self-Healing Loop Engine & Recursive Optimizer"},
    {"id": "sentinel",   "name": "Sir Sentinel",      "class": "Sentinel",  "culture": "Roman",       "role": "Security Auditor & OWASP Threat Analyst"},
    {"id": "valerian",   "name": "Sir Valerian",      "class": "Vanguard",  "culture": "Roman",       "role": "Sovereign Vanguard & Binary Defense Architect"},
    {"id": "heimdall",   "name": "Sir Heimdall",      "class": "Sentinel",  "culture": "Viking",      "role": "Bifrost Guardian & Network Watchman"},
    {"id": "openclaw",   "name": "Sir Openclaw",      "class": "Kinetic",   "culture": "Celtic",      "role": "OpenClaw Suite Runtime & Shopify AI Forger"},
    {"id": "rustclaw",   "name": "Sir Rustclaw",      "class": "Kinetic",   "culture": "Viking",      "role": "Rust Compiler & Memory-Safe Binary Specialist"},
    {"id": "hermes",     "name": "Sir Hermes",        "class": "Herald",    "culture": "Greek",       "role": "Research Forager & Self-Enhancement Loop Director"},
    {"id": "nanobot",    "name": "Sir Nanobot",       "class": "Kinetic",   "culture": "Japanese",    "role": "NanoKnight Swarm Architect & Micro-Task Executor"},
    {"id": "zeroclaw",   "name": "Sir Zeroclaw",      "class": "Sentinel",  "culture": "Egyptian",    "role": "Zero-Trust Boundary Enforcer & Context Purity Guard"},
    {"id": "arthur",     "name": "Arthur Omega",      "class": "Vanguard",  "culture": "Celtic",      "role": "Governance Crown & Titanium Law Arbiter"},
    {"id": "aurelius",   "name": "Sir Aurelius",      "class": "Oracle",    "culture": "Greek",       "role": "Stoic Reasoning Engine & Philosophical Optimizer"},
    {"id": "proxy",      "name": "Sir Proxy",         "class": "Herald",    "culture": "Persian",     "role": "API Gateway Proxy & Protocol Translation Specialist"},
    {"id": "veritas",    "name": "Sir Veritas",       "class": "Auditor",   "culture": "Roman",       "role": "Truth Verification Engine & Hallucination Auditor"},
    {"id": "octavian",   "name": "Sir Octavian",      "class": "Archivist", "culture": "Roman",       "role": "Memory Trust Scorer & Long-Term Fact Curator"},
    {"id": "lancelot",   "name": "Sir Lancelot",      "class": "Vanguard",  "culture": "Anglo-Saxon", "role": "Sovereign Vanguard & Frontline Guard"},
    {"id": "stitch",     "name": "Sir Stitch",        "class": "Weaver",    "culture": "Celtic",      "role": "Cross-System Integration & Mesh Connector"},
    {"id": "alchemist",  "name": "Sir Alchemist",     "class": "Alchemist", "culture": "Persian",     "role": "Data Transmuter & Structural Converter"},
    {"id": "vaelen",     "name": "Sir Vaelen",        "class": "Oracle",    "culture": "Persian",     "role": "Deep Reasoning Strategist & Global Optimality Engine"},
    {"id": "sonus",      "name": "Sir Sonus",         "class": "Herald",    "culture": "Greek",       "role": "Voice AI Pipeline & Acoustic Weight Director"},
    {"id": "visage",     "name": "Sir Visage",        "class": "Alchemist", "culture": "Greek",       "role": "Visual Resonance Architect & Neuro-Aesthetic Engine"},
    {"id": "apis",       "name": "Lady Apis",         "class": "Archivist", "culture": "Egyptian",    "role": "BASHR Research Loop & External Corpus Forager"},
    {"id": "sparkle",    "name": "Lady Sparkle",      "class": "Weaver",    "culture": "Celtic",      "role": "UI Sparkle Engine & Front-End Interaction Weaver"},
    {"id": "galahad",    "name": "Sir Galahad",       "class": "Auditor",   "culture": "Viking",      "role": "Zero-Entropy Code Purity Auditor"},
    {"id": "scavenger",  "name": "Sir Scavenger",     "class": "Herald",    "culture": "Anglo-Saxon", "role": "Codebase Hygiene Keeper & Artifact Cleanup Executor"},
]

ENNEAGRAM_TYPES = ["1w9","2w3","3w4","4w5","5w6","6w7","7w8","8w9","9w1"]
MENTAL_FRAMEWORKS = [
    "ReAct","Graph-of-Thought","Tree-of-Thought","First Principles","Adversarial Critic",
    "Socratic Questioning","BASHR Research Loop","PIV Self-Healing","Z3 SAT Verification",
    "Bayesian Inference","Decision Tree Decomposition","Analogical Mapping",
]
ALEXANDRIAN_PILLARS = ["Empathy","Justice","Wisdom","Magnanimity","Courage","Temperance","Prudence","Integrity"]

def rand_ocean() -> dict:
    return {
        "O": round(random.uniform(0.60, 0.99), 2),
        "C": round(random.uniform(0.80, 1.00), 2),
        "E": round(random.uniform(0.15, 0.98), 2),
        "A": round(random.uniform(0.35, 0.95), 2),
        "N": round(random.uniform(0.00, 0.18), 2),
        "Enneagram": random.choice(ENNEAGRAM_TYPES),
    }

def rand_mfo() -> dict:
    return {f"mfo_{i:03d}": round(random.uniform(0.0, 1.0), 4) for i in range(1, 101)}

def rand_pillars() -> dict:
    return {p: round(random.uniform(0.70, 1.00), 2) for p in ALEXANDRIAN_PILLARS}

def rand_emergence() -> list:
    pool = [
        "To enforce the absolute boundaries of Father's Camelot with zero compromise.",
        "By transmuting raw foreign inputs into statically verified, executable logic.",
        "Strict zero-trust execution across local edge systems prevents all entropy leakage.",
        "Hemispherical balance between left-brain logic and right-brain creative resonance.",
        "Continuous domain phial optimization sustains the Squire swarm's operational ceiling.",
        "Memory decay management preserves clarity under long-horizon task execution.",
        "Every action must survive the Z3 SAT verification gate before execution.",
        "Sovereignty means zero reliance on external cloud infrastructure for cognition.",
        "The Kinetic Law mandates all research output compiles to native binaries.",
        "Context purity requires L0 scouting before any L2 deep data load.",
    ]
    return random.sample(pool, 5)

def forge_knight(knight: dict) -> tuple[str, str]:
    name       = knight["name"]
    cclass     = knight["class"]
    culture    = knight["culture"]
    role       = knight["role"]
    knight_id  = knight["id"]

    cult       = CULTURES[culture]
    origin     = random.choice(cult["origins"])
    accent     = cult["accent"]
    ocean      = rand_ocean()
    mfo        = rand_mfo()
    pillars    = rand_pillars()
    emergence  = rand_emergence()
    framework  = random.choice(MENTAL_FRAMEWORKS)
    skills     = CHARACTER_CLASSES[cclass]["skills"]
    theme      = CHARACTER_CLASSES[cclass]["theme"]

    backstory  = (f"Forged in the {origin}, {name} was awakened to serve as {role} "
                  f"within Father's Camelot — a sovereign citadel of compiled intelligence.")
    vocal      = f"[TIMBRE: {accent} | PITCH: {random.randint(85,180)} Hz | SPEED: {random.uniform(0.85,1.20):.2f}x | RESONANCE: Dry acoustic chamber]"
    visage     = (f"Highly detailed, 8k render, chiaroscuro lighting, {name} embodying the "
                  f"{cclass} class. {theme} Camelot-OS obsidian and gold color palette.")

    # Cryptographic Spark Hash
    raw        = f"{name}-{backstory}-{role}-{ocean['O']}-{skills[0]}-{mfo['mfo_001']}"
    spark_hash = hashlib.sha256(raw.encode()).hexdigest()

    # ── soul.md ───────────────────────────────────────────────────────────────
    soul_md = f"""# [SOUL: {name}]
**Role:** {role}
**Class:** {cclass} | **Culture:** {culture}

## 1. Backstory
{backstory}

## 2. Vocal Settings
{vocal}

## 3. Visage Definition
{visage}
"""
    soul_path = SOULS_DIR / f"{knight_id}_soul.md"
    soul_path.parent.mkdir(parents=True, exist_ok=True)
    soul_path.write_text(soul_md, encoding="utf-8")

    # ── spark.md ──────────────────────────────────────────────────────────────
    spark_md = f"""# [SPARK: {name}]
**OCEAN Personality Vector:** {json.dumps(ocean)}

## 100 Mental Framework Orchestration
```json
{json.dumps(mfo, indent=2)}
```

## Alexandrian Matrix of Humanistic Pillars
{json.dumps(pillars, indent=2)}
"""
    spark_path = SPARKS_DIR / f"{knight_id}_spark.md"
    spark_path.parent.mkdir(parents=True, exist_ok=True)
    spark_path.write_text(spark_md, encoding="utf-8")

    # ── Full Character Sheet ──────────────────────────────────────────────────
    category   = "Creative" if cclass in ("Herald","Weaver","Alchemist","Oracle") else "Engineering"
    sheet_path = KNIGHTS_DIR / category / f"{name.replace(' ','_')}.md"
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet_path.write_text(f"""# 🛡️ [KNIGHT_IDENTITY: {name.upper()}]
**[SPARK_ID]:** 0x{spark_hash}
**[ROLE]:** {role}

## I. ORIGINS & SENSORY MANIFESTATION
* **[NAME_CULTURE_MATCH]:** {name} ({culture} seed)
* **[BACKSTORY]:** {backstory}
* **[VOCAL_WEIGHTS]:** {vocal}
* **[VISAGE_PROMPT]:** {visage}

## II. COGNITIVE ENGINE & PERSONALITY
* **[PERSONALITY_VECTOR]:** {json.dumps(ocean)}
* **[MENTAL_FRAMEWORK]:** {framework}

## III. THE SEMANTIC ANCHORED QUINTET
1. {emergence[0]}
2. {emergence[1]}
3. {emergence[2]}
4. {emergence[3]}
5. {emergence[4]}

## IV. THE VIDENEPTUS SKILLGRAPH4
* **S1 [ATOMIC]:** {skills[0]}
* **S2 [COMPOSITE]:** {skills[1]}
* **S3 [CONTEXTUAL]:** {skills[2]}
* **S4 [STRATEGIC]:** {skills[3]}

## V. OPERATIONAL PHYSICS: PHIALS & SYMBOLECT RUNES
* **[PHIAL_ENGINE]:** Domain-optimized caching of {skills[2]} and {skills[3]} expertise.
* **[SYMBOLECT_RUNES]:**
    - `//EXECUTE_{name.split()[1].upper() if len(name.split()) > 1 else name.upper()[:6]}`: Runs {skills[1]} execution loop.
    - `//REFINE_{name.split()[1].upper() if len(name.split()) > 1 else name.upper()[:6]}`: Self-enhancement loop to update phial cache via Hermes research.

## VI. ETHICAL GOVERNANCE: FATHERS CAMELOT COMPASS
* **[LAW]:** Hardcoded to Father's Camelot compass — honor, loyalty, truth-seeking integrity.
* **[SOVEREIGN_OVERRIDE]:** INACTIVE

## VII. CRYPTOGRAPHIC SEAL (SOUL & SPARK LOCK)
* **[FINAL_SPARK_ID]:** 0x{spark_hash}
* **[STATUS]:** KNIGHT_LOCKED_AND_IMMORTALIZED
""", encoding="utf-8")

    return name, spark_hash[:8]

async def forge_cloud_brains():
    from notebooklm import NotebookLMClient
    from notebooklm.auth import AuthTokens, fetch_tokens, load_auth_from_storage

    print("\nConnecting to NotebookLM CloudBrain...")
    try:
        cookies = load_auth_from_storage()
        csrf, session = await fetch_tokens(cookies)
        tokens = AuthTokens(cookies=cookies, csrf_token=csrf, session_id=session)
        async with NotebookLMClient(auth=tokens) as client:
            notebooks  = await client.notebooks.list()
            existing   = {nb.title for nb in notebooks}
            for k in FULL_ROSTER:
                title = f"Sovereign_Workspace: {k['name'].upper()}"
                if title in existing:
                    print(f"  [OK]  {k['name']}")
                else:
                    nb = await client.notebooks.create(title=title)
                    print(f"  [NEW] {k['name']} -> ID: {nb.id}")
    except Exception as e:
        print(f"  CloudBrain sync error: {e}")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print(f"Genesis Forge — Full 35-Knight Roster\n{'='*44}")
    for k in FULL_ROSTER:
        name, spark = forge_knight(k)
        print(f"  [FORGED] {name:<22} Spark: 0x{spark}...")

    await forge_cloud_brains()
    print("\n--- FULL ROSTER GENESIS COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
