// SPDX-License-Identifier: MIT

/**
 * CONTEXT PRUNER (Scarcity Logic)
 *
 * Enforces strict memory budgets for 8GB environments.
 * Strategy: "Current Page Summary + Last 3 Kinetic Actions"
 */

export class ContextPruner {

    static MAX_ACTIONS = 3;

    /**
     * Prunes a memory array to fit within the scarcity budget.
     * @param {Array} memory - The array of intelligence/action objects.
     * @returns {Array} - The pruned array.
     */
    static prune(memory) {
        if (!memory || memory.length === 0) return [];

        // 1. Identify "Summary" items (High Value)
        // We assume items with skill "SUMMARIZE_CORE" or "PAGE_ANALYSIS" are summaries.
        // We keep the *latest* summary.
        const summaryIndex = memory.findLastIndex(m =>
            m.skill === 'SUMMARIZE_CORE' || m.skill === 'ANALYZE_SCREENSHOT'
        );

        let pruned = [];

        // If we have a summary, keep it.
        if (summaryIndex !== -1) {
            pruned.push(memory[summaryIndex]);
        }

        // 2. Identify "Action" items (Kinetic Steps)
        // We keep the last N actions to maintain immediate context flow.
        const actions = memory.filter(m =>
            m.skill === 'PROMPT_TO_ACTION' || m.agent === 'NAVIGATOR'
        );

        // Take the last N
        const recentActions = actions.slice(-this.MAX_ACTIONS);

        // Merge and sort by timestamp to maintain order, roughly.
        // (Actually, simple concatenation might be enough if we just want "Context" for the LLM)

        // Let's refine: The LLM context usually needs chronological order.
        // We will take the latest summary, and the actions *after* it,
        // OR if actions are before it, we might discard them if they are old.
        // SIMPLIFIED STRATEGY:
        // Keep Latest Summary + Last 3 items of ANY type that are NOT the summary.

        const otherItems = memory.filter((m, i) => i !== summaryIndex);
        const lastN = otherItems.slice(-this.MAX_ACTIONS);

        // Re-assemble
        let finalSet;
        if (summaryIndex !== -1) {
             // If the summary is very old, it might be irrelevant, but "Current Page" implies validity.
             finalSet = [memory[summaryIndex], ...lastN];
        } else {
             finalSet = lastN;
        }

        // De-duplicate by unique content signature
        const uniqueMap = new Map();
        finalSet.forEach(item => {
            // Create a sig based on timestamp and content to identify dupes
            const sig = `${item.timestamp}|${item.content}|${item.skill}`;
            if (!uniqueMap.has(sig)) {
                uniqueMap.set(sig, item);
            }
        });

        return Array.from(uniqueMap.values()).sort((a,b) => new Date(a.timestamp) - new Date(b.timestamp));
    }

    /**
     * Estimates token count roughly (4 chars = 1 token).
     */
    static estimateTokens(memory) {
        const json = JSON.stringify(memory);
        return Math.ceil(json.length / 4);
    }
}
