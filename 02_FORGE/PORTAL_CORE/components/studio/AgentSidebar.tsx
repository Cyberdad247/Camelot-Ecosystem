'use client';

import React from 'react';

export default function AgentSidebar() {
  return (
    <div className="h-full w-64 bg-black border-l border-green-900 flex flex-col font-mono text-xs">
      <div className="p-3 border-b border-green-900 text-green-400 font-bold">⚔️ KNIGHT ROSTER</div>

      <div className="flex-1 p-2 space-y-2 overflow-y-auto">
        <div className="p-2 bg-green-900 bg-opacity-20 border border-green-800 rounded">
          <div className="font-bold text-green-300">Merlin_Omega</div>
          <div className="opacity-50">Orchestrator</div>
          <div className="text-[10px] mt-1 text-blue-400">● IDLE</div>
        </div>

        <div className="p-2 bg-gray-900 border border-gray-800 rounded opacity-50">
          <div className="font-bold">Sir Syntax</div>
          <div>Code Smith</div>
        </div>

        <div className="p-2 bg-gray-900 border border-gray-800 rounded opacity-50">
          <div className="font-bold">Sir Visage</div>
          <div>Visuals</div>
        </div>
      </div>

      <div className="p-3 border-t border-green-900">
        <div className="text-gray-500 mb-1">Active Cartridge:</div>
        <select className="w-full bg-black border border-green-700 text-green-500 p-1 rounded">
          <option>HAWK (Strategy)</option>
          <option>BEAVER (Build)</option>
          <option>ANT (Research)</option>
        </select>
      </div>
    </div>
  );
}
