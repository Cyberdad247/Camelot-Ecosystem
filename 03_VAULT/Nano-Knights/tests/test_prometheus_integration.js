/**
 * Verification Suite: Prometheus-Knights Integration
 * Validates: TOON Encoding, GraphRAG Indexing, Sentinel Compression, Knight Spawner
 */

import { TOONEncoder, GraphRAG, Sentinel } from '../src/prometheus/index.js';
import { KnightSpawner } from '../src/knights/knight_spawner.js';

// Mock Browser Environment
global.chrome = {
    storage: {
        local: { get: async () => ({}), set: async () => {} },
        sync: { get: async () => ( { stealthConfig: {} } ), set: async () => {} }
    },
    tabs: { create: async () => ({ id: 123 }), remove: async () => {} },
    scripting: { executeScript: async () => {} },
    runtime: { sendMessage: () => {} }
};

// Mock Profile Manager
const mockProfileManager = {
    loadProfile: async (id) => ({ id, name: "Test Profile" })
};

async function runTest() {
    console.log("🛡️ STARTING PROMETHEUS VERIFICATION...\n");
    let passed = 0;
    let failed = 0;

    // TEST 1: TOON Encoder
    try {
        const article = TOONEncoder.encodeWebArticle(
            "https://example.com/ai-agents",
            "Future of AI Agents",
            "AI agents are autonomous systems. They can perceive and act. Agents use tools."
        );
        if (article['@type'] === 'WEB_ARTICLE' && article.entities.length > 0) {
            console.log("✅ TOON Encoder: Success");
            passed++;
        } else throw new Error("Invalid TOON output");
    } catch(e) {
        console.error("❌ TOON Encoder Failed:", e.message);
        failed++;
    }

    // TEST 2: GraphRAG Indexing & Query
    try {
        const graph = new GraphRAG();
        const node1 = TOONEncoder.encodeNote("Note A", "Concept Alpha is related to Beta.");
        const node2 = TOONEncoder.encodeNote("Note B", "Concept Beta is critical for Gamma.");

        await graph.indexNodes([node1, node2]);
        const results = await graph.query("What is related to Beta?");

        if (results.nodes.length >= 1) {
            console.log("✅ GraphRAG: Success (Found related nodes)");
            passed++;
        } else throw new Error("Query returned no results");
    } catch(e) {
        console.error("❌ GraphRAG Failed:", e.message);
        failed++;
    }

    // TEST 3: Sentinel Compression
    try {
        const nodes = Array(10).fill(0).map((_, i) => ({
            '@type': 'NOTE',
            id: `node_${i}`,
            summary: `This is a long summary for node ${i} that takes up tokens. `.repeat(10),
            entities: [`Entity${i}`]
        }));

        const compressed = await Sentinel.compress(nodes, { target_tokens: 50 });

        if (compressed.nodes.length < 10 || compressed.compressed_tokens < compressed.original_tokens) {
            console.log(`✅ Sentinel: Success (Compressed ${compressed.original_tokens} -> ${compressed.compressed_tokens})`);
            passed++;
        } else throw new Error("Compression failed");
    } catch(e) {
        console.error("❌ Sentinel Failed:", e.message);
        failed++;
    }

    // TEST 4: Knight Spawner
    try {
        const spawner = new KnightSpawner(mockProfileManager);
        const squad = await spawner.deploySquad("Test Mission");

        if (squad.tabIds.length === 3 && squad.conf.length === 3) {
            console.log("✅ Knight Spawner: Success (Deployed 3 Knights)");
            passed++;
        } else throw new Error("Incorrect squad size");
    } catch(e) {
        console.error("❌ Knight Spawner Failed:", e.message);
        failed++;
    }

    console.log(`\n🏁 VERIFICATION COMPLETE: ${passed} PASSED, ${failed} FAILED`);
}

runTest();
