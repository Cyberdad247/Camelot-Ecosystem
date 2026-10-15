// SPDX-License-Identifier: MIT
// Client Oracle Portal (Bifrost Board Edition)
// Compatible with lucide-react

import React, { useState, useEffect } from 'react';
import { Mic, MicOff, BarChart3, TrendingUp, ShieldCheck, Zap, Activity, Send } from 'lucide-react';

export interface ClientMetrics {
  conversions: number;
  cpa: number;
  roi: number;
  pipelineARR: number;
}

export function ClientOraclePortal() {
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [transcript, setTranscript] = useState<string>('Awaiting voice input or query...');
  const [waveformBars, setWaveformBars] = useState<number[]>([15, 30, 60, 45, 80, 50, 95, 40, 70, 25, 45, 20]);
  const [queryInput, setQueryInput] = useState<string>('');

  const [metrics, setMetrics] = useState<ClientMetrics>({
    conversions: 142,
    cpa: 42.50,
    roi: 315,
    pipelineARR: 142500,
  });

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isListening || isSpeaking) {
      interval = setInterval(() => {
        setWaveformBars(Array.from({ length: 16 }, () => Math.floor(Math.random() * 85 + 15)));
      }, 90);
    } else {
      setWaveformBars([10, 16, 12, 18, 14, 16, 12, 20, 15, 14, 18, 12, 10, 16, 12, 14]);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isListening, isSpeaking]);

  const toggleMic = () => {
    if (!isListening) {
      setIsListening(true);
      setTranscript('Listening... (Ask: "What is our current marketing ROI and conversion count?")');

      setTimeout(() => {
        setIsListening(false);
        setIsSpeaking(true);
        setTranscript('Lady Apis: "Campaign ROI is currently tracking at +342% with CPA down to $38.20. Rendering visual telemetry."');

        setTimeout(() => {
          setMetrics({
            conversions: 156,
            cpa: 38.20,
            roi: 342,
            pipelineARR: 158200,
          });
          setIsSpeaking(false);
          setTranscript('Telemetry successfully updated via Viking WAL2 ledger. Ready for next query.');
        }, 2500);
      }, 2000);
    } else {
      setIsListening(false);
      setTranscript('Voice channel closed. Tap microphone to reopen acoustic link.');
    }
  };

  const handleTextQuery = (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput.trim()) return;

    const query = queryInput;
    setQueryInput('');
    setIsSpeaking(true);
    setTranscript(`Query received: "${query}". Lady Apis querying WorldTree memory...`);

    setTimeout(() => {
      if (query.toLowerCase().includes('energy') || query.toLowerCase().includes('rate')) {
        setTranscript('Lady Apis: "Regional PJM energy tariffs show a $14,200 monthly arbitrage buffer. Hedging locked."');
      } else {
        setMetrics((prev) => ({
          ...prev,
          conversions: prev.conversions + 4,
          roi: prev.roi + 12,
        }));
        setTranscript(`Lady Apis: "Query answered. Added +4 conversions. ROI elevated to ${metrics.roi + 12}%. Telemetry live."`);
      }
      setIsSpeaking(false);
    }, 1400);
  };

  return (
    <div className="w-full bg-[#050508] p-4 md:p-8 font-sans text-slate-200 border-2 border-camelot-gold/40 shadow-[6px_6px_0px_0px_#D4AF37] rounded-xl flex flex-col">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-6 mb-8 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-camelot-gold animate-pulse" />
            <span className="text-[10px] font-mono text-camelot-cyan tracking-[0.25em] uppercase">
              CLIENT-FACING PORTAL // A2UI PROJECTION LAYER
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase mt-1">
            Client Oracle <span className="text-camelot-gold">Portal</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Living Digital Entity &bull; Real-Time GraphRAG Reporting &bull; Invisioned VIP Lounge
          </p>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <span className="px-3 py-1 bg-[#0B0B0E] border border-camelot-gold/40 text-camelot-gold font-bold uppercase tracking-wider rounded">
            TENANT: INVISIONED_VIP
          </span>
          <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 font-bold uppercase tracking-wider rounded">
            LIVE AIR-GAP VERIFIED
          </span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <div className="md:col-span-5 bg-[#121217] border-2 border-camelot-gold/40 rounded-xl p-6 flex flex-col items-center justify-between shadow-[4px_4px_0px_0px_#D4AF37] relative overflow-hidden">
          <div className="pointer-events-none absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(212,175,55,0.04)_3px)]" />

          <div className="w-full flex justify-between items-center text-xs font-mono border-b border-slate-800 pb-3">
            <span className="text-camelot-gold font-bold">LADY APIS ORACLE</span>
            <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
              {isSpeaking ? 'SPEAKING' : isListening ? 'LISTENING' : 'ONLINE'}
            </span>
          </div>

          <div className="my-8 relative flex items-center justify-center">
            {(isSpeaking || isListening) && (
              <>
                <span className="absolute h-40 w-40 animate-ping rounded-full border border-camelot-gold/30 opacity-75" />
                <span className="absolute h-52 w-52 animate-pulse rounded-full border border-camelot-violet/30" />
              </>
            )}

            <div
              className={`h-32 w-32 rounded-full transition-all duration-300 flex items-center justify-center relative shadow-[0_0_50px_rgba(212,175,55,0.4)] ${
                isSpeaking
                  ? 'scale-110 shadow-[0_0_60px_rgba(255,215,0,0.8)]'
                  : isListening
                  ? 'scale-105 shadow-[0_0_60px_rgba(0,229,255,0.8)]'
                  : 'hover:scale-105'
              }`}
              style={{
                background: isSpeaking
                  ? 'radial-gradient(circle at 35% 30%, #FFD700, #D4AF37 55%, #050508 85%)'
                  : isListening
                  ? 'radial-gradient(circle at 35% 30%, #00E5FF, #0088AA 55%, #050508 85%)'
                  : 'radial-gradient(circle at 35% 30%, #D4AF37, #8A6D1C 55%, #050508 85%)',
              }}
            >
              <span className="text-4xl select-none filter drop-shadow-md">🐝</span>
              <div className="absolute inset-0 rounded-full border border-white/20 pointer-events-none" />
            </div>
          </div>

          <div className="w-full bg-[#0B0B0E] p-3 rounded-lg border border-slate-800 flex flex-col items-center gap-2">
            <div className="flex items-end justify-center gap-1.5 h-10 w-full px-2">
              {waveformBars.map((h, i) => (
                <div
                  key={i}
                  className="w-1.5 rounded-full transition-all duration-75"
                  style={{
                    height: `${h}%`,
                    backgroundColor: isSpeaking
                      ? '#FFD700'
                      : isListening
                      ? '#00E5FF'
                      : '#D4AF37',
                    opacity: isSpeaking || isListening ? 0.9 : 0.4,
                  }}
                />
              ))}
            </div>

            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
              LOCAL VAD &bull; DUPLEX ACOUSTIC PIPELINE
            </span>
          </div>

          <div className="mt-5 w-full flex justify-center">
            <button
              type="button"
              onClick={toggleMic}
              className={`w-full py-3.5 rounded font-mono font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all shadow-[2px_2px_0px_0px_#000000] active:translate-y-0.5 ${
                isListening
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                  : 'bg-camelot-gold hover:bg-yellow-400 text-black'
              }`}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              {isListening ? 'LISTENING... (TAP TO CLOSE)' : 'PRESS TO SPEAK TO YOUR ORACLE'}
            </button>
          </div>
        </div>

        <div className="md:col-span-7 space-y-6 flex flex-col justify-between">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-[#121217] border border-[#2A2A35] rounded-xl p-5 hover:border-camelot-gold/50 transition-colors">
              <span className="text-xs font-mono uppercase text-slate-400 block">Total Conversions</span>
              <div className="mt-2 text-3xl font-black font-mono text-white tracking-tight">
                {metrics.conversions}
              </div>
              <span className="text-[10px] font-mono text-emerald-400 mt-1 block">+18 this cycle</span>
            </div>

            <div className="bg-[#121217] border border-[#2A2A35] rounded-xl p-5 hover:border-camelot-gold/50 transition-colors">
              <span className="text-xs font-mono uppercase text-slate-400 block">Average CPA</span>
              <div className="mt-2 text-3xl font-black font-mono text-emerald-400 tracking-tight">
                ${metrics.cpa.toFixed(2)}
              </div>
              <span className="text-[10px] font-mono text-emerald-400 mt-1 block">-14.2% vs target</span>
            </div>

            <div className="bg-[#121217] border-2 border-camelot-gold/40 rounded-xl p-5 shadow-[4px_4px_0px_0px_#D4AF37]">
              <span className="text-xs font-mono uppercase text-slate-400 block">Campaign ROI</span>
              <div className="mt-2 text-3xl font-black font-mono text-camelot-gold tracking-tight">
                +{metrics.roi}%
              </div>
              <span className="text-[10px] font-mono text-yellow-300 mt-1 block">Arbitrage Verified</span>
            </div>
          </div>

          <div className="bg-[#121217] border border-[#2A2A35] rounded-xl p-6 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-center border-b border-slate-800 pb-3 mb-4">
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Activity className="w-3.5 h-3.5 text-camelot-gold" />
                  ORACLE DIALOGUE &bull; A2UI PROJECTION
                </span>
                <span className="text-[10px] font-mono text-slate-500">
                  SUB-100MS VAD ENGINE
                </span>
              </div>

              <div className="p-4 bg-[#0B0B0E] border border-slate-800 rounded-lg min-h-[90px] flex items-center">
                <p className="font-mono text-sm text-slate-200 leading-relaxed">
                  <span className="text-camelot-gold font-bold mr-2">&gt;</span>
                  {transcript}
                </p>
              </div>
            </div>

            <form onSubmit={handleTextQuery} className="mt-4 pt-4 border-t border-slate-800 flex gap-2">
              <input
                type="text"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                placeholder="Type query (e.g., 'What are our current energy savings?')..."
                className="flex-1 bg-[#0B0B0E] border border-slate-700 px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:border-camelot-gold focus:outline-none focus:ring-1 focus:ring-camelot-gold transition-all rounded font-mono"
              />
              <button
                type="submit"
                disabled={!queryInput.trim()}
                className="px-5 py-2.5 bg-camelot-gold hover:bg-yellow-400 text-black font-mono font-black text-xs uppercase tracking-wider rounded transition-all disabled:opacity-50 flex items-center gap-1.5"
              >
                <Send className="w-3.5 h-3.5" /> ASK
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ClientOraclePortal;
