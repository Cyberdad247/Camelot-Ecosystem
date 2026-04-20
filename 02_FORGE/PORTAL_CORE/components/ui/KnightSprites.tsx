"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { useSocket } from '@/hooks/use-socket';

const KNIGHTS_META = [
  { name: 'Merlin', aliases: ['MERLIN', 'ARCHITECT'], pos: { bottom: '20%', left: '45%' }, sprite: '/assets/knights/merlin.png', color: 'shadow-yellow-500/50' },
  { name: 'Zenith', aliases: ['ZENITH', 'SENTINEL'], pos: { bottom: '15%', left: '70%' }, sprite: '/assets/knights/zenith.png', color: 'shadow-red-500/50' },
  { name: 'Anya', aliases: ['ANYA', 'COMPILER', 'ANYA_APEE'], pos: { bottom: '15%', left: '20%' }, sprite: '/assets/knights/anya.png', color: 'shadow-green-500/50' },
  // Percival uses Merlin's sprite for now or a placeholder if missing
  { name: 'Percival', aliases: ['PERCIVAL', 'GRAPH_WEAVER', 'SIR_PERCIVAL'], pos: { bottom: '25%', left: '30%' }, sprite: '/assets/knights/merlin.png', color: 'shadow-blue-500/50', isGhost: true },
];

export function KnightSprites() {
  const { logs, knightState } = useSocket();
  const lastLog = logs.length > 0 ? logs[logs.length - 1] : "";

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {KNIGHTS_META.map((knight, idx) => {
        // Activation Logic:
        // 1. Matches knightState name (Strongest signal)
        // 2. Matches lastLog content (Fallback signal)
        const stateMatch = knightState?.name ? knight.aliases.some(a => knightState.name.toUpperCase().includes(a)) : false;
        const logMatch = knight.aliases.some(alias => lastLog.toUpperCase().includes(alias));
        const isActive = stateMatch || logMatch;
        
        // Determine Thought Text
        const thoughtText = stateMatch ? knightState?.last_thought : (isActive && lastLog.includes("[THOUGHT]") ? lastLog.replace("[THOUGHT]", "") : null);

        return (
          <motion.div
            key={idx}
            className="absolute flex flex-col items-center"
            style={knight.pos}
            initial={{ y: 20, opacity: knight.isGhost ? 0.5 : 0 }}
            animate={{ 
              y: [0, -10, 0],
              opacity: knight.isGhost ? (isActive ? 0.9 : 0.4) : 1 
            }}
            transition={{ 
              y: { duration: 4, repeat: Infinity, ease: "easeInOut", delay: idx * 0.5 },
              opacity: { duration: 1 }
            }}
          >
            {/* THOUGHT BUBBLE */}
            <AnimatePresence>
              {isActive && thoughtText && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.5 }}
                  className="absolute -top-32 w-64 p-4 bg-black/60 backdrop-blur-xl border border-white/20 rounded-2xl pointer-events-auto z-50 text-center"
                >
                  <p className="text-xs text-blue-200 font-mono mb-1">
                    Running: {knightState?.current_task || "PROCESSING..."}
                  </p>
                  <p className="text-sm text-white font-serif italic leading-snug">
                    "{thoughtText}"
                  </p>
                  {/* Speech arrow */}
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-black/60 border-r border-b border-white/20 rotate-45 transform" />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Sprite Image */}
            <div className={`relative w-48 h-64 transition-all duration-500 ${isActive ? 'scale-110 z-20' : 'scale-100 z-10'} ${knight.isGhost ? 'opacity-80 mix-blend-screen' : ''}`}>
              <img 
                src={knight.sprite} 
                alt={knight.name} 
                className={`w-full h-full object-contain filter drop-shadow-[0_0_20px_rgba(255,255,255,0.2)] ${isActive ? 'brightness-125' : 'brightness-90'}`}
              />
              
              {/* Active Glow Ring */}
              {isActive && (
                <motion.div 
                  className={`absolute -bottom-4 left-1/2 -translate-x-1/2 w-32 h-8 bg-white/20 blur-xl rounded-full ${knight.color}`}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1.2, opacity: 1 }}
                />
              )}
            </div>

            {/* Label */}
            <div className={`mt-2 px-3 py-1 rounded-full border border-white/10 backdrop-blur-md transition-all ${isActive ? 'bg-white/20 text-white' : 'bg-black/40 text-gray-400'}`}>
              <span className="text-[10px] font-bold tracking-widest flex items-center gap-2">
                {isActive && <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"/>}
                {knight.name.toUpperCase()}
              </span>
            </div>
            
            {/* Stats (HP bar) */}
            {stateMatch && (
                 <div className="w-24 h-1 bg-gray-700 rounded-full mt-1 overflow-hidden">
                    <motion.div 
                        className={`h-full ${knight.name === 'Zenith' ? 'bg-red-500' : 'bg-blue-500'}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${knightState?.hp || 100}%` }}
                    />
                 </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}

import { AnimatePresence } from 'framer-motion';
