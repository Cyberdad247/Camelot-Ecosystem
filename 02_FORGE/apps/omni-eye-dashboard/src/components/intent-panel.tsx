'use client';

import { useState, useRef } from 'react';
import type { ASTNode }     from '@/lib/parse-ast';
import { parseASTNode }     from '@/lib/parse-ast';

const AGENTS = [
  { id: 'hydron',     label: 'Hydron',     color: '#58a6ff' },
  { id: 'visage',     label: 'Visage',     color: '#a371f7' },
  { id: 'syntax',     label: 'Syntax',     color: '#3fb950' },
  { id: 'stitch',     label: 'Stitch',     color: '#f78166' },
  { id: 'forgemaster',label: 'ForgeMaster',color: '#d29922' },
  { id: 'alchemist',  label: 'Alchemist',  color: '#79c0ff' },
  { id: 'vaelen',     label: 'Vaelen',     color: '#ff7b72' },
];

const TAG_EXAMPLES: Record<string, string> = {
  hero:        'hero section with bold headline',
  nav:         'navigation bar with logo and links',
  features:    'features grid with three benefits',
  testimonial: 'testimonial with customer quote',
  pricing:     'pricing tiers starter pro enterprise',
  gallery:     'image gallery portfolio showcase',
  cta:         'call to action get started button',
  contact:     'contact form with email and message',
  footer:      'footer with links and copyright',
};

interface Props {
  bg:       string;
  onBgChange: (hex: string) => void;
  onAdd:    (node: ASTNode) => void;
  onError:  (msg: string)   => void;
}

export function IntentPanel({ bg, onBgChange, onAdd, onError }: Props) {
  const [intent,  setIntent]  = useState('');
  const [loading, setLoading] = useState(false);
  const [active,  setActive]  = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleAdd() {
    const trimmed = intent.trim();
    if (!trimmed) return;
    setLoading(true);
    setActive('hydron');
    try {
      const res = await fetch('/api/infer', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ intent: trimmed }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({})) as { error?: string };
        throw new Error(err.error ?? `HTTP ${res.status}`);
      }
      const data = await res.json() as { ast_json: string; latency_ms: number };
      const node = parseASTNode(data.ast_json);
      onAdd(node);
      setIntent('');
      inputRef.current?.focus();
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
      setActive(null);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void handleAdd();
    }
  }

  function quickAdd(tag: string) {
    const ex = TAG_EXAMPLES[tag];
    if (ex) {
      setIntent(ex);
      inputRef.current?.focus();
    }
  }

  return (
    <div className="flex flex-col h-full gap-4 p-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-bold tracking-widest uppercase" style={{ color: '#58a6ff' }}>
          Omni-Eye
        </span>
        <span style={{ color: '#30363d' }}>|</span>
        <span className="text-xs" style={{ color: '#8b949e' }}>Website Builder Cartridge</span>
      </div>

      {/* Intent input */}
      <div className="flex flex-col gap-2">
        <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#8b949e' }}>
          Intent
        </label>
        <input
          ref={inputRef}
          value={intent}
          onChange={e => setIntent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="hero section with bold headline…"
          disabled={loading}
          className="w-full rounded-md px-3 py-2 text-sm outline-none transition-colors"
          style={{
            background:  '#161b22',
            border:      '1px solid #30363d',
            color:       '#e6edf3',
            fontFamily:  'inherit',
          }}
        />
        <button
          onClick={() => void handleAdd()}
          disabled={loading || !intent.trim()}
          className="w-full rounded-md px-3 py-2 text-sm font-semibold transition-opacity disabled:opacity-40"
          style={{ background: '#58a6ff', color: '#0d1117' }}
        >
          {loading ? 'Inferring…' : '+ Add Component'}
        </button>
      </div>

      {/* Quick-add tags */}
      <div className="flex flex-col gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#8b949e' }}>
          Quick Add
        </span>
        <div className="flex flex-wrap gap-1">
          {Object.keys(TAG_EXAMPLES).map(tag => (
            <button
              key={tag}
              onClick={() => quickAdd(tag)}
              className="rounded px-2 py-0.5 text-xs font-mono transition-colors hover:opacity-80"
              style={{ background: '#21262d', border: '1px solid #30363d', color: '#8b949e' }}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Background color */}
      <div className="flex flex-col gap-2">
        <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#8b949e' }}>
          Background Color
        </label>
        <div className="flex items-center gap-2">
          <input
            type="color"
            value={bg}
            onChange={e => onBgChange(e.target.value)}
            className="h-8 w-10 cursor-pointer rounded border"
            style={{ border: '1px solid #30363d', background: 'none' }}
          />
          <span className="text-xs font-mono" style={{ color: '#8b949e' }}>{bg}</span>
        </div>
      </div>

      {/* Agent status */}
      <div className="flex flex-col gap-2 mt-auto">
        <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#8b949e' }}>
          Knights Online
        </span>
        <div className="flex flex-col gap-1">
          {AGENTS.map(a => (
            <div key={a.id} className="flex items-center gap-2 text-xs">
              <span
                className="inline-block h-1.5 w-1.5 rounded-full"
                style={{
                  background: active === a.id ? a.color : '#30363d',
                  boxShadow:  active === a.id ? `0 0 6px ${a.color}` : 'none',
                  transition: 'all 0.2s',
                }}
              />
              <span style={{ color: active === a.id ? a.color : '#8b949e' }}>{a.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
