import { spawn }    from 'node:child_process';
import { NextRequest, NextResponse } from 'next/server';
import path from 'node:path';

// ---------------------------------------------------------------------------
// Ouroboros binary path.
// OUROBOROS_BIN env var overrides the default release build location.
// ---------------------------------------------------------------------------

const CAMELOT_ROOT = process.env.CAMELOT_ROOT
  ?? 'C:\\Users\\vizio\\CAMELOT_OS';

const BINARY = process.env.OUROBOROS_BIN
  ?? path.join(CAMELOT_ROOT, '02_FORGE', 'excalibur-dev', 'target', 'release', 'ouroboros.exe');

const LATENCY_CEILING_MS = 101;
const SPAWN_TIMEOUT_MS   = 5_000;  // hard kill if binary hangs

interface OuroborosRequest {
  intent:     string;
  state_dim?: number;
}

interface OuroborosResponse {
  ast_json:   string;
  latency_ms: number;
}

function runOuroboros(req: OuroborosRequest): Promise<OuroborosResponse> {
  return new Promise((resolve, reject) => {
    const proc = spawn(BINARY, [], { stdio: ['pipe', 'pipe', 'pipe'] });

    let stdout = '';
    let stderr = '';
    let killed = false;

    const timer = setTimeout(() => {
      killed = true;
      proc.kill('SIGKILL');
      reject(new Error(`[OUROBOROS_TIMEOUT] binary exceeded ${SPAWN_TIMEOUT_MS}ms`));
    }, SPAWN_TIMEOUT_MS);

    proc.stdout.on('data', (chunk: Buffer) => { stdout += chunk.toString(); });
    proc.stderr.on('data', (chunk: Buffer) => { stderr += chunk.toString(); });

    proc.on('close', (code) => {
      clearTimeout(timer);
      if (killed) return;

      if (code !== 0) {
        return reject(new Error(`[OUROBOROS_EXIT:${code}] ${stderr.trim()}`));
      }

      try {
        resolve(JSON.parse(stdout.trim()) as OuroborosResponse);
      } catch {
        reject(new Error(`[OUROBOROS_PARSE] bad stdout: ${stdout.slice(0, 200)}`));
      }
    });

    proc.on('error', (err) => {
      clearTimeout(timer);
      reject(new Error(`[OUROBOROS_SPAWN] ${err.message} — is the binary built? Run: cargo build --release -p excalibur-ouroboros`));
    });

    proc.stdin.write(JSON.stringify(req));
    proc.stdin.end();
  });
}

// ---------------------------------------------------------------------------
// POST /api/infer
// Body: { intent: string, state_dim?: number }
// ---------------------------------------------------------------------------

export async function POST(req: NextRequest) {
  let body: { intent?: string; state_dim?: number };

  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'invalid JSON body' }, { status: 400 });
  }

  if (!body.intent || typeof body.intent !== 'string' || !body.intent.trim()) {
    return NextResponse.json({ error: 'intent is required' }, { status: 400 });
  }

  const t0 = performance.now();

  let result: OuroborosResponse;
  try {
    result = await runOuroboros({
      intent:    body.intent.trim(),
      state_dim: body.state_dim ?? 256,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: msg }, { status: 502 });
  }

  const wallLatency = performance.now() - t0;

  if (wallLatency > LATENCY_CEILING_MS) {
    return NextResponse.json(
      { error: `[LATENCY_BREACH] ${wallLatency.toFixed(1)}ms exceeds ${LATENCY_CEILING_MS}ms ceiling` },
      { status: 504 },
    );
  }

  return NextResponse.json({
    ast_json:        result.ast_json,
    latency_ms:      wallLatency,
    engine_latency:  result.latency_ms,
  });
}
