import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Send } from 'lucide-react';
import QuantumScene from '@/components/engine/Scene';
import { useEngineStore } from './engineStore';
import { useAnyaSocket } from './useAnyaSocket';
import { runtimeConfig } from '@/config/runtime';
import { bifrostFetch } from '@/lib/bifrostClient';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const LOCAL_DISPATCH_URL = runtimeConfig.bifrost.dispatchUrl;

function formatDispatchResponse(data: any): string {
  const payload = data?.payload ?? data;
  const route = payload?.route ?? {};
  const result = payload?.result ?? {};

  const lines: string[] = [];
  if (payload?.status) lines.push(`status: ${payload.status}`);
  if (payload?.execution_target) lines.push(`execution_target: ${payload.execution_target}`);
  if (route?.knight_id) lines.push(`route_knight: ${route.knight_id}`);
  if (route?.engine) lines.push(`route_engine: ${route.engine}`);
  if (payload?.service) lines.push(`service: ${payload.service}`);

  if (typeof result?.brief === 'string' && result.brief.trim()) {
    lines.push('');
    lines.push(result.brief.trim());
  } else if (typeof result?.bridge_response?.result === 'string' && result.bridge_response.result.trim()) {
    lines.push('');
    lines.push(result.bridge_response.result.trim());
  } else if (typeof data?.response === 'string' && data.response.trim()) {
    lines.push('');
    lines.push(data.response.trim());
  } else if (typeof result?.archivist_voice === 'string' && result.archivist_voice.trim()) {
    lines.push('');
    lines.push(result.archivist_voice.trim());
  }

  if (payload?.error) {
    lines.push('');
    lines.push(`error: ${payload.error}`);
  }

  return lines.filter(Boolean).join('\n') || 'No response.';
}

export default function BrainInterface() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const addObject = useEngineStore((state) => state.addObject);
  const { isConnected, latestEvent } = useAnyaSocket();

  useEffect(() => {
    if (!latestEvent) {
      return;
    }
    if (latestEvent.event === 'bridge.ready') {
      setMessages((prev) => {
        if (prev.some((message) => message.content.includes('websocket uplink established'))) {
          return prev;
        }
        return [
          ...prev,
          {
            role: 'assistant',
            content: `${latestEvent.source}: ${latestEvent.detail}`,
          },
        ];
      });
      return;
    }
    if (latestEvent.event === 'dispatch.accepted' || latestEvent.event === 'dispatch.completed') {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `[${latestEvent.event}] ${latestEvent.source ?? 'bridge'}${latestEvent.detail ? ` | ${latestEvent.detail}` : ''}`,
        },
      ]);
    }
  }, [latestEvent]);

  const handleAsk = async () => {
    const cleanQuery = query.trim();
    if (!cleanQuery) return;

    if (cleanQuery.toLowerCase().includes('spawn cube')) {
      const cubeId = `cube-${Date.now()}`;
      addObject({
        id: cubeId,
        type: 'cube',
        position: [0, 2.5, 0],
        color: '#22d3ee',
      });
      setMessages((prev) => [
        ...prev,
        { role: 'user', content: cleanQuery },
        { role: 'assistant', content: `Spawned cube ${cubeId} in the Quantum Scene.` },
      ]);
      setQuery('');
      return;
    }

    const userMsg = { role: 'user' as const, content: cleanQuery };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await bifrostFetch(LOCAL_DISPATCH_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: userMsg.content,
          cartridge: 'COGNITIVE',
          preferred_knight: 'sir_alex',
          execution_target: 'analysis_only',
          metadata: {
            source: 'brain_ui',
            bridge_knight: 'sir_link',
          },
        })
      });

      const data = await res.json();
      const aiMsg = { role: 'assistant' as const, content: formatDispatchResponse(data) };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Local dispatch unreachable. Brain UI could not hand off through Sir Link." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-full w-full gap-4 p-4 bg-slate-950 overflow-y-auto lg:overflow-hidden">
      {/* Left Panel: Quantum Engine */}
      <div className="w-full lg:w-1/2 min-h-[300px] lg:h-full rounded-2xl overflow-hidden border border-slate-800 relative shadow-2xl shadow-cyan-900/20">
        <QuantumScene />
        <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-md px-3 py-1 rounded-full text-[10px] text-cyan-400 font-mono border border-cyan-500/30">
            QUANTUM RENDERER ACTIVE
        </div>
      </div>

      {/* Right Panel: Chat */}
      <Card className="flex-1 flex flex-col h-[500px] lg:h-full border-none shadow-2xl bg-slate-900/50 backdrop-blur-sm" 
            title="Anya's Interface"
            description="Commanding the Kernel & Engine">

        <div className="px-2 pb-2 text-[10px] uppercase tracking-widest">
          <span className={isConnected ? 'text-emerald-400' : 'text-amber-400'}>
            {isConnected ? 'websocket linked to morgana bridge' : 'websocket offline, dispatch still available'}
          </span>
        </div>
        
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-2">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                m.role === 'user' ? 'bg-cyan-600 text-white' : 'bg-slate-800 text-slate-200'
              }`}>
                {m.content}
              </div>
            </div>
          ))}
          {loading && <div className="text-slate-500 text-sm animate-pulse">Routing through Sir Alex and Sir Link...</div>}
        </div>

        <div className="flex gap-2">
          <input
            className="flex-1 px-4 py-2 rounded-full border border-slate-700 bg-slate-950 text-white focus:ring-2 focus:ring-cyan-500"
            placeholder="Ask a question or type 'spawn cube'..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
          />
          <button 
            onClick={handleAsk} 
            className="p-3 bg-cyan-600 rounded-full text-white"
            title="Send Message"
            aria-label="Send Message"
          >
            <Send size={20} />
          </button>
        </div>
      </Card>
    </div>
  );
}
