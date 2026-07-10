'use client';

import { useState } from 'react';
import { Cable, GitBranch, Network, ShieldCheck, Workflow } from 'lucide-react';
import { useAstStore }    from '@/lib/crdt';
import { IntentPanel }    from '@/components/intent-panel';
import { NodeTree }       from '@/components/node-tree';
import { PreviewFrame }   from '@/components/preview-frame';
import type { ASTNode }   from '@/lib/parse-ast';

const BRIDGE_MATRIX = [
  { label: 'Codex', status: 'SIR_CODEX', detail: 'Kinetic lane', icon: Workflow, accent: '#D4AF37' },
  { label: 'Heimdall', status: 'Bifrost governor', detail: '5 nano-knights harnessed', icon: ShieldCheck, accent: '#3fb950' },
  { label: 'Bifrost', status: ':3001 bridge', detail: 'OmniRoute + CLIProxyAPI + BitRouter + 9Router + Multivoice', icon: Cable, accent: '#58a6ff' },
  { label: 'Router Mesh', status: ':8080 / :20128 / :8078 / :8079 / :7680', detail: 'Provider, voice, and fallback lanes', icon: Network, accent: '#a371f7' },
  { label: 'Cartridges', status: 'Excalibur + Cybertronia', detail: 'Forge lanes armed', icon: ShieldCheck, accent: '#ff7b72' },
];

const UPSTREAM_REFS = [
  { name: 'CLIProxyAPI', repo: 'Cyberdad247/CLIProxyAPI', head: 'f8334be', pushed: '2026-07-02 18:32Z' },
  { name: 'OmniRoute', repo: 'Cyberdad247/OmniRoute', head: 'b729a8f', pushed: '2026-07-02 18:33Z' },
  { name: 'BitRouter', repo: 'Cyberdad247/bitrouter', head: '56b2634', pushed: '2026-07-02 07:53Z' },
  { name: '9Router', repo: 'Cyberdad247/9router', head: '0b3c794', pushed: '2026-07-02 07:52Z' },
  { name: 'Multivoice', repo: 'Cyberdad247/Multivoice-router', head: '57c7c50', pushed: '2026-06-10 20:21Z' },
];

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

      <div
        className="flex flex-col gap-3 px-4 py-3 flex-shrink-0 border-b"
        style={{ background: '#0d1117', borderColor: '#30363d' }}
      >
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 min-w-0">
            <GitBranch size={16} color="#D4AF37" aria-hidden />
            <span className="text-xs font-bold uppercase tracking-widest" style={{ color: '#D4AF37' }}>
              Bridge Matrix
            </span>
            <span className="text-xs" style={{ color: '#8b949e' }}>
              Codex to Bifrost router mesh to cartridge lanes
            </span>
          </div>
          <div className="ml-auto flex flex-wrap gap-2">
            {UPSTREAM_REFS.map(ref => (
              <span
                key={ref.name}
                className="rounded px-2 py-1 text-[11px] font-mono"
                style={{ background: '#161b22', border: '1px solid #30363d', color: '#8b949e' }}
                title={`${ref.repo} pushed ${ref.pushed}`}
              >
                {ref.name} {ref.head}
              </span>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-2">
          {BRIDGE_MATRIX.map(item => {
            const Icon = item.icon;
            return (
              <div
                key={item.label}
                className="rounded-md px-3 py-2 flex items-center gap-3"
                style={{ background: '#161b22', border: '1px solid #30363d' }}
              >
                <Icon size={18} color={item.accent} aria-hidden />
                <div className="min-w-0">
                  <div className="text-xs font-bold truncate" style={{ color: '#e6edf3' }}>
                    {item.label}
                  </div>
                  <div className="text-[11px] truncate" style={{ color: item.accent }}>
                    {item.status}
                  </div>
                  <div className="text-[10px] truncate" style={{ color: '#8b949e' }}>
                    {item.detail}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
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
