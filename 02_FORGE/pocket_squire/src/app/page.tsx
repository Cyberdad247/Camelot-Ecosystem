"use client";

import React, { useState, useEffect } from "react";
import {
  Shield,
  Zap,
  Activity,
  Terminal,
  Cpu,
  Menu,
  Bell,
  Search,
  Sword,
  Hammer,
  Radio,
} from "lucide-react";

export default function PocketSquire() {
  const [osStatus, setOsStatus] = useState("RADIANT");
  const [activeKnights, setActiveKnights] = useState(4);
  const [recentActions, setRecentActions] = useState<any[]>([]);
  const [loadIndex, setLoadIndex] = useState("12.4%");

  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = "localhost:8001"; // Target Kernel
    const ws = new WebSocket(`${protocol}//${host}/ws?token=merlin-v100-dev`);

    ws.onopen = () => {
      console.log("📡 [SQUIRE] Linked to Sovereign Kernel.");
      setOsStatus("RADIANT");
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === "LEDGER_UPDATE") {
          const parts = msg.data.split("|");
          if (parts.length >= 4) {
            const newAction = {
              id: Math.random(),
              action: parts[3].trim(),
              time: "Just now",
              status: parts[4].trim(),
              icon: <Zap size={14} className="text-yellow-400" />,
            };
            setRecentActions((prev) => [newAction, ...prev].slice(0, 8));
          }
        }

        if (msg.type === "METRICS_UPDATE") {
          const cpu = parseFloat(msg.data.cpu).toFixed(1);
          setLoadIndex(`${cpu}%`);
          if (msg.data.knights) setActiveKnights(msg.data.knights);
        }
      } catch (e) {
        console.error("WS Parse Error", e);
      }
    };

    ws.onclose = () => {
      setOsStatus("OFFLINE");
      console.log("📡 [SQUIRE] Link Severed.");
    };

    const ticker = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 2000);

    return () => {
      ws.close();
      clearInterval(ticker);
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#050505] text-white p-4 font-sans select-none">
      {/* Mobile Header */}
      <header className="flex justify-between items-center mb-8 pt-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#7D52FF] rounded-lg flex items-center justify-center">
            <Sword size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tighter uppercase">
              Pocket Squire
            </h1>
            <p className="text-[10px] text-zinc-500 font-mono tracking-widest">
              v101.0_MOBILE
            </p>
          </div>
        </div>
        <div className="flex gap-4">
          <Bell size={20} className="text-zinc-400" />
          <Menu size={20} className="text-zinc-400" />
        </div>
      </header>

      {/* OS Status Card */}
      <div className="bg-[#111] rounded-2xl p-5 border border-[#1a1a1a] mb-6 relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-active:opacity-30 transition-opacity">
          <Shield size={80} />
        </div>
        <div className="flex justify-between items-end">
          <div>
            <p className="text-[10px] text-zinc-500 font-mono uppercase mb-1">
              System Pulse
            </p>
            <h2
              className={`text-3xl font-black tracking-tighter ${osStatus === "RADIANT" ? "text-[#04B575]" : "text-yellow-500"}`}
            >
              {osStatus}
            </h2>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-zinc-500 font-mono uppercase mb-1">
              Load Index
            </p>
            <p className="text-xl font-bold text-zinc-300">{loadIndex}</p>
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <div className="h-1 bg-[#04B575] rounded-full flex-1" />
          <div
            className="h-1 bg-zinc-800 rounded-full flex-2"
            style={{ flex: 2 }}
          />
        </div>
      </div>

      {/* Grid Menu */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <QuickAction
          title="FORGE"
          icon={<Hammer className="text-[#7D52FF]" />}
          subtitle="Develop"
        />
        <QuickAction
          title="FLEET"
          icon={<Radio className="text-[#04B575]" />}
          subtitle="Monitor"
        />
        <QuickAction
          title="AUDIT"
          icon={<Shield className="text-[#FF0055]" />}
          subtitle="Secure"
        />
        <QuickAction
          title="BRAIN"
          icon={<Cpu className="text-zinc-300" />}
          subtitle="Research"
        />
      </div>

      {/* Activity Stream */}
      <div className="mb-4 flex justify-between items-center px-1">
        <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">
          A2A_STREAM
        </h3>
        <Activity size={14} className="text-[#7D52FF] animate-pulse" />
      </div>

      <div className="space-y-3">
        {recentActions.map((item) => (
          <div
            key={item.id}
            className="bg-[#111] flex items-center justify-between p-4 rounded-xl border border-[#1a1a1a]"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400">
                {item.icon}
              </div>
              <div>
                <p className="text-sm font-medium">{item.action}</p>
                <p className="text-[10px] text-zinc-500">{item.time}</p>
              </div>
            </div>
            <div
              className={`text-[10px] font-mono px-2 py-0.5 rounded border ${item.status === "FAILURE" ? "text-red-500 bg-red-500/10 border-red-500/20" : "text-[#04B575] bg-[#04B575]/10 border-[#04B575]/20"}`}
            >
              {item.status || "SUCCESS"}
            </div>
          </div>
        ))}
      </div>

      {/* Bottom Nav Simulation */}
      <div className="fixed bottom-0 left-0 right-0 p-6 pointer-events-none">
        <div className="bg-[#1a1a1a]/80 backdrop-blur-xl border border-white/5 rounded-full p-2 flex justify-around items-center max-w-sm mx-auto pointer-events-auto shadow-2xl">
          <NavButton icon={<Terminal size={20} />} active />
          <NavButton icon={<Zap size={20} />} />
          <NavButton icon={<Search size={20} />} />
          <NavButton icon={<Cpu size={20} />} />
        </div>
      </div>
    </div>
  );
}

function QuickAction({ title, icon, subtitle }) {
  return (
    <button className="bg-[#111] border border-[#1a1a1a] p-4 rounded-3xl flex flex-col items-start gap-4 active:scale-95 transition-all text-left group">
      <div className="w-10 h-10 bg-zinc-900 rounded-2xl flex items-center justify-center border border-zinc-800 group-active:border-[#7D52FF]/50 transition-colors">
        {icon}
      </div>
      <div>
        <p className="text-sm font-bold tracking-tight">{title}</p>
        <p className="text-[10px] text-zinc-500 font-mono uppercase">
          {subtitle}
        </p>
      </div>
    </button>
  );
}

function NavButton({ icon, active = false }) {
  return (
    <button
      className={`p-3 rounded-full transition-all ${active ? "bg-[#7D52FF] text-white" : "text-zinc-500 hover:text-zinc-300"}`}
    >
      {icon}
    </button>
  );
}
