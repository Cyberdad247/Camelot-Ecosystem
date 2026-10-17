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
