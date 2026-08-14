// SPDX-License-Identifier: MIT

'use client';

export function EmptyEvidenceState({ panel }: { panel: string }) {
  return (
    <div className="flex h-full min-h-24 items-center justify-center border border-white/10 px-4 py-6 text-center">
      <p className="font-mono text-xs text-white/40">
        No verified evidence yet — <span className="uppercase">{panel}</span>
      </p>
    </div>
  );
}
