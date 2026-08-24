// OPTIONS LOGIC
import { LLMClient } from './llm_client.js';
import { DiagnosticCore } from './src/diagnostics/diagnostic_core.js';

// Initialize LLM for this context if not already global
if (!window.LLM) {
    window.LLM = new LLMClient();
}

document.addEventListener('DOMContentLoaded', () => {
    restoreOptions();
    setupTabs();
    setupDiagnostics();
    setupEventListeners(); // Move listeners here
    checkAuthState();      // Check auth on load
});

document.getElementById('save').addEventListener('click', saveOptions);

function setupEventListeners() {
    const el = (id) => document.getElementById(id);
    if(el('llmProvider')) el('llmProvider').addEventListener('change', toggleProviderConfig);
    if(el('proxyMode')) el('proxyMode').addEventListener('change', toggleProxyConfig);
    if(el('testConnection')) el('testConnection').addEventListener('click', testConnection);
    if(el('activeProfile')) el('activeProfile').addEventListener('change', loadProfileSettings);
    if(el('btnNewProfile')) el('btnNewProfile').addEventListener('click', createNewProfile);
    if(el('primaryCloudEngine')) el('primaryCloudEngine').addEventListener('change', toggleCustomProvider);
    
    // Auth
    if(el('btnLogin')) el('btnLogin').addEventListener('click', handleLogin);
    if(el('btnLogout')) el('btnLogout').addEventListener('click', handleLogout);
    
    // Import/Export
    if(el('btnExport')) el('btnExport').addEventListener('click', handleExport);
    if(el('btnImport')) el('btnImport').addEventListener('click', handleImport);

    // 8GB Mode
    if(el('lowMemoryMode')) {
        el('lowMemoryMode').addEventListener('change', (e) => {
            if (e.target.checked) {
                document.getElementById('ollamaModel').value = 'gemma3:1b';
                showStatus("Low Spec Mode: Model set to 'gemma3:1b'.", "info");
            }
        });
    }
}

function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const target = tab.dataset.tab;
            const section = document.querySelector(`.tab-content[data-tab="${target}"]`);
            if (section) {
                section.classList.remove('hidden');
                section.classList.add('active');
            }
        });
    });
}

function setupDiagnostics() {
    const btn = document.getElementById('btnRunDiagnostics');
    if (btn) {
        btn.addEventListener('click', async () => {
            console.log("[DIAG] Button clicked, starting tests...");
            btn.innerText = "Running Tests (Max 15s)...";
            btn.disabled = true;
            
            try {
                const diag = new DiagnosticCore();
                const results = await diag.runAll();
                renderResults(diag.results);
            } catch (error) {
                console.error("[DIAG] Test suite failed:", error);
                showStatus(`Test Failed: ${error.message}`, 'error');
            } finally {
                btn.innerText = "Run Full Suite";
                btn.disabled = false;
            }
        });
    }
}

function renderResults(results) {
    const container = document.getElementById('diagnosticResults');
    const scoreVal = document.getElementById('scoreVal');
    const scoreBadge = document.getElementById('diagScore');
    
    if (scoreVal) scoreVal.innerText = results.score;
    if (scoreBadge) scoreBadge.classList.remove('hidden');

    let html = '';
    const renderCat = (title, items) => {
        if (!items || items.length === 0) return '';
        let list = items.map(i => `
            <div class="result-item ${i.status.toLowerCase()}">
                <span class="status">[${i.status}]</span>
                <span class="msg">${i.message}</span>
            </div>
        `).join('');
        return `<div class="diag-category"><h3>${title}</h3>${list}</div>`;
    };

    html += renderCat('🚀 Deployment', results.deployment);
    html += renderCat('🔌 Integration', results.integration);
    html += renderCat('⚔️ Execution', results.execution);
    html += renderCat('🎨 UI Architecture', results.ui);
    html += renderCat('🧠 UX Comprehension', results.ux);

    if (container) container.innerHTML = html;
}

// --- AUTH LOGIC (Updated for MV3 Messages) ---
const loginForm = document.getElementById('loginForm');
const sessionInfo = document.getElementById('sessionInfo');

function checkAuthState() {
    chrome.runtime.sendMessage({ action: "GET_AUTH_STATE" }, (response) => {
        if (chrome.runtime.lastError) return; // SW might be waking up
        
        if (response && response.isAuthenticated) {
            loginForm.style.display = 'none';
            sessionInfo.style.display = 'block';
            document.getElementById('githubToken').value = response.githubToken || '';
        } else {
            loginForm.style.display = 'block';
            sessionInfo.style.display = 'none';
        }
    });
}

function handleLogin() {
    const email = document.getElementById('authEmail').value;
    const pass = document.getElementById('authPassword').value;
    const code = document.getElementById('auth2FA').value;
    const ghToken = "ghp_mock_token_for_demo"; 
    
    chrome.runtime.sendMessage({ 
        action: "AUTH_LOGIN", 
        email, pass, code, ghToken 
    }, (result) => {
        if (result && result.status === "SUCCESS") {
            showStatus("Identity Verified.", "success");
            checkAuthState();
        } else {
            showStatus("Auth Failed: " + (result?.reason || "Unknown"), "error");
        }
    });
}

function handleLogout() {
    chrome.runtime.sendMessage({ action: "AUTH_LOGOUT" }, () => {
        checkAuthState();
        showStatus("Session Terminated.", "info");
    });
}

// --- CONFIG LOGIC ---

async function saveOptions() {
  // same logic, just cleaner
  const missionServer = document.getElementById('missionServer') ? document.getElementById('missionServer').value : '';
  const autoStealth = document.getElementById('autoStealth') ? document.getElementById('autoStealth').checked : false;
  
  const llmConfig = {
      provider: document.getElementById('llmProvider').value,
      geminiApiKey: document.getElementById('geminiApiKey').value,
      geminiModel: document.getElementById('geminiModel').value,
      ollamaEndpoint: document.getElementById('ollamaEndpoint').value,
      ollamaModel: document.getElementById('ollamaModel').value,
      hybridMode: document.getElementById('hybridMode').checked,
      lowMemoryMode: document.getElementById('lowMemoryMode').checked,
      allowCloudOffload: document.getElementById('allowCloudOffload').checked,
      primaryCloudEngine: document.getElementById('primaryCloudEngine').value,
      customBaseUrl: document.getElementById('customBaseUrl').value,
      customApiKey: document.getElementById('customApiKey').value,
      customModelId: document.getElementById('customModelId').value
  };

  const stealthConfig = {
      activeProfile: document.getElementById('activeProfile').value,
      emulationMode: document.getElementById('emulationMode').value,
      sovereignMode: document.getElementById('sovereignMode').checked
  };

  const proxyConfig = {
      mode: document.getElementById('proxyMode').value,
      host: document.getElementById('proxyHost').value.split(':')[0] || '',
      port: document.getElementById('proxyHost').value.split(':')[1] || '',
      auth: document.getElementById('proxyAuth').value,
      rotateOnBan: document.getElementById('rotateOnBan').checked
  };

  await chrome.storage.sync.set({ missionServer, autoStealth, llmConfig, stealthConfig, proxyConfig });

  chrome.runtime.sendMessage({ action: "LOG_CONFIG_CHANGE", config: { llmConfig, stealthConfig, proxyConfig } });
  showStatus('Settings Saved & Applied.', 'success');
}

async function restoreOptions() {
    checkAuthState();

    const data = await chrome.storage.sync.get([
        'missionServer', 'autoStealth', 'llmConfig', 'stealthConfig', 'proxyConfig'
    ]);
    
    if(document.getElementById('missionServer')) document.getElementById('missionServer').value = data.missionServer || 'http://localhost:8000';
    if(document.getElementById('autoStealth')) document.getElementById('autoStealth').checked = data.autoStealth !== false;

    if (data.llmConfig) {
        if(document.getElementById('llmProvider')) document.getElementById('llmProvider').value = data.llmConfig.provider || 'ollama';
        if(document.getElementById('geminiApiKey')) document.getElementById('geminiApiKey').value = data.llmConfig.geminiApiKey || '';
        if(document.getElementById('geminiModel')) document.getElementById('geminiModel').value = data.llmConfig.geminiModel || 'gemini-1.5-flash';
        if(document.getElementById('ollamaEndpoint')) document.getElementById('ollamaEndpoint').value = data.llmConfig.ollamaEndpoint || 'http://localhost:11434';
        if(document.getElementById('ollamaModel')) document.getElementById('ollamaModel').value = data.llmConfig.ollamaModel || 'gemma3:1b';
        if(document.getElementById('hybridMode')) document.getElementById('hybridMode').checked = data.llmConfig.hybridMode || false;
        if(document.getElementById('lowMemoryMode')) document.getElementById('lowMemoryMode').checked = data.llmConfig.lowMemoryMode || false;
        if(document.getElementById('allowCloudOffload')) document.getElementById('allowCloudOffload').checked = data.llmConfig.allowCloudOffload || false;
        
        if(document.getElementById('primaryCloudEngine')) document.getElementById('primaryCloudEngine').value = data.llmConfig.primaryCloudEngine || 'gemini';
        if(document.getElementById('customBaseUrl')) document.getElementById('customBaseUrl').value = data.llmConfig.customBaseUrl || '';
        if(document.getElementById('customApiKey')) document.getElementById('customApiKey').value = data.llmConfig.customApiKey || '';
        if(document.getElementById('customModelId')) document.getElementById('customModelId').value = data.llmConfig.customModelId || '';
        
        toggleCustomProvider(); 
    }

    if (data.stealthConfig) {
        if(document.getElementById('activeProfile')) document.getElementById('activeProfile').value = data.stealthConfig.activeProfile || 'default';
        if(document.getElementById('emulationMode')) document.getElementById('emulationMode').value = data.stealthConfig.emulationMode || 'DESKTOP';
        if(document.getElementById('sovereignMode')) document.getElementById('sovereignMode').checked = data.stealthConfig.sovereignMode || false;
    }
    
    if (data.proxyConfig) {
        if(document.getElementById('proxyMode')) document.getElementById('proxyMode').value = data.proxyConfig.mode || 'direct';
        if(data.proxyConfig.host && document.getElementById('proxyHost')) {
            document.getElementById('proxyHost').value = `${data.proxyConfig.host}:${data.proxyConfig.port}`;
        }
        if(document.getElementById('proxyAuth')) document.getElementById('proxyAuth').value = data.proxyConfig.auth || '';
        if(document.getElementById('rotateOnBan')) document.getElementById('rotateOnBan').checked = data.proxyConfig.rotateOnBan;
    }

    toggleProviderConfig();
    toggleProxyConfig();
}

function toggleCustomProvider() {
    const engine = document.getElementById('primaryCloudEngine').value;
    const customConfig = document.getElementById('customProviderConfig');
    if (customConfig) customConfig.style.display = (engine === 'custom') ? 'block' : 'none';
}

function toggleProviderConfig() {
    const provider = document.getElementById('llmProvider').value;
    const ollamaConfig = document.getElementById('ollamaConfig');
    const geminiConfig = document.getElementById('geminiConfig');
    if (ollamaConfig) ollamaConfig.style.display = provider === 'ollama' ? 'block' : 'none';
    if (geminiConfig) geminiConfig.style.display = provider === 'gemini' ? 'block' : 'none';
}

function toggleProxyConfig() {
    const mode = document.getElementById('proxyMode').value;
    const proxyConfig = document.getElementById('proxyConfig');
    if (proxyConfig) proxyConfig.style.display = mode === 'fixed_servers' ? 'block' : 'none';
}

async function testConnection() {
    showStatus('Testing Neural Link...', 'info');
    try {
        const result = await window.LLM.generate("Ping.", "System check.");
        showStatus(`Success: ${result.substring(0, 50)}...`, 'success');
    } catch (e) {
        console.error("[NEURAL_LINK] Test Failed:", e);
        showStatus(`Connection Failed: ${e.message}. Check browser console!`, 'error');
    }
}

function createNewProfile() {
    const name = prompt("Enter new identity name:");
    if (name) {
        chrome.runtime.sendMessage({ action: "CREATE_PROFILE", name }, (response) => {
            if (response && response.status === "SUCCESS") {
                const opt = document.createElement('option');
                opt.text = response.profile.name;
                opt.value = response.profile.id;
                document.getElementById('activeProfile').add(opt);
                document.getElementById('activeProfile').value = opt.value;
                showStatus(`Identity '${name}' created locally.`, 'info');
            } else {
                showStatus("Profile Creation Failed", "error");
            }
        });
    }
}

function handleExport() {
    const profileId = document.getElementById('activeProfile').value;
    const pass = prompt("Set encryption password for team share:");
    if (!pass) return;
    
    chrome.runtime.sendMessage({ action: "EXPORT_PROFILE", profileId, pass }, (response) => {
        if (response && response.status === "SUCCESS") {
            const blob = new Blob([response.data], {type: 'text/plain'});
            const url = URL.createObjectURL(blob);
            chrome.downloads.download({
                 url: url,
                 filename: `nano_profile_${profileId}.enc`
             });
            showStatus("Profile Encrypted & Downloaded.", "success");
        } else {
            showStatus("Export Error: " + response?.msg, "error");
        }
    });
}

function handleImport() {
    const pass = prompt("Enter decryption PLACEHOLDER_KEY_REMOVED_BY_SIR_SENTINELinput');
    input.type = 'file';
    input.accept = '.enc';
    input.onchange = e => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = async event => {
            const encryptedContent = event.target.result;
            chrome.runtime.sendMessage({ action: "IMPORT_PROFILE", encryptedContent, pass }, (res) => {
                if (res.status === "SUCCESS") {
                   showStatus(`Profile '${res.name}' Imported!`, "success");
                   const opt = document.createElement('option');
                   opt.text = res.name;
                   opt.value = res.id;
                   document.getElementById('activeProfile').add(opt);
                   document.getElementById('activeProfile').value = opt.value;
                } else {
                   showStatus("Import Error: " + res.msg, "error");
                }
            });
        };
        reader.readAsText(file);
    };
    input.click();
}

function loadProfileSettings() {
    // Stub
}

function showStatus(msg, type) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = msg;
    statusEl.className = type;
    setTimeout(() => {
        statusEl.textContent = '';
        statusEl.className = '';
    }, 3000);
}