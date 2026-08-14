// SPDX-License-Identifier: MIT

/**
 * Verification Suite: Social Engineering & Handoff
 */

import { SOCIAL_SKILLS } from '../src/skills/social_skills.js';
import { KnightSpawner } from '../src/knights/knight_spawner.js';

// Mock Browser
global.chrome = {
    tabs: {
        get: async (id) => ({ id, url: 'http://target.com/login' }),
        remove: async (id) => console.log(`   [MOCK] Tab ${id} closed.`),
        create: async () => ({ id: 999 }), // New Tab ID
        update: async (id, props) => console.log(`   [MOCK] Tab ${id} navigated to ${props.url}`)
    },
    scripting: {
        executeScript: async () => {} // Logic tested separately or simulated
    }
};

// Mock Document for Form Fill
global.document = {
    querySelector: (sel) => {
        // Simulate finding an email input
        if (sel.includes('email')) return { 
            value: '', 
            dispatchEvent: () => {} 
        };
        return null;
    }
};

async function runTest() {
    console.log("🛡️ VERIFYING SOCIAL OPERATIONS...\n");
    let passed = 0;

    // TEST 1: Form Fill Skill
    try {
        const profile = { email: 'agent@nano.os' };
        const res = SOCIAL_SKILLS['FORM_FILL'](profile); // Direct call
        
        if (res.action === 'FORM_RESULT' && res.filledFields >= 1) {
             console.log("✅ Form Fill: Success (Filled email)");
             passed++;
        } else console.error("❌ Form Fill Failed", res);
    } catch(e) { console.error(e); }

    // TEST 2: Persona Handoff
    try {
        const spawner = new KnightSpawner({});
        // Simulate handing off Tab 123 to Sir Zenith (Mobile/Stealth)
        const newTabId = await spawner.handoff(123, 'SIR_ZENITH');
        
        if (newTabId === 999) {
            console.log("✅ Handoff: Success (Swapped Tab 123 -> 999)");
            passed++;
        } else console.error("❌ Handoff Failed");

    } catch(e) { console.error("❌ Handoff Exception:", e); }

    console.log(`\n🏁 VERIFICATION COMPLETE: ${passed} PASSED`);
}

runTest();
