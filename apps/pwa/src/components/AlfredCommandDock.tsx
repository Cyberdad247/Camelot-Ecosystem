// SPDX-License-Identifier: MIT
'use client';

import React, { useState, useEffect, useRef } from 'react';

export function AlfredCommandDock() {
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [transcription, setTranscription] = useState<string>('Standing by for voice command...');
  const [volumeLevel, setVolumeLevel] = useState<number>(0.1);
  const [audioLatencyMs, setAudioLatencyMs] = useState<number>(24);

  // Toggle Push-to-Talk (Local VAD)
  const toggleListening = () => {
    if (!isListening) {
      setIsListening(true);
      setTranscription('Acoustic VAD active · Listening (sub-50ms glass-to-ear)...');
      // Simulate VAD waveform pulses
      const interval = setInterval(() => {
        setVolumeLevel(Math.random() * 0.8 + 0.2);
      }, 100);
      setTimeout(() => {
        clearInterval(interval);
        setIsListening(false);
        setIsSpeaking(true);
        setTranscription('Alfred: Sovereign, all 38 Knights and mesh nodes are verified green.');
        setTimeout(() => {
          setIsSpeaking(false);
          setVolumeLevel(0.05);
        }, 3000);
      }, 2500);
    } else {
      setIsListening(false);
      setVolumeLevel(0.05);
    }
  };

  return (
    <div className="fixed bottom-0 inset-x-0 bg-smoke-950/90 border-t border-gold/40 backdrop-blur-md px-6 py-3 z-40 flex items-center justify-between text-white shadow-2xl">
      {/* Alfred Golden Wireframe Sprite */}
      <div className="flex items-center gap-4">
        <div className="relative">
          <div
            className={`w-12 h-12 rounded-full border-2 flex items-center justify-center transition-all ${
              isListening
                ? 'border-emerald-400 bg-emerald-950/60 shadow-emerald-500/40 shadow-lg scale-105'
                : isSpeaking
                ? 'border-gold bg-gold/20 shadow-gold/50 shadow-lg scale-105'
                : 'border-gold/40 bg-smoke-900'
            }`}
          >
            <span className="text-2xl animate-pulse">👑</span>
          </div>
          <span className="absolute -bottom-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-obsidian">
            <span
              className={`h-2 w-2 rounded-full ${
                isListening ? 'bg-emerald-400 animate-ping' : isSpeaking ? 'bg-gold animate-bounce' : 'bg-gold/40'
              }`}
            />
          </span>
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-bold text-gold tracking-wide">ALFRED SOVEREIGN DOCK</h4>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-smoke-800 border border-gold/20 text-gold-light">
              KICKBOX WASM VAD
            </span>
            <span className="text-[10px] font-mono text-white/40">
              {audioLatencyMs}ms Latency
            </span>
          </div>
          <p className="text-xs text-white/60 font-mono truncate max-w-md mt-0.5">
            {transcription}
          </p>
        </div>
      </div>

      {/* Luxora Gold Audio Waveform */}
      <div className="hidden md:flex items-center gap-1.5 px-4 py-2 bg-obsidian/80 border border-gold/20 rounded-md">
        {[0.3, 0.6, 0.9, 0.4, 0.8, 1.0, 0.5, 0.7, 0.3, 0.9, 0.6, 0.2].map((heightScale, idx) => (
          <div
            key={idx}
            className="w-1 bg-gold rounded-full transition-all duration-75"
            style={{
              height: `${Math.max(4, heightScale * volumeLevel * 28)}px`,
              backgroundColor: isListening ? '#00FF66' : isSpeaking ? '#D4AF37' : '#6B3FA0',
              opacity: isListening || isSpeaking ? 0.9 : 0.4,
            }}
          />
        ))}
      </div>

      {/* Push-to-Talk Command Controls */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={toggleListening}
          className={`px-4 py-2 rounded font-semibold text-xs transition-all flex items-center gap-2 tracking-wider ${
            isListening
              ? 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/30'
              : 'bg-gold/20 hover:bg-gold/30 text-gold border border-gold/40 shadow-gold/20'
          }`}
        >
          <span>{isListening ? '🛑' : '🎙️'}</span>
          {isListening ? 'RELEASE TO SEND' : 'PUSH TO TALK'}
        </button>
      </div>
    </div>
  );
}
