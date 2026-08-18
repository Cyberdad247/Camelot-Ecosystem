// SPDX-License-Identifier: MIT

// HIVE CRAWLER (Sub-Agent)
// Injected into background tabs by Lady Apis (Hive Protocol)

(function notifyHive() {
  // 1. Basic Metadata Extraction
  const title = document.title;
  const url = window.location.href;
  const metaDesc = document.querySelector('meta[name="description"]')?.content;
  const headers = Array.from(document.querySelectorAll('h1, h2, h3')).map((h) =>
    h.innerText.trim(),
  );

  // 2. Identify High-Value Targets (Docs, Configs, APIs)
  const isHighValue = /api|docs|guide|reference|config|schema/i.test(
    document.body.innerText.substring(0, 2000),
  );

  // 3. Report Back to Mothership
  const intel = {
    agent: 'LADY_APIS_DRONE',
    url: url,
    title: title,
    summary: metaDesc || 'No meta description',
    structure: headers.slice(0, 10), // First 10 headers
    isHighValue: isHighValue,
    timestamp: new Date().toISOString(),
  };

  // Send to Background.js
  chrome.runtime.sendMessage({
    action: 'REPORT_INTEL',
    agent: 'LADY_APIS_DRONE',
    topic: 'HIVE_CRAWL',
    data: JSON.stringify(intel),
  });
})();
