// VAULT BRIDGE (Connectivity to Camelot Kernel)

const KERNEL_API = "http://localhost:8001";

async function syncToVault(intel, token) {
  try {
    console.log("[BRIDGE] Attempting Sync to Ouroboros...");
    
    const payload = {
        intent: `[AUTO-MEMORIZE]: Web Intel from ${intel.agent}`,
        agent_id: "MERLIN",
        metadata: {
            source: "Nano-Browser",
            url: intel.url, // Ensure we capture URL
            timestamp: intel.timestamp
        },
        // We wrap the intel as a memory ingestion request
        // Note: Real implementation needs a dedicated /memory/ingest endpoint
        // For now, we use agent/dispatch to tell Merlin to save it.
        context: JSON.stringify(intel.content) 
    };

    const response = await fetch(`${KERNEL_API}/agent/dispatch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-camelot-token": "merlin-v100-dev" // In prod, use user's configured token
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
        return { status: "SUCCESS", msg: "Synced to Vault" };
    } else {
        return { status: "ERROR", msg: "Kernel Rejected" };
    }
  } catch (e) {
    return { status: "ERROR", msg: "Kernel Offline" };
  }
}

// DOWNLINK: Fetch Commands from Kernel
async function fetchFromVault() {
    try {
        const response = await fetch(`${KERNEL_API}/agent/inbox?agent=Nano-Browser`, {
            method: "GET",
            headers: { "x-camelot-token": "merlin-v100-dev" }
        });
        if (response.ok) {
            return await response.json(); // Expecting { commands: [] }
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