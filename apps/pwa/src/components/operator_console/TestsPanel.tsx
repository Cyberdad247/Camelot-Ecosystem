// SPDX-License-Identifier: MIT

'use client';

import type { TestRunResult } from '../../lib/operator_console/schemas';

const STATUS_STYLE: Record<string, string> = {
  passed: 'text-emerald-400',
  failed: 'text-red-400',
  cancelled: 'text-white/40',
  timed_out: 'text-amber-300',
};

export function TestsPanel({ tests }: { tests: TestRunResult[] }) {
  if (!tests.length) {
    return <p className="text-xs italic text-white/40">No test runs yet.</p>;
  }
  return (
    <ul className="space-y-3">
      {tests.map((t) => (
        <li key={t.runId} className="border border-white/10 p-3">
          <div className="flex items-center justify-between gap-2">
            <span className={`font-mono text-[11px] uppercase ${STATUS_STYLE[t.status] ?? ''}`}>
              {t.status}
            </span>
            <span className="font-mono text-[10px] text-white/40">
              {t.summary.passed}/{t.summary.total} passed · {t.summary.failed} failed
            </span>
          </div>
          {t.suites.map((s) => (
            <p key={s.name} className="mt-1 text-[11px] text-white/50">
              {s.name} · <span className="uppercase">{s.status}</span> · {s.durationMs}ms
            </p>
          ))}
        </li>
      ))}
    </ul>
  );
}
