'use client';

import { useMemo, useRef, useState } from 'react';
import type { ASTNode }              from '@/lib/parse-ast';
import { generateSiteHTML }          from '@/lib/site-generator';
import { dispatchDeploy }            from '@/lib/dispatch-deploy';
import type { DeployClientError }    from '@/lib/dispatch-deploy';

interface Props {
  nodes:    ReadonlyMap<string, ASTNode>;
  bg:       string;
  siteName: string;
}

type DeployState =
  | { status: 'idle' }
  | { status: 'deploying' }
  | { status: 'done';  url: string; ms: number }
  | { status: 'error'; msg: string };

export function PreviewFrame({ nodes, bg, siteName }: Props) {
  const iframeRef                       = useRef<HTMLIFrameElement>(null);
  const [deployState, setDeployState]   = useState<DeployState>({ status: 'idle' });

  const srcdoc = useMemo(() => {
    const list = [...nodes.values()];
    if (list.length === 0) return '';
    return generateSiteHTML(list, bg, siteName);
  }, [nodes, bg, siteName]);

  async function handleDeploy() {
    const list = [...nodes.values()];
    if (list.length === 0) return;
    setDeployState({ status: 'deploying' });
    try {
      const result = await dispatchDeploy({ nodes: list, bg, siteName });
      setDeployState({ status: 'done', url: result.url, ms: result.latency_ms });
    } catch (e) {
      const err = e as DeployClientError;
      setDeployState({ status: 'error', msg: err.message });
    }
  }

  const nodeCount = nodes.size;

  return (
    <div className="flex flex-col h-full">
      {/* Preview toolbar */}
      <div
        className="flex items-center gap-2 px-3 py-2 border-b flex-shrink-0"
        style={{ borderColor: '#30363d' }}
      >
        <span className="text-xs font-semibold uppercase tracking-wider mr-auto" style={{ color: '#8b949e' }}>
          Preview
        </span>
        <span className="text-xs font-mono" style={{ color: '#30363d' }}>
          {nodeCount} component{nodeCount !== 1 ? 's' : ''}
        </span>
        <div
          className="h-3 w-3 rounded-full"
          style={{ background: bg, border: '1px solid #30363d' }}
          title={bg}
        />
      </div>

      {/* iframe */}
      <div className="flex-1 relative overflow-hidden" style={{ background: '#0d1117' }}>
        {nodeCount === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3">
            <span style={{ color: '#30363d', fontSize: '3rem' }}>◌</span>
            <p className="text-xs text-center" style={{ color: '#8b949e' }}>
              Add a component to see the preview
            </p>
          </div>
        ) : (
          <iframe
            ref={iframeRef}
            srcDoc={srcdoc}
            title="Site preview"
            sandbox="allow-same-origin allow-forms"
            className="w-full h-full border-0"
            style={{ transform: 'scale(1)', transformOrigin: 'top left' }}
          />
        )}
      </div>

      {/* Deploy panel */}
      <div
        className="flex-shrink-0 flex flex-col gap-2 p-3 border-t"
        style={{ borderColor: '#30363d' }}
      >
        {deployState.status === 'done' && (
          <a
            href={deployState.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-md px-3 py-2 text-xs font-mono truncate hover:opacity-80 transition-opacity"
            style={{ background: '#0d2d1c', border: '1px solid #3fb950', color: '#3fb950' }}
          >
            <span>✓</span>
            <span className="truncate">{deployState.url}</span>
            <span className="ml-auto flex-shrink-0 opacity-60">{(deployState.ms / 1000).toFixed(1)}s</span>
          </a>
        )}
        {deployState.status === 'error' && (
          <div
            className="rounded-md px-3 py-2 text-xs font-mono"
            style={{ background: '#2d1010', border: '1px solid #ff7b72', color: '#ff7b72' }}
          >
            {deployState.msg}
          </div>
        )}
        <button
          onClick={() => void handleDeploy()}
          disabled={nodeCount === 0 || deployState.status === 'deploying'}
          className="w-full rounded-md px-3 py-2 text-sm font-semibold transition-opacity disabled:opacity-40"
          style={{ background: '#3fb950', color: '#0d1117' }}
        >
          {deployState.status === 'deploying' ? '⟳ Deploying to Vercel…' : '▲ Deploy to Vercel'}
        </button>
        {deployState.status !== 'idle' && deployState.status !== 'deploying' && (
          <button
            onClick={() => setDeployState({ status: 'idle' })}
            className="text-xs hover:opacity-80"
            style={{ color: '#8b949e' }}
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
}
