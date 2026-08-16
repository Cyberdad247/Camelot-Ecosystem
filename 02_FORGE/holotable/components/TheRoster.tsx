'use client';

import { useEffect, useState } from 'react';
import { Agent, api } from '@/lib/api';
import { Bot, Zap, Brain, Shield } from 'lucide-react';

export default function TheRoster() {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    // Poll every 5 seconds
    const interval = setInterval(async () => {
      const data = await api.getAgents();
      setAgents(data);
    }, 5000);

    // Initial fetch
    api.getAgents().then(setAgents);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel p-4 rounded-xl">
      <h2 className="text-xl font-mono font-bold text-primary mb-4 flex items-center gap-2">
        <Bot className="w-5 h-5" /> ACTIVE KNIGHTS
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className="border border-slate-800 bg-slate-900/50 p-3 rounded-lg flex items-center gap-3"
          >
            <div
              className={`w-2 h-2 rounded-full ${agent.status === 'ACTIVE' ? 'bg-green-500 neon-border' : 'bg-slate-500'}`}
            />

            <div>
              <div className="font-bold text-slate-200">{agent.name}</div>
              <div className="text-xs text-slate-500 font-mono">{agent.status}</div>
            </div>

            <div className="ml-auto">
              <Brain className="w-4 h-4 text-purple-500 opacity-50" />
            </div>
          </div>
        ))}

        {agents.length === 0 && (
          <div className="text-slate-500 italic text-sm">No active signals...</div>
        )}
      </div>
    </div>
  );
}
