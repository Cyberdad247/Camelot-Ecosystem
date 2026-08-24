/**
 * Unit Tests for VoiceSquire
 * Tests wake word detection and command extraction
 */

import { VoiceSquire } from '../src/squires/voice_squire.js';

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

// Create instance
const voiceSquire = new VoiceSquire();

// Test 1: Wake word "nano" detection
const test1 = voiceSquire.extractCommand('Nano, research quantum computing');
assert(test1 !== null, 'Test 1: Detects nano wake word');
assertEqual(test1.wakeWord, 'nano', 'Test 1: Correct wake word identified');
assertEqual(test1.command, 'research quantum computing', 'Test 1: Command extracted correctly');

// Test 2: Wake word "anya" detection
const test2 = voiceSquire.extractCommand('Anya, queue this task');
assert(test2 !== null, 'Test 2: Detects anya wake word');
assertEqual(test2.wakeWord, 'anya', 'Test 2: Correct wake word identified');
assertEqual(test2.command, 'queue this task', 'Test 2: Command extracted correctly');

// Test 3: Wake word "merlin" detection
const test3 = voiceSquire.extractCommand('Merlin, show status');
assert(test3 !== null, 'Test 3: Detects merlin wake word');
assertEqual(test3.wakeWord, 'merlin', 'Test 3: Correct wake word identified');
assertEqual(test3.command, 'show status', 'Test 3: Command extracted correctly');

// Test 4: No wake word (should return null)
const test4 = voiceSquire.extractCommand('Just talking about research');
assertEqual(test4, null, 'Test 4: Returns null when no wake word');

// Test 5: Wake word with no command
const test5 = voiceSquire.extractCommand('Nano');
assertEqual(test5, null, 'Test 5: Returns null when wake word has no command');

// Test 6: Wake word in middle of sentence
const test6 = voiceSquire.extractCommand("I said nano but this isn't a command");
assert(test6 !== null, 'Test 6: Detects wake word in middle');
assert(test6.command.includes("this isn't"), 'Test 6: Extracts command after wake word');

// Test 7: Case insensitivity
const test7 = voiceSquire.extractCommand('NANO, RESEARCH AI');
assert(test7 !== null, 'Test 7: Case insensitive wake word detection');
assert(test7.command.toLowerCase().includes('research'), 'Test 7: Case preserved in command');

// Test 8: Multiple wake words (first one wins)
const test8 = voiceSquire.extractCommand('Nano, tell Anya to research');
assertEqual(test8.wakeWord, 'nano', 'Test 8: First wake word takes precedence');
assert(test8.command.includes('Anya'), 'Test 8: Rest of sentence preserved');

// Test 9: Empty string
const test9 = voiceSquire.extractCommand('');
assertEqual(test9, null, 'Test 9: Empty string returns null');

// Test 10: Wake word with punctuation
const test10 = voiceSquire.extractCommand('Nano, research AI!');
assert(test10 !== null, 'Test 10: Handles punctuation');
assert(test10.command.includes('research'), 'Test 10: Command extracted with punctuation');

// Results Summary
console.log('\n' + '='.repeat(50));
console.log('VOICE SQUIRE TEST RESULTS');
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
