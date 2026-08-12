'use client';

import React, { useRef, useEffect, useState } from 'react';
import { motion, useMotionTemplate, useMotionValue, useSpring } from 'framer-motion';
import Image from 'next/image';
import { useBifrost } from '../src/hooks/useBifrost';
import { useLedgerStore } from '../src/store/ledgerStore';
import { CartridgeSlot } from '../src/components/CartridgeSlot';
import { HighContrastButton } from '../src/components/HighContrastButton';
import { ExecutiveMetricsPanel } from '../src/components/ExecutiveMetricsPanel';
import { LakeshaVoiceEnclave } from '../src/components/LakeshaVoiceEnclave';
import { OpenDesignStatusPills } from '../src/components/OpenDesignStatusPills';

// --- 3D Hover Physics Wrapper (Design Judge Heuristics) ---
const TiltCard = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const mouseXSpring = useSpring(x, { stiffness: 300, damping: 30 });
  const mouseYSpring = useSpring(y, { stiffness: 300, damping: 30 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = (mouseX / width - 0.5) * 2;
    const yPct = (mouseY / height - 0.5) * 2;
    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX: useMotionTemplate`${mouseYSpring} * -12deg`,
        rotateY: useMotionTemplate`${mouseXSpring} * 12deg`,
        transformStyle: 'preserve-3d',
      }}
      className={`relative border-2 border-[#D4AF37]/30 bg-gradient-to-br from-[#121218]/95 to-[#0B0B0E]/95 backdrop-blur-2xl shadow-2xl transition-colors duration-500 hover:border-[#D4AF37]/80 group ${className}`}
    >
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      <div style={{ transform: 'translateZ(40px)' }} className="h-full w-full p-6 relative z-10">
        {children}
      </div>
    </motion.div>
  );
};

// --- Animated Audio Equalizer ---
const AudioVisualizer = () => {
  return (
    <div className="flex items-end justify-center space-x-1 h-6">
      {[1, 2, 3, 4, 5].map((i) => (
        <motion.div
          key={i}
          animate={{ height: ['20%', '100%', '30%', '80%', '20%'] }}
          transition={{
            duration: 1.4,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.1,
          }}
          className="w-1 bg-[#9D4EDD] shadow-[0_0_8px_#9D4EDD]"
        />
      ))}
    </div>
  );
};

export default function KBASovereignInterphase() {
  const { connectionStatus, sendIntent } = useBifrost();
  const { pendingTransactions, addTransaction, offlineItemCount } = useLedgerStore();

  const [chloeStatus, setChloeStatus] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [telemetry, setTelemetry] = useState<string[]>([
    "[100.71.218.75] BIFROST_MESH_ACTIVE",
    "[Z3_ENGINE] STATE_MACHINE_CONVEX",
    "AWAITING_SOVEREIGN_INTENT..."
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const logs = [
        "[BULLMQ] Job queue:chloe_billing processed.",
        "[WEBRTC] VAD threshold nominal.",
        "[WASM_LEDGER] CRDT checksum verified.",
        "[TAILSCALE] Peer discovery heartbeat OK."
      ];
      setTelemetry((prev) => [...prev.slice(-4), logs[Math.floor(Math.random() * logs.length)]]);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = () => {
    setChloeStatus('APPROVED');
    addTransaction({
      tenant_id: 'KBA-TENANT-001',
      description: 'Chloe (Billing) - $150.00 Refund Approved',
      entries: [
        { account_id: 'ACC_REVENUE_CHLOE', entry_type: 'Debit', amount_cents: 15000 },
        { account_id: 'ACC_CUSTOMER_REFUND', entry_type: 'Credit', amount_cents: 15000 },
      ],
    });

    sendIntent({
      action: 'APPROVE_KBA_REFUND',
      tenant_id: 'KBA-TENANT-001',
      data: { client: 'Chloe', amount: 150.0, status: 'APPROVED' },
      timestamp: Date.now(),
    });

    setActionLog((prev) => [`[APPROVAL_EXECUTED] Chloe $150.00 Refund -> Bifrost Mesh Queue`, ...prev]);
  };

  const handleReject = () => {
    setChloeStatus('REJECTED');
    sendIntent({
      action: 'REJECT_KBA_REFUND',
      tenant_id: 'KBA-TENANT-001',
      data: { client: 'Chloe', amount: 150.0, status: 'REJECTED' },
      timestamp: Date.now(),
    });

    setActionLog((prev) => [`[REJECTION_EXECUTED] Chloe $150.00 Refund -> Decision Logged`, ...prev]);
  };

  return (
    <div className="min-h-screen bg-[#050507] text-[#D4AF37] p-2 md:p-6 font-sans overflow-x-hidden selection:bg-[#9D4EDD] selection:text-white">
      
      {/* HEADER WITH FLUID CLAMP TYPOGRAPHY */}
      <header className="relative z-10 mb-8 flex flex-col md:flex-row justify-between items-start md:items-end border-b-2 border-[#D4AF37]/30 pb-6 gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-2 font-mono">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full bg-[#9D4EDD] opacity-75"></span>
              <span className="relative inline-flex h-3 w-3 bg-[#9D4EDD]"></span>
            </span>
            <p className="text-xs uppercase tracking-[0.4em] text-[#9D4EDD] font-extrabold">
              TAILSCALE NODE: 100.71.218.75
            </p>
            <span className="text-[10px] px-2.5 py-0.5 border border-[#D4AF37]/40 text-[#D4AF37] font-bold uppercase bg-[#0B0B0E]">
              STATUS: {connectionStatus}
            </span>
          </div>
          <h1
            className="font-extrabold uppercase tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-[#D4AF37] via-[#FFF8D6] to-[#D4AF37]" 
            style={{ fontSize: 'var(--font-fluid-h1)' }}
          >
            Sovereign Executive Intelligence
          </h1>
        </div>
        <div className="text-left md:text-right mt-2 md:mt-0 font-mono">
          <p className="text-xs tracking-[0.3em] text-[#FFF8D6] font-extrabold border-2 border-[#D4AF37]/40 px-4 py-2 bg-[#0B0B0E] shadow-[4px_4px_0px_0px_#9D4EDD]">
            DREAMS DON'T COME TRUE VISIONS DO
          </p>
        </div>
      </header>

      {/* OPEN DESIGN STATUS PILL BAR */}
      <section className="relative z-10 mb-6">
        <OpenDesignStatusPills />
      </section>

      {/* SYSTEMATIC EXECUTIVE METRICS PANEL */}
      <section className="relative z-10 mb-8">
        <ExecutiveMetricsPanel />
      </section>

      {/* LAKESHA VOICE ENCLAVE SECTION */}
      <section className="relative z-10 mb-8">
        <LakeshaVoiceEnclave />
      </section>

      {/* ASYMMETRICAL BENTO GRID ARCHITECTURE */}
      <main className="relative z-10 grid grid-cols-1 md:grid-cols-12 gap-6 auto-rows-min mb-8">
        
        {/* Module 1: Property & Total Portfolio Valuation (Spans 8 cols) */}
        <TiltCard className="md:col-span-8 row-span-2 overflow-hidden">
          <div className="flex flex-col justify-between h-full relative z-10">
            <p className="text-xs uppercase tracking-widest text-slate-400 font-bold font-mono">
              PROPERTY & TOTAL PORTFOLIO VALUATION
            </p>
            <div className="mt-4 z-20">
              <h2 className="font-serif italic drop-shadow-[0_0_20px_rgba(212,175,55,0.4)] text-[#FFF8D6]" style={{ fontSize: 'clamp(3.5rem, 8vw, 6.5rem)' }}>
                $14.2M
              </h2>
              <p className="font-mono text-sm text-[#D4AF37]/80 mt-1 tracking-widest">$14,200,000.00 USD</p>
            </div>
            <div className="mt-8 flex items-center space-x-4 font-mono">
              <div className="inline-flex items-center px-4 py-2 bg-[#9D4EDD]/20 border-2 border-[#9D4EDD] shadow-[3px_3px_0px_0px_#D4AF37]">
                <span className="text-[#FFF8D6] text-xs font-black tracking-widest">QTD +12.4%</span>
              </div>
              <p className="text-[10px] uppercase text-slate-400 tracking-widest">
                WASM Ledger Synced ({offlineItemCount} Items Pending)
              </p>
            </div>
          </div>
          
          {/* Abstract SVG Sparkline Graphic */}
          <div className="absolute bottom-0 right-0 w-3/4 h-3/4 opacity-25 pointer-events-none">
            <svg viewBox="0 0 100 50" preserveAspectRatio="none" className="w-full h-full">
              <path d="M0,50 Q20,40 40,20 T70,30 T100,5" fill="none" stroke="#D4AF37" strokeWidth="2" vectorEffect="non-scaling-stroke" className="drop-shadow-[0_0_8px_#D4AF37]"/>
              <path d="M0,50 Q20,40 40,20 T70,30 T100,5 L100,50 L0,50 Z" fill="url(#goldGradient)" opacity="0.35"/>
              <defs>
                <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#D4AF37" />
                  <stop offset="100%" stopColor="#0B0B0E" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </TiltCard>

        {/* Module 2: LaKesha 3D Spatial Viewport (Spans 4 cols) */}
        <TiltCard className="md:col-span-4 row-span-3 p-0 relative overflow-hidden group border-2 border-[#D4AF37]">
          <div className="absolute inset-0 w-full h-full bg-[#0B0B0E] min-h-[360px]">
            {/* CRT Scanline Shader */}
            <div className="absolute inset-0 z-20 pointer-events-none crt-scanlines" />
            <div className="absolute inset-0 bg-gradient-to-t from-[#0B0B0E] via-[#0B0B0E]/40 to-transparent z-10" />
            <Image 
              src="/assets/LaKesha.png" 
              alt="LaKesha" 
              fill
              sizes="(max-width: 768px) 100vw, 33vw"
              priority
              className="object-cover object-top opacity-75 group-hover:opacity-100 transition-all duration-700 scale-105 group-hover:scale-100 filter contrast-125"
            />
          </div>

          <div className="absolute bottom-6 left-6 z-30 w-full pr-12">
            <div className="flex justify-between items-end">
              <div>
                <h3 className="text-3xl font-serif italic text-white drop-shadow-2xl">LaKesha</h3>
                <p className="text-[9px] uppercase tracking-[0.2em] font-extrabold font-mono mt-1 text-[#D4AF37]">
                  Executive Voice Hypervisor
                </p>
              </div>
              <div className="pr-6 pb-1">
                <AudioVisualizer />
              </div>
            </div>
            <div className="h-[2px] w-4/5 bg-gradient-to-r from-[#D4AF37] via-[#9D4EDD] to-transparent my-3" />
            <div className="font-mono text-[9px] text-[#9D4EDD] font-bold uppercase tracking-widest">
              [VAD: Active] [WebRTC: Bound]
            </div>
          </div>
        </TiltCard>

        {/* Module 3: Tailscale Telemetry Log Feed (Spans 4 cols) */}
        <TiltCard className="md:col-span-4 row-span-1 bg-[#050507]">
          <p className="text-[10px] uppercase tracking-widest text-[#D4AF37] mb-3 border-b border-[#D4AF37]/20 pb-2 font-mono font-bold">
            Tailscale Mesh Telemetry Feed
          </p>
          <div className="font-mono text-[9px] text-emerald-400 space-y-1 h-16 flex flex-col justify-end">
            {telemetry.map((log, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, x: -10 }} 
                animate={{ opacity: 1, x: 0 }}
                className="truncate"
              >
                &gt; {log}
              </motion.div>
            ))}
          </div>
        </TiltCard>

        {/* Module 4: Active Streaming Nodes (Spans 4 cols) */}
        <TiltCard className="md:col-span-4 row-span-1">
          <div className="flex justify-between items-start font-mono">
            <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-bold">Active Streaming Nodes</p>
            <span className="flex h-2.5 w-2.5 bg-emerald-500 shadow-[0_0_10px_#10b981]"></span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3 font-mono">
            <p className="text-4xl font-mono tracking-tighter text-slate-100 font-bold">2<span className="text-slate-600">/3</span></p>
            <span className="text-[10px] text-[#D4AF37] uppercase tracking-wider border border-[#D4AF37]/30 px-2 py-0.5 bg-slate-900 font-bold">
              +1 Standby
            </span>
          </div>
        </TiltCard>

        {/* Module 5: Retail & Venture Stakes (Spans 8 cols) */}
        <TiltCard className="md:col-span-8 row-span-1 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400 font-mono font-bold">
              RETAIL & VENTURE STAKES
            </p>
            <p className="text-3xl font-mono text-[#FFF8D6] font-bold mt-1">$3.8M</p>
          </div>
          <div className="text-right font-mono">
            <span className="px-4 py-2 bg-[#D4AF37]/10 border-2 border-[#D4AF37] text-[#D4AF37] text-xs font-black uppercase tracking-widest shadow-[3px_3px_0px_0px_#9D4EDD]">
              +2 Rounds Seed
            </span>
          </div>
        </TiltCard>

        {/* Module 6: HITL Approval Gate (Spans 12 cols) */}
        <TiltCard className="md:col-span-12 border-[#9D4EDD]">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div>
              <div className="text-[10px] text-[#9D4EDD] font-bold font-mono tracking-widest uppercase">
                HUMAN-IN-THE-LOOP (HITL) GATEWAY // TENANT 001
              </div>
              <h3 className="text-xl font-serif italic text-slate-100 mt-1">
                Chloe (Billing) — Refund Pending ($150.00 USD)
              </h3>
              <p className="text-xs text-slate-400 font-mono mt-1">
                STATE: <span className="text-[#D4AF37] font-bold">{chloeStatus}</span> | CRDT Invariant: Debits ($150.00) == Credits ($150.00)
              </p>
            </div>

            <div className="flex gap-4 w-full lg:w-auto">
              <HighContrastButton
                variant="danger"
                onClick={handleReject}
                disabled={chloeStatus !== 'PENDING'}
              >
                ✗ REJECT INTENT
              </HighContrastButton>

              <HighContrastButton
                variant="purple"
                onClick={handleApprove}
                disabled={chloeStatus !== 'PENDING'}
              >
                ✓ APPROVE $150.00
              </HighContrastButton>
            </div>
          </div>
        </TiltCard>

      </main>

      {/* CARTRIDGE SLOT SYSTEM (SaaS Workflow Pills) */}
      <section className="relative z-10 mb-8">
        <CartridgeSlot />
      </section>

      {/* KINETIC ACTION AUDIT LOG */}
      {actionLog.length > 0 && (
        <footer className="relative z-10 border-2 border-slate-800 bg-slate-950 p-4 font-mono space-y-2">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
            KINETIC ACTION AUDIT LOG:
          </div>
          <div className="space-y-1 text-xs text-emerald-400">
            {actionLog.map((log, index) => (
              <div key={index} className="flex gap-2">
                <span className="text-slate-600">&gt;</span>
                <span>{log}</span>
              </div>
            ))}
          </div>
        </footer>
      )}

    </div>
  );
}
