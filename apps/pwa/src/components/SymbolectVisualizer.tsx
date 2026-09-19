'use client';

import React, { useState } from 'react';

// Glyph Knowledge Registry matching scripts/symbolect_transpiler.py
export const GLYPH_MAP: Record<string, { category: string; description: string; knight: string }> = {
  '🧠': { category: 'COGNITION', description: 'High-level strategic reasoning and intent distillation', knight: 'MERLIN_OMEGA' },
  '⚡': { category: 'KINETIC', description: 'Direct deterministic execution and compiled native binaries', knight: 'SIR_FORGE' },
  '💬': { category: 'DIALOGUE', description: 'Inter-agent voice resonance and multimodal dialog', knight: 'SIR_SONUS' },
  '🧲': { category: 'FORAGE', description: 'VFS harvesting, web exploration, and document foraging', knight: 'LADY_APIS' },
  '🧪': { category: 'TEST', description: 'Z3 formal verification and automated regression battery', knight: 'SIR_SENTINEL' },
  '📈': { category: 'EVOLVE', description: 'Self-improving trajectory distillation and parameter refinement', knight: 'HERMES_PRIME' },
  '🏆': { category: 'DEPLOY', description: 'Production endpoint release and mesh promotion', knight: 'SIR_KAY' },
  '🛡️': { category: 'SHIELD', description: 'Zero-trust perimeter gating and Agent-Armor PDG protection', knight: 'SIR_HEIMDALL' },
  '🏗️': { category: 'STRUCTURE', description: 'Monorepo architecture and AST structural scaffolding', knight: 'SIR_BORIS' },
  '📜': { category: 'MEMORY', description: 'Tripartite episodic memory and living knowledge graph retrieval', knight: 'LADY_MNEMOSYNE' },
  '🔮': { category: 'ORACLE', description: 'Deep Tree-of-Thought (ToT) search and mathematical proofing', knight: 'MERLIN_OMEGA' },
  '⚜️': { category: 'SOVEREIGN', description: 'Supreme operator directive and HITL governance authorization', knight: 'ARTHUR_OMEGA' },
};

export interface SymbolectDecompiled {
  expression: string;
  glyphs: Array<{ glyph: string; category: string; description: string; knight: string }>;
  anchors: string[];
  primaryKnight: string;
  plainEnglish: string;
  tokenSavingsPct: number;
}

export function decompileSymbolect(expression: string): SymbolectDecompiled {
  const foundGlyphs: Array<{ glyph: string; category: string; description: string; knight: string }> = [];

  for (const [glyph, data] of Object.entries(GLYPH_MAP)) {
    if (expression.includes(glyph)) {
      foundGlyphs.push({ glyph, ...data });
    }
  }

  // Extract bracket anchors ⟨Omega: ...⟩ or |...⟩
  const anchorMatch = expression.match(/[⟨|](?:Omega:)?([^⟩|]+)[⟩|]/);
  let anchors: string[] = [];
  if (anchorMatch && anchorMatch[1]) {
    anchors = anchorMatch[1]
      .split(/[⊗,]/)
      .map((s) => s.replace(/[()]/g, '').trim())
      .filter((s) => s.length > 0 && !Object.keys(GLYPH_MAP).includes(s));
  }

  const primaryKnight = foundGlyphs.length > 0 ? foundGlyphs[0].knight : 'SIR_BORIS';
  const rawWordsEstimate = Math.max(12, foundGlyphs.length * 6 + anchors.length * 8);
  const symbolectTokens = Math.max(2, foundGlyphs.length + anchors.length);
  const tokenSavingsPct = Math.round((1 - symbolectTokens / rawWordsEstimate) * 100);

  const actions = foundGlyphs.map((g) => g.description).join('; ');
  const plainEnglish = actions
    ? `Directs ${primaryKnight} to execute: ${actions}.`
    : `Sovereign symbolic intent anchored to ${primaryKnight}.`;

  return {
    expression,
    glyphs: foundGlyphs,
    anchors,
    primaryKnight,
    plainEnglish,
    tokenSavingsPct,
  };
}

interface SymbolectVisualizerProps {
  rune?: string;
  className?: string;
  showDetails?: boolean;
}

export const SymbolectVisualizer: React.FC<SymbolectVisualizerProps> = ({
  rune = '|🧠⊗(⚡💬)⟩',
  className = '',
  showDetails = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [inputRune, setInputRune] = useState(rune);
  const decompiled = decompileSymbolect(inputRune);

  return (
    <div className={`relative inline-block font-mono text-xs ${className}`}>
      {/* Interactive Rune Trigger Pill */}
      <div
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-md cursor-pointer transition-all duration-200 bg-[#0B0F19] border border-[#D4AF37]/50 hover:border-[#D4AF37] hover:shadow-[0_0_12px_rgba(212,175,55,0.25)] text-slate-100"
      >
        <span className="text-[#D4AF37] text-sm">🔮</span>
        <span className="font-bold tracking-wider text-amber-200">{inputRune}</span>
        <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-[#D4AF37]/15 text-[#D4AF37] border border-[#D4AF37]/30">
          -{decompiled.tokenSavingsPct}% TOKENS
        </span>
      </div>

      {/* Hovercard Tooltip (3 AM Incident Decompiler) */}
      {(isHovered || showDetails) && (
        <div
          className="absolute z-50 top-full mt-2 left-0 w-80 p-4 rounded-lg bg-[#070A12] border border-[#D4AF37]/60 shadow-[0_8px_32px_rgba(0,0,0,0.85)] text-slate-200 transition-opacity animate-in fade-in zoom-in-95 duration-150"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-2 border-b border-white/10">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#D4AF37] animate-pulse" />
              <span className="text-[11px] font-bold tracking-widest text-[#D4AF37] uppercase">
                Symbolect Decompiler
              </span>
            </div>
            <span className="text-[10px] text-slate-400 font-medium">3 AM Incident Guard</span>
          </div>

          {/* Target Knight */}
          <div className="mt-3 flex items-center justify-between">
            <span className="text-[11px] text-slate-400">Target Knight:</span>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/40">
              {decompiled.primaryKnight}
            </span>
          </div>

          {/* Plain English Translation */}
          <div className="mt-2.5 p-2 rounded bg-white/[0.03] border border-white/5">
            <p className="text-[11px] text-slate-300 leading-relaxed">
              {decompiled.plainEnglish}
            </p>
          </div>

          {/* Glyph Breakdown */}
          {decompiled.glyphs.length > 0 && (
            <div className="mt-3 space-y-1.5">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">
                Active Glyphs ({decompiled.glyphs.length})
              </span>
              <div className="space-y-1">
                {decompiled.glyphs.map((g, i) => (
                  <div key={i} className="flex items-start gap-2 text-[10px]">
                    <span className="text-sm leading-none">{g.glyph}</span>
                    <div>
                      <span className="font-bold text-amber-200">{g.category}: </span>
                      <span className="text-slate-400">{g.description}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Token Compression Efficiency Bar */}
          <div className="mt-3 pt-2.5 border-t border-white/10 flex items-center justify-between text-[10px]">
            <span className="text-slate-400">Efficiency Gain:</span>
            <div className="flex items-center gap-1.5">
              <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#D4AF37] rounded-full"
                  style={{ width: `${decompiled.tokenSavingsPct}%` }}
                />
              </div>
              <span className="font-bold text-[#D4AF37]">
                {decompiled.tokenSavingsPct}% saved
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SymbolectVisualizer;
