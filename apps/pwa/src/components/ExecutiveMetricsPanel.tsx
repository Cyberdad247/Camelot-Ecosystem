// SPDX-License-Identifier: MIT

'use client';

import React from 'react';

export interface MetricCardData {
  title: string;
  value: string;
  subtext: string;
  trend: 'UP' | 'DOWN' | 'NOMINAL';
  highlightColor?: string;
}

const METRICS: MetricCardData[] = [
  {
    title: 'PORTFOLIO VALUATION',
    value: '$14,250,000.00',
    subtext: '+14.2% YoY (CRDT WASM Verified)',
    trend: 'UP',
    highlightColor: '#D4AF37',
  },
  {
    title: 'BIFROST MESH TELEMETRY',
    value: '100.71.218.75:4433',
    subtext: '12ms Ping | 100% Packet Integrity',
    trend: 'NOMINAL',
    highlightColor: '#9D4EDD',
  },
  {
    title: 'WORLDTREE CLOUDBRAIN',
    value: '24 / 24 KNIGHTS',
    subtext: 'UUID: a0a4bfb9... Anchored',
    trend: 'NOMINAL',
    highlightColor: '#10B981',
  },
  {
    title: 'TRANSACTION VELOCITY',
    value: '1,420 Tx / sec',
    subtext: 'Zero-Burn Local CLIProxy Active',
    trend: 'UP',
    highlightColor: '#D4AF37',
  },
];

export function ExecutiveMetricsPanel() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono mb-8">
      {METRICS.map((metric, idx) => (
        <div
          key={idx}
          className="border-2 border-[#D4AF37]/40 bg-[#0B0B0E] p-5 shadow-[4px_4px_0px_0px_#D4AF37] relative group hover:scale-[1.02] transition-transform"
        >
          <div className="flex justify-between items-center mb-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              {metric.title}
            </span>
            <span
              className={`text-[10px] font-black px-1.5 py-0.5 border ${
                metric.trend === 'UP'
                  ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10'
                  : 'border-slate-700 text-slate-300 bg-slate-900'
              }`}
            >
              {metric.trend}
            </span>
          </div>

          <div
            className="text-xl md:text-2xl font-black text-slate-100 mt-1 truncate"
            style={{ color: metric.highlightColor || '#D4AF37' }}
          >
            {metric.value}
          </div>

          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>{metric.subtext}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
