// SPDX-License-Identifier: MIT
// Holographic Client Oracle (Bifrost Board Edition)
// Compatible with lucide-react

import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Sparkles, Send, Activity, Radio } from 'lucide-react';

export interface OracleMessage {
  id: string;
  sender: string;
  role: 'oracle' | 'client';
  text: string;
  timestamp: string;
}

export function HolographicClientOracle() {
  const [isMicActive, setIsMicActive] = useState<boolean>(false);
  const [isOracleSpeaking, setIsOracleSpeaking] = useState<boolean>(false);
  const [audioLatencyMs, setAudioLatencyMs] = useState<number>(18);
  const [waveformBars, setWaveformBars] = useState<number[]>([20, 45, 75, 30, 90, 60, 40, 85, 55, 30, 65, 40]);
  const [inputText, setInputText] = useState<string>('');

  const [messages, setMessages] = useState<OracleMessage[]>([
    {
      id: 'msg_1',
      sender: 'Lady Apis (Oracle)',
      role: 'oracle',
      text: 'Greetings, Principal. I am Lady Apis, your sovereign swarm conductor. The live audit on your B2B deregulated energy accounts shows a 14.2% rate arbitrage vector in the PJM territory. Would you like me to dispatch Sir Hydron to lock in the rates?',
      timestamp: '11:25 AM',
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isMicActive || isOracleSpeaking) {
      interval = setInterval(() => {
        setWaveformBars(Array.from({ length: 16 }, () => Math.floor(Math.random() * 85 + 15)));
        setAudioLatencyMs(Math.floor(Math.random() * 6 + 14));
      }, 90);
    } else {
      setWaveformBars([12, 18, 14, 22, 16, 20, 14, 24, 18, 16, 22, 14, 12, 18, 15, 14]);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isMicActive, isOracleSpeaking]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMsg: OracleMessage = {
      id: `msg_${Date.now()}`,
      sender: 'Client Principal',
      role: 'client',
      text: inputText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    const query = inputText;
    setInputText('');

    setIsOracleSpeaking(true);
    setTimeout(() => {
      let replyText = `Confirmed. Routing your query regarding "${query}" through the Round Table DAG. All telemetry checks are passing with zero drift.`;
      if (query.toLowerCase().includes('energy') || query.toLowerCase().includes('rates')) {
        replyText = `Understood. Analyzing regional electricity tariffs across Ohio and Pennsylvania. Current savings projection stands at $18,450/month. Rate lock request prepared.`;
      } else if (query.toLowerCase().includes('marketing') || query.toLowerCase().includes('seo') || query.toLowerCase().includes('ad')) {
        replyText = `Swarm telemetry active. Sir Visage has compiled 12 conversion hooks with a predicted +24% CTR. Deployed live to A2UI staging.`;
      }

      const oracleMsg: OracleMessage = {
        id: `msg_${Date.now() + 1}`,
        sender: 'Lady Apis (Oracle)',
        role: 'oracle',
        text: replyText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, oracleMsg]);
      setIsOracleSpeaking(false);
    }, 1200);
  };

  const toggleMic = () => {
    if (!isMicActive) {
      setIsMicActive(true);
      setTimeout(() => {
        setIsMicActive(false);
        setIsOracleSpeaking(true);
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            {
              id: `msg_${Date.now()}`,
              sender: 'Client Principal (Voice Input)',
              role: 'client',
              text: 'Oracle, give me a status report on our marketing ROI and current energy arbitrations.',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
            {
              id: `msg_${Date.now() + 1}`,
              sender: 'Lady Apis (Oracle)',
              role: 'oracle',
              text: `Acoustic link verified. Overall pipeline value is up +12% this quarter ($142,500 active ARR). Energy hedging contracts are 100% sealed on Tailscale dark mesh.`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);
          setIsOracleSpeaking(false);
        }, 1100);
      }, 2200);
    } else {
      setIsMicActive(false);
    }
  };

  return (
    <div className="w-full bg-[#050508] p-4 md:p-8 font-sans text-slate-200 border-2 border-camelot-gold/40 shadow-[6px_6px_0px_0px_#D4AF37] rounded-xl">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#2A2A35] pb-5 mb-6 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-camelot-gold animate-pulse" />
            <span className="text-[10px] font-mono text-camelot-cyan tracking-[0.25em] uppercase">
              HOLOGRAPHIC CLIENT ORACLE // VECTOR 1
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight uppercase mt-1">
            Sovereign <span className="text-camelot-gold">Client Oracle</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            2.5D Audio-Reactive Hologram &bull; Duplex WebRTC Voice &bull; Port :7680
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1.5 bg-smoke-800 border border-camelot-gold/40 text-camelot-gold font-mono text-xs font-bold uppercase tracking-wider">
            LATENCY: {audioLatencyMs}ms
          </span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <div className="md:col-span-5 bg-[#121217] border-2 border-camelot-gold/40 rounded-xl p-6 flex flex-col items-center justify-between shadow-[4px_4px_0px_0px_#D4AF37] relative overflow-hidden">
          <div className="pointer-events-none absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(212,175,55,0.04)_3px)]" />

          <div className="w-full flex justify-between items-center text-xs font-mono border-b border-slate-800 pb-3">
            <span className="text-camelot-gold font-bold">LADY APIS</span>
            <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
              {isOracleSpeaking ? 'TRANSMITTING' : isMicActive ? 'LISTENING' : 'RESONATING'}
            </span>
          </div>

          <div className="my-8 relative flex items-center justify-center">
            {(isOracleSpeaking || isMicActive) && (
              <>
                <span className="absolute h-40 w-40 animate-ping rounded-full border border-camelot-gold/30 opacity-75" />
                <span className="absolute h-52 w-52 animate-pulse rounded-full border border-camelot-violet/30" />
              </>
            )}

            <div
              className={`h-32 w-32 rounded-full transition-all duration-300 flex items-center justify-center relative shadow-[0_0_50px_rgba(212,175,55,0.4)] ${
                isOracleSpeaking
                  ? 'scale-110 shadow-[0_0_60px_rgba(255,215,0,0.8)]'
                  : isMicActive
                  ? 'scale-105 shadow-[0_0_60px_rgba(0,229,255,0.8)]'
                  : 'hover:scale-105'
              }`}
              style={{
                background: isOracleSpeaking
                  ? 'radial-gradient(circle at 35% 30%, #FFD700, #D4AF37 55%, #050508 85%)'
                  : isMicActive
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
                    backgroundColor: isOracleSpeaking
                      ? '#FFD700'
                      : isMicActive
                      ? '#00E5FF'
                      : '#D4AF37',
                    opacity: isOracleSpeaking || isMicActive ? 0.9 : 0.4,
                  }}
                />
              ))}
            </div>

            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
              DUPLEX WEBRTC &bull; 432Hz HARMONIC TUNNEL
            </span>
          </div>

          <div className="mt-5 w-full flex justify-center">
            <button
              type="button"
              onClick={toggleMic}
              className={`w-full py-3 rounded font-mono font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all shadow-[2px_2px_0px_0px_#000000] active:translate-y-0.5 ${
                isMicActive
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                  : 'bg-camelot-gold hover:bg-yellow-400 text-black'
              }`}
            >
              {isMicActive ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              {isMicActive ? 'RECORDING VOICE... (CLICK TO STOP)' : 'SPEAK TO THE ORACLE'}
            </button>
          </div>
        </div>

        <div className="md:col-span-7 bg-[#121217] border border-[#2A2A35] rounded-xl p-5 flex flex-col justify-between h-[480px]">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3 mb-3">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Radio className="w-3.5 h-3.5 text-camelot-gold" />
              LIVE ORACLE INTELLIGENCE FEED
            </span>
            <span className="text-[10px] font-mono text-slate-500">
              TENANT: INVISIONED_MARKETING_INC
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-2 font-mono text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`p-3 rounded-lg border leading-relaxed ${
                  m.role === 'oracle'
                    ? 'bg-[#0B0B0E] border-camelot-gold/30 text-slate-200'
                    : 'bg-smoke-800 border-slate-700 text-slate-100 ml-6'
                }`}
              >
                <div className="flex justify-between items-center mb-1 text-[10px]">
                  <span className={m.role === 'oracle' ? 'text-camelot-gold font-bold' : 'text-camelot-cyan font-bold'}>
                    {m.sender.toUpperCase()}
                  </span>
                  <span className="text-slate-500">{m.timestamp}</span>
                </div>
                <p className="font-sans text-sm">{m.text}</p>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="pt-2 flex flex-wrap gap-2 text-[10px] font-mono">
            <button
              type="button"
              onClick={() => setInputText('Audit our current deregulated energy savings.')}
              className="px-2.5 py-1 bg-[#0B0B0E] border border-slate-800 hover:border-camelot-gold/50 text-slate-400 hover:text-camelot-gold rounded transition-all"
            >
              &bull; Energy Savings Audit
            </button>
            <button
              type="button"
              onClick={() => setInputText('Show marketing campaign CTR and lead yields.')}
              className="px-2.5 py-1 bg-[#0B0B0E] border border-slate-800 hover:border-camelot-gold/50 text-slate-400 hover:text-camelot-gold rounded transition-all"
            >
              &bull; Marketing Campaign CTR
            </button>
            <button
              type="button"
              onClick={() => setInputText('What is our current monthly retainers total?')}
              className="px-2.5 py-1 bg-[#0B0B0E] border border-slate-800 hover:border-camelot-gold/50 text-slate-400 hover:text-camelot-gold rounded transition-all"
            >
              &bull; Retainer Total
            </button>
          </div>

          <form onSubmit={handleSendMessage} className="mt-3 pt-3 border-t border-slate-800 flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Query your AI Knight on metrics, contracts, or ad spend..."
              className="flex-1 bg-[#0B0B0E] border border-slate-700 px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:border-camelot-gold focus:outline-none focus:ring-1 focus:ring-camelot-gold transition-all rounded"
            />
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="px-5 py-2.5 bg-camelot-gold hover:bg-yellow-400 text-black font-mono font-black text-xs uppercase tracking-wider rounded transition-all disabled:opacity-50 flex items-center gap-1.5"
            >
              <Send className="w-3.5 h-3.5" /> TRANSMIT
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default HolographicClientOracle;
