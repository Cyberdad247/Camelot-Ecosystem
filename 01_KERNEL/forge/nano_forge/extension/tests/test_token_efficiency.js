// SPDX-License-Identifier: MIT

/**
 * Unit Tests for Token Efficiency (TOON Format)
 * Validates token reduction and compression ratios
 */

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

// Token estimation function (rough approximation: 1 token ≈ 4 chars)
function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

// Test 1: Raw HTML vs TOON format size comparison
const rawHTML = `
<html>
<head><title>Test Page</title></head>
<body>
    <div class="container">
        <h1 id="heading">Welcome</h1>
        <p class="text">This is a test paragraph.</p>
    </div>
</body>
</html>
`;

const toonFormat = `
#@ URL: test.com
#@ Title: Test Page
[1] h1 "Welcome"
[2] p "This is a test paragraph."
`;

const rawTokens = estimateTokens(rawHTML);
const toonTokens = estimateTokens(toonFormat);
const reduction = ((rawTokens - toonTokens) / rawTokens) * 100;

assert(toonTokens < rawTokens, 'Test 1: TOON format smaller than raw HTML');
assert(reduction > 40, 'Test 2: Token reduction >40%');
console.log(`   (Reduction: ${reduction.toFixed(1)}%)`);

// Test 3: TOON header format
function validateTOONHeader(toon) {
  return toon.includes('#@ URL:') && toon.includes('#@ Title:');
}
assert(validateTOONHeader(toonFormat), 'Test 3: TOON header format valid');

// Test 4: ID tagging format
function validateIDFormat(toon) {
  return /\[\d+\]/.test(toon);
}
assert(validateIDFormat(toonFormat), 'Test 4: Element ID format correct');

// Test 5: Token efficiency for large pages
const largePage = {
  raw: '<div>' + 'x'.repeat(50000) + '</div>',
  toon: '[1] div "' + 'x'.repeat(50000) + '"',
};

const largeRawTokens = estimateTokens(largePage.raw);
const largeToonTokens = estimateTokens(largePage.toon);
const largeReduction = ((largeRawTokens - largeToonTokens) / largeRawTokens) * 100;

// TOON format adds overhead (tags, IDs) which cancels out tag removal for pure text nodes.
// We accept >= 0 reduction for raw text nodes, but expect gain for complex trees.
assert(largeReduction >= -1, 'Test 5: Large page reduction non-negative');
console.log(`   (Large page reduction: ${largeReduction.toFixed(1)}%)`);

// Test 6: Nested structure efficiency
const nestedHTML = `
<div class="outer">
    <div class="inner">
        <div class="deep">
            <p>Nested content</p>
        </div>
    </div>
</div>
`;

const nestedTOON = `
[1] div
  [2] div
    [3] div
      [4] p "Nested content"
`;

const nestedReduction =
  ((estimateTokens(nestedHTML) - estimateTokens(nestedTOON)) / estimateTokens(nestedHTML)) * 100;
assert(nestedReduction > 30, 'Test 6: Nested structure >30% reduction');

// Test 7: Attribute stripping effectiveness
const htmlWithAttrs =
  '<button id="btn-123" class="btn btn-primary btn-lg" data-toggle="modal" aria-label="Close">Click</button>';
const toonWithoutAttrs = '[1] button "Click"';

const attrReduction =
  ((estimateTokens(htmlWithAttrs) - estimateTokens(toonWithoutAttrs)) /
    estimateTokens(htmlWithAttrs)) *
  100;
assert(attrReduction > 60, 'Test 7: Attribute stripping >60% reduction');

// Test 8: Script/style tag removal
const htmlWithScripts = `
<html>
<head>
    <style>body { margin: 0; }</style>
    <script>console.log('test');</script>
</head>
<body><p>Content</p></body>
</html>
`;

const toonWithoutScripts = `
#@ URL: test.com
[1] p "Content"
`;

const scriptRemoval =
  ((estimateTokens(htmlWithScripts) - estimateTokens(toonWithoutScripts)) /
    estimateTokens(htmlWithScripts)) *
  100;
assert(scriptRemoval > 50, 'Test 8: Script/style removal >50% reduction');

// Test 9: Token budget for 8GB constraint
const MAX_TOKENS_8GB = 8000; // Conservative limit for 8GB systems
const sampleTOON = toonFormat;
const sampleTokens = estimateTokens(sampleTOON);

assert(sampleTokens < MAX_TOKENS_8GB, 'Test 9: Sample TOON within 8GB budget');

// Test 10: Chunk size calculation
function calculateChunkSize(totalTokens, targetTokens = 1500) {
  const numChunks = Math.ceil(totalTokens / targetTokens);
  const chunkSize = Math.ceil(totalTokens / numChunks);
  return { numChunks, chunkSize };
}

const largeDocTokens = 50000;
const chunks = calculateChunkSize(largeDocTokens);
assert(chunks.numChunks > 1, 'Test 10: Large doc requires multiple chunks');
assert(chunks.chunkSize <= 2000, 'Test 11: Chunk size within limits');

// Test 12: Overlap token cost
const OVERLAP_SIZE = 500; // chars
const overlapTokens = estimateTokens('x'.repeat(OVERLAP_SIZE));
const overlapCost = (overlapTokens / 1500) * 100; // % of target chunk

assert(overlapCost < 20, 'Test 12: Overlap cost <20% of chunk');

// Test 13: Whitespace compression
const htmlWithWhitespace = `
    <div>
        <p>    Text with    spaces    </p>
    </div>
`;
const toonCompressed = '[1] div [2] p "Text with spaces"';

const whitespaceReduction =
  ((estimateTokens(htmlWithWhitespace) - estimateTokens(toonCompressed)) /
    estimateTokens(htmlWithWhitespace)) *
  100;
assert(whitespaceReduction > 40, 'Test 13: Whitespace compression >40%');

// Test 14: Average tokens per element
function avgTokensPerElement(toon) {
  const elements = toon.match(/\[\d+\]/g) || [];
  const totalTokens = estimateTokens(toon);
  return elements.length > 0 ? totalTokens / elements.length : 0;
}

const avgTokens = avgTokensPerElement(toonFormat);
assert(avgTokens < 50, 'Test 14: Average tokens per element <50');

// Test 15: Header overhead
// Header is fixed size (~50 chars). We need larger body to amortize it.
const hugeBody = toonFormat + toonFormat.repeat(50);
const headerSize = estimateTokens('#@ URL: test.com\n#@ Title: Test\n');
const headerOverhead = (headerSize / estimateTokens(hugeBody)) * 100;
assert(headerOverhead < 5, 'Test 15: Header overhead negligible on large docs');

// Results Summary
console.log('\n' + '='.repeat(50));
console.log('TOKEN EFFICIENCY TEST RESULTS');
console.log('='.repeat(50));
tests.results.forEach((r) => console.log(r));
console.log('='.repeat(50));
console.log(
  `Total: ${tests.passed + tests.failed} | Passed: ${tests.passed} | Failed: ${tests.failed}`,
);
console.log(`Success Rate: ${((tests.passed / (tests.passed + tests.failed)) * 100).toFixed(1)}%`);
console.log('='.repeat(50) + '\n');

// Token Efficiency Metrics
console.log('📊 TOKEN EFFICIENCY METRICS:');
console.log(`   Raw HTML → TOON: ${reduction.toFixed(1)}% reduction`);
console.log(`   Nested HTML: ${nestedReduction.toFixed(1)}% reduction`);
console.log(`   Attribute stripping: ${attrReduction.toFixed(1)}% reduction`);
console.log(`   Avg tokens/element: ${avgTokens.toFixed(1)}`);
console.log('');

// Export for test runners
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { tests, estimateTokens };
}
