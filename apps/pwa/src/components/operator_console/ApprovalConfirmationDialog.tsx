// SPDX-License-Identifier: MIT

'use client';

export function ApprovalConfirmationDialog({
  open,
  decision,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  decision: 'approve' | 'deny';
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Confirm ${decision}`}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
    >
      <div className="w-full max-w-md border border-gold/30 bg-obsidian p-5">
        <h3 className="font-display text-base tracking-minted text-gold-light">
          CONFIRM {decision.toUpperCase()}
        </h3>
        <p className="mt-2 text-xs text-white/60">
          This submits a manifest-scoped decision to Sentinel. Only the manifest ID and your
          decision are transmitted — no commands, no paths, no diffs.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="border border-white/20 px-4 py-2 text-xs uppercase tracking-widest text-white/60"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`border px-4 py-2 text-xs uppercase tracking-widest ${
              decision === 'approve'
                ? 'border-emerald-400/60 text-emerald-300'
                : 'border-red-400/60 text-red-300'
            }`}
          >
            Confirm {decision}
          </button>
        </div>
      </div>
    </div>
  );
}
