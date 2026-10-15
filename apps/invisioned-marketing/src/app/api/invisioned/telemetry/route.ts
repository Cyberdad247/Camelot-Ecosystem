// SPDX-License-Identifier: MIT
import { NextResponse } from 'next/server';
import os from 'node:os';

interface AgentStatus {
  id: string;
  name: string;
  role: string;
  state: 'active' | 'standby' | 'optimizing' | 'offline';
  load: number;
  tokensProcessed: number;
  currentTask: string;
}

export async function GET() {
  try {
    const totalMemBytes = os.totalmem();
    const freeMemBytes = os.freemem();
    const usedMemBytes = totalMemBytes - freeMemBytes;

    const nodeMaxMemBytes = 4 * 1024 * 1024 * 1024; // 4096 MB Camelot Node Ceiling
    const serverMaxMemBytes = 8 * 1024 * 1024 * 1024; // 8192 MB Sovereign Hub Ceiling

    const agents: AgentStatus[] = [
      {
        id: 'sir_helios',
        name: 'Sir Helios',
        role: 'High Sentinel & CloudBrain Telemetry',
        state: 'active',
        load: 42,
        tokensProcessed: 142850,
        currentTask: 'Dynamic VFS Worktree Monitoring',
      },
      {
        id: 'anya_omega',
        name: 'Anya Ω',
        role: 'L7 Modality Hypervisor & Entropy Scythe',
        state: 'active',
        load: 28,
        tokensProcessed: 98400,
        currentTask: 'Zero-Bypass Gate Enforcement',
      },
      {
        id: 'lady_apis',
        name: 'Lady Apis',
        role: 'Swarm Conductor & Lead Hunter',
        state: 'optimizing',
        load: 64,
        tokensProcessed: 231500,
        currentTask: 'Deregulated Energy Prospect Enrichment',
      },
      {
        id: 'sir_visage',
        name: 'Sir Visage',
        role: 'Crucible Aesthetic & UI Architect',
        state: 'active',
        load: 35,
        tokensProcessed: 78900,
        currentTask: 'Spatial 2.5D Layout Calibration',
      },
      {
        id: 'sir_sonus',
        name: 'Sir Sonus',
        role: 'Multivoice Duplex Audio Sentinel',
        state: 'standby',
        load: 12,
        tokensProcessed: 43200,
        currentTask: 'Sub-100ms VAD Stream Monitoring',
      },
    ];

    return NextResponse.json({
      timestamp: new Date().toISOString(),
      node: {
        hostname: os.hostname(),
        platform: os.platform(),
        uptimeSeconds: Math.floor(os.uptime()),
        cpuLoadPercent: Math.min(100, Math.round(os.loadavg()[0] * 10 || 18)),
        memory: {
          usedMB: Math.round(usedMemBytes / (1024 * 1024)),
          totalMB: Math.round(totalMemBytes / (1024 * 1024)),
          nodeCapMB: 4096,
          serverCapMB: 8192,
          isWithinNodeBound: usedMemBytes <= nodeMaxMemBytes,
          isWithinServerBound: usedMemBytes <= serverMaxMemBytes,
        },
      },
      swarm: {
        activeCount: agents.filter((a) => a.state === 'active').length,
        totalKnights: agents.length,
        agents,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to retrieve telemetry', detail: String(error) },
      { status: 500 }
    );
  }
}
