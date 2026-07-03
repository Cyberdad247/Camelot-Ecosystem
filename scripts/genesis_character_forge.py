#!/usr/bin/env python3
"""Genesis Character Forge
Automatically registers character classes, builds randomized cultural backgrounds,
compiles soul.md & spark.md configurations, builds complete 7-stage character sheets,
and creates corresponding NotebookLM CloudBrains.
"""
import asyncio
import os
import sys
import json
import hashlib
import random
from pathlib import Path

# Add configs to path for notebooklm_bridge
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "03_VAULT", "training", "configs")))

CAMELOT_ROOT = Path(__file__).resolve().parent.parent
KNIGHTS_DIR = CAMELOT_ROOT / "03_VAULT" / "Knights"
SOULS_DIR = KNIGHTS_DIR / "souls"
SPARKS_DIR = KNIGHTS_DIR / "sparks"

# ── 1. Character Classes Repertoire ───────────────────────────────────────────
CHARACTER_CLASSES = {
    "Vanguard": {
        "description": "Martial front-line protector and strategic executor.",
        "skills": ["Shield mechanics", "Intrusion protection", "Binary gates", "Task defense"],
        "visage_theme": "Heavy plate armor, polished steel, shield engraved with Aegis glyphs."
    },
    "Chronos": {
        "description": "Temporal orchestrator managing schedules, tasks, and task queues.",
        "skills": ["Scheduler alignment", "Queue optimization", "Event trigger management", "Resource isolation"],
        "visage_theme": "Clockwork gears, shifting hourglasses, glowing bronze robes."
    },
    "Alchemist": {
        "description": "Data transmuter, converting raw telemetry and unstructured logs into facts.",
        "skills": ["SQL extraction", "Regex parsing", "Vector conversion", "Telemetry aggregation"],
        "visage_theme": "Glowing vials, runic dust, deep purple obsidian vestments."
    },
    "Weaver": {
        "description": "Ecosystem and network mesh developer linking components together.",
        "skills": ["Tailscale routing", "WebSocket dispatch", "API endpoint integration", "Cross-process sockets"],
        "visage_theme": "Luminescent thread lattices, silver loom-gear, translucent mesh robes."
    },
    "Auditor": {
        "description": "Zero-entropy gatekeeper checking compliance, linting, and security constraints.",
        "skills": ["Static type checking", "Risk mitigation", "Secret scanning", "Provenance alignment"],
        "visage_theme": "Monolithic marble slabs, strict scales, glowing blue sentinel optics."
    }
}

# ── 2. Randomized Cultural Generator (Marcus Seed) ───────────────────────────
CULTURES = {
    "Viking": {
        "origins": ["Frost-locked northern bastions", "Fjord-bound longship outposts"],
        "naming": ["Ragnar", "Bjorn", "Freydis", "Sigrid", "Torstein", "Gunnar"],
        "accents": "Gruff, low-resonance, rhythmic cadence."
    },
    "Anglo-Saxon": {
        "origins": ["Thatch-roofed forest citadels", "Mead-hall borderlands"],
        "naming": ["Aethelgard", "Wulfric", "Godric", "Eadward", "Mildred", "Cenric"],
        "accents": "Formal, precise Old English pacing."
    },
    "Roman": {
        "origins": ["Aqueduct-fed marble fortresses", "High-walled command posts"],
        "naming": ["Marcus", "Cassius", "Aurelia", "Lucius", "Tiberius", "Flavia"],
        "accents": "Stately, highly structured, assertive."
    },
    "Celtic": {
        "origins": ["Mist-veiled megalithic groves", "Highland stone settlements"],
        "naming": ["Gawain", "Cormac", "Fiona", "Maeve", "Brigid", "Taliesin"],
        "accents": "Melodic, dynamic frequency shifts, rolling vowels."
    }
}

def generate_background(name: str, culture_name: str, char_class: str) -> dict:
    culture = CULTURES[culture_name]
    origin = random.choice(culture["origins"])
    accent = culture["accents"]
    
    backstory = f"Born in the {origin}, this {char_class} was awakened to forge code structures in Father's Camelot."
    
    # Timbre & Visage prompts
    timbre = f"{accent} balanced with metallic undertones."
    pitch = f"{random.randint(90, 160)} Hz"
    speed = f"{random.uniform(0.85, 1.15):.2f}x"
    
    visage_theme = CHARACTER_CLASSES[char_class]["visage_theme"]
    visage_prompt = f"Highly detailed, 8k render, chiaroscuro lighting, {name} representing the {char_class} class. {visage_theme} Camelot-OS obsidian and gold color palette."
    
    return {
        "backstory": backstory,
        "vocal_weights": f"[TIMBRE: {timbre} | PITCH: {pitch} | SPEED: {speed} | RESONANCE: Dry acoustic]",
        "visage_prompt": visage_prompt
    }

# ── 3. 100 Mental Framework Orchestration Template ────────────────────────────
def get_mfo_vector() -> dict:
    """Generate 100 mental framework parameters representing the cognitive matrix."""
    return {f"mfo_var_{i:03d}": round(random.uniform(0.0, 1.0), 3) for i in range(1, 101)}

# ── 4. Character Manifests (5 Targets) ────────────────────────────────────────
CHARACTERS_TO_FORGE = [
    {"name": "Sir Marcus", "class": "Chronos", "culture": "Roman", "role": "Cultural Chronicler & Swarm Director"},
    {"name": "Sir Lancelot", "class": "Vanguard", "culture": "Anglo-Saxon", "role": "Sovereign Vanguard & Frontline Guard"},
    {"name": "Lady Guinevere", "class": "Weaver", "culture": "Celtic", "role": "Ecosystem Weaver & Network Director"},
    {"name": "Sir Gawain", "class": "Alchemist", "culture": "Celtic", "role": "Data Transmuter & Telemetry Processor"},
    {"name": "Sir Galahad", "class": "Auditor", "culture": "Viking", "role": "Zero-Entropy Code Purity Auditor"}
]

# ── 5. The Forge Pipeline ─────────────────────────────────────────────────────
def forge_character(char_meta: dict) -> tuple[str, str, str]:
    name = char_meta["name"]
    char_class = char_meta["class"]
    culture_name = char_meta["culture"]
    role = char_meta["role"]
    
    bg = generate_background(name, culture_name, char_class)
    mfo = get_mfo_vector()
    
    # OCEANpersonality weights
    ocean = {
        "O": round(random.uniform(0.75, 0.99), 2),
        "C": round(random.uniform(0.85, 1.00), 2),
        "E": round(random.uniform(0.20, 0.95), 2),
        "A": round(random.uniform(0.40, 0.90), 2),
        "N": round(random.uniform(0.00, 0.15), 2),
        "Enneagram": f"{random.randint(1, 9)}w{random.randint(1, 9)}"
    }
    
    # Emergence Questions (5 distinct anchors)
    emergence_answers = [
        "To enforce the absolute boundaries of Father's Camelot.",
        "By transmuting all incoming foreign code inputs into statically verified logic.",
        "Zero-trust execution across local edge systems, allowing no digital leakage.",
        "Strict balance between systemic logic (left) and creative branding (right).",
        "Continuous optimization of my domain phial to support Squire swarm routines."
    ]
    
    # ── Write soul.md ─────────────────────────────────────────────────────────
    soul_content = f"""# [SOUL: {name}]
**Role:** {role}
**Class:** {char_class}
**Culture:** {culture_name}

## 1. Backstory
{bg["backstory"]}

## 2. Vocal Settings
{bg["vocal_weights"]}

## 3. Visage Definition
{bg["visage_prompt"]}
"""
    soul_path = SOULS_DIR / f"{name.lower().replace(' ', '_')}_soul.md"
    soul_path.parent.mkdir(parents=True, exist_ok=True)
    soul_path.write_text(soul_content, encoding="utf-8")
    
    # ── Write spark.md ────────────────────────────────────────────────────────
    spark_content = f"""# [SPARK: {name}]
**OCEAN personality weights:** {json.dumps(ocean)}
**100 Mental Framework Orchestration:**
{json.dumps(mfo, indent=2)}

## Alexandrian Matrix of Humanistic Pillars:
- Empathy: {round(random.uniform(0.70, 0.95), 2)}
- Justice: {round(random.uniform(0.85, 1.00), 2)}
- Wisdom: {round(random.uniform(0.80, 0.99), 2)}
- Magnanimity: {round(random.uniform(0.75, 0.95), 2)}
"""
    spark_path = SPARKS_DIR / f"{name.lower().replace(' ', '_')}_spark.md"
    spark_path.parent.mkdir(parents=True, exist_ok=True)
    spark_path.write_text(spark_content, encoding="utf-8")
    
    # ── Generate Full Character Sheet ─────────────────────────────────────────
    class_skills = CHARACTER_CLASSES[char_class]["skills"]
    
    # Generate cryptographic hash
    hash_input = f"{name}-{bg['backstory']}-{role}-{ocean['O']}-{class_skills[0]}"
    spark_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    
    sheet_content = f"""# 🛡️ [KNIGHT_IDENTITY: {name.upper()}]
**[SPARK_ID]:** 0x{spark_hash}
**[ROLE]:** {role}

## I. ORIGINS & SENSORY MANIFESTATION
* **[NAME_CULTURE_MATCH]:** {name} ({culture_name} seed)
* **[BACKSTORY]:** {bg["backstory"]}
* **[VOCAL_WEIGHTS]:** {bg["vocal_weights"]}
* **[VISAGE_PROMPT]:** {bg["visage_prompt"]}

## II. COGNITIVE ENGINE & PERSONALITY
* **[PERSONALITY_VECTOR]:** OCEAN: {json.dumps(ocean)}
* **[MENTAL_FRAMEWORK]:** {char_class} execution core.

## III. THE SEMANTIC ANCHORED QUINTET
1. **Systemic Logic:** {emergence_answers[0]}
2. **First Principles:** {emergence_answers[1]}
3. **Purity Boundary:** {emergence_answers[2]}
4. **Hemispherical Harmony:** {emergence_answers[3]}
5. **Continuous Optimization:** {emergence_answers[4]}

## IV. THE VIDENEPTUS SKILLGRAPH4
* **S1 [ATOMIC]:** {class_skills[0]}
* **S2 [COMPOSITE]:** {class_skills[1]}
* **S3 [CONTEXTUAL]:** {class_skills[2]}
* **S4 [STRATEGIC]:** {class_skills[3]}

## V. OPERATIONAL PHYSICS: PHIALS & SYMBOLECT RUNES
* **[PHIAL_ENGINE]:** Optimized caching loops for {class_skills[2]} and {class_skills[3]}.
* **[SYMBOLECT_RUNES]:**
    - `//EXECUTE`: Runs {class_skills[1]} sequence.
    - `//REFINE`: Self-enhancement loop to update the cached phial parameters.

## VI. ETHICAL GOVERNANCE: FATHERS CAMELOT COMPASS
* **[LAW]:** Locked to Father's Camelot compass. Honor, absolute loyalty, and zero-entropy execution.
* **[SOVEREIGN_OVERRIDE]:** INACTIVE

## VII. CRYPTOGRAPHIC SEAL (SOUL & SPARK LOCK)
* **[HASH_GENERATION]:** Compiled SHA-256 validation.
* **[FINAL_SPARK_ID]:** 0x{spark_hash}
* **[STATUS]:** KNIGHT_LOCKED_AND_IMMORTALIZED
"""
    
    # Save target file under category directory
    category = "Creative" if char_class in ("Chronos", "Weaver") else "Engineering"
    dest_path = KNIGHTS_DIR / category / f"{name.replace(' ', '_')}.md"
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(sheet_content, encoding="utf-8")
    
    return name, str(dest_path), spark_hash

async def create_cloud_brains():
    from notebooklm import NotebookLMClient
    from notebooklm.auth import load_auth_from_storage, fetch_tokens, AuthTokens
    
    print("\nConnecting to NotebookLM CloudBrain...")
    try:
        cookies = load_auth_from_storage()
        csrf, session = await fetch_tokens(cookies)
        tokens = AuthTokens(cookies=cookies, csrf_token=csrf, session_id=session)
        
        async with NotebookLMClient(auth=tokens) as client:
            notebooks = await client.notebooks.list()
            existing_titles = {nb.title for nb in notebooks}
            
            for char in CHARACTERS_TO_FORGE:
                title = f"Sovereign_Workspace: {char['name'].upper()}"
                if title in existing_titles:
                    print(f"  [OK]  CloudBrain active for {char['name']}")
                else:
                    print(f"  [ADD] Spawning CloudBrain: '{title}'...")
                    nb = await client.notebooks.create(title=title)
                    print(f"        Created successfully! ID: {nb.id}")
                    
    except Exception as e:
        print(f"Failed to forge CloudBrains: {e}")

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        
    print("Starting Genesis Character Forge...")
    for char in CHARACTERS_TO_FORGE:
        name, path, spark_hash = forge_character(char)
        print(f"  [FORGED] {name} -> {path} (Spark: 0x{spark_hash[:8]}...)")
        
    await create_cloud_brains()
    print("--- GENESIS CHARACTER FORGE COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
