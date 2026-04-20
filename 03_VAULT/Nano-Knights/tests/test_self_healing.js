/**
 * Verification Suite: Self-Healing Automation
 */

import { ActionExecutor } from '../src/logic/action_executor.js';

// Mock VisionHealer (since it's imported by ActionExecutor)
// We need to override the module behavior or ensure the import is mockable.
// In this basic node test, since we're using ES modules, mocking imports is tricky without a loader or proxy.
// However, since we just wrote ActionExecutor to assume VisionHealer.heal exists, we can mock the behavior if we control the environment.

// But wait, ActionExecutor imports it. 
// A quick verification is to just mock the chrome environment and see if ActionExecutor behaves.

global.chrome = {
    tabs: {
        get: async () => ({ url: 'http://test.com' }),
        captureVisibleTab: async () => "fake_image_data_base64"
    },
    scripting: {
        executeScript: async ({target, func}) => {
            // First call matches specialized skills? NO.
            // Then it tries HeursiticResolver.
            
            // SIMULATE FAILURE on first attempt
            if (!global.attemptCount) global.attemptCount = 0;
            global.attemptCount++;
            
            if (global.attemptCount === 1) {
                // Fail
                return [{ result: { found: false } }];
            } else {
                // Succeed on retry
                return [{ result: { found: true, element: "BUTTON_SUCCESS" } }];
            }
        }
    }
};

async function runTest() {
    console.log("🛡️ VERIFYING SELF-HEALING AUTOMATION...\n");
    let passed = 0;

    global.attemptCount = 0;
    
    // Test Perform
    try {
        console.log("   [TEST] Triggering intent that will fail once...");
        // We expect it to fail, trigger heal, then retry and succeed.
        
        const res = await ActionExecutor.perform(1, { action: 'click', target: 'Submit' });
        
        if (res.status === 'SUCCESS' && global.attemptCount === 2) {
            console.log("✅ Self-Healing: Success (Retried after initial failure)");
            console.log("   Details:", res.resolution);
            passed++;
        } else {
            console.error("❌ Self-Healing Failed:", res);
        }
    } catch (e) {
        console.error("❌ Exception:", e);
    }
    
    console.log(`\n🏁 VERIFICATION COMPLETE: ${passed} PASSED`);
}

runTest();
