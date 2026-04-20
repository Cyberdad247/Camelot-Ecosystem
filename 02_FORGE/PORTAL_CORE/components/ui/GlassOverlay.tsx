"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  Cpu, 
  Terminal, 
  Users, 
  Wand2, 
  Menu,
  Activity
} from 'lucide-react';

// --- Sidebar Component ---
function Sidebar({ activeAgent }: { activeAgent: string }) {
  const [expanded, setExpanded] = useState(false);

  const getAgentGlow = (agentName: string) => {
    return activeAgent === agentName ? "text-yellow-400 drop-shadow-[0_0_8px_rgba(250,204,21,0.5)]" : "text-gray-400 hover:text-white";
  };

  return (
    <motion.div 
      className="h-full flex flex-col bg-black/40 backdrop-blur-xl border-r border-white/10 text-white z-50 pointer-events-auto"
      initial={{ width: "4rem" }}
      animate={{ width: expanded ? "16rem" : "4rem" }}
      onHoverStart={() => setExpanded(true)}
      onHoverEnd={() => setExpanded(false)}
    >
      {/* Branding */}
      <div className="p-4 flex items-center justify-center border-b border-white/10">
        <Shield className={`w-8 h-8 ${activeAgent === 'ZENITH' ? 'text-red-500 animate-pulse' : 'text-yellow-500'}`} />
        {expanded && <span className="ml-3 font-bold text-yellow-500 tracking-widest">CAMELOT</span>}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 flex flex-col gap-2">
        <NavItem 
          icon={Users} 
          label="Guild Hall (Anya)" 
          expanded={expanded} 
          active={activeAgent === 'ANYA'}
        />
        <NavItem 
          icon={Terminal} 
          label="Antigravity Console" 
          expanded={expanded} 
          active={activeAgent === 'SYSTEM'}
        />
        <NavItem 
          icon={Wand2} 
          label="Merlin's Forge" 
          expanded={expanded} 
          active={activeAgent === 'MERLIN'}
        />
        <NavItem 
          icon={Cpu} 
          label="System Status" 
          expanded={expanded} 
          active={activeAgent === 'KERNEL'}
        />
      </nav>

      {/* User / Settings */}
      <div className="p-4 border-t border-white/10">
        <NavItem icon={Menu} label="Settings" expanded={expanded} />
      </div>
    </motion.div>
  );
}

function NavItem({ icon: Icon, label, expanded, active = false }: { icon: any, label: string, expanded: boolean, active?: boolean }) {
  return (
    <div className={`
      flex items-center px-4 py-3 cursor-pointer transition-colors relative
      ${active ? "text-yellow-400 bg-white/5 shadow-[inset_4px_0_0_0_#eab308]" : "text-gray-400 hover:text-white hover:bg-white/5"}
    `}>
      <Icon className={`w-6 h-6 min-w-[1.5rem] ${active ? 'animate-pulse' : ''}`} />
      {expanded && (
        <motion.span 
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="ml-3 whitespace-nowrap text-sm font-medium"
        >
          {label}
        </motion.span>
      )}
    </div>
  );
}

// --- Sky Prism (Antigravity Chamber) ---
import { useSocket } from '@/hooks/use-socket';

function SkyPrism({ logs, isConnected }: { logs: string[], isConnected: boolean }) {
  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 w-[600px] pointer-events-none">
      <motion.div 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-lg overflow-hidden shadow-2xl shadow-yellow-500/10 pointer-events-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/5">
          <div className="flex items-center gap-2">
            <Activity className={`w-4 h-4 ${isConnected ? 'text-green-400' : 'text-red-400'}`} />
            <span className={`text-xs font-mono ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
              {isConnected ? 'ANTIGRAVITY_CHAMBER::ONLINE' : 'BRIDGE::OFFLINE'}
            </span>
          </div>
          <div className="flex gap-1">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
            <div className="w-2 h-2 rounded-full bg-green-500/50" />
          </div>
        </div>
        
        {/* Terminal Content - Live Logs */}
        <div className="p-4 font-mono text-xs h-32 overflow-y-auto relative custom-scrollbar">
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent pointer-events-none z-10" />
          <div className="flex flex-col gap-1 text-gray-300 relative z-0">
            {logs.length === 0 && (
              <p className="text-gray-500 italic">:: Awaiting signal from Kernel...</p>
            )}
            {logs.slice(-10).map((log, i) => {
              const isUser = log.includes('[USER]');
              const isThought = log.includes('[THOUGHT]');
              return (
                <p key={i} className={`${isUser ? 'text-cyan-300' : isThought ? 'text-purple-300' : 'text-gray-300'}`}>
                  {log}
                </p>
              );
            })}
            <p className="animate-pulse text-green-400">$ _</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// --- Status HUD ---
function StatusHUD({ activeAgent }: { activeAgent: string }) {
  return (
    <div className="absolute top-4 right-4 flex flex-col gap-2 scale-90 origin-top-right pointer-events-auto">
      <StatusItem label="VRAM" value="5.5/8.0 GB" color="text-yellow-400" />
      <StatusItem label="LATENCY" value="12ms" color="text-green-400" />
      <StatusItem label="KNIGHTS" value="5 ACTIVE" color="text-blue-400" />
      
      {/* Agent Status */}
      <div className="flex items-center justify-between bg-white/10 backdrop-blur-md px-3 py-1 rounded border border-white/20 w-40 mt-2">
        <span className="text-[10px] text-gray-400 font-bold">SPEAKER</span>
        <span className="text-xs font-mono text-purple-300 animate-pulse">{activeAgent}</span>
      </div>
    </div>
  );
}

function StatusItem({ label, value, color }: { label: string, value: string, color: string }) {
  return (
    <div className="flex items-center justify-between bg-black/40 backdrop-blur-md px-3 py-1 rounded border border-white/5 w-40">
      <span className="text-[10px] text-gray-500 font-bold">{label}</span>
      <span className={`text-xs font-mono ${color}`}>{value}</span>
    </div>
  );
}

export function GlassOverlay() {
  const { logs, isConnected } = useSocket();
  const [activeAgent, setActiveAgent] = useState("SYSTEM");

  // Determine Active Agent from latest logs
  React.useEffect(() => {
    if (logs.length > 0) {
      const lastLog = logs[logs.length - 1];
      if (lastLog.includes('MERLIN')) setActiveAgent("MERLIN");
      else if (lastLog.includes('DAME_ANYA') || lastLog.includes('ANYA')) setActiveAgent("ANYA");
      else if (lastLog.includes('SIR_ZENITH') || lastLog.includes('ZENITH')) setActiveAgent("ZENITH");
      else if (lastLog.includes('KERNEL')) setActiveAgent("KERNEL");
      else if (lastLog.includes('USER')) setActiveAgent("USER");
      // Don't reset to SYSTEM immediately to keep the 'thought' state visible for a moment
    }
  }, [logs]);

  return (
    <div className="w-full h-full relative flex">
      <Sidebar activeAgent={activeAgent} />
      <SkyPrism logs={logs} isConnected={isConnected} />
      <StatusHUD activeAgent={activeAgent} />
    </div>
  );
}
