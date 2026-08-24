// SPDX-License-Identifier: MIT

/**
 * SEMANTIC ANCHOR ENGINE (Phase 52)
 * Moves beyond brittle selectors to semantic element mapping.
 * Uses localized DOM tree embeddings and visual context to 'anchor' targets.
 */

export class SemanticAnchor {
    /**
     * Attempts to find an element using semantic anchors.
     * @param {string} goal - The semantic goal (e.g. "The search button in the top right")
     * @param {object} context - Brief description of the current page state.
     */
    static async resolve(goal, context) {
        console.log(`[ANCHOR] Resolving semantic goal: "${goal}"`);

        // Phase 52 Strategy:
        // 1. Snapshot the current DOM structure (Pruned)
        // 2. Identify 'Candidate Anchors' (Elements with high textual or ARIA relevance)
        // 3. Score candidates based on spatial proximity to the 'Conceptual Target'

        const candidates = await chrome.scripting.executeScript({
            target: { tabId: context.tabId },
            func: (goalText) => {
                const elements = Array.from(document.querySelectorAll('button, a, input, [role="button"]'));
                return elements.map(el => {
                    const rect = el.getBoundingClientRect();
                    return {
                        id: el.getAttribute('data-nano-id') || 'unknown',
                        text: (el.innerText || el.value || el.placeholder || "").toLowerCase(),
                        aria: (el.getAttribute('aria-label') || "").toLowerCase(),
                        title: (el.getAttribute('title') || "").toLowerCase(),
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2,
                        visible: rect.width > 0 && rect.height > 0
                    };
                }).filter(e => e.visible);
            },
            args: [goal]
        });

        const list = candidates[0]?.result || [];

        // Use the Neural Engine to pick the best anchor from the descriptions
        const bestMatch = await process_via_offscreen("PICK_SEMANTIC_ANCHOR", {
            goal: goal,
            candidates: list
        });

        if (bestMatch && bestMatch.found) {
            console.log(`[ANCHOR] Semantic Match SUCCESS: Resolved to ID ${bestMatch.id}`);
            return {
                resolved: true,
                selector: `[data-nano-id='${bestMatch.id}']`,
                confidence: bestMatch.confidence
            };
        }

        return { resolved: false };
    }
}
