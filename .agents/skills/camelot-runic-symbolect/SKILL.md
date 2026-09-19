---
name: camelot-runic-symbolect
description: This skill should be used when the user invokes runic commands (such as //PLAN, //THINK, //FORGE, //SWARM, //CARTRIDGE_VERIFY, //ASSIMILATE_REPO, //MOTO_EDGE_BUS, //QTSCRCPY, //VALIDATE_SPEC, Omega_Merlin, Omega_THINK, Omega_GLYPH, Omega_MOTO_EDGE, Omega_QTSCRCPY, Omega_SPEC_VALIDATE), asks to "compile symbolect", "compress intent into symbolect", "run Merlin crucible", "validate cartridge schema", "decode symbolect expression", access the Moto edge bus, control devices via QtScrcpy, validate the Camelot-OS specification repository, or requests symbolic reasoning under Merlin Omega.
version: 1.1.0
---

# Camelot-OS Runic Symbolect Workflow

This skill formalizes the procedural workflow for interpreting, composing, and compiling Camelot-OS runic directives (`//...`, `Omega_...`) and high-density Symbolect glyph expressions under the governance of **Merlin Omega**.

---

## 1. Architectural Foundations & Governance

Camelot-OS operates on a dual-layer cognitive protocol designed to maximize execution velocity, preserve context windows, and enforce strict hardware scarcity constraints (8GB RAM boundary):

1. **Runic Command Dispatch (`//` and `Omega_`)**:
   Bypasses non-deterministic natural language routing. Directives mapped to registered runes route deterministically to designated Knights (e.g. `merlin_omega`, `sir_forge`, `sir_boris`, `sir_sentinel`) with pre-assigned execution modes and queue priorities.
2. **Symbolect Semantic Anchor Compression (SAC)**:
   A formal symbolic grammar combining emoji operators, mathematical tensor logic, and alchemical trigrams. Symbolect achieves $>70\%$ token reduction while maintaining $<10\%$ semantic loss across agent handoffs.
3. **Merlin Omega (`MERLIN_OMEGA`) Authority**:
   The Sovereign Lead Reasoner, System 2 Architect, GoT/ToT Oracle, and Crucible Auditor. Merlin governs:
   - Context-as-a-Compiler transformation (Triple-QFT / APEE v6.1).
   - Ambiguity gating and Type III error prevention (Socratic halt).
   - Formal schema verification (`//CARTRIDGE_VERIFY`).
   - Deep strategic search trees (`//PLAN`, `//THINK`, `//OWL`).

```
┌─────────────────────────────────────────────────────────────┐
│                      OPERATOR INTENT                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   [Runic Command: // or Omega_]        [Natural Language Intent]
            │                                     │
            ▼                                     ▼
   ┌─────────────────┐                 ┌──────────────────────┐
   │  Runic Router   │                 │ Triple-QFT Pipeline  │
   │  (runic_router) │                 │ (symbolect_transpile)│
   └────────┬────────┘                 └──────────┬───────────┘
            │                                     │
            ▼                                     ▼
   ┌─────────────────┐                 ┌──────────────────────┐
   │ Knight Dispatch │                 │ Symbolect Expression │
   │ (harness_queue) │                 │ |🧠⊗(⚡💬)⟩ ⟨Omega:..⟩ │
   └─────────────────┘                 └──────────────────────┘
```

---

## 2. The Triple-QFT Semantic Compilation Workflow

To compress natural language into Symbolect or prepare high-density prompt conditioning for downstream models, execute the Triple-QFT (Physics-Pedagogy-Engineering) pipeline:

### Step 1: Physics Phase (Renormalization Group Flow)
Strip unphysical noise and conversational fluff.
- Identify and eliminate empty politeness markers ("can you please", "could you", "helpful assistant").
- Isolate the raw physical signal representing the core technical requirement.
- Collapse whitespace into a single dense intent vector.

### Step 2: Pedagogy Phase (The QFT Ambiguity Verification Gate)
Calculate the Ambiguity Score ($A_s \in [0, 100]$) to protect against Type III errors (solving the wrong problem with high precision):
- Add `+25` points for every vague descriptor (`something`, `stuff`, `help me`, `fix it`, `make it better`).
- Add `+40` points if the target subject is missing or unspecified (<3 words).
- **Evaluation Rule**:
  - If $A_s > 20$: **EMIT IMMEDIATE HALT STOP SEQUENCE**. Do not generate code. Do not mutate state. Present 3 structured clarification questions to the operator:
    1. Define the concrete target and boundary.
    2. Specify required inputs, outputs, and artifact formats.
    3. Declare hardware or latency constraints (e.g. 8GB ceiling, SLA).
  - If $A_s \le 20$: Proceed to Step 3.

### Step 3: Engineering Phase (Context Quantization & Anchoring)
Quantize the cleansed intent vector into high-density Anchor Tokens:
- Extract domain nouns, kinetic verbs, and cryptographic identifiers.
- Eliminate grammatical particles and function words.
- If fewer than 4 anchor tokens are extracted, inject structural stabilizers (`Omnicompetent`, `Savant`, `Orthogonal`, `Symmetry`).

### Step 4: Symbolect Emission
Assemble the formal Symbolect token block:
```
|🧠⊗(⚡💬)⟩ ⟨Omega:anchor_1|anchor_2|...|anchor_n⟩
```
For chained operations, insert the operational glyph stages between the state vector and the anchor bracket:
```
|🧠⊗(⚡💬)⟩ 🧲[FORAGE] ⇢ 🧪[TEST] ⇢ 🏆[DEPLOY] ⟨Omega:OAuth2|PKCE|Tailscale|VPS_Bridge⟩
```

---

## 3. Runic Command Interpretation & Dispatch Protocol

When encountering directives prefixed by `//` or `Omega_`, bypass general conversation loops and execute according to the runic dispatch table:

### Step 1: Parse Runic Token
Extract the primary rune identifier and the remaining task parameter:
- Split input string on the first space: `RUNE = tokens[0].upper()`, `TASK = tokens[1:]`.

### Step 2: Resolve Target Knight & Mode
Map the rune to its canonical handler, knight, and mode:

| Rune Prefix | Assigned Knight | Mode | Priority | Standard Action |
|---|---|---|---|---|
| `//PLAN` | `merlin_omega` | `ORACLE` | 3 | Tree-of-Thought (ToT) strategic decomposition $\rightarrow$ `Plan.json` |
| `//THINK` | `merlin_omega` | `ORACLE` | 3 | Multi-hop Graph-of-Thought (GoT) proof and analysis chain |
| `//OWL` | `merlin_omega` | `ORACLE` | 1 | Strigiform Owl high-logic optimization loop |
| `//CARTRIDGE_VERIFY` | `merlin_omega` | `ORACLE` | 1 | Crucible 5-point schema and invariant verification |
| `//ASSIMILATE_REPO` | `merlin_omega` | `ORACLE` | 1 | Git worktree branch isolation and cartridge scaffolding |
| `//FORGE` | `sir_forge` | `KINETIC` | 2 | Kinetic code generation, compilation, and hotswap |
| `//SWARM` | `sir_boris` | `SWARM` | 2 | 5-panel expert debate, multi-agent voting, and consensus |
| `//SCAN` | `squire_colony` | `SENTINEL` | 2 | CLARITY_CORE AST scan, secret detection, and triage report |
| `//STATUS` | `sir_boris` | `ORACLE` | 1 | Port probes, service topology, and health telemetry |
| `//HEAL` | `sir_debug` | `FORGE` | 2 | PIV (Propose-Instrument-Verify) self-healing loop |
| `//MOTO_EDGE_BUS` | `sir_heimdall` | `SENTINEL` | 1 | Moto edge bus probe, drain, and signed dispatch (:8096) |
| `//QTSCRCPY` | `sir_heimdall` | `KINETIC` | 1 | QtScrcpy kinetic bridge audit, device orchestration, and ADB screen injection |
| `//VALIDATE_SPEC` | `hermes_prime` | `SENTINEL` | 1 | Formal specification, 36 schemas, and authority closure validation |
| `Omega_Merlin` | `merlin_omega` | `ORACLE` | 1 | Bare-metal direct reasoning session with Merlin Omega |
| `Omega_GLYPH` | `merlin_omega` | `ORACLE` | 1 | NPE TCoT formal verification of symbolic statements |
| `Omega_COMPRESS` | `merlin_omega` | `ORACLE` | 1 | Explicit execution of SAC $\rightarrow$ CCF context compression |
| `Omega_MOTO_EDGE` | `sir_heimdall` | `SENTINEL` | 1 | Moto Edge Bus signed outbox and telemetry drain (:8096) |
| `Omega_QTSCRCPY` | `sir_heimdall` | `KINETIC` | 1 | QtScrcpy mobile kinetic bridge and ADB device control |
| `Omega_SPEC_VALIDATE` | `hermes_prime` | `SENTINEL` | 1 | Formal specification, 36 schemas, and authority closure validation |

### Step 3: Enqueue or Execute
Format the standard execution packet and append to `logs/harness_queue.jsonl` or run immediately via the command dispatcher.

---

## 4. Merlin Crucible Verification Protocol (`//CARTRIDGE_VERIFY`)

Prior to merging changes, promoting cartridges, or deploying code to VPS nodes, run the artifact through Merlin's Crucible:

### The 5 Invariant Gates
1. **Gate 1: Schema & Contract Adherence**
   Verify the manifest against canonical schema (metadata, version, entrypoints, explicit knight binding).
2. **Gate 2: 8GB Scarcity Ceiling**
   Assert that memory allocation does not exceed runtime limits (384MB for line-rate processes, 2GB ceiling for background tasks). Enforce zero memory leaks and bounded queues.
3. **Gate 3: Iron Gate HITL Barrier**
   Scan for destructive primitives (`rm -rf`, `DROP TABLE`, `push --force`). If risk score $\ge 50$, pause for explicit operator authorization.
4. **Gate 4: Air-Gap & Privacy Confinement**
   Inspect all code touching keys, credentials, or private data. Verify routing to `SIR_GHOST` on local Ollama, strictly bypassing public cloud endpoints.
5. **Gate 5: Provenance Hash Continuity**
   Calculate SHA-256 fingerprint of all touched files and stage a verification receipt for `PROVENANCE_LEDGER.md`.

### Verdict States
- `CERTIFIED`: All 5 gates satisfied. Ready for immediate kinetic reforging.
- `REJECTED`: Schema violation, memory ceiling breach, or untrusted network call detected. Emit diagnostic breakdown.
- `HITL_SUSPENDED`: Risk score $\ge 50$. Execution paused awaiting operator confirmation.

---

## 5. Hermes Prime & Sir Heimdall Kinetic & Specification Workflows

Under the Cybertronia architecture, **Hermes Prime** (`HERMES_PRIME`) and **Sir Heimdall** (`SIR_HEIMDALL`) orchestrate edge bus communication, mobile physical hardware control via QtScrcpy, and formal contract forge verification.

### 5.1 Motorola Moto Edge Bus Protocol (`//MOTO_EDGE_BUS`, `Omega_MOTO_EDGE`)
- **Assigned Knight**: `SIR_HEIMDALL` (with `HERMES_PRIME` trajectory logging)
- **Network Coordinates**: Dedicated daemon `camelot-edge-bus.service` on `http://100.110.180.18:8096` (`vps-camelot-hub`).
- **Target Edge Device**: `motorola-moto-g-power-5g---2024` (`cancunn`, Tailscale IP `100.89.129.105`, USB serial `ZY22L3K36P`).
- **Authentication & Invariant**:
  - Requires base64 JSON envelope in header `x-camelot-edge-envelope`.
  - Canonical signing tuple: `("device_id", "action", "payload", "issued_at", "expires_at", "nonce")`.
  - Replay protection: Memory-cached and SQLite-persisted nonces return HTTP 401 `{"error":"replayed-nonce"}` upon duplication.
- **Runic Invocations**:
  - `python -m control_plane.runes.runic_router --rune MOTO_EDGE_BUS --task "health_probe"` $\rightarrow$ queries `/healthz`.
  - `python -m control_plane.runes.runic_router --rune MOTO_EDGE_BUS --task "flush_outbox"` $\rightarrow$ drains pending edge telemetry.
  - `python -m control_plane.runes.runic_router --rune Omega_MOTO_EDGE --task "status"` $\rightarrow$ inspects device registration state.
- **Symbolect Expression**:
  ```
  |🧠⊗(🛡️⚡)⟩ 🧲[EDGE_BUS] ⇢ 📱[MOTO_CANCUNN:8096] ⇢ 🔒[ED25519_NONCE] ⟨Omega:Heimdall|Hermes|MotoEdge|Scarcity4GB⟩
  ```

### 5.2 QtScrcpy Kinetic Mobile Bridge (`//QTSCRCPY`, `Omega_QTSCRCPY`)
- **Assigned Knight**: `SIR_HEIMDALL` (with `SIR_FORGE` kinetic assistance)
- **Local Runtime Core**: `04_KINETIC/qtscrcpy/qtscrcpy_kinetic_bridge.py` interfacing `C:\Users\vizio\QtScrcpy`.
- **Capabilities**:
  - **Audit**: Verifies `adb.exe` (v1.0.41), `scrcpy-server` binary (733,706 bytes), FFmpeg x64 DLLs, and keymap profiles (`tiktok.json`, `gameforpeace.json`).
  - **Reverse Tunneling**: ADB port reverse forward `localabstract:scrcpy tcp:27183`.
  - **Server Deployment**: Pushes `scrcpy-server` payload to `/data/local/tmp/scrcpy-server.jar`.
  - **Dual Device Orchestration**:
    1. Samsung Galaxy S26 Ultra (`SM_S948U`, serial `R3GL2009ZCH`, transport `13`).
    2. Motorola Moto G Power 5G 2024 (`cancunn`, serial `ZY22L3K36P`, transport `9`).
- **Runic Invocations**:
  - `python -m control_plane.runes.runic_router --rune QTSCRCPY --task "audit"`
  - `python -m control_plane.runes.runic_router --rune QTSCRCPY --task "devices"`
  - `python -m control_plane.runes.runic_router --rune QTSCRCPY --task "push-server"`
  - `python -m control_plane.runes.runic_router --rune QTSCRCPY --task "tap 540 1200"`
- **Symbolect Expression**:
  ```
  |🧠⊗(👁️📱)⟩ 🧲[QTSCRCPY] ⇢ 🔌[ADB:5555] ⇢ 📺[SCRCPY_SERVER_JAR] ⟨Omega:Heimdall|QtScrcpy|Excalibur|ReverseTunnel⟩
  ```

### 5.3 Formal Specification & Authority Closure Validation (`//VALIDATE_SPEC`, `Omega_SPEC_VALIDATE`)
- **Assigned Knight**: `HERMES_PRIME` (System 2 Synthesizer) & `ANYA_OMEGA` (Arch-Gatekeeper)
- **Target Repository**: [`https://github.com/Cyberdad247/CAMELOT_OS.git`](https://github.com/Cyberdad247/CAMELOT_OS.git)
- **Verification Battery**:
  1. **36 Draft 2020-12 Wire Contract Schemas**: `harness/contracts/validate_contract_schemas.py` confirms all schemas in `packages/contracts/` strictly comply with `https://json-schema.org/draft/2020-12/schema` and `index.json`.
  2. **Sprint 2 Authority Closure**: `harness/contracts/validate_authority_closure.py` executes 10 adversarial proofs verifying dynamic Crown epoch fencing, receipt parent chain linkage, and immutable Knight/Soul package admission.
  3. **Contract Forge**: `harness/contracts/validate_contract_forge.py` verifies canonical JSON c14n, Ed25519 signing, and Synthetos persona continuity.
- **Runic Invocations**:
  - `python -m control_plane.runes.runic_router --rune VALIDATE_SPEC --task "https://github.com/Cyberdad247/CAMELOT_OS.git"`
  - `python -m control_plane.runes.runic_router --rune Omega_SPEC_VALIDATE --task "audit"`
- **Symbolect Expression**:
  ```
  |🧠⊗(📜⚖️)⟩ 🧲[CONTRACT_VERIFY] ⇢ 📑[36_SCHEMAS] ⇢ 👑[DYNAMIC_EPOCH] ⟨Omega:CamelotOS_Spec|SADD_v1.2|HermesPrime⟩
  ```

---

## 6. Bundled Resources & Tooling Integration

This skill includes executable utilities and reference documentation:

### Executable Scripts (`scripts/`)
- **`scripts/symbolect_transpiler.py`**:
  Deterministic Python 3 CLI implementing the full Triple-QFT pipeline.
  - Compile intent to Symbolect:
    ```bash
    python scripts/symbolect_transpiler.py compile "<prompt>"
    ```
  - Decode and validate Symbolect:
    ```bash
    python scripts/symbolect_transpiler.py decode "<symbolect_expression>"
    ```
  - Detect and route runic commands:
    ```bash
    python scripts/symbolect_transpiler.py route "<//COMMAND>"
    ```

### Reference Documentation (`references/`)
For exhaustive specifications, consult:
- **`references/symbolect_lexicon.md`**: Complete glyph catalog, operator grammar, set-theoretic definitions, and elemental trigram mappings.
- **`references/merlin_crucible_protocols.md`**: Detailed GoT/ToT reasoning chains, APEE v6.1 ambiguity mathematics, and Crucible verification rules.
- **`references/runic_command_matrix.md`**: Exhaustive listing of all 11+ runic commands, 31 Omega runes, and biomimetic fauna matrix mappings.

### Practical Examples (`examples/`)
For working walkthroughs, review:
- **`examples/symbolect_compilation.md`**: Real-world intent translations, ambiguity halt scenarios, and decoding sessions.
- **`examples/runic_dispatch_workflows.md`**: End-to-end execution walkthroughs for `//PLAN`, `//CARTRIDGE_VERIFY`, and `//SWARM`.

---

## 7. Procedural Best Practices & Invariants

- **Always run ambiguity detection before generating code**: Never guess ambiguous parameters; trigger the QFT halt sequence and ask for clarification.
- **Honor the 8GB Scarcity Protocol**: Keep prompt sizes, temporary data structures, and execution buffers within the strict resource envelope.
- **Preserve Provenance Integrity**: Never manually edit `PROVENANCE_LEDGER.md`; allow system hooks and verified receipts to log state transitions.
- **Respect Knight Separation of Concerns**: Let Merlin plan and verify (`ORACLE`), Sir Boris orchestrate (`SWARM`), Sir Forge execute (`KINETIC`), and Sir Sentinel protect (`SENTINEL`).
