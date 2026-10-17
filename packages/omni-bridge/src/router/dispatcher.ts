import { determineRoute, resolveKnightEngine } from './policy';
import { A2ARequest, type A2AResponse, validateA2ARequest } from './schema';

export class A2ADispatcher {
  public async dispatch(request: unknown): Promise<A2AResponse> {
    if (!validateA2ARequest(request)) {
      return {
        jsonrpc: '2.0',
        error: {
          code: -32600,
          message: 'Invalid A2A JSON-RPC Request',
        },
        id: (request as any)?.id || 'null',
      };
    }

    const contextSize = request.params.context_payload.length;
    const taskType = (request.params.metadata?.task_type as string) || 'general';

    const route = determineRoute({ contextSize, taskType });
    const knight = resolveKnightEngine({ contextSize, taskType });

    return {
      jsonrpc: '2.0',
      result: {
        status: 'success',
        output: `Dispatched to ${route} via Knight [${knight.knightId}] on engine [${knight.engineTarget}]: ${knight.reason}`,
        token_usage: {
          prompt_tokens: Math.ceil(contextSize / 4),
          completion_tokens: 0,
        },
      },
      id: request.id,
    };
  }
}
