import { ResourceSquire } from './src/squires/resource_squire.js';
import { ChunkManager } from './src/logic/chunk_manager.js';

const DEFAULT_CONFIG = {
    provider: 'ollama', // 'ollama' | 'gemini'
    ollamaEndpoint: 'http://127.0.0.1:11434',
    ollamaModel: 'gemma3:1b', // 8GB Constraint: Default to 1B/2B/3B
    geminiEndpoint: 'https://generativelanguage.googleapis.com/v1beta/models',
    geminiModel: 'gemini-1.5-flash',
    geminiApiKey: '',
    lowMemoryMode: false, // New Flag
    allowCloudOffload: false
};

export class LLMClient {
    constructor() {
        this.config = { ...DEFAULT_CONFIG };
        this.cache = {};
        this.loadConfig();
    }

    async loadConfig() {
        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync) {
            try {
                const stored = await chrome.storage.sync.get('llmConfig');
                if (stored.llmConfig) {
                    this.config = { ...this.config, ...stored.llmConfig };
                }
            } catch (e) {
                console.warn("[LLM] Config Load Failed:", e);
            }
        } else {
             console.warn("[LLM] chrome.storage unavailable. Using defaults.");
        }

        // 8GB Constraint: Aggressive Cache Clearing
        if (this.config.lowMemoryMode && Object.keys(this.cache).length > 20) {
            console.log("[MEM] Low Memory Mode: Clearing LLM Cache");
            this.cache = {};
        }
    }

    // Complexity: 'LOW' | 'HIGH'
    // Format: 'JSON' | 'TOON'
    // Images: Array of base64 strings (optional)
    async generate(prompt, systemInstruction = "You are a helpful assistant.", complexity = 'HIGH', format = 'JSON', images = []) {
        await this.loadConfig(); // Ensure fresh config

        // 0. TOON/COGNITIVE INJECTION
        if (format === 'TOON') {
            systemInstruction += `\n\n[SYSTEM: INPUT_FORMAT_TOON]\nInput is in Token Optimized Object Notation (#@ Header). Pipe-delimited. Indentation denotes hierarchy. T=True, F=False, _=Null. Respond concisely.`;
        } else if (format === 'COGNITIVE') {
            systemInstruction += `\n\n[SYSTEM: COGNITIVE_PROTOCOL]\nRespond using structured cognitive tags BEFORE the main output. \nRequired Tags: [AttentionFocus], [TheoryOfMind], [ReasoningPathway], [Metacognition]. \nOptional Tags: [RevisionQuery], [CognitiveOperations], [KeyInfoExtraction], [Exploration], [ContextAdherenceTLDR]. \nFormat: [TagName: Content] followed by [OUTPUT START] marker.`;
        }

        // 1. CACHE CHECK (The Echo Chamber)
        // Hash includes images length/content to differentiate
        const cacheKey = this._hash(prompt + systemInstruction + format + images.length);
        if (this.cache[cacheKey]) {
            console.log("[LLM] Cache Hitted! (0 Tokens)");
            return this.cache[cacheKey];
        }

        console.log(`[LLM] Generating... Mode: ${complexity}, Hybrid: ${this.config.hybridMode}, Format: ${format}, Images: ${images.length}`);

        let response = null;

        // 2. RESOURCE JUDGEMENT SQUIRE
        // If images are present, we MUST use Cloud (Gemini) as Ollama/Gemma 2b text models can't see.
        // Unless we have LLaVA local? For now, force Cloud for Vision.
        let judgement = { environment: 'LOCAL', reason: 'Default' };

        if (images.length > 0) {
            judgement = { environment: 'CLOUD', reason: 'Vision Required' };
        } else {
            judgement = this._judgeAndRoute(prompt, complexity);
        }

        console.log(`[LLM] Squire Verdict: ${judgement.environment} (${judgement.reason})`);

        // 3. EXECUTION
        if (judgement.environment === 'LOCAL') {
            try {
                console.log("[LLM] Routing to Ollama (Local)...");
                response = await this._callOllama(prompt, systemInstruction);
            } catch (e) {
                console.warn("[LLM] Ollama failed. Checking Cloud Permissions...", e);
                if (this.config.allowCloudOffload) {
                     response = await this._callCloud(prompt, systemInstruction, images);
                }
            }
        } else {
            // CLOUD REQUIRED
            if (this.config.allowCloudOffload || images.length > 0) { // Vision implies consent? Or should we check? allowCloud is strictly for 'offloading', maybe Vision is a separate permission?
                // For now, assuming if user asks for screenshot analysis, they expect cloud.
                console.log("[LLM] Offloading to Cloud (Morgana/Modal)...");
                response = await this._callCloud(prompt, systemInstruction, images);
            } else {
                console.warn("[LLM] Cloud Offload Denied. Cannot process Vision locally yet.");
                return "[ERROR] Vision tasks require Cloud Access enabled.";
            }
        }

        // 4. CACHE SAVE
        if (response && !response.startsWith("[ERROR]")) {
            this.cache[cacheKey] = response;
        }

        return response;
    }

    _judgeAndRoute(prompt, complexity) {
        return ResourceSquire.judge(prompt, complexity, this.config);
    }

    async _callCloud(prompt, system, images = []) {
        if (this.config.primaryCloudEngine === 'custom' || this.config.primaryCloudEngine === 'modal') {
             return await this._callOpenAI(prompt, system, images);
        } else {
             return await this._callGemini(prompt, system, images);
        }
    }

    _hash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = (hash << 5) - hash + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash;
    }

    // --- OLLAMA ADAPTER ---
    async _callOllama(prompt, system) {
        try {
            // 8GB Constraint: Agentic Optimization
            // Gemma 2b/Gemma 3 1b handles 4k-8k well, but we limit to 4k for speed/RAM balance.
            const max_tokens = this.config.lowMemoryMode ? 4096 : 8192;

            const response = await fetch(`${this.config.ollamaEndpoint}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: this.config.ollamaModel || 'gemma3:1b',
                    prompt: prompt,
                    system: system,
                    stream: false,
                    options: {
                        num_predict: 1024, // Increased for COT/Agentic output
                        temperature: 0.3,
                        num_ctx: max_tokens, // Valid Agentic Context Window
                        num_thread: 4 // Explicit threading for stability
                    }
                })
            });

            if (!response.ok) throw new Error(`Ollama API Error: ${response.status}`);
            const data = await response.json();
            return data.response;
        } catch (e) {
            throw e; // Propagate to trigger fallback
        }
    }

    /**
     * EXTRACT: Structured Data Extraction with Hydra Protocol (Smart Chunking)
     * @param {string} rawText - The TOON content to extract from
     * @param {object} schema - The JSON Schema to enforce
     * @param {string} userGoal - (Optional) Specific focus for the extraction
     */
    async extract(rawText, schema, userGoal = "Extract all matching entities") {
        await this.loadConfig();

        // [HYDRA] 1. Check for Chunking Necessity
        const CHUNK_THRESHOLD = this.config.lowMemoryMode ? 8000 : 16000;

        if (rawText.length > CHUNK_THRESHOLD) {
            console.log(`[HYDRA] Input size ${rawText.length} > ${CHUNK_THRESHOLD}. Engaging Chunk Manager.`);

            const chunks = ChunkManager.chunk(rawText, 6000, 500); // 6000 chars ~ 1500 tokens
            console.log(`[HYDRA] Created ${chunks.length} chunks.`);

            const results = [];

            // SERIAL EXECUTION (Safe for 8GB)
            for (let i = 0; i < chunks.length; i++) {
                console.log(`[HYDRA] Processing Chunk ${i+1}/${chunks.length}...`);
                const result = await this._extractSinglePass(chunks[i], schema, userGoal);
                if (!result.error) results.push(result);
            }

            console.log(`[HYDRA] Merging ${results.length} results...`);
            return ChunkManager.merge(results, schema);
        }

        // Standard Single Pass
        return await this._extractSinglePass(rawText, schema, userGoal);
    }

    async _extractSinglePass(rawText, schema, userGoal) {
        const schemaString = JSON.stringify(schema, null, 2);

        const systemPrompt = `
You are an advanced Data Extraction Engine (NANO-EXTRACT).
Your goal is to parse the provided text (in TOON format) and output valid JSON matching the schema.

[SCHEMA]
${schemaString}

[RULES]
1. OUTPUT MUST BE VALID JSON.
2. For every extracted field, if you can locate the specific source text in the input, include a "_source" key with the "Ref" ID from the TOON input.
   Example: { "price": "$1200", "_source": "42" } assuming TOON line: "  |42|p|T|$1200|42"
3. If data is missing, use null. do not invent data.
4. Respond ONLY with the JSON object.
`;

        const userPrompt = `
[GOAL] ${userGoal}

[INPUT_DATA (TOON)]
${rawText}
`;

        const judgement = this._judgeAndRoute(userPrompt, 'HIGH');

        let responseText = "";
        try {
            if (judgement.environment === 'LOCAL') {
                responseText = await this._callOllama(userPrompt, systemPrompt);
            } else {
                responseText = await this._callCloud(userPrompt, systemPrompt);
            }

            // Clean markdown code blocks
            const cleanParams = responseText.replace(/```json/g, '').replace(/```/g, '').trim();
            return JSON.parse(cleanParams);
        } catch (e) {
            console.error("[EXTRACT] Single Pass Failed:", e);
            return { error: "JSON_PARSE_FAILED", raw: responseText };
        }
    }

    /**
     * ORCHESTRATE: Remote State Handoff (Phase 26)
     * Packages current browser state into TOON and delegates planning to Remote Agent.
     */
    async orchestrate(state, goal) {
        await this.loadConfig();

        // 1. Construct State Object (TOON-Ready)
        const payload = {
            goal: goal,
            url: state.url,
            title: state.title,
            domSource: state.dom, // Ideally simplified
            timestamp: Date.now()
        };

        const systemPrompt = `
[SYSTEM: REMOTE_ORCHESTRATOR]
You are the Strategic Planner. The user is a constrained Edge Agent.
Receive the State (TOON) and Goal.
Output a MACRO-ACTION SCHEDULE (JSON).
Format: { "plan_id": "...", "steps": [ { "action": "...", "target": "..." } ] }
`;

        const userPrompt = `
[GOAL]: ${goal}
[STATE]: ${JSON.stringify(payload)}
`;

        // Force Cloud for Orchestration
        if (this.config.allowCloudOffload || this.config.primaryCloudEngine === 'custom') {
            console.log("[ORCHESTRATE] Handoff to Cloud...");
            return await this._callCloud(userPrompt, systemPrompt);
        } else {
             return "[ERROR] Remote Orchestration requires Cloud Offload enabled.";
        }
    }


    // --- UNIVERSAL ADAPTER (OpenAI-Compatible) ---
    async _callOpenAI(prompt, system, images = []) {
        if (!this.config.customApiKey || !this.config.customBaseUrl) {
            return "[ERROR]: Custom Provider Config missing. Check Options.";
        }

        try {
            // Ensure trailing slash logic if needed
            const baseUrl = this.config.customBaseUrl.replace(/\/$/, "");
            const url = `${baseUrl}/chat/completions`;

            const messages = [
                { role: "system", content: system }
            ];

            if (images.length > 0) {
                // OpenAI Vision Format
                const content = [{ type: "text", text: prompt }];
                images.forEach(img => {
                    // Assuming img is base64 string
                    content.push({
                        type: "image_url",
                        image_url: { url: `data:image/jpeg;base64,${img}` }
                    });
                });
                messages.push({ role: "user", content: content });
            } else {
                messages.push({ role: "user", content: prompt });
            }

            const payload = {
                model: this.config.customModelId || "gpt-3.5-turbo",
                messages: messages,
                temperature: 0.3
            };

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.customApiKey}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`Status ${response.status}: ${errText}`);
            }

            const data = await response.json();
            return data.choices[0].message.content;

        } catch (e) {
            console.error("[LLM] Custom Provider Failed:", e);
            return `[ERROR]: Custom Provider Failed. (${e.message})`;
        }
    }

    // --- GEMINI ADAPTER ---
    async _callGemini(prompt, system, images = []) {
        if (!this.config.geminiApiKey) {
            return "[ERROR]: Gemini API Key missing. Please configure it in Options.";
        }

        try {
            const url = `${this.config.geminiEndpoint}/${this.config.geminiModel}:generateContent?key=${this.config.geminiApiKey}`;

            // Construct Content Parts
            const parts = [{ text: prompt }];

            // Append Images (Gemini Format)
            images.forEach(img => {
                // Determine mime type if possible, default to jpeg
                // img is expected to be base64 data (without header, or we strip it)
                const base64Data = img.replace(/^data:image\/\w+;base64,/, '');

                parts.push({
                    inlineData: {
                        mimeType: "image/jpeg",
                        data: base64Data
                    }
                });
            });

            const payload = {
                contents: [{ parts: parts }],
                systemInstruction: { parts: [{ text: system }] }
            };

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error?.message || response.statusText);
            }

            const data = await response.json();
            return data.candidates[0].content.parts[0].text;
        } catch (e) {
            console.error("[LLM] Gemini Failed:", e);
            return `[ERROR]: Gemini API Failed. (${e.message})`;
        }
    }

}

// Window export for non-module contexts (fallback, though we aim for module everywhere now)
// We'll attach it if 'window' exists for standard script compat, but since we are moving to modules
// specifically to FIX the architecture, we usually rely on 'import'.
// However, options.js might need it on window if not updated fully.
// Let's support both for transition.
// End of LLMClient Module
