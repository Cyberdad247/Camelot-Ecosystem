// SPDX-License-Identifier: MIT

'use client';

export function CancellationDialog({
  open,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Cancel active task"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
    >
      <div className="w-full max-w-md border border-red-400/40 bg-obsidian p-5">
        <h3 className="font-display text-base tracking-minted text-red-300">CANCEL ACTIVE TASK</h3>
        <p className="mt-2 text-xs text-white/60">
          Cancelling revokes the lease, stops workers, and cleans the VFS workspace, then emits a
          cancellation receipt.
        </p>
        <div className="mt-5 flex justify-end gap-3">
          <button type="button" onClick={onCancel} className="border border-white/20 px-4 py-2 text-xs uppercase tracking-widest text-white/60">
            Keep running
          </button>
          <button type="button" onClick={onConfirm} className="border border-red-400/60 px-4 py-2 text-xs uppercase tracking-widest text-red-300">
            Confirm cancel
          </button>
        </div>
      </div>
    </div>
  );
}
