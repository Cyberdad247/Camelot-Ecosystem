# Omni-Router Architecture

The Omni-Router is the central command dispatch and intent routing lattice of CAMELOT-OS. It abstracts away the complexity of managing 9 sovereign Knights, 11 explicit runic commands, 29 Omega system runes, and natural language semantic intents into a unified, secure, and context-aware execution layer.

## Core Components

The Omni-Router matrix consists of three primary routing paradigms governed by a single ontological ledger.

### 1. Taxonomy Ledger (`control_plane/taxonomy.py`)
The single source of truth for the routing matrix. It eliminates state fragmentation by centralizing:
- **IntentCategories**: Enum defining the core task families (`FORGE`, `CODE`, `RESEARCH`, `MEMORY`, `OPS`, `SECURITY`, `VOICE`, `NATIVE_AUDIO`).
- **Semantic Keywords**: Dictionaries mapping natural language to IntentCategories.
- **Terminal Maps**: Prioritized arrays defining which Knights are best suited for which intents.
- **Privacy Keywords**: A universal `frozenset` of words (e.g., "secret", "private", "credential") that trigger immediate air-gapped isolation.

### 2. Runic Router (`control_plane/runic_router.py`)
The exact-match execution layer. It processes explicit directives prefixed with `//` or `Omega_`.
- **Functionality**: Maps discrete commands to specific Knights and pushes the enriched tasks directly into `harness_queue.jsonl` for execution by the Worker daemon.
- **Privacy Shield**: Validates every incoming rune and parameter against the `PRIVACY_KEYWORDS` ledger. If a breach is detected, the task is dynamically hijacked from its intended cloud-capable Knight and forcefully assigned to `sir_ghost` (a local, air-gapped model) under the `SENTINEL` execution mode.

### 3. Intent Router (`control_plane/intent_router.py`)
The semantic classification layer for UI and TUI interactions.
- **Functionality**: Evaluates natural language using keyword heuristics to determine an `IntentCategory`. It then probes live Switchboard terminals in priority order based on the `INTENT_TERMINAL_MAP` to find the most capable active Knight for the task.
- **Speed**: Designed to execute in <1ms without requiring an LLM call.

### 4. Soul Router (`control_plane/soul_router.py`)
The MFOE (Multi-Factor Orchestration Engine) Tensor Engine.
- **Functionality**: Evaluates dynamic routing decisions based on the **Soul Equation**:
  `S_omega = (0.20 * Velocity) + (0.35 * Magnitude) + (0.30 * Privacy) + (0.15 * Environment)`
- **Dynamic Allocation**: Monitors `TTFT` (Time To First Token) for each Knight to avoid SLO violations, dynamically routing around degraded nodes.
- **Privacy Override**: Intercepts high-privacy tensors (>=0.8) and enforces air-gapped execution via `sir_ghost`.

## LATTICE_RADIANT Cloud Brain Synchronization

The Omni-Router is deeply integrated with the `HydrationManager`, providing a persistent, bidirectional memory pipeline to the NotebookLM Cloud Brain.

1. **Context Mounting**: Whenever a high-complexity directive is routed, the router commands the `HydrationManager` to query the Cloud Brain (L2) for synthesized insights. If retrieved, this context is injected into the payload via `[CLOUD_BRAIN_CONTEXT]`.
2. **Provenance Logging**: Regardless of which router (Runic, Intent, or Soul) makes a dispatch decision, the metadata, reason, and classification intent are stored as `L1` or `L2` tissues. These artifacts are selectively pushed into NotebookLM, creating an unbroken sovereign ledger of all routing decisions mapped to the specific Knight.

## Data Flow

```mermaid
graph TD
    A[User Input] --> B{Input Type}
    B -- "// or Omega_" --> C[Runic Router]
    B -- "Natural Language" --> D[Soul/Intent Router]
    
    C --> E{Privacy Shield}
    D --> E
    
    E -- "Secret Detected" --> F[Force: SIR_GHOST (Air-Gapped)]
    E -- "Safe" --> G[Target Knight Assigned]
    
    F --> H[HydrationManager]
    G --> H
    
    H -- "Sync Intent" --> I[(NotebookLM Cloud Brain)]
    I -- "[CLOUD_BRAIN_CONTEXT]" --> H
    
    H --> J[Queue / Execute]
```

## Security & Titanium Laws

The Omni-Router enforces the core Titanium Laws of CAMELOT-OS:
- **Zero-Trust**: The architecture defaults to denying cloud models access to any query bearing privacy signatures.
- **Sovereign Custody**: All routing decisions are archived natively to Cloud Brain Notebooks aligned to specific Knights, preventing context amnesia and ensuring continuous personality alignment across reboots.