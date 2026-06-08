'use client';

import type { ASTNode } from '@/lib/parse-ast';

const TAG_ICONS: Record<string, string> = {
  nav:         '≡',
  hero:        '◈',
  features:    '⊞',
  testimonial: '❝',
  pricing:     '$',
  gallery:     '⊟',
  cta:         '►',
  contact:     '✉',
  footer:      '⊥',
  card:        '▣',
};

const TAG_COLORS: Record<string, string> = {
  nav:         '#58a6ff',
  hero:        '#a371f7',
  features:    '#3fb950',
  testimonial: '#f0883e',
  pricing:     '#d29922',
  gallery:     '#79c0ff',
  cta:         '#ff7b72',
  contact:     '#56d364',
  footer:      '#8b949e',
  card:        '#bc8cff',
};

interface Props {
  nodes:    ReadonlyMap<string, ASTNode>;
  canUndo:  boolean;
  canRedo:  boolean;
  onRemove: (id: string) => void;
  onUndo:   () => void;
  onRedo:   () => void;
  onReset:  () => void;
}

export function NodeTree({ nodes, canUndo, canRedo, onRemove, onUndo, onRedo, onReset }: Props) {
  const list = [...nodes.values()].sort((a, b) => {
    const ORDER: Record<string, number> = {
      nav: 0, hero: 1, features: 2, gallery: 3,
      testimonial: 4, pricing: 5, cta: 6, contact: 7, footer: 8,
    };
    return (ORDER[a.tag] ?? 3) - (ORDER[b.tag] ?? 3);
  });

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div
        className="flex items-center gap-1 px-3 py-2 border-b text-xs"
        style={{ borderColor: '#30363d' }}
      >
        <span className="font-semibold uppercase tracking-wider mr-auto" style={{ color: '#8b949e' }}>
          Components
          <span className="ml-2 font-mono" style={{ color: '#58a6ff' }}>{list.length}</span>
        </span>
        <button
          onClick={onUndo}
          disabled={!canUndo}
          title="Undo"
          className="px-2 py-0.5 rounded disabled:opacity-30 hover:opacity-80 font-mono"
          style={{ background: '#21262d', color: '#8b949e', border: '1px solid #30363d' }}
        >↩</button>
        <button
          onClick={onRedo}
          disabled={!canRedo}
          title="Redo"
          className="px-2 py-0.5 rounded disabled:opacity-30 hover:opacity-80 font-mono"
          style={{ background: '#21262d', color: '#8b949e', border: '1px solid #30363d' }}
        >↪</button>
        <button
          onClick={onReset}
          disabled={list.length === 0}
          title="Clear all"
          className="px-2 py-0.5 rounded disabled:opacity-30 hover:opacity-80 font-mono"
          style={{ background: '#21262d', color: '#ff7b72', border: '1px solid #30363d' }}
        >✕</button>
      </div>

      {/* Node list */}
      <div className="flex-1 overflow-y-auto">
        {list.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2 p-6 text-center">
            <span style={{ color: '#30363d', fontSize: '2rem' }}>◌</span>
            <p className="text-xs" style={{ color: '#8b949e' }}>
              No components yet.<br />Type an intent and press Add.
            </p>
          </div>
        ) : (
          <ul className="py-1">
            {list.map(node => {
              const icon  = TAG_ICONS[node.tag]  ?? '·';
              const color = TAG_COLORS[node.tag] ?? '#8b949e';
              const intent = String(node.props.intent ?? '').slice(0, 48);
              return (
                <li
                  key={node.id}
                  className="group flex items-start gap-2 px-3 py-2 hover:opacity-90 transition-opacity border-b"
                  style={{ borderColor: '#21262d' }}
                >
                  <span
                    className="mt-0.5 flex-shrink-0 text-xs w-5 text-center font-bold"
                    style={{ color }}
                  >
                    {icon}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold font-mono" style={{ color }}>
                      {node.tag}
                    </div>
                    {intent && (
                      <div
                        className="text-xs truncate mt-0.5"
                        style={{ color: '#8b949e' }}
                        title={String(node.props.intent ?? '')}
                      >
                        {intent}
                      </div>
                    )}
                    <div className="text-xs mt-0.5 font-mono" style={{ color: '#30363d' }}>
                      {node.id.slice(0, 8)}
                    </div>
                  </div>
                  <button
                    onClick={() => onRemove(node.id)}
                    className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity px-1 rounded text-xs hover:opacity-80"
                    style={{ color: '#ff7b72' }}
                    title="Remove"
                  >
                    ✕
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
