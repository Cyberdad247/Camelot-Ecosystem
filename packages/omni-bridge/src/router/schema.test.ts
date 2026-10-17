import { describe, expect, it } from 'vitest';
import { validateA2ARequest } from './schema';

describe('A2A Schema Validation', () => {
  it('should validate a correct A2A JSON-RPC request', () => {
    const payload = {
      jsonrpc: '2.0',
      method: 'execute_task',
      params: {
        source_agent: 'Merlin_Ω',
        target_engine: 'Goose',
        context_payload: '{ "@context": "..." }',
        mcp_tools_allowed: ['read_file', 'write_file'],
      },
      id: '123e4567-e89b-12d3-a456-426614174000',
    };
    expect(validateA2ARequest(payload)).toBe(true);
  });

  it('should reject malformed or missing fields', () => {
    expect(validateA2ARequest(null)).toBe(false);
    expect(validateA2ARequest({})).toBe(false);
    expect(
      validateA2ARequest({
        jsonrpc: '2.0',
        method: 'other_method',
        params: {},
        id: '1',
      }),
    ).toBe(false);
  });
});
