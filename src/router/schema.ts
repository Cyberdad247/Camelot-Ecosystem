export interface A2ARequest {
    jsonrpc: "2.0";
    method: "execute_task";
    params: {
        source_agent: string;
        target_engine: string;
        context_payload: string;
        mcp_tools_allowed: string[];
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
        && typeof p.id === 'string';
}
