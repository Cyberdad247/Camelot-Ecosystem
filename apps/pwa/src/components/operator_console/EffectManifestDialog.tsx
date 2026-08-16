// SPDX-License-Identifier: MIT

'use client';

import { useState } from 'react';
import type { EffectManifest } from '../../lib/operator_console/schemas';

export function EffectManifestDialog({
  manifest,
  onApprove,
  onDeny,
  disabled,
}: {
  manifest: EffectManifest;
  onApprove: (reason?: string) => void;
  onDeny: (reason?: string) => void;
  disabled: boolean;
}) {
  const [reason, setReason] = useState('');

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Effect manifest approval"
      className="border border-gold/30 bg-obsidian p-4 shadow-[4px_4px_0px_0px_#050507]"
    >
      <h3 className="font-display text-sm tracking-minted text-gold-light">EFFECT MANIFEST</h3>
      <dl className="mt-3 space-y-2 text-xs text-white/70">
        <div className="flex justify-between gap-4">
          <dt className="text-white/40">Manifest</dt>
          <dd className="break-all">{manifest.manifestId}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-white/40">Kind</dt>
          <dd>{manifest.kind}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-white/40">Diff SHA-256</dt>
          <dd className="break-all">{manifest.diffSha256}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-white/40">Policy</dt>
          <dd>{manifest.policyClass}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-white/40">Expires</dt>
          <dd>{manifest.expiresAt}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-white/40">Base → Candidate</dt>
          <dd className="break-all">
            {manifest.baseRevision.slice(0, 8)} → {manifest.candidateRevision.slice(0, 8)}
          </dd>
        </div>
      </dl>
      <div className="mt-3">
        <p className="mb-1 text-[10px] uppercase tracking-widest text-white/40">Changed paths</p>
        <ul className="max-h-28 overflow-auto border border-white/10 p-2 font-mono text-[10px] text-white/60">
          {manifest.allowedPaths.map((p) => (
            <li key={p}>+ {p}</li>
          ))}
        </ul>
      </div>
      <div className="mt-3">
        <p className="mb-1 text-[10px] uppercase tracking-widest text-white/40">
          Required evidence
        </p>
        <ul className="font-mono text-[10px] text-white/60">
          {manifest.requiredEvidence.map((e) => (
            <li key={e}>· {e}</li>
          ))}
        </ul>
      </div>
      <label className="mt-4 block">
        <span className="text-[10px] uppercase tracking-widest text-white/40">Optional reason</span>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          maxLength={500}
          className="mt-1 w-full border border-white/15 bg-black/30 p-2 text-xs text-white/80"
          aria-label="Optional decision reason"
        />
      </label>
      <div className="mt-4 flex gap-3">
        <button
          type="button"
          onClick={() => onApprove(reason)}
          disabled={disabled}
          className="border border-emerald-400/60 px-4 py-2 text-xs uppercase tracking-widest text-emerald-300 transition-colors enabled:hover:bg-emerald-400/10 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Approve
        </button>
        <button
          type="button"
          onClick={() => onDeny(reason)}
          disabled={disabled}
          className="border border-red-400/60 px-4 py-2 text-xs uppercase tracking-widest text-red-300 transition-colors enabled:hover:bg-red-400/10 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Deny
        </button>
      </div>
      {disabled && (
        <p className="mt-3 text-[11px] text-amber-200" role="alert">
          Approve/deny disabled: Sentinel, policy, Gideon, VFS, or evidence integrity is unavailable
          or invalid.
        </p>
      )}
    </div>
  );
}
