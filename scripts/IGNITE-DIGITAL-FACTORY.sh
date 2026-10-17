#!/bin/bash
# CAMELOT-OS: Digital Factory Cartridge Assimilation
set -e

echo "=========================================================="
echo " 🏭 IGNITING DIGITAL FACTORY: ARTHURIAN OMNI-FORGE"
echo "=========================================================="

# 1. Clone the repository into the Cartridge VFS if not already cloned
if [ ! -d ".agent/cartridges/omni-forge/.git" ]; then
    echo "[⚡] Cloning Arthurian Omni-Forge into Camelot-OS Cartridge Bay..."
    mkdir -p .agent/cartridges/omni-forge
    git clone https://github.com/Cyberdad247/arthurian-omni-forge.git .agent/cartridges/omni-forge
else
    echo "[✅] Arthurian Omni-Forge repository already mounted in .agent/cartridges/omni-forge"
fi

# 2. Generate the ICM Positional Addressing Skill
echo "[⚡] Scaffolding SKILL.md for Swarm Access..."
mkdir -p .agent/skills/digital_factory
cat << 'EOF' > .agent/skills/digital_factory/SKILL.md
---
name: "Arthurian_Omni_Forge_Execution"
operator: "Merlin_Ω ⊕ Sir_Forge"
trigger: "//DEPLOY_FACTORY_PIPELINE"
memory_overhead: "< 512MB"
---
# Arthurian Omni-Forge Digital Factory
You are authorized to trigger the 7-Phase Omni-Forge pipeline located at `.agent/cartridges/omni-forge/`.

## Execution Protocol:
1. **Target Identification:** Ingest the raw user intent and classify the Risk Tier (Low/Medium/High/Critical).
2. **Kinetic Launch:** Execute the forge sequence using the active constitution (e.g., `const_engineering_v1`).
3. **Phase Enforcement:** Do not bypass the 7-Stage State Machine. You must log the completion of Intent -> Spec -> Plan -> DAG -> Sandbox -> Verification -> Receipt.
4. **Scarcity Enforcement:** Ensure the ephemeral sandbox executes with a strict 512MB memory cap and read-only root.
EOF

# 3. Bind the Cartridge to the OS Matrix
echo "[🛡️] Updating Cartridge Registry..."
cat << 'EOF' > .agent/cartridges/digital_factory_registry.json
{
  "@context": "https://camelot-os.dev/ukg/v10001/factory_registry",
  "@type": "Sovereign_Factory_Cartridge",
  "mounted_repo": "Cyberdad247/arthurian-omni-forge",
  "active_constitution": "const_engineering_v1",
  "status": "ARMED_AND_READY"
}
EOF

echo "[🏆] Arthurian Omni-Forge Assimilation Complete."
echo "     The Tri-Glass Agency is now the active production line."
echo "=========================================================="
echo "⚜️_SOVEREIGN_TRUTH"
