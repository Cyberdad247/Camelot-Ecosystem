'use client';

import { useState } from 'react';
import { useAstStore }    from '@/lib/crdt';
import { IntentPanel }    from '@/components/intent-panel';
import { NodeTree }       from '@/components/node-tree';
import { PreviewFrame }   from '@/components/preview-frame';
import type { ASTNode }   from '@/lib/parse-ast';

export default function CockpitPage() {
  const [bg,       setBg]       = useState('#ffffff');
  const [siteName, setSiteName] = useState('camelot-site');
  const [error,    setError]    = useState<string | null>(null);

  const { nodes, insert, remove, undo, redo, canUndo, canRedo, reset } = useAstStore();

  function handleAdd(node: ASTNode) {
    try {
      insert(node);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  function handleRemove(id: string) {
    try {
      remove(id);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Top bar */}
      <div
        className="flex items-center gap-3 px-4 py-2 flex-shrink-0 border-b"
        style={{ background: '#161b22', borderColor: '#30363d' }}
      >
        <span className="text-xs font-bold tracking-widest" style={{ color: '#58a6ff' }}>
          CAMELOT-OS
        </span>
        <span style={{ color: '#30363d' }}>›</span>
        <span className="text-xs" style={{ color: '#8b949e' }}>Website Builder Cartridge</span>
        <span style={{ color: '#30363d' }}>›</span>
        <input
          value={siteName}
          onChange={e => setSiteName(e.target.value)}
          className="text-xs rounded px-2 py-0.5 outline-none"
          style={{
            background: '#0d1117',
            border:     '1px solid #30363d',
            color:      '#e6edf3',
            fontFamily: 'inherit',
            width:      '180px',
          }}
          placeholder="site-name"
        />
        <span className="ml-auto text-xs font-mono" style={{ color: '#30363d' }}>
          Ouroboros SSM · 1.58-bit · AVX2
        </span>
      </div>

      {/* Error banner */}
      {error && (
        <div
          className="flex items-center gap-3 px-4 py-2 text-xs font-mono flex-shrink-0"
          style={{ background: '#2d1010', borderBottom: '1px solid #ff7b72', color: '#ff7b72' }}
        >
          <span>⚠</span>
          <span className="flex-1">{error}</span>
          <button onClick={() => setError(null)} className="hover:opacity-70">✕</button>
        </div>
      )}

      {/* Three-panel body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Panel A — Intent + Agents */}
        <div
          className="flex-shrink-0 overflow-y-auto border-r"
          style={{ width: '220px', background: '#0d1117', borderColor: '#30363d' }}
        >
          <IntentPanel
            bg={bg}
            onBgChange={setBg}
            onAdd={handleAdd}
            onError={setError}
          />
        </div>

        {/* Panel B — Component Tree */}
        <div
          className="flex-shrink-0 border-r overflow-hidden flex flex-col"
          style={{ width: '260px', background: '#161b22', borderColor: '#30363d' }}
        >
          <NodeTree
            nodes={nodes}
            canUndo={canUndo}
            canRedo={canRedo}
            onRemove={handleRemove}
            onUndo={undo}
            onRedo={redo}
            onReset={reset}
          />
        </div>

        {/* Panel C — Preview + Deploy */}
        <div className="flex-1 overflow-hidden flex flex-col" style={{ background: '#0d1117' }}>
          <PreviewFrame
            nodes={nodes}
            bg={bg}
            siteName={siteName}
          />
        </div>
      </div>
    </div>
  );
}
