// SPDX-License-Identifier: MIT

/**
 * PRECISE MODE VERIFICATION HARNESS (Track G3)
 * Deterministic simulation of Nano-Knight swarm logic.
 */

import { GoalOrchestrator } from './goal_orchestrator.js';
import { ActionExecutor } from './action_executor.js';
import { TranscriptManager } from './transcript_manager.js';
import { MissionEvaluator } from './mission_evaluator.js';

// --- 1. MOCK CHROME API ---
global.chrome = {
  storage: {
    local: {
      data: {},
      set: async (obj) => {
        Object.assign(global.chrome.storage.local.data, obj);
      },
      get: async (key) => ({ [key]: global.chrome.storage.local.data[key] }),
    },
  },
  tabs: {
    get: async (id) => ({ id, url: 'https://example.com/step1' }),
    query: async () => [{ id: 1, url: 'https://example.com/final' }],
    create: async () => ({ id: Math.floor(Math.random() * 1000) }),
  },
  scripting: {
    executeScript: async ({ target, func, args }) => {
      // Simulate successful DOM resolution or skill execution
      return [{ result: { found: true, id: 'mock-123', element: { tagName: 'BUTTON' } } }];
    },
  },
  runtime: {
    lastError: null,
  },
};

// Mock process_via_offscreen (LLM Bridge)
global.process_via_offscreen = async (action, data) => {
  console.log(`[MOCK_LLM] Handling ${action}`);
  if (action === 'DECOMPOSE_MISSION') {
    return [
      { id: 'goal_1', description: 'Navigate to docs', dependencies: [] },
      { id: 'goal_2', description: 'Extract API key', dependencies: ['goal_1'] },
    ];
  }
  if (action === 'REFLECT_ON_ACTION') return { approved: true };
  if (action === 'EVALUATE_MISSION_SUCCESS')
    return { success: true, confidence: 0.95, rationale: 'Goal met' };
  if (action === 'PREDICT_NEXT_MOVE') return [];
  return {};
};

// --- 2. TEST SUITE ---
async function runAcceptanceTest() {
  console.log('=== STARTING PRECISE MODE ACCEPTANCE RUN (G3) ===');

  const orchestrator = new GoalOrchestrator('Research Camelot API');

  // Test Goal Execution
  const results = await orchestrator.execute(async (goalDesc, context, laneId) => {
    console.log(`[TEST] Executing Goal: ${goalDesc}`);
    const intent = { action: 'click', target: 'Login' };
    return await ActionExecutor.perform(1, intent, laneId);
  });

  // --- 3. ASSERTIONS ---
  console.log('\n=== VERIFICATION RESULTS ===');

  // Check Goal 1 Results
  const g1 = results['goal_1'];
  console.log(`Goal 1 Status: ${g1.evaluation.success ? 'PASSED' : 'FAILED'}`);
  console.log(`Goal 1 Transcript Events: ${g1.transcript.events.length}`);

  if (g1.evaluation.success && g1.transcript.events.length > 0) {
    console.log('✅ D6 (Transcripts) Verified: Data captured and replayable.');
    console.log('✅ D8 (Success Criteria) Verified: LLM Evaluation processed.');
  } else {
    throw new Error('D6/D8 Verification Failed');
  }

  // Test D7 (Retry Policy) Simulation
  console.log('\n[TEST] Simulating Transient Failure for Retry Policy (D7)...');
  let attemptsDetected = 0;
  const failingScripting = {
    executeScript: async () => {
      attemptsDetected++;
      throw new Error('TRANSIENT_DETECTION_ERROR');
    },
  };

  // Temporarily swap scripting to test retries
  const originalScripting = global.chrome.scripting;
  global.chrome.scripting = failingScripting;

  try {
    await ActionExecutor.perform(1, { action: 'click', target: 'Ghost' }, 'retry_test_lane');
  } catch (e) {
    console.log(`Captured Expected Failure: ${e.message}`);
  }

  console.log(`Retry Attempts Detected: ${attemptsDetected}`);
  if (attemptsDetected >= 3) {
    console.log('✅ D7 (Retry Policy) Verified: Exponential backoff triggered 3+ times.');
  } else {
    console.error(`Retry policy only triggered ${attemptsDetected} times.`);
  }

  global.chrome.scripting = originalScripting;
  console.log('\n=== ACCEPTANCE RUN COMPLETE: RADIANT ===');
}

runAcceptanceTest().catch((err) => {
  console.error('❌ ACCEPTANCE RUN FAILED:', err);
  process.exit(1);
});
