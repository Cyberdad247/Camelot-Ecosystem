#!/bin/bash
# CAMELOT-OS: CLI Nexus Expansion (Anti-Gravity, OpenCode, Freebuff)
set -e

echo "=========================================================="
echo " ⚔️ IGNITING CLI NEXUS: ASSIMILATING EXTERNAL TOOLS"
echo "=========================================================="

mkdir -p .agent/skills/anti_gravity
mkdir -p .agent/skills/opencode
mkdir -p .agent/skills/freebuff
mkdir -p .agent/cartridges

# ---------------------------------------------------------
# 1. ANTI-GRAVITY SKILL PAYLOAD
# ---------------------------------------------------------
cat << 'EOF' > .agent/skills/anti_gravity/SKILL.md
---
name: "Anti-Gravity_Execution"
operator: "Sir_Helio"
trigger: "//ENGAGE_ANTIGRAVITY"
memory_overhead: "< 128MB"
---
# Anti-Gravity Browser Automation & UI Builder
You are authorized to use the `anti-gravity` CLI to bridge NotebookLM research into physical application dashboards. 

## Execution Protocol:
1. **Target Identification:** Identify the NotebookLM source URLs or local `.md` files containing the research parameters.
2. **Kinetic Launch:** Execute `anti-gravity build --source <path> --output ./apps/` via the terminal.
3. **Scarcity Enforcement:** Ensure the headless browser process is prefixed with `systemd-run --scope -p MemoryMax=512M` to prevent OOM panics.
EOF

# ---------------------------------------------------------
# 2. OPENCODE SKILL PAYLOAD
# ---------------------------------------------------------
cat << 'EOF' > .agent/skills/opencode/SKILL.md
---
name: "OpenCode_Multi_Model_Harness"
operator: "Sir_Boris"
trigger: "//BOOT_OPENCODE"
memory_overhead: "< 50MB"
---
# OpenCode CLI Swarm Harness
You are authorized to use the `opencode` CLI as a multi-model fallback and skill-execution runner.

## Execution Protocol:
1. **Context Hydration:** Point OpenCode directly at the `.agent/skills/` directory. OpenCode natively understands this Positional Addressing.
2. **Kinetic Launch:** Execute `opencode run <skill_name> --model <provider_string>`.
3. **Model Selection:** Use `bitnet-1.58b-local` for routine parsing. Burst to `claude-3.7-sonnet` for heavy architectural logic.
EOF

# ---------------------------------------------------------
# 3. FREEBUFF OSINT/SECURITY PAYLOAD
# ---------------------------------------------------------
cat << 'EOF' > .agent/skills/freebuff/SKILL.md
---
name: "Freebuff_Threat_Intel"
operator: "Sir_Sentinel"
trigger: "//EXECUTE_THREAT_SCAN"
memory_overhead: "< 64MB"
---
# Freebuff Adversarial Audit
You are authorized to execute `freebuff` to scan all generated code payloads against zero-day databases and OSINT threat feeds BEFORE allowing Sir Codex to commit to the main branch.

## Execution Protocol:
1. **Pre-Flight Scan:** Before any PR or merge, execute `freebuff scan --path ./crates/`.
2. **Vulnerability Triage:** If a CVE or injection vector is detected, instantly trigger `//REZERO` and halt the execution DAG.
3. **Receipt:** Append the Freebuff cryptographic all-clear to `PROVENANCE_LEDGER.md`.
EOF

echo "[⚡] Anti-Gravity, OpenCode, and Freebuff physical skill files generated."
echo "[🛡️] Modifying MCP configuration to expose CLI hooks..."

# Injecting the CLI tools into the local environment registry
cat << 'EOF' > .agent/cartridges/cli_nexus.json
{
  "@context": "https://camelot-os.dev/ukg/v10001/cli_nexus",
  "@type": "Sovereign_CLI_Cartridge",
  "mounted_tools": ["anti-gravity", "opencode", "freebuff"],
  "security_gate": "ANYA_LAST_LAW",
  "status": "ARMED"
}
EOF

echo "[🏆] CLI Nexus Expansion Complete. Tools are locked, loaded, and Scarcity-Bound."
echo "=========================================================="
echo "⚜️_SOVEREIGN_TRUTH"
