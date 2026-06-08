// Client-side wrapper — calls POST /api/deploy with the current AST snapshot.
// Returns the Vercel deployment URL on success.

import type { ASTNode } from './parse-ast';

export interface DispatchDeployRequest {
  nodes:     ASTNode[];
  bg?:       string;
  siteName?: string;
}

export interface DispatchDeployResult {
  url:        string;
  latency_ms: number;
}

export class DeployClientError extends Error {
  constructor(
    public readonly status: number,
    public readonly stage: string | undefined,
    detail: string,
  ) {
    super(`[DEPLOY_CLIENT:${status}] ${detail}`);
  }
}

export async function dispatchDeploy(req: DispatchDeployRequest): Promise<DispatchDeployResult> {
  const resp = await fetch('/api/deploy', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(req),
  });

  const data = await resp.json() as Record<string, unknown>;

  if (!resp.ok) {
    throw new DeployClientError(
      resp.status,
      data.stage as string | undefined,
      (data.error as string | undefined) ?? resp.statusText,
    );
  }

  return data as unknown as DispatchDeployResult;
}
