// SPDX-License-Identifier: MIT

'use client';

export function StaleEvidenceNotice({ ageLabel }: { ageLabel: string }) {
  return (
    <div
      role="status"
      className="flex items-center gap-2 border border-amber-300/40 bg-amber-300/5 px-3 py-2 font-mono text-[11px] text-amber-200"
    >
      <span aria-hidden="true">◷</span>
      <span>STALE · last verified {ageLabel}</span>
    </div>
  );
}
