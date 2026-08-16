// SPDX-License-Identifier: MIT

/**
 * PRECISE MODE TEST SUITE (Task D9)
 * Automated verification of Lane Transcripts, Retry Policies, and Success Criteria.
 */

import { GoalOrchestrator } from '../src/logic/goal_orchestrator.js';
import { ActionExecutor } from '../src/logic/action_executor.js';
import { TranscriptManager } from '../src/logic/transcript_manager.js';
import { MissionEvaluator } from '../src/logic/mission_evaluator.js';

// --- 1. TEST MOCKS ---
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
    get: async (id) => ({ id, url: 'https://example.com/active' }),
    query: async () => [{ id: 1, url: 'https://example.com/target' }],
    create: async () => ({ id: 101 }),
    update: async () => {},
  },
  scripting: {
    executeScript: async () => [{ result: { found: true, id: 'n-1', element: { tagName: 'A' } } }],
  },
  runtime: { lastError: null },
};

global.process_via_offscreen = async (action, data) => {
  if (action === 'DECOMPOSE_MISSION')
    return [{ id: 'g1', description: 'Test goal', dependencies: [] }];
  if (action === 'REFLECT_ON_ACTION') return { approved: true };
  if (action === 'EVALUATE_MISSION_SUCCESS') return { success: true, confidence: 1.0 };
  return {};
};

// --- 2. TESTS ---

async function test_transcript_logging() {
  console.log('[TEST] Transcript Logging (D6)...');
  const tm = new TranscriptManager('lane_test');
  await tm.log('ACTION', { cmd: 'test' });
  const replay = tm.getReplayable();
  if (replay.events.length === 1 && replay.events[0].type === 'ACTION') {
    console.log('✅ Passed');
  } else {
    throw new Error('Transcript logging failed');
  }
}

async function test_retry_policy() {
  console.log('[TEST] Action Executor Retry (D7)...');
  let scriptCalls = 0;
  const originalScripting = global.chrome.scripting.executeScript;

  // Force transient failure
  global.chrome.scripting.executeScript = async () => {
    scriptCalls++;
    // First 2 calls (first attempt + first retry resolution) fail
    if (scriptCalls <= 2) throw new Error('BUSY');
    return [{ result: { found: true } }];
  };

  const result = await ActionExecutor.perform(1, { action: 'click', target: 'Test' }, 'lane_retry');

  global.chrome.scripting.executeScript = originalScripting;

  // Expected:
  // 1. Attempt 1: resolution call (fails) -> scriptCalls=1
  // 2. Retry 1: resolution call (fails) -> scriptCalls=2
  // 3. Retry 2: resolution call (success), execution call (success) -> scriptCalls=4
  if (scriptCalls === 4 && result.status === 'SUCCESS') {
    console.log(`✅ Passed (${scriptCalls} script calls recorded)`);
  } else {
    throw new Error(`Retry failed: ${scriptCalls} script calls, status ${result.status}`);
  }
}

async function test_mission_evaluation() {
  console.log('[TEST] Mission Success Criteria (D8)...');
  const transcript = { events: [{ type: 'ACTION_SUCCESS' }] };
  const verdict = await MissionEvaluator.evaluate('Test Goal', transcript, 'https://example.com');
  if (verdict.success === true) {
    console.log('✅ Passed');
  } else {
    throw new Error('Evaluation failed');
  }
}

async function run_all() {
  console.log('=== NANO-FORGE PRECISE MODE TEST HARNESS ===');
  try {
    await test_transcript_logging();
    await test_retry_policy();
    await test_mission_evaluation();
    console.log('\n✨ ALL TESTS RADIANT');
  } catch (e) {
    console.error(`\n❌ TEST FAILED: ${e.message}`);
    process.exit(1);
  }
}

run_all();
