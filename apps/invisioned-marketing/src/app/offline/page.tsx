// SPDX-License-Identifier: MIT
import React from 'react';
import Link from 'next/link';

export default function InvisionedOfflinePage() {
  return (
    <main className="min-h-screen bg-[#0B0B0E] text-slate-100 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-md w-full border border-[#D4AF37]/40 bg-[#121217] p-8 rounded-xl shadow-[8px_8px_0px_0px_#D4AF37] text-center space-y-6">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full border border-[#D4AF37] bg-[#0B0B0E] text-[#D4AF37] text-2xl font-bold font-mono">
          IM
        </div>

        <div>
          <span className="text-[10px] uppercase font-bold tracking-widest text-[#D4AF37] font-mono">
            INVISIONED MARKETING // OFFLINE CACHE
          </span>
          <h1 className="text-xl font-black text-white mt-2 uppercase tracking-wide">
            Autonomous Engine Cached
          </h1>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            Internet connection temporarily unavailable. Your client oracle sessions, proposal calculations, and digital agency assets remain available in offline storage.
          </p>
        </div>

        <div className="p-4 bg-[#0B0B0E] border border-[#2A2A35] rounded-lg text-left text-[11px] space-y-1.5 font-mono text-slate-300">
          <div className="flex justify-between">
            <span className="text-slate-500">Service Worker:</span>
            <span className="text-emerald-400 font-bold">ONLINE (v1)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Proposal Simulator:</span>
            <span className="text-emerald-400 font-bold">CACHED</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Oracle Voice Models:</span>
            <span className="text-[#D4AF37] font-bold">LIVING_BUFFER</span>
          </div>
        </div>

        <div className="pt-2 flex flex-col gap-2">
          <Link
            href="/"
            className="w-full py-2.5 bg-[#D4AF37] hover:bg-[#F3E5AB] text-black font-black text-xs uppercase tracking-wider rounded transition-all shadow-[2px_2px_0px_0px_#000]"
          >
            Return to Portal &rarr;
          </Link>
          <button
            onClick={() => window.location.reload()}
            className="w-full py-2 bg-[#0B0B0E] hover:bg-[#1A1A22] text-slate-400 hover:text-white border border-[#2A2A35] text-xs font-mono rounded transition-all"
          >
            Refresh Local Session
          </button>
        </div>
      </div>
    </main>
  );
}
