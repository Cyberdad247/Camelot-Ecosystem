/**
 * Verification Suite: Sovereign Mode Data Privacy
 * Validates: CryptoVault, PII Scrubbing, GraphRAG Persistence
 */

import { CryptoVault } from '../src/security/crypto_vault.js';
import { TOONEncoder } from '../src/prometheus/encoder.js';
import { GraphRAG } from '../src/prometheus/index.js';

// Mock Web Crypto (if not available in Node environment, polyfill or check)
if (!global.crypto) {
    console.error("❌ Node environment missing Web Crypto API. Upgrade Node.");
    process.exit(1);
}

// Mock Chrome Storage
const storage = new Map();
global.chrome = {
    storage: {
        local: {
            get: async (key) => ({ [key]: storage.get(key) }),
            set: async (obj) => Object.entries(obj).forEach(([k,v]) => storage.set(k,v)),
            remove: async (key) => storage.delete(key),
            clear: async () => storage.clear()
        }
    }
};

async function runTest() {
    console.log("🛡️ VERIFYING SOVEREIGN DATA PRIVACY...\n");
    let passed = 0;
    
    // TEST 1: PII Scrubbing
    const rawText = "Contact me at user@example.com or call 555-019-2834.";
    const scrubbed = TOONEncoder.scrubPII(rawText);
    if (scrubbed.includes('[REDACTED_EMAIL]') && scrubbed.includes('[REDACTED_PHONE]')) {
        console.log("✅ PII Scrubbing: Success");
        passed++;
    } else console.error("❌ PII Scrubbing Failed:", scrubbed);

    // TEST 2: Encryption & Persistence
    try {
        const graph = new GraphRAG();
        await graph.indexNodes([
            TOONEncoder.encodeNote("Secret Plan", "The mission starts at dawn.")
        ]);
        
        // Check Storage - Should be encrypted blob
        const stored = storage.get('encrypted_graph');
        if (stored && stored.iv && stored.content) {
            console.log("✅ Encryption: Data is stored as IV/Content pair");
            passed++;
        } else {
            console.error("❌ Encryption Failed: Storage format invalid", stored);
        }

        // TEST 3: Decryption (Load)
        // Simulate restart
        const graph2 = new GraphRAG();
        await graph2.load();
        if (graph2.nodes.size === 1) {
             console.log("✅ Decryption: Data restored successfully");
             passed++;
        } else console.error("❌ Decryption Failed: Node count 0");

    } catch(e) { console.error("❌ Persistence Test Failed:", e); }

    // TEST 4: Data Purge
    const graph3 = new GraphRAG();
    await graph3.clear();
    if (!storage.get('encrypted_graph')) {
        console.log("✅ Data Purge: Storage wiped");
        passed++;
    } else console.error("❌ Purge Failed");

    console.log(`\n🏁 VERIFICATION COMPLETE: ${passed} PASSED`);
}

runTest();
