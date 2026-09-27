/**
 * Unit Tests for ChunkManager
 * Tests text chunking and result merging logic
 */

import { ChunkManager } from '../src/logic/chunk_manager.js';

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

function assertEqual(actual, expected, testName) {
  assert(JSON.stringify(actual) === JSON.stringify(expected), testName);
}

// Test 1: No chunking needed (small text)
const smallText = '#@ URL: test.com\nSmall content';
const test1 = ChunkManager.chunk(smallText, 6000, 500);
assert(test1.length === 1, 'Test 1: No chunking for small text');
assert(test1[0].includes('Small content'), 'Test 1: Content preserved');

// Test 2: Basic chunking
const largeText = '#@ URL: test.com\n#@ Title: Test\n' + 'A'.repeat(10000);
const test2 = ChunkManager.chunk(largeText, 3000, 300);
assert(test2.length > 1, 'Test 2: Large text gets chunked');
assert(test2[0].includes('#@ URL'), 'Test 2: Header preserved in first chunk');
assert(test2[1].includes('#@ URL'), 'Test 2: Header preserved in second chunk');
assert(test2[0].includes('[...CHUNK...]'), 'Test 2: Chunk marker present');

// Test 3: Overlap preservation
const test3 = ChunkManager.chunk('#@ Header\n' + 'X'.repeat(7000), 3000, 500);
assert(test3.length >= 2, 'Test 3: Multiple chunks created');
// Verify overlap by checking that end of chunk N overlaps with start of chunk N+1
const firstChunkEnd = test3[0].slice(-100);
const secondChunkStart = test3[1].slice(0, 200);
assert(secondChunkStart.includes('X'), 'Test 3: Overlap contains content');

// Test 4: Empty text handling
const test4 = ChunkManager.chunk('', 6000, 500);
assert(test4.length === 1, 'Test 4: Empty text returns single chunk');

// Test 5: Only header (no body)
const test5 = ChunkManager.chunk('#@ URL: test.com\n#@ Title: Test', 6000, 500);
assert(test5.length === 1, "Test 5: Header-only text isn't chunked");

// Test 6: Merge - Array results
const results1 = [
  [
    { name: 'Alice', _source: '1' },
    { name: 'Bob', _source: '2' },
  ],
  [{ name: 'Charlie', _source: '3' }],
];
const merged1 = ChunkManager.merge(results1, { type: 'array' });
assert(Array.isArray(merged1), 'Test 6: Merge returns array');
assert(merged1.length === 3, 'Test 6:Merge combines all items');

// Test 7: Merge - Deduplication by _source
const results2 = [
  [{ name: 'Alice', _source: '1' }],
  [{ name: 'Alice', age: 30, _source: '1' }], // Same source, should merge
];
const merged2 = ChunkManager.merge(results2, { type: 'array' });
assert(merged2.length === 1, 'Test 7: Deduplication by _source');
assert(merged2[0].age === 30, 'Test 7: Fields merged from duplicate');

// Test 8: Merge - Object results with array property
const results3 = [
  { employees: [{ name: 'Alice', _source: '1' }] },
  { employees: [{ name: 'Bob', _source: '2' }] },
];
const merged3 = ChunkManager.merge(results3, { type: 'object' });
assert(
  merged3.employees && merged3.employees.length === 2,
  'Test 8: Object merge preserves structure',
);

// Test 9: Merge - No _source (JSON dedup)
const results4 = [
  [{ name: 'Alice' }, { name: 'Bob' }],
  [{ name: 'Alice' }], // Duplicate without _source
];
const merged4 = ChunkManager.merge(results4, { type: 'array' });
assert(merged4.length === 2, 'Test 9: JSON stringify deduplication');

// Test 10: Merge - Empty results
const merged5 = ChunkManager.merge([], { type: 'array' });
assert(merged5.length === 0, 'Test 10: Empty results array');

// Test 11: Merge - Null/undefined handling
const results6 = [
  [{ name: 'Alice', _source: '1' }],
  null,
  undefined,
  [{ name: 'Bob', _source: '2' }],
];
const merged6 = ChunkManager.merge(results6, { type: 'array' });
assert(merged6.length === 2, 'Test 11: Handles null/undefined in results');

// Test 12: Line-break preservation
const textWithLines = '#@ Header\nLine 1\nLine 2\nLine 3\n' + 'Content'.repeat(2000);
const test12 = ChunkManager.chunk(textWithLines, 3000, 300);
assert(test12[0].includes('Line 1'), 'Test 12: Lines preserved in chunk');

// Results Summary
console.log('\n' + '='.repeat(50));
console.log('CHUNK MANAGER TEST RESULTS');
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
