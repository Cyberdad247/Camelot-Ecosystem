// SPDX-License-Identifier: MIT

/**
 * SOCIAL OPERATIONS SKILLS
 * Techniques for identity management and access negotiation.
 */

export const SOCIAL_SKILLS = {

    // 🎭 FORM FILLER: Uses Profile Identity to populate fields
    'FORM_FILL': (profileData = {}) => {
        const mappings = {
            'email': ['email', 'user[email]', 'username'],
            'password': ['password', 'pwd', 'user[password]'],
            'firstName': ['firstname', 'first_name', 'name'],
            'lastName': ['lastname', 'last_name']
        };

        let filled = 0;

        // Basic Heuristic Loop
        for (const [key, selectors] of Object.entries(mappings)) {
            const value = profileData[key];
            if (!value) continue;

            for (const sel of selectors) {
                const input = document.querySelector(`input[name*="${sel}"], input[id*="${sel}"]`);
                if (input && !input.value) {
                    input.value = value;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    filled++;
                    break; // One match per key
                }
            }
        }

        return {
            action: 'FORM_RESULT',
            filledFields: filled
        };
    },

    // 🚧 BLOCK DETECTOR: Checks for common access denial signals
    'DETECT_BLOCK': () => {
        const title = document.title.toLowerCase();
        const text = document.body.innerText.toLowerCase();

        const isCloudflare = title.includes('just a moment') || text.includes('cloudflare');
        const is403 = title.includes('403') || title.includes('forbidden');
        const is429 = title.includes('429') || text.includes('too many requests');

        return {
            action: 'BLOCK_RESULT',
            blocked: isCloudflare || is403 || is429,
            reason: isCloudflare ? 'CLOUDFLARE' : (is403 ? '403_FORBIDDEN' : (is429 ? '429_RATE_LIMIT' : 'NONE'))
        };
    }
};
