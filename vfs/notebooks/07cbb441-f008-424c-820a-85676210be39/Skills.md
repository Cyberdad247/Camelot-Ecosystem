# 🛡️ Skills Matrix: SIR_SENTINEL
**Knight:** `SIR_SENTINEL` (AgentArmor Warden)  
**Node UUID:** `07cbb441-f008-424c-820a-85676210be39`  
**Security Governance Level:** `L3 Guardian / Tier-S3 Formal Gatekeeper`  
**Last Audit:** 2026-09-21T16:08:00+00:00  

---

## 1. Core Kinetic & Security Capabilities

### A. Capability Lease Arbitration (`SENTINEL_LEASE_CORE`)
- **`lease_arbitrate(agent_id: str, paths: List[str], ttl_sec: int, max_bytes: int) -> LeaseToken`**  
  Evaluates requesting agent credentials against the active security matrix. Issues a cryptographically signed Ed25519 token containing an immutable sandbox envelope, path whitelist, and self-destruct countdown.
- **`lease_verify(lease_token: str, action: KineticAction) -> bool`**  
  Real-time inline verification ensuring that kinetic file mutations or shell commands do not exceed the granted directory boundary, memory ceiling, or duration.
- **`lease_revoke(lease_id: str, reason: str) -> bool`**  
  Instantly revokes capability leases, terminates running sandboxed tasks via `SIGKILL`, and flags the originating agent for behavioral review.

### B. PDG Taint Tracking & Secret Air-Gap Guard (`SENTINEL_TAINT_SCAN`)
- **`pdg_taint_scan(source_ast: AST, data_sources: List[DataSource]) -> TaintReport`**  
  Constructs a dynamic Program Dependence Graph (PDG) tracing variable assignments, string interpolation, and arguments from untrusted or sensitive sources to network/file sinks.
- **`route_to_sir_ghost(tainted_payload: Dict) -> AirGapSanitizedResult`**  
  Diverts any payload carrying credentials, API tokens, or cryptographic keys to **SIR_GHOST** inside the air-gapped local container, preventing cloud telemetry leakage.
- **`redact_secrets_in_stream(log_stream: Stream) -> CleanStream`**  
  Real-time regex and Shannon entropy stream filter that scrubs tokens, API keys, and hashes before logs touch disk or terminal output.

### C. AST Syntax & Static Safety Gate (`SENTINEL_AST_GATE`)
- **`ast_verify_syntax(file_path: str, proposed_patch: str) -> SyntaxVerificationResult`**  
  Parses proposed Python, TypeScript, or Rust diffs into formal AST structures. Detects syntax anomalies, malicious imports (`eval`, `os.system`, `subprocess.Popen` in non-kernel modules), and unhandled exceptions.
- **`enforce_line_limit(diff: Diff) -> bool`**  
  Enforces the 10-line unassisted mutation limit. If a diff touches $>10$ lines, automatically suspends kinetic commit and redirects to the Iron Gate.

### D. CUA (Computer Use Agent) Red-Zone Quarantine (`SENTINEL_CUA_GUARD`)
- **`cua_red_zone_register(boundary_box: Rect, classification: str) -> None`**  
  Defines forbidden screen coordinates (e.g. 1Password vaults, banking portals, cloud identity settings).
- **`cua_quarantine_enforce(input_event: MouseOrKeyboardEvent) -> bool`**  
  Intercepts kinetic mouse clicks or keystrokes prior to execution. If coordinates intersect a registered red zone, locks OS input and sounds an audible alarm.

### E. Dual-Gate Z3 Formal Logic Prover (`SENTINEL_Z3_PROVER`)
- **`z3_invariant_prove(pre_conditions: List[Expr], post_conditions: List[Expr]) -> ProofResult`**  
  Translates system state assertions into first-order logic SMT formulas. Solves for satisfiability via the Z3 theorem prover within a 1500ms timeout window.

### F. Iron Gate HITL Interceptor (`SENTINEL_HITL_GATE`)
- **`hitl_gate_intercept(risk_score: float, action_summary: str) -> JobSuspension`**  
  Triggers a synchronous halt whenever risk $\ge 50$ or sensitive boundaries are crossed. Emits an authorization challenge to the Excalibur mobile cockpit.
- **`hitl_token_verify(operator_token: str, job_id: str) -> bool`**  
  Validates `CAMELOT_DASHBOARD_OPERATOR_TOKEN`. Upon cryptographic confirmation, resumes suspended pipeline.

---

## 2. Runic Invocation & Tool Mappings

| Tool / Skill Identifier | Runic Dispatch Trigger | Operational Response |
| :--- | :--- | :--- |
| `SENTINEL_LEASE_CORE` | `//LEASE_GRANT`, `//LEASE_REVOKE` | Sub-50ms cryptographic lease generation and enforcement |
| `SENTINEL_TAINT_SCAN` | `//SENTINEL_AUDIT`, `//TAINT_CHECK` | Deep AST dataflow taint analysis and secret interception |
| `SENTINEL_AST_GATE` | `//AST_VERIFY`, `//GATE_CHECK` | Static syntax parsing and 10-line mutation guard |
| `SENTINEL_CUA_GUARD` | `//CUA_LOCK`, `//REDZONE_ARM` | Kinetic input bounding-box lockdown and screen isolation |
| `SENTINEL_Z3_PROVER` | `//PROVE_Z3`, `//SOLVE_SMT` | Formal logic invariant proof generation |
| `SENTINEL_HITL_GATE` | `//HITL_INTERCEPT`, `//HITL_APPROVE` | Iron Gate operator authorization lifecycle |

---

*Compiled by MERLIN_OMEGA under //Forge Knight Protocol at 2026-09-21T16:08:00+00:00.*
