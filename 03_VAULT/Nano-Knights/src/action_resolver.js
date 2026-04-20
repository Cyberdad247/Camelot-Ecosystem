/**
 * ACTION RESOLVER (Heuristic Element Resolver - HER)
 * Decouples Intent ("Click Login") from Execution ("#btn-123")
 * Part of Phase 18: Cognitive Action Layer
 */

(function() {
    window.HeuristicResolver = {
        
        // Main Entry Point
        resolve: function(intent) {
            console.log(`[HER] Resolving intent:`, intent);
            
            // 1. Text Match (Exact -> Fuzzy)
            let candidates = this.findByText(intent.target);
            
            // 2. Filter by Visibility
            candidates = candidates.filter(this.isVisible);
            
            // 3. Score & Sort
            const bestMatch = this.rankCandidates(candidates, intent);
            
            if (bestMatch) {
                console.log(`[HER] Found match:`, bestMatch);
                return {
                    found: true,
                    element: bestMatch,
                    id: bestMatch.getAttribute('data-nano-id') // If we have tagged it
                };
            }
            
            return { found: false };
        },

        findByText: function(text) {
            const xpath = `//*[contains(text(), '${text}')] | //input[@value='${text}'] | //*[@aria-label='${text}'] | //img[@alt='${text}']`;
            const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            const nodes = [];
            for (let i = 0; i < result.snapshotLength; i++) {
                nodes.push(result.snapshotItem(i));
            }
            return nodes;
        },

        isVisible: function(el) {
            const rect = el.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
        },

        rankCandidates: function(candidates, intent) {
            if (candidates.length === 0) return null;
            
            // Priority: Button > Input > Link > Div
            return candidates.sort((a, b) => {
                const scoreA = this.getScore(a);
                const scoreB = this.getScore(b);
                return scoreB - scoreA;
            })[0];
        },

        getScore: function(el) {
            let score = 0;
            const tag = el.tagName.toLowerCase();
            if (tag === 'button') score += 10;
            if (tag === 'input') score += 8;
            if (tag === 'a') score += 6;
            if (el.getAttribute('role') === 'button') score += 5;
            return score;
        }
    };

    console.log("[HER] Heuristic Resolver Loaded.");
})();
