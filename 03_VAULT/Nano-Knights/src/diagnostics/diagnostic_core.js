export class DiagnosticCore {
  constructor() {
    this.results = {
      deployment: [],
      integration: [],
      execution: [],
      ui: [],
      ux: [],
      score: 0,
    };
  }

  async runAll() {
    console.log('⚡ [DIAGNOSTIC] Starting Full System Scan...');

    await this.testDeployment();
    await this.testIntegration();
    await this.testExecution();
    await this.testUI();
    await this.testUX();

    return this.calculateScore();
  }

  // T1: Deployment
  async testDeployment() {
    console.log('   > Testing Deployment...');
    // 1. Check Storage Access
    try {
      await chrome.storage.local.set({ _diag_test: Date.now() });
      const data = await chrome.storage.local.get('_diag_test');
      if (data._diag_test) this.log('deployment', 'PASS', 'Storage Write/Read');
      else this.log('deployment', 'FAIL', 'Storage Persistence');
    } catch (e) {
      this.log('deployment', 'FAIL', `Storage Error: ${e.message}`);
    }

    // 2. Manifest Version
    const manifest = chrome.runtime.getManifest();
    if (manifest.version) this.log('deployment', 'PASS', `Manifest Version: ${manifest.version}`);
    else this.log('deployment', 'FAIL', 'Manifest Version Missing');
  }

  // T2: Integration
  async testIntegration() {
    console.log('   > Testing Integration...');

    // Helper: Timeout Wrapper
    const withTimeout = (promise, ms = 15000) =>
      Promise.race([
        promise,
        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout (15s)')), ms)),
      ]);

    // 1. Neural Link (Ollama)
    if (window.LLM) {
      try {
        // Short "Ping" prompt with strictly enforced timeout
        const res = await withTimeout(window.LLM.generate('Ping', 'System Check', 'LOW'));
        if (res && res.length > 0)
          this.log('integration', 'PASS', `Neural Link (Ollama): ${res.substring(0, 20)}...`);
        else this.log('integration', 'FAIL', 'Neural Link returned empty');
      } catch (e) {
        this.log('integration', 'FAIL', `Neural Link Error: ${e.message}`);
      }
    } else {
      this.log('integration', 'SKIP', 'LLM Client not loaded');
    }

    // 2. Vault Bridge (Kernel)
    try {
      const res = await withTimeout(fetch('http://localhost:8001/system/health'));
      if (res.ok) this.log('integration', 'PASS', 'Vault Kernel (8001) Online');
      else this.log('integration', 'WARN', `Vault Kernel Check: ${res.status}`);
    } catch (e) {
      this.log('integration', 'FAIL', `Vault Kernel Offline: ${e.message}`);
    }
  }

  // T3: Execution (Abilities)
  async testExecution() {
    console.log('   > Testing Execution...');
    // Mock Skill Check
    try {
      const response = await new Promise((resolve) => {
        chrome.runtime.sendMessage({ action: 'HEARTBEAT' }, resolve);
      });

      if (response && response.status === 'ALIVE') {
        this.log('execution', 'PASS', 'Background Service Worker: ACTIVE');
      } else {
        this.log('execution', 'FAIL', 'Background Service Worker: UNRESPONSIVE');
      }
    } catch (e) {
      this.log('execution', 'WARN', `SW Communication Error: ${e.message}`);
    }
  }

  // T4: UI Architecture
  async testUI() {
    console.log('   > Testing UI...');
    const requiredIds = ['save', 'llmProvider', 'activeProfile'];
    let missing = 0;
    requiredIds.forEach((id) => {
      if (document.getElementById(id)) this.log('ui', 'PASS', `DOM Element #${id} Found`);
      else {
        this.log('ui', 'FAIL', `Missing DOM Element #${id}`);
        missing++;
      }
    });
  }

  // T5: User Comprehension (UX)
  async testUX() {
    console.log('   > Testing UX...');
    // Check Labeling
    const inputs = document.querySelectorAll('input, select, textarea');
    let labeled = 0;
    inputs.forEach((el) => {
      const id = el.id;
      const label = document.querySelector(`label[for="${id}"]`);
      const aria = el.getAttribute('aria-label');
      if (label || aria) labeled++;
    });

    const coverage = Math.round((labeled / inputs.length) * 100);
    if (coverage > 80) this.log('ux', 'PASS', `Accessibility Coverage: ${coverage}%`);
    else this.log('ux', 'WARN', `Accessibility Low: ${coverage}%`);
  }

  log(category, status, message) {
    this.results[category].push({ status, message });
  }

  calculateScore() {
    let total = 0;
    let passed = 0;

    // Only iterate over test category arrays, not the 'score' property
    const categories = ['deployment', 'integration', 'execution', 'ui', 'ux'];
    categories.forEach((category) => {
      if (this.results[category] && Array.isArray(this.results[category])) {
        this.results[category].forEach((item) => {
          total++;
          if (item.status === 'PASS') passed++;
        });
      }
    });

    this.results.score = total === 0 ? 0 : Math.round((passed / total) * 100);
    return this.results;
  }
}
