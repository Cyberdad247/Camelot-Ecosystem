// SPDX-License-Identifier: MIT

/**
 * Verification Suite: Ouroboros Integration
 */

import { MemoryExporter } from '../src/prometheus/memory_exporter.js';
import { GraphRAG } from '../src/prometheus/index.js';

async function runTest() {
    console.log("🛡️ VERIFYING OUROBOROS MEMORY BRIDGE...\n");
    let passed = 0;

    // Test Exporter
    try {
        const graph = new GraphRAG();
        // Manually hydrate for test
        graph.nodes.set('node_1', {
             id: 'node_1',
             '@type': 'Concept',
             summary: 'Test Concept',
             timestamp: new Date().toISOString(),
             entities: ['Tag1']
        });
        graph.edges.push({ from: 'node_1', to: 'node_2', type: 'LINKS_TO' });

        const json = MemoryExporter.export(graph);

        if (json['@graph'] && json['@graph'][0]['@type'] === 'ResearchSession') {
             console.log("✅ Memory Exporter: JSON-LD Structure Valid");
             if (json['@graph'][0].nodes.length === 1) {
                 console.log("✅ Data Content: Node count correct");
                 passed++;
             }
        }
    } catch(e) {
        console.error("❌ Exporter Failed:", e);
    }

    console.log(`\n🏁 VERIFICATION COMPLETE: ${passed} PASSED`);
}

runTest();
