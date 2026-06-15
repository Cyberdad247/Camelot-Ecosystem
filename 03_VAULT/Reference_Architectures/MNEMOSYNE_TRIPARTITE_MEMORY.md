# Project MNEMOSYNE: Tripartite Memory Architecture

**Author:** Sir Boris (with Anya, Merlin, Lady M, Sir Alex)
**Status:** PROPOSED (Architectural Blueprint)

## Core Philosophy: The Memory Funnel
To achieve hyper-velocity reasoning while maintaining deep, persistent, and synthesized knowledge, CAMELOT-OS implements a tripartite memory architecture. 

Data flows through a "cooling" funnel:
1. **Flash (Hot):** Sub-millisecond state via Redis.
2. **Semantic (Warm):** Vector-based conceptual mapping via Qdrant.
3. **Cloud Brain (Cold/Synthesized):** Deep research and narrative synthesis via NotebookLM.

---

## I. Redis: Flash & Short-Term Working Memory
**Handler:** Anya (Router) & Kinetic Edge
**Latency Target:** < 5ms
**Data Characteristics:** Ephemeral, high-frequency, exact-match, TTL-bound.

### Best Systematic Uses:
*   **Session State:** Current conversational turn, active Runes, and active Knight statuses.
*   **Rate Limiting & Locks:** Preventing race conditions in parallel Knight execution (e.g., `Rustclaw` orchestration).
*   **Rapid Context Caching:** Storing the results of immediate shell commands (`//SCAN`, `//STATUS`) for instant retrieval during a single execution loop.
*   **Pub/Sub Event Bus:** Fast-path communication between parallel agents (HCOM integration).

---

## II. Qdrant: Semantic & Episodic Memory
**Handler:** Sir Alex (Planner) & Lady M (Memory Orchestrator)
**Latency Target:** < 50ms
**Data Characteristics:** Vectorized, searchable by meaning, contextual.

### Best Systematic Uses:
*   **RAG for Codebase & Docs:** Chunking and embedding the `03_VAULT` and `01_KERNEL` so Knights can ask "How does the boot sequence work?" and retrieve `awaken.py` and `Rustclaw` concepts.
*   **Past Plan Retrieval (Sir Alex):** Before generating a new AST plan, Alex queries Qdrant to find similar historical `PROVENANCE_LEDGER` entries. This enables "Learning from Mistakes" (Skill Evolution).
*   **Agent Episedes:** Storing individual conversation turns embedded with metadata (Knight ID, Timestamp, Success/Fail flag).

---

## III. NotebookLM: The Cloud Brain (Long-Term Synthesis)
**Handler:** Merlin (Deep Reasoning)
**Latency Target:** Asynchronous (Deep Research)
**Data Characteristics:** Highly synthesized, cross-referenced, document-grounded, narrative.

### Best Systematic Uses:
*   **Architectural Synthesis:** NotebookLM ingest massive amounts of raw code, logs, and architectural markdowns (`03_VAULT`). Merlin queries this not for a specific line of code, but for *understanding* (e.g., "Summarize the evolution of our security posture").
*   **GoT/ToT Grounding:** When Merlin executes a Graph-of-Thoughts reasoning chain, he relies on NotebookLM as the "Source of Truth" document oracle to ground his logic and prevent hallucination.
*   **Knowledge Base Curation:** Lady M periodically takes highly successful Qdrant vectors (proven solutions) and promotes them into structured Markdown documents, which are then synced into NotebookLM's source documents.

---

## IV. The Hydration/Dehydration Pipeline (Lady M's Domain)
Lady M orchestrates the lifecycle of memory.

1.  **Ingestion:** User inputs and tool outputs hit **Redis**.
2.  **Vectorization (Dehydration):** After a task completes, Lady M takes the Redis session log, chunks it, embeds it, and pushes it to **Qdrant**. The Redis key is then given a TTL to expire.
3.  **Synthesis (Promotion):** Weekly, or upon `//SYNC`, Lady M triggers a background script that extracts the highest-value Qdrant vectors (e.g., new working patterns), formats them as Markdown, and updates the **NotebookLM** source drive via the Google Workspace/Drive MCP integration.
