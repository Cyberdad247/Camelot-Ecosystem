export interface A2ARequest {
    jsonrpc: "2.0";
    method: "execute_task";
    params: {
        source_agent: string;
        target_engine: string;
        context_payload: string;
        mcp_tools_allowed: string[];
        // BitRouter & Cost Guardrails
        virtual_key?: string;      // virtual key prefixed with brvk_
        spend_cap?: number;        // maximum allowed cost for this loop
        current_spend?: number;    // current accumulated cost
        loop_count?: number;       // current loop iteration count
        max_loops?: number;        // loop guard: maximum allowed iterations
        // agency-agents & Persona
        persona?: string;          // agent persona (e.g. planner, critic)
        // simonw/llm Template Parameters
        template_params?: Record<string, string>; // prompt template parameters
        // Lane / Intent text for OmniRoute lane-signal policies
        intent_text?: string;       // intent text containing keywords
    };
    id: string;
}

export function validateA2ARequest(payload: unknown): payload is A2ARequest {
    if (typeof payload !== 'object' || payload === null) {
        return false;
    }
    const p = payload as Record<string, any>;
    return p.jsonrpc === "2.0"
        && p.method === "execute_task"
        && typeof p.params === 'object'
        && p.params !== null
        && typeof p.params.source_agent === 'string'
        && typeof p.params.target_engine === 'string'
        && typeof p.params.context_payload === 'string'
        && Array.isArray(p.params.mcp_tools_allowed)
        && p.params.mcp_tools_allowed.every((item: unknown) => typeof item === 'string')
        && typeof p.id === 'string'
        // Validate optional BitRouter parameters
        && (p.params.virtual_key === undefined || (typeof p.params.virtual_key === 'string' && p.params.virtual_key.startsWith('brvk_')))
        && (p.params.spend_cap === undefined || typeof p.params.spend_cap === 'number')
        && (p.params.current_spend === undefined || typeof p.params.current_spend === 'number')
        && (p.params.loop_count === undefined || typeof p.params.loop_count === 'number')
        && (p.params.max_loops === undefined || typeof p.params.max_loops === 'number')
        // Validate optional Persona parameter
        && (p.params.persona === undefined || typeof p.params.persona === 'string')
        // Validate optional Intent parameter
        && (p.params.intent_text === undefined || typeof p.params.intent_text === 'string')
        // Validate optional Template parameters
        && (p.params.template_params === undefined || (typeof p.params.template_params === 'object' && p.params.template_params !== null && Object.values(p.params.template_params).every(v => typeof v === 'string')));
}
