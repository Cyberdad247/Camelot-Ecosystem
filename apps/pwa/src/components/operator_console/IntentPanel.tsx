// SPDX-License-Identifier: MIT

'use client';

export function IntentPanel({ intent }: { intent: Record<string, unknown> }) {
  return (
    <pre className="whitespace-pre-wrap break-all text-[11px] text-white/70">
      {JSON.stringify(intent, null, 2)}
    </pre>
  );
}
