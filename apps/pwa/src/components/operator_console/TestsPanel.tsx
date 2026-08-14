// SPDX-License-Identifier: MIT

'use client';

import type { TestRunResult } from '../../lib/operator_console/schemas';

export function TestsPanel({ tests }: { tests: TestRunResult[] }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {tests.map((t) => (
        <li key={t.runId} className="flex items-center gap-2">
          <span className="uppercase">{t.status}</span>
          <span className="text-white/40">{t.summary.passed}/{t.summary.total} passed</span>
        </li>
      ))}
    </ul>
  );
}
