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
