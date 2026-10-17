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
