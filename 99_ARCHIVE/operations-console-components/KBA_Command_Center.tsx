"use client";

import React, { useState } from 'react';
import { useBifrostConduit } from '../hooks/useBifrostConduit';
import { ShieldCheck, Mic, MicOff, Activity, Cpu } from 'lucide-react';

export const KBA_Command_Center: React.FC = () => {
  const { isConnected, videoRef, telemetry } = useBifrostConduit();
  const [micActive, setMicActive] = useState(true);

  return (
    <div className="bg-[#0B0B0E] min-h-screen text-white font-mono p-4">
      {/* 12-Column Grid */}
      <div className="grid grid-cols-12 gap-4 h-full">
        
        {/* Header spanning all columns */}
        <header className="col-span-12 border-b border-[#D4AF37] pb-4 mb-4 flex justify-between items-center">
          <h1 className="text-[#D4AF37] text-3xl font-bold tracking-widest uppercase">
            KBA Sovereign Command
          </h1>
          <div className={`px-3 py-1 text-xs border ${isConnected ? 'border-[#D4AF37] text-[#D4AF37]' : 'border-red-600 text-red-600'} flex items-center gap-2 uppercase`}>
            {isConnected ? 'Bifrost Linked' : 'Bifrost Disconnected'}
            <ShieldCheck size={14} />
          </div>
        </header>

        {/* Left Panel: Knight Roster */}
        <aside className="col-span-3 border border-[#333] bg-black/50 p-4">
          <h2 className="text-[#9D4EDD] text-sm uppercase tracking-widest border-b border-[#333] pb-2 mb-4 flex items-center gap-2">
            <Cpu size={16} /> Active Roster
          </h2>
          <ul className="space-y-4">
            <li className="flex justify-between text-xs">
              <span className="text-[#D4AF37]">[LADY ETHEREA]</span>
              <span className="text-gray-500">UI / VDOM</span>
            </li>
            <li className="flex justify-between text-xs">
              <span className="text-[#D4AF37]">[LORD VESPER]</span>
              <span className="text-gray-500">VAD / PCM</span>
            </li>
            <li className="flex justify-between text-xs">
              <span className="text-[#D4AF37]">[SIR CODA]</span>
              <span className="text-gray-500">mTLS / WebRTC</span>
            </li>
          </ul>
        </aside>

        {/* Center Panel: LaKesha Viewport */}
        <main className="col-span-6 relative border border-[#D4AF37] bg-black shadow-[0_0_20px_rgba(212,175,55,0.1)] flex items-center justify-center min-h-[500px]">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            className="absolute inset-0 w-full h-full object-cover opacity-80"
          />
          
          {/* Overlay: Nameplate */}
          <div className="absolute bottom-4 left-4 bg-[#0B0B0E]/80 border border-[#9D4EDD] p-2 backdrop-blur-sm">
            <div className="text-[#9D4EDD] text-xs font-bold uppercase tracking-widest">
              Ambassador LaKesha
            </div>
            <div className="text-[10px] text-gray-400">Executive Voice Hypervisor</div>
          </div>

          {/* Overlay: Mic Toggle */}
          <button 
            onClick={() => setMicActive(!micActive)}
            className={`absolute bottom-4 right-4 p-3 border transition-colors ${
              micActive ? 'border-[#D4AF37] bg-[#D4AF37]/20 text-[#D4AF37]' : 'border-red-600 bg-red-900/40 text-red-500'
            }`}
          >
            {micActive ? <Mic size={20} /> : <MicOff size={20} />}
          </button>
        </main>

        {/* Right Panel: Telemetry */}
        <aside className="col-span-3 border border-[#333] bg-black/50 p-4">
          <h2 className="text-gray-400 text-sm uppercase tracking-widest border-b border-[#333] pb-2 mb-4 flex items-center gap-2">
            <Activity size={16} /> Bifrost Telemetry
          </h2>
          <div className="space-y-4 font-mono">
            <div>
              <div className="text-[10px] text-gray-500 uppercase">Memory Alloc</div>
              <div className="text-xl text-[#D4AF37]">{telemetry.memoryAlloc}</div>
            </div>
            <div>
              <div className="text-[10px] text-gray-500 uppercase">VAD Latency</div>
              <div className="text-xl text-[#9D4EDD]">{telemetry.vadLatency}</div>
            </div>
          </div>
        </aside>

      </div>
    </div>
  );
};
