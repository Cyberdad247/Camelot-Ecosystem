"use client";

import { useEffect, useState } from "react";
import { Copy, Terminal, Activity, Mic, Shield } from "lucide-react";
import { checkKernelHealth, dispatchCommand } from "../src/lib/kernel-bridge";

export default function PocketSquireDeck() {
  const [online, setOnline] = useState(false);
  const [status, setStatus] = useState("IDLE");
  const [lastLog, setLastLog] = useState("Waiting for Neural Link...");

  // Health Check Poll
  useEffect(() => {
    const interval = setInterval(async () => {
      const isHealthy = await checkKernelHealth();
      setOnline(isHealthy);
      setStatus(isHealthy ? "CONNECTED" : "OFFLINE");
    }, 5000);
    checkKernelHealth().then(setOnline);
    return () => clearInterval(interval);
  }, []);

  const handleCommand = async (cmd: string) => {
    setLastLog(`> ${cmd}...`);
    const res = await dispatchCommand(cmd);
    if (res.status === "SUCCESS") {
      setLastLog(`[OK] ${res.msg}`);
    } else {
      setLastLog(`[ERR] ${res.msg}`);
    }
  };

  return (
    <main className="flex min-h-screen flex-col bg-[var(--color-void)] text-[var(--color-foreground)] p-4 font-mono">
      {/* HEADER */}
      <header className="flex justify-between items-center border-b border-[var(--color-royal)] pb-4 mb-6">
        <div>
          <h1 className="text-xl font-bold text-[var(--color-gold)] tracking-widest">
            POCKET SQUIRE
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <div
              className={`w-2 h-2 rounded-full ${online ? "bg-green-500 animate-pulse" : "bg-red-500"}`}
            ></div>
            <span className="text-xs text-gray-500">{status}</span>
          </div>
        </div>
        <Shield className="text-[var(--color-royal)]" />
      </header>

      {/* SYSTEM MONITOR (Mock) */}
      <section className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-[#111] border border-[#333] p-4 rounded-md">
          <span className="text-xs text-[#888] uppercase">Host CPU</span>
          <div className="text-2xl font-bold text-[var(--color-royal)] mt-1">
            12%
          </div>
        </div>
        <div className="bg-[#111] border border-[#333] p-4 rounded-md">
          <span className="text-xs text-[#888] uppercase">Host RAM</span>
          <div className="text-2xl font-bold text-[var(--color-gold)] mt-1">
            7.2GB
          </div>
        </div>
      </section>

      {/* TERMINAL STREAM */}
      <section className="flex-1 bg-[#0a0a0a] border border-[#333] rounded-md p-4 mb-6 overflow-hidden relative">
        <div className="absolute top-2 right-2 opacity-50">
          <Terminal size={16} />
        </div>
        <div className="font-mono text-xs text-green-400 h-full overflow-y-auto">
          {lastLog}
          <span className="animate-pulse">_</span>
        </div>
      </section>

      {/* TACTICAL GRID */}
      <section className="grid grid-cols-2 gap-3 mb-20">
        <button
          onClick={() => handleCommand("Deploy Nano-Swarm")}
          className="p-4 bg-[#111] border border-[var(--color-royal)] rounded flex flex-col items-center gap-2 active:bg-[var(--color-royal)] active:text-white transition-colors"
        >
          <Activity />
          <span className="text-xs font-bold">DEPLOY SWARM</span>
        </button>
        <button
          onClick={() => handleCommand("Audit Codebase")}
          className="p-4 bg-[#111] border border-[#333] rounded flex flex-col items-center gap-2 active:bg-[#333] transition-colors"
        >
          <Copy />
          <span className="text-xs font-bold">AUDIT CODE</span>
        </button>
      </section>

      {/* FAB (Voice) */}
      <button
        aria-label="Activate Voice Command"
        className="fixed bottom-6 right-6 w-16 h-16 bg-[var(--color-royal)] rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(157,0,255,0.5)] active:scale-95 transition-transform"
      >
        <Mic className="text-white w-8 h-8" />
      </button>
    </main>
  );
}
