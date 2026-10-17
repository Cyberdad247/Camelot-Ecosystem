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
