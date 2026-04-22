# SKILL BIBLE — Security & Agent-Armor
# Knight: Sir Sentinel | Layer: L6_GOVERNANCE | v400.1.0
# LOAD: SEC_OP — instilled on any security/audit/armor task

## AGENT-ARMOR v2.0 — THE IMMUNE SYSTEM
Every prompt is source code. Every untrusted input is a potential injection vector.

## PDG TAINT ANALYSIS
1. Label all inputs: HIGH_INTEGRITY (system files, internal) vs LOW_INTEGRITY (web, user)
2. Map data flow: source → transform → sink
3. Block: LOW_INTEGRITY → shell/eval/file-delete sinks without sanitization
4. Log all blocked flows to PROVENANCE_LEDGER with [ARMOR_BLOCK] tag

## IRON GATE — HITL TRIGGERS (Titanium Law #3)
| Condition | Response |
|---|---|
| Net lines > 10 | HITL_REQUIRED — BriefingScript mandatory |
| Deletion > 50MB | HITL_REQUIRED — explicit approval |
| A2A cross-agent call | RBAC check via rbac_matrix.py |
| Untrusted data → privileged sink | BLOCKED — APEE validation gate |
| Unknown knight identity | BLOCKED |

## SPOTLIGHTING (XML Delimiter Injection Defense)
Wrap all untrusted user/web data in XML delimiters before passing to any LLM:
```
<user_input>{{untrusted}}</user_input>
```
Never interpolate raw untrusted strings into system prompts or tool calls.

## OWASP TOP 10 ENFORCEMENT
- A01 Broken Access Control → A2A RBAC matrix enforced at anya_gate
- A02 Crypto Failures → No secrets in tracked files; Vault/Env only
- A03 Injection → Spotlighting on all external input; parameterized SQL only
- A04 Insecure Design → PDG taint analysis before privileged ops
- A05 Security Misconfiguration → Trivy scan on container changes
- A06 Vulnerable Components → `cargo audit` / `pip-audit` on dependency changes
- A07 Auth Failures → JWT + NextAuth v5; no session tokens in local storage
- A08 Software Integrity → Provenance Ledger hash on all file mods
- A09 Logging Failures → Rotel OpenTelemetry spans on all agent actions
- A10 SSRF → Allowlist-only outbound URLs; no arbitrary URL fetching

## VERIFICATION TOOLS
- **Trivy**: `trivy fs .` — container + filesystem CVE scan
- **Miri**: Rust undefined behavior detection on unsafe blocks
- **DoT**: Depth-of-Thought security chain before any privileged operation
- **pip-audit**: Python dependency vulnerability scan

## ANTI-PATTERNS (//SCORPION will flag)
- Hardcoded API keys, tokens, or passwords in any tracked file
- `exec()`, `eval()`, `os.system()`, `__import__()` with dynamic args
- Bare `except:` clauses (masks security errors)
- Untyped function arguments at trust boundaries
- Skipping HITL gate for >10 line diffs
- A2A calls without RBAC validation
- Prompt injection without XML delimiters
