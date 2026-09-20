# SPDX-License-Identifier: MIT
"""Synchronize vfs/skills.md with the actual filesystem skills in .agents/skills and vfs/skills/superpowers/skills."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".agents" / "skills"
SKILLS_MD = ROOT / "vfs" / "skills.md"

def main():
    lines = [
        "---",
        "id: skills",
        "title: Dynamic Process Reference & Sovereign Skills Index",
        'context: "camelot-os.dev/ukg/v10001/vfs_master_scaffold"',
        "type: Specialist_Nodes",
        "---",
        "# Dynamic Process Reference & Sovereign Skills Index",
        "Repository of deterministic processes, execution guidelines, and sovereign skills.",
        "Avoids 'vibe-coding' by requiring agents to refer to hardcoded execution guidelines and certified skill workflows.",
        "",
        "## 1. Verified Obra & Camelot Sovereign Skills (`.agents/skills/`)",
        "| Skill Name | Path | Core Operational Intent |",
        "| :--- | :--- | :--- |",
    ]

    for item in sorted(SKILLS_DIR.iterdir()):
        if item.is_dir() and (item / "SKILL.md").exists():
            txt = (item / "SKILL.md").read_text(encoding="utf-8")
            desc_match = re.search(r'description:\s*(["\']?)(.*?)\1(?:\n|$)', txt)
            desc = desc_match.group(2).strip() if desc_match else "Sovereign Agent Skill"
            if len(desc) > 90:
                desc = desc[:87] + "..."
            rel_path = f".agents/skills/{item.name}"
            lines.append(f"| **`{item.name}`** | [`{rel_path}`]({rel_path}/SKILL.md) | {desc} |")

    lines += [
        "",
        "## 2. Kinetic Execution Engines & Specialized Substrates",
        "- **`Speculative_Pre_Warming`**: Pre-warms worker pools and cache contexts before DAG dispatch.",
        "- **`Autonomous_OSINT_Scraping`**: Air-gapped web foraging via NullClaw and BASHR agents.",
        "- **`Hermes_Prime_PhialEngine`**: Executable MGV research loop (Monitor → Generate → Verify → Evolve), Ouroboros memory bank, Phial weight re-weighting. Engine: `01_KERNEL/titan/phials/hermes_prime_phial.py`. Run via `//IGNITE_SELF_EVOLUTION_LOOP <seed>`, `//SYNC_VFS_WORKSPACE`, or `//FORGE_HERMES_PRIME_FILES`.",
        "- **`QtScrcpy_Kinetic_Bridge`**: Android device orchestration, screen mirroring, scrcpy-server payload deployment, wireless TCP/IP pairing, and input injection. Engine: `04_KINETIC/qtscrcpy/qtscrcpy_kinetic_bridge.py`.",
        "",
    ]

    SKILLS_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated {SKILLS_MD} with all skills from filesystem.")

if __name__ == "__main__":
    main()
