import { describe, expect, it } from 'vitest';
import { AgentProcessPool, spawnAgent } from './wrapper';

describe('Execution Wrapper', () => {
  it('should spawn target with pipe stdio', () => {
    // In test environment, echo/node command is cross-platform
    const proc = spawnAgent('node -e "process.exit(0)"');
    expect(proc).toBeDefined();
    expect(proc.stdout).toBeDefined();
    expect(proc.stdin).toBeDefined();
    expect(proc.stderr).toBeDefined();
    proc.kill();
  });

  it('should track active processes in pool', () => {
    AgentProcessPool.drain();
    const proc1 = spawnAgent('node -e "process.exit(0)"');
    expect(AgentProcessPool.getActiveCount()).toBeGreaterThanOrEqual(1);
    proc1.kill();
  });
});
