// SPDX-License-Identifier: MIT

import { SOCIAL_SKILLS } from '../skills/social_skills.js';
import { SPECIALIZED_SKILLS } from './specialized_skills.js';
import { TranscriptManager } from './transcript_manager.js';
import { VisionHealer } from './vision_healer.js';

export class ActionExecutor {
  /**
   * Executes a heuristic intent (Click/Type) OR a Specialized/Social Skill.
   * @param {number} tabId - The ID of the tab to act on.
   * @param {object} intent - { action: 'click'|'type'|'FORM_FILL', target: 'text', value: '...' }
   * @param {string} laneId - Unique ID for the mission lane (for transcripts).
   */
  static async perform(tabId, intent, laneId = 'default_lane') {
    const transcript = new TranscriptManager(laneId);

    // 0. Meta-Cognition: The Mirror (Phase 51)
    if (typeof process_via_offscreen !== 'undefined') {
      console.log(`[MIRROR] Reflecting on action: ${intent.action}...`);
      const reflection = await process_via_offscreen('REFLECT_ON_ACTION', {
        mission_intent: intent.mission_intent || 'Complete task',
        action: intent.action,
        target: intent.target,
      });

      if (reflection && reflection.approved === false) {
        console.warn(`[MIRROR] Reflection Veto: ${reflection.critique}`);
        await transcript.log('VETO', {
          reason: reflection.critique,
          suggestion: reflection.suggestion,
        });
        return { status: 'VETOED', reason: reflection.critique, suggestion: reflection.suggestion };
      }
    }

    // --- Task D7: Exponential Backoff Retry Policy ---
    const MAX_RETRIES = 3;
    let attempt = 0;
    let lastError = null;

    while (attempt <= MAX_RETRIES) {
      if (attempt > 0) {
        const delay = Math.pow(2, attempt) * 1000;
        console.log(`[HER] Retry Attempt ${attempt}/${MAX_RETRIES} in ${delay}ms...`);
        await transcript.log('RETRY_WAIT', { attempt, delay });
        await new Promise((resolve) => setTimeout(resolve, delay));
      }

      try {
        await transcript.log('ACTION_ATTEMPT', { attempt, intent });
        const result = await this._executeAttempt(tabId, intent);

        await transcript.log('ACTION_SUCCESS', { attempt, result });
        return result;
      } catch (e) {
        attempt++;
        lastError = e;
        console.warn(`[HER] Attempt ${attempt} Failed: ${e.message}`);
        await transcript.log('ACTION_FAILURE', { attempt, error: e.message });

        // If it's a "TAB_GONE" error, no point in retrying
        if (e.message === 'TAB_GONE') break;

        // On final retry failure, try Self-Healing
        if (attempt > MAX_RETRIES) {
          console.warn(`[HER] All retries exhausted. Initiating Self-Healing...`);

          const diagnosis = await VisionHealer.heal(
            tabId,
            intent,
            e.message,
            typeof process_via_offscreen !== 'undefined' ? process_via_offscreen : null,
          );

          if (diagnosis.healed) {
            console.log(`[HER] Retrying with Healed Strategy: ${diagnosis.reason}`);
            await transcript.log('HEALING_ATTEMPT', { diagnosis });

            const healedIntent = {
              ...intent,
              selectorOverride:
                diagnosis.strategy === 'SELECTOR' ? diagnosis.fallback_selector : null,
              coordinateOverride:
                diagnosis.strategy === 'COORDINATE' ? { x: diagnosis.x, y: diagnosis.y } : null,
            };

            try {
              const result = await this._executeAttempt(tabId, healedIntent);
              await transcript.log('HEALING_SUCCESS', { result });
              return result;
            } catch (retryErr) {
              await transcript.log('HEALING_FAILURE', { error: retryErr.message });
              return { status: 'FAILED', reason: 'HEALING_FAILED', details: retryErr.message };
            }
          } else {
            await transcript.log('UNHEALABLE', { error: e.message });
            return { status: 'FAILED', reason: 'UNHEALABLE', details: e.message };
          }
        }
      }
    }

    return { status: 'FAILED', reason: 'MAX_RETRIES_EXCEEDED', details: lastError?.message };
  }

  static async _executeAttempt(tabId, intent) {
    console.log(`[HER] Executing Intent: "${intent.target || 'N/A'}" (${intent.action})`);

    // 0. Check Specialized Skills (Round Table)
    if (SPECIALIZED_SKILLS[intent.action]) {
      console.log(`[SKILL] Executing Specialized Skill: ${intent.action}`);
      const result = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: SPECIALIZED_SKILLS[intent.action],
      });
      return { status: 'SUCCESS', data: result[0]?.result };
    }

    // 0.5 Check Social Skills (Persona)
    if (SOCIAL_SKILLS[intent.action]) {
      console.log(`[SOCIAL] Executing Social Skill: ${intent.action}`);
      const result = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: SOCIAL_SKILLS[intent.action],
        args: [intent.value || {}], // Pass profile data for FORM_FILL
      });
      return { status: 'SUCCESS', data: result[0]?.result };
    }

    // 0.7 Check Synthesized Skills (Phase 47)
    if (intent.synthesizedCode) {
      console.log(`[FORGE] Executing Synthesized Skill: ${intent.action}`);
      const result = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: (code) => {
          return eval(`(${code})()`);
        },
        args: [intent.synthesizedCode],
      });
      return { status: 'SUCCESS', data: result[0]?.result };
    }

    // 1. Snapshot State (for verification)
    let pre_url = 'unknown';
    try {
      const tab = await chrome.tabs.get(tabId);
      pre_url = tab.url;
    } catch (e) {
      console.warn('[HER] Tab unavailable for pre-check', e);
      throw new Error('TAB_GONE');
    }

    // 2. Resolve & Execute in Content Script
    const result = await chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: (intent) => {
        if (intent.selectorOverride) {
          const el = document.querySelector(intent.selectorOverride);
          if (el)
            return {
              found: true,
              id: el.getAttribute('data-nano-id') || 'healed',
              element: { tagName: el.tagName },
            };
        }

        // Relies on HeuristicResolver being injected by content_sentry.js
        if (!window.HeuristicResolver) return { success: false, error: 'HER_NOT_LOADED' };
        return window.HeuristicResolver.resolve(intent);
      },
      args: [intent],
    });

    const resolution = result[0]?.result;

    // 3. Handle Resolution
    if (resolution && resolution.found) {
      console.log(`[HER] Target Resolved:`, resolution.element);

      // Execute Click/Input via Scripting (Secure Context)
      await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: (id, action, value, selectorOverride, coordinateOverride) => {
          // 1. Physical Coordinate Bypass
          if (coordinateOverride) {
            const absX = (coordinateOverride.x / 100) * window.innerWidth;
            const absY = (coordinateOverride.y / 100) * window.innerHeight;
            const el = document.elementFromPoint(absX, absY);
            if (!el) return { success: false, error: 'COORD_OUT_OF_BOUNDS' };

            if (action === 'click') {
              el.click();
              return { success: true, method: 'COORD_CLICK' };
            }
            return { success: false, error: 'COORD_ACTION_NOT_SUPPORTED' };
          }

          // 2. Try Override -> Data-Nano-ID -> Heuristic fallback
          const el =
            (selectorOverride ? document.querySelector(selectorOverride) : null) ||
            document.querySelector(`[data-nano-id='${id}']`) ||
            window.HeuristicResolver.findByText(value)[0];
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
        args: [
          resolution.id,
          intent.action,
          intent.value,
          intent.selectorOverride,
          intent.coordinateOverride,
        ],
      });

      // 4. Verification Loop
      setTimeout(() => this.verifyOutcome(tabId, pre_url), 500);
      return { status: 'SUCCESS', resolution };
    } else {
      console.warn(`[HER] Failed to resolve intent.`);
      throw new Error('TARGET_NOT_FOUND');
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
      console.warn('[VERIFY] Tab closed or inaccessible.');
    }
  }
}
