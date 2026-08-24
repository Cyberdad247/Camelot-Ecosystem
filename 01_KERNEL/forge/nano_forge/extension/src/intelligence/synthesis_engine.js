// SPDX-License-Identifier: MIT

/**
 * Synthesis Engine: The Sense-Maker
 * Aggregates fragmented research into coherent intelligence.
 */

import { Sentinel } from '../prometheus/index.js';

export class SynthesisEngine {
    constructor(llmClient, graphRAG) {
        this.llm = llmClient;
        this.graph = graphRAG;
    }

    /**
     * Synthesize a report from a GraphRAG query or set of nodes
     */
    async synthesize(query, maxTokens = 4000) {
        console.log(`[SYNTHESIS] Starting synthesis for: "${query}"`);

        // 1. Gather Intelligence (GraphRAG)
        // We get nodes relevant to the query + their 1-hop neighbors
        const searchResults = await this.graph.query(query, { maxResults: 15, hopDistance: 1 });
        const nodes = searchResults.nodes;

        if (nodes.length === 0) {
            return "Insufficient intelligence gathered. Deploy swarm to collect data.";
        }

        // 2. Compress Context (Sentinel)
        // Fit hundreds of potential nodes into the context window
        const compressionResult = await Sentinel.compress(nodes, {
            target_tokens: maxTokens,
            anchor_strategy: 'importance'
        });

        console.log(`[SYNTHESIS] Context: ${compressionResult.original_tokens} -> ${compressionResult.compressed_tokens} tokens`);

        // 3. Construct Synthesis Prompt
        const contextblock = compressionResult.nodes.map(n => {
            return `[SOURCE: ${n.metadata.title || n.id}]\n${n.summary}\nEntities: ${n.entities.join(', ')}`;
        }).join('\n\n');

        const prompt = `
        You are the Synthesis Engine of the Prometheus System.
        
        MISSION: Generate a comprehensive intelligence report based on the provided research fragments.
        QUERY: "${query}"

        Directives:
        1. Synthesize facts, do not just list them.
        2. Highlight conflicts or discrepancies between sources.
        3. Identify unique insights discovered by specific agents (Alpha/Beta/Gamma).
        4. Maintain a professional, objective tone.

        === CLASSIFIED RESEARCH DATA ===
        ${contextblock}
        
        === END DATA ===

        REPORT:
        `;

        // 4. Generate Report (LLM)
        try {
            // We assume LLMClient has a simple generate method.
            // In background.js context, we might need to route this.
            // But if this runs in background, we can use the LLMClient instance if available,
            // OR route via offscreen if needed (which is what LLMClient usually does).

            // Simplification: We assume 'this.llm' wraps the complexity
            const report = await this.llm.generate(prompt, "SYNTHESIS_PRIME");
            return report;
        } catch (e) {
            console.error("[SYNTHESIS] LLM Failure:", e);
            return "Synthesis processing failed due to neural link error.";
        }
    }

    /**
     * Phase 55: Transforms Mission Results into Reusable Skills
     */
    async crystallize(missionResults) {
        console.log("[HIVE] Crystallizing Mission Intel into Neural Patterns...");

        // Use the new EXTRACT_PATTERN skill via Offscreen bridge
        const patternIntel = await process_via_offscreen("EXTRACT_PATTERN", {
            results: missionResults
        });

        if (patternIntel && patternIntel.patterns && patternIntel.patterns.length > 0) {
            console.log(`[HIVE] Extracted ${patternIntel.patterns.length} reusable patterns.`);

            // In a real system, we'd save these to the GraphRAG
            // For now, we simulate storing them in local storage as a "Skill Cache"
            chrome.storage.local.get(['skillCache'], (data) => {
                const cache = data.skillCache || [];
                const newCache = [...cache, ...patternIntel.patterns];
                chrome.storage.local.set({ skillCache: newCache });
                console.log("[HIVE] Skill Cache Updated.");
            });

            return patternIntel.summary;
        }

        return "No clear reusable patterns identified.";
    }
}
