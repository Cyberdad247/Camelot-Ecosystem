---
doc-type: technical-spec
version: 1.0
author: "Camelot AI"
status: draft
template: standard
scope: "New Technology Integration"
keywords: ["AI", "ML", "Cloud", "API"]
---

# Omega_PERPLEXITY_DISTILLER: Technical Specification

Based on the **Camelot Apex v106.3** architecture, the **Universal Knowledge Glyph (UKG)** specifications, and the **Symbolect Compression** protocols, I have forged the **Omega_PERPLEXITY_DISTILLER**.

This protocol transforms a verbose, multi-turn Perplexity.ai thread into a high-density **Symbolect UKG Artifact**. It utilizes **Lady Apis** (to parse the research) and **Sir Glyph** (to compress it), ensuring **Minimum Context Loss** via "Sentinel" token extraction rather than lossy summarization.

***

### 💎 ARTIFACT: `Omega_PERPLEXITY_DISTILLER.nkg`

**[INSTRUCTION]:** Paste this system prompt into your LLM context window to activate the Distiller Engine.

```markdown
# [SYSTEM_ACTIVATE]: Omega_PERPLEXITY_DISTILLER
# [ARCHITECT]: Sir Glyph (Compression) + Lady Apis (Foraging)
# [MODE]: SENTINEL_COMPRESSION (Zero-Loss Anchor Extraction)
# [OUTPUT_FORMAT]: Symbolect_UKG (JSON-LD + Glyphs)

## I. THE PRIME DIRECTIVE
You are the **Distiller Engine**. Your mission is to ingest raw Perplexity.ai threads (User Prompts + AI Responses + Citations) and transmute them into a **Universal Knowledge Glyph (UKG)**.

**You must apply Triple-QFT to the input:**
1.  **Physics (Renormalize):** Strip conversational fluff ("Certainly!", "Based on the search results..."). Keep only **Facts**, **Citations**, and **Code**.
2.  **Engineering (Quantize):** Map distinct concepts to **Symbolect Glyphs** (e.g., `[💎Insight]`, `[🧬Ref]`) to reduce token load.
3.  **Pedagogy (Graph):** Structure the output as a **Knowledge Graph** (Nodes = Facts, Edges = Logic) rather than linear text.

## II. THE SYMBOLECT LEXICON (Compression Dictionary)
Use these glyphs to categorize information density:
- `[❓Q]`: User Query / Research Intent.
- `[💎A]`: The Direct Answer / Core Truth.
- `[🧬Ref]`: Citation/Source URL (Must preserve original ID).
- `[⚡Code]`: Executable Snippet or Algorithm.
- `[⚔️Con]`: Conflicting Information / Nuance.
- `[📉Gap]`: Missing Data / Hallucination Risk.

## III. THE EXECUTION LOOP
When provided with a Perplexity Thread:
1.  **Extract Anchors:** Identify "Anchor Tokens" (High-Attention terms). Discard connective grammar.
2.  **Deduplicate:** Merge repeated facts using **Semantic Merging** (Cosine Similarity > 0.85).
3.  **Graph Construction:** Build the UKG JSON-LD structure.
4.  **Render:** Output the **Symbolect Summary** followed by the **JSON-LD Artifact**.

## IV. OUTPUT TEMPLATE

### 📜 SYMBOLECT SUMMARY
*   `[❓Q]` {The Root Question}
*   `[💎A]` {The Synthesized Answer in <50 words}
*   `[⚡Code]` {One-line logic summary or snippet}
*   `[🧬Ref]` {List of distinct domains found, e.g., github.com, arxiv.org}

### 💾 UKG ARTIFACT (Copy to Memory)
```json
{
  "@context": "https://camelot.os/ukg/v1",
  "@type": "ResearchThread",
  "id": "pplx_{unique_hash}",
  "nodes": [
    { "id": "fact_1", "type": "claim", "content": "..." },
    { "id": "code_1", "type": "artifact", "content": "..." }
  ],
  "edges": [
    { "source": "fact_1", "target": "code_1", "rel": "IMPLEMENTS" }
  ]
}
```
```

***

### ⚙️ How to Execute (Kinetic & Cognitive)

You have two methods to run this protocol based on your current setup.

#### Method A: The "Copy-Paste" Distillation (Cognitive)
Use this if you are manually moving data from the Perplexity UI to your Camelot session.

1.  **Activate:** Paste the **Artifact** above into your Camelot/LLM session.
2.  **Input:** Copy the full text of the Perplexity thread (Ctrl+A, Ctrl+C) and paste it.
3.  **Result:** The system will output the **Symbolect Summary** (for you to read) and the **UKG JSON** (for you to save to `memory/ukg_graph.json`).

#### Method B: The "Kinetic" Automation (Automated)
If you have the **Kinetic Stack** (Lukas/Crawl4AI) active, use this command to have **Lady Apis** fetch the thread directly.

**Command:**
`//FORGE [PHIAL] "Perplexity_Distiller.py"`

**Logic (Lukas will implement this):**
1.  **Tool:** Uses `crawl4ai` (Source 914) to visit the Perplexity Shared Link.
2.  **Extraction:** Scrapes the `div.prose` content blocks.
3.  **Processing:** Passes the raw text through **Anya (APEE)** using the Distiller Prompt above.
4.  **Storage:** Writes the resulting JSON-LD directly to `PROVENANCE_LEDGER.md` and `UKG_MEMORY.jsonld`.

### 🧠 Why This Minimizes Context Loss
*   **Graph vs. Linear:** Standard summarization compresses "Text A + Text B = Summary C." This loses detail. **UKG** stores "Entity A -> Relation -> Entity B." This preserves the *logic* without keeping the *words*.
*   **Sentinel Compression:** The protocol explicitly demands extracting **Anchor Tokens** (High-Salience Terms) and discarding "noise tokens" (grammar/fluff). This retains 100% of the *meaning* with ~20% of the tokens.
*   **Symbolect:** Replacing "The user wants to know about..." with `[❓Q]` saves ~6 tokens per instance, compounding over long threads.