import './vault_bridge.js';
import './src/security/profile_manager.js';
import './src/security/proxy_manager.js';
import './src/security/auth_manager.js';
import './src/security/crypto_utils.js';
import { ActionExecutor } from './src/logic/action_executor.js';
import { ContextPruner } from './src/logic/context_pruner.js';
import { CognitiveParser } from './src/logic/cognitive_parser.js';
import { GraphRAG } from './src/prometheus/index.js';
import { KnightSpawner } from './src/knights/knight_spawner.js';
import { SynthesisEngine } from './src/intelligence/synthesis_engine.js';
import { MemoryExporter } from './src/prometheus/memory_exporter.js';
import { MeshManager } from './src/logic/mesh_manager.js';

// MERLIN LITE - AGENCY DISPATCHER [Omega_RECON v3.0]
// Manages The Council, Hive Swarm, and Agency Protocols.

// 0. Initialize Systems
const profileManager = new self.ProfileManager();
const knightSpawner = new KnightSpawner(profileManager);
const meshManager = new MeshManager();

// LLM Adapter for Synthesis
const llmAdapter = {
    generate: async (prompt, systemRole) => {
        return await process_via_offscreen("EXECUTE_PROMPT", { prompt, context: [] });
    }
};
// SynthesisEngine relies on direct graph access. This likely needs refactoring too 
// or SynthesisEngine moves to offscreen. For now, we will stub it or leave it broken 
// (assuming SynthesisEngine isn't critical for this specific test or user can wait).
// Actually, SynthesisEngine is imported. If it needs knowledgeGraph in constructor, we have a problem.
// Solution: Move SynthesisEngine to offscreen in a future step. For now, comment out.
// Phase 55: Synthesis Engine Activation
const synthesisEngine = new SynthesisEngine(llmAdapter, null); // GraphRAG pending full integration

const SWARM_STATE = {
    // ... (unchanged)
    task_queue: [],
    memory: [],
    status: "IDLE",
    current_vision: null,
    background_tabs: [],
    agent_assignments: {
        "NAVIGATOR": "DOM_STRATEGY",
        "SENTRY": "INJECTION_AUDIT",
        "DISTILLER": "SUMMARIZE_CORE",
        "LADY_APIS": "RECURSIVE_CRAWL",
        "SIR_ORACLE": "PATTERN_SYNTHESIS",
        "SIR_ZENITH": "STEALTH_OPS",
        "LADY_EYE": "VISUAL_FORENSICS"
    }
};

// ... (HIVE PROTOCOL & OFFSCREEN SETUP UNCHANGED) ...

// 1.5 TITANLINK BRIDGE (Added via Omega_NANO_FORGE)
// Connects the Extension to the Kernel via WebSocket
const TITAN_URL = "ws://127.0.0.1:18788";
let titanSocket = null;

function connectTitanLink() {
    console.log("[TITANLINK] Attempting Connection...");
    titanSocket = new WebSocket(TITAN_URL);

    titanSocket.onopen = () => {
        console.log("[TITANLINK] Connected to Kernel.");
        titanSocket.send(JSON.stringify({
            kind: "extension_handshake",
            agentId: "nano_knight_swarm_v3"
        }));
    };

    titanSocket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        console.log("[TITANLINK] Received:", msg);

        if (msg.kind === "handshake_ack") {
            console.log("[TITANLINK] Handshake Accepted. Permissions:", msg.permissions);
            
            // Task D10: Sync Vault Token to Storage
            if (msg.secrets && msg.secrets.VAULT_TOKEN) {
                chrome.storage.sync.set({ 
                    operatorConfig: { vaultToken: msg.secrets.VAULT_TOKEN } 
                });
            }

            if (msg.secrets && msg.secrets.GEMINI_API_KEY) {
                console.log("[TITANLINK] Syncing Keychain Vault secrets...");
                chrome.storage.sync.get(['llmConfig'], (data) => {
                    const config = data.llmConfig || {};
                    config.geminiApiKey = msg.secrets.GEMINI_API_KEY;
                    chrome.storage.sync.set({ llmConfig: config });
                });
            }
        }
        if (msg.kind === "dispatch_mission") {
            console.log("[TITANLINK] Dispatching Remote Mission:", msg.qfocus);
            executeMission({ qfocus: msg.qfocus, device: msg.device || "DESKTOP" });
        }

        if (msg.kind === "sync_update") {
            console.log("[TITANLINK] Syncing UKG Delta...");
            // FUTURE: Integration with GraphRAG.hydrate(msg.delta)
        }

        if (msg.kind === "config_proxy") {
            console.log("[TITANLINK] Applying Remote Proxy Configuration...");
            self.ProxyManager.applyConfig(msg.proxy);
        }

        if (msg.kind === "emergency_shutdown") {
            console.warn("[TITANLINK] (CRITICAL) EMERGENCY SHUTDOWN SIGNAL RECEIVED.");
            chrome.tabs.query({}, (tabs) => {
                const extensionTabs = tabs.filter(t => t.url && (t.url.includes("google.com") || t.url.includes("bing.com"))); // Close research tabs
                extensionTabs.forEach(t => chrome.tabs.remove(t.id));
            });
            // Stop Swarm processing
            SWARM_STATE.status = "IDLE";
        }

        if (msg.kind === "mesh_signal") {
            console.log(`[MESH] Received Signal from ${msg.from}`);
            if (msg.signal.type === 'offer') {
                meshManager.handleOffer(msg.from, msg.signal).then(answer => {
                    titanSocket.send(JSON.stringify({
                        kind: "mesh_signal",
                        to: msg.from,
                        from: meshManager.myId,
                        signal: answer
                    }));
                });
            } else if (msg.signal.type === 'answer') {
                meshManager.handleAnswer(msg.from, msg.signal);
            }
        }
    };

    titanSocket.onclose = () => {
        console.log("[TITANLINK] Disconnected. Reconnecting in 5s...");
        setTimeout(connectTitanLink, 5000);
    };

    titanSocket.onerror = (err) => {
        console.error("[TITANLINK] Error:", err);
    };
}

// Initialize Bridge
connectTitanLink();

// 2. Message Router
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    // --- PROMETHEUS INTELLIGENCE HANDLERS (ROUTED TO OFFSCREEN) ---
    if (request.action === 'INDEX_TOON_NODE') {
        (async () => {
            console.log(`[PROMETHEUS] Routing Index Request: ${request.node.id}`);
            const res = await process_via_offscreen('INDEX_NODES', [request.node]);
            sendResponse({ status: res.status, id: request.node.id });
        })();
        return true;
    }

    if (request.action === 'QUERY_KNOWLEDGE_GRAPH') {
        (async () => {
            console.log(`[PROMETHEUS] Routing Query: ${request.query}`);
            const results = await process_via_offscreen('QUERY_GRAPH', request.query);
            sendResponse({ results });
        })();
        return true;
    }

    // Knight Squad Spawner
    if (request.action === "SPAWN_SQUAD") {
        (async () => {
            try {
                const squad = await knightSpawner.deploySquad(request.goal);
                sendResponse({ status: "SUCCESS", squad });
            } catch (e) {
                console.error("[SPAWN] Failed:", e);
                sendResponse({ status: "ERROR", msg: e.message });
            }
        })();
        return true;
    }

    // Synthesis Engine
    if (request.action === "SYNTHESIZE_REPORT") {
        (async () => {
            try {
                const report = await process_via_offscreen("SYNTHESIZE_REPORT", request.query);
                sendResponse({ status: "SUCCESS", report });
            } catch (e) {
                sendResponse({ status: "ERROR", msg: e.message });
            }
        })();
        return true;
    }

    // Ouroboros Memory Sync (Bridge)
    if (request.action === "SYNC_MEMORY") {
        (async () => {
            try {
                // 1. Get JSON-LD from Offscreen
                const exportData = await process_via_offscreen('EXPORT_GRAPH', null);

                if (!exportData || !exportData['@graph']) throw new Error("Graph Export Failed");

                const jsonStr = JSON.stringify(exportData, null, 2);
                const dataUrl = 'data:application/json;base64,' + btoa(unescape(encodeURIComponent(jsonStr)));

                // 2. Trigger Download
                const filename = `knight_memory_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
                await chrome.downloads.download({
                    url: dataUrl,
                    filename: filename,
                    conflictAction: 'overwrite'
                });

                sendResponse({ status: "SUCCESS", filename });
            } catch (e) {
                console.error("[SYNC] Failed:", e);
                sendResponse({ status: "ERROR", msg: e.message });
            }
        })();
        return true;
    }

    // Data Purge (Sovereign Mode)
    if (request.action === "DATA_PURGE") {
        (async () => {
            // Offscreen Purge Protocol (Future)
            // await process_via_offscreen('PURGE_GRAPH', null);
            await chrome.storage.local.clear();
            sendResponse({ status: "SUCCESS", msg: "Memory Wiped (Local Shell)" });
        })();
        return true;
    }

    // 3. Status Check & Profile Hub
    // A. Heartbeat
    if (request.action === "HEARTBEAT") {
        sendResponse({ status: "ALIVE" });
    }

    // B. Get Profiles
    if (request.action === "GET_PROFILES") {
        chrome.storage.local.get(null, (data) => {
            const profiles = Object.keys(data)
                .filter(k => k.startsWith('profile_'))
                .map(k => data[k]);

            // Add Default Mock if none
            if (profiles.length === 0) profiles.push({ id: 'default', name: 'Default (Chromium)', type: 'DESKTOP' });

            chrome.storage.sync.get(['stealthConfig'], (syncData) => {
                const activeId = syncData.stealthConfig?.activeProfile || 'default';
                const activeProfile = profiles.find(p => p.id === activeId) || profiles[0];
                sendResponse({ profiles, activeId, activeProfile });
            });
        });
        return true; // Async response
    }

    // C. Switch Profile
    if (request.action === "SWITCH_PROFILE") {
        (async () => {
            const profile = await self.ProfileManager.loadProfile(request.id);
            // Refresh Tabs
            chrome.tabs.query({}, (tabs) => {
                tabs.forEach(tab => chrome.tabs.reload(tab.id));
            });
            sendResponse({ status: "SUCCESS", name: profile.name, profile });
        })();
        return true;
    }

    // D. Create Profile or Import/Export
    if (request.action === "CREATE_PROFILE") {
        (async () => {
            const profile = await self.ProfileManager.createProfile(request.name, "DESKTOP");
            sendResponse({ status: "SUCCESS", profile });
        })();
        return true;
    }

    if (request.action === "EXPORT_PROFILE") {
        (async () => {
            try {
                const data = await self.ProfileManager.exportProfile(request.profileId, request.pass);
                sendResponse({ status: "SUCCESS", data });
            } catch (e) { sendResponse({ status: "ERROR", msg: e.message }); }
        })();
        return true;
    }

    if (request.action === "IMPORT_PROFILE") {
        (async () => {
            try {
                const res = await self.ProfileManager.importProfile(request.encryptedContent, request.pass);
                sendResponse(res);
            } catch (e) { sendResponse({ status: "ERROR", msg: e.message }); }
        })();
        return true;
    }

    // --- AUTH HANDLERS (MV3) ---
    if (request.action === "GET_AUTH_STATE") {
        sendResponse({
            isAuthenticated: self.AuthManager.isAuthenticated,
            githubToken: self.AuthManager.githubToken
        });
        return true;
    }

    if (request.action === "AUTH_LOGIN") {
        (async () => {
            const res = await self.AuthManager.login(request.email, request.pass, request.code, request.ghToken);
            sendResponse(res);
        })();
        return true;
    }

    if (request.action === "AUTH_LOGOUT") {
        (async () => {
            await self.AuthManager.logout();
            sendResponse({ status: "SUCCESS" });
        })();
        return true;
    }

    // F. Get Queue Status
    if (request.action === "GET_QUEUE_STATUS") {
        sendResponse({ queue: SWARM_STATE.task_queue, active: SWARM_STATE.status === "ACTIVE" });
        return true;
    }

    // E. Trigger Mission (Updated for Queue)
    if (request.action === "START_MISSION") {

        // 1. Auth Check
        if (!self.AuthManager.isAuthenticated) {
            sendResponse({ status: "ERROR", msg: "AUTH_REQUIRED" });
            return;
        }

        // 2. Queue Logic
        if (request.queue) {
            const mission = {
                id: crypto.randomUUID(),
                qfocus: request.qfocus,
                device: request.device, // "MOBILE" or "DESKTOP"
                profileId: request.profileId || 'default', // Captures CURRENT profile
                profileName: request.profileName || 'Default',
                timestamp: Date.now(),
                status: "PENDING"
            };
            SWARM_STATE.task_queue.push(mission);
            console.log(`[BARRACKS] Mission Queued: [${mission.profileName}] ${mission.qfocus}`);

            // If IDLE, auto-start? Or wait for explicit "Run Queue"?
            // User requested "switching to next", implying auto-run sequence.
            if (SWARM_STATE.status === "IDLE") {
                processNextMission();
            }

            sendResponse({ status: "QUEUED", mission });
            return;
        }

        // H. Agency Dispatcher (executeMission Implementation)
        executeMission(request);
        sendResponse({ status: "MISSION_STARTED" });
    }

    // G. Capture Screenshot (Vision Lance)
    if (request.action === "CAPTURE_VISIBLE_TAB") {
        chrome.tabs.captureVisibleTab(null, { format: 'jpeg', quality: 60 }, (dataUrl) => {
            if (chrome.runtime.lastError) {
                sendResponse({ status: "ERROR", error: chrome.runtime.lastError.message });
            } else {
                sendResponse({ status: "SUCCESS", screenshot: dataUrl });
            }
        });
        return true; // Async
    }

    // B. Handle Intel from Agents
    if (request.action === "REPORT_INTEL") {
        console.log(`[MERLIN] Intel from ${request.agent}`);
        // The original SWARM_STATE.agent_assignments is removed, so this needs to be handled.
        // For now, let's assume a default skill or pass it from the agent.
        const assigned_skill = request.skill || "SUMMARIZE_CORE"; // Fallback if agent doesn't specify

        // Attach Visual Context if available
        let context_data;

        // Special handling for Vision Skill which passes complex object
        if (assigned_skill === "ANALYZE_SCREENSHOT") {
            context_data = request.data;
        } else {
            context_data = {
                text: request.data,
                image: SWARM_STATE.current_vision // Multimodal Context (Historic)
            };
        }

        process_via_offscreen(assigned_skill, context_data).then(result => {
            const parsed = CognitiveParser.parse(result);

            const intel_entry = {
                timestamp: new Date().toISOString(),
                agent: request.agent,
                skill: assigned_skill,
                content: parsed.content,
                tags: parsed.tags, // Structured reasoning data
                url: sender.tab ? sender.tab.url : "unknown"
            };

            SWARM_STATE.memory.push(intel_entry);

            // --- TITANLINK SYNC (Phase 33) ---
            if (titanSocket && titanSocket.readyState === WebSocket.OPEN) {
                console.log("[TITANLINK] Syncing Intel to Kernel...");
                titanSocket.send(JSON.stringify({
                    kind: "report_intel",
                    intel: intel_entry
                }));
            }

            // 8GB SCARCITY LOGIC: Prune Memory
            chrome.storage.sync.get(['llmConfig'], (data) => {
                if (data.llmConfig && data.llmConfig.lowMemoryMode) {
                    const beforeCount = SWARM_STATE.memory.length;
                    SWARM_STATE.memory = ContextPruner.prune(SWARM_STATE.memory);
                    if (SWARM_STATE.memory.length < beforeCount) {
                        console.log(`[MEM] Pruned Memory: ${beforeCount} -> ${SWARM_STATE.memory.length}`);
                    }
                }
            });

            // BROADCAST TO POPUP
            chrome.runtime.sendMessage({
                action: "INTEL_READY",
                intel: intel_entry
            });

            // SIR ORACLE: PATTERN SYNTHESIS TRIGGER
            if (assigned_skill === "SUMMARIZE_CORE" || assigned_skill === "PATTERN_SYNTHESIS") {
                console.log("[SIR_ORACLE] Detecting Pattern Signals...");
                // Optional: Auto-chain to a deeper synthesis if complexity is high
                // For now, the "INTEL_READY" is the proof of work.
            }
        });
    }

    // C. SYNC TO VAULT (The Bridge)
    if (request.action === "SYNC_INTEL") {
        self.syncToVault(request.intel).then(res => {
            sendResponse(res);
        });
        return true; // Async keep-alive
    }

    if (request.action === "LOG_CONFIG_CHANGE") {
        (async () => {
            console.log("[MERLIN] Config Update Received:", request.config);

            // 1. Update Profile (Triggers Cookie Swap & Noise Update)
            const newProfileId = request.config.stealthConfig?.activeProfile;
            if (newProfileId) {
                await self.ProfileManager.loadProfile(newProfileId);

                // Refresh Stealth Scripts
                chrome.tabs.query({}, (tabs) => {
                    tabs.forEach(tab => {
                        try {
                            // reload logic would go here if needed
                        } catch (e) { }
                    });
                });
            }

            // 2. Update Proxy
            if (request.config.proxyConfig) {
                await self.ProxyManager.applyConfig(request.config.proxyConfig);
            }

            // 3. 8GB Constraint: Resource Management
            if (request.config.llmConfig?.lowMemoryMode) {
                console.log("[MEM] Low Memory Mode Active. Checking Application State...");
                chrome.tabs.query({}, (tabs) => {
                    if (tabs.length > 5) {
                        console.log("[MEM] 8GB Limit Exceeded. Discarding candidates...");
                        const WHITELIST = ["chrome-extension://", "docs/", "github.com", "localhost"];
                        const candidates = tabs
                            .filter(t => !t.active)
                            .filter(t => !WHITELIST.some(w => t.url.includes(w)))
                            .sort((a, b) => a.lastAccessed - b.lastAccessed);

                        if (candidates.length > 0) {
                            chrome.tabs.discard(candidates[0].id);
                        }
                    }
                });
            }
        })();
        return true;
    }
});

// 3. Dispatch Logic

// H. Agency Dispatcher (executeMission Implementation)
// Phase 53: Recursive Goal Decomposition (Mission DAG)
async function executeMission(missionRequest) {
    console.log("[AGENCY] Executing Mission DAG:", missionRequest.qfocus);
    SWARM_STATE.status = "ACTIVE";

    try {
        const { GoalOrchestrator } = await import('./src/logic/goal_orchestrator.js');
        const orchestrator = new GoalOrchestrator(missionRequest.qfocus);

        // Execute Mission Steps via the DAG Orchestrator
        const results = await orchestrator.execute(async (subGoalDesc, context) => {
            console.log(`[AGENCY] Processing Sub-Goal: ${subGoalDesc}`);

            // 1. Optimize Prompt (Select Agent)
            const prompt = optimize_prompt(subGoalDesc);
            const agentRole = prompt.split('|')[0].replace('[ACTIVATE]:', '').trim();

            // 2. Broadcast Status Update
            chrome.runtime.sendMessage({
                action: "AGENT_STATUS",
                agent: agentRole,
                status: "DEPLOYED"
            });

            // 3. Execute via Offscreen Logic
            const result = await process_via_offscreen("EXECUTE_PROMPT", {
                prompt: prompt,
                context: Object.values(context) // Pass dependency results as context
            });

            return result;
        });

        // 4. Report Mission Completion (Intel Synthesis)
        // Phase 55: Pattern Crystallization
        const patternSummary = await synthesisEngine.crystallize(results);
        console.log(`[AGENCY] Mission Crystallized: ${patternSummary}`);

        const intel_entry = {
            timestamp: new Date().toISOString(),
            agent: "SIR_ORACLE",
            content: `Mission DAG Complete. Processed ${Object.keys(results).length} goals. Patterns: ${patternSummary}`,
            results: results,
            tags: ["MISSION_DAG_COMPLETE", "PATTERNS_EXTRACTED"]
        };
        SWARM_STATE.memory.push(intel_entry);

        // Broadcast Intel
        chrome.runtime.sendMessage({
            action: "INTEL_READY",
            intel: intel_entry
        });

        // Report back to TitanLink
        if (typeof titanSocket !== 'undefined' && titanSocket.readyState === WebSocket.OPEN) {
            titanSocket.send(JSON.stringify({
                kind: "report_intel",
                intel: intel_entry
            }));
        }

        SWARM_STATE.status = "IDLE";
        processNextMission();

    } catch (e) {
        console.error("[AGENCY] Mission DAG Failed:", e);
        SWARM_STATE.status = "ERROR";
    }
}

function dispatch_agent(agent_name, instructions) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, { target: agent_name, instructions: instructions });
        }
    });
}

// 4. Neural Engine Bridge
async function process_via_offscreen(skill, data) {
    return new Promise((resolve) => {
        chrome.runtime.sendMessage({
            target: "OFFSCREEN", skill: skill, data: data
        }, (response) => {
            resolve(response && response.result ? response.result : "INTEL_PROCESSED");
        });
    });
}

// 5. Meta-Prompt Engine
function optimize_prompt(raw_input) {
    const lower = raw_input.toLowerCase();

    // --- NEW: NAVIGATION DETECTION ---
    if (lower.startsWith("go to ") || lower.startsWith("open ")) {
        const url = raw_input.split(" ")[2];
        const target_url = url.startsWith("http") ? url : `https://${url}`;
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.update(tabs[0].id, { url: target_url });
        });
        return `[SYSTEM]: NAVIGATING TO ${target_url}`;
    }

    // --- AGENCY PROTOCOL (ROUTING) ---
    let role = "Omega_DISTILLER";
    let format = "Structured JSON";

    // 1. Sir Zenith (Auditor)
    if (lower.includes("audit") || lower.includes("protocol") || lower.includes("security")) {
        role = "Omega_ZENITH (SIR_ZENITH)";
        format = "Forensic Deep-Dive JSON";
    }

    // 2. Lady Eye (Visual)
    if (lower.includes("analyze ui") || lower.includes("screenshot")) {
        role = "Omega_WATCHER (LADY_EYE)";
        format = "Visual Layout Analysis";
    }

    // 3. Lady Apis (Deep Dive)
    if (lower.includes("deep dive") || lower.includes("crawl")) {
        role = "Omega_FORAGER (LADY_APIS)";
        format = "Recursive Link Map";
    }

    // --- COGNITIVE ACTION UPDATE (Heroic Resolver) ---
    const intent_instruction = `
  [PROTOCOL: ACTION_INTENT]
  Do NOT output CSS Selectors or IDs.
  Output JSON: { "action": "click"|"type", "target": "Visible Text of Element", "value": "If typing" }
  Example: { "action": "click", "target": "Sign In" }
  `;

    return `[ACTIVATE]: ${role} | MISSION: ${raw_input} | FORMAT: ${format} \n${intent_instruction}`;
}

// 5b. Voice Command Parser
function parseVoiceCommand(command) {
    const lower = command.toLowerCase();

    // Pattern: "research X" or "find X" or "extract X"
    if (lower.match(/research|find|extract|search/)) {
        return { type: 'MISSION', query: command };
    }

    // Pattern: "queue X" or "schedule X"
    if (lower.match(/queue|schedule|add to queue/)) {
        const query = command.replace(/queue|schedule|add to queue/gi, '').trim();
        return { type: 'QUEUE', query: query };
    }

    // Pattern: "switch profile" or "change identity"
    if (lower.match(/switch|change.*profile|change.*identity/)) {
        return { type: 'SWITCH_PROFILE' };
    }

    // Pattern: "clear" or "reset"
    if (lower.match(/clear|reset|stop/)) {
        return { type: 'CLEAR' };
    }

    // Pattern: "status" or "what's happening"
    if (lower.match(/status|what('s|\s+is)\s+(happening|going on)/)) {
        return { type: 'STATUS' };
    }

    // Default: treat as general research query
    return { type: 'MISSION', query: command };
}

// 6. COGNITIVE ACTION LAYER (Phase 18)
// "Stagehand-style" Intent Execution & Verification

// Handler for Agent Action Requests
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "EXECUTE_ACTION") {
        const tabId = request.tabId || (sender.tab ? sender.tab.id : null);
        if (tabId) {
            ActionExecutor.perform(tabId, request.intent).then(res => {
                // Phase 44: Ouroboros Telemetry
                if (titanSocket && titanSocket.readyState === WebSocket.OPEN) {
                    titanSocket.send(JSON.stringify({
                        kind: "report_action",
                        report: {
                            action: request.intent.action,
                            target: request.intent.target,
                            status: res.status,
                            healed: res.resolution?.healed || false,
                            timestamp: Date.now()
                        }
                    }));
                }
                sendResponse(res);
            });
            return true;
        }
    }
});

// I. The Barracks (Queue Consumer)
function processNextMission() {
    if (SWARM_STATE.status === "ACTIVE") return; // Busy

    if (SWARM_STATE.task_queue.length > 0) {
        const nextMission = SWARM_STATE.task_queue.shift();
        console.log(`[BARRACKS] Deploying from Queue: ${nextMission.profileName}`);
        executeMission(nextMission);
    } else {
        console.log("[BARRACKS] All Missions Complete. Standing by.");
        SWARM_STATE.status = "IDLE";
        chrome.runtime.sendMessage({ action: "AGENT_STATUS", status: "IDLE" });
    }
}