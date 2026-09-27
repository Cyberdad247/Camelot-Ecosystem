// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
export const API_BASE = 'http://localhost:3001';

export interface Agent {
  name: string;
  status: string;
  last_active: string;
}

export interface OracleState {
  epoch: number;
  global_tension: number;
  factions: any[];
  resources: Record<string, string>;
}

export const api = {
  /**
   * Fetch Active Agents (Knights)
   */
  getAgents: async (): Promise<Agent[]> => {
    try {
      const res = await fetch(`${API_BASE}/system/agents`);
      if (!res.ok) return [];
      const data = await res.json();
      return data.agents || [];
    } catch (e) {
      console.error('API Error (getAgents):', e);
      return [];
    }
  },

  /**
   * Fetch Oracle World State
   */
  getWorldState: async (): Promise<OracleState | null> => {
    try {
      // Logic: In a real app, this would be a dedicated endpoint
      // For now, we assume state is exposed via /system/state or similar
      // Since it's not implemented, we mock it for development if fetch fails
      const res = await fetch(`${API_BASE}/oracle/state`);
      if (res.ok) return await res.json();

      // Mock Data for Dev
      return {
        epoch: 42,
        global_tension: 0.75,
        factions: [
          { name: 'Corp A', assets: ['Tower'] },
          { name: 'Rebels', assets: ['Bunker'] },
        ],
        resources: { Energy: 'Low' },
      };
    } catch (e) {
      console.warn('API Error (getWorldState), returning mock:', e);
      return {
        epoch: 42,
        global_tension: 0.75,
        factions: [
          { name: 'Corp A', assets: ['Tower'] },
          { name: 'Rebels', assets: ['Bunker'] },
        ],
        resources: { Energy: 'Low' },
      };
    }
  },

  /**
   * Fetch Ledger Stream
   */
  getLedger: async (lines = 50): Promise<{ lines: string[]; total: number }> => {
    try {
      const res = await fetch(`${API_BASE}/system/ledger?lines=${lines}`);
      if (!res.ok) return { lines: [], total: 0 };
      const data = await res.json();
      return { lines: data.lines || [], total: data.total_lines || 0 };
    } catch (e) {
      console.error('API Error (getLedger):', e);
      return { lines: [], total: 0 };
    }
  },

  /**
   * Send Command to Kernel
   */
  sendCommand: async (command: string): Promise<string> => {
    try {
      const res = await fetch(`${API_BASE}/agent/dispatch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: command }),
      });
      const data = await res.json();
      return data.response || 'No response';
    } catch (e) {
      return `Error: ${e}`;
    }
  },
};
