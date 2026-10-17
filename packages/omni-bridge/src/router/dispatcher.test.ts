import { describe, expect, it } from 'vitest';
import { A2ADispatcher } from './dispatcher';
import type { A2ARequest } from './schema';

describe('A2A Dispatcher', () => {
  it('should dispatch valid requests to appropriate Knight engine', async () => {
    const dispatcher = new A2ADispatcher();
    const req: A2ARequest = {
      jsonrpc: '2.0',
      method: 'execute_task',
      params: {
        source_agent: 'Merlin_Ω',
        target_engine: 'Auto',
        context_payload: 'const x = 42;'.repeat(100),
        mcp_tools_allowed: ['read_file'],
        metadata: {
          task_type: 'kinetic_code_generation',
        },
      },
      id: 'test-123',
    };

    const res = await dispatcher.dispatch(req);
    expect(res.jsonrpc).toBe('2.0');
    expect(res.id).toBe('test-123');
    expect(res.result?.status).toBe('success');
    expect(res.result?.output).toContain('SIR_BORIS');
  });

  it('should return error for invalid payload', async () => {
    const dispatcher = new A2ADispatcher();
    const res = await dispatcher.dispatch({} as any);
    expect(res.error).toBeDefined();
    expect(res.error?.code).toBe(-32600);
  });
});
