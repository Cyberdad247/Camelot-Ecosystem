/**
 * VISION HEALER
 * Self-Correction Module using Multimodal Analysis
 */

export class VisionHealer {

    /**
     * Diagnose a failed action and propose a fix
     * @param {number} tabId 
     * @param {object} intent - The original failed intent
     * @param {string} error - The error message
     * @returns {object} - New intent (e.g. { action: 'click', type: 'COORDINATE', x: 100, y: 200 })
     */
    static async heal(tabId, intent, error) {
        console.log(`[HEALER] Diagnosing failure for: ${intent.action} on "${intent.target}"`);

        // 1. Kinetic Recon: Try fuzzy matching using attributes before escalating to Vision
        const kineticResult = await chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: (target) => {
                if (window.HeuristicResolver) {
                    const matches = window.HeuristicResolver.fuzzyMatch(target);
                    if (matches.length > 0) {
                        return {
                            resolved: true,
                            id: matches[0].getAttribute('data-nano-id'),
                            selector: `[data-nano-id='${matches[0].getAttribute('data-nano-id')}']`
                        };
                    }
                }
                return { resolved: false };
            },
            args: [intent.target]
        });

        const diagnosis = kineticResult[0]?.result;
        if (diagnosis && diagnosis.resolved) {
            console.log("[HEALER] Kinetic Recon SUCCESS: Found target via fuzzy attribute match.");
            return {
                healed: true,
                strategy: 'SELECTOR',
                new_target: intent.target,
                fallback_selector: diagnosis.selector,
                reason: "Semantic attribute match (Fuzzy)"
            };
        }

        // 2. Capture Vision Context (Escalation)
        console.log("[HEALER] Kinetic Recon FAILED. Escalating to Vision...");
        const screenshot = await chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 50 });

        // Call the neural engine via background bridge
        // Note: process_via_offscreen is expected to be passed as a 4th argument in Phase 41
        // or we use a message-based fallback. For now, we assume it's passed.
        if (arguments[3] && typeof arguments[3] === 'function') {
            const process_via_offscreen = arguments[3];
            const visionResult = await process_via_offscreen("LOCATE_ELEMENT_VISUALLY", {
                screenshot,
                intent: intent.target
            });

            if (visionResult && visionResult.found && visionResult.box_2d) {
                console.log(`[HEALER] Visual Match SUCCESS: Found @ [${visionResult.box_2d}]`);
                // box_2d is [ymin, xmin, ymax, xmax]
                // Calculate center (Normalized 0-1000)
                const centerX = (visionResult.box_2d[1] + visionResult.box_2d[3]) / 2;
                const centerY = (visionResult.box_2d[0] + visionResult.box_2d[2]) / 2;

                return {
                    healed: true,
                    strategy: 'COORDINATE',
                    x: centerX / 10, // Convert to % for the executor
                    y: centerY / 10,
                    reason: `Visual detection via Omega_OCULAR (${visionResult.label || 'Match'})`
                };
            }
        }

        return {
            healed: false,
            reason: "Target truly missing or obscured by complex overlay."
        };
    }
}
