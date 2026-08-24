import React, { useMemo, useState } from 'react';
import { ScrollText, X } from 'lucide-react';
import type { PlanEvent } from './useKnightStream';

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Safe minimal markdown -> HTML. The content is HTML-escaped FIRST, then a
 * fixed set of formatting tags is applied to the already-escaped text. Because
 * any markup in the source is neutralized before our tags are added, this
 * cannot inject HTML/JS — so feeding the result to dangerouslySetInnerHTML is
 * safe, with zero markdown dependencies.
 */
function renderMarkdownSafe(md: string): string {
  return escapeHtml(md)
    .replace(/^### (.*)$/gm, '<h3 class="text-sm font-semibold text-fuchsia-300 mt-3 mb-1">$1</h3>')
    .replace(/^## (.*)$/gm, '<h2 class="text-base font-bold text-slate-100 mt-4 mb-1">$1</h2>')
    .replace(/^# (.*)$/gm, '<h1 class="text-lg font-black text-fuchsia-200 mb-2">$1</h1>')
    .replace(/`([^`]+)`/g, '<code class="rounded bg-slate-800 px-1 font-mono text-emerald-300">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong class="text-slate-100">$1</strong>')
    .replace(/^- (.*)$/gm, '<div class="pl-3">• $1</div>')
    .replace(/\n/g, '<br />');
}

/**
 * Renders the latest `mdx` visual plan from the go_router SSE stream. Manages
 * its own dismissal: a new plan (different ts) reappears automatically.
 */
export default function VisualPlanOverlay({ plan }: { plan: PlanEvent | null }) {
  const [dismissedTs, setDismissedTs] = useState<string | null>(null);
  const html = useMemo(() => (plan ? renderMarkdownSafe(plan.content) : ''), [plan]);

  if (!plan || plan.ts === dismissedTs) return null;

  return (
    <div className="rounded-xl border border-fuchsia-500/30 bg-slate-900/70 p-4 shadow-lg">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-slate-500">
          <ScrollText className="h-3.5 w-3.5" /> Visual Plan
          <span className="font-mono text-[10px] capitalize text-slate-600">{plan.knight}</span>
          {plan.title && <span className="text-[11px] text-fuchsia-300">{plan.title}</span>}
        </h2>
        <button
          onClick={() => setDismissedTs(plan.ts)}
          className="text-slate-500 hover:text-slate-300"
          aria-label="dismiss plan"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      <div
        className="max-h-72 overflow-y-auto text-sm leading-relaxed text-slate-300"
        dangerouslySetInnerHTML={{ __html: html }}
      />
      <p className="mt-2 font-mono text-[10px] text-slate-600">
        {new Date(plan.ts).toLocaleTimeString()}
      </p>
    </div>
  );
}
