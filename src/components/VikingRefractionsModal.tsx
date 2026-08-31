import React, { useState } from 'react';
import { X, Anchor, Waves, Terminal, Shield, RefreshCw, Cpu, Check, ArrowRight } from 'lucide-react';

interface VikingRefractionsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const VikingRefractionsModal: React.FC<VikingRefractionsModalProps> = ({ isOpen, onClose }) => {
  const [selectedChannel, setSelectedChannel] = useState<number>(0);

  if (!isOpen) return null;

  const channels = [
    { name: 'STREAM_CHANNEL_0', target: '/vfs/refractions/char_states', throughput: '1.2 GB/s', latency: '12 μs', status: 'SYNCHRONIZED', progress: 88 },
    { name: 'STREAM_CHANNEL_1', target: '/vfs/refractions/prompt_scaffolding', throughput: '840 MB/s', latency: '18 μs', status: 'STREAMING', progress: 95 },
    { name: 'STREAM_CHANNEL_2', target: '/vfs/refractions/agent_dag', throughput: '2.1 GB/s', latency: '9 μs', status: 'DMA_LOCK', progress: 76 },
    { name: 'STREAM_CHANNEL_3', target: '/vfs/refractions/context_hydration', throughput: '1.8 GB/s', latency: '14 μs', status: 'HYDRATED', progress: 92 },
    { name: 'STREAM_CHANNEL_4', target: '/vfs/refractions/sandbox_boundary', throughput: 'VERIFIED', latency: '4 μs', status: 'ENFORCED', progress: 100 }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-3xl rounded-2xl bg-[#080d1a] border-2 border-cyan-500/50 shadow-[0_0_50px_rgba(34,211,238,0.3)] p-6 font-mono text-slate-300">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-cyan-500/30 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-950/80 border border-cyan-400/60 text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.4)]">
              <Anchor className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-widest">
                  OPEN VIKING REFRACTION PROTOCOL
                </span>
                <span className="px-2 py-0.5 text-[9px] bg-emerald-500/20 text-emerald-200 rounded border border-emerald-400/40">
                  DMA RING BUFFER ACTIVE
                </span>
              </div>
              <h2 className="text-xl font-bold text-white tracking-wide">
                VFS REFRACTIONS <span className="text-sm font-terminal text-emerald-400 font-normal">[/vfs/refractions/*]</span>
              </h2>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-900 hover:bg-cyan-950 text-slate-400 hover:text-white border border-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 my-4">
          {/* Channels List */}
          <div className="md:col-span-6 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800 pb-1">
              <span>ACTIVE VFS CHANNELS</span>
              <span className="text-emerald-400 font-bold">5 ONLINE</span>
            </div>

            <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
              {channels.map((ch, idx) => (
                <div
                  key={ch.name}
                  onClick={() => setSelectedChannel(idx)}
                  className={`p-2.5 rounded-lg border cursor-pointer transition-all ${
                    selectedChannel === idx
                      ? 'bg-cyan-950/60 border-cyan-400 text-cyan-200 shadow-[0_0_10px_rgba(34,211,238,0.2)]'
                      : 'bg-slate-900/50 border-slate-800 hover:border-cyan-800 text-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-bold mb-1">
                    <span className="text-cyan-300">{ch.name}</span>
                    <span className="text-[10px] text-emerald-400">{ch.throughput}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 truncate mb-1.5">{ch.target}</div>
                  <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 rounded-full"
                      style={{ width: `${ch.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Channel Detail Inspector */}
          <div className="md:col-span-6 flex flex-col justify-between bg-slate-900/70 border border-cyan-900/60 rounded-xl p-4">
            <div>
              <div className="flex items-center justify-between border-b border-cyan-950 pb-2 mb-3">
                <span className="text-xs font-bold text-amber-300">CHANNEL TELEMETRY</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/40">
                  {channels[selectedChannel].status}
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Target Path:</span>
                  <span className="text-cyan-300 font-mono">{channels[selectedChannel].target}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Throughput:</span>
                  <span className="text-emerald-300 font-bold">{channels[selectedChannel].throughput}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">DMA Ring Latency:</span>
                  <span className="text-amber-300 font-bold">{channels[selectedChannel].latency}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800">
                  <span className="text-slate-400">Zero-Copy DMA:</span>
                  <span className="text-cyan-400 font-bold">ACTIVE (ring_buf_0x7F)</span>
                </div>
              </div>
            </div>

            <div className="mt-4 p-2.5 rounded bg-slate-950 border border-emerald-900/50 text-[10px] text-emerald-400">
              [VFS_DMA] Memory barrier satisfied. Ring buffer pointer: 0x00FF89E10A. High-velocity context streaming enabled.
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-cyan-950 pt-3 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <Waves className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span>Emerald Data Rivers // Sovereign Viking Navigation Matrix</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-cyan-950 hover:bg-cyan-900 text-cyan-200 border border-cyan-500/50 transition-colors"
          >
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
};
