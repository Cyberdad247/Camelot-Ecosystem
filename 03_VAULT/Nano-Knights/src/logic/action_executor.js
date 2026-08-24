import { SPECIALIZED_SKILLS } from './specialized_skills.js';
import { SOCIAL_SKILLS } from '../skills/social_skills.js';
import { VisionHealer } from './vision_healer.js';

export class ActionExecutor {

    /**
     * Executes a heuristic intent (Click/Type) OR a Specialized/Social Skill.
     * @param {number} tabId - The ID of the tab to act on.
     * @param {object} intent - { action: 'click'|'type'|'FORM_FILL', target: 'text', value: '...' }
     */
    static async perform(tabId, intent) {
        try {
            return await this._executeAttempt(tabId, intent);
        } catch (e) {
            console.warn(`[HER] Action Failed: ${e.message}. Initiating Self-Healing...`);

            // Invoke Vision Healer
            const diagnosis = await VisionHealer.heal(tabId, intent, e.message);

            if (diagnosis.healed) {
                console.log(`[HER] Retrying with Healed Strategy: ${diagnosis.reason}`);
                // Retry with new strategy (Simulated by just retrying original for now,
                // but real logic would use diagnosis.fallback_selector)
                try {
                    return await this._executeAttempt(tabId, intent);
                } catch (retryErr) {
                    return { status: "FAILED", reason: "HEALING_FAILED", details: retryErr.message };
                }
            } else {
                return { status: "FAILED", reason: "UNHEALABLE", details: e.message };
            }
        }
    }

    static async _executeAttempt(tabId, intent) {
        console.log(`[HER] Executing Intent: "${intent.target || 'N/A'}" (${intent.action})`);

        // 0. Check Specialized Skills (Round Table)
        if (SPECIALIZED_SKILLS[intent.action]) {
            console.log(`[SKILL] Executing Specialized Skill: ${intent.action}`);
            const result = await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: SPECIALIZED_SKILLS[intent.action]
            });
            return { status: "SUCCESS", data: result[0]?.result };
        }

        // 0.5 Check Social Skills (Persona)
        if (SOCIAL_SKILLS[intent.action]) {
            console.log(`[SOCIAL] Executing Social Skill: ${intent.action}`);
            const result = await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: SOCIAL_SKILLS[intent.action],
                args: [intent.value || {}] // Pass profile data for FORM_FILL
            });
            return { status: "SUCCESS", data: result[0]?.result };
        }

        // 1. Snapshot State (for verification)
        let pre_url = "unknown";
        try {
            const tab = await chrome.tabs.get(tabId);
            pre_url = tab.url;
        } catch (e) {
            console.warn("[HER] Tab unavailable for pre-check", e);
            throw new Error("TAB_GONE");
        }

        // 2. Resolve & Execute in Content Script
        const result = await chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: (intent) => {
                // Relies on HeuristicResolver being injected by content_sentry.js
                if (!window.HeuristicResolver) return { success: false, error: "HER_NOT_LOADED" };
                return window.HeuristicResolver.resolve(intent);
            },
            args: [intent]
        });

        const resolution = result[0]?.result;

        // 3. Handle Resolution
        if (resolution && resolution.found) {
            console.log(`[HER] Target Resolved:`, resolution.element);

            // Execute Click/Input via Scripting (Secure Context)
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: (id, action, value) => {
                    // Try Data-Nano-ID first (from BuildDomTree), then Heuristic fallback
                    const el = document.querySelector(`[data-nano-id='${id}']`) || window.HeuristicResolver.findByText(value)[0];
                    if (!el) return { success: false };

                    if (action === 'click') {
                        el.click();
                        return { success: true };
                    }
                    if (action === 'type') {
                        el.value = value;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        return { success: true };
                    }
                },
                args: [resolution.id, intent.action, intent.value]
            });

            // 4. Verification Loop
            setTimeout(() => this.verifyOutcome(tabId, pre_url), 500);
            return { status: "SUCCESS", resolution };
        } else {
            console.warn(`[HER] Failed to resolve intent.`);
            throw new Error("TARGET_NOT_FOUND");
        }
    }

    static async verifyOutcome(tabId, pre_url) {
        try {
            const post_tab = await chrome.tabs.get(tabId);
            const post_url = post_tab.url;

            if (pre_url !== post_url) {
                console.log(`[VERIFY] Navigation Detected: ${pre_url} -> ${post_url}`);
                // Trigger New Analysis?
            } else {
                console.log(`[VERIFY] No Navigation. Checking DOM Mutation...`);
                // Future: Inject MutationObserver check
            }
        } catch (e) {
            console.warn("[VERIFY] Tab closed or inaccessible.");
        }
    }
}
