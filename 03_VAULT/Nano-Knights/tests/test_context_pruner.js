/**
 * Unit Tests for ContextPruner
 * Tests memory management and pruning logic
 */

import { ContextPruner } from '../src/logic/context_pruner.js';

const tests = {
  passed: 0,
  failed: 0,
  results: [],
};

function assert(condition, testName) {
  if (condition) {
    tests.passed++;
    tests.results.push(`✅ ${testName}`);
  } else {
    tests.failed++;
    tests.results.push(`❌ ${testName}`);
    console.error(`FAILED: ${testName}`);
  }
}

// Test 1: Empty memory array
const test1 = ContextPruner.prune([]);
assert(test1.length === 0, 'Test 1: Empty array returns empty');

// Test 2: Memory under limit (no pruning needed)
const smallMemory = [
  { timestamp: '2024-01-01T10:00:00Z', skill: 'PROMPT_TO_ACTION', content: 'action1' },
  { timestamp: '2024-01-01T10:01:00Z', skill: 'PROMPT_TO_ACTION', content: 'action2' },
];
const test2 = ContextPruner.prune(smallMemory);
assert(test2.length === 2, 'Test 2: Small memory not pruned');

// Test 3: Preserve latest summary
const memoryWithSummary = [
  { timestamp: '2024-01-01T10:00:00Z', skill: 'PROMPT_TO_ACTION', content: 'old action' },
  { timestamp: '2024-01-01T10:01:00Z', skill: 'SUMMARIZE_CORE', content: 'page summary' },
  { timestamp: '2024-01-01T10:02:00Z', skill: 'PROMPT_TO_ACTION', content: 'action1' },
  { timestamp: '2024-01-01T10:03:00Z', skill: 'PROMPT_TO_ACTION', content: 'action2' },
  { timestamp: '2024-01-01T10:04:00Z', skill: 'PROMPT_TO_ACTION', content: 'action3' },
  { timestamp: '2024-01-01T10:05:00Z', skill: 'PROMPT_TO_ACTION', content: 'action4' },
];
const test3 = ContextPruner.prune(memoryWithSummary);
assert(
  test3.some((m) => m.skill === 'SUMMARIZE_CORE'),
  'Test 3: Summary preserved',
);
assert(test3.length <= 4, 'Test 3: Memory pruned to reasonable size');

// Test 4: Keep last N actions
const largeMemory = Array.from({ length: 20 }, (_, i) => ({
  timestamp: `2024-01-01T${String(10 + i).padStart(2, '0')}:00:00Z`,
  skill: 'PROMPT_TO_ACTION',
  content: `action${i}`,
}));
const test4 = ContextPruner.prune(largeMemory);
assert(test4.length <= ContextPruner.MAX_ACTIONS, 'Test 4: Respects MAX_ACTIONS limit');
assert(test4[test4.length - 1].content.includes('19'), 'Test 4: Keeps most recent actions');

// Test 5: Vision/Screenshot summary preservation
const memoryWithVision = [
  { timestamp: '2024-01-01T10:00:00Z', skill: 'PROMPT_TO_ACTION', content: 'old1' },
  { timestamp: '2024-01-01T10:01:00Z', skill: 'ANALYZE_SCREENSHOT', content: 'visual analysis' },
  { timestamp: '2024-01-01T10:02:00Z', skill: 'PROMPT_TO_ACTION', content: 'action1' },
  { timestamp: '2024-01-01T10:03:00Z', skill: 'PROMPT_TO_ACTION', content: 'action2' },
];
const test5 = ContextPruner.prune(memoryWithVision);
assert(
  test5.some((m) => m.skill === 'ANALYZE_SCREENSHOT'),
  'Test 5: Screenshot analysis preserved',
);

// Test 6: Chronological ordering maintained
const unorderedMemory = [
  { timestamp: '2024-01-01T10:05:00Z', skill: 'PROMPT_TO_ACTION', content: 'last' },
  { timestamp: '2024-01-01T10:01:00Z', skill: 'SUMMARIZE_CORE', content: 'summary' },
  { timestamp: '2024-01-01T10:03:00Z', skill: 'PROMPT_TO_ACTION', content: 'middle' },
];
const test6 = ContextPruner.prune(unorderedMemory);
assert(
  test6[0].timestamp <= test6[test6.length - 1].timestamp,
  'Test 6: Chronological order maintained',
);

// Test 7: Null/undefined handling
const test7a = ContextPruner.prune(null);
assert(test7a.length === 0, 'Test 7a: Null input returns empty');

const test7b = ContextPruner.prune(undefined);
assert(test7b.length === 0, 'Test 7b: Undefined input returns empty');

// Test 8: Deduplication
const memoryWithDupes = [
  { timestamp: '2024-01-01T10:00:00Z', skill: 'SUMMARIZE_CORE', content: 'summary' },
  { timestamp: '2024-01-01T10:00:00Z', skill: 'SUMMARIZE_CORE', content: 'summary' }, // duplicate
];
const test8 = ContextPruner.prune(memoryWithDupes);
assert(test8.length === 1, 'Test 8: Duplicates removed');

// Results Summary
console.log('\n' + '='.repeat(50));
console.log('CONTEXT PRUNER TEST RESULTS');
console.log('='.repeat(50));
tests.results.forEach((r) => console.log(r));
console.log('='.repeat(50));
console.log(
  `Total: ${tests.passed + tests.failed} | Passed: ${tests.passed} | Failed: ${tests.failed}`,
);
console.log(`Success Rate: ${((tests.passed / (tests.passed + tests.failed)) * 100).toFixed(1)}%`);
console.log('='.repeat(50) + '\n');

// Export for test runners
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { tests };
}
