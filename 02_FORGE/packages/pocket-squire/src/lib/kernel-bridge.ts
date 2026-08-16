// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
export const KERNEL_API = process.env.NEXT_PUBLIC_KERNEL_API || 'http://localhost:8001';

/**
 * POCKET SQUIRE KERNEL BRIDGE
 * Connects the Mobile PWA to the Sovereign Kernel via simple HTTP/REST (initially).
 * Future upgrade: WebSocket for dual streaming.
 */

// Simple typed interface for the Kernel Response
export interface KernelResponse<T = any> {
  status: 'SUCCESS' | 'ERROR';
  data?: T;
  msg?: string;
}

// 1. Check Connection (Heartbeat)
export async function checkKernelHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${KERNEL_API}/health`, {
      signal: AbortSignal.timeout(2000),
    });
    return res.ok;
  } catch (e) {
    return false;
  }
}

// 2. Dispatch Command (A2A Protocol Wrapper)
export async function dispatchCommand(
  intent: string,
  agentId: string = 'MERLIN',
): Promise<KernelResponse> {
  try {
    const payload = {
      agent_id: agentId,
      intent: intent,
      source: 'POCKET_SQUIRE_MOBILE',
    };

    const res = await fetch(`${KERNEL_API}/agent/dispatch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-camelot-token': 'merlin-v100-dev', // Shared Secret
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error('Kernel Rejected Command');
    return await res.json();
  } catch (e: any) {
    return { status: 'ERROR', msg: e.message || 'Network Error' };
  }
}

// 3. Stream Logs (Mock for now, would be SSE/WS)
export async function fetchAgentLogs() {
  // In v1, we poll. In v2, we socket.
  return [];
}
