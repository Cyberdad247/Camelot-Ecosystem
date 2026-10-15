// SPDX-License-Identifier: MIT
// Interactive B2B Proposal & ROI Calculator (Bifrost Board Edition)
// Compatible with lucide-react

import React, { useState, MouseEvent } from 'react';
import { Calculator, ShieldCheck, ArrowRight, FileSignature, TrendingUp, Check } from 'lucide-react';

export interface InteractiveB2BProposalProps {
  clientName?: string;
  contractType?: string;
  initialVolume?: number;
}

export function InteractiveB2BProposal({
  clientName = 'Enterprise Partner',
  contractType = 'Deregulated Energy & Marketing Retainer',
  initialVolume = 50000,
}: InteractiveB2BProposalProps) {
  const [volume, setVolume] = useState<number>(initialVolume);
  const [isSigned, setIsSigned] = useState<boolean>(false);
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const [tilt, setTilt] = useState<{ rotateX: number; rotateY: number }>({ rotateX: 0, rotateY: 0 });

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    setTilt({
      rotateX: +(yPct * -14).toFixed(2),
      rotateY: +(xPct * 14).toFixed(2),
    });
  };

  const handleMouseEnter = () => setIsHovered(true);

  const handleMouseLeave = () => {
    setIsHovered(false);
    setTilt({ rotateX: 0, rotateY: 0 });
  };

  const projectedSavings = Math.floor(volume * 0.124);
  const efficiencyGain = ((projectedSavings / volume) * 100).toFixed(1);
  const annualBenefit = projectedSavings * 12;

  return (
    <div className="w-full bg-[#050508] flex items-center justify-center p-4 md:p-8 font-sans selection:bg-camelot-gold selection:text-black">
      <div className="w-full max-w-4xl" style={{ perspective: '1200px' }}>
        <div
          onMouseMove={handleMouseMove}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          style={{
            transform: `rotateX(${tilt.rotateX}deg) rotateY(${tilt.rotateY}deg)`,
            transition: isHovered ? 'transform 0.08s ease-out' : 'transform 0.4s ease-out',
            transformStyle: 'preserve-3d',
          }}
          className="relative bg-[#121217] border-2 border-camelot-gold/40 rounded-2xl p-6 md:p-10 shadow-[0_20px_60px_rgba(0,0,0,0.8),6px_6px_0px_0px_#D4AF37] text-slate-200"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-camelot-gold to-transparent opacity-90" />

          {/* Top Proposal Header */}
          <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-6 mb-8 gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-camelot-gold animate-pulse" />
                <span className="text-[10px] font-mono text-camelot-cyan tracking-[0.25em] uppercase">
                  SOVEREIGN CLIENT HANDOFF // A2UI v10000.56
                </span>
              </div>
              <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase mt-1">
                Executive Proposal: <span className="text-camelot-gold">{clientName}</span>
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Target Vector: <span className="text-slate-200 font-semibold">{contractType}</span>
              </p>
            </div>

            <div className="flex items-center gap-3 font-mono text-xs">
              <span className="px-3 py-1 bg-[#0B0B0E] border border-camelot-gold/40 text-camelot-gold font-bold uppercase tracking-wider rounded">
                D.A.X. TIER 1
              </span>
              <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 font-bold uppercase tracking-wider rounded">
                KYBER-768 SEALED
              </span>
            </div>
          </header>

          {/* Interactive ROI Calculator Section */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center mb-8">
            <div className="md:col-span-7 space-y-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label htmlFor="volume-slider-bifrost" className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Calculator className="w-4 h-4 text-camelot-gold" />
                    Monthly Energy Consumption / Ad Spend
                  </label>
                  <span className="text-lg font-black font-mono text-camelot-gold">
                    ${volume.toLocaleString()}
                  </span>
                </div>

                <input
                  id="volume-slider-bifrost"
                  type="range"
                  min={10000}
                  max={250000}
                  step={5000}
                  value={volume}
                  onChange={(e) => setVolume(Number(e.target.value))}
                  className="w-full h-2 bg-[#0B0B0E] rounded-lg appearance-none cursor-pointer accent-[#D4AF37] border border-slate-700"
                />

                <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                  <span>$10,000 / mo</span>
                  <span>$125,000 / mo</span>
                  <span>$250,000 / mo</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="bg-[#0B0B0E] p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block">Efficiency Yield</span>
                  <span className="text-xl font-black text-emerald-400 font-mono">+{efficiencyGain}%</span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">Automated Arbitrage</span>
                </div>
                <div className="bg-[#0B0B0E] p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] font-mono uppercase text-slate-400 block">Audited Baseline</span>
                  <span className="text-xl font-black text-camelot-cyan font-mono">Z3 VERIFIED</span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">Formal Convexity Pass</span>
                </div>
              </div>
            </div>

            <div className="md:col-span-5 bg-[#0B0B0E] border-2 border-camelot-gold/40 rounded-xl p-6 text-center space-y-4 shadow-[4px_4px_0px_0px_#D4AF37]">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-slate-400">
                  PROJECTED MONTHLY SAVINGS
                </span>
                <div className="text-4xl md:text-5xl font-black font-mono text-camelot-gold tracking-tight mt-1">
                  ${projectedSavings.toLocaleString()}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800">
                <span className="text-[10px] font-mono uppercase text-slate-400">ANNUAL NET BENEFIT</span>
                <div className="text-2xl font-bold font-mono text-white mt-0.5">
                  ${annualBenefit.toLocaleString()}
                </div>
              </div>

              <div className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 py-1.5 px-2 rounded border border-emerald-500/30">
                GUARANTEED DOWNTIME &lt; 0.001%
              </div>
            </div>
          </div>

          {/* Execution & Signature Section */}
          <div className="pt-6 border-t border-[#2A2A35] flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full border border-camelot-gold/40 bg-camelot-gold/10 flex items-center justify-center text-camelot-gold">
                <ShieldCheck className="w-5 h-5 text-camelot-gold" />
              </div>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-white">
                  Sovereign Cryptographic Lock
                </div>
                <div className="text-[10px] font-mono text-slate-400">
                  {isSigned
                    ? 'Receipt minted & anchored into WorldTree Provenance Ledger'
                    : 'Awaiting digital execution signature from client principal'}
                </div>
              </div>
            </div>

            <div>
              {isSigned ? (
                <div className="px-6 py-3 bg-emerald-500/20 border-2 border-emerald-400 text-emerald-300 font-mono font-black text-xs uppercase tracking-widest rounded-lg flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-400" />
                  AGREEMENT EXECUTED &bull; RECEIPT #0xAB8AA359
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setIsSigned(true)}
                  className="px-8 py-3.5 bg-camelot-gold hover:bg-yellow-400 text-black font-mono font-black text-xs uppercase tracking-widest shadow-[4px_4px_0px_0px_#000000] active:translate-y-0.5 transition-all flex items-center gap-2"
                >
                  <FileSignature className="w-4 h-4" />
                  EXECUTE AGREEMENT &rarr;
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InteractiveB2BProposal;
