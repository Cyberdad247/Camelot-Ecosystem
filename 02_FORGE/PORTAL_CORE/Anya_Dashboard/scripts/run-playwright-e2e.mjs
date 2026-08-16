import { existsSync } from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const dashboardRoot = path.resolve(scriptDir, '..');
const repoRoot = path.resolve(scriptDir, '../../../..');
const port = Number(process.env.PLAYWRIGHT_PORT ?? 5191);
const host = process.env.PLAYWRIGHT_HOST ?? '127.0.0.1';
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? `http://${host}:${port}`;

const pythonCandidates =
  process.platform === 'win32'
    ? [path.join(repoRoot, '.venv', 'Scripts', 'python.exe'), 'python']
    : [path.join(repoRoot, '.venv', 'bin', 'python'), 'python3', 'python'];

const python = pythonCandidates.find(
  (candidate) => candidate === 'python' || candidate === 'python3' || existsSync(candidate),
);
const serverScript = path.join(repoRoot, 'scripts', 'serve_anya_dashboard.py');
const playwrightBin =
  process.platform === 'win32'
    ? path.join(dashboardRoot, 'node_modules', '.bin', 'playwright.cmd')
    : path.join(dashboardRoot, 'node_modules', '.bin', 'playwright');

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForServer() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 2_000);
      const response = await fetch(`${baseURL}/support/test`, { signal: controller.signal });
      clearTimeout(timeout);
      if (response.ok) {
        return;
      }
    } catch {
      await delay(500);
    }
  }
  throw new Error(`dashboard test server did not become ready at ${baseURL}`);
}

function spawnChecked(command, args, options = {}) {
  return spawn(command, args, {
    cwd: dashboardRoot,
    shell: false,
    stdio: options.stdio ?? 'inherit',
    env: options.env ?? process.env,
  });
}

function run(command, args, env) {
  return new Promise((resolve) => {
    let child;
    try {
      child = spawnChecked(command, args, { env });
    } catch {
      resolve(1);
      return;
    }
    child.on('exit', (code) => resolve(code ?? 1));
    child.on('error', () => resolve(1));
  });
}

async function stopServer(server) {
  if (!server || server.exitCode !== null) {
    return;
  }
  server.kill();
  await Promise.race([new Promise((resolve) => server.once('exit', resolve)), delay(2_000)]);
  if (server.exitCode === null) {
    server.kill('SIGKILL');
  }
}

const server = spawnChecked(python, [serverScript, '--host', host, '--port', String(port)], {
  stdio: 'ignore',
});

let exitCode = 1;
try {
  await waitForServer();
  exitCode = await run(
    process.platform === 'win32' ? 'cmd' : existsSync(playwrightBin) ? playwrightBin : 'npx',
    process.platform === 'win32'
      ? [
          '/c',
          existsSync(playwrightBin) ? playwrightBin : 'npx',
          ...(existsSync(playwrightBin) ? ['test'] : ['playwright', 'test']),
        ]
      : existsSync(playwrightBin)
        ? ['test']
        : ['playwright', 'test'],
    {
      ...process.env,
      PLAYWRIGHT_SKIP_WEB_SERVER: '1',
      PLAYWRIGHT_BASE_URL: baseURL,
    },
  );
} finally {
  await stopServer(server);
}

process.exit(exitCode);
