import React, { useState, useEffect } from 'react';
import { KNIGHTS_ROSTER } from '../data/knightsData';
import { Knight } from '../types';
import { Network, Shield, Sparkles, Activity, Zap, Cpu, Lock } from 'lucide-react';

interface SwarmLatticeVisualizerProps {
  onSelectKnight?: (knight: Knight) => void;
}

export const SwarmLatticeVisualizer: React.FC<SwarmLatticeVisualizerProps> = ({ onSelectKnight }) => {
  const [selectedNode, setSelectedNode] = useState<Knight | null>(KNIGHTS_ROSTER[7] || null); // default to Merlin_Ω
  const [pulseTick, setPulseTick] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setPulseTick((t) => (t + 1) % 100);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 12 Outer nodes arranged in circle, 4 inner nodes, 1 core
  const coreKnights = KNIGHTS_ROSTER.slice(0, 16);

  return (
    <div className="flex-1 flex flex-col lg:flex-row h-full bg-neutral-950 text-neutral-100 overflow-hidden font-mono">
      {/* Visual Canvas Area */}
      <div className="flex-1 relative flex flex-col items-center justify-center p-6 bg-radial from-neutral-900/80 via-neutral-950 to-black overflow-hidden border-b lg:border-b-0 lg:border-r border-neutral-800">
        
        {/* Canvas Background Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#171717_1px,transparent_1px),linear-gradient(to_bottom,#171717_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

        {/* Top Controls & Lattice Header */}
        <div className="absolute top-6 left-6 z-10 flex items-center space-x-3 bg-neutral-900/80 backdrop-blur border border-neutral-800 px-4 py-2 rounded-xl shadow-lg">
          <Network className="w-5 h-5 text-sky-400 animate-pulse" />
          <div>
            <h3 className="text-xs font-bold text-white font-sans uppercase tracking-wider">
              24D Leech Lattice Swarm Topology
            </h3>
            <p className="text-[10px] text-neutral-400">Kissing Number: 196,560 | 1.58-bit Ternary SSM</p>
          </div>
        </div>

        {/* Center Node Interactive Visualization Map */}
        <div className="relative w-full max-w-xl aspect-square flex items-center justify-center">
          
          {/* Animated Orbit Rings */}
          <div className="absolute w-[80%] h-[80%] rounded-full border border-dashed border-neutral-800/80 animate-[spin_60s_linear_infinite]" />
          <div className="absolute w-[50%] h-[50%] rounded-full border border-neutral-800/60 animate-[spin_40s_linear_infinite_reverse]" />

          {/* SVG Connection Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {coreKnights.map((_, idx) => {
              const angle = (idx / coreKnights.length) * 2 * Math.PI;
              const x = 50 + 38 * Math.cos(angle);
              const y = 50 + 38 * Math.sin(angle);
              return (
                <line
                  key={idx}
                  x1="50%"
                  y1="50%"
                  x2={`${x}%`}
                  y2={`${y}%`}
                  stroke="rgba(245, 158, 11, 0.15)"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                />
              );
            })}
          </svg>

          {/* Center Hub: Merlin_Ω & Anya_Ω Core */}
          <div
            onClick={() => setSelectedNode(KNIGHTS_ROSTER.find(k => k.id === 'k-merlin') || null)}
            className="absolute z-20 w-24 h-24 rounded-full bg-gradient-to-br from-amber-500/30 to-purple-600/30 border-2 border-amber-400 flex flex-col items-center justify-center cursor-pointer hover:scale-110 transition-all duration-300 shadow-[0_0_30px_rgba(245,158,11,0.3)] group"
          >
            <Shield className="w-6 h-6 text-amber-300 group-hover:scale-125 transition-transform" />
            <span className="text-[10px] font-bold text-white mt-1">CORE_GATE</span>
            <span className="text-[8px] text-amber-300 font-mono">MERLIN / ANYA</span>
          </div>

          {/* Outer Ring Nodes */}
          {coreKnights.map((knight, idx) => {
            const angle = (idx / coreKnights.length) * 2 * Math.PI;
            const x = 50 + 38 * Math.cos(angle);
            const y = 50 + 38 * Math.sin(angle);
            const isSelected = selectedNode?.id === knight.id;

            return (
              <div
                key={knight.id}
                style={{
                  left: `${x}%`,
                  top: `${y}%`,
                  transform: 'translate(-50%, -50%)',
                }}
                onClick={() => {
                  setSelectedNode(knight);
                  if (onSelectKnight) onSelectKnight(knight);
                }}
                className={`absolute z-10 w-12 h-12 rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all duration-200 shadow-md ${
                  isSelected
                    ? 'bg-amber-400 text-neutral-950 scale-125 ring-4 ring-amber-500/40 font-bold'
                    : 'bg-neutral-900 border border-neutral-700 text-neutral-200 hover:border-amber-400 hover:bg-neutral-800'
                }`}
              >
                <div className="w-2 h-2 rounded-full mb-1 bg-emerald-400 animate-pulse" />
                <span className="text-[9px] font-mono leading-none truncate max-w-[40px] text-center">
                  {knight.name.split('_')[0].split(' ')[0]}
                </span>
              </div>
            );
          })}
        </div>

        <div className="absolute bottom-6 z-10 text-[11px] text-neutral-500 bg-neutral-900/60 backdrop-blur px-4 py-1.5 rounded-full border border-neutral-800">
          Click any node on the coordinate plane to inspect sub-agent telemetry & capability leases.
        </div>
      </div>

      {/* Selected Node Telemetry Sidebar */}
      <aside className="w-full lg:w-96 bg-neutral-900 p-6 flex flex-col justify-between overflow-y-auto space-y-6 shrink-0 border-l border-neutral-800">
        {selectedNode ? (
          <div className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800/40">
                  {selectedNode.division}
                </span>
                <span className="text-xs text-emerald-400 flex items-center gap-1 font-semibold">
                  <Activity className="w-3.5 h-3.5" />
                  {selectedNode.status}
                </span>
              </div>
              <h2 className="text-2xl font-bold text-white font-sans tracking-tight">
                {selectedNode.name}
              </h2>
              <p className="text-xs text-neutral-400 italic mt-0.5">{selectedNode.avatarTitle}</p>
            </div>

            {/* Load Meter */}
            <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-neutral-400 flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-amber-400" />
                  Current Compute Load
                </span>
                <span className="font-bold text-amber-300">{selectedNode.load}%</span>
              </div>
              <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-red-500 rounded-full transition-all duration-500"
                  style={{ width: `${selectedNode.load}%` }}
                />
              </div>
            </div>

            {/* Description / Bio */}
            <div className="space-y-1.5">
              <h4 className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">Mission Statement:</h4>
              <p className="text-xs text-neutral-300 font-sans leading-relaxed bg-neutral-950 p-3.5 rounded-xl border border-neutral-800/80">
                {selectedNode.bio}
              </p>
            </div>

            {/* Domain & Capability Matrix */}
            <div className="space-y-2">
              <h4 className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">Assigned Capabilities:</h4>
              <div className="flex flex-wrap gap-1.5">
                {selectedNode.skills.map((skill) => (
                  <span
                    key={skill}
                    className="text-[11px] bg-neutral-950 text-neutral-300 border border-neutral-800 px-2.5 py-1 rounded-lg"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Assigned Domain */}
            <div className="p-3 bg-neutral-950 rounded-xl border border-neutral-800 text-xs">
              <span className="text-[10px] text-neutral-500 uppercase tracking-wider block mb-0.5">Primary Domain</span>
              <span className="text-sky-300 font-medium">{selectedNode.domain}</span>
            </div>
          </div>
        ) : (
          <div className="text-center text-neutral-500 my-auto">
            Select a knight node from the lattice.
          </div>
        )}

        <div className="pt-4 border-t border-neutral-800 text-[11px] text-neutral-500 flex items-center justify-between">
          <span>Topology: 24D Leech</span>
          <span>Entropy: 0.000</span>
        </div>
      </aside>
    </div>
  );
};
