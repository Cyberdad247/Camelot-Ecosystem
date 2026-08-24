// SPDX-License-Identifier: MIT

'use client';

export function IntentPanel({ intent }: { intent: Record<string, unknown> }) {
  const hasIntent = Object.keys(intent).length > 0;
  if (!hasIntent) {
    return <p className="text-xs italic text-white/40">No signed raw intent available.</p>;
  }
  return (
    <div className="space-y-3">
      <p className="text-xs text-white/50">Signed raw intent (read-only):</p>
      <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-all rounded-sm border border-white/10 bg-black/30 p-3 text-[11px] text-white/80">
        {JSON.stringify(intent, null, 2)}
      </pre>
    </div>
  );
}
