import { type ChildProcess, spawn } from 'node:child_process';
import * as os from 'node:os';

export interface SpawnAgentOptions {
  cwd?: string;
  env?: NodeJS.ProcessEnv;
  headless?: boolean;
  isolation?: 'auto' | 'native' | 'wasm' | 'smolvm';
}

const activePool = new Map<number, { proc: ChildProcess; startedAt: number; target: string }>();
export const MAX_CONCURRENT_LOCAL_PROCESSES = 2; // Strict 4GB RAM guardrail

export const AgentProcessPool = {
  register(proc: ChildProcess, target: string): void {
    if (proc.pid) {
      if (activePool.size >= MAX_CONCURRENT_LOCAL_PROCESSES) {
        const oldestEntry = Array.from(activePool.entries()).sort(
          (a, b) => a[1].startedAt - b[1].startedAt,
        )[0];
        if (oldestEntry) {
          const [oldestPid, { proc: oldestProc }] = oldestEntry;
          try {
            oldestProc.kill('SIGTERM');
          } catch {
            // Ignore error if already terminated
          }
          activePool.delete(oldestPid);
        }
      }

      activePool.set(proc.pid, { proc, startedAt: Date.now(), target });
      proc.on('exit', () => {
        if (proc.pid) activePool.delete(proc.pid);
      });
    }
  },

  getActiveCount(): number {
    return activePool.size;
  },

  drain(): void {
    for (const [_, { proc }] of activePool.entries()) {
      try {
        proc.kill('SIGTERM');
      } catch {
        // Ignore
      }
    }
    activePool.clear();
  },
};

export function spawnAgent(target: string, options?: SpawnAgentOptions): ChildProcess {
  const isWindows = os.platform() === 'win32';
  const isolation = options?.isolation || 'auto';

  let proc: ChildProcess;

  if (isolation === 'smolvm') {
    const args = [
      'machine',
      'run',
      '--net',
      '--image',
      'alpine',
      '--',
      'executor',
      'daemon',
      'run',
      target,
      '--headless',
    ];
    proc = spawn('smolvm', args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: options?.cwd,
      env: options?.env,
    });
  } else if (isWindows) {
    const parts = target.split(' ');
    const command = parts[0];
    const args = parts.slice(1);
    if (options?.headless !== false) {
      args.push('--headless');
    }

    proc = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true,
      cwd: options?.cwd,
      env: options?.env,
    });
  } else {
    const parts = target.split(' ');
    const command = parts[0];
    const args = parts.slice(1);
    if (options?.headless !== false) {
      args.push('--headless');
    }

    proc = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: options?.cwd,
      env: options?.env,
    });
  }

  AgentProcessPool.register(proc, target);
  return proc;
}
