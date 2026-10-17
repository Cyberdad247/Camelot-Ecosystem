export interface A2AParams {
  source_agent: string;
  target_engine: string;
  context_payload: string;
  mcp_tools_allowed: string[];
  symbolect_state?: string;
  metadata?: Record<string, unknown>;
}

export interface A2ARequest {
  jsonrpc: '2.0';
  method: 'execute_task';
  params: A2AParams;
  id: string;
}

export interface A2AResponse {
  jsonrpc: '2.0';
  result?: {
    status: 'success' | 'failed' | 'gated';
    output: string;
    token_usage?: {
      prompt_tokens: number;
      completion_tokens: number;
    };
    latency_ms?: number;
  };
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
  id: string;
}

export function validateA2ARequest(payload: any): payload is A2ARequest {
  return Boolean(
    payload &&
      payload.jsonrpc === '2.0' &&
      payload.method === 'execute_task' &&
      payload.params &&
      typeof payload.params.source_agent === 'string' &&
      typeof payload.params.target_engine === 'string' &&
      typeof payload.params.context_payload === 'string' &&
      Array.isArray(payload.params.mcp_tools_allowed) &&
      typeof payload.id === 'string',
  );
}
