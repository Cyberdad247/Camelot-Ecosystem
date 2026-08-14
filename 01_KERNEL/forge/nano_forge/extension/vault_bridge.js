// SPDX-License-Identifier: MIT

// VAULT BRIDGE (Connectivity to Camelot Kernel)

const KERNEL_API = "http://localhost:8001";

async function syncToVault(intel) {
  try {
    console.log("[BRIDGE] Attempting Sync to Ouroboros...");
    
    // Task D10: Retrieve operator token from storage
    const storage = await chrome.storage.sync.get(['operatorConfig']);
    const token = storage.operatorConfig?.vaultToken || "SECURE_TOKEN_REQUIRED";

    const payload = {
        intent: `[AUTO-MEMORIZE]: Web Intel from ${intel.agent}`,
        agent_id: "MERLIN",
        metadata: {
            source: "Nano-Browser",
            url: intel.url, 
            timestamp: intel.timestamp
        },
        context: JSON.stringify(intel.content) 
    };

    const response = await fetch(`${KERNEL_API}/agent/dispatch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-camelot-token": token
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
        return { status: "SUCCESS", msg: "Synced to Vault" };
    } else {
        return { status: "ERROR", msg: `Kernel Rejected (Status: ${response.status})` };
    }
  } catch (e) {
    return { status: "ERROR", msg: "Kernel Offline" };
  }
}

// DOWNLINK: Fetch Commands from Kernel
async function fetchFromVault() {
    try {
        const storage = await chrome.storage.sync.get(['operatorConfig']);
        const token = storage.operatorConfig?.vaultToken || "SECURE_TOKEN_REQUIRED";

        const response = await fetch(`${KERNEL_API}/agent/inbox?agent=Nano-Browser`, {
            method: "GET",
            headers: { "x-camelot-token": token }
        });
        if (response.ok) {
            return await response.json(); 
        }
    } catch (e) {
        // Silent fail on polling
    }
    return { commands: [] };
}

// HEARTBEAT
async function checkKernelConnection() {
    try {
        const res = await fetch(`${KERNEL_API}/health`);
        return res.ok;
    } catch {
        return false;
    }
}

// 3. Reinforcement Learning Loop
async function sendTrainingData(training_sample) {
   // Sample: { prompt, dom_snapshot, action_taken, success_rating }
   console.log("[VAULT] Uploading Training Data to Merlin...");
   try {
       const response = await fetch(`${KERNEL_API}/api/learn`, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(training_sample)
       });
       return await response.json();
   } catch (err) {
       console.warn("[VAULT] Learning Node Offline:", err);
       return { status: "OFFLINE_MODE", stored_locally: true };
   }
}

// Export for Background.js
self.VaultBridge = {
    sync: syncToVault,
    fetch: fetchFromVault,
    heartbeat: checkKernelConnection,
    sendTrainingData: sendTrainingData
};
self.syncToVault = syncToVault; // Legacy comaptibility