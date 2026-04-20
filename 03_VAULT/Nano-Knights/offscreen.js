import { GraphRAG } from './src/prometheus/index.js';
import { MemoryExporter } from './src/prometheus/memory_exporter.js';
import { SynthesisEngine } from './src/intelligence/synthesis_engine.js';

// Singleton Instance for Offscreen
const knowledgeGraph = new GraphRAG();

// LLM Adapter for Synthesis (Direct Internal Call)
const llmAdapter = {
    generate: async (prompt, systemRole) => {
        // Use the window.LLM exposed by llm_client.js
        return await window.LLM.generate(prompt, systemRole);
    }
};

const synthesisEngine = new SynthesisEngine(llmAdapter, knowledgeGraph);

// Extend Skill Library
if (window.SKILL_LIBRARY) {
    window.SKILL_LIBRARY["INDEX_NODES"] = async (nodes) => {
        console.log(`[OFFSCREEN] Indexing ${nodes.length} nodes...`);
        await knowledgeGraph.indexNodes(nodes);
        return { status: 'INDEXED', count: nodes.length };
    };

    window.SKILL_LIBRARY["QUERY_GRAPH"] = async (query) => {
        console.log(`[OFFSCREEN] Querying Graph: ${query}`);
        return await knowledgeGraph.query(query);
    };
    
    window.SKILL_LIBRARY["EXPORT_GRAPH"] = async () => {
         console.log("[OFFSCREEN] Exporting Memory Snapshot (JSON-LD)...");
         const exportData = MemoryExporter.export(knowledgeGraph);
         return exportData;
    };
    
    window.SKILL_LIBRARY["SYNTHESIZE_REPORT"] = async (query) => {
        console.log(`[OFFSCREEN] Synthesizing Report: ${query}`);
        return await synthesisEngine.synthesize(query);
    };
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.target !== "OFFSCREEN") return;

  console.log(`[OFFSCREEN] Executing Aspect: ${msg.skill}`);
  
  const skill_fn = window.SKILL_LIBRARY?.[msg.skill];
  
  if (skill_fn) {
    // Wrap in Promise for async skills (LLM calls)
    Promise.resolve(skill_fn(msg.data))
      .then(result => sendResponse({ status: "SUCCESS", result: result }))
      .catch(err => sendResponse({ status: "ERROR", error: err.toString() }));
      
    return true; // Keep message channel open for async response
  } else {
    sendResponse({ status: "ERROR", error: "Unknown Skill" });
  }
});