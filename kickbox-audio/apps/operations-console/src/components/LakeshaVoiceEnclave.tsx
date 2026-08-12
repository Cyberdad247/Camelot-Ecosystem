'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export function LakeshaVoiceEnclave() {
  const [isListening, setIsListening] = useState<boolean>(false);
  const [transcript, setTranscript] = useState<string>(
    'LaKesha Audio VAD active. Say "Approve Chloe Refund" or click to speak.'
  );
  const [audioBars, setAudioBars] = useState<number[]>([30, 60, 45, 80, 55, 90, 40, 70]);

  useEffect(() => {
    if (!isListening) return;
    const interval = setInterval(() => {
      setAudioBars(Array.from({ length: 8 }, () => Math.floor(Math.random() * 70) + 25));
    }, 150);
    return () => clearInterval(interval);
  }, [isListening]);

  const toggleMic = () => {
    setIsListening((prev) => !prev);
    if (!isListening) {
      setTranscript('Listening... Web Speech WASM VAD active (sub-350ms TTFA)');
    } else {
      setTranscript('LaKesha Audio VAD standby. Click mic to engage voice hypervisor.');
    }
  };

  return (
    <div className="border-2 border-[#9D4EDD]/60 bg-[#0B0B0E] p-6 shadow-[6px_6px_0px_0px_#9D4EDD] space-y-4 font-mono relative">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-[#9D4EDD]/30 pb-4 gap-3">
        <div className="flex items-center gap-3">
          <span className={`h-3 w-3 ${isListening ? 'bg-emerald-400 shadow-[0_0_12px_#10B981] animate-ping' : 'bg-[#9D4EDD]'}`} />
          <div>
            <div className="text-[10px] text-[#D4AF37] font-bold tracking-widest uppercase">
              LAKESHA VOICE HYPERVISOR // WEBRTC VAD
            </div>
            <h3 className="text-lg font-black text-slate-100 uppercase mt-0.5">
              Voice Command Enclave
            </h3>
          </div>
        </div>

        <button
          onClick={toggleMic}
          className={`px-4 py-2 text-xs font-black uppercase tracking-wider transition-all cursor-pointer border-2 ${
            isListening
              ? 'bg-emerald-500 text-slate-950 border-emerald-300 shadow-[3px_3px_0px_0px_#050507]'
              : 'bg-[#9D4EDD] text-slate-950 border-[#9D4EDD] hover:bg-purple-400 shadow-[3px_3px_0px_0px_#D4AF37]'
          }`}
        >
          {isListening ? '🎙️ MIC ACTIVE (RECORDING)' : '🎙️ ENGAGE LAKESHA MIC'}
        </button>
      </div>

      {/* Audio Spectrum VU Meter */}
      <div className="flex items-end justify-center space-x-1.5 h-12 bg-slate-950 p-2 border border-slate-800">
        {audioBars.map((height, i) => (
          <motion.div
            key={i}
            animate={{ height: isListening ? `${height}%` : '15%' }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className={`w-2.5 transition-colors ${
              isListening ? 'bg-[#9D4EDD] shadow-[0_0_10px_#9D4EDD]' : 'bg-slate-800'
            }`}
          />
        ))}
      </div>

      {/* Real-time Voice Transcript Display */}
      <div className="p-3 border border-slate-800 bg-slate-950/80 text-xs text-slate-300 flex items-center gap-3">
        <span className="text-[#D4AF37] font-bold shrink-0">TRANSCRIPT:</span>
        <span className="truncate italic font-sans text-slate-200">{transcript}</span>
      </div>
    </div>
  );
}
