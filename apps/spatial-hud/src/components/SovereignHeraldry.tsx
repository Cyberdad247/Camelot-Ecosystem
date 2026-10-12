import React from 'react';
import { ThemeMode } from '../types';
import { Shield, Crown, Sparkles, Cpu, Radio, Network } from 'lucide-react';

interface SovereignHeraldryProps {
  variant?: 'camelot' | 'invisioned' | 'combined' | 'compact';
  theme?: ThemeMode;
  className?: string;
}

export const SovereignHeraldry: React.FC<SovereignHeraldryProps> = ({
  variant = 'combined',
  theme = 'dark',
  className = ''
}) => {
  const isDark = theme === 'dark';

  if (variant === 'compact') {
    return (
      <div className={`flex items-center gap-2 px-2.5 py-1 border ${
        isDark 
          ? 'bg-[#0A0710]/90 border-amber-500/30 text-amber-300' 
          : 'bg-amber-50/90 border-amber-400 text-amber-900 shadow-sm'
      } ${className}`}>
        <Crown className="w-4 h-4 text-amber-400 animate-pulse" />
        <div className="flex flex-col">
          <span className="text-[10px] font-bold tracking-widest font-mono">HOME OF CAMELOT-OS</span>
          <span className="text-[8px] opacity-70">INVISIONED MARKETING // AGENTIC SYSTEMS</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 w-full ${className}`}>
      
      {/* CREST 1: HOME OF CAMELOT-OS (Cybernetic Crown & Shield with AI Kernel) */}
      <div className={`relative border p-4 backdrop-blur-md overflow-hidden flex flex-col items-center justify-between ${
        isDark 
          ? 'bg-[#080511]/80 border-cyan-500/30 text-white shadow-[0_0_20px_rgba(0,229,255,0.08)]' 
          : 'bg-white/90 border-cyan-600/30 text-slate-900 shadow-md'
      }`}>
        {/* Technical Header Data */}
        <div className="w-full flex items-center justify-between text-[9px] font-mono border-b pb-1.5 mb-3 border-cyan-500/20">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
            <span className={isDark ? 'text-cyan-400' : 'text-cyan-700'}>SECURE_PROTOCOL v3.14</span>
          </div>
          <span className="text-amber-400 font-bold">STATUS: OPTIMAL</span>
        </div>

        {/* Heraldic Shield Graphic SVG */}
        <div className="relative w-48 h-52 my-1 flex items-center justify-center">
          <svg viewBox="0 0 200 240" className="w-full h-full drop-shadow-[0_0_12px_rgba(157,78,221,0.5)]">
            <defs>
              <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#2E1065" stopOpacity="0.9" />
                <stop offset="50%" stopColor="#1E0A3C" stopOpacity="0.95" />
                <stop offset="100%" stopColor="#0B0314" stopOpacity="1" />
              </linearGradient>
              <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#FDE047" />
                <stop offset="50%" stopColor="#E5B842" />
                <stop offset="100%" stopColor="#A16207" />
              </linearGradient>
              <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#22D3EE" />
                <stop offset="100%" stopColor="#0891B2" />
              </linearGradient>
              <pattern id="gridPattern" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(0, 229, 255, 0.15)" strokeWidth="0.5" />
              </pattern>
            </defs>

            {/* Shield Body */}
            <path
              d="M 100 20 L 175 45 L 160 160 L 100 225 L 40 160 L 25 45 Z"
              fill="url(#shieldGrad)"
              stroke="url(#cyanGrad)"
              strokeWidth="2.5"
            />
            {/* Grid Mesh Texture Inside Shield */}
            <path
              d="M 100 20 L 175 45 L 160 160 L 100 225 L 40 160 L 25 45 Z"
              fill="url(#gridPattern)"
            />

            {/* Golden Crown on Shield Top */}
            <path
              d="M 60 42 L 72 20 L 100 35 L 128 20 L 140 42 L 100 48 Z"
              fill="url(#goldGrad)"
              stroke="#FEF08A"
              strokeWidth="1.5"
            />
            <circle cx="72" cy="19" r="2.5" fill="#FEF08A" />
            <circle cx="100" cy="12" r="3.5" fill="#FEF08A" />
            <circle cx="128" cy="19" r="2.5" fill="#FEF08A" />

            {/* Center Golden Crystal Core (AI_KERNEL) */}
            <polygon
              points="100,75 130,115 100,165 70,115"
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth="3"
            />
            <polygon
              points="100,90 120,115 100,145 80,115"
              fill="#E5B842"
              fillOpacity="0.25"
              stroke="#00E5FF"
              strokeWidth="1.5"
            />
            <circle cx="100" cy="115" r="5" fill="#FEF08A" />

            {/* Lateral Wing Accents */}
            <path
              d="M 25 45 Q 5 80 15 120 Q 5 150 40 160"
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth="2"
            />
            <path
              d="M 175 45 Q 195 80 185 120 Q 195 150 160 160"
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth="2"
            />

            {/* Tech Labels in SVG */}
            <text x="100" y="180" textAnchor="middle" fill="#00E5FF" fontSize="7" fontFamily="monospace" fontWeight="bold">A.I._KERNEL</text>
            <text x="100" y="192" textAnchor="middle" fill="#E5B842" fontSize="6.5" fontFamily="monospace">DGT_STRUC</text>
          </svg>
        </div>

        {/* Crest Footer Title */}
        <div className="text-center mt-2">
          <div className="text-base font-black tracking-[0.25em] font-mono text-amber-400 drop-shadow-[0_0_8px_rgba(229,184,66,0.5)]">
            HOME OF CAMELOT-OS
          </div>
          <div className="text-[9px] font-mono opacity-80 mt-0.5 text-cyan-400 tracking-wider">
            CORE_INT_SYNC // 8GB EDGE SUBSTRATE
          </div>
        </div>
      </div>

      {/* CREST 2: INVISIONED MARKETING (Agentic Systems Consulting // Golden Knight) */}
      <div className={`relative border p-4 backdrop-blur-md overflow-hidden flex flex-col items-center justify-between ${
        isDark 
          ? 'bg-[#080511]/80 border-purple-500/30 text-white shadow-[0_0_20px_rgba(157,78,221,0.08)]' 
          : 'bg-white/90 border-purple-600/30 text-slate-900 shadow-md'
      }`}>
        {/* Technical Header Data */}
        <div className="w-full flex items-center justify-between text-[9px] font-mono border-b pb-1.5 mb-3 border-purple-500/20">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span className={isDark ? 'text-purple-300' : 'text-purple-700'}>AGENTIC CONSULTING MATRIX</span>
          </div>
          <span className="text-cyan-400 font-bold">EDGE_NODE: CLEVELAND, OH</span>
        </div>

        {/* Knight Avatar Graphic */}
        <div className="relative w-48 h-52 my-1 flex items-center justify-center">
          <svg viewBox="0 0 200 240" className="w-full h-full drop-shadow-[0_0_15px_rgba(229,184,66,0.35)]">
            {/* Glowing Concentric Neon Rings */}
            <circle cx="100" cy="110" r="85" fill="none" stroke="#9D4EDD" strokeWidth="2.5" strokeDasharray="6,4" opacity="0.7" />
            <circle cx="100" cy="110" r="75" fill="none" stroke="#E5B842" strokeWidth="3" opacity="0.9" />

            {/* City Skyline Silhouette Backdrop */}
            <polygon points="40,160 40,110 50,110 50,95 65,95 65,160" fill="#2E1065" opacity="0.6" />
            <polygon points="65,160 65,80 80,65 80,160" fill="#3B1569" opacity="0.8" />
            <polygon points="120,160 120,70 135,50 135,160" fill="#3B1569" opacity="0.8" />
            <polygon points="135,160 135,90 155,90 155,160" fill="#2E1065" opacity="0.6" />

            {/* Golden Cyber Knight Helmet Profile */}
            <path
              d="M 65 60 Q 110 30 145 75 Q 160 110 135 155 L 75 150 Q 55 110 65 60 Z"
              fill="url(#goldGrad)"
              stroke="#FEF08A"
              strokeWidth="2"
            />
            {/* Knight Visor (Radiant Purple Glow) */}
            <path
              d="M 70 85 L 115 80 Q 130 95 105 105 L 75 100 Z"
              fill="#9D4EDD"
              stroke="#00E5FF"
              strokeWidth="1.5"
            />
            {/* Armor Neck Collar */}
            <path
              d="M 65 150 L 155 155 L 170 200 L 50 200 Z"
              fill="url(#goldGrad)"
              stroke="#B45309"
              strokeWidth="1.5"
            />
          </svg>
        </div>

        {/* Crest Footer Title */}
        <div className="text-center mt-2">
          <div className="text-lg font-serif italic font-bold text-amber-300 tracking-wide">
            invisioned <span className="font-sans not-italic font-black text-purple-400 uppercase tracking-widest text-base">MARKETING</span>
          </div>
          <div className="text-[10px] font-mono uppercase tracking-[0.2em] font-semibold text-neutral-300 mt-0.5">
            Agentic Systems Consulting
          </div>
        </div>
      </div>

    </div>
  );
};
