// SPDX-License-Identifier: MIT

/**
 * Verification Suite: Specialized Skills
 * Validates: Skill Registry, Executor Routing
 */

import { ActionExecutor } from '../src/logic/action_executor.js';
import { SPECIALIZED_SKILLS } from '../src/logic/specialized_skills.js';

// Mock Browser
global.chrome = {
  tabs: { get: async () => ({ url: 'http://test.com' }) },
  scripting: {
    executeScript: async ({ target, func }) => {
      // SIMULATE CONTENT SCRIPT ENV
      global.window = { location: { origin: 'http://test.com', protocol: 'https:' } };
      global.document = {
        querySelectorAll: (sel) => {
          if (sel.includes('a[href]'))
            return [
              { href: 'http://test.com/doc A' },
              { href: 'http://test.com/api/v1' },
              { href: 'http://external.com' }, // Should be filtered
            ];
          if (sel.includes('script'))
            return [
              { innerText: "console.log('hi')" },
              { innerText: 'alert(1)' },
              { innerText: 'track()' },
              { innerText: 'ads()' },
              { innerText: 'analytics()' },
              { innerText: 'more()' },
            ]; // 6 scripts with content
          return [];
        },
        querySelector: () => null,
      };

      const res = func();
      return [{ result: res }];
    },
  },
};

async function runTest() {
  console.log('🛡️ VERIFYING SPECIALIZED SKILLS...\n');
  let passed = 0;

  // TEST 1: Registry Lookup
  if (SPECIALIZED_SKILLS['RECURSIVE_CRAWL'] && SPECIALIZED_SKILLS['AUDIT_SECURITY']) {
    console.log('✅ Registry: Skills Loaded');
    passed++;
  } else console.error('❌ Registry Failed');

  // TEST 2: Action Executor Routing (Crawl)
  try {
    const res = await ActionExecutor.perform(1, { action: 'RECURSIVE_CRAWL' });
    if (res.status === 'SUCCESS' && res.data.links.length === 2) {
      console.log('✅ Executor: Crawl Logic Executed (Filtered external links)');
      passed++;
    } else console.error('❌ Executor Crawl Failed', res);
  } catch (e) {
    console.error(e);
  }

  // TEST 3: Action Executor Routing (Security)
  try {
    const res = await ActionExecutor.perform(1, { action: 'AUDIT_SECURITY' });
    if (res.status === 'SUCCESS' && res.data.riskScore >= 20) {
      console.log('✅ Executor: Security Audit Executed (Detected high script count)');
      passed++;
    } else console.error('❌ Executor Security Failed', res);
  } catch (e) {
    console.error(e);
  }

  console.log(`\n🏁 VERIFICATION COMPLETE: ${passed} PASSED`);
}

runTest();
