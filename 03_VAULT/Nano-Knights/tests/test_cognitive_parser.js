/**
 * Unit Tests for CognitiveParser
 * Tests tag extraction and content separation
 */

import { CognitiveParser } from '../src/logic/cognitive_parser.js';

// Test Suite
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

// Test 1: Basic tag extraction
const test1 = CognitiveParser.parse(
  '[AttentionFocus: User query analysis]\n[OUTPUT START]\nFinal response',
);
assertEqual(test1.tags.AttentionFocus, 'User query analysis', 'Test 1: Extract AttentionFocus tag');
assertEqual(test1.content, 'Final response', 'Test 1: Extract content after OUTPUT START');

// Test 2: Multiple tags
const test2 = CognitiveParser.parse(
  '[AttentionFocus: Login workflow]\n[TheoryOfMind: User expects simplicity]\n[ReasoningPathway: Check credentials → Verify 2FA]\n[OUTPUT START]\nLogin successful',
);
assertEqual(test2.tags.AttentionFocus, 'Login workflow', 'Test 2: Multiple tags - AttentionFocus');
assertEqual(
  test2.tags.TheoryOfMind,
  'User expects simplicity',
  'Test 2: Multiple tags - TheoryOfMind',
);
assertEqual(
  test2.tags.ReasoningPathway,
  'Check credentials → Verify 2FA',
  'Test 2: Multiple tags - ReasoningPathway',
);
assertEqual(test2.content, 'Login successful', 'Test 2: Content extraction with multiple tags');

// Test 3: No tags (raw content)
const test3 = CognitiveParser.parse('Just plain content without tags');
assertEqual(Object.keys(test3.tags).length, 0, 'Test 3: No tags detected');
assertEqual(test3.content, 'Just plain content without tags', 'Test 3: Raw content passthrough');

// Test 4: No OUTPUT START marker (fallback)
const test4 = CognitiveParser.parse('[AttentionFocus: Research]\nSome content here');
assertEqual(test4.tags.AttentionFocus, 'Research', 'Test 4: Tag extracted without OUTPUT START');
assert(test4.content.includes('Some content here'), 'Test 4: Content preserved when no marker');

// Test 5: Empty input
const test5 = CognitiveParser.parse('');
assertEqual(test5.tags, {}, 'Test 5: Empty input returns empty tags');
assertEqual(test5.content, '', 'Test 5: Empty input returns empty content');

// Test 6: Complex nested content
const test6 = CognitiveParser.parse(
  '[Metacognition: This requires deep analysis]\n[CognitiveOperations: [ANALYZE, SYNTHESIZE, VERIFY]]\n[OUTPUT START]\n{"result": "complex data"}',
);
assertEqual(test6.tags.Metacognition, 'This requires deep analysis', 'Test 6: Metacognition tag');
assert(
  test6.tags.CognitiveOperations.includes('ANALYZE'),
  'Test 6: CognitiveOperations with array',
);
assert(test6.content.includes('complex data'), 'Test 6: JSON content preserved');

// Test 7: Tag with multiline content
const test7 = CognitiveParser.parse(
  '[ReasoningPathway: Step 1: Analyze\nStep 2: Execute\nStep 3: Verify]\n[OUTPUT START]\nDone',
);
assert(test7.tags.ReasoningPathway.includes('Step 2'), 'Test 7: Multiline tag content preserved');
assertEqual(test7.content, 'Done', 'Test 7: Content after multiline tag');

// Results Summary
console.log('\n' + '='.repeat(50));
console.log('COGNITIVE PARSER TEST RESULTS');
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
