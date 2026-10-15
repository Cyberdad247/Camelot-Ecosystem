// SPDX-License-Identifier: MIT
// D.A.X. Master Skill Matrix Component: Omni-Marketing Fulfillment Canvas
// Authored under D.A.X. v10000.56 (Fulfillment Canvas // Node-Based DAG Architecture // A2UI)
// Chromatic Tokens: Obsidian Void (#050508, #0B0B0E), Surface Slate (#121217, #2A2A35), Luxora Gold (#D4AF37, #FFD700), Violet (#9D4EDD)
// 120fps Kinetic Response & Reactive Node-to-Node Pipeline

'use client';

import React, { useState } from 'react';

export interface NodeData {
  id: string;
  type: 'INGRESS' | 'RESEARCH' | 'DESIGN' | 'COMPILE' | 'AUDIT' | 'DEPLOY';
  title: string;
  agent: string;
  status: 'WAITING' | 'PROCESSING' | 'COMPLETE';
  position: { x: number; y: number };
  outputPayload?: string;
}

export interface EdgeConnection {
  from: string;
  to: string;
}

const DEFAULT_NODES: NodeData[] = [
  {
    id: '1',
    type: 'INGRESS',
    title: 'Client Onboarding Data',
    agent: 'Anya Ω',
    status: 'COMPLETE',
    position: { x: 40, y: 120 },
    outputPayload: 'Entity Spec: Invisioned Marketing Inc. (Omnichannel Agency)',
  },
  {
    id: '2',
    type: 'RESEARCH',
    title: 'Competitor Market Scraping',
    agent: 'Lady Apis',
    status: 'PROCESSING',
    position: { x: 340, y: 60 },
    outputPayload: 'Found 14 competitor ad creative & hook vectors',
  },
  {
    id: '3',
    type: 'DESIGN',
    title: 'Generate Asset Tokens',
    agent: 'Sir Visage',
    status: 'WAITING',
    position: { x: 340, y: 220 },
    outputPayload: 'DTCG 60-30-10 tokens (Obsidian / Gold / Violet)',
  },
  {
    id: '4',
    type: 'COMPILE',
    title: 'Build Conversion Lander',
    agent: 'Sir Hydron',
    status: 'WAITING',
    position: { x: 640, y: 140 },
    outputPayload: 'A2UI AST micro-component ready for DOM injection',
  },
];

const DEFAULT_EDGES: EdgeConnection[] = [
  { from: '1', to: '2' },
  { from: '1', to: '3' },
  { from: '2', to: '4' },
  { from: '3', to: '4' },
];

export function OmniFulfillmentCanvas() {
  const [nodes, setNodes] = useState<NodeData[]>(DEFAULT_NODES);
  const [edges] = useState<EdgeConnection[]>(DEFAULT_EDGES);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string>('2');
  const [activeStepLog, setActiveStepLog] = useState<string>(
    'DAG pipeline initialized. Node 2 (Lady Apis) currently processing market intelligence.'
  );

  const executePipeline = () => {
    setIsRunning(true);
    setActiveStepLog('Executing DAG Pipeline: Lady Apis scraping market data...');

    // Phase 1 -> Complete Node 2, start Node 3
    setTimeout(() => {
      setNodes((prev) =>
        prev.map((n) => (n.id === '2' ? { ...n, status: 'COMPLETE' } : n))
      );
      setActiveStepLog('Lady Apis finished. Sir Visage starting Design Token synthesis...');

      setTimeout(() => {
        setNodes((prev) =>
          prev.map((n) => (n.id === '3' ? { ...n, status: 'PROCESSING' } : n))
        );
        setSelectedNodeId('3');

        // Phase 2 -> Complete Node 3, start Node 4
        setTimeout(() => {
          setNodes((prev) =>
            prev.map((n) => (n.id === '3' ? { ...n, status: 'COMPLETE' } : n))
          );
          setActiveStepLog('Sir Visage generated tokens. Sir Hydron compiling conversion lander...');

          setTimeout(() => {
            setNodes((prev) =>
              prev.map((n) => (n.id === '4' ? { ...n, status: 'PROCESSING' } : n))
            );
            setSelectedNodeId('4');

            // Phase 3 -> Complete Node 4
            setTimeout(() => {
              setNodes((prev) =>
                prev.map((n) => (n.id === '4' ? { ...n, status: 'COMPLETE' } : n))
              );
              setIsRunning(false);
              setActiveStepLog(
                'Pipeline Complete: Lander generated and verified. All 4 nodes in COMPLETE state.'
              );
            }, 1800);
          }, 600);
        }, 1600);
      }, 600);
    }, 1500);
  };

  const resetPipeline = () => {
    setNodes(DEFAULT_NODES);
    setIsRunning(false);
    setSelectedNodeId('2');
    setActiveStepLog('DAG pipeline reset to baseline state.');
  };

  const getStatusBorder = (status: NodeData['status']) => {
    switch (status) {
      case 'COMPLETE':
        return 'border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.25)]';
      case 'PROCESSING':
        return 'border-[#D4AF37] shadow-[0_0_15px_rgba(212,175,55,0.35)] animate-pulse';
      case 'WAITING':
      default:
        return 'border-slate-800 opacity-70';
    }
  };

  const getStatusBadge = (status: NodeData['status']) => {
    switch (status) {
      case 'COMPLETE':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'PROCESSING':
        return 'text-[#D4AF37] bg-[#D4AF37]/10 border-[#D4AF37]/40';
      case 'WAITING':
      default:
        return 'text-slate-500 bg-slate-800/50 border-slate-700';
    }
  };

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || nodes[0];

  return (
    <div className="w-full bg-[#050508] p-4 md:p-8 font-sans text-slate-200 border-2 border-gold/40 shadow-[6px_6px_0px_0px_#D4AF37] rounded-xl">
      {/* Canvas Top Bar */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-5 mb-6 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-gold animate-pulse" />
            <span className="text-[10px] font-mono text-[#00E5FF] tracking-[0.25em] uppercase">
              OMNI-MARKETING FULFILLMENT // KINETIC DAG CANVAS
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase mt-1">
            The Agency <span className="text-gold">Kitchen</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Visual Node Assembly &bull; Autonomous Knight Data Handoffs &bull; A2UI Stream
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={resetPipeline}
            disabled={isRunning}
            className="px-3 py-2 bg-[#0B0B0E] hover:bg-slate-900 border border-slate-700 text-slate-300 font-mono text-xs uppercase tracking-wider rounded transition-all disabled:opacity-50"
          >
            RESET PIPELINE
          </button>
          <button
            type="button"
            onClick={executePipeline}
            disabled={isRunning}
            className="px-5 py-2.5 bg-gold hover:bg-gold-light text-obsidian font-mono font-black text-xs uppercase tracking-widest rounded shadow-[2px_2px_0px_0px_#000000] active:translate-y-0.5 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {/* Play SVG */}
            <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            {isRunning ? 'PIPELINE RUNNING...' : 'EXECUTE PIPELINE'}
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveStepLog(
                '[EXPORTER ACTIVATED]: Compiled AST deployed to client target (Next.js 14 / Shopify Storefront). URL: https://invisioned.client-preview.dev. Receipt: #0x86966760DC8C'
              );
            }}
            className="px-4 py-2.5 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400 text-emerald-300 font-mono font-black text-xs uppercase tracking-wider rounded transition-all flex items-center gap-1.5"
          >
            <svg className="w-3.5 h-3.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            DEPLOY TO CLIENT (SHOPIFY/NEXT.JS)
          </button>
        </div>
      </header>

      {/* Interactive Node Graph Canvas Surface */}
      <div className="relative w-full h-[380px] bg-[#09090D] border-2 border-[#2A2A35] rounded-xl overflow-hidden shadow-inner p-4">
        {/* Subtle Isometric Grid Texture */}
        <div
          className="absolute inset-0 opacity-15 pointer-events-none"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, #D4AF37 1px, transparent 0)',
            backgroundSize: '24px 24px',
          }}
        />

        {/* SVG Bezier Connection Lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          <defs>
            <linearGradient id="edgeGradActive" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#00E5FF" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="edgeGradMuted" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2A2A35" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#2A2A35" stopOpacity="0.4" />
            </linearGradient>
          </defs>

          {edges.map((edge, idx) => {
            const source = nodes.find((n) => n.id === edge.from);
            const target = nodes.find((n) => n.id === edge.to);
            if (!source || !target) return null;

            const x1 = source.position.x + 200; // source right edge
            const y1 = source.position.y + 40;  // source vertical center
            const x2 = target.position.x;       // target left edge
            const y2 = target.position.y + 40;  // target vertical center
            const dx = Math.abs(x2 - x1) * 0.5;

            const isActive =
              source.status === 'COMPLETE' &&
              (target.status === 'PROCESSING' || target.status === 'COMPLETE');

            return (
              <path
                key={idx}
                d={`M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`}
                fill="none"
                stroke={isActive ? 'url(#edgeGradActive)' : 'url(#edgeGradMuted)'}
                strokeWidth={isActive ? '2.5' : '1.5'}
                strokeDasharray={isActive ? '4 2' : 'none'}
                className={isActive ? 'animate-pulse' : ''}
              />
            );
          })}
        </svg>

        {/* Draggable/Interactive Canvas Nodes */}
        {nodes.map((node) => {
          const isSelected = selectedNodeId === node.id;

          return (
            <div
              key={node.id}
              onClick={() => setSelectedNodeId(node.id)}
              style={{
                left: `${node.position.x}px`,
                top: `${node.position.y}px`,
              }}
              className={`absolute w-[210px] bg-[#121217] p-3.5 rounded-xl border-2 cursor-pointer transition-all ${
                getStatusBorder(node.status)
              } ${
                isSelected
                  ? 'ring-2 ring-gold shadow-[0_0_20px_rgba(212,175,55,0.4)]'
                  : 'hover:scale-[1.02]'
              }`}
            >
              {/* Node Card Header */}
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-[9px] font-mono font-bold tracking-wider text-slate-400 uppercase">
                  {node.type}
                </span>
                <span
                  className={`text-[8px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase ${getStatusBadge(
                    node.status
                  )}`}
                >
                  {node.status}
                </span>
              </div>

              {/* Node Title & Assigned Agent */}
              <h4 className="text-xs font-black text-white leading-tight truncate">
                {node.title}
              </h4>
              <div className="text-[10px] font-mono text-gold font-bold mt-1">
                KNIGHT: {node.agent}
              </div>

              {/* Node Port Indicators */}
              <div className="flex justify-between items-center mt-2.5 pt-2 border-t border-slate-800 text-[8px] font-mono text-slate-500">
                <span>IN &bull; A2UI</span>
                <span>OUT &bull; TOON</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Node Inspector & Live Telemetry Console */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-12 gap-5">
        {/* Node Detail Inspector (7 cols) */}
        <div className="md:col-span-7 bg-[#121217] border border-[#2A2A35] rounded-xl p-5">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3 mb-3">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
              ACTIVE NODE INSPECTOR &bull; NODE #{selectedNode.id}
            </span>
            <span className="text-xs font-mono text-gold-royal font-bold">
              {selectedNode.agent}
            </span>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div>
              <span className="text-slate-500">TASK: </span>
              <span className="text-white font-bold">{selectedNode.title}</span>
            </div>
            <div>
              <span className="text-slate-500">STATUS: </span>
              <span
                className={`font-bold ${
                  selectedNode.status === 'COMPLETE'
                    ? 'text-emerald-400'
                    : selectedNode.status === 'PROCESSING'
                    ? 'text-gold'
                    : 'text-slate-400'
                }`}
              >
                {selectedNode.status}
              </span>
            </div>
            <div>
              <span className="text-slate-500">LIVE OUTPUT PAYLOAD: </span>
              <p className="mt-1 p-2.5 bg-[#0B0B0E] border border-slate-800 text-slate-300 rounded font-sans text-xs">
                {selectedNode.outputPayload || 'Awaiting execution trigger...'}
              </p>
            </div>
          </div>
        </div>

        {/* Live Execution Stream Log (5 cols) */}
        <div className="md:col-span-5 bg-[#121217] border border-[#2A2A35] rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center border-b border-slate-800 pb-3 mb-3">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                DAG STREAM MONITOR
              </span>
              <span className="text-[10px] font-mono text-emerald-400">120 FPS</span>
            </div>
            <p className="text-xs font-mono text-slate-400 leading-relaxed">
              {activeStepLog}
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[10px] font-mono text-slate-500 flex justify-between">
            <span>WORKER: DUKTAPE_WASM</span>
            <span className="text-gold">PROVENANCE: LOGGED</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OmniFulfillmentCanvas;
