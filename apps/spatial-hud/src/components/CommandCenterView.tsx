import React, { useState } from 'react';
import { ThemeMode } from '../types';
import { ThreeUIEngine } from './ThreeUIEngine';
import { MultiVoiceRouterDeck } from './MultiVoiceRouterDeck';
import { SovereignHeraldry } from './SovereignHeraldry';
import { 
  Shield, 
  Radio, 
  Sparkles, 
  Terminal, 
  Cpu, 
  Flame, 
  RefreshCw, 
  Zap, 
  Sliders, 
  Layers, 
  Eye, 
  Maximize2 
} from 'lucide-react';
import { multiVoiceRouter } from '../services/multiVoiceRouter';
import { motion } from 'motion/react';

interface CommandCenterViewProps {
  theme?: ThemeMode;
  onKineticTrigger: (cmd: string) => void;
}

export const CommandCenterView: React.FC<CommandCenterViewProps> = ({
  theme = 'dark',
  onKineticTrigger
}) => {
  const isDark = theme === 'dark';

  const [activeSubMode, setActiveSubMode] = useState<'hologram' | 'multivoice' | 'heraldry' | 'unified'>('unified');
  const [selectedNodeInfo, setSelectedNodeInfo] = useState<string | null>(null);

  const handleNodeClick = (nodeName: string) => {
    setSelectedNodeInfo(nodeName);
    multiVoiceRouter.playCyberSfx('lock');
    if (nodeName.includes('SHIELD') || nodeName.includes('CROWN')) {
      multiVoiceRouter.speakAsKnight('arthur', 'High Sovereign Heraldry locked. Home of Camelot-OS is fortified.');
    } else if (nodeName.includes('AUDIO')) {
      multiVoiceRouter.speakAsKnight('visage', 'Audio frequency spectrum analyzer channel focused.');
    } else if (nodeName.includes('FACTORY')) {
      multiVoiceRouter.speakAsKnight('hydron', `Digital factory workstation ${nodeName} online.`);
    }
  };

  return (
    <div className={`w-full min-h-[88vh] flex flex-col gap-6 p-4 lg:p-6 overflow-y-auto ${
      isDark ? 'bg-[#050507] text-white' : 'bg-slate-100 text-slate-900'
    }`}>
      
      {/* COMMAND CENTER HEADER & VIEW MODE SELECTOR */}
      <div className={`border p-4 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isDark ? 'bg-[#0A0710]/90 border-cyan-500/30' : 'bg-white/95 border-cyan-600/30 shadow-md'
      }`}>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500 text-black font-bold">
            <Zap className="w-5 h-5 text-black" />
          </div>
          <div>
            <h1 className="text-base lg:text-lg font-black tracking-widest font-mono uppercase text-cyan-400">
              CAMELOT-OS UNIFIED COMMAND CENTER
            </h1>
            <p className="text-xs font-mono opacity-75">
              ThreeUI WebGPU Spatial Engine // Multivoice-Router Substrate // Invisioned Marketing Node
            </p>
          </div>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-black/40 border border-white/10 text-xs font-mono">
          {[
            { id: 'unified', label: 'UNIFIED DECK' },
            { id: 'hologram', label: '3D THREEUI' },
            { id: 'multivoice', label: 'MULTIVOICE ROUTER' },
            { id: 'heraldry', label: 'HERALDRY CREST' }
          ].map((mode) => (
            <button
              key={mode.id}
              onClick={() => {
                setActiveSubMode(mode.id as any);
                multiVoiceRouter.playCyberSfx('beep');
              }}
              className={`px-3 py-1 font-bold transition-all ${
                activeSubMode === mode.id
                  ? isDark 
                    ? 'bg-cyan-500 text-black shadow-[0_0_8px_rgba(0,229,255,0.4)]' 
                    : 'bg-cyan-600 text-white'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              {mode.label}
            </button>
          ))}
        </div>
      </div>

      {/* VIEW 1: UNIFIED DECK (ThreeUI 3D Stage on Left, Heraldry & MultiVoice on Right) */}
      {(activeSubMode === 'unified' || activeSubMode === 'hologram') && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* THREEUI 3D SPATIAL STAGE (Cols 1-7) */}
          <div className={`lg:col-span-7 border relative flex flex-col justify-between overflow-hidden min-h-[480px] ${
            isDark ? 'bg-[#050507] border-cyan-500/30' : 'bg-white border-cyan-600/30 shadow-lg'
          }`}>
            <div className="p-3 border-b border-cyan-500/20 flex items-center justify-between text-xs font-mono">
              <span className="font-bold text-cyan-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                THREEUI 3D VOLUMETRIC VIEWPORT (Cyberdad247/threeui)
              </span>
              <span className="text-[10px] opacity-70">INTERACTIVE ORBIT & RAYCASTING</span>
            </div>

            {/* 3D WebGL / WebGPU Substrate */}
            <div className="flex-1 w-full min-h-[380px] relative">
              <ThreeUIEngine
                theme={theme}
                activeMode="command"
                onSelectNode={handleNodeClick}
              />
            </div>

            {/* Viewport Footer Bar */}
            <div className="p-2.5 border-t border-cyan-500/20 bg-black/40 flex items-center justify-between text-[11px] font-mono">
              <span className="text-neutral-400">
                CLICK NODES TO INTERACT // ACTIVE: {selectedNodeInfo || 'SOVEREIGN_CORE'}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onKineticTrigger('//chaos:inject')}
                  className="px-2 py-0.5 bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-bold"
                >
                  //chaos:inject
                </button>
                <button
                  onClick={() => onKineticTrigger('//rezero')}
                  className="px-2 py-0.5 bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-[10px] font-bold"
                >
                  //rezero
                </button>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: HERALDRY CRESTS & QUICK DISPATCH (Cols 8-12) */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            <SovereignHeraldry variant="combined" theme={theme} />
          </div>

        </div>
      )}

      {/* VIEW 2: MULTIVOICE ROUTER DECK (Underlayer Component) */}
      {(activeSubMode === 'unified' || activeSubMode === 'multivoice') && (
        <div className="w-full">
          <MultiVoiceRouterDeck
            theme={theme}
            onExecuteIntent={(intent) => {
              onKineticTrigger(intent);
            }}
          />
        </div>
      )}

      {/* VIEW 3: DEDICATED HERALDRY VIEW */}
      {activeSubMode === 'heraldry' && (
        <div className="w-full">
          <SovereignHeraldry variant="combined" theme={theme} className="max-w-5xl mx-auto" />
        </div>
      )}

    </div>
  );
};
