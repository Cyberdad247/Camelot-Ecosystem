// SPDX-License-Identifier: MIT
// Five-Pillar Mathematical Blended Emergence Conversational Dialect Visualizer
// v10001.00-CYBERTRONIA

'use client';

import React from 'react';
import { FivePillarDialectConfig } from '../../lib/voiceInferenceLayer';

interface Props {
  dialect: FivePillarDialectConfig;
  knightName: string;
  isSpeaking?: boolean;
}

export function FivePillarDialectVisualizer({ dialect, knightName, isSpeaking = false }: Props) {
  const {
    pillar1_pitchContour,
    pillar2_intonationAndCadence,
    pillar3_rmsEnergyDynamics,
    pillar4_conversationalBackchanneling,
    pillar5_adaptiveTurnTakingAndVisemes
  } = dialect;

  return (
    <div className="border border-[#D4AF37]/30 bg-[#0B0B0E]/95 p-5 backdrop-blur-md space-y-5 font-mono shadow-[0_0_20px_rgba(212,175,55,0.08)]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-[#D4AF37]/20 pb-3 gap-2">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-[#D4AF37] animate-pulse" />
          <h3 className="text-sm font-black text-slate-100 uppercase tracking-wider">
            5-PILLAR MATHEMATICAL BLENDED EMERGENCE // CONVERSATIONAL DIALECT
          </h3>
        </div>
        <div className="flex items-center gap-2 text-[10px] text-slate-400">
          <span>ACTIVE PROFILE:</span>
          <span className="text-[#D4AF37] font-bold uppercase">{knightName}</span>
          {isSpeaking && (
            <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[9px] animate-pulse">
              LIVE MODULATION
            </span>
          )}
        </div>
      </div>

      {/* Grid of the 5 Mathematical Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Pillar 1: F0 Pitch Contour & Micro-Prosody */}
        <div className="p-3.5 border border-slate-800 bg-slate-950/80 rounded-sm space-y-2">
          <div className="flex items-center justify-between text-[11px] text-[#D4AF37] font-bold uppercase">
            <span>PILLAR 1: F0 PITCH CONTOUR</span>
            <span className="text-[10px] text-slate-400 font-normal">HNR: {pillar1_pitchContour.hnrDb} dB</span>
          </div>
          <div className="h-14 flex items-end justify-between gap-1 px-1 bg-black/40 border border-slate-900 rounded p-1">
            {pillar1_pitchContour.f0Trajectory.map((hz, idx) => {
              const heightPct = Math.min(100, Math.max(15, ((hz - 100) / 150) * 100));
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-0.5">
                  <div 
                    className="w-full bg-gradient-to-t from-[#D4AF37]/30 to-[#D4AF37] rounded-t-sm transition-all duration-300"
                    style={{ height: `${heightPct}%` }}
                  />
                  <span className="text-[8px] text-slate-500">{hz}</span>
                </div>
              );
            })}
          </div>
          <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-300 pt-1">
            <div>Base F0: <span className="text-[#D4AF37] font-bold">{pillar1_pitchContour.basePitchHz} Hz</span></div>
            <div>Delta: <span className="text-[#D4AF37] font-bold">±{pillar1_pitchContour.deltaPitchHz} Hz</span></div>
            <div className="col-span-2 text-slate-400 text-[9px]">
              Micro-Prosody Jitter σ²: <span className="text-slate-200">{pillar1_pitchContour.jitterVariance}</span>
            </div>
          </div>
        </div>

        {/* Pillar 2: Intonation Slope & Cadence */}
        <div className="p-3.5 border border-slate-800 bg-slate-950/80 rounded-sm space-y-2">
          <div className="flex items-center justify-between text-[11px] text-[#D4AF37] font-bold uppercase">
            <span>PILLAR 2: INTONATION & CADENCE</span>
            <span className="text-[10px] text-emerald-400 font-bold">{pillar2_intonationAndCadence.speechCadenceWpm} WPM</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-black/40 border border-slate-900 rounded">
            <div className="text-[10px] text-slate-300">
              <div className="text-slate-500 text-[9px] uppercase">Slope dF0/dt</div>
              <div className="text-sm font-bold text-slate-100 flex items-center gap-1 mt-0.5">
                <span>{pillar2_intonationAndCadence.intonationSlope > 0 ? '▲' : '▼'}</span>
                <span>{pillar2_intonationAndCadence.intonationSlope.toFixed(2)}</span>
                <span className="text-[9px] font-normal text-slate-400">
                  {pillar2_intonationAndCadence.intonationSlope > 0 ? '(Inquiry)' : '(Command)'}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-slate-500 text-[9px] uppercase">Syllabic Rhythm</div>
              <div className="flex items-center gap-1 mt-1 justify-end">
                {pillar2_intonationAndCadence.syllabicRhythm.map((val, idx) => (
                  <div 
                    key={idx} 
                    className="w-1.5 bg-[#9D4EDD] rounded-full" 
                    style={{ height: `${val * 16}px` }} 
                  />
                ))}
              </div>
            </div>
          </div>
          <div className="text-[9px] text-slate-400">
            Cadence velocity aligned for sub-50ms reactive cognitive uptake.
          </div>
        </div>

        {/* Pillar 3: RMS Energy Dynamics */}
        <div className="p-3.5 border border-slate-800 bg-slate-950/80 rounded-sm space-y-2">
          <div className="flex items-center justify-between text-[11px] text-[#D4AF37] font-bold uppercase">
            <span>PILLAR 3: RMS ENERGY</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {pillar3_rmsEnergyDynamics.energyTier}
            </span>
          </div>
          <div className="space-y-1.5 p-2 bg-black/40 border border-slate-900 rounded">
            <div className="flex justify-between text-[10px]">
              <span className="text-slate-400">Intensity Decibels:</span>
              <span className="text-[#D4AF37] font-bold">{pillar3_rmsEnergyDynamics.rmsEnergyDb} dB</span>
            </div>
            <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
              <div 
                className="bg-gradient-to-r from-emerald-500 via-[#D4AF37] to-amber-500 h-full rounded-full"
                style={{ width: `${Math.min(100, Math.max(10, (pillar3_rmsEnergyDynamics.rmsEnergyDb + 35) * 4))}%` }}
              />
            </div>
            <div className="flex justify-between text-[9px] text-slate-500">
              <span>Dyn. Ratio: {pillar3_rmsEnergyDynamics.dynamicRangeRatio}x</span>
              <span>Breathiness: {(pillar3_rmsEnergyDynamics.breathinessCurve * 100).toFixed(0)}%</span>
            </div>
          </div>
          <div className="text-[9px] text-slate-400">
            Zero-distortion dynamic compression preserving vocal intimacy.
          </div>
        </div>

        {/* Pillar 4: Conversational Backchanneling */}
        <div className="p-3.5 border border-slate-800 bg-slate-950/80 rounded-sm space-y-2">
          <div className="flex items-center justify-between text-[11px] text-[#D4AF37] font-bold uppercase">
            <span>PILLAR 4: BACKCHANNELING</span>
            <span className="text-[10px] text-sky-400 font-bold">
              {(pillar4_conversationalBackchanneling.backchannelProbability * 100).toFixed(0)}% P(BC)
            </span>
          </div>
          <div className="p-2 bg-black/40 border border-slate-900 rounded space-y-1.5">
            <div className="text-[9px] text-slate-500 uppercase">Active Backchannel Tokens:</div>
            <div className="flex flex-wrap gap-1">
              {pillar4_conversationalBackchanneling.activeTokens.map((token, idx) => (
                <span key={idx} className="text-[9px] px-1.5 py-0.5 rounded bg-sky-950/70 text-sky-300 border border-sky-800/60 font-sans">
                  "{token}"
                </span>
              ))}
            </div>
            <div className="flex justify-between text-[9px] text-slate-400 pt-1">
              <span>Barge-In Gate: {pillar4_conversationalBackchanneling.bargeInAcousticThresholdDb} dB</span>
              <span className="text-emerald-400 font-bold">Duplex: Continuous</span>
            </div>
          </div>
          <div className="text-[9px] text-slate-400">
            Allows affirmative micro-cues without triggering speaker interruption.
          </div>
        </div>

        {/* Pillar 5: Adaptive Turn-Taking & Visemes */}
        <div className="p-3.5 border border-slate-800 bg-slate-950/80 rounded-sm space-y-2 md:col-span-2">
          <div className="flex items-center justify-between text-[11px] text-[#D4AF37] font-bold uppercase">
            <span>PILLAR 5: TURN-TAKING & 25 FPS VISEME LIP-SYNC</span>
            <span className="text-[10px] text-violet-400 font-bold">
              τ_silence: {pillar5_adaptiveTurnTakingAndVisemes.adaptiveSilenceThresholdMs}ms
            </span>
          </div>
          <div className="p-2 bg-black/40 border border-slate-900 rounded space-y-2">
            <div className="flex items-center justify-between text-[9px] text-slate-400">
              <span>16-Standard Viseme Blend Shapes (25 FPS LiveTalking Stream):</span>
              <span className="text-slate-300">Latency: {pillar5_adaptiveTurnTakingAndVisemes.lipSyncLatencyMs}ms</span>
            </div>
            <div className="grid grid-cols-8 gap-1.5">
              {Object.entries(pillar5_adaptiveTurnTakingAndVisemes.visemeBlendWeights).map(([viseme, weight]) => (
                <div key={viseme} className="flex flex-col items-center bg-slate-900/80 p-1 border border-slate-800 rounded text-center">
                  <span className="text-[8px] text-slate-400 uppercase font-bold">{viseme}</span>
                  <div className="w-full bg-slate-950 h-6 mt-1 rounded overflow-hidden flex items-end">
                    <div 
                      className="w-full bg-gradient-to-t from-violet-600 to-[#D4AF37] transition-all duration-150"
                      style={{ height: `${weight * 100}%` }}
                    />
                  </div>
                  <span className="text-[8px] text-[#D4AF37] mt-0.5">{weight.toFixed(1)}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="text-[9px] text-slate-400">
            Real-time visual phoneme-viseme alignment for seamless 25 FPS digital human immersion.
          </div>
        </div>
      </div>
    </div>
  );
}
