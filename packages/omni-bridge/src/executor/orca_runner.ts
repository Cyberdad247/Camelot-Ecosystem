import type { ChildProcess } from 'node:child_process';
import { type SpawnAgentOptions, spawnAgent } from './wrapper';

export interface OrcaExecutionMetrics {
  target: string;
  startTime: number;
  timeToFirstTokenMs: number | null;
  totalDurationMs: number | null;
  exitCode: number | null;
  outputBytes: number;
  sloBreached: boolean;
}

export const TTFT_SLO_THRESHOLD_MS = 2000;

export async function executeWithMetrics(
  target: string,
  options?: SpawnAgentOptions,
): Promise<{ process: ChildProcess; metrics: Promise<OrcaExecutionMetrics> }> {
  const startTime = Date.now();
  const proc = spawnAgent(target, options);

  let firstTokenTime: number | null = null;
  let outputBytes = 0;

  const metricsPromise = new Promise<OrcaExecutionMetrics>((resolve) => {
    proc.stdout?.on('data', (chunk: Buffer | string) => {
      if (!firstTokenTime) {
        firstTokenTime = Date.now();
      }
      outputBytes += chunk.length;
    });

    proc.on('close', (code) => {
      const endTime = Date.now();
      const ttft = firstTokenTime ? firstTokenTime - startTime : null;
      const totalDuration = endTime - startTime;
      const sloBreached = ttft !== null && ttft > TTFT_SLO_THRESHOLD_MS;

      resolve({
        target,
        startTime,
        timeToFirstTokenMs: ttft,
        totalDurationMs: totalDuration,
        exitCode: code,
        outputBytes,
        sloBreached,
      });
    });

    proc.on('error', () => {
      resolve({
        target,
        startTime,
        timeToFirstTokenMs: null,
        totalDurationMs: Date.now() - startTime,
        exitCode: -1,
        outputBytes,
        sloBreached: true,
      });
    });
  });

  return { process: proc, metrics: metricsPromise };
}

export const OrcaRunner = {
  TTFT_SLO_THRESHOLD_MS,
  executeWithMetrics,
};
