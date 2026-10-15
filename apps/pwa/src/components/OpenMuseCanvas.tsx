'use client';

import React, { useEffect, useState } from 'react';

export interface A2UIComponentItem {
  type: 'Card' | 'Button' | 'DataGrid';
  id: string;
  title?: string;
  content?: string;
  label?: string;
  action?: string;
  rows?: string[];
}

interface OpenMuseCanvasProps {
  initialPayload?: A2UIComponentItem[];
}

export const OpenMuseCanvas: React.FC<OpenMuseCanvasProps> = ({ initialPayload }) => {
  const [components, setComponents] = useState<A2UIComponentItem[]>(
    initialPayload ?? [
      {
        type: 'Card',
        id: 'openmanus_card',
        title: 'OpenManus-RL Status',
        content: 'Autonomous Paperwork: Invoice Generated. Error Rate: 0.05 (Target Met).',
      },
      {
        type: 'Card',
        id: 'readyfleet_card',
        title: 'Readyfleet Mesh',
        content: '50/50 Tasks Processed via Tokio MPSC Channel. 8 Squires Active.',
      },
      {
        type: 'Button',
        id: 'hitl_btn',
        label: 'Scope 2 HITL Gate Authorized 👤✅',
        action: 'CONFIRMED',
      },
    ]
  );
  const [mounted, setMounted] = useState<boolean>(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div className="w-full rounded-lg border border-[#D4AF37]/30 bg-[#050505] p-6 text-[#D4AF37] font-mono shadow-2xl backdrop-blur-md">
      <div className="mb-4 flex items-center justify-between border-b border-[#D4AF37]/20 pb-3">
        <div className="flex items-center space-x-2">
          <span className="h-3 w-3 rounded-full bg-[#D4AF37] animate-pulse" />
          <h2 className="text-sm font-semibold tracking-wider text-[#D4AF37] uppercase">
            OpenMuse WASM Canvas (Dioxus Twin)
          </h2>
        </div>
        <span className="text-xs text-neutral-400">CLS: 0.00 | Latency: 14ms</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {components.map((c) => {
          if (c.type === 'Card') {
            return (
              <div
                key={c.id}
                className="rounded border border-[#D4AF37]/20 bg-neutral-900/60 p-4 transition-all duration-150 hover:border-[#D4AF37]/60"
              >
                <div className="text-xs font-bold text-[#D4AF37] uppercase tracking-wide">
                  {c.title}
                </div>
                <div className="mt-2 text-xs text-neutral-300 leading-relaxed font-sans">
                  {c.content}
                </div>
              </div>
            );
          }

          if (c.type === 'Button') {
            return (
              <div key={c.id} className="md:col-span-2 flex justify-end pt-2">
                <button
                  type="button"
                  className="rounded border border-[#D4AF37] bg-[#D4AF37]/10 px-4 py-2 text-xs font-semibold text-[#D4AF37] hover:bg-[#D4AF37] hover:text-black transition-colors"
                >
                  {c.label}
                </button>
              </div>
            );
          }

          return null;
        })}
      </div>
    </div>
  );
};

export default OpenMuseCanvas;
