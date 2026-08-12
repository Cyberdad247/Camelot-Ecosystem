'use client';

import React from 'react';
import { motion } from 'framer-motion';

export interface OpenDesignPillItem {
  label: string;
  value: string;
  status: 'ONLINE' | 'ACTIVE' | 'ENFORCED' | 'STANDBY';
  color: string;
}

const PILL_DATA: OpenDesignPillItem[] = [
  { label: 'OPEN DESIGN ENGINE', value: 'v1.0.0-LUXURY_BRUTALISM', status: 'ACTIVE', color: '#D4AF37' },
  { label: 'ANYA FIRST LAW', value: 'APEE v7.0 ENFORCED', status: 'ENFORCED', color: '#9D4EDD' },
  { label: 'BIFROST DISPATCH', value: 'mTLS :4433 / :4434', status: 'ONLINE', color: '#10B981' },
  { label: 'WORLDTREE CLOUDBRAIN', value: '24 KNIGHTS TETHERED', status: 'ONLINE', color: '#3B82F6' },
];

export function OpenDesignStatusPills() {
  return (
    <div className="flex flex-wrap items-center gap-3 font-mono">
      {PILL_DATA.map((item, idx) => (
        <motion.div
          key={idx}
          whileHover={{ scale: 1.03 }}
          className="flex items-center gap-2 px-3 py-1.5 border border-[#D4AF37]/30 bg-[#0B0B0E]/90 backdrop-blur-md shadow-[3px_3px_0px_0px_#050507]"
        >
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
          <span className="text-[10px] font-bold text-slate-400 uppercase">{item.label}:</span>
          <span className="text-[11px] font-black text-slate-100">{item.value}</span>
        </motion.div>
      ))}
    </div>
  );
}
