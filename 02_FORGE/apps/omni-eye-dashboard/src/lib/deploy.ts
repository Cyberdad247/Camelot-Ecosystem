// E. Deploy Adapter — generates a static site from ASTNodes, deploys via Vercel CLI.
// Wire: POST /api/deploy { nodes, bg, siteName } → { url, latency_ms }

import path     from 'node:path';
import os       from 'node:os';
import { mkdtemp, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import type { ASTNode } from './parse-ast';
import { generateSiteHTML } from './site-generator';

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface DeployRequest {
  nodes:     ASTNode[];
  bg?:       string;
  siteName?: string;
}

export interface DeployResult {
  url:        string;
  latency_ms: number;
}

export class DeployError extends Error {
  constructor(
    public readonly stage: 'generate' | 'scaffold' | 'cli',
    detail: string,
    cause?: unknown,
  ) {
    super(`[DEPLOY:${stage.toUpperCase()}] ${detail}`);
    this.cause = cause;
  }
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const VERCEL_BIN =
  process.env.VERCEL_BIN ??
  (process.platform === 'win32' ? 'vercel.cmd' : 'vercel');

const DEPLOY_TIMEOUT_MS = 5 * 60 * 1_000; // 5 min


// ---------------------------------------------------------------------------
// Project scaffold (writes index.html + vercel.json to temp dir)
// ---------------------------------------------------------------------------

async function scaffoldProject(dir: string, html: string): Promise<void> {
  await writeFile(path.join(dir, 'index.html'), html, 'utf8');
  await writeFile(
    path.join(dir, 'vercel.json'),
    JSON.stringify({ version: 2 }, null, 2),
    'utf8',
  );
}

// ---------------------------------------------------------------------------
// Vercel CLI runner
// ---------------------------------------------------------------------------

function runVercelCLI(dir: string, siteName: string, token?: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const args = ['--prod', '--yes', '--no-clipboard', '--name', siteName.toLowerCase().replace(/[^a-z0-9-]/g, '-')];
    if (token) args.push('--token', token);

    const proc = spawn(VERCEL_BIN, args, {
      cwd:   dir,
      stdio: ['ignore', 'pipe', 'pipe'],
      env:   { ...process.env },
    });

    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', (chunk: Buffer) => { stdout += chunk.toString(); });
    proc.stderr.on('data', (chunk: Buffer) => { stderr += chunk.toString(); });

    const kill = setTimeout(() => {
      proc.kill();
      reject(new DeployError('cli', `Vercel CLI timed out after ${DEPLOY_TIMEOUT_MS / 1000}s`));
    }, DEPLOY_TIMEOUT_MS);

    proc.on('close', (code: number | null) => {
      clearTimeout(kill);
      if (code !== 0) {
        reject(new DeployError('cli', `vercel exited ${code ?? 'null'}: ${stderr.slice(0, 400)}`));
        return;
      }
      // The deployment URL is the last non-empty line of stdout.
      const url = stdout.trim().split('\n').map(l => l.trim()).filter(Boolean).pop() ?? '';
      if (!url.startsWith('http')) {
        reject(new DeployError('cli', `unexpected CLI output (no URL): ${stdout.slice(0, 200)}`));
        return;
      }
      resolve(url);
    });

    proc.on('error', (err: Error) => {
      clearTimeout(kill);
      reject(new DeployError('cli', `Failed to spawn ${VERCEL_BIN}: ${err.message}`, err));
    });
  });
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export async function deploy(req: DeployRequest): Promise<DeployResult> {
  const t0 = Date.now();
  const bg       = req.bg ?? '#ffffff';
  const siteName = req.siteName ?? 'camelot-site';

  if (!req.nodes.length) {
    throw new DeployError('generate', 'No AST nodes to deploy — add components first');
  }

  let html: string;
  try {
    html = generateSiteHTML(req.nodes, bg, siteName);
  } catch (e) {
    throw new DeployError('generate', `HTML generation failed: ${String(e)}`, e);
  }

  let tmpDir: string;
  try {
    tmpDir = await mkdtemp(path.join(os.tmpdir(), 'camelot-deploy-'));
    await scaffoldProject(tmpDir, html);
  } catch (e) {
    throw new DeployError('scaffold', `Failed to scaffold project: ${String(e)}`, e);
  }

  const token = process.env.VERCEL_TOKEN;
  const url   = await runVercelCLI(tmpDir, siteName, token);

  return { url, latency_ms: Date.now() - t0 };
}
