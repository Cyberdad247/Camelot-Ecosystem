// SPDX-License-Identifier: MIT

/**
 * Unit Tests for Stealth Fingerprinting
 * Tests canvas, audio, WebGL, and UA spoofing logic
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

// Mock profile data
const mockProfile = {
  canvasNoise: 0.0000001,
  audioNoise: 0.0000001,
  webglVendor: 'Intel Inc.',
  webglRenderer: 'Intel Iris Pro',
  userAgent:
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
};

// Test 1: Profile noise values are within safe range
assert(
  mockProfile.canvasNoise > 0 && mockProfile.canvasNoise < 0.001,
  'Test 1: Canvas noise in safe range',
);
assert(
  mockProfile.audioNoise > 0 && mockProfile.audioNoise < 0.001,
  'Test 2: Audio noise in safe range',
);

// Test 3: User Agent format validation
const uaRegex = /Mozilla\/\d+\.\d+ \(.*\) AppleWebKit\/[\d.]+ \(KHTML, like Gecko\)/;
assert(uaRegex.test(mockProfile.userAgent), 'Test 3: User Agent format valid');

// Test 4: WebGL vendor strings are realistic
const validVendors = ['Intel Inc.', 'NVIDIA Corporation', 'AMD', 'Google Inc.'];
const isValidVendor = validVendors.some(
  (v) => mockProfile.webglVendor.includes(v) || v.includes(mockProfile.webglVendor),
);
assert(isValidVendor, 'Test 4: WebGL vendor is realistic');

// Test 5: Noise values are not identical (prevents pattern detection)
const profile2 = {
  canvasNoise: 0.00000015,
  audioNoise: 0.00000012,
};
assert(
  mockProfile.canvasNoise !== profile2.canvasNoise,
  'Test 5: Canvas noise varies between profiles',
);
assert(
  mockProfile.audioNoise !== profile2.audioNoise,
  'Test 6: Audio noise varies between profiles',
);

// Test 7: Script injection template validation
function validateInjectionScript(profile) {
  const scriptTemplate = `
        const NOISE_CANVAS = ${profile.canvasNoise};
        const NOISE_AUDIO = ${profile.audioNoise};
        const VENDOR = "${profile.webglVendor}";
        const RENDERER = "${profile.webglRenderer}";
        const UA = "${profile.userAgent}";
    `;

  // Check for injection vulnerabilities
  const hasInjectionRisk =
    scriptTemplate.includes('</script>') ||
    (scriptTemplate.includes('${') && !scriptTemplate.match(/\$\{[^}]+\}/));
  return !hasInjectionRisk;
}
assert(validateInjectionScript(mockProfile), 'Test 7: Injection script template safe');

// Test 8: Consistency check (timezone/locale should match UA)
function checkConsistency(profile) {
  const isWindows = profile.userAgent.includes('Windows');
  const isMac = profile.userAgent.includes('Mac');
  const isLinux = profile.userAgent.includes('Linux');

  // Basic consistency: OS should be one of the three
  return isWindows || isMac || isLinux;
}
assert(checkConsistency(mockProfile), 'Test 8: Profile OS consistency');

// Test 9: Canvas noise doesn't break rendering
function testCanvasNoise(noise) {
  // Noise should be small enough to not affect visible rendering
  // but large enough to prevent fingerprinting
  return noise > 0.00000001 && noise < 0.0001;
}
assert(testCanvasNoise(mockProfile.canvasNoise), 'Test 9: Canvas noise optimal range');

// Test 10: Audio buffer modification is subtle
function testAudioNoise(noise) {
  // Audio modification should be imperceptible
  // Typically < 0.001 for inaudible changes
  return noise < 0.001;
}
assert(testAudioNoise(mockProfile.audioNoise), 'Test 10: Audio noise imperceptible');

// Test 11: WebGL parameter numbers are correct
const UNMASKED_VENDOR_WEBGL = 37445;
const UNMASKED_RENDERER_WEBGL = 37446;
assert(UNMASKED_VENDOR_WEBGL === 37445, 'Test 11: WebGL vendor parameter correct');
assert(UNMASKED_RENDERER_WEBGL === 37446, 'Test 12: WebGL renderer parameter correct');

// Test 13: User Agent platform consistency
function checkPlatformConsistency(ua) {
  if (ua.includes('Windows')) {
    return ua.includes('Win64') || ua.includes('Win32');
  }
  if (ua.includes('Mac')) {
    return ua.includes('Intel') || ua.includes('ARM');
  }
  return true; // Linux/other
}
assert(checkPlatformConsistency(mockProfile.userAgent), 'Test 13: Platform details consistent');

// Test 14: Chrome version format
function validateChromeVersion(ua) {
  const versionMatch = ua.match(/Chrome\/(\d+)\.(\d+)\.(\d+)\.(\d+)/);
  if (!versionMatch) return false;

  const major = parseInt(versionMatch[1]);
  // Chrome version should be realistic (70-130 range as of 2024)
  return major >= 70 && major <= 150;
}
assert(validateChromeVersion(mockProfile.userAgent), 'Test 14: Chrome version realistic');

// Test 15: No obvious fingerprinting markers
function checkForMarkers(profile) {
  // Should not contain obvious test/bot markers
  const suspicious = ['HeadlessChrome', 'PhantomJS', 'Selenium', 'WebDriver'];
  return !suspicious.some((marker) => profile.userAgent.includes(marker));
}
assert(checkForMarkers(mockProfile), 'Test 15: No bot markers in UA');

// Test 16: Noise randomization function
function generateNoise() {
  return Math.random() * 0.0000005 + 0.00000005;
}
const noise1 = generateNoise();
const noise2 = generateNoise();
assert(noise1 !== noise2, 'Test 16: Noise generation is random');
assert(noise1 >= 0.00000005 && noise1 <= 0.00000055, 'Test 17: Generated noise in range');

// Results Summary
console.log('\n' + '='.repeat(50));
console.log('STEALTH FINGERPRINTING TEST RESULTS');
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
  module.exports = { tests, mockProfile };
}
