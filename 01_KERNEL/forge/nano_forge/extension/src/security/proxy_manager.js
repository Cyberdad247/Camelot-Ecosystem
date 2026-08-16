// SPDX-License-Identifier: MIT

// 🌐 PROXY MANAGER (Residential & Rotating)
// Manages: Proxy Settings, Auth, IP Rotation, Header Spoofing

const DEFAULT_PROXY_CONFIG = {
  mode: 'direct', // 'direct' | 'fixed_servers' | 'pac_script'
  host: '',
  port: '',
  username: '',
  password: '',
  rotateOnBan: true,
  rotationInterval: 0, // 0 = disabled
};

class ProxyManager {
  constructor() {
    this.config = DEFAULT_PROXY_CONFIG;
    this.banDetected = false;
    this.rotationTimer = null;
  }

  async applyConfig(config) {
    this.config = { ...this.config, ...config };

    if (this.config.mode === 'direct') {
      await this.clearProxy();
      return;
    }

    const proxyConfig = {
      mode: 'fixed_servers',
      rules: {
        singleProxy: {
          scheme: 'http',
          host: this.config.host,
          port: parseInt(this.config.port),
        },
        bypassList: ['localhost', '127.0.0.1'],
      },
    };

    chrome.proxy.settings.set({ value: proxyConfig, scope: 'regular' }, () => {
      console.log(`[PROXY] Applied: ${this.config.host}:${this.config.port}`);
      if (this.config.rotationInterval > 0) {
        this.startRotation();
      }
    });

    // Handle Auth
    // Note: Chrome doesn't support programmatic auth for proxies easily in V3 without OnAuthRequired
    // We need to add a listener in background.js or here if we export valid logic.
  }

  async clearProxy() {
    chrome.proxy.settings.clear({ scope: 'regular' });
    this.stopRotation();
    console.log('[PROXY] Cleared (Direct Mode)');
  }

  startRotation() {
    this.stopRotation();
    this.rotationTimer = setInterval(
      () => {
        console.log('[PROXY] Rotating IP...');
        // Real implementation would call a proxy provider API to get a new node
        // For now we simulate by re-applying (or notification)
      },
      this.config.rotationInterval * 60 * 1000,
    );
  }

  stopRotation() {
    if (this.rotationTimer) clearInterval(this.rotationTimer);
  }

  // Header Spoofing via DeclarativeNetRequest
  async updateHeaders(userAgent) {
    await chrome.declarativeNetRequest.updateDynamicRules({
      removeRuleIds: [1],
      addRules: [
        {
          id: 1,
          priority: 1,
          action: {
            type: 'modifyHeaders',
            requestHeaders: [
              { header: 'User-Agent', operation: 'set', value: userAgent },
              { header: 'Sec-CH-UA', operation: 'remove' },
              { header: 'Sec-CH-UA-Platform', operation: 'remove' },
            ],
          },
          condition: {
            urlFilter: '*',
            resourceTypes: ['main_frame', 'sub_frame', 'xmlhttprequest', 'script'],
          },
        },
      ],
    });
    console.log('[NETWORK] Headers Spoofed.');
  }
}

const proxyManager = new ProxyManager();
self.ProxyManager = proxyManager;

// MANIFEST V3 COMPATIBILITY NOTE:
// `chrome.webRequest.onAuthRequired` with "blocking" is NOT supported in MV3.
// For authenticated proxies in MV3, use one of these approaches:
// 1. Embed credentials in the proxy URL: http://user:pass@proxy.example.com:8080
// 2. Use a PAC script that handles auth.
// 3. Use a native messaging host for credential injection.

// Non-blocking auth logging (for debugging only)
if (chrome.webRequest && chrome.webRequest.onAuthRequired) {
  chrome.webRequest.onAuthRequired.addListener(
    (details) => {
      console.warn('[PROXY] Auth Required for:', details.challenger);
      // In MV3, we cannot provide credentials synchronously.
      // User must configure proxy with embedded credentials.
    },
    { urls: ['<all_urls>'] },
    // NOTE: No "blocking" option - this is just a logger now.
  );
}
