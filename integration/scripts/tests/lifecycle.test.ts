// The runtime scripts are the most machine-dependent code in the slice and
// had no tests at all. The riskiest logic is dev-down's ownership guard: it
// decides what gets SIGTERM'd, and getting it wrong means killing a process
// that merely inherited a recycled PID.
//
// These tests drive the real functions from scripts/lib.sh with a throwaway
// RUN_DIR and real background processes — no mocking of the thing under test.
// They follow the precedent set by hermes/tests/engine-wrappers.test.ts.

import { execFile, spawn } from 'node:child_process';
import { existsSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { afterEach, describe, expect, it } from 'vitest';

const run = promisify(execFile);
const scriptsDir = fileURLToPath(new URL('../', import.meta.url));
const LIB = join(scriptsDir, 'lib.sh');

const spawned: number[] = [];

afterEach(() => {
  for (const pid of spawned.splice(0)) {
    try {
      process.kill(pid, 'SIGKILL');
    } catch {
      /* already gone */
    }
  }
});

/** Run a bash snippet with lib.sh sourced and RUN_DIR pointed at a temp dir. */
async function bash(snippet: string, runDir: string) {
  const script = `
set -uo pipefail
source ${JSON.stringify(LIB)}
RUN_DIR=${JSON.stringify(runDir)}
${snippet}
`;
  return run('bash', ['-c', script], { env: { ...process.env, PATH: process.env['PATH'] ?? '' } });
}

/** A real long-lived process whose cmdline contains a recognisable token. */
function spawnTagged(token: string): number {
  const child = spawn('bash', ['-c', `exec -a ${token} sleep 300`], { detached: true, stdio: 'ignore' });
  child.unref();
  spawned.push(child.pid as number);
  return child.pid as number;
}

describe('lib.sh path resolution', () => {
  // Regression: scripts cd into $INTEGRATION_DIR early, after which a
  // relative $(dirname "$BASH_SOURCE") no longer resolves. That produced an
  // exit-127 that a recorder run nearly captured as a false FAIL.
  it('resolves SCRIPT_DIR absolutely regardless of the caller cwd', async () => {
    const fromRoot = await run('bash', ['-c', `cd / && source ${LIB} && echo "$SCRIPT_DIR"`]);
    const fromTmp = await run('bash', ['-c', `cd /tmp && source ${LIB} && echo "$SCRIPT_DIR"`]);
    expect(fromRoot.stdout.trim()).toBe(scriptsDir.replace(/\/$/, ''));
    expect(fromTmp.stdout.trim()).toBe(fromRoot.stdout.trim());
  });

  it('keeps working after the caller changes directory', async () => {
    const { stdout } = await run('bash', [
      '-c',
      `source ${LIB} && cd "$INTEGRATION_DIR" && cd / && [[ -f "$SCRIPT_DIR/lib.sh" ]] && echo reachable`,
    ]);
    expect(stdout.trim()).toBe('reachable');
  });

  it('puts every runtime path under the single .run root', async () => {
    const { stdout } = await run('bash', [
      '-c',
      `source ${LIB} && echo "$RUN_DIR" && echo "$BIN_DIR" && echo "$GATEWAY_DB"`,
    ]);
    const [runDir, binDir, db] = stdout.trim().split('\n');
    expect(runDir.endsWith('/integration/.run')).toBe(true);
    expect(binDir?.startsWith(runDir as string)).toBe(true);
    expect(db?.startsWith(runDir as string)).toBe(true);
  });
});

describe('service_alive ownership guard', () => {
  it('recognises a process we recorded', async () => {
    const runDir = mkdtempSync(join(tmpdir(), 'run-'));
    const token = 'camelot-test-alive';
    const pid = spawnTagged(token);

    const { stdout } = await bash(
      `record_service gateway ${pid} ${token}; service_alive gateway && echo OURS || echo NOT_OURS`,
      runDir,
    );
    expect(stdout.trim()).toBe('OURS');
  });

  // The core safety property: a PID recorded by us, now belonging to an
  // unrelated process, must NOT be claimed. This is what stops dev-down
  // killing a stranger that inherited the number.
  it('refuses a recycled PID whose cmdline no longer matches', async () => {
    const runDir = mkdtempSync(join(tmpdir(), 'run-'));
    const pid = spawnTagged('camelot-test-imposter');

    // Recorded under a token this process does not carry.
    const { stdout } = await bash(
      `record_service gateway ${pid} camelot-token-that-never-ran; service_alive gateway && echo OURS || echo NOT_OURS`,
      runDir,
    );
    expect(stdout.trim()).toBe('NOT_OURS');
  });

  it('refuses a PID that is no longer running', async () => {
    const runDir = mkdtempSync(join(tmpdir(), 'run-'));
    const { stdout } = await bash(
      // PID 2^22 is above the default pid_max on Linux: reliably absent.
      `record_service gateway 4194303 any-token; service_alive gateway && echo OURS || echo NOT_OURS`,
      runDir,
    );
    expect(stdout.trim()).toBe('NOT_OURS');
  });

  it('refuses when the metadata file is missing entirely', async () => {
    const runDir = mkdtempSync(join(tmpdir(), 'run-'));
    const pid = spawnTagged('camelot-test-nometa');
    writeFileSync(join(runDir, 'gateway.pid'), String(pid));

    const { stdout } = await bash(`service_alive gateway && echo OURS || echo NOT_OURS`, runDir);
    expect(stdout.trim()).toBe('NOT_OURS');
  });

  it('refuses when no pid file exists', async () => {
    const runDir = mkdtempSync(join(tmpdir(), 'run-'));
    const { stdout } = await bash(`service_alive gateway && echo OURS || echo NOT_OURS`, runDir);
    expect(stdout.trim()).toBe('NOT_OURS');
  });
});

describe('dev-down', () => {
  it('stops a process it owns and clears its runtime files', async () => {
    const runDir = mkdtempSync(join(tmpdir(), 'run-'));
    const token = 'camelot-test-teardown';
    const pid = spawnTagged(token);

    await bash(
      `record_service gateway ${pid} ${token}
       for s in "\${ALL_SERVICES[@]}"; do
         p=$(service_pid "$s"); [[ -z $p ]] && continue
         service_alive "$s" || continue
         kill -TERM "$p" 2>/dev/null
         rm -f "$(pid_file "$s")" "$(meta_file "$s")"
       done`,
      runDir,
    );

    await new Promise((r) => setTimeout(r, 400));
    expect(() => process.kill(pid, 0)).toThrow(); // gone
    expect(existsSync(join(runDir, 'gateway.pid'))).toBe(false);
    expect(existsSync(join(runDir, 'gateway.meta'))).toBe(false);
  });

  // The whole point of the guard, end to end through the real script.
  it('does NOT signal a process whose metadata does not match', async () => {
    const runDir = mkdtempSync(join(tmpdir(), 'run-'));
    const pid = spawnTagged('camelot-test-bystander');
    writeFileSync(join(runDir, 'gateway.pid'), String(pid));
    writeFileSync(join(runDir, 'gateway.meta'), 'a-token-this-process-does-not-have');

    const { stdout } = await run('bash', [join(scriptsDir, 'dev-down.sh')], {
      env: { ...process.env, RUN_DIR: runDir },
    }).catch((e) => ({ stdout: String(e.stdout ?? '') }));

    // Survived: dev-down recognised it as not ours.
    expect(() => process.kill(pid, 0)).not.toThrow();
    expect(stdout).toMatch(/not ours|skip/i);
  });
});
