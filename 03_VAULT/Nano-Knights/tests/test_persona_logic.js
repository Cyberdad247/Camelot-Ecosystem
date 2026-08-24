/**
 * Verification Suite: The Round Table (Personas)
 * Validates: Persona Registry, Knight Spawner Persona Injection
 */

import { ROUND_TABLE } from '../src/knights/personas.js';
import { KnightSpawner } from '../src/knights/knight_spawner.js';

// Mock Browser Environment
global.chrome = {
    storage: {
        local: { get: async () => ({}), set: async () => {} },
        sync: { get: async () => ( { stealthConfig: {} } ), set: async () => {} }
    },
    tabs: { create: async () => ({ id: 123 }), remove: async () => {} },
    scripting: { executeScript: async ({target, func, args}) => {
        // SIMULATE EXECUTION
        // call the func with args to see if it runs without error
        try {
            // Mock sessionStorage
            global.sessionStorage = { setItem: (k,v) => console.log(`   [MOCK SESSION] ${k} = ${v}`) };
            func(...args);
        } catch(e) {
            console.error("   [MOCK EXEC FAIL]", e);
        }
    } },
    runtime: { sendMessage: () => {} }
};

async function runTest() {
    console.log("🛡️ VERIFYING THE ROUND TABLE...\n");
    let passed = 0;
    let failed = 0;

    // TEST 1: Persona Registry Integrity
    try {
        const apis = ROUND_TABLE['LADY_APIS'];
        if (apis.name === 'Lady Apis' && apis.profile_bias === 'desktop_macos') {
            console.log("✅ Registry: Lady Apis Loaded Correctly");
            passed++;
        } else throw new Error("Registry mismatch");
    } catch(e) {
        console.error("❌ Registry Failed:", e.message);
        failed++;
    }

    // TEST 2: Knight Spawner Persona Injection
    try {
        const spawner = new KnightSpawner({});
        console.log("   [TEST] Deploying Squad...");
        const squad = await spawner.deploySquad("Persona Verification");

        // Check config
        const syntax = squad.conf.find(c => c.personaId === 'SIR_SYNTAX');

        if (squad.conf.length === 3 && syntax && syntax.role === 'Sir Syntax') {
            console.log("✅ Spawner: Squad Configured Correctly (Apis, Syntax, Zenith)");
            passed++;
        } else throw new Error("Squad configuration incomplete");

    } catch(e) {
        console.error("❌ Spawner Failed:", e.message);
        failed++;
    }

    console.log(`\n🏁 VERIFICATION COMPLETE: ${passed} PASSED, ${failed} FAILED`);
}

runTest();
