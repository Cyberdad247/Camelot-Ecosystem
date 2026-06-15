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

// MERLIN LITE - AGENCY DISPATCHER [Omega_RECON v3.0]
// Manages The Council, Hive Swarm, and Agency Protocols.

// 0. Initialize Systems
const profileManager = self.ProfileManager;
const proxyManager = self.ProxyManager;
const knightSpawner = new KnightSpawner(profileManager);
if (self.AuthManager && typeof self.AuthManager.init === 'function') {
    self.AuthManager.init().catch((e) => console.warn("[AUTH] Init Failed:", e));
}

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
// const synthesisEngine = new SynthesisEngine(llmAdapter, knowledgeGraph);

const SWARM_STATE = {
  // ... (unchanged)
  task_queue: [],
  memory: [],
  status: "IDLE",
  current_vision: null, 
  background_tabs: [], 
  precise: {
    active: false,
    stopRequested: false,
    missionId: null,
    status: "IDLE",
    lanes: []
  },
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

function unwrapPreciseContract(contract) {
    if (!contract) throw new Error("EMPTY_PRECISE_CONTRACT");
    if (contract.service === "precise_mode") return contract;
    if (contract.payload && contract.payload.result && contract.payload.result.service === "precise_mode") {
        return contract.payload.result;
    }
    if (contract.result && contract.result.service === "precise_mode") {
        return contract.result;
    }
    throw new Error("INVALID_PRECISE_CONTRACT");
}

function safeParseJson(rawValue) {
    if (!rawValue) return null;
    if (typeof rawValue === "object") return rawValue;
    if (typeof rawValue !== "string") return null;

    const cleaned = rawValue.replace(/```json/gi, "").replace(/```/g, "").trim();
    try {
        return JSON.parse(cleaned);
    } catch {
        return null;
    }
}

function buildSearchUrl(query) {
    return `https://www.google.com/search?q=${encodeURIComponent(query)}`;
}

async function getPreciseLedger() {
    const data = await chrome.storage.local.get("preciseMissionLedger");
    return Array.isArray(data.preciseMissionLedger) ? data.preciseMissionLedger : [];
}

async function appendPreciseLedger(entry) {
    const ledger = await getPreciseLedger();
    const enriched = {
        ledger_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        ...entry
    };
    ledger.unshift(enriched);
    const capped = ledger.slice(0, 200);
    await chrome.storage.local.set({ preciseMissionLedger: capped });
    return enriched;
}

async function syncPreciseLedgerToVault(mode = "latest") {
    const ledger = await getPreciseLedger();
    const bundle = mode === "all" ? ledger : ledger.slice(0, 25);
    if (!bundle.length) {
        return { status: "EMPTY", synced: 0 };
    }

    const intel = {
        agent: "PRECISE_LEDGER",
        timestamp: new Date().toISOString(),
        url: "chrome-extension://nano-knights/precise-ledger",
        content: {
            type: "precise_mission_ledger",
            mode,
            count: bundle.length,
            entries: bundle
        }
    };

    const res = await self.syncToVault(intel);
    return {
        status: res.status,
        synced: bundle.length,
        msg: res.msg || null
    };
}

function waitForTabComplete(tabId, timeoutMs = 15000) {
    return new Promise((resolve) => {
        let settled = false;
        const finish = (value) => {
            if (settled) return;
            settled = true;
            chrome.tabs.onUpdated.removeListener(listener);
            clearTimeout(timer);
            resolve(value);
        };

        const listener = (updatedTabId, changeInfo) => {
            if (updatedTabId === tabId && changeInfo.status === "complete") {
                finish(true);
            }
        };

        const timer = setTimeout(() => finish(false), timeoutMs);
        chrome.tabs.onUpdated.addListener(listener);
    });
}

async function planPreciseLane(unit, contract, optimizedContext) {
    const prompt = `
[SYSTEM]: PRECISE_MODE_LANE_PLANNER
You are planning a browser research lane for one Nano-Knight.
Return ONLY valid JSON.

Required schema:
{
  "start_url": "https://...",
  "research_query": "string",
  "summary": "string",
  "intel_skill": "RECURSIVE_CRAWL|PATTERN_SYNTHESIS|STEALTH_OPS|SUMMARIZE_CORE",
  "action_intent": {
    "action": "click"|"type",
    "target": "visible text",
    "value": "optional string"
  } | null
}

Objective: ${contract.objective}
Knight: ${unit.persona} (${unit.knight_id})
Mission lane: ${unit.mission_lane}
Omniroute engine: ${unit.omniroute_engine}
Omniroute model: ${unit.omniroute_model}
Use a realistic starting page. If uncertain, use a search engine.
Prefer safe first actions. If navigation is enough, set action_intent to null.
`;

    const raw = await process_via_offscreen("EXECUTE_PROMPT", {
        prompt,
        context: optimizedContext
    });

    const parsed = safeParseJson(raw) || {};
    const researchQuery = parsed.research_query || `${contract.objective} ${unit.mission_lane}`;
    return {
        start_url: parsed.start_url || buildSearchUrl(researchQuery),
        research_query: researchQuery,
        summary: parsed.summary || `${unit.persona} assigned to ${unit.mission_lane}.`,
        intel_skill: parsed.intel_skill || "SUMMARIZE_CORE",
        action_intent: parsed.action_intent || null
    };
}

async function captureTabObservation(tabId) {
    try {
        const [result] = await chrome.scripting.executeScript({
            target: { tabId },
            func: () => ({
                title: document.title,
                url: location.href,
                bodyText: (document.body?.innerText || "").slice(0, 4000),
                links: Array.from(document.querySelectorAll("a"))
                    .slice(0, 20)
                    .map((a) => (a.innerText || a.textContent || "").trim())
                    .filter(Boolean),
                buttons: Array.from(document.querySelectorAll("button,input[type='submit'],input[type='button']"))
                    .slice(0, 20)
                    .map((el) => (el.innerText || el.value || "").trim())
                    .filter(Boolean)
            })
        });
        return result?.result || null;
    } catch (e) {
        return {
            title: "unavailable",
            url: "unavailable",
            bodyText: "",
            links: [],
            buttons: [],
            error: e.message
        };
    }
}

async function planPreciseNextAction(unit, contract, observation, stepIndex, optimizedContext) {
    const prompt = `
[SYSTEM]: PRECISE_MODE_STEP_PLANNER
You are controlling one browser lane for a Nano-Knight.
Return ONLY valid JSON.

Schema:
{
  "done": true|false,
  "reason": "string",
  "intel_skill": "RECURSIVE_CRAWL|PATTERN_SYNTHESIS|STEALTH_OPS|SUMMARIZE_CORE",
  "action_intent": {
    "action": "click"|"type",
    "target": "visible text",
    "value": "optional string"
  } | null
}

Objective: ${contract.objective}
Knight: ${unit.persona} (${unit.knight_id})
Mission lane: ${unit.mission_lane}
Current URL: ${observation?.url || "unknown"}
Current title: ${observation?.title || "unknown"}
Buttons: ${(observation?.buttons || []).join(" | ") || "none"}
Links: ${(observation?.links || []).join(" | ") || "none"}
Body excerpt:
${observation?.bodyText || ""}

Rules:
- Keep the lane safe and bounded.
- Prefer one high-confidence next action.
- If the page already satisfies the mission lane, set done=true and action_intent=null.
- If no clear safe action exists, set done=true.
- Step index: ${stepIndex}
`;

    const raw = await process_via_offscreen("EXECUTE_PROMPT", {
        prompt,
        context: optimizedContext
    });
    return safeParseJson(raw) || { done: true, reason: "planner_parse_failed", action_intent: null, intel_skill: "SUMMARIZE_CORE" };
}

async function buildOptimizedContext() {
    const memoryNodes = SWARM_STATE.memory.slice(-5).map(m => ({
        '@type': 'GENERIC',
        id: crypto.randomUUID(),
        summary: typeof m.content === 'object' ? JSON.stringify(m.content) : m.content,
        entities: m.tags ? Object.keys(m.tags) : [],
        timestamp: m.timestamp
    }));

    let optimizedContext = [];
    try {
        const { Sentinel } = await import('./src/prometheus/index.js');
        const compressed = await Sentinel.compress(memoryNodes, { target_tokens: 2000 });
        optimizedContext = compressed.nodes.map(n => n.summary);
        console.log(`[SENTINEL] Context Compressed: ${memoryNodes.length} -> ${compressed.nodes.length} nodes`);
    } catch (e) {
        console.warn("[SENTINEL] Compression skipped via fallback:", e);
        optimizedContext = memoryNodes.map(n => n.summary);
    }
    return optimizedContext;
}

async function runPreciseLane(tabId, unit, contract, optimizedContext) {
    const lanePlan = await planPreciseLane(unit, contract, optimizedContext);

    await chrome.tabs.update(tabId, { url: lanePlan.start_url });
    await waitForTabComplete(tabId);
    await chrome.scripting.executeScript({
        target: { tabId },
        func: (payload) => {
            sessionStorage.setItem("NANO_LANE_QUERY", payload.research_query || "");
            sessionStorage.setItem("NANO_LANE_SUMMARY", payload.summary || "");
            sessionStorage.setItem("NANO_LANE_SKILL", payload.intel_skill || "SUMMARIZE_CORE");
            sessionStorage.setItem("NANO_LANE_START_URL", payload.start_url || "");
        },
        args: [lanePlan]
    });

    let actionResult = null;
    const stepHistory = [];
    const maxSteps = Math.min(4, Math.max(1, contract.swarm_capacity?.safe_swarm_units || 1));
    let finalReason = "initial_navigation_complete";

    if (lanePlan.action_intent && lanePlan.action_intent.action && lanePlan.action_intent.target) {
        try {
            actionResult = await ActionExecutor.perform(tabId, lanePlan.action_intent);
        } catch (e) {
            actionResult = { status: "FAILED", details: e.message };
        }
        stepHistory.push({ step: 0, intent: lanePlan.action_intent, result: actionResult });
    }

    for (let stepIndex = 1; stepIndex <= maxSteps; stepIndex++) {
        if (SWARM_STATE.precise.stopRequested) {
            finalReason = "stop_requested";
            break;
        }

        const observation = await captureTabObservation(tabId);
        const nextPlan = await planPreciseNextAction(unit, contract, observation, stepIndex, optimizedContext);
        if (nextPlan.done || !nextPlan.action_intent) {
            finalReason = nextPlan.reason || "planner_completed";
            break;
        }

        let stepResult;
        try {
            stepResult = await ActionExecutor.perform(tabId, nextPlan.action_intent);
        } catch (e) {
            stepResult = { status: "FAILED", details: e.message };
        }
        stepHistory.push({ step: stepIndex, intent: nextPlan.action_intent, result: stepResult });
        actionResult = stepResult;

        SWARM_STATE.precise.lanes = SWARM_STATE.precise.lanes.map((lane) =>
            lane.knight_id === unit.knight_id
                ? { ...lane, stepIndex, lastResult: stepResult, status: stepResult?.status || "UNKNOWN" }
                : lane
        );
    }

    const intelEntry = {
        timestamp: new Date().toISOString(),
        agent: unit.persona,
        skill: lanePlan.intel_skill,
        content: {
            knight_id: unit.knight_id,
            mission_lane: unit.mission_lane,
            research_query: lanePlan.research_query,
            start_url: lanePlan.start_url,
            action_result: actionResult,
            steps: stepHistory,
            completion_reason: finalReason,
            omniroute_engine: unit.omniroute_engine,
            omniroute_model: unit.omniroute_model
        },
        tags: {
            MODE: "PRECISE",
            FORGE: unit.forge,
            PROXY: unit.proxy_mode,
            STEALTH: unit.stealth
        }
    };

    SWARM_STATE.memory.push(intelEntry);
    chrome.runtime.sendMessage({
        action: "INTEL_READY",
        intel: intelEntry
    });

    await appendPreciseLedger({
        type: "lane_complete",
        mission_id: SWARM_STATE.precise.missionId,
        knight_id: unit.knight_id,
        persona: unit.persona,
        tab_id: tabId,
        completion_reason: finalReason,
        step_count: stepHistory.length,
        action_status: actionResult?.status || "NONE",
        omniroute_engine: unit.omniroute_engine,
        omniroute_model: unit.omniroute_model
    });

    return {
        knight_id: unit.knight_id,
        persona: unit.persona,
        tabId,
        lane_plan: lanePlan,
        action_result: actionResult,
        steps: stepHistory,
        completion_reason: finalReason
    };
}

async function applyPreciseProxyPolicy(contract, explicitProxyConfig = null) {
    const executionPlan = contract.execution_plan || [];
    const requiresProxy = executionPlan.some(unit => unit.proxy_mode === "residential");

    if (!requiresProxy) {
        await proxyManager.clearProxy();
        return { applied: false, mode: "direct", reason: "contract does not require proxy" };
    }

    if (!explicitProxyConfig || !explicitProxyConfig.host || !explicitProxyConfig.port) {
        return { applied: false, mode: "residential", reason: "proxy config missing" };
    }

    await proxyManager.applyConfig({
        mode: "fixed_servers",
        host: explicitProxyConfig.host,
        port: explicitProxyConfig.port,
        username: explicitProxyConfig.username || "",
        password: explicitProxyConfig.password || "",
        rotationInterval: explicitProxyConfig.rotationInterval || 0,
        rotateOnBan: explicitProxyConfig.rotateOnBan !== false
    });

    return {
        applied: true,
        mode: "residential",
        reason: `${explicitProxyConfig.host}:${explicitProxyConfig.port}`
    };
}

async function deployPreciseMission(request) {
    const contract = unwrapPreciseContract(
        request.contract || (await chrome.storage.local.get("preciseMissionContract")).preciseMissionContract
    );

    const executionPlan = contract.execution_plan || [];
    if (!executionPlan.length) throw new Error("PRECISE_CONTRACT_HAS_NO_EXECUTION_PLAN");

    const proxyStatus = await applyPreciseProxyPolicy(contract, request.proxyConfig || null);
    const roster = executionPlan.map(unit => unit.knight_id);
    const squad = await knightSpawner.deploySquad(contract.objective, roster);
    const optimizedContext = await buildOptimizedContext();
    const laneResults = [];
    const missionId = crypto.randomUUID();
    SWARM_STATE.precise = {
        active: true,
        stopRequested: false,
        missionId,
        status: "DEPLOYING",
        lanes: executionPlan.map((unit) => ({
            knight_id: unit.knight_id,
            persona: unit.persona,
            status: "FORGING",
            stepIndex: 0,
            lastResult: null
        }))
    };
    await appendPreciseLedger({
        type: "mission_start",
        mission_id: missionId,
        objective: contract.objective,
        safe_swarm_units: contract.swarm_capacity?.safe_swarm_units || executionPlan.length,
        browser_isolation: contract.browser_isolation,
        proxy_mode: proxyStatus.mode
    });

    for (let i = 0; i < squad.tabIds.length; i++) {
        const tabId = squad.tabIds[i];
        const unit = executionPlan[i];
        if (!tabId || !unit) continue;

        await chrome.scripting.executeScript({
            target: { tabId },
            func: (payload) => {
                sessionStorage.setItem("NANO_PROFILE_ID", payload.browser_profile || "default");
                sessionStorage.setItem("NANO_ROLE", payload.persona || payload.knight_id);
                sessionStorage.setItem("NANO_PERSONA_ID", payload.knight_id);
                sessionStorage.setItem("NANO_OMNI_ENGINE", payload.omniroute_engine || "");
                sessionStorage.setItem("NANO_OMNI_MODEL", payload.omniroute_model || "");
                sessionStorage.setItem("NANO_PROXY_MODE", payload.proxy_mode || "direct");
                sessionStorage.setItem("NANO_STEALTH", payload.stealth || "disabled");
                sessionStorage.setItem("NANO_EPHEMERAL", payload.forge === "ephemeral" ? "true" : "false");
            },
            args: [unit]
        });

        const laneResult = await runPreciseLane(tabId, unit, contract, optimizedContext);
        laneResults.push(laneResult);
        SWARM_STATE.precise.lanes = SWARM_STATE.precise.lanes.map((lane) =>
            lane.knight_id === unit.knight_id
                ? {
                    ...lane,
                    tabId,
                    status: laneResult.completion_reason === "stop_requested" ? "STOPPED" : "COMPLETE",
                    stepIndex: laneResult.steps?.length || 0,
                    lastResult: laneResult.action_result
                }
                : lane
        );
    }

    SWARM_STATE.precise.active = false;
    SWARM_STATE.precise.status = SWARM_STATE.precise.stopRequested ? "STOPPED" : "COMPLETE";

    const missionRecord = {
        missionId,
        objective: contract.objective,
        browserIsolation: contract.browser_isolation,
        safeSwarmUnits: contract.swarm_capacity?.safe_swarm_units || executionPlan.length,
        squadId: squad.squadId,
        roster,
        laneResults,
        proxyStatus,
        deployedAt: Date.now()
    };
    const finalLedgerEntry = await appendPreciseLedger({
        type: "mission_complete",
        mission_id: missionId,
        objective: contract.objective,
        status: SWARM_STATE.precise.status,
        lane_count: laneResults.length,
        proxy_mode: proxyStatus.mode,
        browser_isolation: contract.browser_isolation
    });

    await chrome.storage.local.set({
        preciseMissionContract: contract,
        preciseMissionRecord: missionRecord,
        preciseMissionLastLedger: finalLedgerEntry
    });
    const autoSync = await syncPreciseLedgerToVault("latest");

    return {
        status: "SUCCESS",
        mission: missionRecord,
        squad,
        ledger: {
            last_entry_id: finalLedgerEntry.ledger_id,
            auto_sync: autoSync
        }
    };
}

// ... (HIVE PROTOCOL & OFFSCREEN SETUP UNCHANGED) ...

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
          } catch(e) {
              console.error("[SPAWN] Failed:", e);
              sendResponse({ status: "ERROR", msg: e.message });
          }
      })();
      return true;
  }

  if (request.action === "SAVE_PRECISE_CONTRACT") {
      (async () => {
          try {
              const contract = unwrapPreciseContract(request.contract);
              await chrome.storage.local.set({ preciseMissionContract: contract });
              sendResponse({
                  status: "SUCCESS",
                  objective: contract.objective,
                  safeSwarmUnits: contract.swarm_capacity?.safe_swarm_units || 0
              });
          } catch (e) {
              sendResponse({ status: "ERROR", msg: e.message });
          }
      })();
      return true;
  }

  if (request.action === "GET_PRECISE_CONTRACT") {
      (async () => {
          const data = await chrome.storage.local.get(["preciseMissionContract", "preciseMissionRecord", "preciseMissionLastLedger"]);
          sendResponse({
              status: data.preciseMissionContract ? "SUCCESS" : "EMPTY",
              contract: data.preciseMissionContract || null,
              mission: data.preciseMissionRecord || null,
              ledger: data.preciseMissionLastLedger || null
          });
      })();
      return true;
  }

  if (request.action === "GET_PRECISE_STATUS") {
      (async () => {
          const ledger = await getPreciseLedger();
          sendResponse({
              status: "SUCCESS",
              precise: SWARM_STATE.precise,
              ledger: {
                  count: ledger.length,
                  latest: ledger[0] || null
              }
          });
      })();
      return true;
  }

  if (request.action === "STOP_PRECISE_MISSION") {
      (async () => {
          SWARM_STATE.precise.stopRequested = true;
          SWARM_STATE.precise.status = "STOPPING";
          await appendPreciseLedger({
              type: "mission_stop_requested",
              mission_id: SWARM_STATE.precise.missionId,
              status: "STOPPING"
          });
          sendResponse({ status: "SUCCESS", msg: "STOP_REQUESTED" });
      })();
      return true;
  }

  if (request.action === "SYNC_PRECISE_LEDGER") {
      (async () => {
          const result = await syncPreciseLedgerToVault(request.mode || "latest");
          sendResponse(result);
      })();
      return true;
  }

  if (request.action === "DEPLOY_PRECISE_MISSION") {
      (async () => {
          try {
              if (!self.AuthManager.isAuthenticated) {
                  sendResponse({ status: "ERROR", msg: "AUTH_REQUIRED" });
                  return;
              }
              const result = await deployPreciseMission(request);
              sendResponse(result);
          } catch (e) {
              console.error("[PRECISE] Deploy failed:", e);
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
          } catch(e) {
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
              const filename = `knight_memory_${new Date().toISOString().replace(/[:.]/g,'-')}.json`;
              await chrome.downloads.download({
                  url: dataUrl,
                  filename: filename,
                  conflictAction: 'overwrite'
              });
              
              sendResponse({ status: "SUCCESS", filename });
          } catch(e) {
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
      chrome.tabs.captureVisibleTab(null, {format: 'jpeg', quality: 60}, (dataUrl) => {
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
                    } catch(e){}
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
                        .sort((a,b) => a.lastAccessed - b.lastAccessed);

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
async function executeMission(missionRequest) {
    console.log("[AGENCY] Executing Mission:", missionRequest.qfocus);
    SWARM_STATE.status = "ACTIVE";
    
    // 1. Optimize Prompt (Select Agent)
    const prompt = optimize_prompt(missionRequest.qfocus);
    const agentRole = prompt.split('|')[0].replace('[ACTIVATE]:', '').trim();
    
    // 2. Broadcast Status Update
    chrome.runtime.sendMessage({ 
        action: "AGENT_STATUS", 
        agent: agentRole, 
        status: "DEPLOYED" 
    });

    // 3. Optimize Context via Sentinel (Prometheus)
    // Extract recent memory nodes
    const memoryNodes = SWARM_STATE.memory.slice(-5).map(m => ({
        '@type': 'GENERIC',
        id: crypto.randomUUID(),
        summary: typeof m.content === 'object' ? JSON.stringify(m.content) : m.content,
        entities: m.tags ? Object.keys(m.tags) : [],
        timestamp: m.timestamp
    }));

    // Compress (Target: 2000 tokens for context)
    let optimizedContext = [];
    try {
        const { Sentinel } = await import('./src/prometheus/index.js');
        const compressed = await Sentinel.compress(memoryNodes, { target_tokens: 2000 });
        optimizedContext = compressed.nodes.map(n => n.summary); // Use summaries
        console.log(`[SENTINEL] Context Compressed: ${memoryNodes.length} -> ${compressed.nodes.length} nodes`);
    } catch(e) {
        console.warn("[SENTINEL] Compression skipped via fallback:", e);
        optimizedContext = memoryNodes.map(n => n.summary);
    }

    try {
        const result = await process_via_offscreen("EXECUTE_PROMPT", {
            prompt: prompt,
            context: optimizedContext
        });
        
        // 4. Report Results (Intel)
        const intel_entry = { 
            timestamp: new Date().toISOString(), 
            agent: agentRole, 
            content: result,
            tags: ["MISSION_COMPLETE"] 
        };
        SWARM_STATE.memory.push(intel_entry);
        
        // Broadcast Intel
        chrome.runtime.sendMessage({
            action: "INTEL_READY",
            intel: intel_entry
        });

        SWARM_STATE.status = "IDLE";
        // Check Queue
        processNextMission();

    } catch (e) {
        console.error("[AGENCY] Mission Failed:", e);
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
             ActionExecutor.perform(tabId, request.intent).then(sendResponse);
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
