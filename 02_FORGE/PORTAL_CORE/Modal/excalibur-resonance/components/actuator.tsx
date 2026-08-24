"use client";

import { useState } from "react";
import { Zap } from "lucide-react";

export function Actuator() {
  const [command, setCommand] = useState("");

  return (
    <div className="rounded-2xl border border-zinc-800 bg-white/5 p-4 backdrop-blur flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Zap className="h-5 w-5 text-yellow-400" />
        <h2 className="text-lg font-semibold text-white">Actuator</h2>
      </div>
      <label className="text-xs uppercase tracking-[0.2em] text-slate-400">
        Command
      </label>
      <input
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        placeholder="Deploy bridge, compile assets..."
        className="w-full rounded-lg border border-zinc-800 bg-black/50 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/40"
      />
      <button
        type="button"
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-yellow-500 px-4 py-2 text-sm font-semibold text-black shadow-lg shadow-purple-500/30"
      >
        Fire Command
      </button>
    </div>
  );
}
