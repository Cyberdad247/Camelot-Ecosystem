import { Router } from 'express';

export const telemetryRouter = Router();

// SSE telemetry snapshots every five seconds
telemetryRouter.get('/', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  
  // Send an initial snapshot
  const sendSnapshot = () => {
    // Determine process memory RSS & scale to edge host simulation
    const mem = process.memoryUsage();
    const nodeRssMB = Math.round(mem.rss / 1024 / 1024 * 10) / 10;
    // Edge system total usage (Go registry + Rust DSP + Node + OS kernel) bounded strictly within 4096MB
    const simulatedHostUsedMB = Math.min(
      4096,
      Math.round((780 + nodeRssMB * 1.8 + (Math.random() * 40 - 20)) * 10) / 10
    );
    const ramCeilingMB = 4096;
    const ramPercent = Math.round((simulatedHostUsedMB / ramCeilingMB) * 1000) / 10;
    const madvReclaimedMB = Math.round((280 + Math.random() * 50) * 10) / 10;

    const data = {
      timestamp: Date.now(),
      globalLoad: Math.round((28 + Math.random() * 15) * 10) / 10,
      activeLeases: Math.floor(Math.random() * 3) + 1,
      networkEgress: Math.round(Math.random() * 512 * 10) / 10,
      ramUsageMB: simulatedHostUsedMB,
      ramCeilingMB,
      ramPercent,
      madvReclaimedMB,
      hardwareCeiling: "4GB_RAM_STRICT",
      alerts: simulatedHostUsedMB > 3600 ? ['[ALERT] Approaching 4GB cgroup high water mark'] : []
    };
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  sendSnapshot();

  const intervalId = setInterval(sendSnapshot, 5000);

  req.on('close', () => {
    clearInterval(intervalId);
  });
});
