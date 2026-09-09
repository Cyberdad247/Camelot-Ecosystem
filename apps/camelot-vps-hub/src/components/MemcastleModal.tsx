import React, { useState } from 'react';
import { X, Crown, Database, HardDrive, Key, Layers, Sparkles, Check, ArrowRight } from 'lucide-react';

interface MemcastleModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MemcastleModal: React.FC<MemcastleModalProps> = ({ isOpen, onClose }) => {
  const [selectedKey, setSelectedKey] = useState<string>('/vfs/mempalace/agent_dag/latest');

  if (!isOpen) return null;

  const sampleKeys = [
    { key: '/vfs/mempalace/agent_dag/latest', size: '14.2 KB', ttl: '300s', type: 'DAG_AST', hits: '1,429' },
    { key: '/vfs/mempalace/ouroboros/ssm_weights_q158', size: '48.0 KB', ttl: 'PERM', type: 'TERNARY_WEIGHTS', hits: '89,412' },
    { key: '/vfs/mempalace/open_notebook/reasoning_trace', size: '32.1 KB', ttl: '600s', type: 'Z3_PROOFS', hits: '582' },
    { key: '/vfs/mempalace/notebooklm/context_ast', size: '18.4 KB', ttl: '120s', type: 'AST_INDEX', hits: '3,810' },
    { key: '/vfs/mempalace/viking/stream_channel_0', size: '64.0 KB', ttl: '60s', type: 'DMA_RING_BUFFER', hits: '142,091' }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-3xl rounded-2xl bg-[#080d1a] border-2 border-purple-500/50 shadow-[0_0_50px_rgba(168,85,247,0.3)] p-6 font-mono text-slate-300">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-purple-500/30 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-purple-950/80 border border-purple-400/60 text-purple-300 shadow-[0_0_20px_rgba(168,85,247,0.4)]">
              <Crown className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">
                  APEX CACHE SANCTUARY
                </span>
                <span className="px-2 py-0.5 text-[9px] bg-purple-500/20 text-purple-200 rounded border border-purple-400/40">
                  REDIS 7.2.4 NATIVE
                </span>
              </div>
              <h2 className="text-xl font-bold text-white font-heraldic tracking-wide">
                REDIS MEMCASTLE <span className="text-sm font-terminal text-amber-400 font-normal">[/vfs/mempalace/*]</span>
              </h2>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-900 hover:bg-purple-950 text-slate-400 hover:text-white border border-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 my-4">
          
          {/* Key Explorer (Left) */}
          <div className="md:col-span-6 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800 pb-1">
              <span>LIVE VFS KEYS ({sampleKeys.length})</span>
              <span className="text-purple-400 font-bold">128MB SLAB</span>
            </div>

            <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
              {sampleKeys.map((item) => (
                <div
                  key={item.key}
                  onClick={() => setSelectedKey(item.key)}
                  className={`p-2 rounded-lg border text-left cursor-pointer transition-all ${
                    selectedKey === item.key
                      ? 'bg-purple-950/80 border-purple-400 text-white shadow-[0_0_10px_rgba(168,85,247,0.3)]'
                      : 'bg-[#050914] border-slate-800 hover:border-purple-500/40 text-slate-400'
                  }`}
                >
                  <div className="text-[10px] font-bold truncate text-purple-300">{item.key}</div>
                  <div className="flex items-center justify-between text-[8px] text-slate-400 mt-1">
                    <span>{item.type}</span>
                    <span>{item.size} | {item.hits} hits</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Value Inspector (Right) */}
          <div className="md:col-span-6 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800 pb-1">
              <span>KEY INSPECTOR & STATS</span>
              <span className="text-emerald-400">LATENCY: 0.18ms</span>
            </div>

            <div className="p-3 rounded-xl bg-[#04060d] border border-purple-900/60 text-[10px] space-y-2 text-slate-300">
              <div>
                <span className="text-slate-500 block">KEY URI:</span>
                <span className="text-cyan-300 font-bold break-all">{selectedKey}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[9px] pt-1 border-t border-slate-800">
                <div>
                  <span className="text-slate-500">MAXMEMORY POLICY:</span>
                  <p className="text-amber-300">allkeys-lru</p>
                </div>
                <div>
                  <span className="text-slate-500">CGROUP LIMIT:</span>
                  <p className="text-purple-300">256 MB</p>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800">
                <span className="text-slate-500 block mb-1">AST SERIALIZED PAYLOAD (SNAPPY):</span>
                <pre className="p-2 rounded bg-slate-950 border border-slate-800 text-[8px] text-emerald-400 overflow-x-auto">
{`{
  "protocol": "CAMELOT_VFS_MEMPALACE_v1",
  "root_node": "0x7fffb8e920",
  "quantization": "1.58_BIT_TERNARY",
  "z3_signature": "0x98f4e2...PROVED",
  "lease_valid_until": 1787629999
}`}
                </pre>
              </div>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="border-t border-purple-500/30 pt-3 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-slate-400">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Zero-copy shared memory buffer with Rust hot path.</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-purple-900 hover:bg-purple-800 text-purple-200 border border-purple-400/50 font-bold transition-all"
          >
            DISMISS
          </button>
        </div>

      </div>
    </div>
  );
};
